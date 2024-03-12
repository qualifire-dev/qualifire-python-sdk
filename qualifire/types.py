from typing import Dict, List, Optional

from dataclasses import dataclass, field


@dataclass
class Message:
    role: str
    content: Optional[str] = None


@dataclass
class Choice:
    index: int
    message: Message
    finish_reason: Optional[str] = None


@dataclass
class Usage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class Input:
    model: str
    messages: List[Message] = field(default_factory=list)
    caller: Optional[str] = None


@dataclass
class Output:
    id: str
    model: str
    choices: List[Choice] = field(default_factory=list)
    created: Optional[int] = None
    usage: Optional[Usage] = None
    system_fingerprint: Optional[str] = None


@dataclass
class Evaluation:
    async_: bool
    input: Input
    output: Output


@dataclass
class Result:
    claim: str
    contradiction: bool
    passed: bool
    matchScore: float
    reason: str
    quote: str
    includedInContent: bool
    monitorId: str
    createdAt: str
    organizationId: str
    callId: str


@dataclass
class EvaluationResult:
    type: str
    results: List[Result] = field(default_factory=list)


@dataclass
class ScoreBreakdownItem:
    length: int
    scoreSum: float


@dataclass
class EvaluationResponse:
    success: bool
    score: float
    status: str
    evaluationResults: List[EvaluationResult] = field(default_factory=list)
    scoreBreakdown: Dict[str, ScoreBreakdownItem] = field(default_factory=dict)
