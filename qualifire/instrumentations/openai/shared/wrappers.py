import types

import json
import logging
from importlib.metadata import version

import openai

from ....instrumentations import is_openai_v1
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

    @staticmethod
    def is_streaming_response(response):
        if is_openai_v1():
            return isinstance(response, openai.Stream) or isinstance(
                response, openai.AsyncStream
            )

        return isinstance(response, types.GeneratorType) or isinstance(
            response, types.AsyncGeneratorType
        )

    @staticmethod
    def model_as_dict(model):
        if version("pydantic") < "2.0.0":
            return model.dict()
        if hasattr(model, "model_dump"):
            return model.model_dump()
        elif hasattr(model, "parse"):  # Raw API response
            return OpenAIWrappers.model_as_dict(model.parse())
        else:
            return model

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

        if self.is_streaming_response(response):
            return self._async_build_from_streaming_response(
                id=q_response.get("id"),
                response=response,
            )
        else:
            json_response = (
                response.dict()
                if hasattr(response, "dict")
                else json.loads(
                    json.dumps(
                        response, default=lambda o: getattr(o, "__dict__", str(o))
                    )
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

        if self.is_streaming_response(response):
            return self._build_from_streaming_response(
                id=q_response.get("id"),
                response=response,
            )
        else:
            json_response = (
                response.dict()
                if hasattr(response, "dict")
                else json.loads(
                    json.dumps(
                        response, default=lambda o: getattr(o, "__dict__", str(o))
                    )
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

    def _build_from_streaming_response(self, response, id):
        complete_response = {"choices": [], "model": ""}
        for item in response:
            item_to_yield = item
            self._accumulate_stream_items(item, complete_response)

            yield item_to_yield
        try:
            self._logger.log_response(
                id=id,
                model=complete_response.get("model"),
                body=complete_response,
            )
        except Exception:
            logger.debug("qualifire error while logging response")

    async def _async_build_from_streaming_response(self, response, id):
        complete_response = {"choices": [], "model": ""}
        async for item in response:
            item_to_yield = item
            self._accumulate_stream_items(item, complete_response)

            yield item_to_yield
        try:
            self._logger.log_response(
                id=id,
                model=complete_response.get("model"),
                body=complete_response,
            )
        except Exception:
            logger.debug("qualifire error while logging response")

    def _accumulate_stream_items(self, item, complete_response):
        if is_openai_v1():
            item = self.model_as_dict(item)

        complete_response["model"] = item.get("model")

        for choice in item.get("choices"):
            index = choice.get("index")
            if len(complete_response.get("choices")) <= index:
                complete_response["choices"].append(
                    {"index": index, "message": {"content": "", "role": ""}}
                )
            complete_choice = complete_response.get("choices")[index]
            if choice.get("finish_reason"):
                complete_choice["finish_reason"] = choice.get("finish_reason")

            delta = choice.get("delta")

            if delta.get("content"):
                complete_choice["message"]["content"] += delta.get("content")
            if delta.get("role"):
                complete_choice["message"]["role"] = delta.get("role")
