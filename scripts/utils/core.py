import logging
import subprocess
import itertools
from datetime import datetime, timezone
from typing import TypeVar, Iterable, Iterator, Literal, overload

T = TypeVar('T')

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
