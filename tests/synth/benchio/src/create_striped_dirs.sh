#!/bin/sh
set -e
staged_dir=$(pwd)
mkdir -p ${WRITE_DIR}
cd ${WRITE_DIR}

mkdir -p  striped
mkdir -p unstriped
mkdir -p fullstriped

lfs setstripe -c 1 unstriped
lfs setstripe -c -1 fullstriped
lfs setstripe -c 4 striped