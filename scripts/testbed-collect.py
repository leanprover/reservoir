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

def walk_entries(matrix: TestbedMatrix) -> Iterable[TestbedEntry]:
  for layer in matrix:
    yield from layer['data']

def mk_testbed_result(entry: TestbedEntry, pkg_result: PackageResult) -> TestbedResult:
  result = cast(TestbedResult, pkg_result)
  result['repoId'] = entry['repoId']
  result['indexName'] = entry['indexName']
  return result

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
    matrix: TestbedMatrix = json.load(f)

  jobs = query_jobs(TESTBED_REPO, args.run_id, args.run_attempt)
  def find_testbed_job_id(name: str) -> int | None:
    return next((job['id'] for job in jobs if job['name'].split('/')[-1].strip() == name), None)

  logging.info(f"Testbed entries: {len(matrix)}")

  num_opt_outs = 0
  num_build_results = 0
  results: TestbedResults = list[TestbedResult]()
  archiveSizes = list[int]()
  for entry in walk_entries(matrix):
    jobId = find_testbed_job_id(entry['jobName'])
    if jobId is None:
      logging.error(f"Job ID not found for '{entry['jobName']}'")
      continue
    url = f"https://github.com/{TESTBED_REPO}/actions/runs/{args.run_id}/job/{jobId}#step:4:1"
    result_file = os.path.join(args.results, entry['artifact'], 'result.json')
    try:
      with open(result_file, 'r') as f:
        result: TestbedResult = mk_testbed_result(entry, json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
      continue
    results.append(result)
    if not result['doIndex']:
      logging.info(f"'{id}' opted-out of Reservoir")
      num_opt_outs +=1
    for build in walk_builds(result):
      build['url'] = url
      num_build_results += 1
      archiveSize = build.get('archiveSize', None)
      if archiveSize is not None:
        archiveSizes.append(archiveSize)

  logging.info(f"Package results: {len(results)} ({num_opt_outs} opt-outs)")
  num_archives = len(archiveSizes)
  logging.info(f"Build results: {num_build_results} ({num_archives} with archives)")
  avg = 0 if num_archives == 0 else round(sum(archiveSizes)/num_archives)
  logging.info(f'Average build archive size: {fmt_bytes(avg)} ({avg} bytes)')

  if args.output is None:
    print(json.dumps(results, indent=2))
  else:
    with open(args.output, 'w') as f:
      f.write(json.dumps(results, indent=2))
