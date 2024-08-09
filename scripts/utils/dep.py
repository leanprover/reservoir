import re
from typing import TypedDict, Literal, Union

class DepBase(TypedDict, total=False):
  name: str
  scope: str

class PathDep(DepBase, total=False):
  type: Literal['path']
  dir: str

class GitDep(DepBase, total=False):
  type: Literal['git']
  url: str

Dependency = Union[PathDep, GitDep]

class Manifest(TypedDict, total=False):
  name: str
  packages: list[Dependency]

# assumes escaped names are simple (which is fine for now)
FRENCH_QUOTE_PATTERN = re.compile('[«»]')
def unescape_name(name: str) -> str:
  return FRENCH_QUOTE_PATTERN.sub('', name)
