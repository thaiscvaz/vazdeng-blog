---
title: "IA Foundations 07: janela de 1M tokens não resolve nada se a informação cai no meio"
slug: contexto-longo-nao-resolve-lost-in-the-middle
date: 2026-07-18
publishDate: 2026-07-18
draft: false
description: "---"
tags: ["ia", "agentes"]
images:
  - cover.png
---
---
title: "IA Foundations 07: janela de 1M tokens não resolve nada se a informação cai no meio"
subtitle: "Lost in the middle não é bug, é padrão de atenção. Posicionamento vale mais que tamanho de contexto. E colocar regra crítica na linha 300 é jogar fora acurácia."
publish_date: 2026-07-18
track: IA
num: "007"
slug: contexto-longo-nao-resolve-lost-in-the-middle
tags:
  - llm
  - contexto-longo
  - harness-engineering
  - lost-in-the-middle
---

Existe uma promessa vendida em toda release de modelo novo em 2026: "agora com 1 milhão de tokens de contexto, o modelo lê seu repositório inteiro". A leitura correta é diferente. O modelo lê tudo, mas usa muito melhor o que está no início e no fim. O que cai no meio ele ignora com uma frequência que a maioria dos times não mede, e depois debuga como se fosse falha de raciocínio.

Isso não é opinião. É [Liu et al. 2023](https://arxiv.org/abs/2307.03172), paper que ficou conhecido como "Lost in the Middle: How Language Models Use Long Contexts".

## O que o paper mostrou

Os autores fizeram duas tarefas controladas: multi-document QA e key-value retrieval. Em ambas, colocaram a informação-chave em posições diferentes do contexto e mediram a acurácia. O resultado foi consistente: curva em forma de U. Acurácia alta quando a resposta está no início, alta quando está no fim, e cai de 20 a 30 pontos percentuais quando a resposta está no meio.

Isso vale para GPT-3.5, Claude 1.3, e modelos abertos com contexto explicitamente longo (MPT, LongChat). Não é problema de um modelo específico. É padrão da arquitetura Transformer: tokens do início são atendidos por todos os tokens subsequentes. Tokens do fim se atendem fortemente entre si. Tokens do meio recebem proporcionalmente menos atenção durante a geração. É geometria de atenção, não engenharia mal feita.

![A curva em U de Liu et al. 2023. A acurácia do modelo é alta quando a informação-chave está no início do contexto, alta quando está no fim, e cai de 20 a 30 pontos percentuais quando a informação cai no meio. O padrão vale para GPT-3.5, Claude 1.3 e modelos abertos de contexto longo. Regra crítica no meio do arquivo é acurácia jogada fora.](images/01-curva-em-u.png)

## Por que isso é o inverso do que o mercado promete

Todo release de janela grande em 2026 é vendido como "cabe tudo, não precisa mais organizar". Isso é meia-verdade que engana o time. Sim, cabe. Não, o modelo não usa o mesmo do meio da mesma forma que usa das pontas. Quem passa uma base de código inteira de 800 mil tokens confiando que o modelo vai raciocinar sobre a linha 400 mil está no vale mais fundo da curva U.

Anthropic e OpenAI documentam isso nas próprias diretrizes: instrução crítica deve ficar no topo, e informação de controle "concisa e de alta prioridade". Não é sugestão de estilo. É consequência direta do paper.

## Onde eu vi isso aparecer na prática

O meu `CLAUDE.md` global cresceu por acúmulo. Identidade, regra matriz, padrão world-class, política de vault, sistema de refeição, regra de data, política de privacidade. Foi tudo parar no mesmo arquivo, e o arquivo virou uma enciclopédia de milhares de linhas. Enquanto era pequeno, tudo funcionava. Depois que passou de umas centenas de linhas, comecei a notar que o modelo aplicava com precisão as regras do topo e do fim, e ignorava as do meio com frequência.

A solução não foi encolher forçando resumo. Foi mudar a arquitetura do arquivo: entry file virou router de ~150 linhas com identidade, dez regras invioláveis e links para políticas temáticas carregadas sob demanda. As regras que estavam empilhadas no meio migraram para arquivos específicos em `~/.claude/policies/`. Cada política tem seu próprio trigger declarado. O modelo carrega quando precisa, e o entry file fica curto o suficiente para caber na região de atenção alta.

## O anti-padrão que eu vejo mais

"O contexto agora é grande. Vou jogar tudo lá."

Se você tem 300 documentos e a informação relevante para responder está no documento 150, a probabilidade do modelo pegar essa informação é significativamente menor do que se estivesse no documento 1 ou no 300. Colocar 300 documentos em janela grande não resolve retrieval. É retrieval feito na pior geometria de atenção possível.

O que resolve é preservar a hierarquia de importância. Informação crítica no topo. Informação secundária pode ir para o final. O que sobra vai para arquivo externo carregado sob demanda ou para um índice curto que aponta para o detalhe. Isso é o que a comunidade de harness engineering chama de "entry file = router, não enciclopédia".

## O que fazer com isso na prática

Três decisões simples, na ordem:

1. **Meça o tamanho dos seus arquivos de instrução.** Qualquer entry file (CLAUDE.md, AGENTS.md, system prompt) acima de 300 linhas é candidato imediato a refatoração. Não é meta arbitrária, é o limite empírico onde a região do meio começa a doer.

2. **Coloque as regras não-negociáveis no topo do arquivo, sempre.** Não confie em ordem de escrita. Ordem é o comprimento de onda de atenção do modelo.

3. **Documente por que cada regra está lá.** Sem histórico de origem, ninguém remove regra do meio nem move ela para arquivo externo, porque parece perigoso. Regra sem contexto de origem apodrece no meio do arquivo.

Janela de 1M tokens não é solução. É oportunidade de estruturar melhor o contexto que você já tinha, ou é como preguiça travestida de progresso. Depende de você.
