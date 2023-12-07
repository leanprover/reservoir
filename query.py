#!/usr/bin/env python3
from utils import configure_logging, paginate, capture_cmd
from datetime import datetime
import argparse
import os
import json
import logging

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
    }
  }
}
"""

def query_repo_data(repoIds: 'list[str]') -> dict:
  results = list()
  for page in paginate(repoIds, 100):
    fields = list()
    for id in page:
      fields.append('-f')
      fields.append(f'repoIds[]={id}')
    out = capture_cmd(
      'gh', 'api', 'graphql',
      "-H", "X-Github-Next-Global-ID: 1",
      '-f', f'query={REPO_QUERY}', *fields
    )
    results = results + json.loads(out)['data']['nodes']
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

def filter_falsy(value):
  return value if value else None

def filter_ws(value: str | None):
  value: str | None = value
  if value is not None:
    value = filter_falsy(value.strip())
  return value


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('-L', '--limit', type=int, default=100,
    help='(max) number of results to query from GitHub (<= 0 for no limit)')
  parser.add_argument('-X', '--exclusions', default="query-exclusions.txt",
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

  def enrich(repo: dict):
    license = repo['licenseInfo']
    if license is not None: license = license['spdxId']
    if license in ['NONE', 'NOASSERTION']: license = None
    owner, name = repo['nameWithOwner'].split('/')
    id = repo['nameWithOwner'].replace('-', '--').replace('/', '-')
    return {
      'id': id,
      'name' : name,
      'owner': owner,
      'fullName': repo['nameWithOwner'],
      'description': filter_ws(repo['description']),
      'homepage': filter_ws(repo['homepageUrl']),
      'license': license,
      'createdAt': repo['createdAt'],
      'updatedAt':  max(repo['updatedAt'], repo['pushedAt']),
      'stars': repo['stargazerCount'],
      'sources': [{
        'host': 'github',
        'id': repo['id'],
        'fullName': repo['nameWithOwner'],
        'repoUrl': repo['url'],
        'gitUrl': repo['url'],
      }],
    }

  def curate(pkg: dict):
    return pkg['fullName'] not in exclusions and pkg['stars'] > 1

  repos = query_lake_repos(args.limit)
  logging.info(f"found {len(repos)} repositories with root lakefiles")

  repos = query_repo_data(repos)
  pkgs = map(enrich, repos)
  pkgs = filter(curate, pkgs)
  pkgs = sorted(pkgs, key=lambda pkg: pkg['stars'], reverse=True)
  pkgs = list(pkgs)
  logging.info(f"found {len(pkgs)} notable repositories")

  if args.index_dir is not None:
    for pkg in pkgs:
      pkg_dir = os.path.join(args.index_dir, pkg['owner'], pkg['name'])
      os.makedirs(pkg_dir, exist_ok=True)
      with open(os.path.join(pkg_dir, "metadata.json"), 'w') as f:
        f.write(json.dumps(pkg, indent=2))
        f.write("\n")

  if args.output_manifest is None:
    print(json.dumps(pkgs, indent=2))
  else:
    with open(args.output_manifest, 'w') as f:
      f.write(json.dumps(pkgs, indent=2))
