#!/usr/bin/env python3
from utils import *
from typing import Container, TypedDict
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
  rateLimit {
    cost
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

GH_TOKEN = os.environ['GH_TOKEN']
GH_API_SESSION = requests.Session()
GH_API_HEADERS = {
  "User-Agent": "Reservoir",
  "Accept":"application/vnd.github+json",
  "Authorization": f"Bearer {GH_TOKEN}",
  "X-GitHub-Api-Version": "2022-11-28",
  "X-Github-Next-Global-ID": "1",
}

def query_github_api(endpoint: str, fields: dict | None = None, method="GET") -> dict:
  url=f"https://api.github.com/{endpoint}"
  if method == "GET":
    resp = GH_API_SESSION.get(url, params=fields, headers=GH_API_HEADERS)
  else:
    resp = GH_API_SESSION.post(url, data=json.dumps(fields), headers=GH_API_HEADERS)
  resource = resp.headers.get('x-ratelimit-resource', '?')
  usage = f"{resp.headers.get('x-ratelimit-used', '?')}/{resp.headers.get('x-ratelimit-limit', '?')}"
  reset = resp.headers.get('x-ratelimit-reset', '?')
  if reset != '?':
    reset = fmt_timestamp(int(reset))
  logging.debug(f"GitHub API usage: {usage} of {resource}, resets {reset}")
  try:
    content = resp.json()
  except requests.exceptions.JSONDecodeError:
    raise RuntimeError(f"GitHub API request failed ({resp.status_code}); malformed response: {resp.text}")
  if resp.status_code != 200:
    raise RuntimeError(f"GitHub API request failed ({resp.status_code}): {content.get('message', resp.text)}")
  return content

def query_github_graphql(query: str, variables: dict) -> dict:
  return query_github_api("graphql", {"query": query, "variables": variables}, "POST")

def query_github_results(limit: int, endpoint: str, params: dict) -> Iterable[dict]:
  params['page'] = 1
  params['per_page'] = 100
  while limit > 100:
    res = query_github_api(endpoint, params)
    yield from res['items']
    params['page'] += 1
    limit -= 100
  if limit != 0:
    params['per_page'] = limit
    res = query_github_api(endpoint, params)
    yield from res['items']

def query_repo_data(repo_ids: 'Iterable[str]') -> 'Iterable[Repo | None]':
  for page in paginate(repo_ids, 100):
    data = query_github_graphql(REPO_QUERY, {"repoIds": page})['data']
    logging.debug(f"GitHub GraphQL request cost: {data['rateLimit']['cost']}")
    yield from data['nodes']

def query_lake_repos(limit: int) -> 'list[str]':
  # NOTE: For some reason, the GitHub rate limit is currently (07-08-24) off by one.
  rate_limit = query_github_api("rate_limit")['resources']['code_search']
  if limit < 0:
    # NOTE: GitHub limits code searches to 10 requests/min, which is 1000 results.
    # Thus, the strategy used here will need to change when we hit that limit.
    limit = (rate_limit['limit']-1)*100
  gh_limit = (rate_limit['remaining']-1)*100
  if limit > gh_limit:
    reset = fmt_timestamp(int(rate_limit['reset']))
    logging.warning(f"due to API rate limit, restricted results to a max of {gh_limit} instead of {limit}; resets {reset}")
    limit = gh_limit
  logging.debug(f"querying at most {limit} repositories")
  query='filename:lake-manifest.json path:/'
  items = query_github_results(limit, "search/code", {"q": query})
  return [item['repository']['node_id'] for item in items]

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
        pkg['name'] = unescape_name(name)
        pkg['fullName'] = f"{pkg['owner']}/{name}"
    except json.JSONDecodeError:
      pass
  return pkg

def move_package(index_dir: str, old_relpath: str, new_relpath: str):
  old_path = os.path.join(index_dir, old_relpath)
  if os.path.isdir(old_path):
    new_path = os.path.join(index_dir, new_relpath)
    if os.path.isdir(new_path):
      logging.info(f"Index merge: '{old_relpath}' -> '{new_relpath}'")
      old_builds = load_builds(os.path.join(old_path, 'builds.json'))
      new_builds = load_builds(os.path.join(new_path, 'builds.json'))
      builds = insert_build_results(old_builds, new_builds)
      with open(os.path.join(new_path, 'builds.json'), 'w') as f:
        json.dump(builds, f, indent=2)
      shutil.rmtree(old_path)
    else:
      logging.info(f"Index rename: '{old_relpath}' -> '{new_relpath}'")
      if os.path.isfile(new_path):
        os.remove(new_path)
      os.renames(old_path, new_path)

def packages_with_repos(pkgs: Iterable[Package]):
  ids = list[str]()
  pkgs = list[Package]()
  for pkg in pkgs:
    id = github_repo_id(pkg)
    if id is not None:
      ids.append(id)
      pkgs.append(pkg)
  return zip(pkgs, query_repo_data(ids))

def refresh_index(index_dir: str):
  pkgs = dict[str, Package]()
  old_pkgs, aliases = load_index(index_dir)
  logging.info(f"Found {len(old_pkgs)} existing packages")
  for (old_pkg, repo) in packages_with_repos(old_pkgs):
    if repo is None:
      logging.error(f"{old_pkg['fullName']}: repository ID not found on GitHub: {id}")
      continue
    if repo['id'] in pkgs:
      new_pkg = pkgs[repo['id']]
    else:
      new_pkg = pkgs[repo['id']] = pkg_of_repo(repo)
    old_relpath = package_relpath(old_pkg)
    new_relpath = package_relpath(new_pkg)
    if old_relpath != new_relpath:
      move_package(index_dir, old_relpath, new_relpath)
      logging.info(f"Index alias: '{old_pkg['fullName']}' -> '{new_pkg['fullName']}'")
      aliases[old_pkg['fullName']] = new_pkg
    repo_alias = repo['nameWithOwner']
    if alias_relpath(repo_alias) != new_relpath:
      if repo_alias not in aliases:
        logging.info(f"Index alias: '{repo_alias}' -> '{new_pkg['fullName']}'")
      aliases[repo_alias] = new_pkg  # always set to ensure canonical casing
  return pkgs, aliases

def filter_indexed_repos(repos: 'Iterable[Repo]', ids: 'Iterable[str]') -> 'Iterable[Repo]':
  """Skip index repositories in `repos`"""
  repo_map = dict((repo['id'], repo) for repo in repos)
  new_ids = set(repo_map.keys()).difference(ids)
  return map(repo_map.__getitem__, new_ids)

def pkgs_of_repos(repos: 'Iterable[Repo]', excluded_pkgs: 'Container[str]' = set()) -> 'Iterable[Package]':
  licenses = query_licenses()
  deprecated_ids = set[str]()
  def curate(repo: Repo):
    if repo['nameWithOwner'] in excluded_pkgs or repo['stargazerCount'] <= 1:
      return False
    spdxId = filter_license(repo['licenseInfo'])
    if spdxId is not None:
      license = licenses[spdxId]
      if license is None:
        logging.error(f"GitHub is using unknown SPDX ID '{spdxId}'")
        return False
      if license.get('isDeprecatedLicenseId', False) and spdxId not in deprecated_ids:
        logging.warning(f"GitHub is using deprecated SPDX ID '{spdxId}'")
        deprecated_ids.add(spdxId)
      return license.get('isOsiApproved', False)
    return False
  return map(pkg_of_repo, filter(curate, repos))

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
    indexed_pkgs, aliases = refresh_index(args.index_dir)
  else:
    indexed_pkgs = dict[str, Package]()
    aliases = CaseInsensitiveDict[Package]()

  # Query New Repos
  new_pkgs = list[Package]()
  limit = (0 if args.refresh else 100) if args.limit is None else args.limit
  if limit != 0:
    indexed_ids = indexed_pkgs.keys()
    repo_ids = query_lake_repos(limit)
    logging.info(f"Found {len(repo_ids)} candidate repositories with root Lake manifests")
    repos = filter(None, query_repo_data(repo_ids))
    if len(indexed_ids) != 0:
      repos = list(filter_indexed_repos(repos, indexed_ids))
      logging.info(f"{len(repos)} candidate repositories not in index")
    new_pkgs = list(pkgs_of_repos(repos, exclusions))
  note = 'notable new' if len(indexed_pkgs) != 0 else 'notable'
  logging.info(f"Found {len(new_pkgs)} {note} OSI-licensed packages")

  # Finalize Index
  pkgs = itertools.chain(indexed_pkgs.values(), new_pkgs)
  pkgs = list(sorted(pkgs, key=lambda pkg: pkg['stars'], reverse=True))
  if len(indexed_pkgs) != 0:
    logging.info(f"Indexed {len(pkgs)} total packages")

  # ---
  # Output Results
  # ---

  if args.output_manifest is not None:
    with open(args.output_manifest, 'w') as f:
      json.dump(pkgs, f, indent=2)

  if args.index_dir is not None:
    write_index(args.index_dir, pkgs, aliases)

  if args.output_manifest is not None:
    with open(args.output_manifest, 'w') as f:
      json.dump(pkgs, f, indent=2)

  if args.output_manifest is None and args.index_dir is None:
    print(json.dumps(pkgs, indent=2))
