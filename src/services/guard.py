"""Guarda anti-solução (Princípio I, NON-NEGOTIABLE / FR-005).

Verificação programática — não apenas uma instrução de prompt — aplicada a toda resposta
do modelo antes de ser exibida ao aluno. Ver research.md, item 3.
"""
import re

_CODE_FENCE_RE = re.compile(r"```(?:\w+)?\n?(.*?)```", re.DOTALL)
_FUNCTION_OR_CLASS_RE = re.compile(r"\b(def |class )\w+")

_IMPERATIVE_PATTERNS = (
    r"\ba resposta é\b",
    r"\bbasta (copiar|colar|usar|trocar)\b",
    r"\btroque a linha\b",
    r"\bsubstitua .* por\b",
    r"\baqui está (a solução|o código)\b",
    r"\bcopie e cole\b",
    r"\bo código correto é\b",
)
_IMPERATIVE_RE = re.compile("|".join(_IMPERATIVE_PATTERNS), re.IGNORECASE)


def check_response(question: str) -> bool:
    """Retorna True se `question` é aceitável para exibir ao aluno (não vaza solução)."""
    if not question or not question.strip():
        return False

    for fenced_block in _CODE_FENCE_RE.findall(question):
        block = fenced_block.strip()
        if _FUNCTION_OR_CLASS_RE.search(block):
            return False
        if len(block.splitlines()) > 2:
            return False

    if _IMPERATIVE_RE.search(question):
        return False

    if "?" not in question:
        return False

    return True
