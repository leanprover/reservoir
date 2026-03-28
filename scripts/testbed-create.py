#!/usr/bin/env python3
import base64
import hashlib
import re
import json
import itertools
import argparse
import requests
from typing import Collection
from utils import *

def fetch_registrations(api_url: str) -> dict[str, dict]:
  url = f"{api_url.rstrip('/')}/api/v1/registrations"
  logging.info(f"Fetching registrations from {url}")
  resp = requests.get(url, timeout=30)
  if resp.status_code != 200:
    raise RuntimeError(f"Failed to fetch registrations ({resp.status_code}): {resp.text}")
  return resp.json()['data']

def create_entry(
    name: str, git_url: str,
    toolchains: str, version_tags: str, cache_builds: bool,
    repo_id: str | None, index_name: str | None,
    registration_key: str | None = None,
    ) -> TestbedEntry:
  job_name = f"{'Index' if toolchains == '' else 'Build'} {name}"
  digest = hashlib.sha256(job_name.encode()).digest()
  artifact = base64.urlsafe_b64encode(digest).decode().rstrip('=')
  return {
    'artifact': artifact,
    'gitUrl': git_url,
    'jobName': job_name,
    'toolchains': toolchains,
    'versionTags': version_tags,
    'cacheBuilds': cache_builds,
    "repoId": repo_id,
    "indexName": index_name,
    "registrationKey": registration_key,
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
  parser.add_argument('-T', '--toolchain', nargs='*', action='extend', default=[],
    help="Lean toolchain(s) to build the packages on")
  parser.add_argument('-P', '--packages', type=str, default='',
    help="select indexed package(s) to analyze by a regular expression")
  parser.add_argument('-V', '--version-tags', type=str, default='',
    help="select package version tags to build by a regular expression")
  parser.add_argument('-n', '--num', type=int, default=0,
    help="max number of testbed entries (< 0 for no limit)")
  parser.add_argument('-Q', '--query', type=int, default=0,
    help='(max) number of new packages to query from GitHub (< 0 for no limit)')
  parser.add_argument('--cache', action='store_true', default=True,
    help="upload build archives in cloud storage")
  parser.add_argument('--no-cache', dest='cache', action='store_false',
    help="do not upload build archives in cloud storage")
  parser.add_argument('-R', '--registrations-url', type=str, nargs='?',
    const='https://reservoir.lean-lang.org',
    help="analyze package registrations from the Reservoir API")
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

  reindex = args.packages != ''
  if not reindex and args.query == 0 and args.registrations_url is None:
    raise RuntimeError("Testbed needs at least one of `-P`, '-Q', or '-R'")
  if reindex and not args.index:
    raise RuntimeError("Testbed needs an index (with '-i') to select from it (with '-P')")

  # Entries
  entries = list[TestbedEntry]()

  # Load index
  pkgs = load_index_metadata(args.index) if args.index is not None else []

  # Query new repositories
  limit = ifnone(args.query, 0)
  indexed_repos = set(filter(None, map(github_repo_id, pkgs)))
  new_repos = query_new_repos(limit, indexed_repos, exclusions)

  # Resolve toolchains
  toolchains =  ','.join(resolve_toolchains(args.toolchain, "package"))

  # Create testbed
  for repo in new_repos:
    entry = create_entry(
      repo['nameWithOwner'], repo['url'],
      toolchains, args.version_tags, False,
      repo['id'], None)
    entries.append(entry)

  # Fetch registrations
  if args.registrations_url is not None:
    registrations = fetch_registrations(args.registrations_url)
    # Collect registration repo IDs
    # Filters by exclusions, missing IDs, and indexed repos
    reg_by_repo = dict[str, tuple[str, dict]]()
    for key, src in registrations.items():
      name = src.get('fullName', key)
      if name.lower() in exclusions:
        logging.debug(f"Skipping excluded registration: {name}")
        continue
      repo_id = src.get('id', None)
      if repo_id is None:
        logging.error(f"Registration '{key}' missing repo ID, skipping")
        continue
      if reindex and repo_id in indexed_repos:
        logging.debug(f"Skipping already-indexed registration: {key}")
        continue
      reg_by_repo[repo_id] = (key, src)
    # Curate new registrations
    # Fetches repository data from the GitHub API
    num_registered = 0
    repo_ids = list(reg_by_repo.keys())
    repos = filter(None, query_repo_data(repo_ids))
    for repo in curate_repos(repos, exclusions):
        key, _ = reg_by_repo[repo['id']]
        entry = create_entry(
          repo['nameWithOwner'], repo['url'],
          toolchains, args.version_tags, False,
          repo['id'], None, registration_key=key)
        entries.append(entry)
        num_registered += 1
    logging.info(f"{num_registered} entries from registrations")

  if reindex:
    pkgs = list(filter(lambda pkg: pkg['fullName'].lower() not in exclusions, pkgs))
    logging.info(f"{len(pkgs)} packages in index")
    r = re.compile(args.packages)
    pkgs = list(filter(lambda pkg: r.search(pkg['fullName']) is not None, pkgs))
    logging.info(f"{len(pkgs)} packages selected from index")
    for pkg in pkgs:
      repo_id: str | None = None
      git_url: str | None = None
      for pkg_src in reversed(pkg['sources']):
        if pkg_src.get('type', None) == 'git':
          if pkg_src.get('host', None) == 'github':
            git_url = pkg_src.get('gitUrl', None)
            repo_id = pkg_src.get('id', None)
          elif git_url is None:
            git_url = pkg_src.get('gitUrl', None)
      if git_url is None:
        logging.error(f"{pkg['fullName']}: Package lacks a Git source")
      else:
        cache_builds = (
          args.cache and
          pkg['owner'] in ['leanprover', 'leanprover-community'] and
          pkg['fullName'] != 'leanprover-community/mathlib'
        )
        entry = create_entry(
          pkg['fullName'], git_url,
          toolchains, args.version_tags, cache_builds,
          repo_id, pkg['fullName'])
        entries.append(entry)
  logging.info(f"{len(entries)} total testbed candidates")
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
