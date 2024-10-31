from typing import List

from dataclasses import dataclass


@dataclass
class LLMMessage:
    content: str
    role: str


@dataclass
class EvaluationRequest:
    input: str
    output: str
    consistency_check: bool
    dangerous_content_check: bool
    hallucinations_check: bool
    harassment_check: bool
    hate_speech_check: bool
    pii_check: bool
    prompt_injections: bool
    sexual_content_check: bool
    messages: List[LLMMessage] = None
    assertions: List[str] = None


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
