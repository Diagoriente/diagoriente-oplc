import os

from pathlib import Path

def getenv_checked(env_name: str) -> str:
    env = os.getenv(env_name)
    if env is None:
        raise ValueError(f"Environment variable {env_name} must be defined.")
    else:
        return env

CORS_ALLOWED_ORIGINS = getenv_checked("CORS_ALLOWED_ORIGINS").split()
API_ROOT_PATH = getenv_checked("API_ROOT_PATH") or "/"
DATASET_CACHE_DIR = Path("/tmp/diagoriente-oplc/cache/data_set/")
DEFAULT_DATA_SET = "google docs test spreadsheet"

LOCAL_DATASETS = {
    "local test csv": { "path": "data/test_data.csv" }
}
GOOGLE_DOCS_DATASETS = {
    "google docs test spreadsheet": {
        "key": "1MBasVlYC8Hqki0gU77qd7iVsr6ijfb5a9wZbX36I3_0",
        "gid": "2034486293"
    }
}
