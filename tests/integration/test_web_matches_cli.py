"""T034: a web reproduz exatamente o comportamento da CLI para a mesma entrada (FR-015)."""
import json

from src.web.app import create_app


class LeakingClient:
    """Mesmo cenário do Scenario 2 da US1 (tests/integration/test_single_round_flow.py)."""

    def __init__(self):
        self._leaked = (
            "Aqui está:\n```python\ndef soma(nums):\n    return sum(nums)\n```"
        )

    def generate(self, prompt):
        return {
            "question": self._leaked,
            "stage": "logic_error",
            "raw": json.dumps({"question": self._leaked, "stage": "logic_error"}),
        }


def test_web_blocks_leaked_solution_same_as_cli(tmp_path, monkeypatch):
    from src.services import logger

    monkeypatch.setattr(logger, "DEFAULT_LOG_DIR", tmp_path / "logs")

    app = create_app(client=LeakingClient())
    app.config["TESTING"] = True
    web_client = app.test_client()

    created = web_client.post(
        "/session",
        json={"statement": "Some os números de uma lista.", "code": "def soma(nums):\n    return 0\n"},
    ).get_json()

    response = web_client.post(
        f"/session/{created['session_id']}/round",
        json={"student_code": "def soma(nums):\n    return 0\n"},
    )
    data = response.get_json()

    # mesmo resultado que test_leaked_solution_is_blocked_and_fallback_is_shown (US1, CLI/service)
    assert data["guard_rejected"] is True
    assert data["used_fallback"] is True
    assert "def " not in data["question_shown"]
