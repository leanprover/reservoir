#!/usr/bin/env python3
from utils import add_build
from typing import TypedDict
from datetime import datetime
import json
import re
import subprocess
import argparse
import os

class Job(TypedDict):
  id: int
  name: str

TESTBED_REPO = "leanprover/reservoir"
def query_jobs(run_id: int, run_attempt: int = 1) -> 'list[Job]':
  child = subprocess.run([
    "gh", "api", "--paginate",
    f"repos/{TESTBED_REPO}/actions/runs/{run_id}/attempts/{run_attempt}/jobs",
    "-q", ".jobs[] | {id,name}"
  ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if child.returncode != 0:
    raise RuntimeError(child.stderr.decode('utf-8').strip())
  return [json.loads(ln) for ln in child.stdout.splitlines()]

BUILD_RE = re.compile("Build (.*)")
def is_build_job(job: Job, repo: str):
  match = BUILD_RE.search(job['name'])
  return match is not None and match.group(1) == repo

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('results',
    help="directory containing testbed results")
  parser.add_argument('run_id', type=int,
    help="the testbed run ID")
  parser.add_argument('run_attempt', nargs='?', type=int, default=1,
    help="the testbed run attempt")
  parser.add_argument('-m', '--matrix',
    help="file containing the JSON build matrix")
  parser.add_argument('-D', '--index-dir', default=None,
    help='directory to output hierarchical index')
  parser.add_argument('-o', '--output',
    help='file to output the bundle manifest')
  args = parser.parse_args()

  matrix_file = args.matrix
  if matrix_file is None:
    matrix_file = os.path.join(args.results, 'matrix', 'matrix.json')

  with open(matrix_file, 'r') as f:
    matrix = json.load(f)

  jobs = query_jobs(args.run_id, args.run_attempt)
  def find_build_job(repo: str) -> Job:
    return next(job for job in jobs if is_build_job(job, repo))

  results = dict()
  for entry in matrix:
    jobId = find_build_job(entry['fullName'])['id']
    result = {
      'url': f"https://github.com/{TESTBED_REPO}/actions/runs/{args.run_id}/job/{jobId}#step:5:1",
      'builtAt': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    result_file = os.path.join(args.results, entry['artifact'], 'result.json')
    if not os.path.exists(result_file):
      continue
    with open(result_file, 'r') as f:
      result |= json.load(f)
    results[entry['fullName']] = result
    if args.index_dir is not None:
      pkg_dir = os.path.join(args.index_dir, entry['fullName'])
      if not os.path.exists(pkg_dir):
        continue
      builds_file = os.path.join(pkg_dir, "builds.json")
      if os.path.exists(builds_file):
        with open(os.path.join(pkg_dir, "builds.json"), 'r') as f:
          builds = json.loads(f)
        builds = add_build(builds, result)
      else:
        builds = [result]
      with open(builds_file, 'w') as f:
        f.write(json.dumps(builds, indent=2))
        f.write("\n")

  if args.output is None:
    print(json.dumps(results, indent=2))
  else:
    with open(args.output, 'w') as f:
      f.write(json.dumps(results, indent=2))
