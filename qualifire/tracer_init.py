import os
import sys
from typing import TypeVar, Callable, Optional, Any

from traceloop.sdk import Traceloop

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
    __suppress_prints(
        Traceloop.init,
        app_name="qualifire-agent",
        api_endpoint=f"{get_base_url()}/telemetry",  # /v1/traces is automatically added  # noqa: E501
        headers={"X-Qualifire-API-Key": api_key},
    )


def init(api_key: Optional[str] = None) -> None:
    api_key = api_key or get_api_key()
    __configure_tracer(api_key)
