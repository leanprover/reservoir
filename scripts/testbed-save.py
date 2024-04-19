#!/usr/bin/env python3
from utils import *
import logging
import json
import argparse
import os

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('results',
    help="JSON manifest of results")
  parser.add_argument('index',
    help='directory to output hierarchical index')
  parser.add_argument('-q', '--quiet', dest="verbosity", action='store_const', const=0, default=1,
    help='print no logging information')
  parser.add_argument('-v', '--verbose', dest="verbosity", action='store_const', const=2,
    help='print verbose logging information')
  args = parser.parse_args()

  configure_logging(args.verbosity)

  with open(args.results) as f:
    results: 'dict[str, list[Build]]' = json.load(f)

  did_error = False
  for (full_name, pkg_results) in results.items():
    pkg_dir = os.path.join(args.index, full_name.lower())
    if not os.path.exists(pkg_dir):
      logging.error(f"{full_name}: build save failed: {pkg_dir} does not exist")
      did_error = True
      continue
    builds_file = os.path.join(pkg_dir, 'builds.json')
    if os.path.exists(builds_file):
      with open(os.path.join(pkg_dir, 'builds.json'), 'r') as f:
        builds = json.load(f)
      builds = insert_build_results(builds, pkg_results)
    else:
      builds = pkg_results
    with open(builds_file, 'w') as f:
      f.write(json.dumps(builds, indent=2))
      f.write('\n')

  if did_error:
    exit(1)
