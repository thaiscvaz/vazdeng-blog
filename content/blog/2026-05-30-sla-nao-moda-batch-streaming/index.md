---
title: "SLA, não moda: quando batch, quando streaming, quando ambos"
cover_title: "Batch ou streaming?"
slug: sla-nao-moda-batch-streaming
date: 2026-05-30
publishDate: 2026-05-30
draft: false
description: "A decisão entre batch e streaming não é cultural. É técnica: SLA do consumidor, custo, complexidade. E quase ninguém mede antes de escolher."
tags: ["batch", "streaming", "data-architecture", "data-engineering", "kafka", "spark"]
images:
  - cover.png
---

Vi um time de marketing fazer o que toda equipe faz uma vez: adotar streaming porque soava moderno. Kafka gerenciado, workers 24x7, exactly-once de garantia. Pra processar eventos que chegavam a cada 10 minutos. Batch noturno resolveria igual. Custava um décimo. Levou seis meses até alguém medir.

O padrão se repete. Eu já passei pela mesma decisão em quatro domínios diferentes: pipelines de finanças, processos industriais, marketing, analytics. A discussão sempre começa errada. "Vamos pra streaming porque é mais moderno." Ou "vamos manter batch porque é o que a gente sempre fez." As duas perdem a pergunta certa.

A pergunta certa é uma só: qual o SLA real do consumidor que vai usar esse dado?

## A pergunta certa não é "qual é mais moderno"

Martin Kleppmann formaliza no capítulo 11 de *Designing Data-Intensive Applications* a distinção que organiza qualquer arquitetura de dados em 2026. Dado **bounded** (conjunto finito, tamanho conhecido) versus **unbounded** (fluxo que nunca termina). Toda decisão começa aí.

Mas a distinção bounded/unbounded é técnica, não comportamental. O dado real raramente é só uma coisa. Logs de aplicação são unbounded por natureza. Se eu agrego eles em batches de 1 hora pra alimentar um dashboard que ninguém olha mais de hora em hora, o consumidor está tratando como bounded. O dado é o que o consumo decide.

Tyler Akidau e equipe do Google publicaram em 2015 o paper que virou padrão da indústria, *The Dataflow Model*. A frase central:

> *A practical approach to balancing the inherent tension between correctness, latency, and cost in massive-scale, unbounded, out-of-order data.*

Tradução: streaming é certo em três variáveis ao mesmo tempo. Correção, latência e custo. Você escolhe duas, paga a terceira. Batch é mais simples justamente porque não tenta otimizar latência.

## Tabela de decisão: SLA × tecnologia

![Tabela visual SLA versus tecnologia recomendada](images/01-tabela-sla-tecnologia.png)

Pra a maioria dos pipelines que vejo, a tabela acima resolve a decisão em 30 segundos. SLA acima de 1 hora é território de batch. SLA abaixo de 1 minuto exige streaming. O meio é micro-batch, e a maioria dos casos cai aí, não nos extremos.

## Quando batch ganha (mesmo em 2026)

Spotify roda recomendação em batch noturno no BigQuery. Netflix tem o Maestro orquestrando centenas de milhares de workflows por dia com padrão Write-Audit-Publish sobre Iceberg. Nenhuma das duas é "atrasada". Elas escolheram batch onde batch resolve melhor.

Batch ganha quando:

- O SLA do consumidor é horário ou diário (relatório contábil, fechamento, snapshot histórico, ML training)
- O dado de entrada é estável o suficiente pra você reprocessar quando quiser
- Seu time tem mais facilidade em debugar Python rodando 1 vez por noite do que stream processor 24x7

O custo importa muito. Cluster Spark batch noturno fica desligado durante o dia. Infraestrutura quando não tem job rodando: zero. Kafka gerenciado fica ligado 24x7. Confluent Cloud Standard começa em 1 a 3 mil dólares por mês, e o egress pode chegar a 47 mil dólares por mês em 300 MiB/s de saída. A diferença sobre o ano é o salário de um engenheiro pleno em Curitiba.

## Quando streaming é a única resposta

Pix tem SLA de menos de 10 segundos, 24x7. O BACEN publica isso. Batch diário não funciona. Não é opcional. Sistema de detecção de fraude em ponto de venda também é assim: ou identifica antes da transação fechar ou não serve pra nada. Dashboard de operações em call center, mesma lógica: o agente precisa ver o cliente atualizado no instante em que atende.

Esses casos não admitem batch. Streaming é a única resposta.

Pra eles, Flink entrega latência abaixo de 100 milissegundos. Spark Structured Streaming fica em 100 milissegundos a 1 segundo (micro-batch). Kafka Streams roda embutido na aplicação, sem cluster próprio, e processa cerca de 1 milhão de eventos por segundo. A escolha entre os três é outro post.

Uber é o caso mais interessante. Adotou streaming sem virar 100% streaming. Adicionou o Hudi pra incremental processing e baixou latência de ingestão de 24 horas pra menos de 1 hora em mais de 100 PB. O Flink IngestionNext deles consome 25% menos compute que o batch antigo. Streaming bem feito também economiza, desde que resolva o problema certo.

## Quando "ambos" é a resposta certa

Jay Kreps publicou em 2014 o ensaio que matou a Lambda Architecture. Lambda mantém duas pipelines paralelas pra produzir o mesmo resultado: uma batch confiável, uma streaming rápida. A frase que ficou:

> *The problem with the Lambda Architecture is that maintaining code that needs to produce the same result in two complex distributed systems is exactly as painful as it seems like it would be.*

![Quote Kreps sobre Lambda Architecture](images/02-quote-kreps-lambda.png)

Kreps propôs Kappa: log único (Kafka) como fonte de verdade, com reprocessamento via replay. Batch vira caso especial de streaming sobre o histórico.

O Lakehouse foi um passo a mais. O paper do Databricks de 2021 propõe uma camada de metadata (Delta, Iceberg, Hudi) que serve as duas naturezas. O mesmo dado pode ser consumido em batch pela equipe de BI e em streaming pela aplicação de fraude. Não tem 2 stacks. Tem contrato único.

"Ambos" não é covardia técnica. É design consciente quando você tem consumidores com SLAs diferentes sobre o mesmo dado.

## Perguntas que decidem o caso

Antes de abrir Terraform ou docker-compose, responde isso honestamente:

1. **Qual o SLA real do consumidor que vai ler esse dado?** Não o SLA que você imagina. O que ele de fato precisa.
2. **Esse SLA é diferente por consumidor?** Se sim, considera Lakehouse com contrato único, não 2 pipelines paralelas.
3. **Quanto custa rodar 1 mês de streaming vs batch nesse volume?** Faz a conta antes, não depois do invoice.
4. **Seu time tem maturidade pra debugar exactly-once, watermarks e estado distribuído?** Se não, o custo de aprender vem embutido no projeto.
5. **Você já tem infraestrutura de batch ou streaming rodando?** Reaproveitar reduz risco. Greenfield permite escolher melhor.

![Decision tree visual das 5 perguntas](images/03-decision-tree-5-perguntas.png)

Se você respondeu honestamente as 5 e ainda assim chegou em streaming, ótimo. Streaming faz sentido. Se chegou em batch, ótimo também. Batch resolve a maioria dos casos.

O erro não é escolher streaming. O erro é escolher streaming sem responder as 5.

---

Qual foi o pipeline que você escolheu errado e teve que refazer depois? Me conta no [LinkedIn](https://linkedin.com/in/thaisvaz) ou responde esse email. Quero ver quantos casos batem.
