#!/usr/bin/env python3
from utils import *
import base64
import hashlib
import re
import json
import itertools
import argparse

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('index',
    help="package index (directory or manifest)")
  parser.add_argument('-t', '--toolchain', nargs='*', action='extend', default=[],
    help="Lean toolchain on build the packages on")
  parser.add_argument('-e', '--regex', default=None,
    help="search packages by a regular expression")
  parser.add_argument('-n', '--num', type=int, default=0,
    help="max number of testbed entries (<= 0 for no limit)")
  parser.add_argument('-X', '--exclusions', nargs="*", action='extend', default=[],
    help='file containing repos to exclude')
  parser.add_argument('-o', '--output',
    help='file to output the bundle manifest')
  args = parser.parse_args()

  exclusions = set[str]()
  for file in args.exclusions:
    with open(file, 'r') as f:
      for line in f: exclusions.add(line.strip().lower())

  toolchains = resolve_toolchains(args.toolchain, "package")
  def create_entries(pkgs: Iterable[Package]) -> Iterable[TestbedEntry]:
    for pkg in pkgs:
      src = next(filter(lambda src: 'gitUrl' in src, pkg['sources']))
      if src is None:
        logging.error(f"Package {pkg['fullName']} lacks a Git source")
        continue
      build_name = pkg['fullName']
      digest = hashlib.sha256(build_name.encode()).digest()
      artifact = base64.urlsafe_b64encode(digest).decode().rstrip('=')
      yield {
        'artifact': artifact,
        'gitUrl': src['gitUrl'],
        'buildName': build_name,
        'fullName': pkg['fullName'],
        'toolchains': list(toolchains)
      }

  pkgs, _ = load_index(args.index)
  pkgs = filter(lambda pkg: pkg['fullName'].lower() not in exclusions, pkgs)
  if args.regex is not None:
    r = re.compile(args.regex)
    pkgs = filter(lambda pkg: r.search(pkg['fullName']) is not None, pkgs)
  entries = create_entries(pkgs)
  if args.num > 0:
    entries = itertools.islice(entries, args.num)
  entries = list(entries)

  if args.output is None:
    print(json.dumps(entries))
  else:
    with open(args.output, 'w') as f:
      f.write(json.dumps(entries))
