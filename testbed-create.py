#!/usr/bin/env python3
from utils import load_index
import json
import itertools
import argparse

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('index',
    help="package index (directory or manifest)")
  parser.add_argument('toolchain', nargs='?', default=None,
    help="Lean toolchain on build the packages on")
  parser.add_argument('-n', '--num', type=int, default=10,
    help="max number of packages to test (<= 0 for all)")
  parser.add_argument('-X', '--exclusions', nargs="*", action='extend', default=[],
    help='file containing repos to exclude')
  parser.add_argument('-o', '--output',
    help='file to output the bundle manifest')
  args = parser.parse_args()

  exclusions = set()
  for file in args.exclusions:
    with open(file, 'r') as f:
      for line in f: exclusions.add(line.strip())

  def create_entry(pkg: 'dict[str, any]'):
    artifact = pkg['fullName'].replace('-', '--').replace('/', '-')
    src = next(filter(lambda src: 'gitUrl' in src, pkg['sources']))
    return {
      'artifact': artifact,
      'gitUrl': src['gitUrl'],
      'fullName': pkg['fullName'],
      'toolchain': args.toolchain
    }

  pkgs = load_index(args.index)
  pkgs = filter(lambda pkg: pkg['fullName'] not in exclusions, pkgs)
  pkgs = map(create_entry, pkgs)
  if args.num > 0:
    pkgs = itertools.islice(pkgs, args.num)
  pkgs = list(pkgs)

  if args.output is None:
    print(json.dumps(pkgs))
  else:
    with open(args.output, 'w') as f:
      f.write(json.dumps(pkgs))
