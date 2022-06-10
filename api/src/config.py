import os

def getenv_checked(env_name: str) -> str:
    env = os.getenv(env_name)
    if env is None:
        raise ValueError(f"Environment variable {env_name} must be defined.")
    else:
        return env

CORS_ALLOWED_ORIGINS = getenv_checked("CORS_ALLOWED_ORIGINS").split()
API_ROOT_PATH = getenv_checked("API_ROOT_PATH") or "/"
DEFAULT_DATA_SET = "Base de données proto orientation par les compétences"



