"""T012: validação de sintaxe Python antes de qualquer chamada de IA (FR-016)."""
import pytest

from src.services.validators import InvalidCodeError, validate_python_syntax


def test_valid_python_is_accepted():
    validate_python_syntax("def soma(nums):\n    return sum(nums)\n")  # não deve levantar


def test_python_with_syntax_error_is_still_accepted():
    # Um erro de sintaxe em código Python é um estágio pedagógico legítimo
    # (stage=syntax_error), não uma entrada inválida — não deve ser rejeitado aqui.
    validate_python_syntax("def soma(nums)\n    return sum(nums)\n")


@pytest.mark.parametrize(
    "snippet",
    [
        "public class Main { public static void main(String[] args) {} }",
        "console.log('oi');",
        "#include <stdio.h>\nint main() { return 0; }",
    ],
)
def test_other_language_code_is_rejected(snippet):
    with pytest.raises(InvalidCodeError):
        validate_python_syntax(snippet)


def test_empty_code_is_rejected():
    with pytest.raises(InvalidCodeError):
        validate_python_syntax("   ")
