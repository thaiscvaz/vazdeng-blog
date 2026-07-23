---
title: "Zero to Expert Ep 03: Idempotency, why running the pipeline twice cannot change the result"
slug: idempotencia-reprocessar-sem-duplicar-zte-ep03
date: 2026-06-27
publishDate: 2026-06-27
draft: false
description: "Ep 01 covered data flow, Ep 02 covered DAG dependencies. Now the property that separates a reliable pipeline from a time bomb: idempotency."
tags: ["zero-to-expert", "engenharia-de-dados"]
images:
  - cover.png
series: ["zero-to-expert"]
episode: 3
---
In Ep 01 we talked about *data flow* (the concept before any tool), in Ep 02 about DAG dependencies (the order things need to run in). Today I close the tripod with the property that separates a reliable pipeline from a time bomb: **idempotency**.

## The scare: the number that doubled

Let me start with a real scare, because that is how I learned this. A pipeline loaded the month's sales into a table. A retroactive correction came in (regulatory adjustment, the kind that happens all the time in Brazil) and we had to reprocess the entire month. I ran the backfill. I opened the dashboard. **Revenue had doubled.**

Nobody sold anything extra. The pipeline just ran twice. And running twice changed the result. That is exactly the problem idempotency solves.

## The concept, with no tool involved

Idempotency is an ugly word for a simple idea:

> Running the same operation once or five times has to produce the same result.

Pressing the elevator button ten times does not make the elevator come ten times. It comes once. The button is idempotent. An idempotent pipeline is the same thing: you run it, run it again because of a network failure, run it one more time in a backfill, and the final table stays identical. Re-runs are harmless by design.

And why does this matter so much? Because in a distributed system, **running twice is not the exception, it is routine**. A job dies halfway through and the orchestrator retries. Streaming reprocesses an event after a *checkpoint recovery*. A retroactive correction forces you to redo the past. If every re-run changes the number, you do not have a pipeline, you have a roulette wheel.

## Where the problem is born: the plain INSERT

The villain is almost always the same. An `INSERT` that only knows how to *add* rows:

```sql
INSERT INTO vendas_mes
SELECT * FROM staging_vendas;
```

First run: 100 thousand rows. Reprocessed: 100 thousand more. Now there are 200 thousand, half of them duplicates, and `SUM(valor)` has doubled. The INSERT has no memory of what is already there. It just stacks. That is exactly what doubled my revenue.

## The conceptual fix: natural key + MERGE

The turnaround has two parts, and the order matters.

**1. Define the natural key.** It is the business identifier that says "this row is *this* sale, not another one". It can be `pedido_id`, or the combination `cliente_id + data + produto`. Without that key, the system has no way of knowing whether an incoming row already exists. I see people skip this step and jump straight to the tool. Do not skip it: the natural key is the foundation, the MERGE is just the bricklayer.

**2. Replace the plain INSERT with MERGE (upsert).** The MERGE compares each incoming row against what already exists, using the key: if it exists, it **updates**; if it does not, it **inserts**. "Upsert" is the contraction of update + insert.

```sql
MERGE INTO vendas_mes AS alvo
USING staging_vendas AS origem
  ON alvo.pedido_id = origem.pedido_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

Now run that MERGE ten times. On the second pass, every `pedido_id` already exists, so each row *updates to itself* with the same value. Zero duplicates. The number holds steady. This is what the industry calls *exactly-once* at the destination: the event queue may deliver the same sale twice (*at-least-once* is the norm), but the key-based upsert at the destination absorbs the repetition without complaint.

One detail I learned the hard way: **MERGE without the right key saves no one**. If the `ON` condition matches multiple rows, or if the key is not actually unique, the MERGE goes back to duplicating. The reliable natural key is what makes the magic happen, not the command.

![Plain INSERT versus MERGE/upsert when the pipeline runs twice: the plain INSERT just stacks and the total goes from 100 thousand to 200 thousand rows, doubling SUM(valor); the MERGE by natural key updates each row to itself and the total holds steady at 100 thousand. The natural key thinks, the MERGE executes.](images/01-insert-vs-merge.png)

## Mental checklist before shipping any pipeline

I run these four questions in my head before deploying:

- **If I run this twice in a row, does the final table change?** If yes, it is not idempotent. Go back.
- **What is the natural key?** If you cannot name it in one sentence, it does not exist yet.
- **Is it a plain INSERT or a MERGE/upsert?** A plain INSERT into a destination table is a red flag.
- **Does a retroactive-correction backfill break the numbers?** If it does, the problem will surface at the worst possible moment, with the data already wrong in production.

![The four idempotency questions before deploying: if I run it twice in a row, does the final table change? What is the natural key? Is it a plain INSERT or a MERGE/upsert? Does a retroactive-correction backfill break the numbers? Concept first, tool later.](images/02-checklist.png)

Idempotency is not a perfectionist engineer's frill. It is what lets you sleep well knowing that reprocessing the past will not double the present. Concept first, tool later: the natural key thinks, the MERGE executes.

In Ep 04 we go one step up and talk about real *backfill*, now that you have the safety net to run the past without fear.
