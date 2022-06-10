#!/usr/bin/env bash
set -euo pipefail

pipenv run uvicorn src.api:app --reload
