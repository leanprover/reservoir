#!/usr/bin/env python3
import os
import argparse
import shutil
import logging
import json
import tempfile
from typing import Collection
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
    return any(dep.get('name', None) == 'mathlib' for dep in deps)

def try_build(ver: PackageVersion, target_toolchain: str | None) -> tuple[BuildResult | None, bool]:
  # Reset directory
  run_cmd('git', 'reset', '--hard')
  run_cmd('git', 'clean', '-ffdx')
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
      logging.error(f"No toolchain configured to build {ver['toolchain']}")
      return None, False
  # Validate toolchain
  try:
    run_cmd('lake', '--version')
  except CommandError:
    logging.error("Failed to validate Lean/Lake toolchain installation")
    return None, True
  # Construct result
  result: BuildResult = {
    'built': None,
    'tested': None,
    'toolchain': target_toolchain,
    'requiredUpdate': False,
    'archiveSize': None,
    'date': utc_iso_now(),
    'url': None,
  }
  # Try build
  require_update = False
  uses_mathlib = has_mathlib(ver['dependencies'])
  logging.info(f'Building package revision {ver["revision"]} on {toolchain}')
  try:
    if uses_mathlib:
      logging.info(f'Mathlib dependency detected')
      require_update = cross_toolchain
    if not require_update:
      if uses_mathlib:
        run_cmd('lake', 'exe', 'cache', 'get', allow_failure=True)
      require_update = run_cmd('lake', 'build', allow_failure=True) != 0
      if require_update:
        logging.info('Failed to build package (without `lake update`)')
    if require_update:
      logging.info('Updating dependencies and then trying build')
      run_cmd('lake', 'update')
      if uses_mathlib:
        run_cmd('lake', 'exe', 'cache', 'get', allow_failure=True)
      run_cmd('lake', 'build')
    logging.info(f'Successfully built package')
    result['built'] = True
  except CommandError:
    logging.error(f'Failed to build package')
    result['built'] = False
    return result, True
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
      return result, True
  else:
    logging.warning(f"No package test driver found; skipped testing")
  return result, False

def try_add_build(ver: PackageVersion, target_toolchain: str | None):
  result, failure = try_build(ver, target_toolchain)
  if result is not None: ver['builds'].append(result)
  return failure

def try_add_builds(ver: PackageVersion, target_toolchains: Collection[str | None]):
  failure = False
  if len(target_toolchains) == 0:
    logging.info("No target toolchains specified; skipping build")
  for toolchain in target_toolchains:
    failure = try_add_build(ver, toolchain) or failure
  return failure

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
      return Manifest(json.load(f))
  except (FileNotFoundError, json.JSONDecodeError) as e:
    logging.error(f'Failed to read manifest: {e}')
    return Manifest()

def cwd_reservoir_config(toolchain: str | None = None) -> ReservoirConfig | None:
  lake_ver = None if toolchain is None else toolchain_version_number(toolchain)
  if lake_ver is not None and lake_ver < 12:
    return None # short-circuit downloading old toolchains
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

VERSION_TAG_PATTERN = re.compile(r'v(\d+).*')

def cwd_analyze(target_toolchains: Collection[str | None] = [], tag_regex: re.Pattern[str] | None = None) -> tuple[PackageResult, bool]:
  failure = False
  # Extract Reservoir configuration from Lake
  logging.info(f"Analyzing package HEAD")
  manifest = cwd_manifest()
  toolchain = cwd_toolchain()
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
      'toolchain': toolchain,
      'dependencies': manifest.dependencies,
      'builds': [],
    },
    'versions': list(),
  }
  cfg = cwd_reservoir_config(toolchain)
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
    name = manifest.name
    if name is not None:
      result['name'] = unescape_name(name)
    try:
      tags = capture_cmd('git', 'tag').decode().splitlines()
      version_tags = [tag for tag in tags if VERSION_TAG_PATTERN.match(tag) is not None]
    except CommandError as e:
      logging.error(f'Failed to fetch repository tags: {e}')
      version_tags = None
  # Index and build versions
  if result['index']:
    if tag_regex is None:
      failure = try_add_builds(result['headVersion'], target_toolchains) or failure
    if version_tags is not None:
      logging.info(f'Detected version tags: {version_tags}')
      for tag in version_tags:
        logging.info(f'Analyzing version tag {tag}')
        cwd_checkout(tag)
        toolchain = cwd_toolchain()
        cfg = cwd_reservoir_config(toolchain)
        ver: PackageVersion = {
          'date': cwd_commit_date(),
          'revision': cwd_head_revision(),
          'tag': tag,
          'version': cfg.get('version', '0.0.0') if cfg is not None else '0.0.0',
          'toolchain': toolchain,
          'dependencies': cwd_manifest().dependencies,
          'builds': [],
        }
        result['versions'].append(ver)
        if tag_regex is not None and tag_regex.search(tag) is not None:
          failure = try_add_builds(ver, target_toolchains) or failure
  return result, failure

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('url', nargs='?', type=str, default=None,
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

  # Make testbed
  if args.testbed is None:
    testbed = tempfile.mkdtemp()
    logging.debug(f"Created temporary testbed: {testbed}")
    reuse_clone = False
  else:
    testbed = args.testbed
    reuse_clone = bool(args.reuse_clone) and os.path.exists(testbed)
    if not reuse_clone:
      os.makedirs(testbed, exist_ok=True)
      shutil.rmtree(testbed)

  try:
    # Extract matrix configuration
    if args.matrix is not None:
      entry: TestbedEntry = json.loads(args.matrix)
      url = entry['gitUrl']
      target_toolchains = resolve_toolchains(entry['toolchains'])
    else:
      if args.url is None and not reuse_clone:
        raise RuntimeError("a Git URL is required (either by argument or through `--matrix`)")
      url: str | None = args.url
      target_toolchains = resolve_toolchains(args.toolchain)

    # Compile tag regex (if provided)
    tag_regex: re.Pattern[str] | None = None
    if args.tag_regex is not None:
      tag_regex = re.compile(args.tag_regex)

    # Clone, analyze, and build package
    iwd = os.getcwd()
    os.chdir(testbed)
    if url is not None:
      run_cmd('git', 'clone', url, '.')
    run_cmd('git', 'fetch', '--tags', '--force')
    if args.head:
      cwd_checkout(args.head)
    result, failure = cwd_analyze(target_toolchains, tag_regex)
    os.chdir(iwd)

    # Output result
    if args.output is None:
      print(json.dumps(result, indent=2))
    else:
      with open(args.output, 'w') as f:
        f.write(json.dumps(result, indent=2))

  finally:
    # Cleanup
    if args.testbed is None: # temp testbed
      shutil.rmtree(testbed)
      logging.debug(f"Removed temporary testbed: {testbed}")

  if failure:
    exit(1)
