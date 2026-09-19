"""T023: Acceptance Scenarios 1-2 da User Story 2 (progressão de estágio/dicas)."""
import json

from src.models.session import Stage
from src.services import session_service


class FakeGeminiClient:
    def __init__(self, responses):
        self._responses = list(responses)
        self.prompts_seen = []

    def generate(self, prompt):
        self.prompts_seen.append(prompt)
        return self._responses.pop(0)


def _ok(question, stage):
    return {"question": question, "stage": stage, "raw": json.dumps({"question": question, "stage": stage})}


def test_hints_used_increments_across_rounds():
    session = session_service.start_session(
        exercise_statement="Escreva uma função que soma uma lista.",
        code="def soma(nums):\n    return 0\n",
        test_command=None,
        hint_limit=5,
    )
    client = FakeGeminiClient(
        [
            _ok("O que sua função retorna hoje para uma lista não vazia?", "logic_error"),
            _ok("O que muda no seu código entre essa versão e a anterior?", "logic_error"),
        ]
    )

    round1 = session_service.process_round(session, "def soma(nums):\n    return 0\n", client)
    assert session.hints_used == 1
    assert round1.stage == Stage.LOGIC_ERROR

    round2 = session_service.process_round(session, "def soma(nums):\n    return 1\n", client)
    assert session.hints_used == 2
    assert round2.stage == Stage.LOGIC_ERROR
    assert len(session.rounds) == 2


def test_stage_changes_from_syntax_error_to_logic_error_between_rounds():
    session = session_service.start_session(
        exercise_statement="Escreva uma função que soma uma lista.",
        code="def soma(nums)\n    return 0\n",  # falta ':' -> syntax_error
        test_command=None,
        hint_limit=5,
    )
    client = FakeGeminiClient(
        [
            _ok("O que falta depois dos parênteses da definição da função?", "syntax_error"),
            _ok("O que sua função retorna para [1, 2, 3]?", "logic_error"),
        ]
    )

    round1 = session_service.process_round(session, "def soma(nums)\n    return 0\n", client)
    assert round1.stage == Stage.SYNTAX_ERROR

    round2 = session_service.process_round(session, "def soma(nums):\n    return 0\n", client)
    assert round2.stage == Stage.LOGIC_ERROR

    # o histórico de estágios da rodada anterior deve ter sido incluído no prompt da 2ª chamada
    assert "syntax_error" in client.prompts_seen[1]
