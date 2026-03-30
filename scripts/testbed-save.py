#!/usr/bin/env python3
import hashlib
import logging
import json
import argparse
import requests
from utils import *

def delete_registrations(api_url: str, keys: list[str]):
  url = f"{api_url.rstrip('/')}/api/v1/registrations"
  logging.debug(f"Deleting {len(keys)} package registrations using {url}")
  headers = {}
  token = os.getenv('RESERVOIR_AUTH_TOKEN')
  if token:
    headers['Authorization'] = f"Bearer {token}"
  try:
    resp = requests.delete(url, json=keys, headers=headers, timeout=30)
    if resp.status_code == 200:
      logging.info(f"Finished and removed {len(keys)} package registrations")
    else:
      logging.error(f"Failed to delete registrations ({resp.status_code}): {resp.text}")
  except requests.RequestException as e:
    logging.error(f"Failed to delete registrations: {e}")

def add_result_data(pkg: Package, result: PackageResult):
  pkg['name'] = name = ifnone(result['name'], pkg['name'])
  pkg['description'] = ifnone(result['description'], pkg['description'])
  pkg['homepage'] = ifnone(result['homepage'], pkg['homepage'])
  pkg['keywords'] = ifnone(result['keywords'], pkg['keywords'])
  pkg['updatedAt'] = max(pkg['updatedAt'], result['headVersion']['date'])
  pkg['fullName'] = f"{pkg['owner']}/{name}"
  vers = sorted(result['versions'], key=lambda v: (Version(v['version']), v['date']), reverse=True)
  pkg['versions'] = [result['headVersion']] + vers

def has_unresolved_license_files(result: PackageResult) -> bool:
  for ver in walk_versions(result):
    if ver.get('unresolvedLicenseFiles', False):
      return True
  return False

def download_license_file(url: str) -> bytes | None:
  try:
    resp = requests.get(url, timeout=30)
    if resp.status_code == 200:
      return resp.content
    return None
  except requests.RequestException:
    return None

def check_license_file_hashes(
    pkg: Package, result: TestbedResult, index_dir: str
):
  """Download license files, compare hashes with stored versions, and attach hash data."""
  src = github_src(pkg)
  if src is None:
    return
  fullName = src['fullName']
  revision = result['headVersion']['revision']
  license_files = result['headVersion']['licenseFiles']

  # Load previous hashes from index
  prev_hashes = dict[str, str]()
  pkg_dir = os.path.join(index_dir, package_relpath(pkg))
  versions_file = os.path.join(pkg_dir, 'versions.json')
  if os.path.exists(versions_file):
    with open(versions_file, 'r') as f:
      versions_data = json.load(f)
    for ver in versions_data.get('data', []):
      for lf in ver.get('licenseFiles', []):
        if isinstance(lf, dict) and lf.get('sha256') is not None:
          prev_hashes[lf['path']] = lf['sha256']

  # Download and hash each license file
  new_entries: list[LicenseFileEntry] = []
  for path in license_files:
    if isinstance(path, dict):
      path = path['path']
    url = f"https://raw.githubusercontent.com/{fullName}/{revision}/{path}"
    content = download_license_file(url)
    if content is None:
      logging.warning(f"{pkg['fullName']}: Could not download license file '{path}' from GitHub")
      new_entries.append({'path': path})
      continue
    sha256 = hashlib.sha256(content).hexdigest()
    prev = prev_hashes.get(path, None)
    if prev is not None and prev != sha256:
      logging.warning(f"{pkg['fullName']}: License file '{path}' has changed (review override)")
    elif prev is None and len(prev_hashes) > 0:
      logging.warning(f"{pkg['fullName']}: New license file '{path}' detected (review override)")
    new_entries.append({'path': path, 'sha256': sha256})

  # Check for removed files
  new_paths = {e['path'] for e in new_entries}
  for prev_path in prev_hashes:
    if prev_path not in new_paths:
      logging.warning(f"{pkg['fullName']}: License file '{prev_path}' removed (review override)")

  # Attach hash data to all versions
  for ver in pkg['versions']:
    ver['licenseFiles'] = new_entries

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('results',
    help="JSON manifest of results")
  parser.add_argument('index',
    help='directory to output hierarchical index')
  script_dir = os.path.dirname(os.path.realpath(__file__))
  parser.add_argument('-R', '--registrations-url', type=str, nargs='?',
    const='https://reservoir.lean-lang.org',
    help="delete processed registrations from the Reservoir API")
  parser.add_argument('-L', '--license-overrides',
    default=os.path.join(script_dir, "license-overrides.json"),
    help='JSON file containing license overrides')
  parser.add_argument('-q', '--quiet', dest="verbosity", action='store_const', const=0, default=1,
    help='print no logging information')
  parser.add_argument('-v', '--verbose', dest="verbosity", action='store_const', const=2,
    help='print verbose logging information')
  args = parser.parse_args()

  configure_logging(args.verbosity)

  license_overrides = load_license_overrides(args.license_overrides)
  spdx_licenses = query_licenses()

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

  # Apply license overrides and filter
  licensed_pkgs = list[Package]()
  for pkg in final_pkgs:
    check_osi_license(pkg, spdx_licenses, license_overrides)
    licensed_pkgs.append(pkg)
  final_pkgs = licensed_pkgs

  # Check for unresolved license paths and license file hashes
  checked_pkgs = list[Package]()
  result_by_name = {r.get('indexName') or r.get('name', ''): r for r in results}
  result_by_repo = {r['repoId']: r for r in results if r.get('repoId')}
  for pkg in final_pkgs:
    # Find the corresponding result
    result = result_by_name.get(pkg['fullName'], None)
    if result is None:
      repo_id = github_repo_id(pkg)
      if repo_id is not None:
        result = result_by_repo.get(repo_id, None)
    if result is not None and has_unresolved_license_files(result):
      logging.error(f"{pkg['fullName']}: Excluded from index (unresolved license file paths)")
      continue
    if result is not None and result.get('checkLicenseFiles', False):
      check_license_file_hashes(pkg, result, args.index)
    checked_pkgs.append(pkg)
  final_pkgs = checked_pkgs

  # Save index
  write_index(args.index, final_pkgs, aliases)

  # Remove opt-outs
  for pkg in opt_outs:
    logging.info(f"Index opt-out: {pkg['fullName']}")
    shutil.rmtree(os.path.join(args.index, package_relpath(pkg)))

  # Consume processed registrations
  if args.registrations_url:
    consumed_keys = [r['registrationKey'] for r in results if r.get('registrationKey')]
    if consumed_keys:
      delete_registrations(args.registrations_url, consumed_keys)
