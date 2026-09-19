# Contract: Chamada à API Gemini

Define o formato de entrada e saída usado em cada chamada ao modelo, para que
`gemini_client.py` e a bateria de contract tests concordem sobre o schema.

## Pré-condições

- O código já passou pela validação sintática local (FR-016) antes de chegar aqui.
- `hints_used < hint_limit` (a chamada nunca acontece após o limite ser atingido — FR-009).

## Request (montado pelo sistema)

Campos incluídos no prompt (não é um schema de API externo, é o conteúdo que o sistema
concatena/formata para o modelo):

| Campo | Origem | Obrigatório |
|---|---|---|
| `exercise_statement` | `Session.exercise_statement` | sim |
| `student_code` | `Round.student_code` (rodada atual) | sim |
| `test_result` | `Round.test_result` (`null` se `has_tests=false`) | não |
| `stage_history` | lista resumida dos `stage` das rodadas anteriores desta sessão (não o texto completo do histórico de prompts/respostas — Princípio II) | não |
| `hints_used` / `hint_limit` | `Session.hints_used`, `Session.hint_limit` | sim |

O prompt de sistema instrui o modelo a: nunca produzir código-solução completo ou
instruções diretas de resolução; produzir exatamente uma pergunta orientadora; e, quando
`test_result` for `null`, produzir uma avaliação qualitativa (conforme FR-014) em vez de uma
pergunta convencional.

## Response (exigida do modelo via saída estruturada/JSON mode)

```json
{
  "type": "object",
  "required": ["question", "stage"],
  "properties": {
    "question": {
      "type": "string",
      "description": "Pergunta orientadora (ou avaliação qualitativa, no caso do FR-014). Nunca deve conter código-solução."
    },
    "stage": {
      "type": "string",
      "enum": ["not_understood", "syntax_error", "logic_error", "conceptual_block"]
    }
  }
}
```

## Pós-condições / contrato de uso

1. Toda `response.question` MUST passar pela guarda (`guard.py`) antes de virar
   `Round.question_shown`. Ver `contracts/log-schema.md` para como o resultado da guarda é
   registrado.
2. Se a chamada falhar (erro de rede, timeout, resposta fora do schema esperado), o sistema
   MUST tratar como falha de comunicação (FR-012): informar o aluno, não travar a sessão, e
   NÃO incrementar `hints_used` para uma chamada que não completou com sucesso.
3. Cada chamada bem-sucedida (mesmo que a guarda rejeite `question`) conta como 1 uso do
   limite de dicas (`hints_used += 1`), incluindo tentativas de regeneração dentro da mesma
   rodada (research.md, item 3) — isso é o que garante o teto de custo do Princípio II.

## Casos de teste de contrato sugeridos (`tests/contract/`)

- Resposta válida, dentro do schema, sem código → aceita, `guard_rejected=false`.
- Resposta com bloco de código completo dentro de `question` → guarda rejeita,
  `guard_rejected=true`, sistema tenta regenerar.
- Resposta fora do schema JSON esperado (campo faltando, tipo errado) → tratado como falha
  de comunicação (FR-012), não como rejeição de guarda.
- `stage` fora do enum esperado → tratado como falha de comunicação (FR-012).
