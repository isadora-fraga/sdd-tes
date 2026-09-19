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
