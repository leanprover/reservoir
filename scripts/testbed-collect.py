#!/usr/bin/env python3
from utils import *
from typing import TypedDict
import json
import re
import argparse
import os

class Job(TypedDict):
  id: int
  name: str

TESTBED_REPO = "leanprover/reservoir"
def query_jobs(repo: str, run_id: int, run_attempt: int = 1) -> 'list[Job]':
  out = capture_cmd(
    'gh', 'api', '--paginate',
    f"repos/{repo}/actions/runs/{run_id}/attempts/{run_attempt}/jobs",
    '-q', '.jobs[] | {id,name}'
  )
  return list(map(json.loads, out.splitlines()))

BUILD_JOB_PATTERN = re.compile("Build (.*)")
def is_build_job(job: Job, name: str):
  match = BUILD_JOB_PATTERN.search(job['name'])
  return match is not None and match.group(1) == name

def mk_build_results(builtAt: str, url: str, result: PackageResult) -> Iterable[Build]:
  head_ver = result['headVersion']
  for build in head_ver['builds']:
    yield {
      'url': url,
      'builtAt': builtAt,
      'outcome': 'success' if build['built'] else 'failure',
      'revision': head_ver['revision'],
      'toolchain': build['toolchain'],
      'requiredUpdate': build['requiredUpdate'],
      'archiveSize': build['archiveSize'],
    }

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
  parser.add_argument('-o', '--output',
    help='file to output the collected results')
  parser.add_argument('-q', '--quiet', dest="verbosity", action='store_const', const=0, default=1,
    help='print no logging information')
  parser.add_argument('-v', '--verbose', dest="verbosity", action='store_const', const=2,
    help='print verbose logging information')
  args = parser.parse_args()

  configure_logging(args.verbosity)

  matrix_file = args.matrix
  if matrix_file is None:
    matrix_file = os.path.join(args.results, 'matrix', 'matrix.json')

  with open(matrix_file, 'r') as f:
    matrix: list[TestbedEntry] = json.load(f)

  jobs = query_jobs(TESTBED_REPO, args.run_id, args.run_attempt)
  def find_build_job(name: str) -> Job:
    return next(job for job in jobs if is_build_job(job, name))

  logging.info(f"{len(matrix)} total testbed entries")

  num_results = 0
  num_build_results = 0
  results = dict[str, list[Build]]()
  archiveSizes = list[int]()
  now = utc_iso_now()
  for entry in matrix:
    result_file = os.path.join(args.results, entry['artifact'], 'result.json')
    try:
      with open(result_file, 'r') as f:
        result: PackageResult = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
      continue
    num_results += 1
    jobId = find_build_job(entry['buildName'])['id']
    url = f"https://github.com/{TESTBED_REPO}/actions/runs/{args.run_id}/job/{jobId}#step:4:1"
    if entry['fullName'] not in results:
      build_results = results[entry['fullName']] = list()
    else:
      build_results =  results[entry['fullName']]
    for build in mk_build_results(now, url, result):
      num_build_results += 1
      build_results.append(build)
      archiveSize = build.get('archiveSize', None)
      if archiveSize is not None:
        archiveSizes.append(archiveSize)

  logging.info(f"{len(results)} testbed entries with results")

  num_archives = len(archiveSizes)
  logging.info(f"{num_archives} testbed entries with archives")
  avg = 0 if num_archives == 0 else round(sum(archiveSizes)/num_archives)
  logging.info(f'Average build archive size: {fmt_bytes(avg)} ({avg} bytes)')

  if args.output is None:
    print(json.dumps(results, indent=2))
  else:
    with open(args.output, 'w') as f:
      f.write(json.dumps(results, indent=2))
