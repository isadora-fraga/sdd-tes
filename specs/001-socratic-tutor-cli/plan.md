# Implementation Plan: Tutor Socrático de Programação (CLI)

**Branch**: `001-socratic-tutor-cli` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-socratic-tutor-cli/spec.md`

## Summary

Ferramenta local, em Python, que acompanha um aluno de CS1/CS2 resolvendo um exercício de
código. A cada rodada, roda os testes do exercício localmente (`pytest` via `subprocess`),
envia enunciado + código + resultado dos testes + estado da sessão para a API do Gemini
pedindo uma única pergunta orientadora (nunca a solução) em formato estruturado (JSON), e
aplica uma guarda determinística sobre a resposta antes de exibi-la. Cada rodada é
registrada em log JSON Lines. A sessão termina por sucesso (testes passam, ou confirmação
manual do aluno quando não há testes) ou por atingir o limite de dicas configurado. A CLI é
a entrega principal; uma camada web local mínima e sem login (Flask) reexpõe a mesma lógica
de negócio para fins de demonstração/comparação na apresentação do trabalho.

## Technical Context

**Language/Version**: Python 3.11+ (planejado); implementado e testado neste ambiente com
Python 3.9 por ser a única versão disponível na máquina de desenvolvimento — código evita
sintaxe exclusiva de 3.10+ para permanecer compatível com ambos

**Primary Dependencies**: `google-genai` (SDK oficial da API Gemini), `pytest` (execução dos
testes do exercício do aluno via `subprocess`, e testes do próprio projeto), `Flask`
(camada web local mínima, User Story 5 — única dependência extra sobre a CLI)

**Storage**: arquivo local em disco, formato JSON Lines (um arquivo de log por sessão); sem
banco de dados

**Testing**: `pytest` para os testes do próprio projeto (unit/contract/integration)

**Target Platform**: máquina local do usuário (macOS/Linux), execução via terminal;
interface web servida em `localhost` sem exposição externa

**Project Type**: single project — CLI com um módulo de core reutilizado por uma camada web
opcional fina

**Performance Goals**: não crítico; latência por rodada dominada pela chamada de rede à API
Gemini (fora do controle do projeto) — sem metas numéricas formais

**Constraints**: uso econômico da API (Princípio II da constitution): modelo "flash",
resposta em formato estruturado curto, sem reenvio de histórico completo, máximo de 1–2
tentativas de regeneração por rodada antes do fallback; execução 100% local (Princípio V);
sem autenticação (Princípio V)

**Scale/Scope**: uso individual, uma sessão por vez, um aluno por execução — escopo
deliberadamente pequeno (constitution, Radical Simplicity)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Verificação | Status |
|---|---|---|
| I. Socratic-Only Responses (NON-NEGOTIABLE) | Guarda determinística (heurísticas + resposta estruturada em JSON com campo `question` isolado) roda sobre toda resposta do modelo antes da exibição; testável via contract tests com respostas simuladas | PASS |
| II. Cost-Conscious API Usage | Modelo "flash"; 1 chamada por rodada (estágio incluso na mesma resposta); limite de regeneração 1–2 tentativas; limite de dicas configurável (padrão 5); sem reenvio de histórico completo (estado resumido, não a conversa inteira) | PASS |
| III. Structured Pedagogical State | Entidades `Session`/`Round` explícitas com campo `stage` e `hints_used`, persistidas/logadas a cada rodada — inspecionável fora do prompt | PASS |
| IV. Research-Grade Logging | Um `LogEntry` estruturado por rodada, formato JSON Lines, schema documentado em `contracts/log-schema.md` | PASS |
| V. Radical Simplicity | CLI single-process; execução de testes via `subprocess` local; sem DB; sem auth; camada web é opcional e reusa o mesmo módulo de core, sem duplicar regra de negócio | PASS |

Nenhuma violação identificada — `Complexity Tracking` não se aplica.

**Revisão pós-implementação (T041)**: reconfirmado contra o código final —
44 testes automatizados passando (`python -m pytest tests/`); número de chamadas de API
por sessão nunca excede `hint_limit` mesmo com regenerações (`tests/integration/test_hint_limit.py`);
nenhuma infraestrutura além de arquivos locais (JSON Lines) foi introduzida; Python
efetivamente usado nesta máquina foi 3.9 (não 3.11+ como planejado — ver Technical Context),
sem impacto nos princípios da constitution.

## Project Structure

### Documentation (this feature)

```text
specs/001-socratic-tutor-cli/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   ├── gemini-contract.md
│   ├── cli-contract.md
│   ├── web-api-contract.md
│   └── log-schema.md
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
# Option 1: Single project (DEFAULT) — escolhido para este feature
src/
├── models/
│   ├── session.py        # Session, Round (entidades + transições de estado)
│   └── log_entry.py       # LogEntry (schema do JSON Lines)
├── services/
│   ├── validators.py       # valida sintaxe Python do código antes de qualquer chamada de IA (FR-016)
│   ├── test_runner.py     # roda pytest do exercício via subprocess
│   ├── gemini_client.py   # chamada à API Gemini (resposta estruturada JSON)
│   ├── guard.py           # verificação anti-solução sobre a resposta do modelo
│   ├── logger.py          # escrita append-only do log JSON Lines
│   └── session_service.py # orquestrador único (start_session/process_round) — evita
│                           # duplicar regra de negócio entre CLI e web (FR-015)
├── cli/
│   └── main.py             # loop interativo de sessão no terminal, chama session_service
└── web/
    └── app.py              # Flask mínimo, chama session_service (User Story 5)

tests/
├── contract/     # schema da resposta do Gemini, schema do log
├── integration/  # fluxo completo de sessão (sucesso, limite de dicas, guard disparando)
└── unit/         # guard.py, session.py (transições de estágio), logger.py
```

**Structure Decision**: Opção 1 (projeto único). Toda a regra de negócio vive em
`src/models` e `src/services`; `src/cli` e `src/web` são as duas interfaces (fina camada de
apresentação cada uma) sobre o mesmo core, conforme exigido pela spec (FR-015) e pelo
Princípio V da constitution — nenhuma regra de negócio duplicada entre CLI e web.

## Complexity Tracking

*Nenhuma violação da constitution identificada nesta fase — tabela não se aplica.*
