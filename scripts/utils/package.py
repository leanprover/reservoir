from utils.core import *
from utils.manifest import *
from typing import Literal, Iterable, TypedDict, cast

#---
# Types
#---

class PackageSrc(TypedDict, total=False):
  type: str
  host: str
  id: str
  fullName: str
  repoUrl: str
  gitUrl: str
  defaultBranch: str

class GitSrc(TypedDict):
  type: Literal['git']
  gitUrl: str
  defaultBranch: str

class GitHubSrc(GitSrc):
  host: Literal['github']
  id: str
  fullName: str
  repoUrl: str

class OldBuildBase(TypedDict):
  url: str | None
  builtAt: str
  revision: str
  toolchain: str
  outcome: str

class OldBuild(OldBuildBase, total=False):
  requiredUpdate: bool
  archiveSize: int | None

class BuildResult(TypedDict):
  built: bool | None
  tested: bool | None
  toolchain: str
  requiredUpdate: bool
  archiveSize: int | None
  date: str
  url: str | None

class PackageVersionMetadata(TypedDict):
  version: str | None
  revision: str
  date: str
  tag: str | None
  toolchain: str | None
  dependencies: list[Dependency] | None

class PackageVersion(PackageVersionMetadata):
  builds: list[BuildResult]

class PackageResult(TypedDict):
  index: bool
  name: str | None
  homepage: str | None
  description: str | None
  keywords: list[str] | None
  headVersion: PackageVersion
  versions: list[PackageVersion]

class TestbedEntry(TypedDict):
  artifact: str
  gitUrl: str
  buildName: str
  toolchains: str
  repoId: str

class PackageMetadata(TypedDict):
  name: str
  owner: str
  fullName: str
  description: str | None
  keywords: list[str] | None
  homepage: str | None
  license: str | None
  createdAt: str
  updatedAt: str
  stars: int
  sources: list[PackageSrc]
  versions: list[PackageVersionMetadata]

class Package(PackageMetadata):
  builds: list[OldBuild]
  renames: list['Package']
  path: str | None

class SerialPackage(PackageMetadata):
  builds: list[OldBuild]

#---
# Utils
#---

def package_metadata(pkg: Package) -> PackageMetadata:
  return cast(PackageMetadata, {k: pkg[k] for k in PackageMetadata.__annotations__.keys()})

def serialize_package(pkg: Package) -> SerialPackage:
   return cast(SerialPackage, {k: pkg[k] for k in SerialPackage.__annotations__.keys()})

def package_of_metadata(data: PackageMetadata) -> Package:
  pkg = cast(Package, data)
  pkg['path'] = None
  pkg['builds'] = []
  pkg['renames'] = []
  return pkg

def version_metadata(ver: PackageVersion) -> PackageVersionMetadata:
  return cast(PackageVersionMetadata, {k: ver[k] for k in PackageVersionMetadata.__annotations__.keys()})

def walk_versions(result: PackageResult) -> Iterable[PackageVersion]:
  yield result['headVersion']
  yield from result['versions']

def walk_builds(result: PackageResult) -> Iterable[BuildResult]:
  for ver in walk_versions(result):
    yield from ver['builds']

def git_src(pkg: Package) -> GitSrc | None:
  for src in pkg['sources']:
    if src.get('type', None) == 'git':
      return cast(GitSrc, src)
  return None

def github_src(pkg: Package) -> GitHubSrc | None:
  for src in pkg['sources']:
    if src.get('host', None) == 'github':
      return cast(GitHubSrc, src)
  return None

def github_repo_id(pkg: Package) -> str | None:
  for src in pkg['sources']:
    if src.get('host', None) == 'github':
      return cast(GitHubSrc, src)['id']
  return None
