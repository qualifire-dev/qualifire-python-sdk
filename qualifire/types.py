from typing import Dict, List, Optional

from dataclasses import dataclass, field


@dataclass
class LLMMessage:
    content: str
    role: str


@dataclass
class SyntaxCheckArgs:
    args: str


@dataclass
class EvaluationRequest:
    input: str
    output: str
    dangerous_content_check: bool
    hallucinations_check: bool
    harassment_check: bool
    hate_speech_check: bool
    pii_check: bool
    prompt_injections: bool
    sexual_content_check: bool
    grounding_check: bool = False
    instructions_following_check: bool = False
    syntax_checks: Optional[Dict[str, SyntaxCheckArgs]] = None
    messages: Optional[List[LLMMessage]] = field(default_factory=list)
    assertions: Optional[List[str]] = field(default_factory=list)


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
