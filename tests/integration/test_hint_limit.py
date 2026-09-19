"""T026: encerramento por limite de dicas, sem chamadas adicionais à API (FR-009)."""
import json

import pytest

from src.models.session import SessionStatus
from src.services import session_service


class CountingFakeClient:
    def __init__(self, question="Isso funciona para todos os casos?", stage="logic_error"):
        self.call_count = 0
        self._question = question
        self._stage = stage

    def generate(self, prompt):
        self.call_count += 1
        return {
            "question": self._question,
            "stage": self._stage,
            "raw": json.dumps({"question": self._question, "stage": self._stage}),
        }


def test_session_ends_after_exactly_hint_limit_calls():
    session = session_service.start_session(
        exercise_statement="x", code="def f():\n    return 0\n", test_command=None, hint_limit=1
    )
    client = CountingFakeClient()

    round_ = session_service.process_round(session, "def f():\n    return 0\n", client)

    assert session.status == SessionStatus.LIMIT_REACHED
    assert session.hints_used == 1
    assert client.call_count == 1


def test_further_round_is_refused_locally_without_new_api_call():
    session = session_service.start_session(
        exercise_statement="x", code="def f():\n    return 0\n", test_command=None, hint_limit=1
    )
    client = CountingFakeClient()
    session_service.process_round(session, "def f():\n    return 0\n", client)
    assert client.call_count == 1

    with pytest.raises(session_service.SessionEndedError):
        session_service.process_round(session, "def f():\n    return 1\n", client)

    assert client.call_count == 1  # nenhuma chamada adicional (FR-009)
