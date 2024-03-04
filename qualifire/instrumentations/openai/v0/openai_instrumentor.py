import logging

from openai.api_resources import ChatCompletion, Completion
from wrapt import wrap_function_wrapper

from ...base_instrumentor import BaseInstrumentor
from ..shared import QualifireLogger

logger = logging.getLogger("qualifire")


class OpenAiInstrumentorV0(BaseInstrumentor):
    WRAPPED_METHODS = [
        {
            "func": ChatCompletion.create,
            "object": "ChatCompletion",
            "method": "create",
            "async": False,
        },
        {
            "func": Completion.create,
            "object": "Completion",
            "method": "create",
            "async": False,
        },
        {
            "func": ChatCompletion.acreate,
            "object": "ChatCompletion",
            "method": "acreate",
            "async": True,
        },
        {
            "func": Completion.acreate,
            "object": "Completion",
            "method": "acreate",
            "async": True,
        },
    ]

    def __init__(
        self,
        base_url: str,
        api_key: str,
        version: str,
    ):
        self._base_url = base_url
        self._api_key = api_key
        self._version = version
        self._logger = QualifireLogger(
            base_url=base_url,
            api_key=api_key,
            version=version,
        )

    async def _wrap_async(self, func, instance, args, kwargs):
        if hasattr(func, "__wrapped__"):
            return func(*args, **kwargs)

        try:
            q_response = self._logger.log_request(
                caller=f"{instance.__name__}.{func.__name__}",
                body=kwargs,
            )
        except Exception:
            q_response = {}

        response = await func(*args, **kwargs)

        try:
            if q_response.get("id"):
                self._logger.log_response(
                    id=q_response["id"],
                    model=response.get("model"),
                    body=response,
                )
        except Exception:
            logger.debug("error while patching")
        return response

    def _wrap(self, func, instance, args, kwargs):
        if hasattr(func, "__wrapped__"):
            return func(*args, **kwargs)

        try:
            q_response = self._logger.log_request(
                caller=f"{instance.__name__}.{func.__name__}",
                body=kwargs,
            )
        except Exception:
            logger.debug("qualifire error while logging request")
            q_response = {}

        response = func(*args, **kwargs)

        try:
            if q_response.get("id"):
                self._logger.log_response(
                    id=q_response["id"],
                    model=response.get("model"),
                    body=response,
                )
        except Exception:
            logger.debug("qualifire error while patching")
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

            if not wrapped_method.get("async"):
                wrap_function_wrapper(
                    "openai",
                    f"{wrap_object}.{wrap_method}",
                    self._wrap,
                )
            else:
                wrap_function_wrapper(
                    "openai",
                    f"{wrap_object}.{wrap_method}",
                    self._wrap_async,
                )
