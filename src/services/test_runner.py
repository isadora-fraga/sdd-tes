"""Execução local dos testes do exercício via subprocess (FR-002).

Decisão de research.md item 1: subprocess + pytest local, sem sandbox remoto, sem
Google Colab, sem a ferramenta de code execution da API Gemini.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional, Union

from src.models.session import ExecutionResult

_TIMEOUT_SECONDS = 30


def run_tests(
    test_command: Optional[str], cwd: Optional[Union[str, Path]] = None
) -> Optional[ExecutionResult]:
    """Roda os testes do exercício. Retorna None quando não há testes (has_tests=false)."""
    if not test_command:
        return None

    result = subprocess.run(
        ["pytest", str(test_command), "-q", "--tb=short"],
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=_TIMEOUT_SECONDS,
    )

    passed = result.returncode == 0
    failed_tests = []
    if not passed:
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("FAILED "):
                failed_tests.append(line[len("FAILED "):].split(" ")[0])

    return ExecutionResult(
        passed=passed, failed_tests=failed_tests, raw_output=result.stdout + result.stderr
    )
