#!/usr/bin/env bash
set -euo pipefail

MAX_RESULTS=${1:-1000}
QUERY="language:Lean stars:>1 sort:stars"
gh search repos $QUERY -L $MAX_RESULTS | cut -f1
