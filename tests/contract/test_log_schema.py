"""T029: contrato do schema de log (contracts/log-schema.md)."""
import json

from src.services import session_service
from src.services.validators import InvalidCodeError

EXPECTED_KEYS = {
    "session_id", "round_number", "timestamp", "stage", "hints_used", "hint_limit",
    "test_result", "prompt_sent", "model_response_raw", "guard_rejected",
    "regeneration_attempts", "used_fallback", "question_shown", "session_status_after",
}


class FakeClient:
    def generate(self, prompt):
        return {"question": "Isso cobre o caso de lista vazia?", "stage": "logic_error", "raw": "{}"}


def test_log_line_matches_schema(tmp_path, monkeypatch):
    from src.services import logger

    monkeypatch.setattr(logger, "DEFAULT_LOG_DIR", tmp_path / "logs")

    session = session_service.start_session(
        exercise_statement="x", code="def f():\n    return 0\n", test_command=None, hint_limit=5
    )
    session_service.process_round(session, "def f():\n    return 0\n", FakeClient())

    log_file = (tmp_path / "logs") / f"{session.session_id}.jsonl"
    lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1

    entry = json.loads(lines[0])
    assert set(entry.keys()) == EXPECTED_KEYS
    assert entry["test_result"] is None  # sem testes automatizados nesta sessão


def test_rejected_input_before_any_ai_call_produces_no_log_line(tmp_path, monkeypatch):
    from src.services import logger

    monkeypatch.setattr(logger, "DEFAULT_LOG_DIR", tmp_path / "logs")

    session = session_service.start_session(
        exercise_statement="x", code="def f():\n    return 0\n", test_command=None, hint_limit=5
    )

    try:
        session_service.process_round(session, "console.log('oi');", FakeClient())
    except InvalidCodeError:
        pass

    assert not (tmp_path / "logs").exists()
