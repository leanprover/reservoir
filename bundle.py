#!/usr/bin/env python3
from utils import *
from datetime import datetime
import argparse
import json

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('index',
    help="package index (directory or manifest)")
  parser.add_argument('results', nargs='?', default=None,
    help="testbed results")
  parser.add_argument('-o', '--output',
    help='file to output the bundle manifest')
  args = parser.parse_args()

  pkgs = load_index(args.index, include_builds=True)
  fullPkgs: 'dict[str, any]' = dict()
  for pkg in pkgs:
    fullPkgs[pkg['fullName']] = pkg
  if args.results is not None:
    with open(args.results, 'r') as f:
      results: 'dict[str, dict[str, any]]' = json.load(f)
    for (fullName, result) in results.items():
      pkg = fullPkgs[fullName]
      pkg['builds'] = add_build(pkg['builds'], result)

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
