import logging

from wrapt import wrap_function_wrapper

from ...base_instrumentor import BaseInstrumentor
from ..shared import OpenAIWrappers, QualifireLogger

logger = logging.getLogger("qualifire")


class OpenAiInstrumentorV1(BaseInstrumentor):
    WRAPPED_METHODS = [
        {
            "object": "openai.resources.chat.completions",
            "method": "Completions.create",
        },
        {
            "object": "openai.resources.completions",
            "method": "Completions.create",
        },
        {
            "object": "openai.resources.completions",
            "method": "AsyncCompletions.create",
            "async": True,
        },
        {
            "object": "openai.resources.chat.completions",
            "method": "AsyncCompletions.create",
            "async": True,
        },
    ]

    def __init__(
        self,
        base_url: str,
        api_key: str,
        version: str,
    ):
        self._version = version
        self._base_url = base_url
        self._api_key = api_key

        self._logger = QualifireLogger(
            base_url=base_url,
            api_key=api_key,
            version=version,
        )

        self._wrapper = OpenAIWrappers(
            base_url=base_url,
            api_key=api_key,
            version=version,
        )

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

            if not wrapped_method.get("async"):
                wrap_function_wrapper(
                    f"{wrap_object}",
                    f"{wrap_method}",
                    self._wrapper.wrap,
                )
            else:
                wrap_function_wrapper(
                    f"{wrap_object}",
                    f"{wrap_method}",
                    self._wrapper.wrap_async,
                )
