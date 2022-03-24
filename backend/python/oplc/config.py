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
DEFAULT_DATA_SET = "Base de données proto orientation par les compétences"

EXPERIENCES_SKILLS_DATA_SOURCES = {
    "type": "google docs",
    "name": "Base de données proto orientation par les compétences - Expériences",
    "key": "1PCLOHAE0yXt_tghVlV44ZTt7ZzEUV-f3COrKEMbLamc",
    "gid": "0",
}

JOBS_SKILLS_DATA_SOURCES = {
    "type": "google docs",
    "name": "Base de données proto orientation par les compétences - Métiers",
    "key": "1PCLOHAE0yXt_tghVlV44ZTt7ZzEUV-f3COrKEMbLamc",
    "gid": "1032477800",
}



