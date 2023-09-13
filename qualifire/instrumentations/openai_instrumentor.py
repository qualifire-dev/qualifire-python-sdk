import json
import logging
import urllib.parse

import openai
import requests
from wrapt import wrap_function_wrapper

from .base_instrumentor import BaseInstrumentor

logger = logging.getLogger("qualifire")


class OpenAiInstrumentor(BaseInstrumentor):
    WRAPPED_METHODS = [
        {
            "func": openai.ChatCompletion.create,
            "object": "ChatCompletion",
            "method": "create",
            "span_name": "openai.chat",
        },
        {
            "func": openai.Completion.create,
            "object": "Completion",
            "method": "create",
            "span_name": "openai.completion",
        },
    ]

    def __init__(
        self,
        base_url: str,
        api_key: str,
    ):
        self._base_url = base_url
        self._api_key = api_key

    def _wrap(self, func, instance, args, kwargs):
        if hasattr(func, "__wrapped__"):
            return func(*args, **kwargs)

        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "X-qualifire-key": self._api_key,
        }

        q_response = requests.post(
            urllib.parse.urljoin(self._base_url, "/api/intake"),
            data=json.dumps(
                {
                    "caller": f"{instance.__name__}.{func.__name__}",
                    "body": kwargs,
                }
            ),
            headers=headers,
        )

        response = func(*args, **kwargs)

        if q_response.json()["success"]:
            requests.patch(
                urllib.parse.urljoin(self._base_url, "/api/intake"),
                data=json.dumps(
                    {
                        "createdCallId": q_response.json()["id"],
                        "model": kwargs["model"],
                        "body": response,
                    },
                ),
                headers=headers,
            )
        return response

    def initialize(
        self,
    ):
        for wrapped_method in self.WRAPPED_METHODS:
            wrap_object = wrapped_method.get("object")
            wrap_method = wrapped_method.get("method")
            logger.debug(
                "patching function",
                {
                    "wrap_method": wrap_method,
                },
            )
            wrap_function_wrapper(
                "openai",
                f"{wrap_object}.{wrap_method}",
                self._wrap,
            )
