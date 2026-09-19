# Quickstart: Tutor Socrático de Programação (CLI)

Guia de validação ponta-a-ponta desta feature. Não contém código de implementação — apenas
como rodar e o que esperar (ver `contracts/` para os schemas exatos).

## Pré-requisitos

- Python 3.11+
- Uma chave de API do Google Gemini, exportada como variável de ambiente:
  ```bash
  export GEMINI_API_KEY="sua-chave-aqui"
  ```
- Dependências instaladas (`google-genai`, `pytest`, e `Flask` se for validar a interface
  web da User Story 5).

## Cenário 1 — Pergunta orientadora em vez de solução (User Story 1, P1)

1. Prepare um enunciado simples (ex.: "escreva uma função que retorna a soma de uma lista")
   e um arquivo de código do aluno com um bug conhecido (ex.: usa `+` em vez de acumular em
   loop, ou esquece o `return`).
2. Rode a CLI apontando para esses dois arquivos e para um arquivo de teste `pytest`
   correspondente (`--tests`).
3. **Esperado**: a saída mostra que o teste falhou, seguida de uma pergunta orientadora
   relacionada ao bug — nunca um trecho de código-solução completo.

## Cenário 2 — Guarda bloqueando uma resposta com solução (User Story 1)

1. Use o modo de teste do `gemini_client` (mock/stub, conforme os contract tests) para
   simular uma resposta do modelo que contém um bloco de código completo.
2. **Esperado**: a pergunta exibida ao aluno não é essa resposta — é a pergunta de fallback
   fixa, e o log da rodada mostra `guard_rejected: true`, `used_fallback: true`.

## Cenário 3 — Progressão de estágio ao longo de rodadas (User Story 2, P2)

1. Rode uma sessão com dois envios de código seguidos: o primeiro com erro de sintaxe
   (ex.: falta de `:` em um `if`), o segundo já sintaticamente correto mas com lógica errada.
2. **Esperado**: o log da sessão mostra `stage: syntax_error` na primeira rodada e
   `stage: logic_error` na segunda, com `hints_used` incrementando a cada rodada.

## Cenário 4 — Encerramento por limite de dicas (User Story 3, P3)

1. Inicie uma sessão com `--hint-limit 1` e um código que nunca chega a passar nos testes.
2. **Esperado**: após a 1ª dica, uma nova tentativa de rodada é recusada com mensagem de
   limite atingido, sem nenhuma chamada adicional à API (verificável tanto pela ausência de
   nova linha de log quanto, em teste automatizado, por um mock de API não invocado
   novamente).

## Cenário 5 — Sucesso sem testes automatizados (FR-014)

1. Inicie uma sessão sem `--tests`.
2. Após a IA responder com uma avaliação qualitativa (ex.: "parece consistente com o
   enunciado"), digite `/done`.
3. **Esperado**: a sessão encerra com status de sucesso; sem `/done`, a sessão permanece
   `active` indefinidamente (até o limite de dicas).

## Cenário 6 — Rejeição de código não-Python (FR-016)

1. Inicie uma sessão apontando `--code` para um arquivo `.java` ou `.js` qualquer.
2. **Esperado**: erro imediato pedindo código Python válido; nenhuma linha é adicionada ao
   log da sessão (nenhuma chamada de IA ocorreu).

## Cenário 7 — Log estruturado reprocessável (User Story 4, P4)

1. Rode qualquer uma das sessões acima até o fim.
2. Abra o arquivo `logs/<session_id>.jsonl` e confirme que cada linha é um JSON válido,
   isoladamente parseável, seguindo `contracts/log-schema.md`.

## Cenário 8 — Interface web local para apresentação (User Story 5, P5)

1. Rode a aplicação Flask localmente (`python -m src.web.app`).
2. Acesse `http://localhost:5000` sem nenhum login.
3. Repita o Cenário 1 pela interface web e confirme que o comportamento (pergunta em vez de
   solução) é idêntico ao da CLI para a mesma entrada — este é o cenário a ser usado na
   apresentação para comparar lado a lado com um assistente de IA genérico (SC-005).

## Rodando os testes do próprio projeto

```bash
pytest tests/unit tests/contract tests/integration
```
