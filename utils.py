import itertools
import json
import logging
import os
import subprocess

def load_index(path: str):
  if os.path.isdir(path):
    pkgs = list()
    for owner in os.listdir(path):
      owner_dir = os.path.join(path, owner)
      for pkg in os.listdir(owner_dir):
        md_file = os.path.join(owner_dir, pkg, 'metadata.json')
        with open(md_file, 'r') as f:
          pkgs.append(json.load(f))
    pkgs = sorted(pkgs, key=lambda pkg: pkg['stars'], reverse=True)
  else:
    with open(path, 'r') as f:
      pkgs = json.load(f)
  return pkgs

# from https://antonz.org/page-iterator/
def paginate(iterable, page_size):
  it = iter(iterable)
  slicer = lambda: list(itertools.islice(it, page_size))
  return iter(slicer, [])

def run_cmd(*args: str) -> bytes:
  child = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if child.returncode != 0:
    raise RuntimeError(child.stderr.decode().strip())
  elif len(child.stderr) > 0:
    logging.error(child.stderr.decode())
  return child.stdout
