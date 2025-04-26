"""Qualifire PYthon SDK"""

import logging
import os

import pkg_resources

from . import client, types

logger = logging.getLogger("qualifire")
QUALIFIRE_API_KEY_ENV_VAR = "QUALIFIRE_API_KEY"
QUALIFIRE_BASE_URL_ENV_VAR = "QUALIFIRE_BASE_URL"
_DEFAULT_BASE_URL = "https://proxy.qualifire.ai/"


from importlib import metadata as importlib_metadata


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


version: str = get_version()
