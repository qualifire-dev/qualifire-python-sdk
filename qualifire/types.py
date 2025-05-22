from typing import Any, Dict, List, Optional

from dataclasses import dataclass, field


@dataclass
class LLMTooLDefinition:
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
    available_tools: Optional[List[LLMTooLDefinition]] = None
    dangerous_content_check: bool = False
    hallucinations_check: bool = False
    harassment_check: bool = False
    hate_speech_check: bool = False
    pii_check: bool = False
    prompt_injections: bool = False
    sexual_content_check: bool = False
    grounding_check: bool = False
    instructions_following_check: bool = False
    syntax_checks: Optional[Dict[str, SyntaxCheckArgs]] = None
    assertions: Optional[List[str]] = field(default_factory=list)
    tool_selection_quality_check: bool = False


@dataclass
class EvaluationResult:
    claim: str
    confidence_score: int
    label: str
    name: str
    quote: str
    reason: str
    score: int


@dataclass
class EvaluationResultItem:
    results: List[EvaluationResult]
    type: str


@dataclass
class EvaluationResponse:
    evaluationResults: List[EvaluationResultItem]
    score: int
    status: str
