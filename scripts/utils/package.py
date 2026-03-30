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

class BuildResult(TypedDict):
  built: bool | None
  tested: bool | None
  toolchain: str
  requiredUpdate: bool | None
  archiveSize: int | None
  archiveHash: str | None
  runAt: str
  url: str | None

class Build(BuildResult):
  revision: str

class LicenseFileEntry(TypedDict, total=False):
  path: str
  sha256: str | None

class PackageVersionMetadata(TypedDict):
  version: str
  revision: str
  date: str
  tag: str | None
  toolchain: str | None
  platformIndependent: bool | None
  license: str | None
  licenseFiles: 'list[str | LicenseFileEntry]'
  readmeFile: str | None
  dependencies: list[Dependency]

class PackageVersion(PackageVersionMetadata):
  builds: list[BuildResult]
  unresolvedLicenseFiles: bool

class PackageResult(TypedDict):
  doIndex: bool
  name: str | None
  homepage: str | None
  description: str | None
  keywords: list[str] | None
  headVersion: PackageVersion
  versions: list[PackageVersion]

class TestbedEntry(TypedDict):
  artifact: str
  gitUrl: str
  jobName: str
  toolchains: str
  versionTags: str
  cacheBuilds: bool
  repoId: str | None
  indexName: str | None
  registrationKey: str | None
  checkLicenseFiles: bool

class TestbedLayer(TypedDict):
  name: str
  data: list[TestbedEntry]

TestbedMatrix = list[TestbedLayer]

class TestbedResult(PackageResult):
  repoId: str | None
  indexName: str | None
  registrationKey: str | None
  checkLicenseFiles: bool

TestbedResults = list[TestbedResult]

#`1.0.0: Reservoir 1.0
# 1.1.0: Added `archiveHash`
# 1.2.0: More Dependency data (`transitive``, `inputRev`, `url``)
# 1.3.0: `licenseFiles` changed from `list[str]` to `list[LicenseFileEntry]`
INDEX_SCHEMA_VERSION_STR = '1.3.0'
INDEX_SCHEMA_VERSION = Version(INDEX_SCHEMA_VERSION_STR)

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

class PackageRename(TypedDict):
  fullName: str
  relpath: str | None

class Package(PackageMetadata):
  schemaVersion: Version
  versions: list[PackageVersion]
  builds: list[Build]
  renames: list[PackageRename]
  relpath: str | None

class SerialPackage(PackageMetadata):
  dependents: list[Dependent]
  versions: list[PackageVersionMetadata]
  builds: list[Build]

#---
# Utils
#---

def package_metadata(pkg: PackageMetadata) -> PackageMetadata:
  return cast(PackageMetadata, {k: pkg[k] for k in PackageMetadata.__annotations__.keys()})

def mk_rename(pkg: Package) -> PackageRename:
  return {'fullName': pkg['fullName'], 'relpath': pkg['relpath']}

def package_of_metadata(
    data: PackageMetadata,
    relpath: str | None = None,
    schema_ver: Version = INDEX_SCHEMA_VERSION
  ) -> Package:
  pkg = cast(Package, data)
  pkg['relpath'] = relpath
  pkg['schemaVersion'] = schema_ver
  pkg['versions'] = []
  pkg['renames'] = [mk_rename(pkg)]
  pkg['builds'] = []
  return pkg

def normalize_license_file(entry: 'str | LicenseFileEntry') -> LicenseFileEntry:
  if isinstance(entry, str):
    return {'path': entry}
  return entry

def version_metadata(ver: PackageVersionMetadata) -> PackageVersionMetadata:
  data = cast(PackageVersionMetadata, {k: ver[k] for k in PackageVersionMetadata.__annotations__.keys()})
  data['licenseFiles'] = [normalize_license_file(e) for e in data['licenseFiles']]
  return data

def version_of_metadata(data: PackageVersionMetadata) -> PackageVersion:
  ver = cast(PackageVersion, data)
  ver['builds'] = []
  return ver

def mk_build(ver: PackageVersion, build: BuildResult) -> Build:
  build = cast(Build, build)
  build['revision'] = ver['revision']
  return build

def build_result(build: Build) -> BuildResult:
  return cast(BuildResult, {k: build.get(k, None) for k in BuildResult.__annotations__.keys()})

def serialize_package(pkg: Package) -> SerialPackage:
  r = cast(SerialPackage, package_metadata(pkg))
  r['dependents'] = []
  r['versions'] = []
  r['builds'] =  []
  for ver in pkg['versions']:
    r['versions'].append(version_metadata(ver))
    for build in ver['builds']:
      r['builds'].append(mk_build(ver, build))
  r['builds'].extend(pkg['builds'])
  return r

def walk_versions(result: PackageResult) -> Iterable[PackageVersion]:
  yield result['headVersion']
  yield from result['versions']

def walk_builds(result: PackageResult) -> Iterable[BuildResult]:
  for ver in walk_versions(result):
    yield from ver['builds']

def git_src(pkg: PackageMetadata) -> GitSrc | None:
  for src in pkg['sources']:
    if src.get('type', None) == 'git':
      return cast(GitSrc, src)
  return None

def git_url(pkg: PackageMetadata) -> str | None:
  for src in pkg['sources']:
    if src.get('type', None) == 'git':
      return cast(GitSrc, src)['gitUrl']
  return None

def github_src(pkg: PackageMetadata) -> GitHubSrc | None:
  for src in pkg['sources']:
    if src.get('host', None) == 'github':
      return cast(GitHubSrc, src)
  return None

def github_repo_id(pkg: PackageMetadata) -> str | None:
  for src in pkg['sources']:
    if src.get('host', None) == 'github':
      return cast(GitHubSrc, src)['id']
  return None
