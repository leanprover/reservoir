#!/usr/bin/env python3
from datetime import datetime
import json
import argparse
import os

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('manifest',
    help="repository manifest (e.g., from query)")
  parser.add_argument('-n', '--num', type=int, default=10,
    help="max number of the repositories to test")
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

  data = manifest['matrix']
  data = filter(lambda repo: repo['fullName'] not in exclusions, data)
  data = list(data)[0:args.num]

  if args.output is None:
    print(json.dumps(data))
  else:
    with open(args.output, 'w') as f:
      f.write(json.dumps(data))
