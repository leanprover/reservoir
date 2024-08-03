import re
from typing import TypedDict, Any

# assumes escaped names are simple (which is fine for now)
FRENCH_QUOTE_PATTERN = re.compile('[«»]')
def unescape_name(name: str) -> str:
  return FRENCH_QUOTE_PATTERN.sub('', name)

class Dependency(TypedDict):
  type: str
  name: str
  scope: str
  version: str
  rev: str | None

def mk_dependency(contents: Any, type: str | None = None) -> Dependency | None:
  if not isinstance(contents, dict): return None
  type = type or contents.get('type', None)
  if type is None: return None
  name = contents.get('name', None)
  if name is None: return None
  return {
    'type': type,
    'name': unescape_name(name),
    'scope': contents.get('scope', ''),
    'version': contents.get('version', '0.0.0'),
    'rev': contents.get('rev', None),
  }

MANIFEST_VERSION_PATTERN = re.compile(r'(\d+)\.(\d+)\.(\d+)(?:-(.*))?')

class ManifestVersion:
  major: int
  minor: int
  patch: int
  special_descr: str

  def __init__(self, ver: str | int | None = None) -> None:
    self.major = 0
    self.minor = 0
    self.patch = 0
    self.specialDescr = ''
    if ver is None:
      return
    if isinstance(ver, int):
      self.minor = ver
      return
    match = MANIFEST_VERSION_PATTERN.match(ver)
    if match is not None:
      self.major = int(match.group(1))
      self.minor = int(match.group(2))
      self.patch = int(match.group(3))
      self.special_descr = match.group(4)

  def __lt__(self, other: 'ManifestVersion | int'):
    if isinstance(other, int):
      return self.major == 0 and self.minor < other
    else:
      if self.major != other.major: return self.major < other.major
      if self.minor != other.minor: return self.minor < other.minor
      if self.patch != other.patch: return self.patch < other.patch
      if self.special_descr != other.special_descr:
        if self.special_descr == '': return True
        if other.special_descr == '': return False
        return self.special_descr < other.special_descr
      return False

class Manifest():
  name: str | None
  dependencies: list[Dependency]

  def __init__(self, contents: Any = None) -> None:
    self.name = None
    self.dependencies = []
    if not isinstance(contents, dict):
      return
    manifest_version = ManifestVersion(contents.get('version', None))
    name = contents.get('name', None)
    if name is not None:
      self.name = unescape_name(str(name))
    deps = contents.get('packages', None)
    if not isinstance(deps, list):
      return
    for manifest_dep in deps:
      if not isinstance(manifest_dep, dict):
        continue
      if manifest_version < 7:
        dep = mk_dependency(manifest_dep.get('path', None), 'path')
        if dep is not None:
          self.dependencies.append(dep)
          continue
        dep = mk_dependency(manifest_dep.get('git', None), 'git')
        if dep is not None:
          self.dependencies.append(dep)
          continue
      else:
        dep = mk_dependency(manifest_dep)
        if dep is not None:
          self.dependencies.append(dep)
