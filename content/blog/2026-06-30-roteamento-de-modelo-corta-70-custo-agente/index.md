---
title: "Você está rodando tudo no modelo mais caro: rotear por papel corta 60-70% da conta do agente"
slug: roteamento-de-modelo-corta-70-custo-agente
date: 2026-06-30
publishDate: 2026-06-30
draft: false
description: "Num swarm de agentes, só a decisão irreversível justifica o frontier. O resto é coordenação, implementação e transformação de artefato. Cobrar Opus por isso é inverter a prioridade de gasto."
tags: ["engenharia-de-dados"]
images:
  - cover.png
---
A pergunta que ninguém faz quando monta um sistema multi-agente é a mais cara: qual modelo roda cada agente?

A resposta padrão é silenciosa e devastadora. Você abre a sessão no modelo mais forte que tem, e cada sub-agente que ela dispara herda esse modelo por inércia. O agente que escreve o runbook final roda no mesmo nível de raciocínio que o agente que decide a arquitetura do data lake. Você está pagando preço de cirurgião para alguém preencher um formulário.

Quando montei minha squad de engenharia de dados com 16 agentes, essa foi a primeira conta que me incomodou.

## O custo mora no agente, não na chamada

> Em uma frase: num swarm hierárquico, a maior parte do volume de tokens é coordenação e implementação rotineira, e rodar isso no modelo de fronteira é desperdício puro.

Deixa eu separar de um post anterior que escrevi sobre prompt caching, porque é fácil confundir. Caching ataca o **prefixo**: você reaproveita o pedaço repetido do prompt (system prompt, contexto, documentos) e paga uma fração na releitura. É um eixo. Roteamento de modelo ataca outro eixo completamente diferente: **qual cérebro** processa cada tarefa. Caching deixa a mesma chamada mais barata. Roteamento escolhe não usar o cérebro de R$ 25 quando o de R$ 5 entrega igual.

Os dois se somam. Mas confundir um com o outro faz você otimizar metade do problema e achar que terminou.

A conta de modelo na API da Anthropic deixa o desperdício gritante. Os preços públicos hoje:

| Modelo | Input (US$/M tokens) | Output (US$/M tokens) |
|---|---|---|
| Opus 4.8 | 5,00 | 25,00 |
| Sonnet 4.6 | 3,00 | 15,00 |
| Haiku 4.5 | 1,00 | 5,00 |

Output do Opus custa 5x o output do Haiku. Se metade do seu swarm é gente escrevendo documento final, handoff e runbook (trabalho de transformação de conteúdo já decidido), você está pagando 5x a mais por token de saída em tarefa que o Haiku faz com qualidade suficiente. Multiplica isso por milhares de execuções no mês e a fatura para de ser ruído.

## A decisão: 16 agentes roteados por tipo de trabalho cognitivo

O princípio que adotei tem nome na literatura de swarm: Heterogeneous Agentic Mesh, ou Executive-Worker. O Executive (modelo de fronteira) decide. Os Workers (modelos menores) executam. A regra que escrevi para a minha squad foi: **cada agente declara explicitamente o modelo que o roda, segundo o tipo de trabalho cognitivo do papel**, e essa declaração tem que casar entre o frontmatter do agente e o registro de auditoria que ele emite. Se houver divergência, o gate da fase trava.

Classifiquei o trabalho em três tipos:

| Tipo de trabalho | Modelo | Por quê |
|---|---|---|
| Decisão irreversível (framing, arquitetura, gate de segurança) | Opus | Erro contamina a cadeia inteira ou viola compliance. Vale a capacidade máxima. |
| Coordenação e implementação estruturada (quebrar issues, código padrão, IaC) | Sonnet | Padrão definido, exige consistência, não exige fronteira de raciocínio. |
| Transformação de artefato pronto (doc final, runbook, handoff) | Haiku | Conteúdo já decidido. Velocidade e custo importam, raciocínio não. |

Na prática isso virou 4 Opus, 10 Sonnet, 2 Haiku. Quem ganhou Opus na minha squad:

- O **product owner**, que faz o framing do problema. Erro no PRD contamina arquitetura, plano e código depois. É a decisão mais a montante de todas.
- O **arquiteto de dados**, que decide Medallion, particionamento e governança. São escolhas irreversíveis, viram registro permanente.
- O **engenheiro de IA**, que decide arquitetura de RAG, multi-agente e guardrails.
- O **revisor de QA e segurança**, último gate antes do deploy. Falso negativo aqui é crítico.

Repara no critério. Não é "esse agente é importante". Todo agente é importante, senão eu não o teria. O critério é: **o erro desse papel é reversível?** Se o arquiteto erra o particionamento, eu reprocesso terabytes e refaço pipeline. Se o tech writer erra uma frase no runbook, eu corrijo a frase. Custos de erro em ordens de grandeza diferentes justificam modelos em ordens de grandeza de preço diferentes.

Os 10 Sonnet são o corpo do trabalho: gerente de projeto quebrando issues, desenvolvedores Python e PySpark implementando transformações, os agentes de discovery varrendo a ideia em fan-out paralelo, os reasoners explorando opções de arquitetura. Trabalho estruturado, padrão claro, qualidade alta sem precisar da fronteira.

Os 2 Haiku são o tech writer e o crítico de QA, que aplica um checklist fixo sobre um relatório já consolidado. Crítica de artefato pronto, não decisão de gate.

## O frontmatter como contrato de custo

A parte que torna isso real, e não uma boa intenção, é que a escolha de modelo virou um campo versionado e auditável. No agente:

```yaml
---
name: data-architect
tools: Read, Write, Edit, Grep, Glob
version: v1.1.0
model: opus
---
```

E o agente, ao terminar, registra no envelope de auditoria qual modelo de fato o rodou. Se o orquestrador detecta que o frontmatter diz Opus e o envelope diz Sonnet, ele trava até eu confirmar. Isso fecha o buraco clássico: alguém edita um agente, esquece o campo de modelo, e três meses depois você descobre que metade do swarm migrou pro modelo errado e ninguém viu na fatura.

A tabela não é eterna. Eu deixei escrito que ela se reavalia quando um agente acumular evidência de subperformance no modelo atribuído, ou quando a Anthropic lançar geração que mude a fronteira preço/capacidade. Mas mudar exige argumento explícito no commit. Não vale "achei melhor". Vale "vi esse artefato falhar X vezes no Haiku".

## Por que isso importa pra fatura em reais

O ponto que conecta com a realidade de quem paga conta de cloud no Brasil: custo de LLM em produção é despesa recorrente em dólar, e dólar não para de subir. Cada agente que você sobe de tier sem precisar é multiplicador na fatura de fim de mês, convertida no câmbio do dia.

A literatura de swarm de 2026 aponta cortes na casa de 60 a 70% no custo de token quando a escolha de modelo respeita o tipo de trabalho de cada papel, sem perder qualidade nas decisões que importam. Não é número que eu medi na minha squad (ela é blueprint, não roda volume de produção ainda), é a faixa que a literatura do padrão reporta, e por isso eu a trato como estimativa de mercado. O mecanismo, porém, é aritmético: se 12 dos 16 agentes saíram de Opus para Sonnet ou Haiku, e Sonnet custa 60% do Opus enquanto Haiku custa 20%, o agregado cai sozinho. A única pergunta é se a qualidade segura, e ela segura desde que a decisão irreversível continue no frontier.

Vale uma ressalva honesta sobre um número que circula muito. O relatório do MIT (Project NANDA, "State of AI in Business 2025") encontrou que 95% dos pilotos de IA generativa em empresas não geram retorno mensurável, baseado em mais de 300 implementações. O dado é real, mas a causa que o relatório aponta é o "learning gap" e a má integração ao workflow, não disciplina de custo. Então eu não atribuo os 95% a custo, porque o MIT não atribui. O que eu afirmo, por engenharia, é mais modesto: um sistema cuja economia não fecha não sobrevive ao corte de orçamento do ano seguinte, por melhor que seja tecnicamente. Disciplina de custo é condição de sobrevivência, não de elegância.

## Anti-padrões

- **Abrir a sessão no modelo mais forte e deixar todo sub-agente herdar.** É o default silencioso. Você nunca decidiu rodar o tech writer no Opus, simplesmente nunca decidiu o contrário.
- **Rotear por "importância" do agente em vez de reversibilidade do erro.** Todo agente é importante. A pergunta certa é o custo de errar, não o prestígio do papel.
- **Deixar a escolha de modelo implícita no código.** Se não está num campo versionado e auditável, ela vai derivar sem ninguém ver, e você descobre na fatura.
- **Confundir roteamento com caching.** São eixos ortogonais. Fazer um e achar que cobriu o outro deixa metade da economia na mesa.
- **Cortar Opus da decisão irreversível pra economizar.** O inverso do desperdício é igualmente burro. Economizar no framing do problema é onde o erro fica mais caro.

## Checklist antes do próximo deploy de agente

- [ ] Cada agente tem o modelo declarado num campo explícito, não herdado por inércia?
- [ ] A escolha de cada modelo passa no teste "o erro desse papel é reversível?"?
- [ ] A decisão irreversível (framing, arquitetura, gate de segurança) está no frontier, e só ela?
- [ ] Existe algum mecanismo que trava quando o modelo que rodou diverge do declarado?
- [ ] Você consegue dizer, sem abrir a fatura, qual fração do seu swarm roda em cada tier?

Se respondeu não pra qualquer uma, você provavelmente está pagando preço de Opus por trabalho de Haiku. Qual agente do seu sistema roda no modelo mais caro sem precisar?
