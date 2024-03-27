from typing import Iterable, Tuple, TypeVar, TypedDict
import itertools
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

def load_builds(path: str) -> 'list[Build]':
  if os.path.exists(path):
    with open(path, 'r') as f:
      return json.load(f)
  else:
    return list()

def load_index(path: str, include_builds=False) -> 'Tuple[list[Package], dict[str,str]]':
  aliases = dict()
  if os.path.isdir(path):
    pkgs: 'list[Package]' = list()
    for owner in os.listdir(path):
      owner_dir = os.path.join(path, owner)
      if (owner.startswith('.')): continue
      for pkg in os.listdir(owner_dir):
        pkg_path = os.path.join(owner_dir, pkg)
        if os.path.isdir(pkg_path):
          with open(os.path.join(pkg_path, 'metadata.json'), 'r') as f:
            pkg: Package = json.load(f)
          if include_builds:
            pkg['builds'] = load_builds(os.path.join(pkg_path, 'builds.json'))
          pkgs.append(pkg)
        else:
          with open(pkg_path, 'r') as f:
            aliases[f"{owner}/{pkg}"] = f.read().strip()
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
def paginate(iterable: 'Iterable[T]', page_size: int) -> 'Iterable[list[T]]':
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
  tag: str
  prerelease: bool

def query_releases(repo=DEFAULT_ORIGIN, paginate=True) -> 'Iterable[Release]':
  out = capture_cmd(
    'gh', 'api',
    '--cache', '1h',
    f'repos/{repo}/releases',
    *(['--paginate'] if paginate else []),
    '-q', '.[] | {tag: .tag_name, prerelease: .prerelease}'
  )
  return map(json.loads, out.decode().splitlines())

def query_toolchain_releases(repo=DEFAULT_ORIGIN):
  return [f"{repo}:{release['tag']}" for release in query_releases(repo)]

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
