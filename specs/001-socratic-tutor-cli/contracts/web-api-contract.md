# Contract: Interface Web Local (User Story 5 / FR-015)

Camada de apresentação fina sobre os mesmos `services/`/`models/` da CLI — nenhuma regra de
negócio nova. Servida apenas em `localhost`, sem autenticação (constitution, Princípio V).

## `GET /`

Retorna a página com o formulário de início de sessão (enunciado, código, testes opcionais,
limite de dicas). Equivalente visual do `cli-contract.md#iniciar-uma-sessão`.

## `POST /session`

Cria uma sessão, mesmas regras e validações de `start` na CLI (FR-001, FR-016).

**Body (form ou JSON)**:
```json
{
  "statement": "string, obrigatório",
  "code": "string, obrigatório",
  "test_command": "string, opcional",
  "hint_limit": "int, opcional, padrão 5"
}
```

**Response**: `{"session_id": "...", "status": "active", "hints_used": 0, "hint_limit": 5, ...}`
ou erro 4xx com mensagem clara (mesmas condições de erro da CLI, sem chamada de IA em caso
de entrada inválida). `hints_used`/`hint_limit` são incluídos para a UI renderizar o
indicador de dicas sem precisar de uma chamada extra.

## `POST /session/<session_id>/round`

Envia uma nova rodada (código atualizado e/ou comando especial), equivalente ao loop
interativo da CLI.

**Body**:
```json
{
  "student_code": "string",
  "command": "done | quit | null"
}
```

**Response**: o `Round` resultante (estágio, se a guarda rejeitou, pergunta exibida), o
`status` atualizado da sessão, e `hints_used`/`hint_limit` — mesmo formato de dados que a
CLI grava no log (`contracts/log-schema.md`), apenas serializado como resposta HTTP em vez
de linha de log.

## Restrições explícitas

- Sem sessões persistidas entre reinícios do processo além do arquivo de log já gravado
  (sem banco de dados, Princípio V).
- Sem múltiplos usuários simultâneos previstos — uso individual local, para fins de
  demonstração/apresentação (comparação lado a lado com um assistente de IA genérico,
  SC-005).
- Sem HTTPS/autenticação — não deve ser exposta fora de `localhost`.
