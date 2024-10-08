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
  version: str
  versionTags: list[str]
  description: str
  homepage: str
  keywords: list[str]
  platformIndependent: bool
  license: str
  licenseFiles: list[str]
  readmeFile: str | None
  doIndex: bool

def has_mathlib(deps: list[Dependency] | None):
  if deps is None:
    return None
  else:
    return any(dep.get('name', None) == 'mathlib' for dep in deps)

def try_build(
    ver: PackageVersion,
    build_dir: str | None,
    target_toolchain: str | None,
    is_mathlib: bool = False
    )-> tuple[BuildResult | None, bool]:
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
    'archiveHash': None,
    'runAt': utc_iso_now(),
    'url': None,
  }
  # Try build
  require_update = False
  uses_mathlib = is_mathlib or has_mathlib(ver['dependencies'])
  logging.info(f'Building package revision {ver["revision"]} on {toolchain}')
  try:
    if uses_mathlib:
      logging.info(f'Mathlib detected; will use build cache')
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
  with tempfile.TemporaryDirectory() as tmp:
    archive = os.path.join(tmp, 'build.barrel')
    if run_cmd('lake', 'pack', archive, allow_failure=True) != 0:
      logging.error('Failed to pack build archive')
    else:
      archive_size = result['archiveSize'] = os.path.getsize(archive)
      logging.info(f'Packed build archive size: {fmt_bytes(archive_size)} ({archive_size})')
      if build_dir is not None:
        archive_hash = result['archiveHash'] = filehash(archive)
        shutil.move(archive, os.path.join(build_dir, f"{archive_hash}.barrel"))
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

def try_add_builds(
    ver: PackageVersion,
    build_dir: str | None,
    target_toolchains: Collection[str | None],
    is_mathlib: bool = False
    ):
  failure = False
  if len(target_toolchains) == 0:
    logging.info("No target toolchains specified; skipping build")
  for toolchain in target_toolchains:
    result, toolchain_failure = try_build(ver, build_dir, toolchain, is_mathlib)
    if result is not None: ver['builds'].append(result)
    failure = toolchain_failure or failure
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

def cfg_default(cfg: ReservoirConfig | None, key: str, type: type[T], default: V = None) -> T | V:
  return get_type(cfg, key, type, default) if cfg is not None else default

def cwd_licenses(cfg: ReservoirConfig | None) -> list[str]:
  if cfg is None:
    if os.path.exists('LICENSE'):
      return ['LICENSE']
    else:
      return []
  return cfg.get('licenseFiles', [])

def cwd_readme(cfg: ReservoirConfig | None) -> str | None:
  if cfg is None:
    if os.path.exists('README.md'):
      return 'README.md'
    else:
      return None
  else:
    return get_type(cfg, 'readmeFile', str)

VERSION_TAG_PATTERN = re.compile(r'v(\d+).*')

def cwd_analyze(
    out_dir: str,
    cache_builds: bool = False,
    target_toolchains: Collection[str | None] = [],
    tag_pattern: re.Pattern[str] | None = None
    ) -> tuple[PackageResult, bool]:
  failure = False
  # Extract Reservoir configuration from Lake
  logging.info(f"Analyzing package HEAD")
  manifest = cwd_manifest()
  toolchain = cwd_toolchain()
  result: PackageResult = {
    'name': None,
    'doIndex': True,
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
      'platformIndependent': None,
      'license': None,
      'licenseFiles': [],
      'readmeFile': None,
      'builds': [],
    },
    'versions': list(),
  }
  cfg = cwd_reservoir_config(toolchain)
  if cfg is not None:
    name = get_type(cfg, 'name', str)
    if name is not None:
      result['name'] = unescape_name(name)
    result['doIndex'] = get_type(cfg, 'doIndex', bool, True)
    result['homepage'] = filter_ws(get_type(cfg, 'homepage', str))
    result['description'] = filter_ws(get_type(cfg, 'description', str))
    result['keywords'] = list(get_type_values(cfg, 'keywords', str))
    result['headVersion']['version'] = get_type(cfg, 'version', str, '0.0.0')
    result['headVersion']['platformIndependent'] = get_type(cfg, 'platformIndependent', bool, None)
    result['headVersion']['license'] = filter_license(get_type(cfg, 'license', str))
    result['headVersion']['licenseFiles'] = list(get_type_values(cfg, 'licenseFiles', str))
    result['headVersion']['readmeFile'] = cwd_readme(cfg)
    version_tags = list(get_type_values(cfg, 'versionTags', str))
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
  is_mathlib = result['name'] == 'mathlib'
  build_dir = out_dir if cache_builds else None
  if result['doIndex']:
    if tag_pattern is None:
      failure = try_add_builds(result['headVersion'], build_dir, target_toolchains, is_mathlib) or failure
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
          'version': cfg_default(cfg, 'version', str, '0.0.0'),
          'toolchain': toolchain,
          'platformIndependent': cfg_default(cfg, 'platformIndependent', bool),
          'license': filter_ws(cfg_default(cfg, 'license', str)),
          'licenseFiles': cwd_licenses(cfg),
          'readmeFile': cwd_readme(cfg),
          'dependencies': cwd_manifest().dependencies,
          'builds': [],
        }
        result['versions'].append(ver)
        if tag_pattern is not None and tag_pattern.search(tag) is not None:
          failure = try_add_builds(ver, build_dir, target_toolchains, is_mathlib) or failure
  return result, failure

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('url', nargs='?', type=str, default=None,
    help="Git URL of the repository to clone")
  parser.add_argument('-m', '--matrix', type=str, default=None,
    help='JSON testbed matrix entry with build configuration')
  parser.add_argument('-d', '--testbed', type=str, default=None,
    help="directory to test in and output results")
  parser.add_argument('-T', '--toolchain', type=str, nargs='*', action='extend', default=[],
    help="Lean toolchain(s) on build the package on")
  parser.add_argument('-o', '--output', type=str, default=None,
    help='file to output the build results')
  parser.add_argument('-V', '--version-tags', type=str, default=None,
    help='select version tags to build by regular expression')
  parser.add_argument('--cache', action='store_true', default=True,
    help="include build archives in artifact")
  parser.add_argument('--no-cache', dest='cache', action='store_false',
    help="do not include build archives in artifact")
  parser.add_argument('-q', '--quiet', dest="verbosity", action='store_const', const=0, default=1,
    help='print no logging information')
  parser.add_argument('-v', '--verbose', dest="verbosity", action='store_const', const=2,
    help='print verbose logging information')
  parser.add_argument('-R', '--reuse-clone', action='store_true', default=False,
    help='reuse cloned repository if it already exists')
  parser.add_argument('-H', '--head', type=str, default=None,
    help='initial revision of the repository to checkout')
  args = parser.parse_args()

  configure_logging(args.verbosity)

  # Make testbed
  if args.testbed is None:
    testbed = tempfile.mkdtemp()
    logging.debug(f"Created temporary testbed: {testbed}")
    reuse_clone = False
    repo = os.path.join(testbed, 'repo')
  else:
    testbed = os.path.abspath(args.testbed)
    repo = os.path.join(testbed, 'repo')
    reuse_clone = bool(args.reuse_clone) and os.path.exists(repo)
    if not reuse_clone:
      os.makedirs(repo, exist_ok=True)
      shutil.rmtree(repo)

  # Make output directory
  out_dir = os.path.join(testbed, 'artifact')
  os.makedirs(out_dir, exist_ok=True)

  try:

    # Extract matrix configuration
    if args.matrix is not None:
      entry: TestbedEntry = json.loads(args.matrix)
      url = entry['gitUrl']
      target_toolchains = resolve_toolchains([entry['toolchains']])
      version_tags = entry['versionTags']
      cache_builds = entry['cacheBuilds']
    else:
      if args.url is None and not reuse_clone:
        raise RuntimeError("a Git URL is required (either by argument or through `--matrix`)")
      url: str | None = args.url
      target_toolchains = resolve_toolchains(args.toolchain)
      version_tags = args.version_tags
      cache_builds = args.cache

    # Compile version tag regex (if provided)
    tag_pattern: re.Pattern[str] | None = None
    if version_tags == '':
      tag_pattern = None
    elif version_tags is not None:
      tag_pattern = re.compile(version_tags)

    # Clone, analyze, and build package
    iwd = os.getcwd()
    logging.info(f"Setting up testbed in '{repo}'")
    os.makedirs(repo, exist_ok=True)
    os.chdir(repo)
    if url is not None and not reuse_clone:
      run_cmd('git', 'clone', url, '.')
    run_cmd('git', 'fetch', '--tags', '--force')
    if args.head:
      cwd_checkout(args.head)
    result, failure = cwd_analyze(out_dir, cache_builds, target_toolchains, tag_pattern)
    os.chdir(iwd)

    # Output result
    result_file = ifnone(args.output, os.path.join(out_dir, 'result.json'))
    with open(result_file, 'w') as f:
      f.write(json.dumps(result, indent=2))

  finally:
    # Cleanup
    if args.testbed is None: # temp testbed
      shutil.rmtree(testbed)
      logging.debug(f"Removed temporary testbed: {testbed}")

  if failure:
    exit(1)
