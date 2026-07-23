---
title: "Iceberg in production: 3 anti-patterns that kill your data lake in 3 months"
slug: iceberg-3-antipatterns-producao
date: 2026-07-14
publishDate: 2026-07-14
draft: false
description: "Naive partitioning, bloated manifests, forgotten compaction. How that turns into 100k GET requests on a query that should cost cents."
tags: ["engenharia-de-dados"]
images:
  - cover.png
---

Iceberg has a virtue that is also a trap: it works before you learn how to use it. You create the table, the ingestion job comes up, the query runs. Everything looks fine. Three months later, without anything actually "breaking", a query that should take 200 milliseconds starts taking 45 seconds, and the object storage bill explodes because the same data now costs 500 times more to read.

I have seen this pattern in a finance pipeline in production. And I saw it again in completely different contexts, with solid technical teams. The anti-patterns are always the same three. None of them is a bug. All of them are architecture decisions that looked reasonable on day 1.

![The three Iceberg anti-patterns in production, each with symptom and fix: partitioning by hour(ts) creates 8,760 partitions of a few MB per year and is fixed with low cardinality plus SORT or Z-order; manifest bloat shows up when you write every 40s without expiring snapshots and is fixed with scheduled expire_snapshots and rewrite_manifests; deferred compaction accumulates millions of small files in streaming and is fixed with a nightly rewrite_data_files and remove_orphan_files. None is a bug, all are deferred maintenance.](images/01-tres-antipadroes.png)

## The first: partitioning by a field with no access statistics

The classic mistake is partitioning by `hour(event_timestamp)`. It makes sense on paper: temporal data, fine granularity, queries by time range. Except that if your table receives 50MB per hour, by the end of the year you have 8,760 partitions, each a few megabytes. According to [LakeOps](https://lakeops.dev/blog/iceberg-partitioning-best-practices), that is the guaranteed-fragmentation scenario.

The target Parquet file size for OLAP sits between 128MB and 512MB. Below that, the query planner spends more time opening metadata than reading data. And Iceberg opens the metadata of every potentially relevant file to do partition pruning and column statistics, before even deciding what to read.

The right path is to partition by low cardinality (date, region, maybe a business category), and use `SORT BY` or Z-order inside the partition to speed up seeks by key. Never partition by ID, granular timestamp, or any field with millions of distinct values.

## The second: manifest bloat and the late vacuum

Every write in Iceberg creates a new snapshot, and the snapshot references a manifest listing which data files belong to it. If you write every 40 seconds because the stream is continuous, the manifest grows fast. Nobody ran `expire_snapshots` because nobody has felt pain yet. Within a few weeks, metadata alone consumes gigabytes, and query planning reads all of it just to figure out what it actually needs to read.

According to [Starburst](https://www.starburst.io/blog/apache-iceberg-files/), 100 thousand small files with bloated metadata turn 200ms of planning into 45 seconds. And the object storage cost becomes 100 thousand independent GET requests. Same data volume. Same query. 500 times more expensive. Not because Iceberg is bad, but because you left the maintenance operation for later.

![Cost comparison of the same query in two table states. Fragmented, no maintenance: 100,000 small files with bloated metadata push query planning to 45 seconds and generate 100,000 object storage GET requests. Compacted with a nightly rewrite_data_files and expire_snapshots job, in 128 to 512 MB files: the same planning drops to 200 milliseconds and a handful of GET requests. Same data, same query, 500x more expensive.](images/02-mesma-query-500x.png)

When the team wakes up and runs `expire_snapshots` all at once on 50 thousand accumulated snapshots, the maintenance job alone takes hours and reprocesses months of metadata. Then it breaks on the very night it was supposed to let you sleep.

## The third: compaction as an end-of-sprint chore

Compaction (`rewrite_data_files`) is the operation that consolidates many small files into a few large ones. It is not optional with streaming ingestion. And it cannot run alone: it needs to come with `rewrite_manifests`, `expire_snapshots` and `remove_orphan_files`, otherwise you accumulate garbage along another dimension. [Dremio](https://www.dremio.com/blog/compaction-in-apache-iceberg-fine-tuning-your-iceberg-tables-data-files/) documents these four as a set that runs together, not a menu to pick from.

The rule I follow: compaction is budgeted as infra cost, not as next quarter's project. A nightly Spark job burning a few dollars of compute every day is infinitely cheaper than refactoring partitioning with historical data already scattered across millions of files. The cost is small up front and enormous later.

## Why this matters in Brazil

BACEN and LGPD add a double layer: they demand auditable retention (a minimum 5-year trail for financial institutions) and selective, purpose-scoped deletion. Iceberg delivers both natively via time travel and delete files, but only if the metadata is not rotten. A 5-terabyte manifest sitting on top of 50 of data is not just a technical problem, it is an audit risk: you cannot quickly prove which snapshot contained subject X's data on day Y.

## What I would change if I were starting today

Three simple things, in order:

1. Partition only by low-cardinality fields and use `hidden partitioning` so queries are not tied to the physical layout.
2. Schedule `rewrite_data_files` + `rewrite_manifests` + `expire_snapshots` + `remove_orphan_files` as a nightly job from day one.
3. Alert when the number of data files per partition goes above N. Cheap metric, prevents expensive pain.

A data lake does not break in a day. It accumulates silence until the day the cost blows past the ceiling or the SLA breaks in the demo for the board. The three decisions above cost little at the start and are worth the entire bill.
