"""T030: log de uma sessão multi-rodada é reprocessável linha a linha."""
import json

from src.services import logger, session_service


class FakeClient:
    def __init__(self, stages):
        self._stages = list(stages)

    def generate(self, prompt):
        stage = self._stages.pop(0)
        question = f"Pergunta para o estágio {stage}?"
        return {"question": question, "stage": stage, "raw": json.dumps({"question": question, "stage": stage})}


def test_full_session_log_is_one_parseable_line_per_round(tmp_path, monkeypatch):
    monkeypatch.setattr(logger, "DEFAULT_LOG_DIR", tmp_path / "logs")

    session = session_service.start_session(
        exercise_statement="x", code="def f():\n    return 0\n", test_command=None, hint_limit=5
    )
    client = FakeClient(["syntax_error", "logic_error"])

    session_service.process_round(session, "def f():\n    return 0\n", client)
    session_service.process_round(session, "def f():\n    return 1\n", client)

    log_file = (tmp_path / "logs") / f"{session.session_id}.jsonl"
    lines = log_file.read_text(encoding="utf-8").strip().splitlines()

    assert len(lines) == 2
    parsed = [json.loads(line) for line in lines]
    assert [entry["round_number"] for entry in parsed] == [1, 2]
    assert [entry["stage"] for entry in parsed] == ["syntax_error", "logic_error"]
