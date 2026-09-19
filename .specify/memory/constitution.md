<!--
Sync Impact Report
Version change: 1.0.0 → 1.1.0
Modified principles: V. Radical Simplicity (One-Day Scope) → V. Radical Simplicity
  (removed the one-day timeframe framing from governance text; the constraint now speaks
  only to being basic/simple, not to a specific delivery timeframe)
Added sections:
  - Scope & Technology Constraints: added a paragraph putting a basic, no-auth local web UI
    in scope, for demonstration/comparison purposes, explicitly reusing the CLI's business
    logic and remaining subject to Principle V
Removed sections: none
Templates requiring follow-up: none — plan/spec/tasks templates consume this file at runtime and
  need no edits themselves.
Deferred TODOs: none
-->

# Tutor Socrático de Programação — Constitution

## Core Principles

### I. Socratic-Only Responses (NON-NEGOTIABLE)
O agente de IA NUNCA deve entregar a solução direta do exercício — nem código completo,
nem funcional, nem pseudocódigo que resolva o problema. Toda resposta ao aluno DEVE ser
formulada como uma pergunta orientadora (estilo socrático) que o conduza a encontrar a
solução por conta própria. Toda saída do modelo DEVE passar por uma checagem/guarda
programática antes de ser exibida ao aluno (ex.: detectar blocos de código executáveis,
funções completas, ou instruções imperativas de "faça X"); se a guarda disparar, a
resposta é descartada e o sistema deve pedir nova geração ou usar um fallback textual
fixo. Não é aceitável confiar apenas na instrução dada ao modelo via prompt — a garantia
precisa ser verificável em código.
**Racional**: este é o requisito pedagógico central do projeto (baseado em evidência de
que respostas diretas de IA reduzem pensamento crítico e geram over-reliance); é também o
que diferencia esta ferramenta de um simples chat de propósito geral com um prompt de
sistema — aqui a regra é reforçada por software, não apenas sugerida ao modelo.

### II. Cost-Conscious API Usage
O uso da API do Gemini DEVE ser econômico por padrão. Isso significa: usar o modelo mais
barato disponível adequado à tarefa (ex.: variante "flash"), nunca reenviar o histórico
completo da conversa quando um resumo/estado reduzido for suficiente, limitar o tamanho de
prompt e de contexto enviado, e impor um limite explícito de chamadas por exercício/sessão
(ex.: número máximo de dicas antes de encerrar o ciclo). Qualquer funcionalidade que exija
aumento relevante de chamadas ou contexto DEVE justificar o custo adicional antes de ser
implementada.
**Racional**: restrição explícita do usuário/orçamento do projeto; também força um design
mais simples e mais alinhado ao escopo de um agente único (Princípio V).

### III. Structured Pedagogical State
O sistema DEVE manter um estado pedagógico simples e explícito por exercício/aluno (ex.:
estágio atual — não entendeu o enunciado, erro de sintaxe, erro de lógica, bloqueio
conceitual —, e contagem de dicas já fornecidas). Esse estado é o que determina o tipo de
pergunta socrática gerada a cada rodada; ele DEVE ser inspecionável (não pode viver apenas
implícito dentro do prompt de conversa) e DEVE evoluir de forma determinística e testável
a partir das interações do aluno.
**Racional**: é o que torna o comportamento do agente auditável e testável via SDD (specs
podem descrever transições de estado como critérios de aceite), em vez de depender do
comportamento emergente e não determinístico de um chat livre.

### IV. Research-Grade Logging
Toda interação relevante (prompt enviado, resposta do agente, estágio pedagógico no
momento, resultado de testes automatizados quando aplicável) DEVE ser registrada de forma
estruturada (ex.: JSON Lines ou equivalente), com timestamp, de modo a viabilizar análise
posterior. O log é um artefato de pesquisa, não apenas depuração: seu formato DEVE ser
estável e documentado o suficiente para permitir reprocessamento automatizado.
**Racional**: este projeto é um artefato inicial de uma investigação de doutorado sobre
arquiteturas multiagente em educação de programação; os dados coletados aqui (mesmo em
escala pequena) precisam ser reaproveitáveis para análise futura.

### V. Radical Simplicity
O sistema DEVE permanecer básico e simples: interfaces mínimas (CLI e, quando presente, uma
aplicação web local simples), execução local, sem exigência de deploy em nuvem, sem sistema
de autenticação/autorização complexo, sem persistência além do necessário para logging e
estado pedagógico (Princípios III e IV), e sem infraestrutura adicional (filas, múltiplos
serviços, containers orquestrados) a menos que estritamente necessária. Qualquer elemento
de complexidade adicional DEVE ser justificado explicitamente contra este princípio antes
de entrar no plano de implementação.
**Racional**: o objetivo do trabalho é praticar corretamente o processo de Spec-Driven
Development (constitution → specify → clarify → plan → tasks → implement) em um sistema
pequeno mas real, com regras de negócio testáveis — não produzir um produto polido ou um
sistema de produção.

## Scope & Technology Constraints

Este projeto é o primeiro artefato de escopo reduzido dentro de uma linha de pesquisa
sobre arquiteturas multiagente para apoio educacional em programação; ele implementa
deliberadamente um único agente (o tutor socrático), não a arquitetura multiagente final
da pesquisa. Extensões futuras (múltiplos agentes especializados, comparação
single-agent vs. multi-agent) estão fora do escopo deste trabalho e não devem ser
antecipadas na implementação além do necessário para não contradizer os Princípios I–V.

A integração de IA usa a API do Gemini como único provedor. O sistema é destinado a
exercícios de programação introdutória (CS1/CS2): entrada mínima esperada é um enunciado
de exercício, o código atual do aluno e, quando disponível, o resultado de testes
automatizados sobre esse código.

Além da interface de linha de comando (CLI), o escopo inclui uma interface web local básica
e sem autenticação, cuja única finalidade é permitir a demonstração/apresentação do
trabalho (incluindo comparação lado a lado com um assistente de IA genérico sem as guardas
deste projeto). Essa interface web NÃO introduz regras de negócio próprias: ela reutiliza
integralmente a lógica definida para a CLI e permanece sujeita ao Princípio V.

## Development Workflow (SDD Process)

O desenvolvimento segue o fluxo padrão do Spec Kit: `/speckit-constitution` (este
documento) → `/speckit-specify` → `/speckit-clarify` → `/speckit-plan` → `/speckit-tasks`
→ `/speckit-implement`. Cada especificação e plano gerados a partir daqui DEVEM ser
verificados contra os Princípios I–V antes de avançar para a fase seguinte; qualquer
desvio precisa ser justificado explicitamente no próprio artefato (spec ou plano), não
apenas decidido silenciosamente durante a implementação.

Critérios de aceite relacionados ao Princípio I (nunca revelar solução direta) DEVEM ser
expressos como casos de teste verificáveis (ex.: dado um conjunto de respostas simuladas
do modelo contendo código-solução, o guard DEVE rejeitá-las) antes de a funcionalidade ser
considerada concluída.

## Governance

Esta constitution tem precedência sobre preferências de implementação individuais dentro
deste projeto. Emendas requerem: registro do motivo da mudança, atualização do número de
versão conforme versionamento semântico (MAJOR para remoção/redefinição incompatível de
princípios, MINOR para adição de princípio ou seção, PATCH para clarificações), e
atualização da data de última emenda. Toda revisão de spec, plano ou tarefas DEVE verificar
conformidade com os Princípios I–V; complexidade adicional não justificada explicitamente
contra o Princípio V (Radical Simplicity) deve ser rejeitada ou simplificada antes de
prosseguir.

**Version**: 1.1.0 | **Ratified**: 2026-09-19 | **Last Amended**: 2026-09-19
