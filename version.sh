#!/usr/bin/env bash

set -euo pipefail

# If working directory is clean (no changes to be committed), make the version
# number from the last commit date and hash. Otherwise, use the string "dev"
if [ -z "$(git status --porcelain)" ]
then
    git log -n 1 --format=%cd-%h --date=format:%Y%m%d-%H%m%S
else
    echo "dev"
fi
