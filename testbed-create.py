#!/usr/bin/env python3
from datetime import datetime
import json
import argparse
import os


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('manifest',
    help="package index manifest (e.g., from query)")
  parser.add_argument('toolchain',
    help="Lean toolchain on build the packages on")
  parser.add_argument('-n', '--num', type=int, default=10,
    help="max number of packages to test")
  parser.add_argument('-X', '--exclusions', nargs="*", action='extend', default=[],
    help='file containing repos to exclude')
  parser.add_argument('-o', '--output',
    help='file to output the bundle manifest')
  args = parser.parse_args()

  exclusions = set()
  for file in args.exclusions:
    with open(file, 'r') as f:
      for line in f: exclusions.add(line.strip())

  with open(args.manifest, 'r') as f:
    manifest = json.load(f)

  def create_entry(pkg: 'dict[str, any]'):
    return {
      'id': pkg['id'],
      'url': pkg['url'],
      'fullName': pkg['fullName'],
      'toolchain': args.toolchain
    }

  pkgs = manifest['packages']
  pkgs = filter(lambda pkg: pkg['fullName'] not in exclusions, pkgs)
  pkgs = map(create_entry, pkgs)
  pkgs = list(pkgs)[0:args.num]

  if args.output is None:
    print(json.dumps(pkgs))
  else:
    with open(args.output, 'w') as f:
      f.write(json.dumps(pkgs))
