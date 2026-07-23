---
title: "Zero to Expert · Ep 02: DAG dependencies, the law every orchestrator obeys"
slug: dependencias-dag-lei-orquestrador
date: 2026-06-13
publishDate: 2026-06-13
draft: false
description: "Before picking Airflow, Dagster, Prefect or anything else, understand the graph."
tags: ["dag", "airflow", "orquestracao", "zero-to-expert"]
images:
  - cover.png
series: ["zero-to-expert"]
episode: 2
---

You want to learn pipeline orchestration and there are 8 tools to choose from. Airflow, Dagster, Prefect, Mage, Argo, Temporal, Luigi, Kestra. Every tutorial assumes you already understand what comes before the tool. I worked with one of them in production for 2 years, and what unlocked me wasn't mastering the syntax. It was understanding the concept all of them implement under the name. That's what I'll cover today.

This is ZTE Ep 02. Zero to Expert is the track that makes you stop following tutorials and start understanding. Episode 01 covered data flow. Today it's the DAG's turn.

## DAG: three letters that show up everywhere

DAG stands for Directed Acyclic Graph. Break the acronym into 3 parts:

- **Graph:** a set of nodes connected by edges. In a pipeline, each node is a task (load a table, transform, validate, save). Each edge is a dependency (task B can only run after A finishes).
- **Directed:** the edge has a direction. If A points to B, B depends on A. Not the other way around. This matters because pipelines have order.
- **Acyclic:** you can't get back to the starting node by following edges. There is no A → B → C → A. If there were, you could never start. Who would run first?

Visually: picture a network of tasks where every arrow points forward, and no path takes you back to the beginning. That's a DAG.

![Anatomy of the DAG acronym: a graph of nodes and edges, directed with ordering, acyclic with no path back](images/01-anatomia-dag.png)

## Why every tool uses a DAG

Airflow, Dagster, Prefect, Mage, Argo Workflows, Temporal, Luigi, Kestra. All of them model pipelines as DAGs. It's not coincidence. It's the natural structure for representing task dependency.

The execution algorithm is the same in all 8 tools: topological ordering of the graph, then parallel execution of nodes with no mutual dependency. Topological ordering is just a sequence that respects the edges (A before B whenever A points to B).

The complexity of computing that order and detecting cycles is O(V+E) with depth-first search, where V is the number of nodes and E the number of edges. In a real pipeline DAG, that's milliseconds. The computational cost isn't in this part. It's in running the tasks themselves.

That's why learning the DAG first unlocks every future tool. The syntax changes. The Python of an Airflow DAG is not the Python of a Dagster DAG. But the concept is the same. After 2 years maintaining Airflow DAGs, I can read pipelines from any orchestrator I've never run. The graph underneath is always the same.

## A real-world example: Brazil's instant payment system

Pix is Brazil's instant payment rail, run by the central bank. A transfer is not a single API call. It's a DAG with dozens of nodes that has to complete in under 10 seconds to meet the regulator's SLA.

The simplified chain of one transfer:

1. Message pre-processing (parse, format validation).
2. Anti-fraud validation (rules + risk model + blocklist checks).
3. Balance check at the source bank.
4. Amount hold on the source account.
5. Settlement at the central bank's instant payment system.
6. Settlement confirmation.
7. Credit at the destination account.
8. Push notification to the receiver.
9. Push notification to the payer.
10. Statement updates at both banks.

Each node depends on the previous ones in a specific order. Anti-fraud depends on the parse. Settlement depends on the hold. Notification depends on the credit. None of these steps can run before its predecessor. And several can run in parallel (push notification and statement update can be simultaneous).

That whole chain is modeled as a DAG. If you ripped that out and tried to do it with nested if/else, it would turn into spaghetti in 3 days and become unmaintainable in a week.

![The Pix DAG: 7 nodes in sequence from parse to credit in under 10 seconds, with notifications in parallel afterwards](images/02-dag-do-pix.png)

## When the DAG breaks: the circular anti-pattern

Circular dependency is the most common mistake while learning. Task A needs B's output, B needs A's output. You can't execute either. The pipeline dies at initialization.

The good news is that every tool detects this before running:

- **Airflow:** raises `AirflowDagCycleException` at DAG parse time.
- **Dagster:** raises `DagsterInvalidDefinitionError: cycle in graph` when loading the definition.
- **Prefect:** validates the flow and fails with a circular dependency error before the first deploy.

The bad news is that whoever doesn't understand the concept sees the error and doesn't know what to do. They rewrite the DAG by trial and error, convinced it's a tool bug. It isn't. It's the algorithm telling you that what you defined is impossible to execute.

The fix is almost always rethinking task granularity. If A and B need each other, they're actually one task, or you're modeling input and output wrong.

![Circular dependency: A needs B and B needs A, the pipeline dies at initialization, and the error each tool raises](images/03-ciclo-impossivel.png)

## Learning the DAG unlocks every orchestrator

Understanding DAGs unlocks every orchestration tool, present and future. You swap Airflow for Dagster without trauma. You read someone else's pipeline code and understand it. You sketch the pipeline on paper before picking a technology.

The opposite is also true. Whoever only knows the tool's syntax is hostage to it. When the tool changes (and they change every year), they relearn everything. Whoever understood the concept just adjusts the syntax.

It's the criterion I use to learn anything new in this field: concept first, tool second. Zero to Expert is not about knowing many tools. It's about knowing the concepts no tool teaches.
