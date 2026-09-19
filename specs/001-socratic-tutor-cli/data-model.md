# Data Model: Tutor Socrático de Programação (CLI)

Deriva das entidades já identificadas em `spec.md` (seção Key Entities), detalhadas aqui
com campos, tipos e regras de validação/transição para orientar `/speckit-tasks` e a
implementação.

## Session

Representa uma tentativa do aluno de resolver um exercício específico, do início ao
encerramento.

| Campo | Tipo | Descrição | Regras |
|---|---|---|---|
| `session_id` | string (UUID) | identificador único da sessão | gerado na criação |
| `exercise_statement` | string | enunciado do exercício | obrigatório, não vazio (Edge Case) |
| `has_tests` | bool | se há testes automatizados associados | derivado de `test_command` presente |
| `test_command` | string \| null | comando para rodar os testes (ex.: caminho do arquivo pytest) | obrigatório se `has_tests=true` |
| `hint_limit` | int | limite máximo de dicas/chamadas de IA para esta sessão | configurável via CLI; padrão 5 (FR-008) |
| `hints_used` | int | contagem de dicas já entregues | inicia em 0; incrementa a cada `Round` com chamada de IA |
| `status` | enum: `active` \| `success` \| `limit_reached` | estado corrente da sessão | ver Transições abaixo |
| `rounds` | lista de `Round` | histórico de rodadas desta sessão | ordenado por `timestamp` |

**Transições de estado** (`status`):

```text
active --(testes passam)--------------------> success
active --(sem testes; aluno confirma /done)--> success
active --(hints_used == hint_limit)----------> limit_reached
active --(nova rodada, ainda sem resolver)---> active   (hints_used incrementa)
```

`success` e `limit_reached` são estados finais — nenhuma nova chamada de IA é feita a
partir deles (FR-009, FR-010).

**Nota de implementação**: além dos campos acima, a implementação usa um atributo
`_cwd` (diretório de trabalho para resolver `test_command`) — puramente operacional, não
faz parte do modelo de negócio documentado aqui.

## Round

Uma iteração dentro de uma `Session`.

| Campo | Tipo | Descrição | Regras |
|---|---|---|---|
| `round_number` | int | posição da rodada na sessão (1-based) | sequencial |
| `student_code` | string | código submetido pelo aluno nesta rodada | pode repetir o da rodada anterior se o aluno não editou |
| `test_result` | objeto \| null | resultado da execução dos testes (`passed: bool`, `failed_tests: [string]`, `raw_output: string`) | `null` quando `has_tests=false` |
| `stage` | enum: `not_understood` \| `syntax_error` \| `logic_error` \| `conceptual_block` | estágio pedagógico da rodada | classificado pelo modelo de IA, conforme decisão de regra de negócio em FR-003 da spec |
| `prompt_sent` | string | prompt efetivamente enviado ao Gemini (já resumido/truncado se aplicável) | logado integralmente (FR-011) |
| `model_response_raw` | string | resposta bruta recebida do modelo antes da guarda | logado integralmente |
| `guard_rejected` | bool | se a guarda rejeitou `model_response_raw` | ver `guard.py` |
| `regeneration_attempts` | int | quantas vezes a resposta foi regenerada nesta rodada | 0, 1 ou 2 (limite pequeno, ver research.md) |
| `question_shown` | string | pergunta efetivamente exibida ao aluno (do modelo ou fallback) | nunca contém código-solução (Princípio I) |
| `used_fallback` | bool | se `question_shown` veio do fallback fixo, não do modelo | true quando todas as tentativas de regeneração são rejeitadas |
| `timestamp` | string (ISO 8601) | momento da rodada | gerado no momento do registro |

**Regra de validação central**: nenhuma instância de `Round` pode ter `question_shown`
contendo um bloco de código completo/executável — invariante garantido pela guarda antes de
a `Round` ser considerada concluída (testável isoladamente, ver `tests/unit/guard_test`).

## LogEntry

Representação persistida de um `Round`, uma linha por rodada no arquivo JSON Lines da
sessão (ver `contracts/log-schema.md` para o schema exato serializado).

Relação: `LogEntry` é uma projeção direta de `Round` — não introduz campos novos além dos já
listados acima; existe como entidade separada apenas porque é a fronteira de persistência
(FR-011) e não é consultada pelo próprio sistema durante a sessão (é somente para análise
posterior, conforme Princípio IV da constitution).
