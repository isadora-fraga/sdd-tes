# Log de pesquisa

Este projeto é um artefato de escopo pequeno dentro de uma linha de pesquisa de doutorado
sobre arquiteturas multiagente para apoio educacional em programação (ver
`.specify/memory/constitution.md`, Princípio IV — Research-Grade Logging).

Cada sessão executada gera um arquivo `logs/<session_id>.jsonl`, com uma linha JSON por
rodada, seguindo o schema documentado em
[`specs/001-socratic-tutor-cli/contracts/log-schema.md`](../specs/001-socratic-tutor-cli/contracts/log-schema.md).

Esses arquivos são o dado bruto para análises futuras, por exemplo:

- distribuição de estágios pedagógicos (`stage`) por rodada, ao longo de uma sessão;
- taxa de acionamento da guarda anti-solução (`guard_rejected`/`used_fallback`) — um proxy
  de quão frequentemente um modelo generalista tenta vazar a solução sem essa camada;
  número médio de dicas até o sucesso, por dificuldade percebida do exercício.

Este único agente socrático é deliberadamente mais simples que a arquitetura multiagente
que a pesquisa investiga; os logs aqui gerados servem como linha de base para comparação
futura contra uma versão com múltiplos agentes especializados.
