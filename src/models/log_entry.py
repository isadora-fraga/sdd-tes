"""Serialização de Round para o schema de log (T009), conforme contracts/log-schema.md."""
from __future__ import annotations

from typing import Any, Dict

from src.models.session import Round, Session


def to_log_dict(session: Session, round_: Round) -> Dict[str, Any]:
    test_result = None
    if round_.test_result is not None:
        test_result = {
            "passed": round_.test_result.passed,
            "failed_tests": list(round_.test_result.failed_tests),
        }

    return {
        "session_id": session.session_id,
        "round_number": round_.round_number,
        "timestamp": round_.timestamp,
        "stage": round_.stage.value if round_.stage else None,
        "hints_used": session.hints_used,
        "hint_limit": session.hint_limit,
        "test_result": test_result,
        "prompt_sent": round_.prompt_sent,
        "model_response_raw": round_.model_response_raw,
        "guard_rejected": round_.guard_rejected,
        "regeneration_attempts": round_.regeneration_attempts,
        "used_fallback": round_.used_fallback,
        "question_shown": round_.question_shown,
        "session_status_after": session.status.value,
    }
