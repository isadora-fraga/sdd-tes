"""FR-016: validação sintática local (sem chamada de IA) antes de qualquer uso da API."""
import ast

_OTHER_LANGUAGE_MARKERS = (
    "public class",
    "public static void",
    "#include",
    "console.log",
    "System.out.println",
    "using namespace",
    "func main(",
    "package main",
)


class InvalidCodeError(ValueError):
    """Código vazio ou que não parece ser Python."""


def validate_python_syntax(code: str) -> None:
    if code is None or not code.strip():
        raise InvalidCodeError("O código não pode estar vazio.")

    for marker in _OTHER_LANGUAGE_MARKERS:
        if marker in code:
            raise InvalidCodeError(
                f"O código parece não estar em Python (encontrado padrão '{marker}'). "
                "Este tutor só suporta exercícios em Python nesta versão."
            )

    try:
        ast.parse(code)
    except SyntaxError:
        # Um erro de sintaxe em código que não bate com nenhum marcador de outra
        # linguagem é tratado como Python com um bug (stage=syntax_error) — uma
        # entrada legítima para o tutor ajudar, não uma entrada inválida.
        pass
