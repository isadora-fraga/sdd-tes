"""T010: contrato de request/response da API Gemini (contracts/gemini-contract.md)."""
import json

import pytest

from src.services.gemini_client import GeminiClient, GeminiCommunicationError
from src.services.guard import check_response


def _client_returning(raw_text: str) -> GeminiClient:
    client = GeminiClient(api_key="fake-key-for-tests")
    client._call_model = lambda prompt: raw_text  # bypass da chamada real de rede
    return client


def test_valid_response_is_accepted_and_passes_guard():
    raw = json.dumps({"question": "O que sua função retorna para uma lista vazia?", "stage": "logic_error"})
    client = _client_returning(raw)

    result = client.generate("prompt qualquer")

    assert result["question"].endswith("?")
    assert result["stage"] == "logic_error"
    assert check_response(result["question"]) is True


def test_response_with_leaked_solution_is_parsed_but_rejected_by_guard():
    leaked_question = "Aqui está:\n```python\ndef soma(nums):\n    return sum(nums)\n```"
    raw = json.dumps({"question": leaked_question, "stage": "logic_error"})
    client = _client_returning(raw)

    result = client.generate("prompt qualquer")

    # o gemini_client não filtra conteúdo — isso é responsabilidade da guarda (FR-005)
    assert result["question"] == leaked_question
    assert check_response(result["question"]) is False


def test_missing_required_field_raises_communication_error():
    raw = json.dumps({"stage": "logic_error"})  # falta "question"
    client = _client_returning(raw)

    with pytest.raises(GeminiCommunicationError):
        client.generate("prompt qualquer")


def test_invalid_stage_enum_raises_communication_error():
    raw = json.dumps({"question": "Isso funciona?", "stage": "estagio_invalido"})
    client = _client_returning(raw)

    with pytest.raises(GeminiCommunicationError):
        client.generate("prompt qualquer")


def test_malformed_json_raises_communication_error():
    client = _client_returning("isto não é json")

    with pytest.raises(GeminiCommunicationError):
        client.generate("prompt qualquer")


def test_network_failure_raises_communication_error():
    client = GeminiClient(api_key="fake-key-for-tests")

    def _boom(prompt):
        raise RuntimeError("timeout simulado")

    client._call_model = _boom

    with pytest.raises(GeminiCommunicationError):
        client.generate("prompt qualquer")


def _server_error(code=503):
    from google.genai import errors as genai_errors

    return genai_errors.ServerError(
        code, {"error": {"code": code, "message": "sobrecarregado", "status": "UNAVAILABLE"}}
    )


def test_server_error_is_retried_automatically_then_succeeds(monkeypatch):
    import src.services.gemini_client as gemini_client_module

    monkeypatch.setattr(gemini_client_module.time, "sleep", lambda _: None)  # não espera de verdade

    client = GeminiClient(api_key="fake-key-for-tests")
    calls = {"n": 0}

    def _flaky(prompt):
        calls["n"] += 1
        if calls["n"] < 2:
            raise _server_error()
        return json.dumps({"question": "Funciona para o caso vazio?", "stage": "logic_error"})

    client._call_model = _flaky

    result = client.generate("prompt qualquer")

    assert calls["n"] == 2  # 1 falha (503) + 1 sucesso na retentativa automática
    assert result["question"].endswith("?")


def test_server_error_gives_up_after_max_retries(monkeypatch):
    import src.services.gemini_client as gemini_client_module

    monkeypatch.setattr(gemini_client_module.time, "sleep", lambda _: None)

    client = GeminiClient(api_key="fake-key-for-tests")
    calls = {"n": 0}

    def _always_503(prompt):
        calls["n"] += 1
        raise _server_error()

    client._call_model = _always_503

    with pytest.raises(GeminiCommunicationError):
        client.generate("prompt qualquer")

    assert calls["n"] == gemini_client_module.MAX_SERVER_ERROR_RETRIES + 1  # 1 tentativa + N retries


def test_client_error_is_not_retried(monkeypatch):
    from google.genai import errors as genai_errors
    import src.services.gemini_client as gemini_client_module

    monkeypatch.setattr(gemini_client_module.time, "sleep", lambda _: None)

    client = GeminiClient(api_key="fake-key-for-tests")
    calls = {"n": 0}

    def _bad_key(prompt):
        calls["n"] += 1
        raise genai_errors.ClientError(401, {"error": {"code": 401, "message": "chave inválida"}})

    client._call_model = _bad_key

    with pytest.raises(GeminiCommunicationError):
        client.generate("prompt qualquer")

    assert calls["n"] == 1  # erro de cliente não é transitório — sem retry automático
