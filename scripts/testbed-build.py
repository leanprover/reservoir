#!/usr/bin/env python3
from utils import *
import os
import argparse
import shutil
import logging
import json
import tempfile

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

  result: PartialBuild = {}

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
      toolchain = normalize_toolchain(f.read().strip())
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
      result['requiredUpdate'] = True
    logging.info(f'successfully built {args.url} on {toolchain}')
    result['outcome'] = 'success'
  except CommandError:
    logging.error(f'failed to build {args.url} on {toolchain}')
    result['outcome'] = 'failure'

  # Try to pack result
  try:
    with tempfile.TemporaryDirectory() as tmp:
      archive = os.path.join(tmp, 'build.tgz')
      run_cmd('lake', 'pack', archive)
      result['archiveSize'] = os.path.getsize(archive)
  except Exception as e:
    logging.error(f'failed to pack build archive: {e}')
    result['archiveSize'] = None

  # Output result
  os.chdir(iwd)
  if args.output is None:
    print(json.dumps(result, indent=2))
  else:
    with open(args.output, 'w') as f:
      f.write(json.dumps(result, indent=2))
