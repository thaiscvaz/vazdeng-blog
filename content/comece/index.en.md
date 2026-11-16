---
title: "Start here"
kicker: "First visit"
description: "The right posts to start with on VazDEng, by the three tracks: DE Production, Applied AI and Zero to Expert. Posts are written in Portuguese first."
type: default
---

VazDEng is data engineering and AI in production, with real cases and Brazilian context. Most posts are written in Portuguese first; English versions exist for some of them. Pick the path that matches what you need now and read in order.

<nav class="vz-chips" aria-label="Tracks"><a class="vz-chip amber" href="#trilha-de">DE Production</a><a class="vz-chip sage" href="#trilha-ia">Applied AI</a><a class="vz-chip lavender" href="#trilha-zte">Zero to Expert</a></nav>

<p class="vz-track-kicker amber">DE Production</p>

## If you already run pipelines in production {#trilha-de}

1. [When Medallion Architecture gets in the way more than it helps]({{< relref "blog/2026-05-12-medallion-architecture-quando-nao" >}})<span class="vz-start-why">Where the three layers pay for themselves and where they only multiply storage.</span>
2. [SLA, not trend: when batch, when streaming, when both]({{< relref "blog/2026-05-30-sla-nao-moda-batch-streaming" >}})<span class="vz-start-why">Batch or streaming is decided by the consumer's SLA and by cost, measured first.</span>
3. [The producer renamed a column and nobody told us]({{< relref "blog/2026-06-23-contrato-de-dados-schema-quebra-silencioso" >}})<span class="vz-start-why">The incident that breaks nothing: a green job and wrong numbers for three weeks.</span>

<p class="vz-start-more"><a href="/en/blog/?trilha=amber">More DE Production in the archive →</a></p>

<p class="vz-track-kicker sage">Applied AI</p>

## If you are putting AI in production {#trilha-ia}

All three are a selection from the AI Foundations series. Ep 01 is a glossary of twenty concepts; if you already ship AI to production, start at 02.

1. [AI Foundations · 02: The LLM does nothing. The harness does.]({{< relref "blog/2026-06-13-modelo-vs-harness-llm-nao-faz-nada" >}})<span class="vz-start-why">Agent behavior comes from what surrounds the model, and mixing the two up costs money and security.</span>
2. [The 5 subsystems that separate an agent that works from one that only looks like it works]({{< relref "blog/2026-06-27-harness-5-subsistemas-agente-que-funciona" >}})<span class="vz-start-why">The harness opened up: what each of the five subsystems does.</span>
3. [Your agent is degrading in silence. I built a 9-eval suite to prove it]({{< relref "blog/2026-07-04-agente-degrada-em-silencio-eval-suite-propria" >}})<span class="vz-start-why">Per-step, per-role evals with 9 golden cases, to catch the regression the final output hides.</span>

The full series is at [AI Foundations](/series/ia-foundations/).

<p class="vz-track-kicker lavender">Zero to Expert</p>

## If you want solid fundamentals {#trilha-zte}

The Zero to Expert series, one concept per episode, before any tool. Start with the first four, in order.

1. [Data Flows Ep01: the concept that comes before any tool]({{< relref "blog/2026-05-30-data-flows-ep01" >}})<span class="vz-start-why">Why understanding how data flows comes before picking a tool.</span>
2. [Zero to Expert · Ep 02: DAG dependencies, the law every orchestrator obeys]({{< relref "blog/2026-06-13-dependencias-dag-lei-orquestrador" >}})<span class="vz-start-why">The graph to understand before picking Airflow, Dagster or Prefect.</span>
3. [Zero to Expert Ep 03: Idempotency, why running the pipeline twice cannot change the result]({{< relref "blog/2026-06-27-idempotencia-reprocessar-sem-duplicar-zte-ep03" >}})<span class="vz-start-why">Reprocessing without duplicates, starting from the backfill that doubled revenue.</span>
4. [Zero to Expert Ep 04: Wrong partitioning costs more than not partitioning]({{< relref "blog/2026-07-04-particionar-errado-custa-mais-que-nao-particionar-zte-ep04" >}})<span class="vz-start-why">The wrong granularity makes a table slower and pricier than no partition at all.</span>

Episodes 05 to 07 (fact grain, late data, structured logs) are in the full series, at [Zero to Expert](/series/zero-to-expert/), in Portuguese for now.
