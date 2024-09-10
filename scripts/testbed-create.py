#!/usr/bin/env python3
import base64
import hashlib
import re
import json
import itertools
import argparse
from typing import Collection
from utils import *

def create_entries(pkgs: Iterable[PackageMetadata], toolchains: Collection[str]) -> Iterable[TestbedEntry]:
  for pkg in pkgs:
    src = github_src(pkg)
    if src is None:
      logging.error(f"{pkg['fullName']}: Package lacks a GitHub source")
      continue
    job_name = pkg['fullName']
    digest = hashlib.sha256(job_name.encode()).digest()
    artifact = base64.urlsafe_b64encode(digest).decode().rstrip('=')
    yield {
      'artifact': artifact,
      'gitUrl': src['gitUrl'],
      'jobName': job_name,
      'toolchains': 'none' if len(toolchains) == 0 else ','.join(toolchains),
      "repoId": src['id'],
    }

def create_layers(entries: Iterable[TestbedEntry]) -> Iterable[TestbedLayer]:
  for idx, data in enumerate(paginate(entries, 256), 1):
    yield {'name': str(idx), 'data': data}

if __name__ == "__main__":
  script_dir = os.path.dirname(os.path.realpath(__file__))
  default_exclusions = os.path.join(script_dir, "package-exclusions.txt")
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--index',
    help="package index (directory or manifest)")
  parser.add_argument('-t', '--toolchain', nargs='*', action='extend', default=[],
    help="Lean toolchain(s) on build the packages on")
  parser.add_argument('-e', '--regex', type=str, default='',
    help="select indexed package(s) to analyze by a regular expression")
  parser.add_argument('-n', '--num', type=int, default=0,
    help="max number of testbed entries (< 0 for no limit)")
  parser.add_argument('-Q', '--query', type=int, default=0,
    help='(max) number of new packages to query from GitHub (< 0 for no limit)')
  parser.add_argument('-X', '--exclusions', default=default_exclusions,
    help='file containing repos to exclude')
  parser.add_argument('-o', '--output',
    help='file to output the bundle manifest')
  parser.add_argument('-q', '--quiet', dest="verbosity", action='store_const', const=0, default=1,
    help='print no logging information')
  parser.add_argument('-v', '--verbose', dest="verbosity", action='store_const', const=2,
    help='print verbose logging information')
  args = parser.parse_args()

  configure_logging(args.verbosity)

  exclusions = set[str]()
  with open(args.exclusions, 'r') as f:
    for line in f: exclusions.add(line.strip().lower())

  reindex = args.regex != ''
  if not reindex and args.query == 0:
    raise RuntimeError("Testbed needs at least one of `-e` or '-Q'")
  if reindex and not args.index:
    raise RuntimeError("Testbed needs an index (with '-i') to select from it (with '-e')")

  # Load index
  pkgs = load_index_metadata(args.index) if args.index is not None else []

  # Query new packages
  limit = ifnone(args.query, 0)
  indexed_repos = set(filter(None, map(github_repo_id, pkgs)))
  new_pkgs = query_new_packages(limit, indexed_repos, exclusions)

  # Select packages
  if reindex:
    pkgs = list(filter(lambda pkg: pkg['fullName'].lower() not in exclusions, pkgs))
    logging.info(f"{len(pkgs)} packages in index")
    if args.regex is not None:
      r = re.compile(args.regex)
      pkgs = list(filter(lambda pkg: r.search(pkg['fullName']) is not None, pkgs))
      logging.info(f"{len(pkgs)} packages selected from index")
    pkgs = new_pkgs + pkgs
  else:
    pkgs = new_pkgs
  logging.info(f"{len(pkgs)} total testbed package candidates")

  # Create testbed
  toolchains = resolve_toolchains(args.toolchain, "package")
  entries = create_entries(pkgs, toolchains)
  if args.num >= 0:
    entries = itertools.islice(entries, args.num)
  layers = list(create_layers(entries))

  # Output matrix
  matrix: TestbedMatrix = layers
  if args.output is None:
    print(json.dumps(layers))
  else:
    with open(args.output, 'w') as f:
      f.write(json.dumps(layers))
