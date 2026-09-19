# Tutor Socrático de Programação

Ferramenta local que acompanha um aluno de CS1/CS2 resolvendo um exercício de código: em
vez de dar a solução, faz perguntas orientadoras (estilo socrático), com uma guarda
determinística que bloqueia qualquer resposta de IA que tente vazar a solução. Construída
com [Spec-Driven Development](specs/001-socratic-tutor-cli/) como exercício da disciplina
de pós-graduação, ligada a uma linha de pesquisa de doutorado sobre arquiteturas
multiagente para apoio educacional em programação.

Ver a especificação completa em [`specs/001-socratic-tutor-cli/`](specs/001-socratic-tutor-cli/)
(`spec.md`, `plan.md`, `tasks.md`, `contracts/`) e os princípios do projeto em
[`.specify/memory/constitution.md`](.specify/memory/constitution.md).

## Instalação

Requer Python 3.9+ (desenvolvido/testado com 3.9; alvo original do plano era 3.11+, ver
nota no `plan.md`).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuração

Defina sua chave da API do Gemini de uma das duas formas (**nunca coloque a chave direto
no código, em argumento de linha de comando, ou em qualquer chat/mensagem**):

**Opção A — arquivo `.env` local (recomendado, não precisa repetir a cada sessão de terminal):**
```bash
cp .env.example .env
# edite .env e cole GEMINI_API_KEY=sua-chave-aqui
```
`.env` já está no `.gitignore` — nunca é commitado.

**Opção B — variável de ambiente (só vale para o terminal atual):**
```bash
export GEMINI_API_KEY="sua-chave-aqui"
```

## Rodando a CLI

```bash
python -m src.cli start \
  --statement "Escreva uma função que soma os números de uma lista." \
  --code caminho/para/codigo_do_aluno.py \
  --tests caminho/para/test_exercicio.py \
  --hint-limit 5
```

`--statement` e `--code` aceitam tanto um caminho de arquivo quanto texto literal.
`--tests` é opcional (ver FR-014 no `spec.md` para o comportamento sem testes). Comandos
especiais durante a sessão: `/done` (confirma sucesso quando não há testes) e `/quit`
(encerra manualmente).

## Rodando a interface web (demonstração/comparação — User Story 5)

```bash
python -m src.web.app
```

Acesse `http://localhost:5000`. Sem login — uso local apenas, para demonstração e
comparação lado a lado com um assistente de IA genérico (ver `quickstart.md`, Cenário 8).

## Rodando os testes do projeto

```bash
python -m pytest tests/
```

## Estrutura

Ver `specs/001-socratic-tutor-cli/plan.md` (seção Project Structure) para o mapa completo
de `src/models`, `src/services`, `src/cli`, `src/web`.

## Log de pesquisa

Cada sessão gera `logs/<session_id>.jsonl` — um artefato estruturado para análise
posterior (ver `docs/RESEARCH_LOG.md` e `contracts/log-schema.md`).
