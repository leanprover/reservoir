#!/usr/bin/env python3
from utils import *
import base64
import hashlib
import re
import json
import itertools
import argparse

NIGHTLY_REPO='leanprover/lean4-nightly'
def resolve_toolchain(toolchain: str):
  toolchain = toolchain.strip()
  if len(toolchain) == 0 or toolchain == 'package':
    return None
  elif toolchain == 'stable':
    releases = filter(lambda r: not r['prerelease'], query_releases())
    return f"{DEFAULT_ORIGIN}:{next(releases)['tag']}"
  elif toolchain == 'nightly':
    releases = query_releases(NIGHTLY_REPO, paginate=False)
    return f"{DEFAULT_ORIGIN}:{next(releases)['tag']}"
  elif toolchain == 'latest':
    releases = query_releases(paginate=False)
    return f"{DEFAULT_ORIGIN}:{next(releases)['tag']}"
  else:
    return normalize_toolchain(toolchain)

def resolve_toolchains(toolchains: 'list[str]') -> 'set[str | None]':
  if len(toolchains) == 0:
    return set([None])
  else:
    return set(resolve_toolchain(t) for ts in toolchains for t in ts.split(','))

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

  exclusions = set()
  for file in args.exclusions:
    with open(file, 'r') as f:
      for line in f: exclusions.add(line.strip().lower())

  toolchains = resolve_toolchains(args.toolchain)
  def create_entries(pkgs: 'list[dict[str, any]]'):
    for pkg in pkgs:
      src = next(filter(lambda src: 'gitUrl' in src, pkg['sources']))
      for toolchain in toolchains:
        if len(toolchains) == 0 or toolchain is None:
          build_name = pkg['fullName']
        else:
          build_name = f"{pkg['fullName']} on {toolchain}"
        digest = hashlib.sha256(build_name.encode()).digest()
        artifact = base64.urlsafe_b64encode(digest).decode().rstrip('=')
        yield {
          'artifact': artifact,
          'gitUrl': src['gitUrl'],
          'buildName': build_name,
          'fullName': pkg['fullName'],
          'toolchain': toolchain
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
