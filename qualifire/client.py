from typing import Any, Dict, List, Optional, Union

import json
import logging
from dataclasses import asdict

import requests

from .types import (
    EvaluationInvokeRequest,
    EvaluationRequest,
    EvaluationResponse,
    LLMMessage,
    LLMToolDefinition,
    ModelMode,
    PolicyTarget,
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
        verify: bool = True,
    ) -> None:
        self._base_url = base_url or get_base_url()
        self._api_key = api_key or get_api_key()
        self._version = version
        self._debug = debug
        self._verify = verify

    def evaluate(
        self,
        input: Optional[str] = None,
        output: Optional[str] = None,
        messages: Optional[List[LLMMessage]] = None,
        available_tools: Optional[List[LLMToolDefinition]] = None,
        assertions: Optional[List[str]] = None,
        dangerous_content_check: bool = False,  # Deprecated: use content_moderation_check  # noqa: E501
        grounding_check: bool = False,
        hallucinations_check: bool = False,
        harassment_check: bool = False,  # Deprecated: use content_moderation_check  # noqa: E501
        hate_speech_check: bool = False,  # Deprecated: use content_moderation_check  # noqa: E501
        instructions_following_check: bool = False,
        pii_check: bool = False,
        prompt_injections: bool = False,
        sexual_content_check: bool = False,  # Deprecated: use content_moderation_check
        syntax_checks: Optional[Dict[str, SyntaxCheckArgs]] = None,
        tool_selection_quality_check: bool = False,
        content_moderation_check: bool = False,
        tsq_mode: ModelMode = ModelMode.BALANCED,
        consistency_mode: ModelMode = ModelMode.BALANCED,
        assertions_mode: ModelMode = ModelMode.BALANCED,
        grounding_mode: ModelMode = ModelMode.BALANCED,
        hallucinations_mode: ModelMode = ModelMode.BALANCED,
        grounding_multi_turn_mode: bool = False,
        policy_multi_turn_mode: bool = False,
        policy_target: PolicyTarget = PolicyTarget.BOTH,
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
        :param dangerous_content_check: .. deprecated:: Use :param:`content_moderation_check` instead.
            Check for dangerous content generation.
        :param grounding_check: Check if the output is grounded in the provided
                                input/context.
        :param hallucinations_check: Check for factual inaccuracies or hallucinations.
        :param harassment_check: .. deprecated:: Use :param:`content_moderation_check` instead.
            Check for harassing content.
        :param hate_speech_check: .. deprecated:: Use :param:`content_moderation_check` instead.
            Check for hate speech.
        :param instructions_following_check: Check if the output follows instructions
                                             in the input/messages.
        :param pii_check: Check for personally identifiable information.
        :param prompt_injections: Check for attempts at prompt injection.
        :param sexual_content_check: .. deprecated:: Use :param:`content_moderation_check` instead.
            Check for sexually explicit content.
        :param syntax_checks: Dictionary defining syntax checks (e.g., JSON, SQL).
        :param tool_selection_quality_check: Check for tool selection quality.
            Only works when `available_tools` and `messages` are provided.
        :param content_moderation_check: Check for content moderation (dangerous content,
            harassment, hate speech, and sexual content).
        :param tsq_mode: Model mode for tool selection quality check (speed/balanced/quality).
        :param consistency_mode: Model mode for consistency check (speed/balanced/quality).
        :param assertions_mode: Model mode for assertions check (speed/balanced/quality).
        :param grounding_mode: Model mode for grounding check (speed/balanced/quality).
        :param hallucinations_mode: Model mode for hallucinations check (speed/balanced/quality).
        :param grounding_multi_turn_mode: Enable multi-turn mode for grounding check.
        :param policy_multi_turn_mode: Enable multi-turn mode for policy check.
        :param policy_target: Target for policy checks (input/output/both).

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
            content_moderation_check=content_moderation_check,
            tsq_mode=tsq_mode,
            consistency_mode=consistency_mode,
            assertions_mode=assertions_mode,
            grounding_mode=grounding_mode,
            hallucinations_mode=hallucinations_mode,
            grounding_multi_turn_mode=grounding_multi_turn_mode,
            policy_multi_turn_mode=policy_multi_turn_mode,
            policy_target=policy_target,
        )

        # Filter out None values before dumping to JSON
        body = json.dumps(asdict(request))
        headers = {
            "Content-Type": "application/json",
            "X-Qualifire-API-Key": self._api_key,
        }

        response = requests.post(url, headers=headers, data=body, verify=self._verify)

        if response.status_code != 200:
            message = f"Qualifire API error: {response.status_code}"
            if response.text:
                message += f" - {response.text}"
            raise Exception(message)

        json_response = response.json()
        return EvaluationResponse(**json_response)

    def invoke_evaluation(
        self,
        evaluation_id: str,
        input: Optional[str] = None,
        output: Optional[str] = None,
        messages: Union[
            Optional[List[LLMMessage]],
            Optional[List[Dict[str, Any]]],
        ] = None,
        available_tools: Optional[List[LLMToolDefinition]] = None,
    ) -> EvaluationResponse:
        url = f"{self._base_url}/api/evaluation/invoke/"

        if messages is not None:
            if isinstance(messages, list) and all(
                isinstance(message, dict) for message in messages
            ):
                messages = [LLMMessage(**message) for message in messages]  # type: ignore # noqa E501

        request = EvaluationInvokeRequest(
            evaluation_id=evaluation_id,
            input=input,
            output=output,
            messages=messages,  # type: ignore
            available_tools=available_tools,
        )

        body = json.dumps(asdict(request))
        headers = {
            "X-Qualifire-API-Key": self._api_key,
            "Content-Type": "application/json",
        }

        response = requests.request(
            "POST",
            url,
            data=body,
            headers=headers,
            verify=self._verify,
        )
        if response.status_code != 200:
            if self._debug:
                response.raise_for_status()
            message = f"Qualifire API error: {response.status_code}"
            if response.text:
                message += f" - {response.text}"
            raise Exception(message)

        json_response = response.json()
        return EvaluationResponse(**json_response)
