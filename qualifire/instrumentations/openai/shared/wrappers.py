import logging

from . import QualifireLogger

logger = logging.getLogger("qualifire")


class OpenAIWrappers:
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

    async def wrap_async(self, func, instance, args, kwargs):
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

    def wrap(self, func, instance, args, kwargs):
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
