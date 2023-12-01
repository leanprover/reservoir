#!/usr/bin/env python3
from datetime import datetime
import argparse
import os
import subprocess
import json

RELEASE_REPO = 'leanprover/lean4'
def query_toolchain_releases():
  child = subprocess.run([
    'gh', 'api', '--paginate',
    f'repos/{RELEASE_REPO}/releases',
    '-q', '.[] | .tag_name'
  ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if child.returncode != 0:
    raise RuntimeError(child.stderr.decode().strip())
  return [f'{RELEASE_REPO}:{ver}' for ver in child.stdout.decode().splitlines()]

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('index',
    help="package index (directory or manifest)")
  parser.add_argument('results',
    help="testbed results")
  parser.add_argument('-o', '--output',
    help='file to output the bundle manifest')
  args = parser.parse_args()

  if os.path.isdir(args.index):
    pkgs = list()
    for owner in os.listdir(args.index):
      owner_dir = os.path.join(args.index, owner)
      for pkg in os.listdir(owner_dir):
        md_file = os.path.join(owner_dir, pkg, 'metadata.json')
        with open(md_file, 'r') as f:
          pkgs.append(json.load(f))
    pkgs = sorted(pkgs, key=lambda pkg: pkg['stars'], reverse=True)
  else:
    with open(args.index, 'r') as f:
      pkgs = json.load(f)

  with open(args.results, 'r') as f:
    results: 'dict[str, dict[str, any]]' = json.load(f)

  fullPkgs: 'dict[str, any]' = dict()
  for pkg in pkgs:
    fullPkgs[pkg['id']] = pkg
    fullPkgs[pkg['id']]['builds'] = list()
  for (id, result) in results.items():
    fullPkgs[id]['builds'].insert(0, result)

  data = {
    'bundledAt': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    'toolchains': query_toolchain_releases(),
    'packages': list(fullPkgs.values())
  }
  if args.output is None:
    print(json.dumps(data, indent=2))
  else:
    with open(args.output, 'w') as f:
      f.write(json.dumps(data, indent=2))
