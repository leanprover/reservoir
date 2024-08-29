import os
import json
import shutil
import logging
from typing import Mapping, MutableMapping, overload, Literal, Iterable, TypedDict
from requests.structures import CaseInsensitiveDict
from utils.core import *
from utils.package import *

Alias = TypedDict('Alias', {'from': str, 'to': str})

class AliasStub(TypedDict):
  alias: Alias

# assumes mapping is acyclic
def flatten_mapping(mapping: MutableMapping[T, T]):
  def follow(parents: list[T], target: T):
    if target in mapping:
      follow(parents, mapping[target])
    else:
      for parent in parents:
        mapping[parent] = target
  parents = list[T]()
  for root, target in mapping.items():
    parents.append(root)
    follow(parents, target)
    parents.clear()

def resolve_aliases(pkgs: Iterable[Package], aliases: Mapping[str, str]):
  resolved = CaseInsensitiveDict[Package]()
  for alias, target in aliases.items():
    pkg = next((pkg for pkg in pkgs if pkg['fullName'].lower() == target.lower()), None)
    if pkg is not None:
      resolved[alias] = pkg
    else:
      logging.warning(f"Failed to resolve alias '{alias}' -> '{target}'")
  return resolved

# Alias encoding for the Reservoir `manifest.json`
def serialize_aliases(aliases: Mapping[str, Package]) -> dict[str, str]:
  return dict([alias, pkg['fullName']] for alias, pkg in aliases.items())

def index_relpath(owner: str, name: str) -> str:
  return os.path.join(owner.lower(), name.lower())

def alias_relpath(alias: str) -> str:
  return index_relpath(*alias.split('/'))

def package_relpath(pkg: Package) -> str:
  return index_relpath(pkg['owner'], pkg['name'])

def walk_index(path: str):
  for owner_dir in os.listdir(path):
    if (owner_dir.startswith('.')):
      continue
    owner_path = os.path.join(path, owner_dir)
    for pkg_dir in os.listdir(owner_path):
      yield os.path.join(owner_dir, pkg_dir)

def load_index(path: str, include_builds=False) -> tuple[list[Package], CaseInsensitiveDict[Package]]:
  if os.path.isdir(path):
    pkgs = list[Package]()
    aliases = CaseInsensitiveDict[str]()
    for relpath in walk_index(path):
      pkg_path = os.path.join(path, relpath)
      if os.path.isdir(pkg_path):
        with open(os.path.join(pkg_path, 'metadata.json'), 'r') as f:
          data = json.load(f)
        if 'keywords' not in data:
          data['keywords'] = []
        if 'versions' not in data:
          data['versions'] = []
        pkg = package_of_metadata(data)
        pkg['path'] = relpath
        if include_builds:
          pkg['builds'] = load_builds(os.path.join(pkg_path, 'builds.json'))
        pkgs.append(pkg)
      else:
        with open(pkg_path, 'r') as f:
          content = f.read().strip()
        try:
          obj = json.loads(content)
          alias: Alias = obj.get('alias', None)
          if alias is not None:
            aliases[alias['from']] = alias['to']
        except json.JSONDecodeError:
          logging.error(f"{relpath}: Package stub has invalid JSON")
    pkgs = sorted(pkgs, key=lambda pkg: pkg['stars'], reverse=True)
    flatten_mapping(aliases)
    aliases = resolve_aliases(pkgs, aliases)
    return pkgs, aliases
  else:
    with open(path, 'r') as f:
      pkgs: list[Package] = json.load(f)
    return pkgs, CaseInsensitiveDict[Package]()

def load_builds(path: str) -> list[OldBuild]:
  if os.path.exists(path):
    with open(path, 'r') as f:
      return json.load(f)
  else:
    return list()

def insert_build_results(builds: Iterable[OldBuild], results: Iterable[OldBuild]) -> list[OldBuild]:
  new_builds = list[OldBuild]()
  new_results = dict((r['toolchain'], r) for r in results)
  for build in builds:
    toolchain = build['toolchain']
    result = new_results.get(toolchain, None)
    if result is not None:
      del new_results[toolchain]
      if result['outcome'] == 'success' or build['outcome'] != 'success':
        new_builds.append(result)
        continue
    new_builds.append(build)
  for result in new_results.values():
    new_builds.append(result)
  return sorted(new_builds, key=lambda build: build['toolchain'], reverse=True)

def move_package(index_dir: str, old_relpath: str, new_relpath: str):
  old_path = os.path.join(index_dir, old_relpath)
  if os.path.isdir(old_path):
    new_path = os.path.join(index_dir, new_relpath)
    if os.path.isdir(new_path):
      logging.info(f"Index merge: '{old_relpath}' -> '{new_relpath}'")
      old_builds = load_builds(os.path.join(old_path, 'builds.json'))
      new_builds = load_builds(os.path.join(new_path, 'builds.json'))
      builds = insert_build_results(old_builds, new_builds)
      with open(os.path.join(new_path, 'builds.json'), 'w') as f:
        json.dump(builds, f, indent=2)
      shutil.rmtree(old_path)
    else:
      logging.info(f"Index rename: '{old_relpath}' -> '{new_relpath}'")
      if os.path.isfile(new_path):
        logging.info(f"Removed stub at '{new_relpath}'")
        os.remove(new_path)
      os.renames(old_path, new_path)

def walk_renames(pkg: Package) -> Iterable[Package]:
  for pkg in pkg['renames']:
    walk_renames(pkg)
    yield pkg

def write_index(index_dir: str, pkgs: Iterable[Package], aliases: MutableMapping[str, Package]):
  # Write packages
  for pkg in pkgs:
    # Make package directory
    relpath = package_relpath(pkg)
    pkg_dir = os.path.join(index_dir, relpath)
    if os.path.isfile(pkg_dir):
      logging.info(f"Removed stub at '{relpath}'")
      os.remove(pkg_dir)
    os.makedirs(pkg_dir, exist_ok=True)
    # Write package metadata
    with open(os.path.join(pkg_dir, "metadata.json"), 'w') as f:
      json.dump(package_metadata(pkg), f, indent=2)
      f.write("\n")
    # Perform renames
    for old_pkg in walk_renames(pkg):
      old_relpath = package_relpath(old_pkg)
      if old_relpath is not None and old_relpath != relpath:
        move_package(index_dir, old_relpath, relpath)
        logging.info(f"Index alias: '{old_pkg['fullName']}' -> '{pkg['fullName']}'")
        aliases[old_pkg['fullName']] = pkg
    # Compute source-based aliases
    for src in pkg['sources']:
      alias = src.get('fullName', None)
      if alias is not None and alias_relpath(alias) != relpath:
        if alias not in aliases:
          logging.info(f"Index alias: '{alias}' -> '{pkg['fullName']}'")
        aliases[alias] = pkg  # always set to ensure canonical casing
        builds_file = os.path.join(pkg_dir, 'builds.json')
    # Write builds
    builds_file = os.path.join(pkg_dir, 'builds.json')
    if os.path.exists(builds_file):
      with open(os.path.join(pkg_dir, 'builds.json'), 'r') as f:
        builds: list[OldBuild] = json.load(f)
      builds = insert_build_results(builds, pkg['builds'])
    else:
      builds = pkg['builds']
    with open(builds_file, 'w') as f:
      f.write(json.dumps(builds, indent=2))
      f.write('\n')
  # Write aliases
  for alias, target_pkg in aliases.items():
    target = target_pkg['fullName']
    alias_path = os.path.join(index_dir, alias_relpath(alias))
    if os.path.isdir(alias_path):
      logging.warning(f"Package located at '{alias}': could not write alias '{alias}' -> '{target}'")
    else:
      os.makedirs(os.path.dirname(alias_path), exist_ok=True)
      with open(alias_path, 'w') as f:
        obj: AliasStub = {"alias": {"from": alias, "to": target}}
        f.write(json.dumps(obj))
        f.write("\n")
