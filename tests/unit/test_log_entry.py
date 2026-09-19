"""T008: LogEntry deve bater com contracts/log-schema.md."""
from src.models.log_entry import to_log_dict
from src.models.session import Round, Session, SessionStatus, Stage, ExecutionResult

EXPECTED_KEYS = {
    "session_id", "round_number", "timestamp", "stage", "hints_used", "hint_limit",
    "test_result", "prompt_sent", "model_response_raw", "guard_rejected",
    "regeneration_attempts", "used_fallback", "question_shown", "session_status_after",
}


def _make_round(**overrides):
    defaults = dict(
        round_number=1,
        student_code="def f(): pass",
        test_result=ExecutionResult(passed=False, failed_tests=["test_f"], raw_output="..."),
        stage=Stage.LOGIC_ERROR,
        prompt_sent="prompt",
        model_response_raw="{}",
        guard_rejected=False,
        regeneration_attempts=0,
        question_shown="O que sua função retorna hoje?",
        used_fallback=False,
        timestamp="2026-09-19T12:00:00+00:00",
    )
    defaults.update(overrides)
    return Round(**defaults)


def test_log_entry_has_all_expected_fields():
    session = Session(exercise_statement="x", hint_limit=5, hints_used=1)
    round_ = _make_round()

    entry = to_log_dict(session, round_)

    assert set(entry.keys()) == EXPECTED_KEYS
    assert entry["stage"] == "logic_error"
    assert entry["test_result"] == {"passed": False, "failed_tests": ["test_f"]}
    assert entry["session_status_after"] == SessionStatus.ACTIVE.value


def test_log_entry_test_result_is_null_without_tests():
    session = Session(exercise_statement="x", has_tests=False)
    round_ = _make_round(test_result=None, stage=None)

    entry = to_log_dict(session, round_)

    assert entry["test_result"] is None
    assert entry["stage"] is None
