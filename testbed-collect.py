#!/usr/bin/env python3
from datetime import datetime
import json
import argparse
import os

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('results',
    help="directory containing testbed results")
  parser.add_argument('toolchain',
    help="Lean toolchain the results where built on")
  parser.add_argument('build_id', nargs='?', default=None,
    help="the testbed run ID")
  parser.add_argument('-m', '--matrix',
    help="matrix file within the results")
  parser.add_argument('-o', '--output',
    help='file to output the bundle manifest')
  args = parser.parse_args()

  matrix_file = args.matrix
  if matrix_file is None:
    matrix_file = os.path.join(args.results, 'matrix', 'matrix.json')

  with open(matrix_file, 'r') as f:
    repos = json.load(f)

  matrix = list()
  for repo in repos:
    result = dict()
    result['id'] = repo['id']
    outcome_file = os.path.join(args.results, repo['id'], 'outcome.txt')
    if os.path.exists(outcome_file):
      with open(outcome_file, 'r') as f:
        result['outcome'] = f.read().strip()
    else:
      result['outcome'] = None
    matrix.append(result)

  data = {
    "buildId": args.build_id,
    'builtAt': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    'toolchain': args.toolchain,
    'matrix': matrix
  }
  if args.output is None:
    print(json.dumps(data))
  else:
    with open(args.output, 'w') as f:
      f.write(json.dumps(data))
