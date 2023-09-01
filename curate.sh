#!/usr/bin/env bash
set -euo pipefail

REPO_FILE=$1
MAX_REPOS=${2:-20}
grep -vxFf exclusions.txt $REPO_FILE | head -n $MAX_REPOS
