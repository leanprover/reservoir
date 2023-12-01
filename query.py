#!/usr/bin/env python3
from datetime import datetime
import argparse
import itertools
import os
import subprocess
import json
import logging

# from https://antonz.org/page-iterator/
def paginate(iterable, page_size):
  it = iter(iterable)
  slicer = lambda: list(itertools.islice(it, page_size))
  return iter(slicer, [])

def run_cmd(*args: str) -> bytes:
  child = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if child.returncode != 0:
    raise RuntimeError(child.stderr.decode().strip())
  elif len(child.stderr) > 0:
    logging.error(child.stderr.decode())
  return child.stdout

REPO_QUERY="""
query($repoIds: [ID!]!) {
  nodes(ids: $repoIds) {
    ... on Repository {
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
    out = run_cmd(
      'gh', 'api', 'graphql',
      '-f', f'query={REPO_QUERY}', *fields
    )
    results = results + json.loads(out)['data']['nodes']
  return results

# NOTE: GitHub limits code searches to 10 requests/min, which is 1000 results.
# Thus, the strategy used here will need to change when we hit that limit.
def query_lake_repos(limit: int) -> 'list[str]':
  query='filename:lakefile.lean path:/'
  if limit == 0:
    out = run_cmd(
      'gh', 'api', 'search/code',
      '--paginate', '--cache', '1h',
      '-X', 'GET', '-f', f'q={query}',
      '-q', '.items[] | .repository.node_id'
    )
  else:
    out = run_cmd(
      'gh', 'search', 'code', *query.split(' '), '-L', str(limit),
      '--json', 'path,repository', '-q', '.[] | .repository.id'
    )
  return out.decode().splitlines()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('-L', '--limit', type=int, default=100,
    help='(max) number of results to query from GitHub (0 for no limit)')
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

  if args.verbosity == 0:
    level = logging.CRITICAL
  elif args.verbosity == 1:
    level = logging.INFO
  else:
    level = logging.DEBUG
  logging.basicConfig(level=level, format='%(levelname)s: %(message)s')

  exclusions = set()
  with open(args.exclusions, 'r') as f:
    for line in f: exclusions.add(line.strip())

  fetchedAt = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
  def enrich(repo: dict):
    repo['fullName'] = repo.pop('nameWithOwner')
    repo['id'] = repo['fullName'].replace('-', '--').replace('/', '-')
    repo['owner'], repo['name'] = repo['fullName'].split('/')
    info = repo.pop('licenseInfo')
    spdxId = None if info is None else info['spdxId']
    spdxId = None if spdxId in ['NONE', 'NOASSERTION'] else spdxId
    repo['license'] = spdxId
    repo['homepage'] = repo.pop('homepageUrl')
    repo['stars'] = repo.pop('stargazerCount')
    repo['updatedAt'] = max(repo['updatedAt'], repo.pop('pushedAt'))
    repo['fetchedAt'] = fetchedAt
    return repo

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
      if not os.path.exists(pkg_dir):
        os.makedirs(pkg_dir)
      with open(os.path.join(pkg_dir, "metadata.json"), 'w') as f:
        f.write(json.dumps(pkg, indent=2))

  if args.output_manifest is None:
    print(json.dumps(pkgs, indent=2))
  else:
    with open(args.output_manifest, 'w') as f:
      f.write(json.dumps(pkgs, indent=2))
