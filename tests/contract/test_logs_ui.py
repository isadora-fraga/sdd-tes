"""UI de visualização de logs (/logs, /logs/<session_id>) — sem regra de negócio nova,
só leitura dos arquivos já gerados por src/services/logger.py."""
import json

from src.services import logger, session_service
from src.web.app import create_app


class FakeClient:
    def generate(self, prompt):
        return {"question": "Isso cobre o caso de lista vazia?", "stage": "logic_error", "raw": "{}"}


def _client_with_one_session(tmp_path, monkeypatch):
    monkeypatch.setattr(logger, "DEFAULT_LOG_DIR", tmp_path / "logs")
    app = create_app(client=FakeClient())
    app.config["TESTING"] = True

    session = session_service.start_session(
        exercise_statement="x", code="def f():\n    return 0\n", test_command=None, hint_limit=5
    )
    session_service.process_round(session, "def f():\n    return 0\n", FakeClient())
    return app.test_client(), session.session_id


def test_logs_list_shows_registered_session(tmp_path, monkeypatch):
    client, session_id = _client_with_one_session(tmp_path, monkeypatch)

    response = client.get("/logs")

    assert response.status_code == 200
    assert session_id in response.get_data(as_text=True)


def test_logs_list_empty_state(tmp_path, monkeypatch):
    monkeypatch.setattr(logger, "DEFAULT_LOG_DIR", tmp_path / "logs")
    app = create_app(client=FakeClient())
    app.config["TESTING"] = True

    response = app.test_client().get("/logs")

    assert response.status_code == 200
    assert "Nenhuma sessão" in response.get_data(as_text=True)


def test_logs_detail_shows_round_data(tmp_path, monkeypatch):
    client, session_id = _client_with_one_session(tmp_path, monkeypatch)

    response = client.get(f"/logs/{session_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "logic_error" in html
    assert "Isso cobre o caso de lista vazia?" in html


def test_logs_detail_unknown_session_is_404(tmp_path, monkeypatch):
    client, _ = _client_with_one_session(tmp_path, monkeypatch)

    response = client.get("/logs/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404


def test_logs_detail_rejects_path_traversal(tmp_path, monkeypatch):
    client, _ = _client_with_one_session(tmp_path, monkeypatch)

    response = client.get("/logs/..%2F..%2F..%2Fetc%2Fpasswd")

    assert response.status_code in (400, 404)
