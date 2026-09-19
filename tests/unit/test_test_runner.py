"""T013: execução dos testes do exercício via subprocess (FR-002)."""
from pathlib import Path

from src.services.test_runner import run_tests


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_no_test_command_returns_none(tmp_path):
    assert run_tests(None, tmp_path) is None


def test_passing_code_is_reported_as_passed(tmp_path):
    _write(tmp_path, "solution.py", "def soma(nums):\n    return sum(nums)\n")
    test_file = _write(
        tmp_path,
        "test_solution.py",
        "from solution import soma\n\n" "def test_soma():\n    assert soma([1, 2, 3]) == 6\n",
    )

    result = run_tests(str(test_file), tmp_path)

    assert result is not None
    assert result.passed is True
    assert result.failed_tests == []


def test_failing_code_reports_failed_tests(tmp_path):
    _write(tmp_path, "solution.py", "def soma(nums):\n    return 0\n")
    test_file = _write(
        tmp_path,
        "test_solution.py",
        "from solution import soma\n\n" "def test_soma():\n    assert soma([1, 2, 3]) == 6\n",
    )

    result = run_tests(str(test_file), tmp_path)

    assert result is not None
    assert result.passed is False
    assert any("test_soma" in name for name in result.failed_tests)
