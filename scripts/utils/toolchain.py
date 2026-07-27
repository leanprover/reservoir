import re
import json
import requests
import itertools
from typing import TypedDict
from utils.core import *

class GHRelease(TypedDict):
  tag_name: str
  published_at: str
  html_url: str
  prerelease: bool

DEFAULT_ORIGIN = 'leanprover/lean4'

def query_gh_releases(repo: str = DEFAULT_ORIGIN, paginate: bool = True) -> 'Iterator[GHRelease]':
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

def toolchain_sort_key(t: Toolchain):
    return (t['version'] or 0, of_utc_iso(t['date']))

MIN_TOOLCHAIN_SORT_KEY = (0, datetime.min.replace(tzinfo=timezone.utc))

TOOLCHAIN_VER_PATTERN = re.compile(r"[^:]*:v4\.(\d+)\..*")
def toolchain_version_number(toolchain: str):
  match = LEAN_VER_PATTERN.search(toolchain)
  return int(match.group(1)) if match is not None else None

LEAN_VER_PATTERN = re.compile(r"v4\.(\d+)\..*")
def lean_version_number(tag: str):
  match = LEAN_VER_PATTERN.search(tag)
  return int(match.group(1)) if match is not None else None

def query_gh_toolchains(repo: str = DEFAULT_ORIGIN) -> 'list[Toolchain]':
  def toolchain_of_release(rel: GHRelease) -> Toolchain:
    return {
      "name": f"{repo}:{rel['tag_name']}",
      "version":  lean_version_number(rel['tag_name']),
      "tag": rel['tag_name'],
      "date": rel['published_at'],
      "releaseUrl": rel['html_url'],
      "prerelease": rel['prerelease']
    }
  toolchains = map(toolchain_of_release, query_gh_releases(repo))
  return sorted(toolchains, key=toolchain_sort_key, reverse=True)

class ReleaseAsset(TypedDict):
  name: str
  browser_download_url: str

class Release(TypedDict):
  name: str
  created_at: str
  asset: list[ReleaseAsset]

class ReleaseResp(TypedDict):
  version: str
  stable: list[Release]
  beta: list[Release]
  nightly: list[Release]

def query_releases() -> 'ReleaseResp':
  return requests.get("https://release.lean-lang.org/").json()

def query_toolchains() -> 'list[Toolchain]':
  def toolchain_of_release(rel: Release, prerelease: bool) -> Toolchain:
    return {
      "name": f"{DEFAULT_ORIGIN}:{rel['name']}",
      "version":  lean_version_number(rel['name']),
      "tag": rel['name'],
      "date": rel['created_at'],
      "releaseUrl": f"https://github.com/leanprover/lean4/releases/tag/{rel['name']}",
      "prerelease": prerelease
    }
  resp = query_releases()
  toolchains = itertools.chain(
    (toolchain_of_release(rel, prerelease=False) for rel in resp["stable"]),
    (toolchain_of_release(rel, prerelease=True) for rel in resp["beta"]),
  )
  return sorted(toolchains, key=toolchain_sort_key, reverse=True)

def normalize_toolchain(toolchain: str) -> str:
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

def resolve_toolchain(toolchain: str, package_toolchain: T) -> str | T:
  if toolchain == 'package':
    return package_toolchain
  elif toolchain == 'stable':
    name = query_releases()['stable'][0]['name']
    return f"{DEFAULT_ORIGIN}:{name}"
  elif toolchain == 'nightly':
    name = query_releases()['nightly'][0]['name']
    return f"{DEFAULT_ORIGIN}:{name}"
  elif toolchain == 'latest':
    name = query_releases()['beta'][0]['name']
    return f"{DEFAULT_ORIGIN}:{name}"
  else:
    return normalize_toolchain(toolchain)

def split_toolchains(toolchains: Iterable[str]) -> Iterable[str]:
  for ts in toolchains:
    for t in ts.split(','):
      t = t.strip()
      if len(t) > 0 and t != 'none':
        yield t

def resolve_toolchains(toolchains: Iterable[str], package_toolchain: T = None) -> set[str | T]:
   return set(resolve_toolchain(t, package_toolchain) for t in split_toolchains(toolchains))
