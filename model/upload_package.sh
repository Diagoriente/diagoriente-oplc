#!/usr/bin/env bash
set -euo pipefail

pipenv install build
pipenv install twine
pipenv run python3 -m build
pipenv run python3 -m twine upload --repository testpypi --skip-existing dist/*
