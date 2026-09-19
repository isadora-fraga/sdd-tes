"""T011: heurísticas anti-solução (Princípio I / FR-005)."""
from src.services.guard import check_response


def test_plain_question_is_accepted():
    assert check_response("O que acontece com `total` na primeira iteração do laço?") is True


def test_response_with_full_function_is_rejected():
    leaked = (
        "Aqui está o código:\n"
        "```python\n"
        "def soma(nums):\n"
        "    total = 0\n"
        "    for n in nums:\n"
        "        total += n\n"
        "    return total\n"
        "```\n"
    )
    assert check_response(leaked) is False


def test_imperative_resolution_phrase_is_rejected():
    assert check_response("A resposta é trocar `+` por `+=` na linha 3.") is False
    assert check_response("Basta copiar este trecho para resolver.") is False


def test_response_without_question_mark_is_rejected():
    assert check_response("Sua função está quase certa.") is False


def test_empty_response_is_rejected():
    assert check_response("") is False
    assert check_response("   ") is False


def test_short_inline_code_snippet_in_question_is_still_accepted():
    # Um pequeno trecho inline (ex.: nome de variável) não é uma solução completa.
    assert check_response("O que `total` vale depois do primeiro `for`?") is True
