---
title: "Retroactive lineage is technical debt. Document at decision time or lose it."
slug: evidence-as-byproduct-auditoria-multi-agente
date: 2026-06-20
publishDate: 2026-06-20
draft: false
description: "The Audit Envelope Pattern I learned the hard way: instrumenting later always costs more than instrumenting upfront."
tags: ["engenharia-de-dados"]
images:
  - cover.png
---
End of quarter. Audit knocking on the door. 47 Airflow jobs, 12 dbt models, roughly 200 chained transformations.

Simple question: where does this transaction data come from?

Expected answer: a SQL query against a catalog, answered in seconds.

What actually happened: 4 engineers, 2 weeks, trying to reconstruct by hand what should have been documented. Interviewing whoever wrote each job. Reading 18-month-old code. Discovering that half the comments were wrong or outdated.

I was on that team. And I learned the hard way that retroactive lineage does not exist. There is only lineage instrumented at decision time.

## Why "adding lineage later" does not work

The problem is not technical. It is cognitive.

When you reconstruct lineage after the pipeline has run, you are not documenting what happened. You are documenting what you think happened, based on code that may have changed, comments that may be wrong, and the memory of whoever wrote it months ago.

In real production, jobs change. Parameters change. Today's source for "customers" may not be the same as 6 months ago. Without instrumentation at execution time, you lose the "when" and the "with exactly what".

Tools like OpenLineage and Unity Catalog Lineage help. But they capture structure, not decision context. They know job A read from table B. They do not know why that job ran on that day with those specific parameters.

## The Audit Envelope Pattern

What I use today is a simple pattern I call the Audit Envelope. Every job, every dbt model run, every LLM call in a pipeline, emits a YAML header before running:

```yaml
audit:
  job_id: ingestion_transacoes_pix
  run_id: "{{ run_id }}"
  timestamp_utc: "{{ ts }}"
  input_hash: "sha256:{{ source_file_hash }}"
  output_hash: null  # filled in at the end
  prompt_version: null  # LLM jobs only
  parent_invocation: "{{ dag_id }}/{{ task_id }}"
```

That envelope travels with the data. When the data lands in Silver or Gold, the envelope lands with it. The catalog indexes it. The audit becomes a SQL query.

Practical result: when the audit came back 6 months later, the answer took 45 minutes. 4 engineers were not needed. One query was.

## Why LGPD and model governance will force this

LGPD Art. 20 gives the data subject the right to request a review of any decision made solely through automated processing, and to receive clear information about the criteria used. "The model approved this credit" is not a sufficient answer. "Model version 2.3, with features Y, ran with these parameters at this moment, against this exact input" is.

The direction is not only Brazilian. In April 2026, the Fed, FDIC and OCC replaced SR 11-7 with a more principles-based model risk guidance. Generative and agentic AI were formally left out of that guidance's scope, but the principles are already being applied to those systems by analogy. The reading that circulated in the market captures the spirit well: evidence has to be a byproduct of how the model is built, not reconstructed afterwards.

Retroactive lineage satisfies neither. The Audit Envelope satisfies both as a natural consequence of instrumentation.

The difference between compliance as technical debt and compliance as a byproduct of good engineering is when you instrument. Before is free. After is expensive.

Today I instrument every new pipeline with an Audit Envelope from the first job. The cost is one Python function that emits the header and one extra field in the destination schema.

The cost of not doing it is 2 weeks of 4 engineers at the end of a quarter when everyone is already at their limit.

I do that math once and never need to do it again.
