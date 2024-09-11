#!/usr/bin/env python3
import logging
import json
import argparse
from utils import *

def add_result_data(pkg: Package, result: PackageResult):
  pkg['name'] = name = ifnone(result['name'], pkg['name'])
  pkg['description'] = ifnone(result['description'], pkg['description'])
  pkg['homepage'] = ifnone(result['homepage'], pkg['homepage'])
  pkg['keywords'] = ifnone(result['keywords'], pkg['keywords'])
  pkg['updatedAt'] = max(pkg['updatedAt'], result['headVersion']['date'])
  pkg['fullName'] = f"{pkg['owner']}/{name}"
  vers = sorted(result['versions'], key=lambda ver: ver['date'], reverse=True)
  pkg['versions'] = [result['headVersion']] + vers

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

  # Load index
  pkgs, aliases = load_index(args.index)
  pkgs = {pkg['fullName']: pkg for pkg in pkgs}

  # Load results
  with open(args.results) as f:
    results: TestbedResults = json.load(f)

  # First update pass
  opt_outs = list[Package]()
  final_pkgs = list[Package]()
  repo_results = dict[str, TestbedResult]()
  for result in results:
    if result['repoId'] is not None:
      repo_results[result['repoId']] = result
    elif result['indexName'] is not None:
      # Update indexed package without repository with result
      pkg = pkgs[result['indexName']]
      if not result['doIndex']:
        opt_outs.append(pkg)
        continue
      add_result_data(pkg, result)
      final_pkgs.append(pkg)
    else:
      logging.error(f"Testbed result without package or repository: {result['name']}")

  # Use GitHub repository data to update packages
  repo_pkgs = dict[str, Package]()
  repo_uses = {k: list[str]() for k in repo_results.keys()}
  repos = query_repos(repo_results.keys())
  for pkg in pkgs.values():
    id = github_repo_id(pkg)
    if id is None or id not in repo_results:
      continue
    # Unify multiple packages using the same repository
    repo_uses[id].append(pkg['fullName'])
    repo_pkg = repo_pkgs.get(id, None)
    if repo_pkg is not None:
      repo_pkg['renames'].append(mk_rename(pkg))
      continue
    repo_pkgs[id] = pkg
    # Update unified package using repository and result
    result = repo_results[id]
    if not repo_results[id]['doIndex']:
      opt_outs.append(pkg)
    repo = repos.get(id, None)
    if repo is None:
      logging.error(f"{pkg['fullName']}: Repository ID '{id}' not found on GitHub")
      continue
    add_repo_metadata(pkg, repo)
    add_result_data(pkg, repo_results[id])
    final_pkgs.append(pkg)
  for id, uses in repo_uses.items():
    if len(uses) < 1: # new repo
      result = repo_results[id]
      if result['doIndex']:
        pkg = package_of_repo(repos[id])
        add_result_data(pkg, result)
        final_pkgs.append(pkg)
    elif len(uses) > 1:
      logging.warning(F"Repository reuse: '{repos[id]['nameWithOwner']}' for {uses}")

  # Save index
  write_index(args.index, final_pkgs, aliases)

  # Remove opt-outs
  for pkg in opt_outs:
    logging.info(f"Index opt-out: {pkg['fullName']}")
    shutil.rmtree(os.path.join(args.index, package_relpath(pkg)))
