import itertools
import json
import logging
import os
import subprocess

def load_index(path: str, include_builds=False):
  if os.path.isdir(path):
    pkgs = list()
    for owner in os.listdir(path):
      owner_dir = os.path.join(path, owner)
      for pkg in os.listdir(owner_dir):
        pkg_dir = os.path.join(owner_dir, pkg)
        with open(os.path.join(pkg_dir, 'metadata.json'), 'r') as f:
          pkg = json.load(f)
        if include_builds:
          builds_file = os.path.join(pkg_dir, 'builds.json')
          if os.path.exists(builds_file):
            with open(builds_file, 'r') as f:
              pkg['builds'] = json.load(f)
          else:
            pkg['builds'] = list()
        pkgs.append(pkg)
    pkgs = sorted(pkgs, key=lambda pkg: pkg['stars'], reverse=True)
  else:
    with open(path, 'r') as f:
      pkgs = json.load(f)
    if include_builds:
      for pkg in pkgs:
        pkg['builds'] = list()
  return pkgs

def add_build(builds: list, result: dict) -> list:
  builds = list(filter(lambda build: build['toolchain'] != result['toolchain'], builds))
  builds.append(result)
  return sorted(builds, key=lambda build: build['toolchain'], reverse=True)

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
