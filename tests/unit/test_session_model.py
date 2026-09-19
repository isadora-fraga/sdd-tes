"""T005: Session deve ter os campos e defaults descritos em data-model.md."""
from src.models.session import Session, SessionStatus


def test_session_defaults():
    session = Session(exercise_statement="Some soma de uma lista")

    assert session.exercise_statement == "Some soma de uma lista"
    assert session.has_tests is False
    assert session.test_command is None
    assert session.hint_limit == 5  # FR-008: padrão 5
    assert session.hints_used == 0
    assert session.status == SessionStatus.ACTIVE
    assert session.rounds == []
    assert isinstance(session.session_id, str) and session.session_id


def test_session_custom_hint_limit_and_tests():
    session = Session(
        exercise_statement="Enunciado",
        has_tests=True,
        test_command="tests/exercise_test.py",
        hint_limit=3,
    )
    assert session.has_tests is True
    assert session.test_command == "tests/exercise_test.py"
    assert session.hint_limit == 3
