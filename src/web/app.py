"""Interface web local, sem login (User Story 5 / FR-015, contracts/web-api-contract.md).

Camada de apresentação fina: chama diretamente `session_service`, sem reimplementar
validação, guarda ou lógica de limite de dicas (mesma regra de negócio da CLI).
"""
from __future__ import annotations

from typing import Optional

from flask import Flask, jsonify, render_template, request

from src.models.session import SessionStatus
from src.services import session_service
from src.services.gemini_client import GeminiClient, GeminiCommunicationError
from src.services.validators import InvalidCodeError


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

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
