#!/usr/bin/env bash

set -euo pipefail

latest_release=$(ssh ovh-vps-test "find Diagoriente-Oplc/releases/ -mindepth 1 -maxdepth 1 -print0 | xargs -0 ls -dt | head -n 1")

echo "Run latest release $latest_release"

ssh ovh-vps-test "cd $latest_release; set -a; . .version; set +a; docker-compose up --no-build -d"
