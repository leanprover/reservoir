#!/usr/bin/env bash
set -euxo pipefail

TESTBED="${TESTBED:-testbed}"

REPO=$1
DIR="${2:-$TESTBED/repos/$REPO}"
TOOLCHAIN=${3:-"leanprover/lean4:$(gh release list -R leanprover/lean4 -L 1 | cut -f1)"}

mkdir -p "$DIR"
rm -rf "$DIR"
git clone https://github.com/$REPO "$DIR"
cd "$DIR"
echo -n "$TOOLCHAIN" > lean-toolchain
lake exe cache get || true
if ! lake build; then
  echo "info: build failed, updating and trying again" >&2
  lake update
  lake clean
  lake exe cache get || true
  lake build
fi
echo "info: succesfully built $REPO on $TOOLCHAIN" >&2
