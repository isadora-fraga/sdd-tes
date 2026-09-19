"""CLI interativa (contracts/cli-contract.md)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from src.models.session import SessionStatus
from src.services import session_service
from src.services.gemini_client import GeminiClient, GeminiCommunicationError
from src.services.validators import InvalidCodeError


def _read_text_or_path(value: str) -> str:
    """FR-001: aceita tanto texto literal quanto um caminho de arquivo local."""
    path = Path(value)
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return value


def _print_round(round_) -> None:
    stage = round_.stage.value if round_.stage else "-"
    print(f"\n[{stage}] {round_.question_shown}\n")


def cmd_start(args: argparse.Namespace, client: Optional[object] = None, input_fn=input) -> int:
    try:
        statement = _read_text_or_path(args.statement)
        code = _read_text_or_path(args.code)
        session = session_service.start_session(
            exercise_statement=statement,
            code=code,
            test_command=args.tests,
            hint_limit=args.hint_limit,
        )
    except (ValueError, InvalidCodeError) as exc:
        print(f"Erro: {exc}")
        return 2

    if session.status == SessionStatus.SUCCESS:
        print("Os testes já passam! Sessão concluída com sucesso.")
        return 0

    if client is None:
        client = GeminiClient()

    current_code = code

    while session.status == SessionStatus.ACTIVE:
        try:
            round_ = session_service.process_round(session, current_code, client)
        except GeminiCommunicationError as exc:
            # FR-012: falha de comunicação não trava a sessão nem consome dica. Exige
            # confirmação explícita antes de tentar de novo, para não martelar a API em
            # loop apertado durante uma indisponibilidade temporária (ex.: erro 503).
            print(f"Erro ao comunicar com a IA: {exc}")
            choice = input_fn("Tentar novamente? (Enter para tentar, /quit para sair): ").strip()
            if choice == "/quit":
                print("Sessão encerrada manualmente.")
                return 1
            continue
        except InvalidCodeError as exc:
            print(f"Erro: {exc}")
            continue

        _print_round(round_)

        if session.status != SessionStatus.ACTIVE:
            break

        user_input = input_fn("Sua resposta / código atualizado (ou /done, /quit): ").strip()
        if user_input == "/quit":
            print("Sessão encerrada manualmente.")
            return 1
        if user_input == "/done":
            session_service.confirm_done(session)
            continue
        if user_input:
            current_code = _read_text_or_path(user_input)
        # entrada vazia: reenvia o mesmo código (aluno só respondeu em texto)

    if session.status == SessionStatus.SUCCESS:
        print("Sessão concluída com sucesso!")
        return 0
    if session.status == SessionStatus.LIMIT_REACHED:
        print(f"Limite de {session.hint_limit} dicas atingido para esta sessão. Encerrando.")
        return 1
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tutor-socratico")
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start", help="Inicia uma sessão de tutoria socrática")
    start.add_argument("--statement", required=True, help="Enunciado (texto ou caminho de arquivo)")
    start.add_argument("--code", required=True, help="Código do aluno (texto ou caminho de arquivo)")
    start.add_argument("--tests", default=None, help="Caminho do arquivo de testes pytest (opcional)")
    start.add_argument("--hint-limit", type=int, default=5, help="Limite de dicas (padrão: 5)")

    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "start":
        sys.exit(cmd_start(args))


if __name__ == "__main__":
    main()
