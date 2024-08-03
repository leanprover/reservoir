#!/usr/bin/env python3
from utils import *
import logging
import json
import argparse

def mk_old_build(ver: PackageVersion, build: BuildResult) -> OldBuild:
  return {
    'url': build['url'],
    'builtAt': build['date'],
    'outcome': 'success' if build['built'] else 'failure',
    'revision': ver['revision'],
    'toolchain': build['toolchain'],
    'requiredUpdate': build['requiredUpdate'],
    'archiveSize': build['archiveSize'],
  }

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

  # Query result repositories
  ids = list(results.keys())
  for id, repo in zip(ids, query_repo_data(ids)):
    if repo is None:
      logging.error(f"Repository ID '{id}' not found on GitHub")
    else:
      pkgs[id] = pkg_of_repo(repo)

  # Load index
  indexed_pkgs, aliases = load_index(args.index)
  for indexed_pkg in indexed_pkgs:
    id = github_repo_id(indexed_pkg)
    if id is not None and id in results:
      repo_pkg = pkgs.get(id, None)
      if repo_pkg is None:
        logging.error(f"{indexed_pkg['fullName']}: Repository ID '{id}' not found on GitHub")
      else:
        pkgs[id]['renames'].append(indexed_pkg)

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
    for ver in walk_versions(result):
      pkg['versions'].append(version_metadata(ver))
      for build in ver['builds']:
        pkg['builds'].append(mk_old_build(ver, build))

  # Save index
  write_index(args.index, pkgs.values(), aliases)
