import logging
import subprocess
import itertools
import hashlib
from datetime import datetime, timezone
from typing import Any, Mapping, TypeVar, Iterable, Iterator, Literal, overload

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

def configure_logging(verbosity: int):
  if verbosity == 0:
    level = logging.CRITICAL
  elif verbosity == 1:
    level = logging.INFO
  else:
    level = logging.DEBUG
  logging.basicConfig(level=level, format='%(levelname)s: %(message)s')

# from https://antonz.org/page-iterator/
def paginate(iterable: 'Iterable[T]', page_size: int) -> 'Iterator[list[T]]':
  it = iter(iterable)
  slicer = lambda: list(itertools.islice(it, page_size))
  return iter(slicer, [])

# adapted from https://stackoverflow.com/questions/1094841/get-a-human-readable-version-of-a-file-size
def fmt_bytes(num: float):
  for unit in ("", "K", "M", "G", "T", "P", "E", "Z"):
    if abs(num) < 1000.0:
      return f"{num:3.1f} {unit}B"
    num /= 1000.0
  return f"{num:.1f} YB"

def ifnone(value: T | None, default: T) -> T:
  return default if value is None else value

def filter_type(type: type[T], value: Any, default: V = None) -> T | V:
  return value if isinstance(value, type) else default

def get_type(mapping: Mapping[K, Any], key: K, type: type[T], default: V = None) -> T | V:
  return filter_type(type, mapping.get(key, default), default)

def get_type_values(mapping: Mapping[K, Any], key: K, type: type[T]) -> Iterable[T]:
  for e in get_type(mapping, key, Iterable, []):
    if isinstance(e, type):
      yield e

def filter_ws(value: str | None):
  if value is not None:
    value = value.strip() or None
  return value

# adapted from https://stackoverflow.com/a/44873382
def filehash(path: str) -> str:
    "SHA-256 hash of a file"
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(path, 'rb', buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()

#---
# Time
#---

def fmt_utc_iso(dt: datetime):
  return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def utc_iso_now():
  return fmt_utc_iso(datetime.now(timezone.utc))

def utc_iso_of_timestamp(timestamp: int):
  return fmt_utc_iso(datetime.fromtimestamp(timestamp, timezone.utc))

def of_utc_iso(iso: str) -> datetime:
  return datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

def fmt_timestamp(timestamp: int):
  return datetime.fromtimestamp(timestamp).astimezone().strftime("%Y-%m-%d %I:%M:%S %p %z")

#---
# Commands
#---

class CommandError(RuntimeError):
  pass

def run_cmd(*args: str, allow_failure: bool =False):
  logging.debug(f'> {" ".join(args)}')
  rc = subprocess.run(args).returncode
  if not allow_failure and rc != 0:
    raise CommandError(f'external command exited with code {rc}')
  return rc

@overload
def capture_cmd(*args: str) -> bytes: ...

@overload
def capture_cmd(*args: str, allow_failure: Literal[False]) -> bytes: ...

@overload
def capture_cmd(*args: str, allow_failure: bool) -> bytes | None: ...

def capture_cmd(*args: str, allow_failure: bool = False):
  logging.debug(f'> {" ".join(args)}')
  child = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if child.returncode != 0:
    if allow_failure:
      return None
    else:
      raise CommandError(child.stderr.decode().strip())
  elif len(child.stderr) > 0:
    logging.error(child.stderr.decode())
  return child.stdout
