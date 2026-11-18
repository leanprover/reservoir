import os
import json
import time
import random
import logging
import requests
from datetime import datetime, timedelta, timezone
from typing import Callable, Container, Collection, TypedDict, Any
from utils.index import *
from utils.core import *

REPO_QUERY="""
query($repoIds: [ID!]!) {
  nodes(ids: $repoIds) {
    ... on Repository {
      id
      nameWithOwner
      description
      repositoryTopics(first:100) {
        nodes {
          topic {
            name
          }
        }
      }
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

class GitHubTopic(TypedDict):
  name: str

class RepoTopic(TypedDict):
  topic: GitHubTopic

class RepoTopics(TypedDict):
  nodes: list[RepoTopic]

class Repo(TypedDict):
  id: str
  nameWithOwner: str
  description: str
  repositoryTopics: RepoTopics
  licenseInfo: RepoLicense | None
  createdAt: str
  updatedAt: str
  pushedAt: str
  url: str
  homepageUrl: str
  stargazerCount: int
  defaultBranchRef: RepoDefaultBranchRef

GH_API_SESSION = requests.Session()
GH_API_HEADERS = {
  "User-Agent": "Reservoir",
  "Accept":"application/vnd.github+json",
  "X-GitHub-Api-Version": "2022-11-28",
  "X-Github-Next-Global-ID": "1",
}
GH_TOKEN = os.getenv('GH_TOKEN', None)
if GH_TOKEN is not None:
  GH_API_HEADERS['Authorization'] = f"Bearer {GH_TOKEN}"

def query_github_api(endpoint: str, fields: dict[str, Any] | None = None, method: str = "GET") -> Any:
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

def query_github_graphql(query: str, variables: dict) -> Any:
  return query_github_api("graphql", {"query": query, "variables": variables}, "POST")

def query_github_results(limit: int, endpoint: str, params: dict[str, Any]) -> Iterable[Any]:
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

def query_github_graphql_data(query: str, variables: dict, what: str) -> Any:
  """GraphQL `data`, with retries. Some failures arrive as HTTP 200 with `errors` and no `data`."""
  def request():
    resp = query_github_graphql(query, variables)
    data = resp.get('data')
    if data is None:
      raise RuntimeError(f"GitHub GraphQL request failed: {resp.get('errors')}")
    return data
  return with_retries(request, what)

def query_repo_data(items: Iterable[str]) -> Iterable[Repo | None]:
  for page in paginate(items, 100):
    data = query_github_graphql_data(REPO_QUERY, {"repoIds": page}, "GitHub GraphQL repository query")
    logging.debug(f"GitHub GraphQL request cost: {data['rateLimit']['cost']}")
    yield from data['nodes']

def query_repos(ids: Iterable[str]) -> dict[str, Repo]:
  repos = dict[str, Repo]()
  for id, repo in zip(ids, query_repo_data(ids)):
    if repo is None:
      logging.error(f"Repository ID '{id}' not found on GitHub")
    else:
      repos[id] = repo
  return repos

def query_lake_repos(limit: int, known_repos: Container[str] = set()) -> list[str]:
  # NOTE: For some reason, the GitHub rate limit is currently (07-08-24) off by one.
  rate_limit = query_github_api("rate_limit")['resources']['code_search']
  unbounded = limit < 0
  if unbounded:
    # NOTE: GitHub limits code searches to 10 requests/min, which is 1000 results.
    # Thus, an unbounded query also sweeps a date-windowed repository search (below).
    limit = (rate_limit['limit']-1)*100
  gh_limit = (rate_limit['remaining']-1)*100
  if limit > gh_limit:
    reset = fmt_timestamp(int(rate_limit['reset']))
    logging.warning(f"Due to API rate limit, restricted results to a max of {gh_limit} instead of {limit}; resets {reset}")
    limit = gh_limit
  logging.debug(f"Querying at most {limit} repositories")
  query='filename:lake-manifest.json path:/'
  items = query_github_results(limit, "search/code", {"q": query})
  repo_ids = [item['repository']['node_id'] for item in items]
  if unbounded:
    # The code search above is capped at 1000 results (and is not sortable),
    # so also sweep repository search, which can be partitioned by creation date.
    # A failure here should not discard the code search results.
    try:
      # Repository search returns the same (new-style) node IDs as the index, so known repos can be skipped
      # here. Code search returns legacy IDs, so overlap with it is resolved later, by canonical ID.
      window_ids = [id for id in query_windowed_lean_repos() if id not in known_repos]
      found = query_root_manifest_repos(window_ids)
      logging.info(f"{len(found)} additional repositories with root Lake manifests found by windowed search")
      repo_ids.extend(found)
    except RuntimeError:
      logging.exception("Windowed repository search failed; using code search results only")
  # Unsorted code search pages can overlap, so deduplicate (preserving order).
  # IDs from the two searches differ in format; callers deduplicate by canonical ID after querying data.
  return list(dict.fromkeys(repo_ids))

# GitHub's launch; bisection makes early, sparse windows cheap.
WINDOWED_SEARCH_START = datetime(2008, 1, 1, tzinfo=timezone.utc)
WINDOWED_SEARCH_QUERY = 'language:Lean stars:>1'
GH_SEARCH_CAP = 1000

def with_retries(request: Callable[[], T], what: str, attempts: int = 5, base: float = 4.0) -> T:
  """
  Runs `request`, retrying on `RuntimeError` with exponential backoff and full jitter.
  The waits (up to 4, 8, 16, 32 seconds by default) span about a minute,
  which is what GitHub asks clients to wait after a secondary rate limit.
  """
  for attempt in range(attempts):
    try:
      return request()
    except RuntimeError as e:
      if attempt + 1 == attempts:
        raise
      delay = random.uniform(0, base * 2**attempt)
      logging.warning(f"{what} failed ({e}); retrying in {delay:.1f}s")
      time.sleep(delay)
  raise AssertionError("unreachable")

def wait_for_search_quota():
  # Querying the rate limit does not count against it.
  # Keep one request in reserve, as the reported limit has been observed to be off by one.
  rate_limit = query_github_api("rate_limit")['resources']['search']
  if rate_limit['remaining'] < 2:
    wait = max(0, int(rate_limit['reset']) - int(time.time())) + 1
    logging.debug(f"Search rate limit reached; waiting {wait}s")
    time.sleep(wait)

def query_search_repositories(query: str, page: int = 1) -> Any:
  def request():
    wait_for_search_quota()
    return query_github_api("search/repositories", {"q": query, "per_page": 100, "page": page})
  res = with_retries(request, "GitHub repository search")
  if res.get('incomplete_results', False):
    logging.warning(f"GitHub returned incomplete results for '{query}' (page {page})")
  return res

def query_windowed_lean_repos(
  start: datetime = WINDOWED_SEARCH_START, end: datetime | None = None
) -> list[str]:
  """
  Node IDs of all repositories matching `WINDOWED_SEARCH_QUERY`.
  A search returns at most 1000 results, so the creation-date range is bisected
  until each window holds fewer than that.
  """
  if end is None:
    end = datetime.now(timezone.utc).replace(microsecond=0)
  repo_ids = list[str]()
  windows = [(start, end)]
  while windows:
    a, b = windows.pop()
    query = f"{WINDOWED_SEARCH_QUERY} created:{fmt_utc_iso(a)}..{fmt_utc_iso(b)}"
    res = query_search_repositories(query)
    total = res['total_count']
    if total >= GH_SEARCH_CAP and b - a > timedelta(seconds=1):
      mid = (a + (b - a) / 2).replace(microsecond=0)
      # Ranges are inclusive, so the halves must not share an endpoint.
      windows.append((mid + timedelta(seconds=1), b))
      windows.append((a, mid))
      continue
    if total >= GH_SEARCH_CAP:
      logging.warning(f"Search window '{query}' exceeds {GH_SEARCH_CAP} results; some will be missed")
    items = res['items']
    pages = (min(total, GH_SEARCH_CAP) + 99) // 100
    for page in range(2, pages + 1):
      items.extend(query_search_repositories(query, page)['items'])
    logging.debug(f"{len(items)} repositories created {fmt_utc_iso(a)}..{fmt_utc_iso(b)}")
    repo_ids.extend(item['node_id'] for item in items)
  logging.info(f"{len(repo_ids)} repositories found by windowed search")
  return repo_ids

ROOT_MANIFEST_QUERY="""
query($repoIds: [ID!]!) {
  nodes(ids: $repoIds) {
    ... on Repository {
      id
      lakeManifest: object(expression: "HEAD:lake-manifest.json") {
        __typename
      }
    }
  }
  rateLimit {
    cost
  }
}
"""

def query_root_manifest_repos(repo_ids: Iterable[str]) -> list[str]:
  """Filters repositories to those with a `lake-manifest.json` at the root of their default branch."""
  found = list[str]()
  # Each `object` lookup is a git read, so large pages can exceed GitHub's GraphQL timeout (HTTP 502).
  for page in paginate(repo_ids, 25):
    data = query_github_graphql_data(ROOT_MANIFEST_QUERY, {"repoIds": page}, "GitHub GraphQL manifest check")
    logging.debug(f"GitHub GraphQL request cost: {data['rateLimit']['cost']}")
    for node in data['nodes']:
      if node is not None and node.get('lakeManifest') is not None:
        found.append(node['id'])
  return found

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
def query_licenses(url: str = SPDX_DATA_URL):
  logging.debug(f"Fetching SPDX license data from {url}")
  response = requests.get(url, allow_redirects=True)
  if response.status_code != 200:
    raise RuntimeError(f"Failed to fetch SPDX license data ({response.status_code})")
  license_list: list[License] = json.loads(response.content.decode())['licenses']
  licenses = dict[str, License]()
  for license in license_list:
    licenses[license['licenseId']] = license
  return licenses

def filter_license(license: str | None) -> str | None:
  if filter_ws(license) is None: return None
  if license in ['NONE', 'NOASSERTION']: return None
  return license

def license_id(license: RepoLicense | None) -> str | None:
  if license is None: return None
  if license['spdxId'] in ['NONE', 'NOASSERTION']: return None
  return license['spdxId']

def filter_repo_ids(repos: 'Iterable[Repo]', ids: 'Iterable[str]') -> 'Iterable[Repo]':
  """Filter repositories with `ids` from `repos`"""
  repo_map = dict((repo['id'], repo) for repo in repos)
  new_ids = set(repo_map.keys()).difference(ids)
  return map(repo_map.__getitem__, new_ids)

def src_of_repo(repo: Repo) -> GitHubSrc:
  return {
    'type': 'git',
    'host': 'github',
    'id': repo['id'],
    'fullName': repo['nameWithOwner'],
    'repoUrl': repo['url'],
    'gitUrl': repo['url'],
    'defaultBranch': repo['defaultBranchRef']['name'],
  }

def metadata_of_repo(repo: Repo) -> PackageMetadata:
  owner, name = repo['nameWithOwner'].split('/')
  keywords = (node['topic']['name'] for node in repo['repositoryTopics']['nodes'])
  keywords = [k for k in keywords if k not in ['lean', 'lean4']]
  return {
    'name': name,
    'owner': owner,
    'fullName': repo['nameWithOwner'],
    'description': filter_ws(repo['description']),
    "keywords": keywords,
    'homepage': filter_ws(repo['homepageUrl']),
    'license': license_id(repo['licenseInfo']),
    'createdAt': repo['createdAt'],
    'updatedAt': max(repo['updatedAt'], repo['pushedAt']),
    'stars': repo['stargazerCount'],
    'sources': [cast(PackageSrc, src_of_repo(repo))],
  }

def package_of_repo(repo: Repo) -> Package:
  return package_of_metadata(metadata_of_repo(repo))

def curate_repos(repos: Iterable[Repo], excluded_pkgs: Container[str] = set(), check_stars: bool = True) -> Iterable[Repo]:
  licenses = query_licenses()
  deprecated_ids = set[str]()
  def curate(repo: Repo):
    if repo['nameWithOwner'] in excluded_pkgs:
      return False
    if check_stars and repo['stargazerCount'] <= 1:
      return False
    spdxId = license_id(repo['licenseInfo'])
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
  return filter(curate, repos)

def add_repo_metadata(pkg: Package, repo: Repo):
  pkg.update(cast(Any, metadata_of_repo(repo)))

def query_new_repos(limit: int, indexed_repos: Collection[str], exclusions: Container[str] = set()) -> list[Repo]:
  if limit == 0: return []
  logging.info(f"Searching for new Lean/Lake repositories")
  repo_ids = query_lake_repos(limit, indexed_repos)
  logging.info(f"{len(repo_ids)} candidate repositories with root Lake manifests")
  # Code search returns legacy node IDs, so deduplicate and filter by the canonical IDs GraphQL returns.
  repos = list({repo['id']: repo for repo in query_repo_data(repo_ids) if repo is not None}.values())
  if len(indexed_repos) != 0:
    repos = [repo for repo in repos if repo['id'] not in indexed_repos]
    logging.info(f"{len(repos)} candidate repositories not in index")
  repos = list(curate_repos(repos, exclusions))
  note = 'notable new' if len(indexed_repos) != 0 else 'notable'
  logging.info(f"{len(repos)} {note} OSI-licensed repositories")
  return repos
