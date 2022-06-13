#!/usr/bin/env bash
set -euo pipefail

pipenv run uvicorn src.api:app --host $API_HOST --port $API_PORT $API_EXTRA_ARGS
