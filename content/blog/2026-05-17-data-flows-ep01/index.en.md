---
title: "Data Flows Ep01: the concept that comes before any tool"
description: "Knight Capital lost $440 million in 45 minutes because one server was running old code. Before any tool, there's a concept that separates robust pipeline from fragile pipeline: data flow."
tags: ["zero-to-expert", "data-flows", "fundamentals", "data-engineering"]
images:
  - cover.png
---

On August 1, 2012, Knight Capital lost $440 million in 45 minutes.

It wasn't an algorithm bug. It wasn't a market crisis. It was a single server out of eight that received the new code deploy, while another kept a legacy flag reactivated (Power Peg, 2003 code). The two ran in parallel. The result was a cascade of automated orders that nobody could stop.

The SEC documented the case (Release No. 70694, October 2013): the root cause wasn't a trading logic error. It was state inconsistency between servers that should have been synchronized. In data engineering language, it was a broken data flow.

Knight Capital had sophisticated algorithms. Had more than a decade of operation. What it didn't have was a clear mental model of where the data was born, where it passed through, and where it needed to arrive consistently.

This mental model is what defines the rest. I have worked with data long enough to have seen, at smaller scales, variations of this same failure. Before Apache Spark, before dbt, before Snowflake, before any tool, there's a concept that separates robust pipeline from fragile pipeline.

## In one sentence

> Data flow is the path the data travels from source to destination, with every transformation in between. Getting that path right is an architectural decision. Getting it wrong costs money.

## Where this idea came from

It's not new. Bill Inmon published *Building the Data Warehouse* in 1992 defending top-down architecture, normalized, enterprise-wide. Ralph Kimball responded in 1996 with *The Data Warehouse Toolkit*: bottom-up, dimensional modeling, data marts composing the whole. The Inmon vs Kimball debate dominated the 90s and still shows up in any architecture review.

What changed between 1996 and 2026 wasn't the concept, was the scale. In 2017, Martin Kleppmann published *Designing Data-Intensive Applications* and formalized in chapter 11 the distinction that organizes modern data engineering:

> *"A stream refers to data that is incrementally made available over time... in contrast to batch processing, where the input is a known, finite size."*

Bounded vs unbounded. A dataset with known size (batch) versus one that never ends (stream). Every data architecture decision starts at this distinction.

In 2021, the Lakehouse paper (Armbrust, Ghodsi, Xin, Zaharia, CIDR) proposed unifying warehouse and lake via metadata layer (Delta, Iceberg, Hudi). In 2020, the dbt Labs people popularized ELT over ETL: transformation inside the warehouse, not before. Each wave changed tooling, not principle.

## Bounded vs unbounded: the decision that defines everything

Every pipeline decision starts here. Practical summary in a table:

| Type | Characteristic | When to use | Cost |
|---|---|---|---|
| **Batch** | Finite dataset, processed in defined window | SLA of hours, accounting reports, historical snapshots | Simple to build, debug, recover |
| **Streaming** | Infinite dataset, event processed when it arrives | SLA of seconds to a few minutes, real-time fraud, operational dashboards | Complex, requires watermarks, exactly-once, heavy observability |
| **Micro-batch** | Streaming in short windows (seconds to minutes) | Middle ground: minute dashboards, ML feature store near-real-time | Spark Structured Streaming, Flink mini-batches |

Tyler Akidau and team (Google) published in VLDB 2015 the paper *The Dataflow Model* that formalized the modern vocabulary: event time, processing time, watermarks, triggers, windowing. The central quote:

> *"A practical approach to balancing the inherent tension between correctness, latency, and cost in massive-scale, unbounded, out-of-order data."*

Translation: streaming is correct in three variables at once. You don't maximize the three, you choose two and pay the third.

## When batch, when streaming

The practical rule I use is simple: acceptable latency SLA defines the answer.

- **SLA above 1h** tends to batch. Simple reprocessing, direct debugging, cheap infrastructure.
- **SLA below 1 minute** requires streaming. Whoever tries to force batch in this scenario creates windows so short that they reinvent streaming with the worst of both worlds.
- **SLA between 1 minute and 1h** is micro-batch territory. Spark Structured Streaming or Flink mini-batches solve it.

Jay Kreps, Confluent founder, wrote in 2014 the essay *Questioning the Lambda Architecture* attacking the model proposed by Nathan Marz, which kept two parallel layers (batch + speed). The quote that stayed:

> *"The problem with the Lambda Architecture is that maintaining code that needs to produce the same result in two complex distributed systems is exactly as painful as it seems."*

Kreps proposed Kappa: unified log (Kafka) as source of truth, reprocessing via replay. Kappa became standard in those operating serious streaming.

The most common mistake I see is forcing streaming because "it sounds modern". Streaming is not a better version of batch. It's a different contract, different cost, different mental model. When the decision is made by fashion instead of by SLA, the team spends months building complexity the problem didn't ask for, and I've fallen into this trap more than once.

## What goes wrong when they ignore the flow

Knight Capital was not an isolated accident. The pattern repeats at other scales.

**GitHub, October 2018**: 24-hour outage. Root cause documented by Jason Warner (official post-mortem): 43 seconds of network partition between data centers in US East caused MySQL Orchestrator failover divergence, replication storm, and cross-DC inconsistency. It was pure data flow failure at the replication layer.

**Airbnb, before Minerva**: different teams calculated "active user" with divergent queries on the same Spark cluster. Metrics clashed in executive meetings. The solution wasn't another dashboard, was a single layer of metric definitions with explicit lineage from source to destination. Minerva today indexes more than 200 thousand data assets.

These cases fit into patterns named in the literature. Worth knowing each one:

- **Pipeline jungle** (Sculley et al, NeurIPS 2015, *Hidden Technical Debt in Machine Learning Systems*): *"pipeline jungles often appear as data preparation evolves organically... testing such pipelines requires expensive end-to-end integration tests."* It's what happens when nobody designed the flow at the start and it grows by addition.
- **Data swamp** (Nick Heudecker, Gartner 2014): *"lakes turn into swamps when there is no metadata, governance, or quality control."* Lake became a folder of files thrown anywhere.
- **Schema drift**: fields change without warning between runs, downstream contracts break silently.
- **Lineage gaps**: nobody knows where the data in the dashboard came from.
- **Reverse-ETL chaos**: data goes back from warehouse to SaaS without governance, becomes a secret source of truth nobody audits.

## How the big ones document their own flow

Companies that run data in real production publish the architecture. Worth reading.

| Company | Document | Anchor |
|---|---|---|
| **Netflix** | *Maestro: Netflix's Workflow Orchestrator* (TechBlog, Jul 2024) | Orchestrates hundreds of thousands of workflows per day, WAP pattern (Write-Audit-Publish) over Iceberg |
| **Uber** | *Uber's Big Data Platform* (Eng Blog, Oct 2018) | Hudi reduced ingestion latency from 24h to less than 1h on 100+ PB |
| **Airbnb** | *Democratizing Data at Airbnb* (May 2017) | Dataportal indexes 200K+ data assets with explicit lineage |
| **Stripe** | *Online migrations at scale* (Eng Blog, Feb 2017) | Dual-write + backfill + reconciliation to migrate financial data without loss |
| **Slack** | *How We Built Slack's Data Warehouse* (Sep 2023) | Migration from Presto+Hive to Trino+Iceberg, 60K queries per day |

Common pattern: each one documented the flow before building the next tool. The tool was born from the diagram, not the other way around.

## Anti-patterns to avoid

1. **Forcing streaming because it sounds modern.** If SLA is daily, batch solves with 10% of the complexity.
2. **Building pipeline without drawing the flow first.** Pipeline jungle is literally that: grow without a map.
3. **Accepting the lake as "throw everything here, organize later".** Becomes swamp in 6 months.
4. **Ignoring schema contracts.** Schema drift breaks downstream silently. Use Schema Registry or versioned contract in SQL.
5. **Keeping two parallel implementations (Lambda).** Maintenance cost doubles, behaviors diverge, nobody trusts either.
6. **Skipping lineage.** Lineage isn't luxury. It's the only way to answer "where did this number come from" without opening 12 jobs.

## Where to start

Can you draw, on a napkin, the data flow of your most critical pipeline? Exact source, main transformations, destinations, SLA per step.

If yes, you're ahead of most. If not, start there. Before Spark, before dbt, before any new tool.

The next episodes of the Zero to Expert series will go into each layer with depth: ingestion (formats, idempotency, CDC), transformation (SQL vs Python vs Spark), destination (warehouse vs lake vs lakehouse), orchestration. Each episode with a concrete case and decision at the center, not theory.

If there's a specific concept you'd like to see covered, send it on [LinkedIn](https://linkedin.com/in/thaisvaz) or subscribe to the [newsletter](https://vazdeng.substack.com) to receive the next episodes.
