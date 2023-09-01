#!/usr/bin/env bash
set -euo pipefail

TESTBED="${TESTBED:-testbed}"
REPO_FILE="${1:-"$TESTBED/test-repos.txt"}"
TOOLCHAIN=${2:-"leanprover/lean4:$(gh release list -R leanprover/lean4 -L 1 | cut -f1)"}

i=1
while read -r REPO; do
  DIR="$TESTBED/repos/$i"
  set +e
  echo "info: building $REPO on $TOOLCHAIN in $DIR" >&2
  ./build-one.sh $REPO "$DIR" $TOOLCHAIN >&2
  RC=$?
  set -e
  if [ $RC = 0 ]; then
    echo $REPO
  fi
  ((i++))
done < "$REPO_FILE"
