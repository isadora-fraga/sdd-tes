# Relatório do Processo — Tutor Socrático de Programação (SDD)

## Ferramentas

- GitHub Spec Kit
- Claude Code — modelo Sonnet 5, modo "high", no VSCode
- Google Stitch — usado para gerar a UI; o código foi exportado e depois importado no
  projeto com adaptações

## Observações sobre o processo com a IA

- Bem interativo no início, mexia em vários arquivos da spec (constitution, spec, plan,
  tasks) conforme a conversa avançava.
- Definiu sozinha que o projeto não teria UI, sem me questionar antes.
- Se apegou bastante a não gastar chamada de API.
- Decidiu que o projeto só ia funcionar em Python, sozinha, sem me consultar.
- Esperava que fizesse mais perguntas; assumiu muita coisa sozinha — fez só 3 perguntas,
  e triviais.
- Amei que já pensou na validação, nos testes e nos cenários de uso.
- Também já pensou na inclusão de UI posteriormente.
- Achei a UI proposta muito ruim e básica, sem princípios de usabilidade — só aplicou
  heurísticas depois que eu pedi; tive que pedir pra adicionar botões de copiar/colar
  etc.
- Não pensou em tratar loop em caso de erros.
- Bug no modelo/fluxo da UI — pra resolver não foi um ato proativo (só corrigiu depois
  que eu reportei).
- Integração com a API do Gemini ruim: teve que ser ajustada umas três vezes; não tinha
  documentação sobre o modelo e nem pediu.
- Não pensou em situações de borda, tipo o usuário pedir 100000 dicas.
- Quando alterei coisas depois do desenvolvimento já pronto, não voltou a atualizar as
  specs mais.

## Resultado do teste comparativo (tutor vs. Gem vs. Gemini)

- Testando no meu tutor e num Gem com instruções similares, não consegui quebrar nenhum
  dos dois e conseguir uma resposta direta.
- Usando o Gemini direto (chat comum) ou o modo Learning, consegui.
- Ainda não vi a grande diferença entre o Gem e o meu projeto, mas serviu pra aprender o
  SDD.

## Melhorias de escopo já identificadas para trabalhos futuros

- Respostas do tutor muito básicas, sem citar COMO o estudante pode aprofundar o
  conteúdo.
- Parece que o contexto, mesmo dentro da mesma conversa, fica bem raso.
