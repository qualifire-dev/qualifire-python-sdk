"""Qualifire PYthon SDK"""

import logging
import os

import pkg_resources

from . import client, types

logger = logging.getLogger("qualifire")
QUALIFIRE_API_KEY_ENV_VAR = "QUALIFIRE_API_KEY"
QUALIFIRE_BASE_URL_ENV_VAR = "QUALIFIRE_BASE_URL"
_DEFAULT_BASE_URL = "https://gateway.qualifire.ai/"


from importlib import metadata as importlib_metadata


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


version: str = get_version()


def init(
    api_key=None,
    debug=False,
    base_url=None,
):
    if api_key is None:
        api_key = os.environ.get(QUALIFIRE_API_KEY_ENV_VAR)
        if api_key is None:
            logger.warning(
                f"No API key found, please pass the api key to this function or set the environment variable: {QUALIFIRE_API_KEY_ENV_VAR}"
            )

    if debug is True:
        logger.setLevel("DEBUG")
    else:
        logger.setLevel("ERROR")

    if base_url is None:
        base_url = os.environ.get(QUALIFIRE_BASE_URL_ENV_VAR)

        if base_url is None:
            base_url = _DEFAULT_BASE_URL

    logger.debug(
        "initializing client",
        {
            "base_url": base_url,
        },
    )

    qualifire_client = client.Client(
        base_url=base_url,
        api_key=api_key,
        version=version,
    )

    try:
        qualifire_client.initialize()
    except Exception:
        logger.exception("Error while initializing")
