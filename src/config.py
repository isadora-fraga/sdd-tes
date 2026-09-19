"""Carregamento de configuração local (T003).

Usado tanto pela CLI quanto pela interface web (FR-015 — mesma lógica, sem duplicação).

Lê GEMINI_API_KEY do ambiente ou de um arquivo `.env` local (nunca de código-fonte ou de
argumento de linha de comando, para não deixar a chave visível em `ps`/histórico do shell).
"""
import os

from dotenv import load_dotenv

load_dotenv()  # lê .env na raiz do projeto, se existir; não sobrescreve variáveis já exportadas


class MissingApiKeyError(RuntimeError):
    pass


def get_gemini_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise MissingApiKeyError(
            "GEMINI_API_KEY não encontrada. Crie um arquivo .env na raiz do projeto "
            "(copie .env.example) com GEMINI_API_KEY=sua-chave, ou exporte a variável "
            "de ambiente antes de rodar (ver README.md)."
        )
    return key
