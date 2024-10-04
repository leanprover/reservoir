#!/usr/bin/env python3
from utils import *
import argparse
import json

def mk_dependent(pkg: SerialPackage, dep: Dependency) -> Dependent:
  return {
    'type': dep['type'],
    'name': pkg['name'],
    'scope': pkg['owner'],
    'fullName': pkg['fullName'],
    'version': dep['version'],
    'transitive': dep.get('transitive', None),
    'rev': dep['rev'],
    'inputRev': dep.get('inputRev', None),
    'url': dep.get('url', None),
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
  url_map = dict[str, SerialPackage]()
  for indexed_pkg in indexed_pkgs:
    pkg = serialize_package(indexed_pkg)
    pkg['builds'] = sorted(pkg['builds'], key=build_sort_key, reverse=True)
    pkg_map[pkg['fullName']] = pkg
    src = git_src(pkg)
    if src is not None:
      url = src['gitUrl'].removesuffix('.git')
      url_map[url] = pkg
    pkgs.append(pkg)
  # Compute package dependents
  for pkg in pkgs:
    vers = pkg['versions']
    if len(vers) == 0: continue
    to_add = True
    for ver in vers:
      deps = ver['dependencies']
      if deps is None: continue
      for dep in deps:
        dep_pkg = None
        scope = dep.get('scope', None)
        if scope is not None:
          dep_pkg = pkg_map.get(f"{dep['scope']}/{dep['name']}", None)
          if dep_pkg is not None:
            dep['fullName'] = dep_pkg['fullName']
        if dep_pkg is None:
          url = dep.get('url', None)
          if url is None: continue
          dep_pkg = url_map.get(url.removesuffix('.git'), None)
          if dep_pkg is None: continue
          dep['fullName'] = dep_pkg['fullName']
        if to_add:
          dep_pkg['dependents'].append(mk_dependent(pkg, dep))
      to_add = False
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
