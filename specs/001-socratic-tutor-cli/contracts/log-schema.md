# Contract: Schema do Log (JSON Lines)

Um arquivo por sessão (ex.: `logs/<session_id>.jsonl`), uma linha = um `LogEntry` = uma
`Round` (FR-011, Princípio IV da constitution). Escrita append-only.

## Schema de cada linha

```json
{
  "session_id": "string (UUID)",
  "round_number": "int",
  "timestamp": "string (ISO 8601)",
  "stage": "not_understood | syntax_error | logic_error | conceptual_block",
  "hints_used": "int",
  "hint_limit": "int",
  "test_result": {
    "passed": "bool",
    "failed_tests": ["string"]
  },
  "prompt_sent": "string",
  "model_response_raw": "string",
  "guard_rejected": "bool",
  "regeneration_attempts": "int",
  "used_fallback": "bool",
  "question_shown": "string",
  "session_status_after": "active | success | limit_reached"
}
```

`test_result` é `null` quando `Session.has_tests=false` (ver FR-014).

## Garantias

- Uma linha é escrita **por rodada concluída**, mesmo quando a guarda rejeita a resposta do
  modelo e um fallback é usado (`guard_rejected=true`, `used_fallback=true` nesse caso).
- Rodadas rejeitadas antes de qualquer chamada de IA (entrada vazia, código não-Python —
  FR-016) **não** geram uma linha de log, pois nenhuma chamada de API ocorreu e nenhuma
  dica foi consumida.
- O arquivo MUST permanecer válido (uma linha JSON completa por vez) mesmo se a sessão for
  interrompida abruptamente entre rodadas — cada linha é escrita e sincronizada em disco
  (`flush`) imediatamente após a rodada correspondente ser concluída.

## Reprocessamento (uso de pesquisa)

Qualquer ferramenta capaz de ler JSON Lines pode reprocessar o arquivo linha a linha sem
precisar carregar a sessão inteira em memória — cada linha é autocontida (inclui
`session_id`, `round_number`, `stage`, etc.), suportando análises como distribuição de
estágios por rodada, taxa de uso de fallback, ou número médio de dicas até o sucesso.
