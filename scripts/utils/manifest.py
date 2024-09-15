import re
from typing import TypedDict, Any, NoReturn, overload
from functools import total_ordering

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

VERSION_PATTERN = re.compile(r'(\d+)\.(\d+)\.(\d+)(?:-(.*))?')

@total_ordering
class Version:
  major: int
  minor: int
  patch: int
  special_descr: str

  @overload
  def __init__(self, ver: Any) -> NoReturn: ...

  @overload
  def __init__(self, ver: 'Version | str | int | None' = None) -> None: ...

  def __init__(self, ver: Any = None) -> None:
    if ver is None:
      self.major = 0
      self.minor = 0
      self.patch = 0
      self.special_descr = ''
    elif isinstance(ver, int):
      self.major = 0
      self.minor = ver
      self.patch = 0
      self.special_descr = ''
    elif isinstance(ver, str):
      match = VERSION_PATTERN.match(ver)
      if match is None:
        raise ValueError("Ill-formed version string")
      self.major = int(match.group(1))
      self.minor = int(match.group(2))
      self.patch = int(match.group(3))
      self.special_descr = match.group(4)
    elif isinstance(ver, Version):
      self.major = ver.major
      self.minor = ver.minor
      self.patch = ver.patch
      self.special_descr = ver.special_descr
    else:
      raise TypeError("Invalid type for Version initializer: expected Version, str, int, or None")

  def __eq__(self, other):
    if not isinstance(other, Version):
      try:
        other = Version(other)
      except (TypeError, ValueError):
        return False
    if self.major != other.major: return False
    if self.minor != other.minor: return False
    if self.patch != other.patch: return False
    if self.special_descr != other.special_descr: return False
    return True

  def __lt__(self, other: 'Version | str | int | None'):
    if not isinstance(other, Version):
      other = Version(other)
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
    try:
      manifest_version = Version(contents.get('version', None))
    except (TypeError, ValueError):
      return
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
