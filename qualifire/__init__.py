"""Qualifire Python SDK"""

import logging

from . import client, consts, tracer_init, types, utils
from .tracer_init import init

logger = logging.getLogger("qualifire")


from importlib import metadata as importlib_metadata


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


version: str = get_version()

__all__ = [
    "client",
    "types",
    "init",
    "version",
]
