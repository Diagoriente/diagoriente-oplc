#!/usr/bin/env bash
set -euo pipefail

pipenv run streamlit run main.py --server.address $STREAMLIT_HOST --server.port $STREAMLIT_PORT --server.baseUrlPath $STREAMLIT_SERVER_BASE_URL_PATH
