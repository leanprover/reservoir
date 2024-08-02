import re
import json
from typing import TypedDict
from utils.core import *

class Release(TypedDict):
  tag_name: str
  published_at: str
  html_url: str
  prerelease: bool

DEFAULT_ORIGIN = 'leanprover/lean4'

def query_releases(repo: str = DEFAULT_ORIGIN, paginate: bool = True) -> 'Iterator[Release]':
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

TOOLCHAIN_VER_PATTERN = re.compile("v4\\.(\\d+)\\..*")
def query_toolchains(repo: str = DEFAULT_ORIGIN) -> 'list[Toolchain]':
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

def split_toolchains(toolchains: Iterable[str]) -> Iterable[str]:
  for ts in toolchains:
    for t in ts.split(','):
      t = t.strip()
      if len(t) > 0 and t != 'none':
        yield t

def resolve_toolchains(toolchains: Iterable[str], package_toolchain: T = None) -> set[str | T]:
   return set(resolve_toolchain(t, package_toolchain) for t in split_toolchains(toolchains))
