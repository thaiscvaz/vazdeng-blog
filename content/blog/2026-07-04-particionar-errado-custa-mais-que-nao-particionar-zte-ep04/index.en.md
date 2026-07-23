---
title: "Zero to Expert Ep 04: Wrong partitioning costs more than not partitioning"
slug: particionar-errado-custa-mais-que-nao-particionar-zte-ep04
date: 2026-07-04
publishDate: 2026-07-04
draft: false
description: "Almost everyone learns \"partition to make it fast\". The wrong granularity makes your pipeline slower, pricier and more fragile than no partition at all."
tags: ["zero-to-expert", "engenharia-de-dados"]
images:
  - cover.png
series: ["zero-to-expert"]
episode: 4
---
The first time I saw a table "partitioned by CPF", Brazil's personal taxpayer ID, I thought it was genius. Filtering by customer is the most common query pattern in banking, so partitioning by whatever shows up most in the `WHERE` clause seemed obvious. I was wrong, and the mistake was expensive.

The table had millions of partitions, each a few kilobytes in size. A query that should read a handful of files spent most of its time just listing directories and opening metadata. The job got slower than the version with no partition at all, and the cluster bill went up with it. That is the point of this episode: partitioning is not a "make it fast" button. It is a physical layout decision that, done at the wrong granularity, charges you more than the problem it was supposed to solve.

In the previous episodes we climbed one step at a time. Ep01 looked at data flows, Ep02 organized task ordering in the DAG, Ep03 made sure running again breaks nothing (idempotency). Today the question is more physical: where the bytes live on disk, and why that decides the cost of your pipeline.

## What partitioning actually means

> In one sentence: partitioning is splitting a table into separate folders in storage, one per value of a column, so a query can skip the folders it does not care about.

If you have a transactions table and partition it by `date`, on disk that literally becomes one folder per day: `date=2026-07-01/`, `date=2026-07-02/`, and so on. When you run `WHERE date = '2026-07-01'`, the engine reads only that folder and ignores all the others. That is called **partition pruning**, and it is the engine that makes partitioning worth it: the filter becomes "I do not even need to open these files".

The analogy I use for myself is the hanging file cabinet. If you separate bills by month, finding July's bill means opening one drawer. But if you decide to separate them by protocol number, every bill becomes its own folder, and the drawer becomes a thousand little folders with one sheet each. Finding anything now means flipping through the entire cabinet. The separation criterion is everything. Separating is free in theory and expensive in practice when you separate by the wrong thing.

The missing piece for anyone starting out is that the pruning gain only shows up if two things are true at the same time: your queries filter by that column **and** each partition is large enough that skipping the others outweighs the cost of managing that many folders.

## Why wrong partitioning is worse than no partitioning

There are two classic ways to get it wrong, and both produce the same symptom: **the small files problem**.

A high-cardinality column (CPF, transaction ID, email) generates an explosion of tiny partitions. Spark and Delta keep per-file statistics (min, max, count). With thousands of files of a few KB each, the engine spends more time listing directories, opening footers and assembling metadata than actually reading data. Worse: when the list of partition keys gets huge, Spark itself may **turn off** optimizations like dynamic partition pruning to avoid blowing up the overhead. You partitioned to gain pruning and the pruning switched itself off.

A very low-cardinality column (a `status` with 3 values, for example) fails in the other direction: a few giant, unbalanced partitions. One partition concentrates 90% of the data and becomes a bottleneck, while partitioning gave you no selectivity at all.

The official Databricks docs are blunt about the thresholds, and they are worth tattooing:

- Do not partition tables with less than 1 TB of data.
- Each partition should contain at least 1 GB of data.
- Partitioning works poorly for high-cardinality columns (timestamps, customer IDs).

The number that matters here is the second one. If your partition column cannot guarantee 1 GB per partition for most values, it is the wrong column. And the default target file size of `OPTIMIZE` in Delta is 1 GB, precisely because it is the point that balances reads and overhead well on most instance types. Your partition granularity needs to talk to that scale, not fight it.

## When to partition and when not to

| Situation | Decision | Why |
|---|---|---|
| Table < 1 TB | Do not partition | Pruning does not pay for the overhead; built-in optimizations already handle it |
| TB+ table, queries always filter by date | Partition by date (`business_date`) | Medium cardinality, fat partitions, real pruning |
| High-cardinality column (CPF, ID) | Never partition | Guaranteed small files problem |
| Very low-cardinality column (status) | Do not partition by it | Unbalanced partitions, no selectivity |
| Varied query pattern or in doubt | Liquid Clustering | Handles high cardinality and multiple columns without rewriting |

The most important row is the first one, and it is the most ignored. Most tables under 1 TB simply do not need a partition, and on Databricks Runtime 11.3+ unpartitioned tables already get **ingestion time clustering** for free: the data stays grouped by ingestion time, delivering a benefit similar to partitioning by date without you tuning anything. I have wasted time designing a partition scheme for a table that fit entirely in the memory of a single machine. Do not partition by reflex. Partition by evidence.

## Liquid Clustering: the way out when the answer is "it depends"

When your doubt is honest (the query pattern is varied, cardinality is high, you filter sometimes by one column and sometimes by another), the modern answer is not to force a partition. It is **Liquid Clustering**.

Instead of `PARTITIONED BY`, you use `CLUSTER BY`. The practical difference that changes the game: you can **redefine the clustering keys without rewriting the existing data**, which is impossible with partitioning (change the partition scheme, rewrite the whole table). It also handles high cardinality and multiple columns well, precisely the two scenarios where partitioning betrays you.

Databricks today recommends Liquid Clustering as the default for every new Delta table. That is not a minor version detail: it is a shift in what your first choice should be. Classic partitioning is still valid for a niche (huge table, with a stable and well-known filter pattern by date), but it stopped being the starting point.

Explicit opinion: if you are creating a table on Delta today and do not have a very specific, documented reason to partition, start with Liquid Clustering. Partitioning became the exception that needs to justify itself, not the default you assume.

## A concrete case, with numbers

Picture a Silver table of transactions, 2 TB, queried almost always by date range.

Bad scenario, partitioned by `transaction_id`: cardinality in the millions, each partition a few KB, thousands of tiny files. The date query has nothing to prune (the filter does not hit the partition column), so it scans everything, and still pays the toll of listing a mountain of directories. Slow and expensive.

Good scenario, partitioned by `business_date`: 365 partitions per year, each in the GB range. `WHERE business_date BETWEEN ...` prunes straight to the range and reads only the right folders. That is pruning doing its job.

The contrast is not "partitioned vs unpartitioned". It is the same table, on the same engine, split by two different criteria. One gives money back, the other burns it.

## Anti-patterns

- **Partitioning by reflex.** "It is big, so partition it." A table < 1 TB almost never needs it, and the partition overhead can make it slower.
- **Partitioning by a high-cardinality column** (CPF, ID, email, timestamp to the second). Guaranteed small files problem, and pruning may even switch itself off.
- **More than 10 thousand partitions in a single table.** A sign of wrong granularity. Refactor the criterion or migrate to clustering.
- **Partitioning by a column your queries do not filter on.** You pay the cost of managing folders and gain no pruning at all.
- **Ignoring the 1 GB per partition floor.** If the column cannot guarantee it, it is the wrong column.
- **Forcing a partition where the answer is "it depends".** When the doubt is real, the answer is Liquid Clustering, not picking a column by guesswork.

## Checklist before typing `PARTITIONED BY`

1. Is the table 1 TB or more? If not, you probably should not partition.
2. Do my queries filter by this column most of the time?
3. Will each partition hold at least 1 GB of data?
4. Is the cardinality medium (tens to hundreds of values), not millions?
5. If I answered "I don't know" to any of the above, I should be looking at Liquid Clustering.

Partitioning is one of the very few data engineering decisions where doing the right thing and doing nothing are, quite often, the same answer. The right question was never "how do I partition this?". It is "does this need to be partitioned?". What was the last table you partitioned just because it seemed obvious?

---

*Next step in the Zero to Expert series: file formats and why Parquet won. Concept before tool, always.*
