"""Integração com a API Gemini (contracts/gemini-contract.md).

Decisões de research.md item 2: SDK oficial `google-genai`, modelo "flash" (custo baixo,
Princípio II), saída estruturada em JSON (pergunta + estágio numa única chamada).
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from src.config import get_gemini_api_key
from src.models.session import ExecutionResult, Stage

VALID_STAGES = {stage.value for stage in Stage}

DEFAULT_MODEL = "gemini-flash-latest"

# Limite de caracteres do código enviado ao modelo — cost-conscious (Princípio II) e
# trata o Edge Case de código extremamente longo, sinalizando o truncamento ao aluno.
MAX_CODE_CHARS = 4000

RESPONSE_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "question": {"type": "string"},
        "stage": {"type": "string", "enum": sorted(VALID_STAGES)},
    },
    "required": ["question", "stage"],
}

SYSTEM_INSTRUCTION = (
    "Você é um tutor socrático de programação para alunos de CS1/CS2. "
    "NUNCA forneça a solução do exercício, código completo/executável, nem instruções "
    "diretas de implementação. Responda SEMPRE com uma única pergunta orientadora que "
    "ajude o aluno a raciocinar sobre o próprio erro. Quando o resultado dos testes "
    "automatizados não estiver disponível, ofereça uma avaliação qualitativa breve (sem "
    "revelar a solução) e oriente o aluno a verificar por conta própria (rodando o "
    "código). Classifique também o estágio pedagógico do aluno em exatamente um destes "
    "valores: not_understood, syntax_error, logic_error, conceptual_block. Responda "
    "SEMPRE em JSON com os campos 'question' e 'stage'."
)


class GeminiCommunicationError(Exception):
    """Falha de rede/timeout, ou resposta fora do schema esperado (FR-012)."""


def build_prompt(
    exercise_statement: str,
    student_code: str,
    test_result: Optional[ExecutionResult],
    stage_history: List[str],
    hints_used: int,
    hint_limit: int,
) -> str:
    code = student_code
    truncated = False
    if len(code) > MAX_CODE_CHARS:
        code = code[:MAX_CODE_CHARS]
        truncated = True

    parts = [
        f"Enunciado do exercício:\n{exercise_statement}",
        f"Código atual do aluno:\n```python\n{code}\n```",
    ]
    if truncated:
        parts.append("[Aviso: o código foi truncado por ser muito longo para esta chamada.]")

    if test_result is None:
        parts.append("Não há testes automatizados disponíveis para este exercício.")
    elif test_result.passed:
        parts.append("Resultado dos testes: todos passaram.")
    else:
        failed = ", ".join(test_result.failed_tests) or "não especificado"
        parts.append(f"Resultado dos testes: falhou. Testes que falharam: {failed}.")

    if stage_history:
        parts.append("Estágios das rodadas anteriores desta sessão: " + ", ".join(stage_history))

    parts.append(f"Dicas usadas até agora nesta sessão: {hints_used}/{hint_limit}.")
    return "\n\n".join(parts)


class GeminiClient:
    """Wrapper fino sobre o SDK `google-genai`. `_call_model` é isolado para permitir
    mocking direto nos testes (contracts/gemini-contract.md), sem depender de rede."""

    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        self._api_key = api_key or get_gemini_api_key()
        self.model = model
        self._sdk_client = None

    def _call_model(self, prompt: str) -> str:
        if self._sdk_client is None:
            from google import genai

            self._sdk_client = genai.Client(api_key=self._api_key)

        from google.genai import types

        response = self._sdk_client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=RESPONSE_JSON_SCHEMA,
            ),
        )
        return response.text

    def generate(self, prompt: str) -> Dict[str, Any]:
        try:
            raw_text = self._call_model(prompt)
        except Exception as exc:  # falha de rede/timeout/autenticação etc. (FR-012)
            raise GeminiCommunicationError(
                f"Falha ao comunicar com a API Gemini: {exc}"
            ) from exc

        try:
            data = json.loads(raw_text)
        except (json.JSONDecodeError, TypeError) as exc:
            raise GeminiCommunicationError(
                f"Resposta do modelo fora do formato esperado (JSON inválido): {exc}"
            ) from exc

        if not isinstance(data, dict) or "question" not in data or "stage" not in data:
            raise GeminiCommunicationError(
                "Resposta do modelo não contém os campos obrigatórios 'question'/'stage'."
            )

        if data["stage"] not in VALID_STAGES:
            raise GeminiCommunicationError(
                f"Estágio retornado fora do conjunto esperado: {data['stage']!r}"
            )

        return {"question": data["question"], "stage": data["stage"], "raw": raw_text}
