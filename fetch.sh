#!/usr/bin/env bash
set -euo pipefail

MAX_QUERY=${1:-1000}
MAX_REPOS=${2:-100}
TESTBED=${3:-testbed}

mkdir -p $TESTBED
./query.sh $MAX_QUERY > $TESTBED/gh-repos.txt
echo "info: found $(wc -l < $TESTBED/gh-repos.txt) (max $MAX_QUERY) notable Lean repositories" >&2
./filter-lake.sh $TESTBED/gh-repos.txt > $TESTBED/lake-repos.txt
echo "info: found $(wc -l < $TESTBED/lake-repos.txt) notable Lean repositories with lakefiles" >&2
./curate.sh $TESTBED/lake-repos.txt $MAX_REPOS > $TESTBED/test-repos.txt
