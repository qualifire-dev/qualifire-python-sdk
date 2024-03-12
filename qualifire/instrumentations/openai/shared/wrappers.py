import json
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
        if hasattr(instance, "__qwrapped__"):
            return await func(*args, **kwargs)
        else:
            setattr(instance, "__qwrapped__", True)

        try:
            q_response = self._logger.log_request(
                body=kwargs,
            )
        except Exception:
            logger.debug("qualifire error while logging request")
            q_response = {}

        response = await func(*args, **kwargs)

        json_response = (
            response.dict()
            if hasattr(response, "dict")
            else json.loads(
                json.dumps(response, default=lambda o: getattr(o, "__dict__", str(o)))
            )
        )

        try:
            if q_response.get("id"):
                self._logger.log_response(
                    id=q_response["id"],
                    model=json_response.get("model"),
                    body=json_response,
                )
        except Exception:
            logger.debug("error while patching")
        return response

    def wrap(self, func, instance, args, kwargs):
        if hasattr(instance, "__qwrapped__"):
            return func(*args, **kwargs)
        else:
            setattr(instance, "__qwrapped__", True)

        try:
            q_response = self._logger.log_request(
                body=kwargs,
            )
        except Exception:
            logger.debug("qualifire error while logging request")
            q_response = {}

        response = func(*args, **kwargs)

        json_response = (
            response.dict()
            if hasattr(response, "dict")
            else json.loads(
                json.dumps(response, default=lambda o: getattr(o, "__dict__", str(o)))
            )
        )

        try:
            if q_response.get("id"):
                self._logger.log_response(
                    id=q_response["id"],
                    model=json_response.get("model"),
                    body=json_response,
                )
        except Exception:
            logger.debug("qualifire error while patching")
        return response
