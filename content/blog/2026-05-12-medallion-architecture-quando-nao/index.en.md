---
title: "When Medallion Architecture gets in the way more than it helps"
description: "Medallion became the default answer for any pipeline. Where it works, where it gets in the way, and the anti-pattern nobody talks about."
tags: ["medallion", "lakehouse", "databricks", "data-architecture"]
images:
  - cover.png
---

There's an architecture pattern I've watched grow since 2020, created by Databricks, adopted by Microsoft as the official standard for the Fabric platform in 2023, and that today shows up in almost every conversation about data engineering: Medallion Architecture.

Bronze, Silver, Gold. Raw data, clean data, aggregated data.

The problem isn't the pattern. The problem is that it became the automatic answer. And when any architecture becomes the automatic answer, it starts creating more problems than it solves.

Databricks itself is clear in the official docs: *"Following the medallion architecture is a recommended best practice but not a requirement."*

That rarely shows up in the presentations.

## What Medallion Architecture actually is

Databricks defines it like this: a design pattern that organizes data in a lakehouse into layers that *progressively improve* the structure and quality of the data, from Bronze to Silver to Gold.

**Bronze** stores data exactly as it came from the source, with no transformation. It's the immutable historical archive. If something goes wrong in later layers, you come back here.

**Silver** applies the minimum transformation needed to create a consistent enterprise view: cleansing, standardization, deduplication, joins across sources. It's where data becomes trusted information.

**Gold** organizes data for specific consumption: analytics dashboards, ML models, financial reports. Denormalized, optimized for reads, designed for the end user.

Worth a historical note: the layered pipeline concept isn't new. Data warehousing in the 1990s already used staging, cleansed, and presentation layers. What Databricks created in 2020 was the Bronze/Silver/Gold terminology and the "Medallion" branding, not the principle itself. That doesn't make the pattern invalid, it just helps separate innovation from naming.

## When Medallion works well

The pattern solves three real problems, and solves them well.

**First: reprocessing without loss.** When a bug shows up in a Silver transformation, you go back to Bronze and reprocess without having to fetch the data from the source again. In systems where the source only keeps the last 90 days of history, that protection can be the difference between fixing a problem and losing two years of data.

**Second: multiple teams with different needs.** The analytics team needs monthly totals. The data science team needs the data at the finest grain for model training. Both share Silver, each builds its own Gold layer independently. No duplicated cleansing work, no inconsistency across views.

**Third: separation of responsibility in large teams.** The ingestion team owns Bronze without needing to know business rules. The transformation team owns Silver without depending on the ingestion team. In organizations with more than 20 data professionals working in parallel, this reduces coupling and blockers.

When these three problems exist, Medallion is a solid choice. When they don't, you're adding complexity without a return.

## Where Medallion starts to get in the way

### When there's a single consumer

You have a pipeline that ingests payroll data to feed a single HR dashboard. One team consuming, one purpose, one transformation.

Applying Medallion here means creating Bronze, Silver, and Gold to serve exactly the same thing. The data goes through three layers of reads and writes, three sets of jobs to monitor, and three times the latency. For zero gain.

The practical signal: if Gold is identical to Silver plus one grouping, you don't need three layers. A single direct transformation from source to consumed table does the same work with half the infrastructure.

A case documented by a data architect: a customer had 4.2 billion rows in Bronze accumulated over six years of data, but Silver only consumed the last 90 days. 97% of stored data was never used. The storage cost was real, the benefit wasn't.

### When latency matters more than quality

Each transition Bronze to Silver, Silver to Gold, is a separate job. In Spark pipelines, that's usually 20 to 40 minutes per layer. Three layers in sequence and total latency tops one hour before data reaches anywhere.

Analyses with real practitioner data show overhead of 53% or more in simple cases: 23 minutes with Medallion versus 15 minutes with direct transformation, for the same result.

When the business needs data in 30 minutes to make a decision, an architecture with 80 minutes of latency isn't a code problem. It's an architecture problem.

For data that needs to arrive in real time or near it, Databricks is explicit: it recommends micro-batch (latency in seconds to a few minutes) for Medallion, and explicitly advises that when ingestion comes from a message broker like Kafka, reading directly without an intermediate stage reduces complexity and latency. For sub-second, the documentation itself flags limitations in real-time mode that negatively affect throughput.

### When it's a prototype or short-lived analysis

A quick data exploration. A model that will exist for three months. A one-off analysis that will turn into a number on a slide and never be consumed again.

Forcing Medallion onto a prototype creates tables that will never be maintained, jobs nobody will monitor, and structure that will be abandoned in two weeks. The team spends time and energy organizing what was supposed to be disposable.

A prototype needs to be quick to build and easy to throw away. Three layers make both harder.

### When the team is small and the data is simple

A startup with 3 data engineers processing 500 GB doesn't have the same problems as a bank with 50 engineers and 50 TB. The operational overhead of maintaining Bronze, Silver, and Gold, with all the tables, jobs, documentation, and monitoring that requires, can be unjustifiable when the real benefit is small.

For small teams with one or two use cases, two layers (raw data and consumable data) or a solution with dbt directly on the source solve the problem without the extra complexity.

## The anti-pattern nobody talks about

I've seen one specific problem appear more than any other when Medallion doesn't work well: Bronze gets exposed as a data product.

Elliott Cordo, a data engineer with published work on data architecture, documents this as a direct anti-pattern: exposing the Bronze layer to consumers creates strong coupling between those using the data and the internal details of how it's stored. When the source changes, every consumer breaks together.

The second documented problem: when Silver is Bronze with a renamed field, and Gold is Silver with a GROUP BY, the intermediate layers add no real value. Analysts end up writing complex SQL in Gold or building parallel spreadsheets to compensate. Multiple teams implement the same metric in different ways, and the numbers start to diverge.

In those cases, the pattern isn't being applied, it's being imitated.

## The right question before deciding

Three questions define whether Medallion is the right architecture:

**Are there multiple consumers with different needs?** If yes, a shared layer between them makes sense. If not, you're creating separation without benefit.

**Is reprocessing data from the source expensive or impossible?** If yes, immutable Bronze is real protection. If you can reprocess without cost or history loss, the benefit shrinks.

**Does the latency of each layer fit the deadline the business demands?** If yes, Medallion works. If not, you need a different architecture for that use case.

Three "yes": Medallion is a solid choice. Two or fewer: worth questioning how many layers you actually need.

![Decision diagram: when to use Medallion Architecture](images/decision-tree.svg)

## What large companies actually use

An important detail that rarely shows up in the discussions: Netflix and Uber, two of the most referenced companies in data engineering, don't use Bronze/Silver/Gold terminology.

Netflix uses the WAP pattern (Write-Audit-Publish) with Apache Iceberg: data is written to a hidden snapshot, audited automatically, published if approved. The problem solved is the same (quality before exposure), but the implementation is different and doesn't use Medallion's three layers.

Uber uses a transactional data lake with Apache Hudi, with raw, derived, and aggregated tables. The migration from full batch to incremental ETL cut pipeline time by 82% and cost by 78%, according to the Uber Engineering Blog in March 2023. But those numbers are from incremental ETL, not from the layered pattern itself.

Microsoft adopted Medallion as Fabric's official architecture in 2023 and is today the largest public case of institutional adoption. Even so, Microsoft's own documentation guides: before building complex pipelines between layers, evaluate Materialized Lake Views, which manage transformations automatically without operational overhead.

## What stays

Medallion Architecture is a good pattern for the right problems: large teams, multiple consumers, critical data that needs protected history and progressive quality.

It isn't required. It isn't universal. And when applied where it doesn't fit, the cost is real: unnecessary latency, wasted storage, operational complexity without benefit.

Architecture choices should start from the problem, not from the pattern. What does this pipeline need to solve? Who will consume it? What's the acceptable deadline? Is reprocessing from the source expensive?

If the answers point to Medallion, great. If they don't, a simpler architecture will work better.

Have you ever implemented Medallion somewhere it didn't belong? What happened next? Tell me on [LinkedIn](https://linkedin.com/in/thaisvaz) or subscribe to the [newsletter](https://vazdeng.substack.com) for the next posts.
