#!/usr/bin/env python3
from utils import *
from typing import TypedDict
import argparse
import re
import os
import json
import logging
import requests

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
    }
  }
}
"""

class RepoDefaultBranchRef(TypedDict):
  name: str

class RepoLicense(TypedDict):
  spdxId: str

class Repo(TypedDict):
  id: str
  nameWithOwner: str
  description: str
  license: RepoLicense
  createdAt: str
  updatedAt: str
  pushedAt: str
  url: str
  homepageUrl: str
  stargazerCount: int
  defaultBranchRef: RepoDefaultBranchRef

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
  query='filename:lakefile.lean path:/'
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

def filter_falsy(value):
  return value if value else None

def filter_ws(value: str | None):
  value: str | None = value
  if value is not None:
    value = filter_falsy(value.strip())
  return value

if __name__ == "__main__":
  script_dir = os.path.dirname(os.path.realpath(__file__))
  default_exclusions = os.path.join(script_dir, "index-exclusions.txt")
  parser = argparse.ArgumentParser()
  parser.add_argument('-L', '--limit', type=int, default=100,
    help='(max) number of results to query from GitHub (<= 0 for no limit)')
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

  def pkg_of_repo(repo: Repo) -> Package:
    license = repo['licenseInfo']
    if license is not None: license = license['spdxId']
    if license in ['NONE', 'NOASSERTION']: license = None
    owner, name = repo['nameWithOwner'].split('/')
    return {
      'name': name,
      'owner': owner,
      'fullName': repo['nameWithOwner'],
      'description': filter_ws(repo['description']),
      'homepage': filter_ws(repo['homepageUrl']),
      'license': license,
      'createdAt': repo['createdAt'],
      'updatedAt':  max(repo['updatedAt'], repo['pushedAt']),
      'stars': repo['stargazerCount'],
      'sources': [{
        'type': 'git',
        'host': 'github',
        'id': repo['id'],
        'fullName': repo['nameWithOwner'],
        'repoUrl': repo['url'],
        'gitUrl': repo['url'],
        'defaultBranch': repo['defaultBranchRef']['name'],
      }],
    }

  deprecatedIds = set()
  licenses = query_licenses()
  def curate(pkg: Package):
    if pkg['fullName'] in exclusions or pkg['stars'] <= 1:
      return False
    spdxId = pkg['license']
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

  def github_repo(pkg: Package) -> Source:
    return next(filter(lambda src: src['host'] == 'github', pkg['sources']), None)

  ghuc = requests.Session()
  def query_repo_manifest(repo: Source) -> dict | None:
    url=f"https://raw.githubusercontent.com/{repo['fullName']}/{repo.get('defaultBranch', 'HEAD')}/lake-manifest.json"
    logging.debug(f"fetching Lake manifest from {url}")
    response = ghuc.get(url, allow_redirects=True)
    if response.status_code == 404:
      return None
    if response.status_code != 200:
      raise RuntimeError(f"failed to fetch Lake manifest ({response.status_code})")
    return json.loads(response.content.decode())

  FRENCH_QUOTE_PATTERN = re.compile('[«»]')
  def enrich_with_manifest(pkg: Package) -> Package:
    repo = github_repo(pkg)
    if repo is None: return pkg
    manifest = query_repo_manifest(repo)
    if manifest is None: return pkg
    name: str | None = manifest.get('name', None)
    if name is not None:
      name = FRENCH_QUOTE_PATTERN.sub('', name)
      pkg['name'] = name
      pkg['fullName'] = f"{pkg['owner']}/{name}"
    return pkg

  repos = query_lake_repos(args.limit)
  logging.info(f"found {len(repos)} repositories with root lakefiles")

  repos = query_repo_data(repos)
  pkgs = map(pkg_of_repo, repos)
  pkgs = filter(curate, pkgs)
  pkgs = map(enrich_with_manifest, pkgs)
  pkgs = sorted(pkgs, key=lambda pkg: pkg['stars'], reverse=True)
  pkgs = list(pkgs)
  logging.info(f"found {len(pkgs)} notable OSI-licensed repositories")

  if args.index_dir is not None:
    for pkg in pkgs:
      pkg_dir = os.path.join(args.index_dir, pkg['owner'], pkg['name'])
      os.makedirs(pkg_dir, exist_ok=True)
      with open(os.path.join(pkg_dir, "metadata.json"), 'w') as f:
        json.dump(pkg, f, indent=2)
        f.write("\n")

  if args.output_manifest is not None:
    with open(args.output_manifest, 'w') as f:
      json.dump(pkgs, f, indent=2)

  if args.output_manifest is None and args.index_dir is None:
    print(json.dumps(pkgs, indent=2))
