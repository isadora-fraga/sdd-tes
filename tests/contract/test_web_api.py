"""T033: contrato da interface web (contracts/web-api-contract.md)."""
import json

import pytest

from src.web.app import create_app


class FakeClient:
    def __init__(self, question="Isso funciona para uma lista vazia?", stage="logic_error"):
        self._question = question
        self._stage = stage

    def generate(self, prompt):
        return {
            "question": self._question,
            "stage": self._stage,
            "raw": json.dumps({"question": self._question, "stage": self._stage}),
        }


@pytest.fixture
def client(tmp_path, monkeypatch):
    from src.services import logger

    monkeypatch.setattr(logger, "DEFAULT_LOG_DIR", tmp_path / "logs")
    app = create_app(client=FakeClient())
    app.config["TESTING"] = True
    return app.test_client()


def test_index_returns_form_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"form" in response.data.lower() or b"<html" in response.data.lower()


def test_create_session_valid_payload(client):
    response = client.post(
        "/session",
        json={"statement": "Some uma lista.", "code": "def soma(nums):\n    return 0\n"},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "session_id" in data
    assert data["status"] == "active"


def test_create_session_invalid_code_is_rejected(client):
    response = client.post(
        "/session",
        json={"statement": "Some uma lista.", "code": "console.log('oi');"},
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_round_endpoint_returns_round_fields(client):
    created = client.post(
        "/session",
        json={"statement": "Some uma lista.", "code": "def soma(nums):\n    return 0\n"},
    ).get_json()

    response = client.post(
        f"/session/{created['session_id']}/round",
        json={"student_code": "def soma(nums):\n    return 0\n"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "question_shown" in data
    assert "guard_rejected" in data
    assert "stage" in data
