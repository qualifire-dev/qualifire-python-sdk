from typing import Union

import json
import logging

import requests

from .instrumentations import instrumentors
from .types import EvaluationResponse, Input, Output

logger = logging.getLogger("qualifire")


class Client:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://gateway.qualifire.ai",
        version: str = None,
    ) -> None:
        self._base_url = base_url
        self._api_key = api_key
        self._version = version

    def initialize(self):
        for instrumentor_class in instrumentors:
            logger.debug(
                "initializing instrumentor",
                {
                    "instrumentor": instrumentor_class.__name__,
                },
            )
            try:
                instrumentor = instrumentor_class(
                    api_key=self._api_key,
                    base_url=self._base_url,
                    version=self._version,
                )

                instrumentor.initialize()
            except Exception:
                logger.exception("error while initializing instrumentor.")

        logger.debug("initialized all instrumentors")

    def evaluate(
        self,
        input: Union[str, Input],
        output: Union[str, Output],
        block: bool = True,
    ) -> Union[EvaluationResponse, None]:

        url = f"{self._base_url}/api/evaluation/v1"
        body = json.dumps({"async": block, "input": input, "output": output})
        headers = {
            "Content-Type": "application/json",
            "X-qualifire-key": self._api_key,
        }

        if block:
            requests.post(url, headers=headers, data=body)
            return None
        else:
            response = requests.post(url, headers=headers, data=body)

            if response.status_code != 200:
                raise Exception(f"Qualifire API error: {response.text}")

            jsonResponse = response.json()
            return EvaluationResponse(**jsonResponse)
