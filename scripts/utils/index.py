import os
import json
import shutil
import logging
from typing import Callable, Mapping, MutableMapping, Iterable, TypedDict
from requests.structures import CaseInsensitiveDict
from utils.core import *
from utils.package import *

Alias = TypedDict('Alias', {'from': str, 'to': str})

class AliasStub(TypedDict):
  alias: Alias

def flatten_mapping(mapping: MutableMapping[T, T]):
  def follow(parents: list[T], target: T):
    if target in mapping:
      if target in parents:
        parents.append(target)
        raise RuntimeError(f"Cycle: {parents}")
      parents.append(target)
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

class BuildV0Base(TypedDict):
  url: str | None
  builtAt: str
  revision: str
  toolchain: str
  outcome: str

class BuildV0(BuildV0Base, total=False):
  requiredUpdate: bool | None
  archiveSize: int | None

def of_build_v0(build: BuildV0) -> Build:
  return {
    'url': build.get('url', None),
    'built': build['outcome'] == 'success',
    'tested': None,
    'archiveSize': build.get('archiveSize', None),
    'archiveHash': build.get('archiveHash', None),
    'toolchain': build['toolchain'],
    'requiredUpdate': build.get('requiredUpdate', None),
    'revision': build['revision'],
    'runAt': build['builtAt'],
  }

def load_versions(path: str) -> list[PackageVersionMetadata]:
  if not os.path.exists(path):
    return []
  with open(path, 'r') as f:
    data: Any = json.load(f)
  if isinstance(data, dict):
    return data['data']
  else:
    return data

def load_builds(path: str) -> list[Build]:
  if not os.path.exists(path):
    return []
  with open(path, 'r') as f:
    data: Any = json.load(f)
  if isinstance(data, dict):
    builds = data['data']
    for build in builds:
      build['archiveHash'] = build.get('archiveHash', None)
    return builds
  else:
    return list(map(of_build_v0, data))

def load_package(pkg_dir: str, relpath: str, include_versions: bool = True, include_builds: bool = False) -> Package:
  with open(os.path.join(pkg_dir, 'metadata.json'), 'r') as f:
    data = json.load(f)
  schema_ver = Version(data.get('schemaVersion', None))
  if 'keywords' not in data:
    data['keywords'] = []
  pkg = package_of_metadata(package_metadata(data), relpath, schema_ver)
  # Load versions
  if not include_versions and not include_builds:
    return pkg
  vers: list[PackageVersionMetadata] | None = data.get('versions', None)
  if vers is None:
    vers = load_versions(os.path.join(pkg_dir, 'versions.json'))
  pkg['versions'] = list(map(version_of_metadata, vers))
  if not include_builds:
    return pkg
  # Load builds
  builds = load_builds(os.path.join(pkg_dir, 'builds.json'))
  ver_dict = dict((v['revision'], v) for v in pkg['versions'])
  for build in builds:
    ver = ver_dict.get(build['revision'], None)
    if ver is None:
      pkg['builds'].append(build)
    else:
      ver['builds'].append(build_result(build))
  return pkg

def load_index_metadata(path: str) -> list[PackageMetadata]:
  if os.path.isdir(path):
    pkgs = list[Package]()
    for relpath in walk_index(path):
      pkg_path = os.path.join(path, relpath)
      if os.path.isdir(pkg_path):
        pkgs.append(load_package(pkg_path, relpath, False, False))
    return sorted(pkgs, key=lambda pkg: pkg['stars'], reverse=True)
  else:
    with open(path, 'r') as f:
      pkgs: list[Package] = json.load(f)
    return list(map(package_metadata, pkgs))

def load_index(path: str, include_builds=False) -> tuple[list[Package], CaseInsensitiveDict[Package]]:
  if os.path.isdir(path):
    pkgs = list[Package]()
    aliases = CaseInsensitiveDict[str]()
    for relpath in walk_index(path):
      pkg_path = os.path.join(path, relpath)
      if os.path.isdir(pkg_path):
        pkgs.append(load_package(pkg_path, relpath, True, include_builds))
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

BT = TypeVar('BT', bound=BuildResult)

def trim_builds(builds: Iterable[BT], key: Callable[[BT], T]) -> Iterable[BT]:
  """Trim builds per package to one per key."""
  saved_builds = dict[T, BT]()
  for curr_build in builds:
    id = key(curr_build)
    prev_build = saved_builds.get(id, None)
    if prev_build is None:
      saved_builds[id] = curr_build
    elif curr_build['built'] is False and prev_build['built'] is True:
      saved_builds[id] = prev_build
      logging.warning(f"New build of '{id}' failed despite previous success; keeping old build")
  return saved_builds.values()

def trim_version_builds(pkg: Package):
  """Trim builds per version to one per toolchain."""
  for ver in pkg['versions']:
    ver['builds'] = list(trim_builds(ver['builds'], key=lambda b: b['toolchain']))

def add_builds(pkg: Package, old_builds: Iterable[Build]):
  ver_dict = dict((v['revision'], v) for v in pkg['versions'])
  for old_build in old_builds:
    ver = ver_dict.get(old_build['revision'], None)
    if ver is None:
      pkg['builds'].append(old_build)
    else:
      ver['builds'].append(build_result(old_build))

def mk_builds(pkg: Package) -> Iterable[Build]:
  for ver in pkg['versions']:
    for build in ver['builds']:
      yield mk_build(ver, build)
  for build in trim_builds(pkg['builds'], lambda b: (b['revision'], b['toolchain'])):
    yield build

def write_index(index_dir: str, pkgs: Iterable[Package], aliases: MutableMapping[str, Package]):
  # Write packages
  for pkg in pkgs:
    logging.debug(f"Writing {pkg['fullName']}")
    # Prepare path
    relpath = package_relpath(pkg)
    pkg_dir = os.path.join(index_dir, relpath)
    if os.path.isfile(pkg_dir):
      logging.info(f"Removed stub at '{relpath}'")
      os.remove(pkg_dir)
    # Perform renames
    for rename in pkg['renames']:
      old_name = rename['fullName']
      old_relpath = rename['relpath']
      if old_relpath is None or old_relpath == relpath:
        continue
      old_path = os.path.join(index_dir, old_relpath)
      if os.path.isdir(old_path):
        if os.path.isdir(pkg_dir):
          logging.info(f"Index merge: '{old_relpath}' -> '{relpath}'")
          old_builds = load_builds(os.path.join(old_path, 'builds.json'))
          add_builds(pkg, old_builds)
          shutil.rmtree(old_path)
        else:
          logging.info(f"Index rename: '{old_relpath}' -> '{relpath}'")
          os.renames(old_path, pkg_dir)
      logging.info(f"Index alias: '{old_name}' -> '{pkg['fullName']}'")
      aliases[old_name] = pkg
    # Ensure package directory exists
    os.makedirs(pkg_dir, exist_ok=True)
    # Write package metadata
    with open(os.path.join(pkg_dir, "metadata.json"), 'w') as f:
      data = cast(Any, package_metadata(pkg))
      data['schemaVersion'] = INDEX_SCHEMA_VERSION_STR
      json.dump(data, f, indent=2)
      f.write("\n")
    # Compute source-based aliases
    for src in pkg['sources']:
      alias = src.get('fullName', None)
      if alias is not None and alias_relpath(alias) != relpath:
        if alias not in aliases:
          logging.info(f"Index alias: '{alias}' -> '{pkg['fullName']}'")
        aliases[alias] = pkg  # always set to ensure canonical casing
        builds_file = os.path.join(pkg_dir, 'builds.json')
    # Write versions
    vers = list(map(version_metadata, pkg['versions']))
    if len(vers) > 0:
      with open(os.path.join(pkg_dir, 'versions.json'), 'w') as f:
        json.dump({'schemaVersion': INDEX_SCHEMA_VERSION_STR, 'data': vers}, f, indent=2)
        f.write('\n')
    # Write builds
    trim_version_builds(pkg)
    builds_file = os.path.join(pkg_dir, 'builds.json')
    builds_exists = os.path.exists(builds_file)
    if builds_exists:
      add_builds(pkg, load_builds(builds_file))
    builds = mk_builds(pkg)
    builds = sorted(builds, key=lambda b: b['runAt'], reverse=True)
    if len(builds) > 0:
      with open(builds_file, 'w') as f:
        json.dump({'schemaVersion': INDEX_SCHEMA_VERSION_STR, 'data': builds}, f, indent=2)
        f.write('\n')
    elif builds_exists:
      os.remove(builds_file)
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
