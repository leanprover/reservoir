#!/usr/bin/env python3
import os
import argparse
import shutil
import logging
import json
import tempfile
from utils import *

MANIFEST_FILE = 'lake-manifest.json'
TOOLCHAIN_FILE ='lean-toolchain'

class ReservoirConfig(TypedDict, total=False):
  name: str
  homepage: str
  description: str
  version: str
  versionTags: list[str]
  index: bool
  keywords: list[str]

def has_mathlib(deps: list[Dependency] | None):
  if deps is None:
    return None
  else:
    return any(dep.get('name', '') == 'mathlib' for dep in deps)

def try_build(ver: PackageVersion, target_toolchain: str | None) -> BuildResult | None:
  # Update toolchain
  toolchain = ver['toolchain']
  cross_toolchain = False
  if target_toolchain is not None:
    if ver['toolchain'] != target_toolchain:
      cross_toolchain = True
      with open(TOOLCHAIN_FILE, 'w') as f:
        f.write(target_toolchain)
        f.write('\n')
  else:
    target_toolchain = ver['toolchain']
    if target_toolchain is None:
      return None
  # Validate toolchain
  try:
    run_cmd('lake', '--version')
  except CommandError:
    logging.error("Failed to validate Lean/Lake toolchain installation")
    return None
  # Construct result
  result: BuildResult = {
    'built': None,
    'tested': None,
    'toolchain': target_toolchain,
    'requiredUpdate': False,
    'archiveSize': None,
  }
  # Try build
  required_update = False
  uses_mathlib = has_mathlib(ver['dependencies'])
  logging.info(f'Building package revision {ver["revision"]} on {toolchain}')
  try:
    if uses_mathlib:
      logging.info(f'Mathlib detected; trying to fetch cache')
      required_update = cross_toolchain
      run_cmd('lake', 'exe', 'cache', 'get', allow_failure=True)
    if not required_update:
      required_update = run_cmd('lake', 'build', allow_failure=True) != 0
      if required_update:
        logging.info('Build failed, updating and trying again')
    if required_update:
      run_cmd('lake', 'update')
      if uses_mathlib:
        run_cmd('lake', 'exe', 'cache', 'get', allow_failure=True)
      run_cmd('lake', 'build')
    logging.info(f'Successfully built package')
    result['built'] = True
  except CommandError:
    logging.error(f'Failed to build package')
    result['built'] = False
    return result
  # Try to pack result
  try:
    with tempfile.TemporaryDirectory() as tmp:
      archive = os.path.join(tmp, 'build.tgz')
      run_cmd('lake', 'pack', archive)
      archiveSize = result['archiveSize'] = os.path.getsize(archive)
      logging.info(f'Packed build archive size: {fmt_bytes(archiveSize)} ({archiveSize})')
  except Exception as e:
    logging.error(f'Failed to pack build archive: {e}')
  # Try test
  if run_cmd('lake', 'check-test', allow_failure=True) == 0:
    success = result['tested'] = run_cmd('lake', 'test', allow_failure=True) == 0
    if success:
      logging.info(f"Package tests ran successfully")
    else:
      logging.error(f"Package tests ran, but failed")
  else:
    logging.warning(f"No package test driver found; skipped testing")
  return result

def try_add_build(ver: PackageVersion, target_toolchain: str | None):
  result = try_build(ver, target_toolchain)
  if result is not None: ver['builds'].append(result)

def try_add_builds(ver: PackageVersion, target_toolchains: Iterable[str | None]):
  for toolchain in target_toolchains:
    try_add_build(ver, toolchain)

def cwd_toolchain():
  """Return the Lean toolchain of the current working directory."""
  try:
    with open(TOOLCHAIN_FILE, 'r') as f:
      toolchain = f.read().strip()
      if len(toolchain) > 0:
        return normalize_toolchain(toolchain)
      else:
        return None
  except OSError:
    return None

def cwd_head_revision():
  """Return the Git revision (in hash form) of the current working directory."""
  return capture_cmd('git', 'rev-parse', 'HEAD').decode().strip()

def cwd_manifest() -> Manifest:
  try:
    with open(MANIFEST_FILE, 'r') as f:
      return json.load(f)
  except (FileNotFoundError, json.JSONDecodeError) as e:
    logging.error(f'Failed to read manifest: {e}')
    return Manifest()

def decode_deps(manifest: Manifest) -> list[Dependency] | None:
  return manifest.get('packages', None)

def cwd_reservoir_config() -> ReservoirConfig | None:
  try:
    return json.loads(capture_cmd('lake', 'reservoir-config', '1.0.0'))
  except (CommandError, json.JSONDecodeError) as e:
    logging.error(f"Failed to run `lake reservoir-config`: {e}")
    return None

def cwd_commit_date() -> str:
  return utc_iso_of_timestamp(int(capture_cmd('git', 'show', '-s', '--format=%ct').decode().strip()))

def cwd_head_tag() -> str | None:
  tag = capture_cmd("git", "describe", "--tags", "--exact-match", "HEAD", allow_failure=True)
  if tag is None: return None
  return tag.decode().strip()

def cwd_checkout(rev: str):
  run_cmd('git', 'checkout', '--detach', "--force", rev)

def cwd_analyze(target_toolchains: Iterable[str | None] = [], tag_regex: re.Pattern[str] | None = None):
  # Extract Reservoir configuration from Lake
  logging.info(f"Analyzing package HEAD")
  manifest = cwd_manifest()
  result: PackageResult = {
    'name': None,
    'index': True,
    'homepage': None,
    'description': None,
    'keywords': None,
    'headVersion': {
      'date': cwd_commit_date(),
      'revision': cwd_head_revision(),
      'tag': cwd_head_tag(),
      'version': '0.0.0',
      'toolchain': cwd_toolchain(),
      'dependencies': decode_deps(manifest),
      'builds': [],
    },
    'versions': list(),
  }
  cfg = cwd_reservoir_config()
  if cfg is not None:
    result['name'] = cfg.get('name', None)
    result['index'] = cfg.get('index', True)
    result['homepage'] = cfg.get('homepage', None)
    result['description'] = cfg.get('description', None)
    result['keywords'] = cfg.get('keywords', [])
    result['headVersion']['version'] = cfg.get('version', '0.0.0')
    version_tags = cfg.get('versionTags', list[str]())
  else:
    cfg = ReservoirConfig()
    name = manifest.get('name', None)
    if name is not None:
      result['name'] = unescape_name(name)
    try:
      tags = capture_cmd('git', 'tag').decode().splitlines()
      version_tags = [tag for tag in tags if tag.startswith('v')]
    except CommandError as e:
      logging.error(f'Failed to fetch repository tags: {e}')
      version_tags = None
  # Index and build versions
  if result.get('index', True):
    if tag_regex is None:
      try_add_builds(result['headVersion'], target_toolchains)
    if version_tags is not None:
      logging.info(f'Detected version tags: {version_tags}')
      for tag in version_tags:
        logging.info(f'Analyzing version tag {tag}')
        cwd_checkout(tag)
        cfg = cwd_reservoir_config()
        ver: PackageVersion = {
          'date': cwd_commit_date(),
          'revision': cwd_head_revision(),
          'tag': tag,
          'version': cfg.get('version', '0.0.0') if cfg is not None else '0.0.0',
          'toolchain': cwd_toolchain(),
          'dependencies': decode_deps(cwd_manifest()),
          'builds': [],
        }
        result['versions'].append(ver)
        if tag_regex is not None and tag_regex.search(tag) is not None:
          try_add_builds(ver, target_toolchains)
  return result

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('-u', '--url', type=str, default=None,
    help="Git URL of the repository to clone")
  parser.add_argument('-m', '--matrix', type=str, default=None,
    help='JSON testbed matrix entry with build configuration')
  parser.add_argument('-d', '--testbed', type=str, default=None,
    help="directory to clone the package into")
  parser.add_argument('-t', '--toolchain', type=str, nargs='*', action='extend', default=[],
    help="Lean toolchain(s) on build the package on")
  parser.add_argument('-o', '--output', type=str, default=None,
    help='file to output the build results')
  parser.add_argument('-e', '--tag-regex', type=str, default=None,
    help='build tags by regular expression')
  parser.add_argument('-q', '--quiet', dest="verbosity", action='store_const', const=0, default=1,
    help='print no logging information')
  parser.add_argument('-v', '--verbose', dest="verbosity", action='store_const', const=2,
    help='print verbose logging information')
  parser.add_argument('-R', '--reuse-clone', action='store_true', default=False,
    help='reuse cloned repository if it already exists')
  parser.add_argument('-H', '--head', type=str, default=None,
    help='the initial revision of the repository to checkout')
  args = parser.parse_args()

  configure_logging(args.verbosity)

  if args.matrix is not None:
    entry: TestbedEntry = json.loads(args.matrix)
    url = entry['gitUrl']
    target_toolchains = resolve_toolchains(entry['toolchains'])
  else:
    if args.url is None:
      raise RuntimeError("a Git URL is required (either through `-u` or `-m`)")
    url: str = args.url
    target_toolchains = set[str | None]()

  # Compile tag regex (if provided)
  tag_regex: re.Pattern[str] | None = None
  if args.tag_regex is not None:
    tag_regex = re.compile(args.tag_regex)

  # Make testbed
  if args.testbed is None:
    testbed = tempfile.mkdtemp()
  else:
    testbed = args.testbed
    if not (args.reuse_clone and os.path.exists(testbed)):
      os.makedirs(testbed, exist_ok=True)
      shutil.rmtree(testbed)

  # Clone, analyze, and build package
  iwd = os.getcwd()
  os.chdir(testbed)
  run_cmd('git', 'clone', args.url, '.')
  if args.head:
    cwd_checkout(args.head)
  run_cmd('git', 'fetch', '--tags', '--force')
  result = cwd_analyze(target_toolchains, tag_regex)
  os.chdir(iwd)

  # Output result
  if args.output is None:
    print(json.dumps(result, indent=2))
  else:
    with open(args.output, 'w') as f:
      f.write(json.dumps(result, indent=2))

  # Cleanup
  if args.testbed is None: # temp testbed
    shutil.rmtree(testbed)
