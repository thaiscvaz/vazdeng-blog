---
title: "Comece aqui"
kicker: "Primeira visita"
description: "Os posts certos para começar no VazDEng, separados pelas três trilhas: DE Produção, IA aplicada e Zero to Expert."
type: default
---

O VazDEng é engenharia de dados e IA em produção, com casos reais e contexto brasileiro. Se é a sua primeira visita, não comece pelo post mais recente. Escolha o caminho que combina com o que você precisa agora e leia na ordem.

<nav class="vz-chips" aria-label="Trilhas"><a class="vz-chip amber" href="#trilha-de">DE Produção</a><a class="vz-chip sage" href="#trilha-ia">IA aplicada</a><a class="vz-chip lavender" href="#trilha-zte">Zero to Expert</a></nav>

<p class="vz-track-kicker amber">DE Produção</p>

## Se você já roda pipeline em produção {#trilha-de}

Decisões de arquitetura com custo, número e o caso em que a ideia falha.

1. [Quando a Medallion Architecture atrapalha mais do que ajuda]({{< relref "blog/2026-05-12-medallion-architecture-quando-nao" >}})<span class="vz-start-why">Onde as três camadas se pagam e onde só multiplicam armazenamento.</span>
2. [SLA, não moda: quando batch, quando streaming, quando ambos]({{< relref "blog/2026-05-30-sla-nao-moda-batch-streaming" >}})<span class="vz-start-why">Batch ou streaming se decide pelo SLA do consumidor e pelo custo, medidos antes.</span>
3. [O produtor renomeou uma coluna e ninguém avisou: por que pipeline sem contrato de dados quebra no escuro]({{< relref "blog/2026-06-23-contrato-de-dados-schema-quebra-silencioso" >}})<span class="vz-start-why">O incidente que não derruba nada: job verde e número errado por três semanas.</span>

<p class="vz-start-more"><a href="/blog/?trilha=amber">Mais DE Produção no arquivo →</a></p>

<p class="vz-track-kicker sage">IA aplicada</p>

## Se você está colocando IA em produção {#trilha-ia}

Agentes e LLMs com avaliação, custo e segurança no centro. Os três são uma seleção da série IA Foundations. O Ep 01 é um glossário de vinte conceitos; quem já coloca IA em produção pode começar pelo 02.

1. [IA Foundations · 02: A LLM não faz nada. O harness faz.]({{< relref "blog/2026-06-13-modelo-vs-harness-llm-nao-faz-nada" >}})<span class="vz-start-why">O comportamento do agente vem do que cerca o modelo, e confundir os dois custa dinheiro e segurança.</span>
2. [Os 5 subsistemas que separam um agente que funciona de um que só parece funcionar]({{< relref "blog/2026-06-27-harness-5-subsistemas-agente-que-funciona" >}})<span class="vz-start-why">O harness aberto por dentro: o que cada um dos cinco subsistemas faz.</span>
3. [Seu agente está degradando em silêncio. Montei uma suíte de 9 evals pra provar]({{< relref "blog/2026-07-04-agente-degrada-em-silencio-eval-suite-propria" >}})<span class="vz-start-why">Eval por passo e por papel, com 9 golden cases, para pegar a regressão que o output final esconde.</span>

A série completa está em [IA Foundations](/series/ia-foundations/).

<p class="vz-track-kicker lavender">Zero to Expert</p>

## Se você quer firmar os fundamentos {#trilha-zte}

A série Zero to Expert, um conceito por episódio, antes de qualquer ferramenta. Comece pelos quatro primeiros, na ordem.

1. [Data Flows Ep01: o conceito que vem antes de qualquer ferramenta]({{< relref "blog/2026-05-30-data-flows-ep01" >}})<span class="vz-start-why">Por que entender o fluxo do dado vem antes de escolher ferramenta.</span>
2. [Zero to Expert · Ep 02: Dependências em DAG, a lei que todo orquestrador segue]({{< relref "blog/2026-06-13-dependencias-dag-lei-orquestrador" >}})<span class="vz-start-why">O grafo que você precisa entender antes de escolher Airflow, Dagster ou Prefect.</span>
3. [Zero to Expert Ep 03: Idempotência, por que rodar o pipeline duas vezes não pode mudar o resultado]({{< relref "blog/2026-06-27-idempotencia-reprocessar-sem-duplicar-zte-ep03" >}})<span class="vz-start-why">Reprocessar sem duplicar, a partir do backfill que dobrou o faturamento.</span>
4. [Zero to Expert Ep 04: Particionar errado custa mais caro que não particionar]({{< relref "blog/2026-07-04-particionar-errado-custa-mais-que-nao-particionar-zte-ep04" >}})<span class="vz-start-why">Granularidade errada deixa a tabela mais lenta e mais cara do que sem partição.</span>

Os episódios 05 a 07 (grão do fato, dado atrasado, log estruturado) estão na série completa, em [Zero to Expert](/series/zero-to-expert/).

## O checklist

O [checklist de qualidade de dados](/checklist-qualidade-dados/) junta, numa página só, as 28 perguntas que eu uso antes de subir pipeline e diz quais valem quando o número é só seu.
