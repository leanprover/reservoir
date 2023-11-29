#!/usr/bin/env python3
from datetime import datetime
import argparse
import subprocess
import requests
import json
import logging

def query(limit: int):
  query = "language:Lean stars:>1 sort:stars"
  fields = ["fullName","description","license","createdAt","updatedAt","pushedAt","url","homepage","stargazersCount"]
  child = subprocess.run([
    "gh", "search", "repos",
    *query.split(' '), "-L", str(limit), "--json", ','.join(fields),
  ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if child.returncode != 0:
    raise RuntimeError(child.stderr.decode().strip())
  return json.loads(child.stdout)

def filter_lake(repo):
  repo = repo['fullName']
  url = f"https://raw.githubusercontent.com/{repo}/HEAD/lakefile.lean"
  logging.debug(f"querying {url}")
  code = requests.head(url, allow_redirects=True).status_code
  log = f"status {code} for repository {repo}"
  if code == 404:
    logging.debug(log)
    return False
  elif code == 200:
    logging.debug(log)
    return True
  else:
    logging.error(f"status {code} for repository {repo}")
    return False

def enrich(repo: dict):
  repo['id'] = repo['fullName'].replace("-", "--").replace("/", "-")
  repo['owner'], repo['name'] = repo['fullName'].split('/')
  repo['license'] = repo['license']['key']
  repo['stars'] = repo.pop('stargazersCount')
  repo['updatedAt'] = max(repo['updatedAt'], repo['pushedAt'])
  del repo['pushedAt']
  return repo

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('-L', '--limit', type=int, default=50,
    help='(max) number of results to query from GitHub')
  parser.add_argument('-X', '--exclusions', default="query-exclusions.txt",
    help='file containing repos to exclude')
  parser.add_argument('-o', '--output',
    help='file to output results')
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

  repos = query(args.limit)
  logging.info(f"found {len(repos)} (max {args.limit}) notable Lean repositories")
  repos = filter(lambda repo: repo['fullName'] not in exclusions, repos)
  repos = filter(filter_lake, repos)
  pkgs = map(enrich, repos)
  pkgs = list(pkgs)
  logging.info(f"found {len(pkgs)} notable Lean repositories with lakefiles")

  data = {
    'fetchedAt': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    'packages': pkgs
  }
  if args.output is None:
    print(json.dumps(data))
  else:
    with open(args.output, 'w') as f:
      f.write(json.dumps(data))
