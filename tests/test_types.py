import pytest

from qualifire.types import EvaluationRequest, LLMMessage, LLMToolDefinition

_test_llm_messages = [
    LLMMessage(
        role="user",
        content="test",
    ),
]

_test_available_tools = [
    LLMToolDefinition(
        name="foo",
        description="foo tool function definition",
        parameters={
            "type": "object",
            "properties": {
                "bar": {
                    "type": "string",
                },
                "baz": {
                    "type": "integer",
                },
            },
            "required": ["bar", "baz"],
        },
    )
]


class TestEvaluationRequest:
    @pytest.mark.parametrize(
        "messages,input_,output,expected_error",
        [
            (None, None, None, True),
            ([], None, None, True),
            (None, "", None, True),
            (None, None, "", True),
            (_test_llm_messages, None, None, False),
            (_test_llm_messages, "", None, False),
            (_test_llm_messages, None, "", False),
            (_test_llm_messages, "", "", False),
            (None, "input", None, False),
            (None, "input", "", False),
            ([], "input", None, False),
            ([], "input", "", False),
            (None, None, "output", False),
            (None, "", "output", False),
            ([], None, "output", False),
            ([], "", "output", False),
            (_test_llm_messages, "input", None, False),
            (_test_llm_messages, "input", "", False),
            (_test_llm_messages, None, "output", False),
            (_test_llm_messages, "", "output", False),
            (None, "input", "output", False),
            ([], "input", "output", False),
            (_test_llm_messages, "input", "output", False),
        ],
    )
    def test_validate_messages_input_output(
        self,
        messages,
        input_,
        output,
        expected_error,
    ):
        if expected_error:
            with pytest.raises(ValueError):
                EvaluationRequest(
                    messages=messages,
                    input=input_,
                    output=output,
                )

    @pytest.mark.parametrize(
        "tsq_check,messages,available_tools,expected_error",
        [
            (True, None, None, True),
            (True, [], None, True),
            (True, None, [], True),
            (True, [], [], True),
            (True, _test_llm_messages, None, True),
            (True, _test_llm_messages, [], True),
            (True, None, _test_available_tools, True),
            (True, [], _test_available_tools, True),
            (True, _test_llm_messages, _test_available_tools, False),
            (False, None, None, False),
            (False, [], None, False),
            (False, None, [], False),
            (False, [], [], False),
            (False, _test_llm_messages, None, False),
            (False, _test_llm_messages, [], False),
            (False, None, _test_available_tools, False),
            (False, [], _test_available_tools, False),
            (False, _test_llm_messages, _test_available_tools, False),
        ],
    )
    def test_validate_tsq_requirements(
        self,
        tsq_check,
        messages,
        available_tools,
        expected_error,
    ):
        if expected_error:
            with pytest.raises(ValueError):
                EvaluationRequest(
                    messages=messages,
                    available_tools=available_tools,
                    tool_selection_quality_check=tsq_check,
                )
