from typing import overload, Iterator, Literal, Union, Iterable, Tuple, TypeVar, TypedDict
from datetime import datetime, timezone
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

class Source(TypedDict):
  type: str
  host: str
  id: str
  fullName: str
  repoUrl: str
  gitUrl: str
  defaultBranch: str

class Build(TypedDict):
  url: str
  builtAt: str
  revision: str
  toolchain: str
  requiredUpdate: bool
  outcome: str

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

def load_builds(path: str) -> 'list[Build]':
  if os.path.exists(path):
    with open(path, 'r') as f:
      return json.load(f)
  else:
    return list()

@overload
def load_index(path: str) -> 'Tuple[list[Package], dict[str,str]]': ...

@overload
def load_index(path: str, include_builds: Literal[False]) -> 'Tuple[list[Package], dict[str,str]]': ...

@overload
def load_index(path: str, include_builds: Literal[True]) -> 'Tuple[list[PackageWithBuilds], dict[str,str]]': ...

def load_index(path: str, include_builds=False) -> 'Tuple[Union[list[Package], list[PackageWithBuilds]], dict[str,str]]':
  aliases = dict()
  if os.path.isdir(path):
    pkgs: 'list[Package]' = list()
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
            aliases[f"{owner_dir}/{pkg_dir}"] = f.read().strip()
    pkgs = sorted(pkgs, key=lambda pkg: pkg['stars'], reverse=True)
  else:
    with open(path, 'r') as f:
      pkgs = json.load(f)
    if include_builds:
      for pkg in pkgs:
        pkg['builds'] = list()
  return pkgs, aliases

# assumes aliases are acyclic; mutates the input
def flatten_aliases(aliases: 'dict[T, T]') -> 'dict[T, T]':
  def follow(parents: 'list[T]', target: T):
    if target in aliases:
      parents.append(target)
      follow(parents, aliases[target])
    else:
      for parent in parents:
        aliases[parent] = target
  parents = list()
  for alias, target in aliases.items():
    parents.append(alias)
    follow(parents, target)
    parents.clear()
  return aliases

def insert_build_results(builds: 'list[Build]', results: 'list[Build]') -> 'list[Build]':
  new_builds = list()
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

# from https://antonz.org/page-iterator/
def paginate(iterable: 'Iterable[T]', page_size: int) -> 'Iterator[list[T]]':
  it = iter(iterable)
  slicer = lambda: list(itertools.islice(it, page_size))
  return iter(slicer, [])

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

DEFAULT_ORIGIN = 'leanprover/lean4'

class Release(TypedDict):
  tag_name: str
  created_at: str
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

TOOLCHAIN_VER_PATTERN = re.compile("v4\\.(\\d+)\\..*")
def query_toolchains(repo=DEFAULT_ORIGIN) -> 'list[Toolchain]':
  def toolchain_of_release(rel: Release) -> Toolchain:
    match = TOOLCHAIN_VER_PATTERN.search(rel['tag_name'])
    version = int(match.group(1)) if match is not None else None
    return {
      "name": f"{repo}:{rel['tag_name']}",
      "version": version,
      "tag": rel['tag_name'],
      "date": rel['created_at'],
      "releaseUrl": rel['html_url'],
      "prerelease": rel['prerelease']
    }
  toolchains = map(toolchain_of_release, query_releases(repo))
  return sorted(toolchains, key=lambda t: of_utc_iso(t['date']), reverse=True)

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
