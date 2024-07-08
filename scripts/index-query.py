#!/usr/bin/env python3
from utils import *
from typing import TypedDict
import argparse
import re
import os
import shutil
import json
import logging
import requests

# ===
# Index Utilities
# ===

REPO_QUERY="""
query($repoIds: [ID!]!) {
  nodes(ids: $repoIds) {
    ... on Repository {
      id
      nameWithOwner
      description
      licenseInfo {
        spdxId
      }
      createdAt
      updatedAt
      pushedAt
      url
      homepageUrl
      stargazerCount
      defaultBranchRef {
        name
      }
      lakeManifest: object(expression: "HEAD:lake-manifest.json") {
        ... on Blob {
          text
        }
      }
    }
  }
}
"""

class RepoDefaultBranchRef(TypedDict):
  name: str

class RepoLicense(TypedDict):
  spdxId: str

class RepoLakeManifest(TypedDict):
  text: str

class Repo(TypedDict):
  id: str
  nameWithOwner: str
  description: str
  licenseInfo: RepoLicense | None
  createdAt: str
  updatedAt: str
  pushedAt: str
  url: str
  homepageUrl: str
  stargazerCount: int
  defaultBranchRef: RepoDefaultBranchRef
  lakeManifest: RepoLakeManifest | None

def query_repo_data(repo_ids: 'Iterable[str]') -> 'list[Repo]':
  results = list()
  for page in paginate(repo_ids, 100):
    fields = list()
    for id in page:
      fields.append('-f')
      fields.append(f'repoIds[]={id}')
    out = capture_cmd(
      'gh', 'api', 'graphql',
      "-H", "X-Github-Next-Global-ID: 1",
      '-f', f'query={REPO_QUERY}', *fields
    )
    results += json.loads(out)['data']['nodes']
  return results

# NOTE: GitHub limits code searches to 10 requests/min, which is 1000 results.
# Thus, the strategy used here will need to change when we hit that limit.
def query_lake_repos(limit: int) -> 'list[str]':
  query='filename:lake-manifest.json path:/'
  if limit <= 0:
    out = capture_cmd(
      'gh', 'api', 'search/code',
      '--paginate', '--cache', '1h',
      '-X', 'GET', '-f', f'q={query}',
      '-q', '.items[] | .repository.node_id'
    )
  else:
    out = capture_cmd(
      'gh', 'search', 'code', *query.split(' '), '-L', str(limit),
      '--json', 'path,repository', '-q', '.[] | .repository.id'
    )
  return out.decode().splitlines()

class License(TypedDict):
  reference: str
  isDeprecatedLicenseId: bool
  detailsUrl: str
  referenceNumber: int
  name: str
  licenseId: str
  seeAlso: 'list[str]'
  isOsiApproved: bool

SPDX_DATA_URL = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json"
def query_licenses(url=SPDX_DATA_URL):
  logging.debug(f"fetching SPDX license data from {url}")
  response = requests.get(url, allow_redirects=True)
  if response.status_code != 200:
    raise RuntimeError(f"failed to fetch SPDX license data ({response.status_code})")
  license_list: 'list[License]' = json.loads(response.content.decode())['licenses']
  licenses: 'dict[str, License]' = dict()
  for license in license_list:
    licenses[license['licenseId']] = license
  return licenses

def filter_license(license: RepoLicense | None) -> str | None:
  if license is None: return None
  if license['spdxId'] in ['NONE', 'NOASSERTION']: return None
  return license['spdxId']

def filter_falsy(value):
  return value if value else None

def filter_ws(value: str | None):
  if value is not None:
    value = filter_falsy(value.strip())
  return value

def github_repo(pkg: Package) -> Source | None:
  return next(filter(lambda src: src['host'] == 'github', pkg['sources']), None)

def github_repo_id(pkg: Package) -> str | None:
  repo = github_repo(pkg)
  return None if repo is None else repo['id']

def src_of_repo(repo: Repo) -> Source:
  return {
    'type': 'git',
    'host': 'github',
    'id': repo['id'],
    'fullName': repo['nameWithOwner'],
    'repoUrl': repo['url'],
    'gitUrl': repo['url'],
    'defaultBranch': repo['defaultBranchRef']['name'],
  }

class Manifest(TypedDict, total=False):
  name: str

FRENCH_QUOTE_PATTERN = re.compile('[«»]')
def pkg_of_repo(repo: Repo) -> Package:
  owner, name = repo['nameWithOwner'].split('/')
  pkg: Package = {
    'name': name,
    'owner': owner,
    'fullName': repo['nameWithOwner'],
    'description': filter_ws(repo['description']),
    'homepage': filter_ws(repo['homepageUrl']),
    'license': filter_license(repo['licenseInfo']),
    'createdAt': repo['createdAt'],
    'updatedAt': max(repo['updatedAt'], repo['pushedAt']),
    'stars': repo['stargazerCount'],
    'sources': [src_of_repo(repo)],
  }
  if repo['lakeManifest'] is not None:
    try:
      manifest: Manifest = json.loads(repo['lakeManifest']['text'])
      name = manifest.get('name', None)
      if name is not None:
        name = FRENCH_QUOTE_PATTERN.sub('', name)
        pkg['name'] = name
        pkg['fullName'] = f"{pkg['owner']}/{name}"
    except json.JSONDecodeError:
      pass
  return pkg

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
  # Refresh Index
  # ---

  pkg_map = dict()
  if args.index_dir is not None and args.refresh:
    old_pkgs, aliases = load_index(args.index_dir)
    logging.info(f"found {len(old_pkgs)} existing packages")
    repo_ids = filter(None, map(github_repo_id, old_pkgs))
    for (oldPkg, repo) in zip(old_pkgs, query_repo_data(repo_ids)):
      if repo['id'] in pkg_map:
        pkg = pkg_map[repo['id']]
      else:
        pkg = pkg_map[repo['id']] = pkg_of_repo(repo)
      old_pathname = oldPkg['fullName'].lower()
      new_pathname = pkg['fullName'].lower()
      if old_pathname != new_pathname:
        old_path = os.path.join(args.index_dir, oldPkg['owner'].lower(), oldPkg['name'].lower())
        if os.path.isdir(old_path):
          new_path = os.path.join(args.index_dir, pkg['owner'].lower(), pkg['name'].lower())
          if os.path.isdir(new_path):
            logging.info(f"merge: '{old_pathname}' -> '{new_pathname}'")
            oldBuilds = load_builds(os.path.join(old_path, 'builds.json'))
            newBuilds = load_builds(os.path.join(new_path, 'builds.json'))
            builds = insert_build_results(oldBuilds, newBuilds)
            with open(os.path.join(new_path, 'builds.json'), 'w') as f:
              json.dump(builds, f, indent=2)
            shutil.rmtree(old_path)
          else:
            logging.info(f"rename: '{old_pathname}' -> '{new_pathname}'")
            if os.path.isfile(new_path):
              os.remove(new_path)
              del aliases[new_pathname]
            os.renames(old_path, new_path)
        aliases[old_pathname] = new_pathname
      alias = repo['nameWithOwner'].lower()
      if alias not in aliases and alias != new_pathname:
        owner, name = repo['nameWithOwner'].split('/')
        repo_path = os.path.join(args.index_dir, owner.lower(), name.lower())
        if not os.path.exists(repo_path):
          logging.info(f"alias: '{alias}' -> '{new_pathname}'")
          aliases[alias] = new_pathname
  else:
    aliases = dict()

  # ---
  # Query New Repos
  # ---

  deprecatedIds = set()
  licenses = query_licenses()
  def curate(repo: Repo):
    if repo['nameWithOwner'] in exclusions or repo['stargazerCount'] <= 1:
      return False
    spdxId = filter_license(repo['licenseInfo'])
    if spdxId is not None:
      license = licenses[spdxId]
      if license is None:
        logging.error(f"unknown SPDX ID '{spdxId}'")
        return False
      if license.get('isDeprecatedLicenseId', False) and spdxId not in deprecatedIds:
        logging.warning(f"GitHub is using deprecated SPDX ID '{spdxId}'")
        deprecatedIds.add(spdxId)
      return license.get('isOsiApproved', False)
    return False

  newPkgs: list[Package] = list()
  limit = (0 if args.refresh else 100) if args.limit is None else args.limit
  if limit != 0:
    repo_ids = query_lake_repos(limit)
    logging.info(f"found {len(repo_ids)} candidate repositories with root Lake manifests")
    repos = query_repo_data(repo_ids)
    if len(pkg_map) != 0:
      repoMap = dict((repo['id'], repo) for repo in repos)
      newIds = set(repoMap.keys()).difference(pkg_map.keys())
      repos = list(map(repoMap.__getitem__, newIds))
      logging.info(f"{len(repos)} candidate repositories not in index")
    newPkgs = list(map(pkg_of_repo, filter(curate, repos)))
    note = 'notable new' if len(pkg_map) != 0 else 'notable'
    logging.info(f"found {len(newPkgs)} {note} OSI-licensed packages")

  # ---
  # Output Results
  # ---

  pkgs = itertools.chain(pkg_map.values(), newPkgs)
  pkgs = list(sorted(pkgs, key=lambda pkg: pkg['stars'], reverse=True))
  if len(pkg_map) != 0:
    logging.info(f"indexed {len(pkgs)} total packages")

  if args.output_manifest is not None:
    with open(args.output_manifest, 'w') as f:
      json.dump(pkgs, f, indent=2)

  if args.index_dir is not None:
    for pkg in pkgs:
      pkg_dir = os.path.join(args.index_dir, pkg['owner'].lower(), pkg['name'].lower())
      if os.path.isfile(pkg_dir):
        os.remove(pkg_dir)
        alias = f"{pkg['owner'].lower()}/{pkg['name'].lower()}"
        del aliases[alias]
      os.makedirs(pkg_dir, exist_ok=True)
      with open(os.path.join(pkg_dir, "metadata.json"), 'w') as f:
        json.dump(pkg, f, indent=2)
        f.write("\n")
    flatten_aliases(aliases)
    for alias, target in aliases.items():
      owner, name = alias.split('/')
      owner_dir = os.path.join(args.index_dir, owner)
      alias_path = os.path.join(owner_dir, name)
      if os.path.isdir(alias_path):
        logging.warning(f"package located at '{alias}': could not write alias '{alias}' -> '{target}'")
      else:
        os.makedirs(owner_dir, exist_ok=True)
        with open(alias_path, 'w') as f:
          f.write(target)
          f.write("\n")

  if args.output_manifest is not None:
    with open(args.output_manifest, 'w') as f:
      json.dump(pkgs, f, indent=2)

  if args.output_manifest is None and args.index_dir is None:
    print(json.dumps(pkgs, indent=2))
