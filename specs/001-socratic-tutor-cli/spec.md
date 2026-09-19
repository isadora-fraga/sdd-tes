# Feature Specification: Tutor Socrático de Programação (CLI)

**Feature Branch**: `001-socratic-tutor-cli`

**Created**: 2026-09-19

**Status**: Draft

**Input**: User description: "Um aluno de programação (CS1/CS2) interage via linha de comando (CLI) com um tutor de IA (Gemini) enquanto resolve um exercício de código. O sistema roda os testes do exercício contra o código do aluno, classifica um estágio pedagógico, envia ao modelo um pedido de pergunta orientadora (nunca a solução), verifica a resposta antes de exibi-la, registra cada rodada em log estruturado, e encerra a sessão por sucesso (testes passam) ou por limite de dicas atingido."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Receber orientação socrática em vez da solução (Priority: P1)

Um aluno está travado em um exercício de programação. Ele fornece o enunciado do exercício
e seu código atual ao tutor. Em vez de receber o código corrigido, ele recebe uma pergunta
que o guia a pensar sobre o próprio erro.

**Why this priority**: É o valor central do produto e o critério de sucesso do trabalho —
sem essa garantia, a ferramenta é indistinguível de qualquer chat de IA genérico.

**Independent Test**: Pode ser testado isoladamente fornecendo um enunciado e um código com
um erro conhecido, e verificando que (a) uma pergunta é exibida, nunca uma solução, e (b)
se o modelo de IA for forçado (em teste) a retornar uma resposta contendo código-solução,
o sistema a rejeita e exibe uma pergunta de fallback no lugar.

**Acceptance Scenarios**:

1. **Given** um enunciado de exercício e um código do aluno com um erro, **When** o aluno
   inicia uma rodada de orientação, **Then** o sistema exibe uma pergunta orientadora
   relacionada ao erro, sem exibir código-solução completo ou instruções diretas de "faça X".
2. **Given** uma resposta do modelo de IA que contém um bloco de código-solução completo,
   **When** o sistema avalia essa resposta antes de exibi-la, **Then** o sistema descarta a
   resposta, tenta gerar novamente até o limite de tentativas, e caso todas falhem, exibe uma
   pergunta de fallback fixa pré-definida em vez da resposta rejeitada.
3. **Given** um código do aluno que já passa em todos os testes do exercício, **When** o
   aluno inicia uma rodada, **Then** o sistema não solicita pergunta ao modelo e encerra a
   sessão imediatamente informando sucesso.
4. **Given** um exercício sem testes automatizados associados, **When** o modelo avalia o
   código como aparentemente correto, **Then** o sistema exibe essa avaliação qualitativa,
   orienta o aluno a verificar por conta própria (rodando o código/compilador), e mantém a
   sessão aberta até o aluno emitir um comando explícito de encerramento confirmando que
   está satisfeito.

---

### User Story 2 - Progredir através de rodadas com estado pedagógico (Priority: P2)

Um aluno interage em várias rodadas: recebe uma pergunta, tenta responder ou ajustar o
código, e reenvia. A cada rodada, a pergunta deve refletir em que ponto o aluno está
(travado no enunciado, erro de sintaxe, erro de lógica, ou bloqueio conceitual) e quantas
dicas já foram dadas nesta sessão, evitando perguntas repetitivas ou desconectadas do
progresso real do aluno.

**Why this priority**: Sem estado pedagógico, o sistema seria apenas um gerador de
perguntas aleatórias e sem noção de progresso — a diferenciação de um "estado" é o que
permite tratar isso como um sistema com regras de negócio testáveis (não um chat livre).

**Independent Test**: Pode ser testado isoladamente simulando duas rodadas seguidas com
resultados de teste diferentes (ex.: primeira rodada com erro de execução, segunda rodada
com testes falhando por lógica incorreta) e verificando que o estágio pedagógico registrado
muda de acordo, e que a contagem de dicas incrementa a cada rodada.

**Acceptance Scenarios**:

1. **Given** uma sessão em andamento com 1 dica já fornecida, **When** o aluno reenvia
   código atualizado que ainda falha nos mesmos testes, **Then** o sistema incrementa a
   contagem de dicas e ajusta o estágio pedagógico com base no novo resultado de testes.
2. **Given** um código que não executa (erro de sintaxe/execução), **When** o sistema
   classifica o estágio, **Then** o estágio refletido difere do estágio usado quando o
   código executa mas os testes falham por resultado incorreto (erro de lógica).

---

### User Story 3 - Encerrar a sessão de forma clara ao atingir o limite de dicas (Priority: P3)

Um aluno continua sem resolver o exercício após várias rodadas. Ao atingir o número máximo
de dicas permitido para a sessão, o sistema informa isso claramente e encerra o ciclo, sem
fazer novas chamadas à API de IA e sem repetir perguntas indefinidamente.

**Why this priority**: Garante o princípio de uso econômico da API (custo previsível) e
evita uma experiência ruim de loop sem fim — mas depende de US1/US2 já existirem para fazer
sentido, por isso vem depois na prioridade.

**Independent Test**: Pode ser testado isoladamente configurando um limite baixo de dicas
(ex.: 1) e verificando que, após esse número de rodadas sem sucesso, o sistema exibe uma
mensagem de encerramento por limite e a sessão termina sem novas chamadas à API.

**Acceptance Scenarios**:

1. **Given** uma sessão que atingiu o número máximo de dicas configurado, **When** o aluno
   tenta iniciar mais uma rodada, **Then** o sistema informa que o limite foi atingido,
   encerra a sessão, e não realiza nenhuma chamada adicional à API de IA.

---

### User Story 4 - Registrar cada rodada para análise de pesquisa (Priority: P4)

Cada rodada de interação (prompt enviado, resposta do modelo, se a resposta foi rejeitada
pela verificação, estágio pedagógico, resultado dos testes, carimbo de tempo) é registrada
em um arquivo de log estruturado, permitindo reprocessamento posterior para fins de
pesquisa.

**Why this priority**: Importante para o objetivo de pesquisa por trás do projeto, mas não
afeta a experiência do aluno durante a sessão — pode ser adicionado por último sem
comprometer o valor entregue pelas histórias anteriores.

**Independent Test**: Pode ser testado isoladamente executando uma sessão completa e
verificando que o arquivo de log contém uma entrada por rodada, com todos os campos
esperados presentes e em formato consistente entre entradas.

**Acceptance Scenarios**:

1. **Given** uma sessão com múltiplas rodadas, **When** a sessão é concluída (por sucesso
   ou por limite de dicas), **Then** o arquivo de log contém uma entrada estruturada para
   cada rodada ocorrida, incluindo os casos em que a verificação rejeitou uma resposta.

---

### User Story 5 - Demonstrar a sessão por uma interface web local básica (Priority: P5)

Para apresentar o trabalho, é preciso mostrar a interação de forma visual e comparar lado a
lado com um assistente de IA genérico (ex.: um Gem personalizado com apenas um prompt de
persona socrática). Uma interface web mínima, rodando localmente e sem login, expõe os
mesmos campos de entrada (enunciado, código) e o mesmo diálogo de perguntas já usados na
CLI.

**Why this priority**: Não agrega uma regra de negócio nova (reaproveita inteiramente a
lógica das Histórias 1–4); serve para a apresentação e para evidenciar visualmente a
diferença entre a guarda programática deste sistema e um chat de IA sem essas garantias.
Por isso vem por último na priorização.

**Independent Test**: Pode ser testado isoladamente abrindo a interface web local, iniciando
uma sessão com o mesmo enunciado/código de um caso de teste da CLI, e verificando que o
comportamento observado (pergunta em vez de solução, estágio, limite de dicas) é idêntico ao
da CLI para a mesma entrada.

**Acceptance Scenarios**:

1. **Given** a interface web local rodando, **When** um visitante acessa a página sem
   necessidade de login, **Then** ele consegue iniciar uma sessão, enviar enunciado e
   código, e visualizar o diálogo de perguntas da mesma forma que na CLI.
2. **Given** a mesma entrada (enunciado + código) usada em uma sessão de CLI que foi
   bloqueada pela verificação (guard), **When** essa entrada é usada na interface web,
   **Then** o mesmo bloqueio ocorre e a mesma pergunta de fallback é exibida.

---

### Edge Cases

- O que acontece quando o aluno fornece um enunciado vazio ou um código vazio? O sistema
  deve rejeitar a entrada com uma mensagem clara, sem consumir uma chamada de dica.
- O que acontece quando o aluno submete código em outra linguagem (não Python)? O sistema
  rejeita localmente antes de qualquer chamada de IA (ver FR-016), sem consumir dica.
- O que acontece quando o enunciado não tem relação alguma com um exercício de programação?
  Fora de escopo validar isso semanticamente (exigiria uma chamada de IA extra só para
  julgar relevância, o que fere o Princípio II) — o sistema confia no uso pretendido pelo
  aluno, por ser uma ferramenta de uso pessoal/local, não um serviço público exposto a
  abuso em massa (ver Assumptions).
- O que acontece quando o exercício não possui testes automatizados associados? O sistema
  não encerra automaticamente por sucesso; ele pede ao modelo uma avaliação qualitativa,
  orienta o aluno a verificar por conta própria, e aguarda um comando explícito de
  encerramento do aluno (ver FR-014).
- O que acontece quando a chamada à API de IA falha (erro de rede, timeout, chave inválida,
  limite de uso da conta excedido)? O sistema deve informar o erro claramente ao aluno e
  encerrar a rodada atual sem travar a sessão nem consumir uma dica.
- O que acontece quando todas as tentativas de gerar uma pergunta válida são rejeitadas pela
  verificação (guard) e o fallback fixo também já foi usado na rodada anterior? O sistema
  deve continuar funcional (reutilizar o fallback ou um conjunto pequeno de fallbacks
  rotativos), nunca travar ou encerrar abruptamente sem mensagem.
- O que acontece se o código do aluno for extremamente longo (acima do que é razoável
  incluir em um prompt)? O sistema deve truncar ou resumir de forma sinalizada ao aluno,
  nunca falhar silenciosamente.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST permitir que o aluno inicie uma sessão de exercício fornecendo
  o enunciado do exercício e o código atual (por colagem direta de texto ou por referência a
  um arquivo local).
- **FR-002**: O sistema MUST executar os testes automatizados associados ao exercício
  (quando fornecidos) contra o código atual do aluno e capturar quais passam e quais falham.
- **FR-003**: O sistema MUST classificar, a cada rodada, um estágio pedagógico da sessão a
  partir de um conjunto fixo e pequeno de estágios (ex.: não entendeu o enunciado, erro de
  sintaxe/execução, erro de lógica, bloqueio conceitual), combinado com a contagem de dicas
  já fornecidas. Essa classificação MUST ser feita pelo próprio modelo de IA, como parte do
  mesmo pedido que já gera a pergunta orientadora (sem uma chamada de API adicional só para
  classificar o estágio).
  > **Decisão de regra de negócio (deliberada para este trabalho)**: delega-se ao modelo de
  > IA o julgamento do estágio pedagógico, em vez de um motor de regras determinístico
  > baseado apenas no resultado dos testes. Isso reduz a complexidade de implementação e
  > evita uma segunda chamada de API (alinhado ao princípio de uso econômico), ao custo
  > consciente de menor determinismo/testabilidade dessa classificação específica — esse
  > trade-off é aceito intencionalmente no escopo deste projeto.
- **FR-004**: O sistema MUST solicitar ao modelo de IA, a cada rodada, exclusivamente uma
  pergunta orientadora (nunca uma solução), incluindo no pedido o enunciado, o código atual,
  o resultado dos testes (quando existir) e o estágio pedagógico/contagem de dicas.
- **FR-005**: O sistema MUST verificar programaticamente cada resposta do modelo antes de
  exibi-la ao aluno, rejeitando qualquer resposta que contenha código-solução completo ou
  executável, ou instruções imperativas diretas que resolvam o exercício.
- **FR-006**: O sistema MUST, quando a verificação rejeitar uma resposta, tentar gerar
  novamente até um número máximo de tentativas antes de recorrer a uma pergunta de fallback
  fixa e pré-definida (nunca deixar o aluno sem resposta).
- **FR-007**: O sistema MUST exibir a pergunta orientadora (ou o fallback) ao aluno no
  terminal e aguardar nova entrada do aluno (resposta em texto e/ou código atualizado) antes
  de iniciar a próxima rodada.
- **FR-008**: O sistema MUST impor um limite máximo de dicas (rodadas com chamada à API de
  IA) por sessão de exercício, configurável por parâmetro de linha de comando ao iniciar a
  sessão; quando não especificado, o valor padrão MUST ser 5 dicas por sessão.
- **FR-009**: O sistema MUST, ao atingir o limite de dicas, encerrar a sessão informando
  claramente o aluno sobre o motivo do encerramento, sem realizar novas chamadas à API de IA
  e sem repetir o ciclo indefinidamente.
- **FR-010**: O sistema MUST encerrar a sessão com uma mensagem de sucesso assim que os
  testes do exercício passarem integralmente, sem exigir dicas adicionais além do
  necessário.
- **FR-011**: O sistema MUST registrar cada rodada em um arquivo de log estruturado (uma
  entrada por rodada), contendo no mínimo: prompt enviado ao modelo, resposta recebida, se a
  resposta foi rejeitada pela verificação, estágio pedagógico da rodada, resultado dos
  testes (quando aplicável) e carimbo de tempo.
- **FR-012**: O sistema MUST tratar falhas de comunicação com a API de IA (erro, timeout,
  limite excedido) exibindo uma mensagem clara ao aluno e permitindo encerrar ou tentar
  novamente a rodada, sem travar a sessão nem corromper o log.
- **FR-013**: O sistema MUST operar sobre exercícios em uma única linguagem de programação
  por sessão (Python, com testes automatizados no formato pytest ou equivalente simples),
  sem necessidade de suportar múltiplas linguagens simultaneamente nesta versão.
- **FR-014**: Quando o exercício não possui testes automatizados associados, o sistema MUST
  pedir ao modelo de IA uma avaliação qualitativa do código em relação ao enunciado (ex.:
  "parece consistente com o que foi pedido"), sem nunca revelar a solução, e MUST instruir
  explicitamente o aluno a verificar por conta própria (rodando o código, testando no
  compilador/interpretador ou no restante do projeto) antes de decidir se está satisfeito.
  Nesse cenário, o sistema NÃO MUST encerrar a sessão por sucesso automaticamente; a sessão
  só é encerrada como sucesso quando o próprio aluno emitir um comando explícito de
  encerramento (ex.: `/done`) confirmando que verificou e está satisfeito com o resultado.
- **FR-015**: O sistema MUST oferecer, além da CLI, uma interface web local básica e sem
  autenticação, que exponha a mesma interação (enunciado, código, diálogo de perguntas) e
  reutilize integralmente as regras de negócio já definidas (FR-001 a FR-014), destinada a
  fins de demonstração/apresentação do trabalho.
- **FR-016**: Antes de enviar qualquer conteúdo à API de IA, o sistema MUST validar
  localmente (sem chamada de IA) se o código submetido é sintaticamente válido na linguagem
  suportada (Python, conforme FR-013); se a validação falhar, o sistema MUST rejeitar a
  submissão com uma mensagem clara pedindo código Python válido, sem consumir uma dica e
  sem realizar nenhuma chamada à API nessa rodada.

### Key Entities *(include if feature involves data)*

- **Sessão de Exercício**: representa uma tentativa do aluno de resolver um exercício
  específico; agrega o enunciado, o código atual, o histórico de rodadas, o estágio
  pedagógico corrente, a contagem de dicas usadas e o motivo de encerramento (sucesso ou
  limite atingido).
- **Rodada**: uma iteração dentro de uma sessão; contém o código submetido naquele momento,
  o resultado dos testes, o estágio pedagógico calculado, o prompt enviado ao modelo, a
  resposta recebida, se a verificação rejeitou essa resposta, e o carimbo de tempo.
- **Registro de Log**: representação persistida e estruturada de uma Rodada, destinada à
  análise posterior fora do sistema (não é consultada pelo próprio sistema durante a
  sessão).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% das rodadas de uma sessão, nenhuma resposta exibida ao aluno contém
  uma solução completa e executável para o exercício (verificado por revisão manual de uma
  amostra de sessões de teste).
- **SC-002**: Um aluno consegue completar uma sessão inteira (do início até sucesso ou até
  o limite de dicas) sem que o sistema trave, quebre ou fique sem resposta em nenhuma
  rodada.
- **SC-003**: 100% das sessões executadas geram um arquivo de log completo e consistente,
  com uma entrada por rodada realizada, verificável por reprocessamento automatizado do
  arquivo.
- **SC-004**: O número de chamadas à API de IA por sessão nunca ultrapassa o limite
  configurado, mesmo em cenários com múltiplas tentativas de verificação rejeitadas.
- **SC-005**: É possível, usando a interface web local, demonstrar lado a lado uma sessão
  desta ferramenta e uma conversa equivalente em um assistente de IA genérico (ex.: um Gem
  personalizado), evidenciando de forma visual a diferença de comportamento entre as duas
  abordagens (perguntas orientadoras com guarda vs. respostas diretas sem garantias).

## Assumptions

- A linguagem-alvo dos exercícios nesta primeira versão é Python, com testes automatizados
  no formato pytest (ou equivalente simples de rodar via linha de comando).
- O aluno interage em uma sessão de cada vez, sem suporte a múltiplos alunos simultâneos ou
  autenticação — o escopo é uso individual local (conforme constitution, Radical
  Simplicity).
- O aluno pode fornecer o código tanto colando o conteúdo diretamente no terminal quanto
  apontando para um caminho de arquivo local; ambas as formas são aceitas.
- O arquivo de log é local (ex.: arquivo em disco no formato JSON Lines), sem necessidade de
  banco de dados, conforme constitution.
- O número máximo de tentativas de regeneração após a verificação rejeitar uma resposta
  (antes de usar o fallback fixo) é pequeno (ex.: 1–2 tentativas), para não conflitar com o
  princípio de uso econômico da API; cada tentativa de regeneração conta como uma chamada de
  API para fins do limite de dicas/chamadas da sessão (FR-008).
- A interface web local (User Story 5 / FR-015) é uma camada de apresentação sobre a mesma
  lógica de negócio da CLI, sem persistência ou autenticação próprias, e não implementa
  nenhuma regra nova além das já definidas em FR-001 a FR-014.
- O comando de encerramento manual do aluno (ex.: `/done`, usado em FR-014 quando não há
  testes automatizados) é um comando literal reconhecido tanto pela CLI quanto pela
  interface web.
- Não há validação semântica do enunciado (se ele de fato descreve um exercício de
  programação): esta ferramenta é de uso pessoal/local por um único aluno por vez, não um
  serviço público, então esse tipo de moderação de conteúdo foi deliberadamente deixado
  fora de escopo (ver Edge Cases).
