from typing import Any, Dict, List, Optional

from dataclasses import dataclass, field
from enum import Enum


class ModelMode(str, Enum):
    SPEED = "speed"
    BALANCED = "balanced"
    QUALITY = "quality"


class PolicyTarget(str, Enum):
    INPUT = "input"
    OUTPUT = "output"
    BOTH = "both"


@dataclass
class LLMToolDefinition:
    name: str
    description: str
    parameters: Dict[str, Any]


@dataclass
class LLMToolCall:
    name: str
    arguments: Dict[str, Any]
    id: Optional[str]


@dataclass
class LLMMessage:
    role: str
    content: str
    tool_calls: Optional[List[LLMToolCall]] = None


@dataclass
class SyntaxCheckArgs:
    args: str


@dataclass
class EvaluationRequest:
    input: Optional[str] = None
    output: Optional[str] = None
    messages: Optional[List[LLMMessage]] = field(default_factory=list)
    available_tools: Optional[List[LLMToolDefinition]] = None
    dangerous_content_check: bool = False  # Deprecated: use content_moderation_check
    hallucinations_check: bool = False
    harassment_check: bool = False  # Deprecated: use content_moderation_check
    hate_speech_check: bool = False  # Deprecated: use content_moderation_check
    pii_check: bool = False
    prompt_injections: bool = False
    sexual_content_check: bool = False  # Deprecated: use content_moderation_check
    grounding_check: bool = False
    instructions_following_check: bool = False
    syntax_checks: Optional[Dict[str, SyntaxCheckArgs]] = None
    assertions: Optional[List[str]] = field(default_factory=list)
    tool_selection_quality_check: bool = False
    content_moderation_check: bool = False
    tsq_mode: ModelMode = ModelMode.BALANCED
    consistency_mode: ModelMode = ModelMode.BALANCED
    assertions_mode: ModelMode = ModelMode.BALANCED
    grounding_mode: ModelMode = ModelMode.BALANCED
    hallucinations_mode: ModelMode = ModelMode.BALANCED
    grounding_multi_turn_mode: bool = False
    policy_multi_turn_mode: bool = False
    policy_target: PolicyTarget = PolicyTarget.BOTH

    def __post_init__(self):
        self._validate_messages_input_output()
        self._validate_tsq_requirements()
        self._handle_deprecated_content_checks()

    def _validate_messages_input_output(self):
        if not self.messages and not self.input and not self.output:
            raise ValueError(
                "At least one of messages, input, or output must be set",
            )

    def _validate_tsq_requirements(self):
        if self.tool_selection_quality_check and not self.messages:
            raise ValueError(
                "messages must be provided in conjunction "
                "with tool_selection_quality_check=True."
            )
        if self.tool_selection_quality_check and not self.available_tools:
            raise ValueError(
                "available_tools must be provided in conjunction "
                "with tool_selection_quality_check=True."
            )

    def _handle_deprecated_content_checks(self):
        """Auto-set content_moderation_check if deprecated fields are set."""
        if (
            self.dangerous_content_check
            or self.harassment_check
            or self.hate_speech_check
            or self.sexual_content_check
        ):
            self.content_moderation_check = True


@dataclass
class EvaluationInvokeRequest:
    evaluation_id: str
    input: Optional[str] = None
    output: Optional[str] = None
    messages: Optional[List[LLMMessage]] = None
    available_tools: Optional[List[LLMToolDefinition]] = None

    def __post_init__(self):
        self._validate_messages_input_output()

    def _validate_messages_input_output(self):
        if not self.messages and not self.input and not self.output:
            raise ValueError(
                "At least one of messages, input, or output must be set",
            )


@dataclass
class EvaluationResult:
    claim: str
    confidence_score: int
    label: str
    name: str
    quote: str
    reason: str
    score: int
    flagged: bool


@dataclass
class EvaluationResultItem:
    results: List[EvaluationResult]
    type: str


@dataclass
class EvaluationResponse:
    evaluationResults: List[EvaluationResultItem]
    score: int
    status: str
