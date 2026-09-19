# Specification Quality Checklist: Tutor Socrático de Programação (CLI)

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-19
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- As 3 clarificações pendentes foram resolvidas diretamente em conversa e incorporadas à
  spec: (1) sucesso sem testes automatizados = avaliação qualitativa da IA + confirmação
  manual do aluno (`/done`) — FR-014; (2) estágio pedagógico classificado pelo próprio
  modelo de IA, registrado como decisão de regra de negócio deliberada — FR-003; (3) limite
  de dicas configurável via CLI, padrão 5 — FR-008.
- User Story 5 / FR-015 / SC-005 (interface web local para apresentação/comparação) foram
  adicionados após a resolução das clarificações, a pedido do usuário.
- FR-016 (validação de código não-Python antes de qualquer chamada de IA) foi adicionado
  durante o `/speckit-plan`, a partir de uma pergunta do usuário sobre entradas em outra
  linguagem.
- Spec pronta para `/speckit-plan`.

## Feature Readiness (pós-implementação — T040)

Todos os FR-001 a FR-016 têm teste automatizado correspondente passando
(`python -m pytest tests/` — 44 testes, 0 falhas):

| Requisito | Teste(s) |
|---|---|
| FR-001, FR-016 | `tests/unit/test_validators.py`, `tests/integration/test_single_round_flow.py` |
| FR-002 | `tests/unit/test_test_runner.py` |
| FR-003 | `tests/integration/test_multi_round_progression.py` |
| FR-004, FR-012 | `tests/contract/test_gemini_contract.py`, `tests/unit/test_cli_main.py` (falha de comunicação exige confirmação antes de nova tentativa — corrigido após reproduzir um 503 real da API) |
| FR-005, FR-006 | `tests/unit/test_guard.py`, `tests/integration/test_single_round_flow.py` |
| FR-007 | `src/cli/main.py` (`cmd_start`, loop manual — smoke-testado + `tests/unit/test_cli_main.py`) |
| FR-008, FR-009 | `tests/integration/test_hint_limit.py` |
| FR-010 | `tests/integration/test_single_round_flow.py` (Scenario 3) |
| FR-011 | `tests/contract/test_log_schema.py`, `tests/integration/test_log_reprocessing.py` |
| FR-013 | implícito em `validators.py`/`test_runner.py` (Python + pytest) |
| FR-014 | `tests/integration/test_single_round_flow.py` (Scenario 4) |
| FR-015 | `tests/integration/test_web_matches_cli.py` |

**Ressalva**: T038 (validação manual completa do `quickstart.md` com uma chave real do
Gemini) não pôde ser executada neste ambiente por não haver `GEMINI_API_KEY` disponível.
Toda a lógica de negócio foi validada com um cliente Gemini simulado (mock); a validação
com a API real fica pendente para quando o usuário rodar localmente com sua chave.
