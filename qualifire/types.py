from typing import Any, Dict, List, Optional

from enum import Enum

from pydantic import BaseModel, model_validator


class ModelMode(str, Enum):
    SPEED = "speed"
    BALANCED = "balanced"
    QUALITY = "quality"


class PolicyTarget(str, Enum):
    INPUT = "input"
    OUTPUT = "output"
    BOTH = "both"


class LLMToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]


class LLMToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]
    id: Optional[str] = None


class LLMMessage(BaseModel):
    role: str
    content: str
    tool_calls: Optional[List[LLMToolCall]] = None


class SyntaxCheckArgs(BaseModel):
    args: str


class EvaluationRequest(BaseModel):
    input: Optional[str] = None
    output: Optional[str] = None
    messages: Optional[List[LLMMessage]] = None
    available_tools: Optional[List[LLMToolDefinition]] = None
    dangerous_content_check: bool = False  # Deprecated: use content_moderation_check
    hallucinations_check: bool = False
    harassment_check: bool = False  # Deprecated: use content_moderation_check
    hate_speech_check: bool = False  # Deprecated: use content_moderation_check
    pii_check: bool = False
    prompt_injections: bool = False
    sexual_content_check: bool = False  # Deprecated: use content_moderation_check
    grounding_check: bool = False
    syntax_checks: Optional[Dict[str, SyntaxCheckArgs]] = None
    assertions: Optional[List[str]] = None
    tool_selection_quality_check: bool = False  # Deprecated: use tool_use_quality_check
    tool_use_quality_check: bool = False
    content_moderation_check: bool = False
    tsq_mode: Optional[ModelMode] = None  # Deprecated: use tuq_mode
    tuq_mode: Optional[ModelMode] = None
    consistency_mode: ModelMode = ModelMode.BALANCED
    assertions_mode: ModelMode = ModelMode.BALANCED
    grounding_mode: ModelMode = ModelMode.BALANCED
    hallucinations_mode: ModelMode = ModelMode.BALANCED
    grounding_multi_turn_mode: bool = False
    policy_multi_turn_mode: bool = False
    policy_target: PolicyTarget = PolicyTarget.BOTH

    @model_validator(mode="after")
    def validate_model(self) -> "EvaluationRequest":
        """Validate the model after initialization."""
        self._validate_messages_input_output()
        self._validate_tsq_requirements()
        self._handle_deprecated_content_checks()
        return self

    def _validate_messages_input_output(self) -> None:
        if not self.messages and not self.input and not self.output:
            raise ValueError(
                "At least one of messages, input, or output must be set",
            )

    def _validate_tsq_requirements(self) -> None:
        if (
            self.tool_selection_quality_check or self.tool_use_quality_check
        ) and not self.messages:
            raise ValueError(
                "messages must be provided in conjunction "
                "with tool_use_quality_check=True.",
            )
        if (
            self.tool_selection_quality_check or self.tool_use_quality_check
        ) and not self.available_tools:
            raise ValueError(
                "available_tools must be provided in conjunction "
                "with tool_use_quality_check=True.",
            )

    def _handle_deprecated_content_checks(self) -> None:
        """Auto-set content_moderation_check if deprecated fields are set."""
        if (
            self.dangerous_content_check
            or self.harassment_check
            or self.hate_speech_check
            or self.sexual_content_check
        ):
            self.content_moderation_check = True


class EvaluationInvokeRequest(BaseModel):
    evaluation_id: str
    input: Optional[str] = None
    output: Optional[str] = None
    messages: Optional[List[LLMMessage]] = None
    available_tools: Optional[List[LLMToolDefinition]] = None

    @model_validator(mode="after")
    def validate_model(self) -> "EvaluationInvokeRequest":
        self._validate_messages_input_output()
        return self

    def _validate_messages_input_output(self) -> None:
        if not self.messages and not self.input and not self.output:
            raise ValueError(
                "At least one of messages, input, or output must be set",
            )


class EvaluationResult(BaseModel):
    claim: Optional[str] = None
    confidence_score: float
    label: str
    name: str
    quote: str
    reason: str
    score: int
    flagged: bool


class EvaluationResultItem(BaseModel):
    results: List[EvaluationResult]
    type: str


class EvaluationResponse(BaseModel):
    evaluationResults: List[EvaluationResultItem]
    score: int
    status: str


class ToolResponse(BaseModel):
    type: str
    function: LLMToolDefinition


class CompilePromptResponse(BaseModel):
    id: str
    name: str
    revision: int
    messages: List[LLMMessage]
    tools: List[ToolResponse]
    parameters: Dict[str, Any]
