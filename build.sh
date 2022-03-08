#!/usr/bin/env bash

set -euo pipefail

export VERSION=$(./version.sh)

echo "VERSION=$VERSION" > .version
docker-compose build

