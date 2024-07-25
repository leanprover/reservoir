import logging
import subprocess
import itertools
from datetime import datetime, timezone
from typing import TypeVar, Iterable, Iterator

T = TypeVar('T')

def configure_logging(verbosity):
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

#---
# Time
#---

def utc_iso_now():
  return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def of_utc_iso(iso: str) -> datetime:
  return datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

def fmt_timestamp(timestamp: int):
  return datetime.fromtimestamp(timestamp).astimezone().strftime("%Y-%m-%d %I:%M:%S %p %z")

#---
# Commands
#---

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
