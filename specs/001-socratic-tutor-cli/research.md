# Phase 0 Research: Tutor Socrático de Programação (CLI)

Todas as decisões técnicas de alto nível já foram confirmadas em conversa antes desta fase
(ver Technical Context em `plan.md`); este documento registra o racional e as alternativas
consideradas para cada uma, como exige o processo Spec Kit — não há itens em aberto
(`NEEDS CLARIFICATION`) nesta feature.

## 1. Execução dos testes do exercício

**Decision**: rodar os testes do exercício (quando existirem) localmente via
`subprocess.run(["pytest", ...])` sobre o código do aluno.

**Rationale**: o sistema já roda 100% local (Princípio V); `subprocess` + `pytest` não
exige nenhuma infraestrutura nova, é determinístico, e não depende de rede — ao contrário de
qualquer serviço remoto de execução de código.

**Alternatives considered**:
- *Google Colab*: descartado — não existe API pública para execução headless de código no
  Colab; a chave do Gemini não dá acesso a isso (produtos distintos do Google).
- *Ferramenta de "code execution" da API Gemini*: descartado para este propósito — é
  mediada pelo modelo (menos determinística), só roda Python com bibliotecas limitadas
  pré-instaladas (sem garantia de `pytest`), e geraria uma chamada de API adicional
  (conflita com o Princípio II).

## 2. Integração com a API Gemini

**Decision**: usar o SDK oficial `google-genai`, com um modelo da família "flash" (menor
custo/latência), solicitando **saída estruturada em JSON** (`response_schema`/modo JSON da
API) com os campos `question` (a pergunta orientadora) e `stage` (o estágio pedagógico
percebido pelo modelo, conforme decisão de regra de negócio documentada em FR-003 da spec).

**Rationale**: pedir JSON estruturado (em vez de texto livre) torna a extração do campo
`question` e a aplicação da guarda (item 3 abaixo) mais confiável e testável — evita ter que
fazer parsing heurístico de texto livre para separar "a pergunta" do resto da resposta.
Também é o mecanismo mais simples de obter a classificação de estágio sem uma segunda
chamada de API, alinhado ao Princípio II.

**Alternatives considered**:
- *Texto livre sem schema*: mais simples de prototipar, mas mistura a pergunta com possível
  texto extra do modelo, dificultando a guarda e a extração do estágio de forma confiável.
- *Chamada separada só para classificar o estágio*: mais determinístico por etapa, porém
  dobra o número de chamadas de API por rodada — rejeitado pelo Princípio II.

## 3. Guarda anti-solução (Princípio I)

**Decision**: verificação determinística em código (não apenas instrução de prompt) sobre o
campo `question` da resposta estruturada, usando heurísticas: (a) presença de blocos de
código cercados (```) contendo estruturas de função/programa completas (ex.: `def`, `class`,
múltiplas linhas com lógica executável), (b) presença de instruções imperativas diretas de
resolução (ex.: padrões como "a resposta é", "basta copiar", "troque a linha X por..."), e
(c) ausência de qualquer sinal de interrogação/formato de pergunta. Se qualquer heurística
disparar, a resposta é descartada.

**Rationale**: uma checagem em prompt (pedir educadamente ao modelo para não responder com
a solução) não é uma garantia — é só uma sugestão que o modelo pode ignorar sob certas
entradas. A verificação precisa ser código, testável isoladamente com uma bateria de
respostas simuladas (contract tests), conforme o próprio Princípio I exige.

**Alternatives considered**:
- *Confiar apenas no prompt de sistema*: rejeitado — é exatamente o que diferenciaria esta
  ferramenta de um simples "Gem" personalizado, e a spec exige uma guarda verificável.
  Este ponto já foi discutido e é o motivo central do projeto.
- *Usar um segundo modelo/chamada de IA como "juiz" da resposta*: mais robusto contra casos
  extremos, porém dobra o custo de API por rodada — rejeitado pelo Princípio II para o
  escopo deste trabalho.

## 4. Logging estruturado

**Decision**: um arquivo por sessão, em formato JSON Lines (uma linha = um objeto JSON = uma
rodada), escrito em modo append-only.

**Rationale**: simples de gerar e de reprocessar depois (cada linha é independente,
tolerante a leitura parcial), sem exigir schema de banco de dados nem dependências
adicionais — alinhado aos Princípios IV e V.

**Alternatives considered**:
- *Banco de dados (SQLite, etc.)*: melhor para consultas complexas futuras, mas
  desnecessário para o volume de dados de uma sessão de exercício e conflita com o
  Princípio V (sem infraestrutura adicional a menos que necessária).
- *Um único arquivo de log global para todas as sessões*: mais simples de achar um único
  arquivo, mas dificulta isolar/descartar sessões de teste da pesquisa; um arquivo por
  sessão foi preferido para manter o dado de pesquisa organizado por unidade de análise
  (a sessão).

## 5. Camada web local (User Story 5 / FR-015)

**Decision**: `Flask` como framework mínimo, servindo uma única página com formulário
(enunciado + código) e endpoints que chamam diretamente os mesmos `services/` usados pela
CLI.

**Rationale**: é a opção com menor footprint de dependências para expor uma interação
request/response simples localmente, sem exigir build de frontend (bundlers, frameworks
JS) — coerente com o Princípio V. Por ser só uma camada de apresentação, não introduz
nenhuma regra de negócio nova.

**Alternatives considered**:
- *FastAPI + servidor ASGI*: mais adequado a APIs assíncronas/maiores, desnecessário para
  uma única página local de demonstração.
- *`http.server` da biblioteca padrão, sem framework*: zero dependências externas, mas exige
  escrever manualmente roteamento e parsing de formulário — mais código para o mesmo
  resultado; Flask foi preferido por reduzir código de infraestrutura em favor do tempo
  gasto na lógica de negócio (que é o que importa para o exercício de SDD).
