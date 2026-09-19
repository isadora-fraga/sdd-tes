"""FR-012: falha de comunicação com a IA exige confirmação antes de tentar de novo
(não pode martelar a API em loop apertado durante uma indisponibilidade temporária)."""
from src.cli.main import build_parser, cmd_start
from src.services.gemini_client import GeminiCommunicationError


class FlakyThenOkClient:
    """Simula um erro 503 na primeira chamada, depois responde normalmente."""

    def __init__(self):
        self.calls = 0

    def generate(self, prompt):
        self.calls += 1
        if self.calls == 1:
            raise GeminiCommunicationError("503 UNAVAILABLE (simulado)")
        return {
            "question": "O que sua função retorna para uma lista vazia?",
            "stage": "logic_error",
            "raw": "{}",
        }


def test_communication_error_waits_for_confirmation_before_retry(tmp_path, monkeypatch):
    from src.services import logger

    monkeypatch.setattr(logger, "DEFAULT_LOG_DIR", tmp_path / "logs")

    parser = build_parser()
    args = parser.parse_args(
        ["start", "--statement", "Some uma lista.", "--code", "def soma(nums):\n    return 0\n"]
    )

    inputs = iter(["", "/quit"])  # Enter = tentar de novo; depois sai
    exit_code = cmd_start(args, client=FlakyThenOkClient(), input_fn=lambda _: next(inputs))

    assert exit_code == 1


def test_communication_error_can_be_quit_without_retrying():
    parser = build_parser()
    args = parser.parse_args(["start", "--statement", "x", "--code", "def f():\n    return 0\n"])

    class AlwaysFailsClient:
        def __init__(self):
            self.calls = 0

        def generate(self, prompt):
            self.calls += 1
            raise GeminiCommunicationError("503 UNAVAILABLE (simulado)")

    client = AlwaysFailsClient()
    exit_code = cmd_start(args, client=client, input_fn=lambda _: "/quit")

    assert exit_code == 1
    assert client.calls == 1  # não insiste sozinho depois do /quit
