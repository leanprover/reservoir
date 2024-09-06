#!/usr/bin/env python3
from utils import *
import argparse
import os
import json
import logging

# ===
# Main Processing
# ===

if __name__ == "__main__":
  script_dir = os.path.dirname(os.path.realpath(__file__))
  default_exclusions = os.path.join(script_dir, "index-exclusions.txt")
  parser = argparse.ArgumentParser()
  parser.add_argument('-R', '--refresh', action='store_true',
    help='update existing packages in the index')
  parser.add_argument('-L', '--limit', type=int, default=None,
    help='(max) number of results to query from GitHub (< 0 for no limit)')
  parser.add_argument('-X', '--exclusions', default=default_exclusions,
    help='file containing repos to exclude')
  parser.add_argument('-o', '--output-manifest',
    help='file to output result manifest')
  parser.add_argument('-D', '--index-dir', default=None,
    help='directory to output hierarchical index')
  parser.add_argument('-q', '--quiet', dest="verbosity", action='store_const', const=0, default=1,
    help='print no logging information')
  parser.add_argument('-v', '--verbose', dest="verbosity", action='store_const', const=2,
    help='print verbose logging information')
  args = parser.parse_args()

  configure_logging(args.verbosity)

  exclusions = set()
  with open(args.exclusions, 'r') as f:
    for line in f: exclusions.add(line.strip())

  # ---
  # Compute Index
  # ---

  # Refresh Index
  if args.index_dir is not None and args.refresh:
    indexed_pkgs, aliases = load_index(args.index_dir)
    logging.info(f"{len(indexed_pkgs)} existing packages")
    indexed_pkgs = packages_by_repo(indexed_pkgs)
    logging.info(f"{len(indexed_pkgs)} existing packages with GitHub repositories")
  else:
    indexed_pkgs = dict[str, Package]()
    aliases = CaseInsensitiveDict[Package]()

  # Query New Repos
  new_pkgs = list[Package]()
  limit = (0 if args.refresh else 100) if args.limit is None else args.limit
  if limit != 0:
    indexed_ids = indexed_pkgs.keys()
    repo_ids = query_lake_repos(limit)
    logging.info(f"{len(repo_ids)} candidate repositories with root Lake manifests")
    repos = filter(None, query_repo_data(repo_ids))
    if len(indexed_ids) != 0:
      repos = list(filter_repo_ids(repos, indexed_ids))
      logging.info(f"{len(repos)} candidate repositories not in index")
    new_pkgs = list(pkgs_of_repos(repos, exclusions))
  note = 'notable new' if len(indexed_pkgs) != 0 else 'notable'
  logging.info(f"{len(new_pkgs)} {note} OSI-licensed packages")

  # Finalize Index
  pkgs = itertools.chain(indexed_pkgs.values(), new_pkgs)
  pkgs = list(sorted(pkgs, key=lambda pkg: pkg['stars'], reverse=True))
  if len(indexed_pkgs) != 0:
    logging.info(f"{len(pkgs)} total packages")

  # ---
  # Output Results
  # ---

  if args.index_dir is not None:
    write_index(args.index_dir, pkgs, aliases)

  for pkg in pkgs:
    pkg['renames'] = []

  if args.output_manifest is not None:
    with open(args.output_manifest, 'w') as f:
      json.dump(pkgs, f, indent=2)

  if args.output_manifest is None and args.index_dir is None:
    print(json.dumps(pkgs, indent=2))
