#!/usr/bin/env python3
from utils import CommandError, configure_logging, run_cmd, capture_cmd
import subprocess
import os
import argparse
import shutil
import logging
import json

DEFAULT_ORIGIN = 'leanprover/lean4'
def normalize_toolchain(toolchain: str):
  parts = toolchain.strip().split(':')
  if len(parts) < 2:
    origin = DEFAULT_ORIGIN
    ver = parts[0]
  else:
    origin = parts[0]
    ver = parts[1]
  if ver[0].isdecimal():
    ver = f'v{ver}'
  return f'{origin}:{ver}'

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('url',
    help="Git URL of the repository to clone")
  parser.add_argument('test_dir',
    help="directory to clone the package into")
  parser.add_argument('toolchain', nargs='?', type=str, default='',
    help="Lean toolchain on build the package on")
  parser.add_argument('-o', '--output',
    help='file to output the build results')
  parser.add_argument('-q', '--quiet', dest="verbosity", action='store_const', const=0, default=1,
    help='print no logging information')
  parser.add_argument('-v', '--verbose', dest="verbosity", action='store_const', const=2,
    help='print verbose logging information')
  parser.add_argument('-r', '--reuse-clone', action='store_true',
    help='reuse cloned repository if it already exists')
  args = parser.parse_args()

  configure_logging(args.verbosity)
  result = dict()

  # Clone package
  if not (args.reuse_clone and os.path.exists(args.test_dir)):
    os.makedirs(args.test_dir, exist_ok=True)
    shutil.rmtree(args.test_dir)
    run_cmd('git', 'clone', args.url, args.test_dir)
  iwd = os.getcwd()
  os.chdir(args.test_dir)
  result['revision'] = capture_cmd('git', 'rev-parse', 'HEAD').decode().strip()

  # Set toolchain
  toolchain = args.toolchain.strip()
  toolchain_file = 'lean-toolchain'
  if len(toolchain) > 0:
    with open(toolchain_file, 'w') as f:
      f.write(args.toolchain)
      f.write('\n')
  else:
    with open(toolchain_file, 'r') as f:
      toolchain = normalize_toolchain(f.read())
  result['toolchain'] = toolchain

  # Try build
  try:
    run_cmd('lake', 'exe', 'cache', 'get', allow_failure=True)
    if run_cmd('lake', 'build', allow_failure=True) != 0:
      logging.info('build failed, updating and trying again')
      run_cmd('lake', 'update')
      run_cmd('lake', 'clean')
      run_cmd('lake', 'exe', 'cache', 'get', allow_failure=True)
      run_cmd('lake', 'build')
    logging.info(f'successfully built {args.url} on {toolchain}')
    result['outcome'] = 'success'
  except CommandError:
    logging.error(f'failed to build {args.url} on {toolchain}')
    result['outcome'] = 'failure'

  # Output result
  os.chdir(iwd)
  if args.output is None:
    print(json.dumps(result, indent=2))
  else:
    with open(args.output, 'w') as f:
      f.write(json.dumps(result, indent=2))
