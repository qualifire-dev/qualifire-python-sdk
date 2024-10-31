from typing import List, Union

import json
import logging
from dataclasses import asdict

import requests

from .instrumentations import instrumentors
from .types import EvaluationRequest, EvaluationResponse

logger = logging.getLogger("qualifire")


class Client:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://proxy.qualifire.ai",
        version: str = None,
        debug: bool = False,
    ) -> None:
        self._base_url = base_url
        self._api_key = api_key
        self._version = version
        self._debug = debug

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
        input: str,
        output: str,
        assertions: List[str] = None,
        consistency_check: bool = False,
        dangerous_content_check: bool = False,
        hallucinations_check: bool = False,
        harassment_check: bool = False,
        hate_speech_check: bool = False,
        pii_check: bool = False,
        prompt_injections: bool = False,
        sexual_content_check: bool = False,
    ) -> Union[EvaluationResponse, None]:
        """
        Evaluates the given input and output pairs.

        :param assertions: A list of assertions to check.
        :param consistency_check: Whether to check for consistency.
        :param dangerous_content_check: Whether to check for dangerous content.
        :param hallucinations_check: Whether to check for hallucinations.
        :param harassment_check: Whether to check for harassment.
        :param hate_speech_check: Whether to check for hate speech.
        :param input: The input to evaluate.
        :param messages: The messages to evaluate.
        :param output: The output to evaluate.
        :param pii_check: Whether to check for personally identifiable information.
        :param prompt_injections: Whether to check for prompt injections.
        :param responseFunctionCalls: The response function calls to check.

        :return: An EvaluationResponse object.
        :raises Exception: If an error occurs during the evaluation.

        Example:

        ```python
        from qualifire import Qualifire

        qualifire = Qualifire(api_key="your_api_key")

        evaluation_response = qualifire.evaluate(
            assertions=["The output should be a list of integers."],
            consistency_check=True,
            dangerous_content_check=True,
            hallucinations_check=True,
            harassment_check=True,
            hate_speech_check=True,
            input="Write a list of integers.",
            output="[1, 2, 3]",
            pii_check=True,
            prompt_injections=True,
            responseFunctionCalls="Write a list of integers.",
            sexual_content_check=True,
        )
        """

        url = f"{self._base_url}/api/evaluation/evaluate"
        request = EvaluationRequest(
            assertions=assertions,
            consistency_check=consistency_check,
            dangerous_content_check=dangerous_content_check,
            hallucinations_check=hallucinations_check,
            harassment_check=harassment_check,
            hate_speech_check=hate_speech_check,
            input=input,
            output=output,
            pii_check=pii_check,
            prompt_injections=prompt_injections,
            sexual_content_check=sexual_content_check,
        )

        body = json.dumps(asdict(request))
        headers = {
            "Content-Type": "application/json",
            "X-Qualifire-API-Key": self._api_key,
        }

        response = requests.post(url, headers=headers, data=body)

        if response.status_code != 200:
            raise Exception(f"Qualifire API error: {response.text}")

        jsonResponse = response.json()
        return EvaluationResponse(**jsonResponse)

    def invoke_evaluation(
        self,
        input: str,
        output: str,
        evaluation_id: str,
    ):

        url = f"{self._base_url}/api/evaluation/invoke/"

        payload = {
            "evaluation_id": evaluation_id,
            "input": input,
            "output": output,
        }
        headers = {
            "X-Qualifire-API-Key": self._api_key,
            "Content-Type": "application/json",
        }

        response = requests.request("POST", url, json=payload, headers=headers)
        if response.status_code != 200:
            if self._debug:
                response.raise_for_status()
            raise Exception(f"Qualifire API error: {response.text}")

        jsonResponse = response.json()
        return EvaluationResponse(**jsonResponse)
