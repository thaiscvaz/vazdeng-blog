---
title: "Data Flows Ep01: o conceito que vem antes de qualquer ferramenta"
slug: data-flows-ep01
date: 2026-05-17
publishDate: 2026-05-17
draft: false
description: "Primeiro episódio da série Zero to Expert. Dado sai de um lugar e chega em outro. Por que esse modelo mental simples resolve metade das dificuldades em produção."
tags: ["zero-to-expert", "data-flows", "fundamentos", "data-engineering"]
images:
  - cover.png
---

Antes de qualquer ferramenta, qualquer linguagem, qualquer framework, existe um conceito simples que está por baixo de tudo em engenharia de dados.

Dado sai de um lugar e chega em outro. Isso é um fluxo de dados.

Parece simples demais. Mas a maioria das dificuldades que engenheiros de dados enfrentam em produção, desde pipelines quebrados até dados que chegam atrasados ou inconsistentes, pode ser rastreada até uma confusão sobre onde o dado nasce, o que acontece com ele no caminho, e onde ele termina.

Esse é o primeiro episódio da série Zero to Expert que eu venho construindo. O objetivo não é ensinar ferramenta. É construir o modelo mental que faz todas as ferramentas fazerem sentido.

## De onde vem o dado

Todo fluxo começa numa fonte. A fonte é qualquer sistema que produz informação: um banco de dados de um e-commerce com os pedidos dos clientes, uma API de pagamentos que registra cada transação, sensores IoT numa linha de produção, arquivos de log de um servidor.

A fonte não se preocupa com análise. Ela se preocupa com a operação. O banco de dados do e-commerce foi construído para processar pedidos rápido, não para responder à pergunta "qual produto vende mais nas terças-feiras de novembro".

Essa tensão é o ponto de partida de toda arquitetura de dados: os sistemas operacionais são otimizados para escrever, os sistemas analíticos são otimizados para ler e agregar. Um fluxo de dados conecta os dois.

## O que acontece no meio

Entre a fonte e o destino, o dado passa por transformações. Essas transformações podem ser simples ou complexas, mas elas sempre existem.

**Ingestão** é o primeiro passo: trazer o dado da fonte para o seu ambiente. Pode ser uma cópia completa da tabela, pode ser apenas o que mudou desde a última vez, pode ser um stream em tempo real de eventos.

**Transformação** é onde o dado bruto vira informação útil. Nomes padronizados, valores nulos tratados, duplicatas removidas, tabelas diferentes combinadas, agregações calculadas. É aqui que a regra de negócio entra: o que significa um pedido "completo"? Quando uma transação é considerada fraude? Qual é o critério de retenção desse cliente?

**Destino** é onde o dado transformado vai viver para ser consumido: um dashboard, um modelo de machine learning, um relatório que chega por email toda segunda-feira, um sistema que toma decisões automatizadas.

## A diferença entre batch e streaming

Essa é a primeira decisão arquitetural que define como um pipeline se comporta.

**Batch** processa dados em blocos, num horário definido. O relatório roda todo dia às 6h da manhã e cobre as transações das últimas 24 horas. O dado não é em tempo real, mas é muito mais simples de construir, debugar e manter. A maioria dos pipelines analíticos do mundo é batch.

**Streaming** processa cada evento no momento em que acontece. Quando você abre o aplicativo do banco e a última transação já aparece lá, é streaming. Quando o sistema de fraude bloqueia um cartão em milissegundos, é streaming.

A escolha não é sobre qual é melhor. É sobre qual o caso de uso exige.

Um relatório de vendas mensal para a diretoria não precisa de streaming. Forçar streaming aqui adiciona complexidade sem benefício.

Uma detecção de fraude em cartão de crédito não pode ser batch. Um ciclo de processamento a cada 24h deixaria fraudes acontecerem por horas antes de detectar.

O erro mais comum é usar streaming quando batch resolve, porque streaming parece mais sofisticado. O custo é real: infraestrutura mais complexa, debugging mais difícil, mais pontos de falha.

## Por que isso importa no seu trabalho

Aprendi com o tempo que quando um pipeline quebra em produção, a primeira pergunta sempre é: onde no fluxo o problema aconteceu?

Na fonte? O dado não chegou, a API caiu, o schema mudou.

Na ingestão? O job falhou, o horário mudou, a conexão expirou.

Na transformação? Uma regra de negócio produziu um resultado inesperado, um valor nulo não foi tratado, uma tabela que deveria existir não existe.

No destino? O dashboard está mostrando o dado errado, o modelo recebeu features desatualizadas, o email enviou antes do processamento terminar.

Ter clareza sobre cada etapa do fluxo é o que permite debugar rápido. Sem esse modelo mental, você fica olhando para logs sem saber por onde começar.

## O que vem nos próximos episódios

Nas próximas edições da série Zero to Expert, vou entrar em cada parte desse fluxo com mais profundidade:

- Como a ingestão funciona na prática, os formatos que importam e os erros que todo engenheiro vai cometer ao menos uma vez
- O que é uma camada de transformação e quando usar SQL, Python ou Spark
- Como escolher onde o dado vai viver: data warehouse, data lake, lakehouse
- Orquestração: o que mantém esse fluxo inteiro funcionando de forma confiável

Cada episódio vai ter exemplos reais e a decisão no centro, não teoria.

Se tem algum conceito específico que você quer que eu cubra na série, me manda no [LinkedIn](https://linkedin.com/in/thaisvaz) ou assina a [newsletter](https://vazdeng.substack.com) para receber os próximos episódios.
