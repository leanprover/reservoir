#!/usr/bin/env python3
from utils import run_cmd, load_index
from datetime import datetime
import argparse
import json

RELEASE_REPO = 'leanprover/lean4'
def query_toolchain_releases():
  out = run_cmd(
    'gh', 'api', '--paginate',
    f'repos/{RELEASE_REPO}/releases',
    '-q', '.[] | .tag_name'
  )
  return [f'{RELEASE_REPO}:{ver}' for ver in out.decode().splitlines()]

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('index',
    help="package index (directory or manifest)")
  parser.add_argument('results',
    help="testbed results")
  parser.add_argument('-o', '--output',
    help='file to output the bundle manifest')
  args = parser.parse_args()

  pkgs = load_index(args.index)
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
