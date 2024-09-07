#!/usr/bin/env python3
from utils import *
import logging
import json
import argparse

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('results',
    help="JSON manifest of results")
  parser.add_argument('index',
    help='directory to output hierarchical index')
  parser.add_argument('-q', '--quiet', dest="verbosity", action='store_const', const=0, default=1,
    help='print no logging information')
  parser.add_argument('-v', '--verbose', dest="verbosity", action='store_const', const=2,
    help='print verbose logging information')
  args = parser.parse_args()

  configure_logging(args.verbosity)

  # Create id-package map
  pkgs = dict[str, Package]()

  # Load results
  with open(args.results) as f:
    results: dict[str, PackageResult] = json.load(f)

  # Load index
  indexed_pkgs, aliases = load_index(args.index)

  # Query result repositories
  ids = list(results.keys())
  repos = dict[str, Repo]()
  for id, repo in zip(ids, query_repo_data(ids)):
    if repo is None:
      logging.error(f"Repository ID '{id}' not found on GitHub")
    else:
      repos[id] = repo

  # Add repository data to packages
  repo_uses = {k: list[str]() for k in repos.keys()}
  for pkg in indexed_pkgs:
    id = github_repo_id(pkg)
    if id is not None and id in results:
      repo_uses[id].append(pkg['fullName'])
      repo_pkg = pkgs.get(id, None)
      if repo_pkg is not None:
        repo_pkg['renames'].append(mk_rename(pkg))
        continue
      pkgs[id] = pkg
      repo = repos.get(id, None)
      if repo is None:
        logging.error(f"{pkg['fullName']}: Repository ID '{id}' not found on GitHub")
        continue
      add_repo_metadata(pkg, repo)
  for id, uses in repo_uses.items():
    if len(uses) < 1:
      pkgs[id] = pkg_of_repo(repos[id])
    elif len(uses) > 1:
      logging.warning(F"Repository reuse: '{repos[id]['nameWithOwner']}' for {uses}")

  # Add testbed result data
  for id, result in results.items():
    pkg = pkgs.get(id, None)
    if pkg is None:
      continue
    pkg['name'] = name = ifnone(result['name'], pkg['name'])
    pkg['description'] = ifnone(result['description'], pkg['description'])
    pkg['homepage'] = ifnone(result['homepage'], pkg['homepage'])
    pkg['keywords'] = ifnone(result['keywords'], pkg['keywords'])
    pkg['updatedAt'] = max(pkg['updatedAt'], result['headVersion']['date'])
    pkg['fullName'] = f"{pkg['owner']}/{name}"
    pkg['versions'] = [result['headVersion']] + result['versions']

  # Save index
  write_index(args.index, pkgs.values(), aliases)
