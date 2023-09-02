#!/usr/bin/env bash
set -euo pipefail

TESTBED="${TESTBED:-testbed}"
REPO_FILE="${1:-"$TESTBED/test-repos.txt"}"
TOOLCHAIN=${2:-"leanprover/lean4:$(gh release list -R leanprover/lean4 -L 1 | cut -f1)"}

while read -r REPO; do
  DIR="$TESTBED/repos/$REPO"
  echo "info: building $REPO on $TOOLCHAIN in $DIR" >&2
  if ./build-one.sh $REPO "$DIR" $TOOLCHAIN >&2; then
    echo $REPO
  fi
done < "$REPO_FILE"
