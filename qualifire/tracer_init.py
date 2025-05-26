from typing import Any, Callable, Optional, TypeVar

import os
import sys

try:
    from traceloop.sdk import Traceloop

    traceloop_installed = True
except ImportError:
    traceloop_installed = False

from .utils import get_api_key, get_base_url

R = TypeVar("R")


def __suppress_prints(
    func: Callable[..., R],
    *args: Any,
    **kwargs: Any,
) -> R:
    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, "w")
    try:
        return func(*args, **kwargs)
    finally:
        sys.stdout.close()
        sys.stdout = original_stdout


def __configure_tracer(api_key: str) -> None:
    # traceloop uses env for those configs
    os.environ["TRACELOOP_METRICS_ENABLED"] = "false"
    os.environ["TRACELOOP_LOGGING_ENABLED"] = "false"

    __suppress_prints(
        Traceloop.init,
        app_name="qualifire-agent",
        api_endpoint=f"{get_base_url()}/api/telemetry",  # /v1/traces is automatically added  # noqa: E501
        headers={"X-Qualifire-API-Key": api_key},
        telemetry_enabled=False,
        traceloop_sync_enabled=False,
    )


def init(api_key: Optional[str] = None) -> None:
    if not traceloop_installed:
        if sys.version_info < (3, 10):
            raise RuntimeError("qualifire.init requires Python 3.10 or higher")
        else:
            raise RuntimeError("Dependency error, please reinstall qualifire-sdk")

    api_key = api_key or get_api_key()
    __configure_tracer(api_key)
