#!/usr/bin/env python3
from utils import *
import argparse
import json

def mk_dependent(pkg: SerialPackage, dep: Dependency) -> Dependency:
  return {
    'type': dep['type'],
    'name': pkg['name'],
    'scope': pkg['owner'],
    'version': dep['version'],
    'rev': dep['rev'],
  }

def bundle_index(path: str):
  # Query toolchains
  toolchains = query_toolchains()
  toolchain_sort_keys = dict((t['name'], toolchain_sort_key(t)) for t in toolchains)
  def build_sort_key(build: Build):
    return toolchain_sort_keys.get(build['toolchain'], MIN_TOOLCHAIN_SORT_KEY)
  # Serialize index
  indexed_pkgs, aliases = load_index(path, include_builds=True)
  pkgs = list[SerialPackage]()
  pkg_map = dict[str, SerialPackage]()
  for indexed_pkg in indexed_pkgs:
    pkg = serialize_package(indexed_pkg)
    pkg['builds'] = sorted(pkg['builds'], key=build_sort_key, reverse=True)
    pkg_map[pkg['fullName']] = pkg
    pkgs.append(pkg)
  # Compute package dependents
  for pkg in pkgs:
    vers = pkg['versions']
    if len(vers) == 0: continue
    deps = vers[0]['dependencies']
    if deps is None: continue
    for dep in deps:
      if dep['scope'] == '': continue
      dep_pkg = pkg_map.get(f"{dep['scope']}/{dep['name']}", None)
      if dep_pkg is not None:
        dep_pkg['dependents'].append(mk_dependent(pkg, dep))
  # Return manifest
  return {
    'bundledAt': utc_iso_now(),
    'toolchains': toolchains,
    'packages': pkgs,
    'packageAliases': serialize_aliases(aliases),
  }

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('index',
    help="package index (directory or manifest)")
  parser.add_argument('-o', '--output',
    help='file to output the bundle manifest')
  parser.add_argument('-q', '--quiet', dest="verbosity", action='store_const', const=0, default=1,
    help='print no logging information')
  parser.add_argument('-v', '--verbose', dest="verbosity", action='store_const', const=2,
    help='print verbose logging information')
  args = parser.parse_args()

  configure_logging(args.verbosity)
  data = bundle_index(args.index)
  if args.output is None:
    print(json.dumps(data, indent=2))
  else:
    with open(args.output, 'w') as f:
      f.write(json.dumps(data, indent=2))
