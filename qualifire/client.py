from typing import Dict, List, Optional, Union

import json
import logging
from dataclasses import asdict

import requests

from .types import (
    EvaluationRequest,
    EvaluationResponse,
    LLMMessage,
    LLMToolDefinition,
    SyntaxCheckArgs,
)
from .utils import get_api_key, get_base_url

logger = logging.getLogger("qualifire")


class Client:
    def __init__(
        self,
        api_key: Optional[str],
        base_url: Optional[str] = None,
        version: Optional[str] = None,
        debug: bool = False,
    ) -> None:
        self._base_url = base_url or get_base_url()
        self._api_key = api_key or get_api_key()
        self._version = version
        self._debug = debug

    def evaluate(
        self,
        input: Optional[str] = None,
        output: Optional[str] = None,
        messages: Optional[List[LLMMessage]] = None,
        available_tools: Optional[List[LLMToolDefinition]] = None,
        assertions: Optional[List[str]] = None,
        dangerous_content_check: bool = False,
        grounding_check: bool = False,
        hallucinations_check: bool = False,
        harassment_check: bool = False,
        hate_speech_check: bool = False,
        instructions_following_check: bool = False,
        pii_check: bool = False,
        prompt_injections: bool = False,
        sexual_content_check: bool = False,
        syntax_checks: Optional[Dict[str, SyntaxCheckArgs]] = None,
        tool_selection_quality_check: bool = False,
    ) -> Union[EvaluationResponse, None]:
        """
        Evaluates the given input and output pairs.

        :param input: The primary input for the evaluation.
        :param output: The primary output (e.g., LLM response) to evaluate.
        :param messages: List of message objects representing conversation history.
            Must be set if tool_selection_quality_check is True.
        :param available_tools: List of available tools.
            Must be set if tool_selection_quality_check is True.
        :param assertions: A list of custom assertions to check against the output.
        :param dangerous_content_check: Check for dangerous content generation.
        :param grounding_check: Check if the output is grounded in the provided
                                input/context.
        :param hallucinations_check: Check for factual inaccuracies or hallucinations.
        :param harassment_check: Check for harassing content.
        :param hate_speech_check: Check for hate speech.
        :param instructions_following_check: Check if the output follows instructions
                                             in the input/messages.
        :param pii_check: Check for personally identifiable information.
        :param prompt_injections: Check for attempts at prompt injection.
        :param sexual_content_check: Check for sexually explicit content.
        :param syntax_checks: Dictionary defining syntax checks (e.g., JSON, SQL).
        :param tool_selection_quality_check: Check for tool selection quality.
            Only works when `available_tools` and `messages` are provided.

        :return: An EvaluationResponse object containing the evaluation results.
        :raises Exception: If an error occurs during the evaluation.

        Example:

        ```python
        from qualifire import Qualifire
        from qualifire.types import LLMMessage, SyntaxCheckArgs

        qualifire = Qualifire(api_key="your_api_key")

        evaluation_response = qualifire.evaluate(
            input="Translate 'hello' to French and provide the result in JSON format.",
            output='{"translation": "bonjour"}',
            assertions=["The output must contain the key 'translation'"],
            dangerous_content_check=True,
            grounding_check=True,
            hallucinations_check=True,
            harassment_check=True,
            hate_speech_check=True,
            instructions_following_check=True,
            messages=[
                LLMMessage(
                    role="user",
                    content="Translate 'hello' to French and provide JSON."
                ),
                LLMMessage(role="assistant", content='{"translation": "bonjour"}')
            ],
            pii_check=True,
            prompt_injections=True,
            sexual_content_check=True,
            syntax_checks={
                "json": SyntaxCheckArgs(args="strict") # Example syntax check
            },
        )
        ```

        Example with tools:
        ```python
        from qualifire import Qualifire
        from qualifire.types import LLMMessage, LLMToolDefinition

        qualifire = Qualifire(api_key="your_api_key")

        evaluation_response = qualifire.evaluate(
            messages=[
                LLMMessage(
                    role="user",
                    content="What is the weather tomorrow in New York?",
                ),
                LLMMessage(
                    role="assistant",
                    content='please run the following tool'
                    tool_calls=[
                        LLMToolCall(
                           "id": "tool_call_id",
                            "name": "get_weather_forecast",
                            "arguments": {
                                "location": "New York, NY",
                                "date": "tomorrow",
                            },
                        ),
                    ],
                ),
            ],
            available_tools=[
                LLMToolDefinition(
                    name="get_weather_forecast",
                    description="Provides the weather forecast for a given location and date.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g., San Francisco, CA",
                            },
                            "date": {
                                "type": "string",
                                "description": "The date for the forecast, e.g., tomorrow, or YYYY-MM-DD",
                            },
                        },
                        "required": [
                            "location",
                            "date",
                        ],
                    },
                ),
            ],
            tool_selection_quality_check=True,
        )
        ```
        """  # noqa E501
        url = f"{self._base_url}/api/evaluation/evaluate"
        request = EvaluationRequest(
            input=input,
            output=output,
            messages=messages,
            available_tools=available_tools,
            assertions=assertions,
            dangerous_content_check=dangerous_content_check,
            grounding_check=grounding_check,
            hallucinations_check=hallucinations_check,
            harassment_check=harassment_check,
            hate_speech_check=hate_speech_check,
            instructions_following_check=instructions_following_check,
            pii_check=pii_check,
            prompt_injections=prompt_injections,
            sexual_content_check=sexual_content_check,
            syntax_checks=syntax_checks,
            tool_selection_quality_check=tool_selection_quality_check,
        )

        # Filter out None values before dumping to JSON
        body = json.dumps(asdict(request))
        headers = {
            "Content-Type": "application/json",
            "X-Qualifire-API-Key": self._api_key,
        }

        response = requests.post(url, headers=headers, data=body)

        if response.status_code != 200:
            raise Exception(f"Qualifire API error: {response.text}")

        json_response = response.json()
        return EvaluationResponse(**json_response)

    def invoke_evaluation(
        self,
        input: str,
        output: str,
        evaluation_id: str,
    ) -> EvaluationResponse:
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

        json_response = response.json()
        return EvaluationResponse(**json_response)
