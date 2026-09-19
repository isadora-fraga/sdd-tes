# Contract: CLI

## Iniciar uma sessão

```text
python -m src.cli start \
  --statement <arquivo-ou-texto-do-enunciado> \
  --code <arquivo-do-codigo-do-aluno> \
  [--tests <comando-ou-caminho-dos-testes>] \
  [--hint-limit <int, padrão 5>]
```

- `--statement`: obrigatório; aceita um caminho de arquivo `.txt`/`.md` ou texto direto
  (FR-001). Vazio → erro claro, sessão não inicia (Edge Case).
- `--code`: obrigatório; aceita caminho de arquivo `.py` ou colagem direta via stdin
  (FR-001). Vazio ou não-Python → erro claro, sessão não inicia, sem chamada de IA
  (FR-016).
- `--tests`: opcional; quando omitido, `Session.has_tests=false` e o fluxo do FR-014 se
  aplica.
- `--hint-limit`: opcional; inteiro positivo; padrão 5 (FR-008).

## Loop de rodada (interação no terminal)

A cada rodada, a CLI:
1. Roda os testes (se houver) e mostra passou/falhou.
2. Mostra a pergunta orientadora (ou avaliação qualitativa) recebida.
3. Aguarda o aluno digitar uma resposta e/ou apontar o código atualizado, ou um dos comandos
   especiais abaixo.

## Comandos especiais reconhecidos durante a sessão

| Comando | Efeito |
|---|---|
| `/done` | Encerra a sessão como sucesso quando `has_tests=false` (confirmação manual do aluno, FR-014). Sem efeito se `has_tests=true` (o encerramento por sucesso é automático via testes, FR-010). |
| `/quit` | Encerra a sessão sem marcar sucesso nem consumir dica adicional. |

## Saída ao encerrar

- Sucesso (testes passaram, ou `/done` confirmado): mensagem de sucesso + caminho do
  arquivo de log da sessão.
- Limite de dicas atingido: mensagem explicando o motivo (FR-009) + caminho do log.
- `/quit`: mensagem de encerramento manual + caminho do log.

## Código de saída (exit code)

- `0`: sessão encerrada por sucesso.
- `1`: sessão encerrada por limite de dicas ou `/quit`.
- `2`: erro de entrada (validação falhou antes de a sessão iniciar).
