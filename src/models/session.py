"""Entidades Session e Round (T007), conforme specs/001-socratic-tutor-cli/data-model.md."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class SessionStatus(str, Enum):
    ACTIVE = "active"
    SUCCESS = "success"
    LIMIT_REACHED = "limit_reached"


class Stage(str, Enum):
    NOT_UNDERSTOOD = "not_understood"
    SYNTAX_ERROR = "syntax_error"
    LOGIC_ERROR = "logic_error"
    CONCEPTUAL_BLOCK = "conceptual_block"


@dataclass
class ExecutionResult:
    """Resultado de rodar os testes automatizados do exercício (não é um teste do pytest)."""

    passed: bool
    failed_tests: List[str] = field(default_factory=list)
    raw_output: str = ""


@dataclass
class Round:
    round_number: int
    student_code: str
    test_result: Optional[ExecutionResult]
    stage: Optional[Stage]
    prompt_sent: str
    model_response_raw: str
    guard_rejected: bool
    regeneration_attempts: int
    question_shown: str
    used_fallback: bool
    timestamp: str


@dataclass
class Session:
    exercise_statement: str
    has_tests: bool = False
    test_command: Optional[str] = None
    hint_limit: int = 5
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hints_used: int = 0
    status: SessionStatus = SessionStatus.ACTIVE
    rounds: List[Round] = field(default_factory=list)

    def is_terminal(self) -> bool:
        return self.status is not SessionStatus.ACTIVE
