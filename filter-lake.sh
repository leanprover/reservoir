#!/usr/bin/env bash
set -euo pipefail

REPO_FILE="${1:-/dev/stdin}"
while read -r REPO; do
  URL=https://raw.githubusercontent.com/$REPO/HEAD/lakefile.lean
  echo "trace: querying $URL" >&2
  CODE=$(curl -I -L -s -o /dev/null -w "%{http_code}" $URL)
  if [ $CODE = 200 ]; then
    echo $REPO
  elif [ $CODE = 404 ]; then
    :
  else
    echo "warning: status $CODE for repository $REPO" >&2
  fi
done < "$REPO_FILE"
