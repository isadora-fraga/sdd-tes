"""T014: Acceptance Scenarios 1-4 da User Story 1 (spec.md), ponta a ponta."""
import json

import pytest

from src.models.session import SessionStatus
from src.services import session_service
from src.services.gemini_client import GeminiCommunicationError


class FakeGeminiClient:
    """Cliente Gemini falso, controlado pelo teste (sem rede)."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.call_count = 0

    def generate(self, prompt):
        self.call_count += 1
        item = self._responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def _ok(question, stage="logic_error"):
    return {"question": question, "stage": stage, "raw": json.dumps({"question": question, "stage": stage})}


# Scenario 1: rodada normal -> pergunta orientadora exibida, nunca a solução.
def test_normal_round_shows_question_not_solution():
    session = session_service.start_session(
        exercise_statement="Some os números de uma lista.",
        code="def soma(nums):\n    return 0\n",
        test_command=None,
        hint_limit=5,
    )
    client = FakeGeminiClient([_ok("O que sua função retorna para [1, 2, 3] hoje?")])

    round_ = session_service.process_round(session, session_service_code := "def soma(nums):\n    return 0\n", client)

    assert round_.guard_rejected is False
    assert round_.used_fallback is False
    assert "?" in round_.question_shown
    assert "def " not in round_.question_shown


# Scenario 2: resposta com solução vazada -> guarda bloqueia -> fallback exibido.
def test_leaked_solution_is_blocked_and_fallback_is_shown():
    leaked = "Aqui está:\n```python\ndef soma(nums):\n    return sum(nums)\n```"
    session = session_service.start_session(
        exercise_statement="Some os números de uma lista.",
        code="def soma(nums):\n    return 0\n",
        test_command=None,
        hint_limit=5,
    )
    client = FakeGeminiClient([_ok(leaked), _ok(leaked)])  # rejeitado nas duas tentativas

    round_ = session_service.process_round(session, "def soma(nums):\n    return 0\n", client)

    assert round_.guard_rejected is True
    assert round_.used_fallback is True
    assert "def " not in round_.question_shown
    assert client.call_count == 2  # 1 tentativa inicial + 1 regeneração, depois fallback


# Scenario 3: código já passa nos testes -> sucesso imediato, sem chamada ao Gemini.
def test_already_passing_code_succeeds_immediately(tmp_path):
    (tmp_path / "solution.py").write_text("def soma(nums):\n    return sum(nums)\n", encoding="utf-8")
    test_file = tmp_path / "test_solution.py"
    test_file.write_text(
        "from solution import soma\n\ndef test_soma():\n    assert soma([1, 2, 3]) == 6\n",
        encoding="utf-8",
    )

    session = session_service.start_session(
        exercise_statement="Some os números de uma lista.",
        code="def soma(nums):\n    return sum(nums)\n",
        test_command=str(test_file),
        hint_limit=5,
        cwd=tmp_path,
    )

    assert session.status == SessionStatus.SUCCESS
    assert session.hints_used == 0


# Scenario 4: sem testes -> avaliação qualitativa, sessão continua ativa até /done.
def test_no_tests_gives_qualitative_evaluation_and_waits_for_done():
    session = session_service.start_session(
        exercise_statement="Escreva uma função que inverte uma string.",
        code="def inverte(s):\n    return s[::-1]\n",
        test_command=None,
        hint_limit=5,
    )
    client = FakeGeminiClient([_ok("Isso parece consistente com o enunciado. Você já testou no interpretador?")])

    round_ = session_service.process_round(session, "def inverte(s):\n    return s[::-1]\n", client)

    assert session.status == SessionStatus.ACTIVE  # não encerra sozinho
    assert "?" in round_.question_shown

    session_service.confirm_done(session)
    assert session.status == SessionStatus.SUCCESS


def test_communication_error_propagates_without_consuming_hint():
    session = session_service.start_session(
        exercise_statement="x", code="def f():\n    pass\n", test_command=None, hint_limit=5
    )
    client = FakeGeminiClient([GeminiCommunicationError("timeout")])

    with pytest.raises(GeminiCommunicationError):
        session_service.process_round(session, "def f():\n    pass\n", client)

    assert session.hints_used == 0
