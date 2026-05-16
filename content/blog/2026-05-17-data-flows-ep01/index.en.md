---
title: "Data Flows Ep01: the concept that comes before any tool"
description: "First episode of the Zero to Expert series. Data leaves one place and arrives at another. Why that simple mental model solves half of the difficulties in production."
tags: ["zero-to-expert", "data-flows", "fundamentals", "data-engineering"]
images:
  - cover.png
---

Before any tool, any language, any framework, there's a simple concept that sits underneath everything in data engineering.

Data leaves one place and arrives at another. That's a data flow.

It seems too simple. But most of the difficulties data engineers face in production, from broken pipelines to data arriving late or inconsistent, can be traced back to confusion about where the data is born, what happens to it on the way, and where it ends up.

This is the first episode of the Zero to Expert series I've been building. The goal isn't to teach a tool. It's to build the mental model that makes all the tools make sense.

## Where data comes from

Every flow starts at a source. A source is any system that produces information: an e-commerce database with customer orders, a payments API recording each transaction, IoT sensors on a production line, log files from a server.

The source doesn't worry about analytics. It worries about operations. The e-commerce database was built to process orders fast, not to answer "which product sells most on Tuesdays in November."

That tension is the starting point of every data architecture: operational systems are optimized for writes, analytical systems are optimized for reads and aggregations. A data flow connects the two.

## What happens in the middle

Between source and destination, data goes through transformations. These transformations can be simple or complex, but they always exist.

**Ingestion** is the first step: bringing data from the source into your environment. It can be a full copy of the table, only what changed since last time, or a real-time stream of events.

**Transformation** is where raw data becomes useful information. Standardized names, null values handled, duplicates removed, different tables joined, aggregations computed. This is where business rules show up: what does a "complete" order mean? When is a transaction considered fraud? What's the retention criterion for this customer?

**Destination** is where the transformed data lives to be consumed: a dashboard, a machine learning model, a report delivered every Monday by email, a system that makes automated decisions.

## The difference between batch and streaming

This is the first architectural decision that defines how a pipeline behaves.

**Batch** processes data in blocks at a defined time. The report runs every morning at 6am and covers the last 24 hours of transactions. The data isn't real time, but it's much simpler to build, debug, and maintain. Most of the world's analytical pipelines are batch.

**Streaming** processes each event the moment it happens. When you open your banking app and the last transaction is already there, that's streaming. When a fraud system blocks a card in milliseconds, that's streaming.

The choice isn't about which is better. It's about which one the use case demands.

A monthly sales report for leadership doesn't need streaming. Forcing streaming here adds complexity without benefit.

A credit card fraud detection can't be batch. A 24-hour processing cycle would let fraud happen for hours before it gets caught.

The most common mistake is using streaming when batch solves the problem, because streaming feels more sophisticated. The cost is real: more complex infrastructure, harder debugging, more failure points.

## Why this matters in your work

I've learned over time that when a pipeline breaks in production, the first question is always: where in the flow did the problem happen?

At the source? Data didn't arrive, the API went down, the schema changed.

In ingestion? The job failed, the schedule shifted, the connection expired.

In transformation? A business rule produced an unexpected result, a null wasn't handled, a table that should exist doesn't.

At the destination? The dashboard is showing wrong data, the model received stale features, the email was sent before processing finished.

Being clear about each step of the flow is what lets you debug fast. Without that mental model, you stare at logs without knowing where to start.

## What's coming in the next episodes

In the next editions of the Zero to Expert series, I'll go deeper into each part of this flow:

- How ingestion works in practice, the formats that matter, and the mistakes every engineer will make at least once
- What a transformation layer is, and when to use SQL, Python, or Spark
- How to choose where data lives: data warehouse, data lake, lakehouse
- Orchestration: what keeps this whole flow running reliably

Each episode will have real examples and a decision at the center, not theory.

If there's a specific concept you'd like me to cover in the series, send it on [LinkedIn](https://linkedin.com/in/thaisvaz) or subscribe to the [newsletter](https://vazdeng.substack.com) to get the next episodes.
