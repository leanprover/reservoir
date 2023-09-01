#!/usr/bin/env bash
set -euxo pipefail

REPO=$1
DIR=$2
TOOLCHAIN=${3:-"leanprover/lean4:$(gh release list -R leanprover/lean4 -L 1 | cut -f1)"}

mkdir -p $DIR
rm -rf $DIR
git clone https://github.com/$REPO $DIR
cd $DIR
echo -n "$TOOLCHAIN" > lean-toolchain
lake update
lake exe cache get || true
lake build
