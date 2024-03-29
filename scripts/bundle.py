#!/usr/bin/env python3
from utils import *
from datetime import datetime, timezone
import argparse
import json

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('index',
    help="package index (directory or manifest)")
  parser.add_argument('results', nargs='?', default=None,
    help="testbed results")
  parser.add_argument('-o', '--output',
    help='file to output the bundle manifest')
  parser.add_argument('-q', '--quiet', dest="verbosity", action='store_const', const=0, default=1,
    help='print no logging information')
  parser.add_argument('-v', '--verbose', dest="verbosity", action='store_const', const=2,
    help='print verbose logging information')
  args = parser.parse_args()

  configure_logging(args.verbosity)

  toolchains = query_toolchains()
  toolchainDates = dict((t['name'], of_utc_iso(t['date'])) for t in toolchains)
  min_utc = datetime.min.replace(tzinfo=timezone.utc)
  def toolchain_date(build: Build) -> datetime:
    return toolchainDates.get(build['toolchain'], min_utc)

  pkgs, aliases = load_index(args.index, include_builds=True)
  pkgMap = dict((pkg['fullName'], pkg) for pkg in pkgs)
  if args.results is not None:
    with open(args.results, 'r') as f:
      results: 'dict[str, list[Build]]' = json.load(f)
    for (full_name, pkg_results) in results.items():
      pkg = pkgMap[full_name]
      pkg['builds'] = insert_build_results(pkg['builds'], pkg_results)
  for pkg in pkgMap.values():
    pkg['builds'] = sorted(pkg['builds'], key=toolchain_date, reverse=True)

  data = {
    'bundledAt': utc_iso_now(),
    'toolchains': toolchains,
    'packages': list(pkgMap.values()),
    'packageAliases': flatten_aliases(aliases),
  }
  if args.output is None:
    print(json.dumps(data, indent=2))
  else:
    with open(args.output, 'w') as f:
      f.write(json.dumps(data, indent=2))
