import os

from .consts import (
    _DEFAULT_BASE_URL,
    QUALIFIRE_API_KEY_ENV_VAR,
    QUALIFIRE_BASE_URL_ENV_VAR,
)


def get_api_key() -> str:
    api_key = os.getenv(QUALIFIRE_API_KEY_ENV_VAR)
    if not api_key:
        raise ValueError("Qualifire API Key not found")
    return api_key


def get_base_url() -> str:
    base_url = os.getenv(QUALIFIRE_BASE_URL_ENV_VAR)
    if not base_url:
        return _DEFAULT_BASE_URL
    return base_url
