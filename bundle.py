#!/usr/bin/env python3
from datetime import datetime
import argparse
import subprocess
import json

RELEASE_REPO = 'leanprover/lean4'
def query_toolchain_releases():
  child = subprocess.run([
    'gh', 'api', '--paginate',
    f'repos/{RELEASE_REPO}/releases',
    '-q', '.[] | .tag_name'
  ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if child.returncode != 0:
    raise RuntimeError(child.stderr.decode().strip())
  return [f'{RELEASE_REPO}:{ver}' for ver in child.stdout.decode().splitlines()]

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('index',
    help="package metadata")
  parser.add_argument('results',
    help="testbed results")
  parser.add_argument('-o', '--output',
    help='file to output the bundle manifest')
  args = parser.parse_args()

  with open(args.index, 'r') as f:
    index: 'dict[str, any]' = json.load(f)

  with open(args.results, 'r') as f:
    results: 'dict[str, dict[str, any]]' = json.load(f)

  repos: 'dict[str, any]' = dict()
  for repo in index['packages']:
    repos[repo['id']] = repo
    repos[repo['id']]['builds'] = list()
  for (id, result) in results.items():
    repos[id]['builds'].insert(0, result)

  data = {
    'indexedAt': index['fetchedAt'],
    'bundledAt': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    'toolchains': query_toolchain_releases(),
    'packages': list(repos.values())
  }
  if args.output is None:
    print(json.dumps(data))
  else:
    with open(args.output, 'w') as f:
      f.write(json.dumps(data))
