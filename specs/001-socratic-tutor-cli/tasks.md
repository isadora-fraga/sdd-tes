---
description: "Task list for feature implementation"
---

# Tasks: Tutor Socrático de Programação (CLI)

**Input**: Design documents from `/specs/001-socratic-tutor-cli/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: solicitados explicitamente pelo usuário (TDD por história) — cada história tem
tarefas de teste antes das tarefas de implementação correspondentes.

**Organization**: tarefas agrupadas por user story (P1–P5, mesma ordem de prioridade da
spec), cada uma independentemente implementável e testável.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência de tarefa incompleta)
- **[Story]**: a qual user story a tarefa pertence (US1–US5)
- Caminhos de arquivo exatos em cada descrição

## Path Conventions

Projeto único (Option 1 do plan.md): `src/`, `tests/` na raiz do repositório.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: inicialização do projeto e esqueleto de diretórios

- [X] T001 Criar a estrutura de diretórios do projeto conforme `plan.md` (`src/models/`,
      `src/services/`, `src/cli/`, `src/web/`, `tests/contract/`, `tests/unit/`,
      `tests/integration/`, `logs/`), com `__init__.py` onde necessário.
- [X] T002 Criar `requirements.txt` (ou `pyproject.toml`) na raiz fixando `google-genai`,
      `pytest`, `Flask`, e documentando o requisito de Python 3.11+.
- [X] T003 [P] Implementar carregamento de configuração em `src/config.py` que lê
      `GEMINI_API_KEY` do ambiente e levanta um erro claro na inicialização se estiver
      ausente (usado tanto pela CLI quanto pela web).
- [X] T004 [P] Criar `README.md` mínimo na raiz documentando instalação de dependências,
      configuração de `GEMINI_API_KEY`, e como rodar `python -m src.cli start` (conforme
      `contracts/cli-contract.md`).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: modelos de dados usados por todas as user stories

**⚠️ CRITICAL**: nenhuma user story pode começar antes desta fase estar completa

- [X] T005 [P] Escrever teste unitário `tests/unit/test_session_model.py` verificando que
      `Session` tem os campos `session_id`, `exercise_statement`, `has_tests`,
      `test_command`, `hint_limit` (padrão **5**, conforme FR-008), `hints_used` (inicia em
      **0**), `status` (enum `active|success|limit_reached`, inicia em `active`), `rounds`
      (lista vazia) — conforme `data-model.md`. Teste DEVE falhar até T007.
- [X] T006 [P] Escrever teste unitário `tests/unit/test_session_transitions.py` verificando
      a máquina de estados de `data-model.md`: `active→success` (testes passam, ou `/done`
      manual quando `has_tests=false`), `active→limit_reached` (`hints_used == hint_limit`),
      e que `success`/`limit_reached` são terminais (nenhuma chamada de IA nem incremento de
      `hints_used` permitido a partir deles). Teste DEVE falhar até T007.
- [X] T007 Implementar as dataclasses `Session` e `Round` com o método de transição de
      estado em `src/models/session.py`, conforme as tabelas de campos de `data-model.md`
      (`Round`: `round_number`, `student_code`, `test_result`, `stage` — enum
      `not_understood|syntax_error|logic_error|conceptual_block` —, `prompt_sent`,
      `model_response_raw`, `guard_rejected`, `regeneration_attempts`, `question_shown`,
      `used_fallback`, `timestamp`) — faz T005 e T006 passarem.
- [X] T008 [P] Escrever teste unitário `tests/unit/test_log_entry.py` verificando que a
      serialização de `LogEntry` bate exatamente com o schema de
      `contracts/log-schema.md` (todos os campos presentes; `test_result: null` quando
      `has_tests=false`). Teste DEVE falhar até T009.
- [X] T009 Implementar o serializador `LogEntry` em `src/models/log_entry.py`, convertendo
      um `Round` (+ `session_id`, `hint_limit`, `session_status_after`) para o formato JSON
      de `contracts/log-schema.md` — faz T008 passar.

**Checkpoint**: fundação pronta (`Session`/`Round`/`LogEntry` existem e têm cobertura de
teste) — user stories podem começar.

---

## Phase 3: User Story 1 - Receber orientação socrática em vez da solução (Priority: P1) 🎯 MVP

**Goal**: dado um enunciado, o código do aluno e (quando houver) o resultado dos testes,
obter uma pergunta orientadora — nunca uma solução — com guarda determinística e fallback;
encerramento imediato quando os testes já passam; avaliação qualitativa quando não há
testes.

**Independent Test**: rodar uma sessão com um enunciado e um código com bug conhecido e
verificar que a saída é uma pergunta, não uma solução; simular uma resposta do modelo
contendo uma solução e verificar que a guarda bloqueia e mostra o fallback; rodar com código
já correto e verificar sucesso imediato (ver quickstart.md, Cenários 1, 2, 5, 6).

### Tests for User Story 1 ⚠️

- [X] T010 [P] [US1] Teste de contrato `tests/contract/test_gemini_contract.py` validando a
      montagem do request e o schema de resposta de `contracts/gemini-contract.md`: resposta
      válida é aceita; resposta com bloco de código dentro de `question` dispara rejeição da
      guarda; resposta fora do schema (campo `question`/`stage` ausente, ou `stage` fora do
      enum) é tratada como falha de comunicação (FR-012), não como rejeição de guarda.
- [X] T011 [P] [US1] Teste unitário `tests/unit/test_guard.py` para as heurísticas
      anti-solução (bloco de código cercado com estrutura de função/classe → rejeita; frases
      imperativas de resolução direta → rejeita; texto em forma de pergunta → aceita),
      conforme `research.md` item 3.
- [X] T012 [P] [US1] Teste unitário `tests/unit/test_validators.py` para FR-016: código
      Python válido via `ast.parse` → aceito; trechos característicos de outra linguagem
      (ex.: `public class`, `console.log`, `#include`) → rejeitados com mensagem clara, sem
      nenhuma chamada de API.
- [X] T013 [P] [US1] Teste unitário `tests/unit/test_test_runner.py` para execução via
      `subprocess`: código que passa → `passed=true`, `failed_tests=[]`; código que falha →
      `passed=false` com os nomes dos testes falhos; `has_tests=false` → `test_runner` não é
      chamado e `test_result` permanece `null`.
- [X] T014 [P] [US1] Teste de integração `tests/integration/test_single_round_flow.py`
      cobrindo os Acceptance Scenarios 1–4 da User Story 1 (com um cliente Gemini mockado):
      rodada normal → pergunta exibida; resposta simulada com solução vazada → guarda
      bloqueia → fallback exibido; código já passa nos testes → sucesso imediato, sem
      chamada ao Gemini; sem testes configurados → avaliação qualitativa exibida, sessão
      continua `active` até `/done`.

### Implementation for User Story 1

- [X] T015 [P] [US1] Implementar `src/services/validators.py`:
      `validate_python_syntax(code: str) -> None`, levantando um erro descritivo quando
      `ast.parse` falha ou o código bate com as heurísticas de outra linguagem (FR-016);
      chamado antes de qualquer chamada ao Gemini — faz T012 passar.
- [X] T016 [P] [US1] Implementar `src/services/test_runner.py`:
      `run_tests(test_command, code_path) -> TestResult | None` via
      `subprocess.run(["pytest", ...])`, retornando `None` quando `test_command` é `None`
      (FR-002) — faz T013 passar.
- [X] T017 [P] [US1] Implementar `src/services/gemini_client.py`: monta o prompt conforme a
      tabela de Request de `contracts/gemini-contract.md` (`exercise_statement`,
      `student_code`, `test_result`, `stage_history`, `hints_used`/`hint_limit`, com
      truncamento sinalizado ao aluno se `student_code` for excessivamente longo — Edge
      Case), chama o SDK `google-genai` com um modelo da família "flash" pedindo saída
      estruturada em JSON conforme o schema de `contracts/gemini-contract.md`, e levanta uma
      exceção `GeminiCommunicationError` distinta em erro de rede/timeout/schema inválido
      (FR-012) — faz parte de T010 passar.
- [X] T018 [P] [US1] Implementar `src/services/guard.py`:
      `check_response(question: str) -> bool` aplicando as três heurísticas do item 3 de
      `research.md` (bloco de código completo, frases imperativas de resolução, ausência de
      forma interrogativa) — faz T011 passar e completa T010.
- [X] T019 [US1] Implementar `src/services/session_service.py` (novo módulo orquestrador,
      necessário para que FR-015 não duplique regra de negócio entre CLI e web):
      `start_session(statement, code, test_command, hint_limit) -> Session`, validando
      entrada não vazia e Python válido (FR-001, via T015) e, se `has_tests`, rodando os
      testes uma vez (via T016) com atalho de sucesso imediato (Acceptance Scenario 3 /
      FR-010) antes de qualquer chamada de IA.
- [X] T020 [US1] Em `src/services/session_service.py`, implementar
      `process_round(session, student_code) -> Round` orquestrando
      test_runner → gemini_client → guard → até 1–2 tentativas de regeneração
      (`research.md` item 3) → pergunta de fallback fixa pré-definida (FR-006) quando todas
      as tentativas forem rejeitadas, preenchendo todos os campos de `Round`.
- [X] T021 [US1] Em `src/services/session_service.py`, implementar o ramo do FR-014: quando
      `has_tests=false`, pedir uma avaliação qualitativa (mesma chamada, conforme nota de
      prompt em `contracts/gemini-contract.md`) em vez de uma pergunta convencional, nunca
      definir `status=success` automaticamente, e só transicionar para `success` mediante um
      comando explícito `/done` recebido do chamador (CLI/web).
- [X] T022 [US1] Implementar o subcomando `start` em `src/cli/main.py` conforme
      `contracts/cli-contract.md` (`--statement`, `--code` aceitando texto literal ou
      caminho de arquivo — FR-001 —, `--tests`, `--hint-limit` padrão **5**), chamando
      `session_service.start_session`, exibindo a mensagem de sucesso imediato ou a primeira
      `question_shown`, e tratando `GeminiCommunicationError` (T017) de forma clara sem
      travar e sem consumir dica (FR-012) — suficiente para exercitar o Independent Test da
      US1 manualmente.

**Checkpoint**: User Story 1 completa e testável de forma independente (quickstart.md,
Cenários 1, 2, 5, 6).

---

## Phase 4: User Story 2 - Progredir através de rodadas com estado pedagógico (Priority: P2)

**Goal**: ao longo de várias rodadas, o estágio pedagógico e a contagem de dicas evoluem de
forma coerente com o progresso real do aluno.

**Independent Test**: duas rodadas simuladas com resultados de teste diferentes (erro de
execução → erro de lógica) mostram `stage` diferente entre elas e `hints_used`
incrementando (quickstart.md, Cenário 3).

### Tests for User Story 2 ⚠️

- [X] T023 [P] [US2] Teste de integração `tests/integration/test_multi_round_progression.py`
      cobrindo os Acceptance Scenarios 1–2 da User Story 2: uma sessão com 1 dica já usada
      recebe código atualizado ainda com falha → `hints_used` incrementa e `stage` é
      recalculado; uma sessão em que o código passa de "não executa" para
      "executa mas com saída errada" mostra `stage` mudando de `syntax_error` para
      `logic_error` entre rodadas.

### Implementation for User Story 2

- [X] T024 [US2] Estender `src/services/session_service.py` `process_round` (T020) para
      anexar cada `Round` a `Session.rounds`, incrementar `Session.hints_used` exatamente
      uma vez por chamada de IA concluída (incluindo tentativas internas de regeneração,
      conforme `research.md` item 3 / FR-008), e passar `stage_history` (os `stage` das
      rodadas anteriores) na próxima chamada, conforme `contracts/gemini-contract.md` — faz
      T023 passar.
- [X] T025 [US2] Estender o subcomando `start` em `src/cli/main.py` (T022) para um loop
      interativo completo (`contracts/cli-contract.md`, "Loop de rodada"): após exibir
      `question_shown`, pedir ao aluno código atualizado e/ou um comando especial
      (`/done`, `/quit`), chamar `process_round` novamente, e repetir até um `status`
      terminal ser atingido.

**Checkpoint**: User Stories 1 e 2 funcionam juntas e de forma independente.

---

## Phase 5: User Story 3 - Encerrar a sessão ao atingir o limite de dicas (Priority: P3)

**Goal**: ao atingir `hint_limit`, encerrar a sessão informando claramente o motivo, sem
nenhuma chamada adicional à API.

**Independent Test**: com `hint_limit=1` e código que nunca passa, confirmar encerramento
após 1 dica sem chamada adicional (quickstart.md, Cenário 4).

### Tests for User Story 3 ⚠️

- [X] T026 [P] [US3] Teste de integração `tests/integration/test_hint_limit.py` usando um
      cliente Gemini mockado com contador de chamadas: com `hint_limit=1` e código que nunca
      passa, a sessão transiciona para `limit_reached` após exatamente 1 chamada, uma nova
      tentativa de rodada é recusada localmente, e o contador do mock nunca ultrapassa 1.

### Implementation for User Story 3

- [X] T027 [US3] Implementar em `src/services/session_service.py` `process_round` (T020) a
      checagem `hints_used == hint_limit`: se o limite já foi atingido, retornar
      imediatamente com `status=limit_reached` e um motivo de encerramento claro, **sem**
      chamar `gemini_client` (FR-009) — faz T026 passar.
- [X] T028 [US3] Atualizar o loop de `src/cli/main.py` (T025) para detectar
      `status=limit_reached`, imprimir a mensagem de encerramento de
      `contracts/cli-contract.md` ("Saída ao encerrar"), e sair com código `1`.

**Checkpoint**: User Stories 1–3 completas (quickstart.md, Cenário 4).

---

## Phase 6: User Story 4 - Registrar cada rodada para análise de pesquisa (Priority: P4)

**Goal**: log estruturado em JSON Lines, uma entrada por rodada concluída, reprocessável
para fins de pesquisa.

**Independent Test**: rodar uma sessão completa e verificar uma entrada de log por rodada,
com todos os campos esperados (quickstart.md, Cenário 7).

### Tests for User Story 4 ⚠️

- [X] T029 [P] [US4] Teste de contrato `tests/contract/test_log_schema.py` verificando que
      cada linha escrita bate exatamente com `contracts/log-schema.md` (incluindo
      `test_result: null` quando `has_tests=false`) e que rodadas rejeitadas antes de
      qualquer chamada ao Gemini (falha de validação FR-016) **não** geram linha de log,
      conforme a garantia documentada em `log-schema.md`.
- [X] T030 [P] [US4] Teste de integração `tests/integration/test_log_reprocessing.py`
      rodando uma sessão completa de múltiplas rodadas (reaproveitando o cenário de T023) e
      confirmando que `logs/<session_id>.jsonl` tem uma linha JSON por rodada concluída,
      cada uma parseável isoladamente, em ordem.

### Implementation for User Story 4

- [X] T031 [P] [US4] Implementar `src/services/logger.py`:
      `append_round(session, round) -> None`, escrevendo uma linha JSON (via
      `src/models/log_entry.py`, T009) em `logs/<session_id>.jsonl` em modo append, com
      `flush()`/sincronização em disco logo após cada escrita (garantia de durabilidade de
      `data-model.md`) — faz T030 passar.
- [X] T032 [US4] Conectar `logger.append_round` (T031) em `src/services/session_service.py`
      `process_round` (T020), chamado uma vez por rodada concluída (incluindo rodadas
      rejeitadas pela guarda/fallback) e **não** chamado nas falhas de pré-validação do
      FR-016 — faz T029 passar.

**Checkpoint**: User Stories 1–4 completas (quickstart.md, Cenário 7).

---

## Phase 7: User Story 5 - Interface web local básica (Priority: P5)

**Goal**: UI web local, sem login, reaproveitando integralmente a lógica de negócio da CLI,
para fins de demonstração/comparação na apresentação do trabalho.

**Independent Test**: a mesma entrada usada na CLI produz o mesmo comportamento na web
(mesma pergunta/mesmo bloqueio de guarda) — quickstart.md, Cenário 8.

### Tests for User Story 5 ⚠️

- [X] T033 [P] [US5] Teste de contrato `tests/contract/test_web_api.py` (Flask test client)
      cobrindo `contracts/web-api-contract.md`: `GET /` retorna a página com formulário;
      `POST /session` com payloads válido/inválido espelha a validação de FR-001/FR-016;
      `POST /session/<id>/round` retorna os mesmos campos de `Round` usados no log.
- [X] T034 [P] [US5] Teste de integração `tests/integration/test_web_matches_cli.py`
      reproduzindo a entrada do Cenário 1 da US1 via Flask test client e verificando que o
      resultado (`guard_rejected`/`question_shown`) é idêntico ao teste de integração da CLI
      (T014), comprovando que não há duplicação de regra de negócio (FR-015).

### Implementation for User Story 5

- [X] T035 [US5] Implementar as rotas Flask em `src/web/app.py` (`GET /`, `POST /session`,
      `POST /session/<session_id>/round`) conforme `contracts/web-api-contract.md`, chamando
      diretamente `session_service.start_session`/`process_round` (T019/T024/T027) — sem
      reimplementar validação, guarda ou lógica de limite de dicas — faz T033/T034
      passarem.
- [X] T036 [P] [US5] Criar templates HTML mínimos em `src/web/templates/index.html`
      (formulário de início: enunciado, código, testes opcional, limite de dicas) e
      `src/web/templates/session.html` (diálogo de rodada, mensagens de sucesso/limite) —
      HTML/CSS simples, sem build step, conforme Radical Simplicity.
      **Atualização**: layout final adaptado de um export do Google Stitch (Tailwind via
      CDN), com melhorias de usabilidade aplicadas depois (heurísticas de Nielsen): campo
      único de entrada com detecção automática de bloco de código Python (regras
      client-side, sem chamada de IA), limite de dicas movido para um `<details>`
      secundário/recolhido, feedback em tempo real de detecção, e preservação do texto do
      usuário em caso de erro. `session.html` foi consolidado dentro de `index.html`
      (single-page app com fetch) para reduzir a superfície de arquivos. **Layout provisório —
      substituir pelo export do Google Stitch quando disponível.**
- [X] T037 [US5] Adicionar o entrypoint `python -m src.web.app` (quickstart.md, Cenário 8),
      servindo apenas em `localhost`, sem autenticação.

**Checkpoint**: as 5 user stories completas e independentemente testáveis (quickstart.md,
Cenário 8 — comparação lado a lado com um assistente de IA genérico, SC-005).

---

## Phase 8: Polish & Cross-Cutting Concerns

- [ ] T038 [P] Rodar a validação completa de `quickstart.md` (todos os 8 cenários)
      manualmente, de ponta a ponta, com uma chave de API do Gemini real.
- [X] T039 [P] Criar `docs/RESEARCH_LOG.md` apontando para `logs/*.jsonl` como o artefato de
      dado de pesquisa (Princípio IV da constitution), para referência futura da linha de
      pesquisa de doutorado.
- [X] T040 Revisar FR-001 a FR-016 contra o comportamento implementado e marcar em
      `specs/001-socratic-tutor-cli/checklists/requirements.md` (seção Feature Readiness)
      que cada um tem um teste correspondente passando.
- [X] T041 Revisão final de conformidade com a constitution: confirmar que os 5 princípios
      seguem valendo contra o código implementado (I: testes de guarda passam; II: número de
      chamadas de API por sessão nunca excede `hint_limit`, mesmo com regenerações; III:
      estado inspecionável via `Session`/log; IV: schema de log estável; V: nenhuma
      infraestrutura extra foi introduzida) e atualizar a seção Constitution Check de
      `plan.md` se necessário.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências — pode começar imediatamente.
- **Foundational (Phase 2)**: depende da conclusão do Setup — bloqueia todas as user
  stories.
- **User Stories (Phase 3–7)**: todas dependem da conclusão da Foundational.
  - US2 (Phase 4) estende arquivos criados na US1 (`session_service.py`, `cli/main.py`) —
    não pode começar antes da US1 estar implementada, apesar de ser uma história separada e
    independentemente testável em seu próprio escopo de comportamento.
  - US3 (Phase 5) estende os mesmos arquivos que US2 — depende de US1 e US2 estarem
    implementadas.
  - US4 (Phase 6) estende `session_service.py` (T020) e é independente de US2/US3 em
    termos de arquivo — pode ser feita em paralelo com US2/US3 por outra pessoa, desde que
    ambas façam merge com cuidado no mesmo arquivo.
  - US5 (Phase 7) depende de US1 (reusa `session_service.start_session`/`process_round`) —
    pode começar assim que a US1 estiver completa, em paralelo com US2/US3/US4.
- **Polish (Phase 8)**: depende de todas as user stories desejadas estarem completas.

### Within Each User Story

- Testes escritos e DEVEM falhar antes da implementação correspondente.
- Modelos (Foundational) antes de serviços; serviços antes de CLI/web.
- História completa e validada (checkpoint) antes de avançar para a próxima prioridade.

### Parallel Opportunities

- Todas as tarefas `[P]` da Fase 1 podem rodar em paralelo.
- Todas as tarefas `[P]` da Fase 2 podem rodar em paralelo (os dois testes T005/T006; depois
  T008 em paralelo com a implementação T007, já que são arquivos diferentes).
- Dentro da US1: os 5 testes (T010–T014) são paralelos entre si; das implementações,
  T015–T018 são paralelas entre si (arquivos independentes); T019–T022 são sequenciais
  (mesmo arquivo/dependência direta).
- US4 pode ser desenvolvida em paralelo com US2/US3 (arquivos majoritariamente
  independentes, exceto o ponto de integração em `session_service.py`).
- US5 pode começar em paralelo com US2/US3/US4 assim que US1 estiver pronta.

---

## Parallel Example: User Story 1

```bash
# Testes da User Story 1, em paralelo:
Task: "Contract test em tests/contract/test_gemini_contract.py"
Task: "Unit test em tests/unit/test_guard.py"
Task: "Unit test em tests/unit/test_validators.py"
Task: "Unit test em tests/unit/test_test_runner.py"
Task: "Integration test em tests/integration/test_single_round_flow.py"

# Serviços independentes da User Story 1, em paralelo:
Task: "Implementar src/services/validators.py"
Task: "Implementar src/services/test_runner.py"
Task: "Implementar src/services/gemini_client.py"
Task: "Implementar src/services/guard.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 apenas)

1. Completar Fase 1: Setup
2. Completar Fase 2: Foundational (bloqueia todas as histórias)
3. Completar Fase 3: User Story 1
4. **PARAR e VALIDAR**: rodar quickstart.md Cenários 1, 2, 5, 6 de forma independente
5. Esse já é um MVP demonstrável do argumento central do trabalho (guarda anti-solução
   verificável em código)

### Incremental Delivery

1. Setup + Foundational → fundação pronta
2. + User Story 1 → validar independentemente → MVP demonstrável
3. + User Story 2 → validar independentemente (progressão de estágio)
4. + User Story 3 → validar independentemente (limite de dicas)
5. + User Story 4 → validar independentemente (log de pesquisa)
6. + User Story 5 → validar independentemente (UI web para a apresentação) — pode ficar
   para o fim, ou ser cortada, sem invalidar o restante do trabalho (é a única história
   marcada como "se der tempo" na conversa original)

---

## Notes

- `[P]` = arquivos diferentes, sem dependência de tarefa incompleta.
- `[Story]` mapeia a tarefa a uma user story específica para rastreabilidade.
- Cada user story deve ser completável e testável de forma independente, ainda que US2/US3
  estendam arquivos abertos pela US1 (dependência de arquivo, não de regra de negócio nova).
- Verificar que os testes falham antes de implementar.
- Fazer commit após cada tarefa ou grupo lógico de tarefas.
- Parar em qualquer checkpoint para validar a história isoladamente antes de seguir.
- Evitar: tarefas vagas, conflito de mesmo arquivo sem necessidade, dependências entre
  histórias que quebrem a independência de teste.
