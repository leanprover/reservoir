import os
import json
import logging
from typing import Mapping, MutableMapping, overload, Literal, Iterable, TypedDict, TypeVar
from requests.structures import CaseInsensitiveDict
from utils.core import *

class Source(TypedDict):
  type: str
  host: str
  id: str
  fullName: str
  repoUrl: str
  gitUrl: str
  defaultBranch: str

class RunHeader(TypedDict):
  url: str
  builtAt: str

class BuildBase(RunHeader):
  revision: str
  toolchain: str
  outcome: str

class Build(BuildBase, total=False):
  requiredUpdate: bool
  archiveSize: int | None

class PartialBuild(TypedDict, total=False):
  revision: str
  toolchain: str
  requiredUpdate: bool
  outcome: str
  archiveSize: int | None

class PackageBase(TypedDict):
  name: str
  owner: str
  fullName: str
  description: str | None
  homepage: str | None
  license: str | None
  createdAt: str
  updatedAt: str
  stars: int
  sources: list[Source]

class Package(PackageBase, total=False):
  builds: list[Build]

class PackageWithBuilds(PackageBase):
  builds: list[Build]

Alias = TypedDict('Alias', {'from': str, 'to': str})

class AliasStub(TypedDict):
  alias: Alias

# assumes mapping is acyclic
def flatten_mapping(mapping: 'MutableMapping[T, T]'):
  def follow(parents: 'list[T]', target: T):
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

def resolve_aliases(pkgs: 'Iterable[Package]', aliases: 'Mapping[str, str]'):
  resolved = CaseInsensitiveDict[Package]()
  for alias, target in aliases.items():
    pkg = next((pkg for pkg in pkgs if pkg['fullName'].lower() == target.lower()), None)
    if pkg is not None:
      resolved[alias] = pkg
    else:
      logging.warning(f"Failed to resolve alias '{alias}' -> '{target}'")
  return resolved

# Alias encoding for the `manifest.json``
def encode_aliases(aliases: 'Mapping[str, Package]') -> 'dict[str, str]':
  return dict([alias, pkg['fullName']] for alias, pkg in aliases.items())

def index_relpath(owner: str, name: str) -> str:
  return os.path.join(owner.lower(), name.lower())

def alias_relpath(alias: str) -> str:
  return index_relpath(*alias.split('/'))

def package_relpath(pkg: Package) -> str:
  return index_relpath(pkg['owner'], pkg['name'])

def load_builds(path: str) -> 'list[Build]':
  if os.path.exists(path):
    with open(path, 'r') as f:
      return json.load(f)
  else:
    return list()

@overload
def load_index(path: str) -> 'tuple[list[Package], CaseInsensitiveDict[Package]]': ...

@overload
def load_index(path: str, include_builds: Literal[False]) -> 'tuple[list[Package], CaseInsensitiveDict[Package]]': ...

@overload
def load_index(path: str, include_builds: Literal[True]) -> 'tuple[list[PackageWithBuilds], CaseInsensitiveDict[Package]]': ...

def load_index(path: str, include_builds=False):
  aliases = CaseInsensitiveDict[str]()
  if os.path.isdir(path):
    pkgs = list[Package]()
    for owner_dir in os.listdir(path):
      if (owner_dir.startswith('.')): continue
      owner_path = os.path.join(path, owner_dir)
      for pkg_dir in os.listdir(owner_path):
        pkg_path = os.path.join(owner_path, pkg_dir)
        if os.path.isdir(pkg_path):
          with open(os.path.join(pkg_path, 'metadata.json'), 'r') as f:
            pkg: Package = json.load(f)
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
              aliases[f"{owner_dir}/{pkg_dir}"] = content
    pkgs = sorted(pkgs, key=lambda pkg: pkg['stars'], reverse=True)
  else:
    with open(path, 'r') as f:
      pkgs = json.load(f)
    if include_builds:
      for pkg in pkgs:
        pkg['builds'] = list()
  flatten_mapping(aliases)
  aliases = resolve_aliases(pkgs, aliases)
  return pkgs, aliases

def insert_build_results(builds: 'Iterable[Build]', results: 'Iterable[Build]') -> 'list[Build]':
  new_builds = list[Build]()
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

def write_packages(index_dir: str, pkgs: 'Iterable[Package]'):
  for pkg in pkgs:
    pkg_dir = os.path.join(index_dir, package_relpath(pkg))
    if os.path.isfile(pkg_dir):
      os.remove(pkg_dir)
    os.makedirs(pkg_dir, exist_ok=True)
    with open(os.path.join(pkg_dir, "metadata.json"), 'w') as f:
      json.dump(pkg, f, indent=2)
      f.write("\n")

def write_aliases(index_dir: str, aliases: 'Mapping[str, Package]'):
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

def write_index(index_dir: str, pkgs: 'Iterable[Package]', aliases: 'Mapping[str, Package]'):
  write_packages(index_dir, pkgs)
  write_aliases(index_dir, aliases)
