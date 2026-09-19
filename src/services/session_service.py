"""Orquestrador único da lógica de negócio da sessão (start_session/process_round).

Módulo introduzido durante o /speckit-tasks para que CLI e web (FR-015) chamem exatamente
a mesma lógica, sem duplicar regra de negócio. Ver plan.md, Project Structure.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Union

from src.models.session import ExecutionResult, Round, Session, SessionStatus, Stage
from src.services import guard, logger, test_runner, validators
from src.services.gemini_client import build_prompt
from src.services.validators import InvalidCodeError

MAX_TOTAL_ATTEMPTS_PER_ROUND = 2  # 1 tentativa inicial + no máximo 1 regeneração (Princípio II)

FALLBACK_QUESTIONS = (
    "O que você espera que essa parte do código faça, passo a passo, antes de rodar?",
    "Se você explicasse essa lógica em voz alta para alguém, onde a explicação travaria?",
)


class SessionEndedError(Exception):
    """Sessão já está em um estado terminal (success ou limit_reached) — FR-009/FR-010."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _pick_fallback(round_number: int) -> str:
    return FALLBACK_QUESTIONS[round_number % len(FALLBACK_QUESTIONS)]


def start_session(
    exercise_statement: str,
    code: str,
    test_command: Optional[str] = None,
    hint_limit: int = 5,
    cwd: Optional[Union[str, Path]] = None,
) -> Session:
    """FR-001: cria a sessão; FR-010: atalho de sucesso imediato quando os testes já passam."""
    if not exercise_statement or not exercise_statement.strip():
        raise InvalidCodeError("O enunciado do exercício não pode estar vazio.")

    validators.validate_python_syntax(code)

    session = Session(
        exercise_statement=exercise_statement,
        has_tests=bool(test_command),
        test_command=test_command,
        hint_limit=hint_limit,
    )
    session._cwd = cwd  # runtime-only, não faz parte do data-model.md documentado

    if session.has_tests:
        result = test_runner.run_tests(test_command, cwd)
        if result is not None and result.passed:
            session.status = SessionStatus.SUCCESS

    return session


def confirm_done(session: Session) -> None:
    """FR-014: encerramento manual do aluno quando não há testes automatizados."""
    if session.has_tests:
        return  # /done não tem efeito quando o encerramento por sucesso já é automático
    session.status = SessionStatus.SUCCESS


def process_round(session: Session, student_code: str, client) -> Round:
    if session.is_terminal():
        raise SessionEndedError(f"Sessão já encerrada (status={session.status.value}).")

    validators.validate_python_syntax(student_code)

    round_number = len(session.rounds) + 1
    cwd = getattr(session, "_cwd", None)
    test_result: Optional[ExecutionResult] = (
        test_runner.run_tests(session.test_command, cwd) if session.has_tests else None
    )

    if test_result is not None and test_result.passed:
        session.status = SessionStatus.SUCCESS
        round_ = Round(
            round_number=round_number,
            student_code=student_code,
            test_result=test_result,
            stage=None,
            prompt_sent="",
            model_response_raw="",
            guard_rejected=False,
            regeneration_attempts=0,
            question_shown="Parabéns, os testes passaram! Sessão concluída com sucesso.",
            used_fallback=False,
            timestamp=_now(),
        )
        session.rounds.append(round_)
        logger.append_round(session, round_)
        return round_

    stage_history: List[str] = [r.stage.value for r in session.rounds if r.stage]
    prompt = build_prompt(
        exercise_statement=session.exercise_statement,
        student_code=student_code,
        test_result=test_result,
        stage_history=stage_history,
        hints_used=session.hints_used,
        hint_limit=session.hint_limit,
    )

    attempts = 0
    question: Optional[str] = None
    stage_value: Optional[str] = None
    raw_response = ""
    guard_rejected_final = False
    used_fallback = False

    while True:
        if session.hints_used >= session.hint_limit:
            used_fallback = True
            question = _pick_fallback(round_number)
            session.status = SessionStatus.LIMIT_REACHED
            break

        result = client.generate(prompt)  # cada chamada aqui = 1 dica usada (FR-008)
        session.hints_used += 1
        attempts += 1
        raw_response = result["raw"]
        stage_value = result["stage"]

        if guard.check_response(result["question"]):
            question = result["question"]
            break

        guard_rejected_final = True
        if attempts >= MAX_TOTAL_ATTEMPTS_PER_ROUND:
            used_fallback = True
            question = _pick_fallback(round_number)
            break

    if session.status == SessionStatus.ACTIVE and session.hints_used >= session.hint_limit:
        session.status = SessionStatus.LIMIT_REACHED

    round_ = Round(
        round_number=round_number,
        student_code=student_code,
        test_result=test_result,
        stage=Stage(stage_value) if stage_value else None,
        prompt_sent=prompt,
        model_response_raw=raw_response,
        guard_rejected=guard_rejected_final,
        regeneration_attempts=max(attempts - 1, 0),
        question_shown=question,
        used_fallback=used_fallback,
        timestamp=_now(),
    )
    session.rounds.append(round_)
    logger.append_round(session, round_)
    return round_
