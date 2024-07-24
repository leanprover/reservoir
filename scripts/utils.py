from typing import Mapping, MutableMapping, overload, Iterator, Literal, Iterable, TypeVar, TypedDict
from datetime import datetime, timezone
from requests.structures import CaseInsensitiveDict
import itertools
import re
import json
import logging
import os
import subprocess

T = TypeVar('T')

def configure_logging(verbosity):
  if verbosity == 0:
    level = logging.CRITICAL
  elif verbosity == 1:
    level = logging.INFO
  else:
    level = logging.DEBUG
  logging.basicConfig(level=level, format='%(levelname)s: %(message)s')

# from https://antonz.org/page-iterator/
def paginate(iterable: 'Iterable[T]', page_size: int) -> 'Iterator[list[T]]':
  it = iter(iterable)
  slicer = lambda: list(itertools.islice(it, page_size))
  return iter(slicer, [])

#---
# Processes
#---

class CommandError(RuntimeError):
  pass

def run_cmd(*args: str, allow_failure=False):
  logging.info(f'> {" ".join(args)}')
  rc = subprocess.run(args).returncode
  if not allow_failure and rc != 0:
    raise CommandError(f'external command exited with code {rc}')
  return rc

def capture_cmd(*args: str) -> bytes:
  logging.debug(f'> {" ".join(args)}')
  child = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if child.returncode != 0:
    raise CommandError(child.stderr.decode().strip())
  elif len(child.stderr) > 0:
    logging.error(child.stderr.decode())
  return child.stdout


#---
# Index
#---

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

#---
# Toolchains
#---

DEFAULT_ORIGIN = 'leanprover/lean4'

class Release(TypedDict):
  tag_name: str
  published_at: str
  html_url: str
  prerelease: bool

def query_releases(repo=DEFAULT_ORIGIN, paginate=True) -> 'Iterator[Release]':
  out = capture_cmd(
    'gh', 'api',
    '--cache', '1h',
    f'repos/{repo}/releases',
    *(['--paginate'] if paginate else []),
    '-q', '.[]'
  )
  return map(json.loads, out.decode().splitlines())

class Toolchain(TypedDict):
  name: str
  version: int | None
  tag: str
  date: str
  releaseUrl: str
  prerelease: bool

def utc_iso_now():
  return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def of_utc_iso(iso: str) -> datetime:
  return datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

def toolchain_sort_key(t: Toolchain):
    return (t['version'] or 0, of_utc_iso(t['date']))

MIN_TOOLCHAIN_SORT_KEY = (0, datetime.min.replace(tzinfo=timezone.utc))

TOOLCHAIN_VER_PATTERN = re.compile("v4\\.(\\d+)\\..*")
def query_toolchains(repo=DEFAULT_ORIGIN) -> 'list[Toolchain]':
  def toolchain_of_release(rel: Release) -> Toolchain:
    match = TOOLCHAIN_VER_PATTERN.search(rel['tag_name'])
    version = int(match.group(1)) if match is not None else None
    return {
      "name": f"{repo}:{rel['tag_name']}",
      "version": version,
      "tag": rel['tag_name'],
      "date": rel['published_at'],
      "releaseUrl": rel['html_url'],
      "prerelease": rel['prerelease']
    }
  toolchains = map(toolchain_of_release, query_releases(repo))
  return sorted(toolchains, key=toolchain_sort_key, reverse=True)

def normalize_toolchain(toolchain: str):
  parts = toolchain.split(':')
  if len(parts) < 2:
    origin = DEFAULT_ORIGIN
    ver = parts[0]
  else:
    origin = parts[0]
    ver = parts[1]
  if ver[0].isdecimal():
    ver = f'v{ver}'
  return f'{origin}:{ver}'

NIGHTLY_REPO='leanprover/lean4-nightly'
def resolve_toolchain(toolchain: str):
  toolchain = toolchain.strip()
  if len(toolchain) == 0 or toolchain == 'package':
    return None
  elif toolchain == 'stable':
    releases = filter(lambda r: not r['prerelease'], query_releases())
    return f"{DEFAULT_ORIGIN}:{next(releases)['tag_name']}"
  elif toolchain == 'nightly':
    releases = query_releases(NIGHTLY_REPO, paginate=False)
    return f"{DEFAULT_ORIGIN}:{next(releases)['tag_name']}"
  elif toolchain == 'latest':
    releases = query_releases(paginate=False)
    return f"{DEFAULT_ORIGIN}:{next(releases)['tag_name']}"
  else:
    return normalize_toolchain(toolchain)

def resolve_toolchains(toolchains: 'list[str]') -> 'set[str | None]':
  if len(toolchains) == 0:
    return set([None])
  else:
    return set(resolve_toolchain(t) for ts in toolchains for t in ts.split(','))
