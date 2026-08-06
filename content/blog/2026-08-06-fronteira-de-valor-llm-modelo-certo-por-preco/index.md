---
title: "Fronteira de valor: qual modelo LLM faz sentido pra cada orçamento"
slug: fronteira-de-valor-llm-modelo-certo-por-preco
date: 2026-08-06
publishDate: 2026-08-06
draft: false
description: "De $1 a $10 por milhão de tokens de entrada. A régua certa é o tipo de trabalho cognitivo, não o tamanho da tarefa."
tags: ["ferramentas"]
images:
  - cover.png
---
Quando montei minha squad de agentes de engenharia de dados, cada agente rodava implicitamente no modelo do orquestrador: o mais caro disponível. Ninguém decidiu isso. É o default que se instala sozinho quando você não declara o modelo por papel, e ele cobra raciocínio de fronteira pra formatar runbook. Foi a fatura desse default que me empurrou pro exercício que virou este verdict.

A tabela da Anthropic hoje (conferi em 4 de agosto) vai de $1 por milhão de tokens de entrada no Haiku 4.5 a $10 no topo da linha, com saída de $5 a $50. Amplitude de 10x dentro do mesmo fornecedor. No meio, o Sonnet 4.6 custa $3 de entrada e $15 de saída; o Opus, $5 e $25. E os modificadores mudam a conta de novo: batch processing corta 50% de entrada e saída, e cache hit paga um décimo da tarifa de entrada.

Fronteira de valor é o nome que dou pra leitura certa dessa tabela: uma curva de custo por capacidade onde cada orçamento compra um ponto. Fora da fronteira você está em um de dois erros. Ou paga capacidade que a tarefa não usa, topo de linha resumindo texto pronto. Ou compra retrabalho, modelo de base tomando decisão de arquitetura. A pergunta "qual é o melhor modelo" não fecha conta nenhuma. A que fecha é: qual é o trabalho cognitivo deste papel?

![A fronteira de valor da tabela Claude em três classes de trabalho cognitivo: na base, Haiku 4.5 a um dólar de entrada e cinco de saída por milhão de tokens, para transformação de artefato pronto como runbooks e docs finais; no meio, Sonnet 4.6 a três e quinze dólares, para implementação estruturada dentro de padrão definido; no topo, Opus a cinco e vinte e cinco dólares, reservado a decisão irreversível, arquitetura e gate de segurança. A barra âmbar resume o verdict: default não é decisão, pague fronteira de raciocínio só onde errar é caro.](images/01-fronteira-de-valor.png)

A régua que uso desde então tem três classes. Decisão irreversível: arquitetura, gate de segurança, julgamento de aceite. Erro aqui contamina a cadeia inteira, então vale a capacidade máxima. Implementação estruturada: código dentro de padrão definido, quebra de issues, infra como código. Exige consistência, não fronteira de raciocínio: modelo do meio. Transformação de artefato pronto: doc final, runbook, nota a partir de conteúdo já decidido. Formato conhecido, velocidade importa: modelo de base. Na minha squad isso virou regra escrita: 27 agentes declaram o modelo no próprio frontmatter, 4 no topo, 20 no meio, 3 na base.

## O rebaixamento que me ensinou a régua

O exercício não é estático, e o caso mais útil foi um rebaixamento. O papel que implementa componentes de IA rodava no topo da tabela. Auditando o fluxo, descobri que a decisão cara morava em outro lugar: o arquiteto decide o desenho, o gate de segurança revisa no final, e o que sobra pro papel é volume com critério. Desceu pro meio, com regra escrita de reavaliação: se acumular evidência de subperformance, volta. Corte de custo sem porta de retorno não é disciplina, é aposta.

O limite na direção oposta importa mais. Gate de segurança e julgamento de aceite não descem nunca. Falso negativo no último gate custa mais que qualquer diferença de tarifa, e quem baixa o modelo do revisor pra economizar centavos está comprando o incidente inteiro. A fronteira de valor não é uma licença pra usar sempre o mais barato. É a proibição de pagar sem saber o que está comprando.

## Quando o exercício não vale

Protótipo de volume baixo dispensa a régua: roda tudo no melhor modelo e segue, o custo da análise supera a economia. E a fronteira se move a cada release. O Sonnet 5 está em preço promocional até o fim de agosto e depois sobe pro padrão; a régua precisa de dono e de revisita, não de decisão única gravada em pedra.

Já escrevi em junho sobre rotear modelo por papel dentro de um sistema de agentes. O verdict de hoje é o passo anterior a esse: aceitar que a tabela de preço é uma curva de valor e que o seu orçamento compra um ponto dela. Default não é decisão. Na dúvida, comece no meio, suba só onde errar é caro e desça tudo que já tem formato pronto.
