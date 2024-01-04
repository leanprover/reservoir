from typing import Iterable, TypedDict
import itertools
import json
import logging
import os
import subprocess

def configure_logging(verbosity):
  if verbosity == 0:
    level = logging.CRITICAL
  elif verbosity == 1:
    level = logging.INFO
  else:
    level = logging.DEBUG
  logging.basicConfig(level=level, format='%(levelname)s: %(message)s')

def load_index(path: str, include_builds=False):
  if os.path.isdir(path):
    pkgs = list()
    for owner in os.listdir(path):
      owner_dir = os.path.join(path, owner)
      for pkg in os.listdir(owner_dir):
        pkg_dir = os.path.join(owner_dir, pkg)
        with open(os.path.join(pkg_dir, 'metadata.json'), 'r') as f:
          pkg = json.load(f)
        if include_builds:
          builds_file = os.path.join(pkg_dir, 'builds.json')
          if os.path.exists(builds_file):
            with open(builds_file, 'r') as f:
              pkg['builds'] = json.load(f)
          else:
            pkg['builds'] = list()
        pkgs.append(pkg)
    pkgs = sorted(pkgs, key=lambda pkg: pkg['stars'], reverse=True)
  else:
    with open(path, 'r') as f:
      pkgs = json.load(f)
    if include_builds:
      for pkg in pkgs:
        pkg['builds'] = list()
  return pkgs

def insert_build_results(builds: list, results: 'list[dict]') -> list:
  toolchains = set(r['toolchain'] for r in results)
  builds = list(filter(lambda build: build['toolchain'] not in toolchains, builds))
  builds.extend(results)
  return sorted(builds, key=lambda build: build['toolchain'], reverse=True)

# from https://antonz.org/page-iterator/
def paginate(iterable, page_size):
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
