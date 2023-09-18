#!/usr/bin/env python3
import argparse
import json

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('index',
    help="repository metadata")
  parser.add_argument('results',
    help="testbed results")
  parser.add_argument('-o', '--output',
    help='file to output the bundle manifest')
  args = parser.parse_args()

  with open(args.index, 'r') as f:
    index = json.load(f)

  with open(args.results, 'r') as f:
    results = json.load(f)

  repos = dict()
  for repo in index['matrix']:
    repos[repo['id']] = repo
    repos[repo['id']]['outcome'] = None
  for result in results['matrix']:
    if result['id'] in repos:
      repos[result['id']]['outcome'] = result['outcome']

  data = {
    "buildId": results['buildId'],
    'builtAt': results['builtAt'],
    'toolchain': results['toolchain'],
    'fetchedAt': index['fetchedAt'],
    'matrix': list(repos.values())
  }
  if args.output is None:
    print(json.dumps(data))
  else:
    with open(args.output, 'w') as f:
      f.write(json.dumps(data))
