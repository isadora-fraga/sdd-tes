"""Interface web local, sem login (User Story 5 / FR-015, contracts/web-api-contract.md).

Camada de apresentação fina: chama diretamente `session_service`, sem reimplementar
validação, guarda ou lógica de limite de dicas (mesma regra de negócio da CLI).
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from flask import Flask, abort, jsonify, render_template, request

from src.models.session import SessionStatus
from src.services import logger as logger_module
from src.services import session_service
from src.services.gemini_client import GeminiClient, GeminiCommunicationError
from src.services.validators import InvalidCodeError

# UUID gerado por uuid.uuid4() (Session.session_id) — usado para validar `session_id`
# vindo da URL antes de virar caminho de arquivo (evita path traversal em /logs/<id>).
_SESSION_ID_RE = re.compile(r"^[0-9a-fA-F-]{36}$")


def create_app(client: Optional[object] = None) -> Flask:
    app = Flask(__name__)
    app.config["GEMINI_CLIENT"] = client or GeminiClient()
    sessions: dict = {}

    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    @app.route("/session", methods=["POST"])
    def create_session():
        data = request.get_json(silent=True) or request.form
        try:
            session = session_service.start_session(
                exercise_statement=data.get("statement", ""),
                code=data.get("code", ""),
                test_command=data.get("test_command") or None,
                hint_limit=int(data.get("hint_limit", 5) or 5),
            )
        except (ValueError, InvalidCodeError) as exc:
            return jsonify({"error": str(exc)}), 400

        sessions[session.session_id] = session
        payload = {
            "session_id": session.session_id,
            "status": session.status.value,
            "hints_used": session.hints_used,
            "hint_limit": session.hint_limit,
        }
        if session.status == SessionStatus.SUCCESS:
            payload["message"] = "Os testes já passam! Sessão concluída com sucesso."
        return jsonify(payload), 201

    @app.route("/session/<session_id>/round", methods=["POST"])
    def round_endpoint(session_id):
        session = sessions.get(session_id)
        if session is None:
            return jsonify({"error": "Sessão não encontrada."}), 404

        data = request.get_json(silent=True) or request.form
        command = data.get("command")

        if command == "done":
            session_service.confirm_done(session)
            return jsonify(
                {
                    "status": session.status.value,
                    "hints_used": session.hints_used,
                    "hint_limit": session.hint_limit,
                }
            )
        if command == "quit":
            return jsonify(
                {
                    "status": session.status.value,
                    "message": "Sessão encerrada manualmente.",
                    "hints_used": session.hints_used,
                    "hint_limit": session.hint_limit,
                }
            )

        student_code = data.get("student_code", "")
        try:
            round_ = session_service.process_round(session, student_code, app.config["GEMINI_CLIENT"])
        except GeminiCommunicationError as exc:
            return jsonify({"error": str(exc)}), 502
        except InvalidCodeError as exc:
            return jsonify({"error": str(exc)}), 400
        except session_service.SessionEndedError as exc:
            return jsonify({"error": str(exc)}), 409

        return jsonify(
            {
                "round_number": round_.round_number,
                "stage": round_.stage.value if round_.stage else None,
                "guard_rejected": round_.guard_rejected,
                "used_fallback": round_.used_fallback,
                "question_shown": round_.question_shown,
                "status": session.status.value,
                "hints_used": session.hints_used,
                "hint_limit": session.hint_limit,
            }
        )

    @app.route("/logs", methods=["GET"])
    def logs_list():
        log_dir = Path(logger_module.DEFAULT_LOG_DIR)
        entries = []
        if log_dir.is_dir():
            for path in sorted(log_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True):
                rounds = _read_jsonl(path)
                last = rounds[-1] if rounds else None
                entries.append(
                    {
                        "session_id": path.stem,
                        "round_count": len(rounds),
                        "status": last.get("session_status_after") if last else "—",
                        "modified": datetime.fromtimestamp(path.stat().st_mtime).strftime(
                            "%d/%m/%Y %H:%M"
                        ),
                    }
                )
        return render_template("logs_list.html", entries=entries)

    @app.route("/logs/<session_id>", methods=["GET"])
    def logs_detail(session_id):
        if not _SESSION_ID_RE.match(session_id):
            abort(400, "ID de sessão inválido.")
        path = Path(logger_module.DEFAULT_LOG_DIR) / f"{session_id}.jsonl"
        if not path.is_file():
            abort(404, "Log de sessão não encontrado.")
        rounds = _read_jsonl(path)
        return render_template("logs_detail.html", session_id=session_id, rounds=rounds)

    return app


def _read_jsonl(path: Path) -> list:
    rounds = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rounds.append(json.loads(line))
    return rounds


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
