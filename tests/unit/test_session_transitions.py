"""T006: máquina de estados de Session, conforme data-model.md."""
import pytest

from src.models.session import Session, SessionStatus


def test_terminal_states_are_final():
    session = Session(exercise_statement="x")
    assert not session.is_terminal()

    session.status = SessionStatus.SUCCESS
    assert session.is_terminal()

    session.status = SessionStatus.LIMIT_REACHED
    assert session.is_terminal()


def test_active_is_not_terminal():
    session = Session(exercise_statement="x")
    assert session.status == SessionStatus.ACTIVE
    assert session.is_terminal() is False
