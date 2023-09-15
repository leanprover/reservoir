#!/usr/bin/env python3
import json
import argparse
import os

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('results',
    help="directory containing testbed results")
  parser.add_argument('toolchain',
    help="Lean toolchain the results where built on")
  parser.add_argument('-m', '--matrix',
    help="matrix file within the results")
  parser.add_argument('-o', '--output',
    help='file to output the bundle manifest')
  args = parser.parse_args()

  matrix_file = args.matrix
  if matrix_file is None:
    matrix_file = os.path.join(args.results, 'matrix', 'matrix.json')

  with open(matrix_file, 'r') as f:
    matrix = json.load(f)

  for repo in matrix:
    outcome_file = os.path.join(args.results, repo['id'], 'outcome.txt')
    if os.path.exists(outcome_file):
      with open(outcome_file, 'r') as f:
        repo['outcome'] = f.read().strip()
    else:
      repo['outcome'] = "missing"

  bundle = {'toolchain': args.toolchain, 'matrix': matrix}
  if args.output is None:
    print(json.dumps(bundle))
  else:
    with open(args.output, 'w') as f:
      f.write(json.dumps(bundle))
