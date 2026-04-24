---
title: "Real data engineering content in Portuguese is rare. I'm going to help change that."
slug: real-data-engineering-portuguese
date: 2026-04-18
draft: false
description: "Why a senior data engineer with experience at Apple, Itaú, EBANX and Bradesco decided to start writing, and what you'll find here."
tags: ["manifesto", "data engineering", "databricks", "crypto", "master's"]
images:
  - bookshelf.png
---

The kind of data engineering content in Portuguese where you can tell the person actually lived what they're writing about, that's hard to find.

Search right now. You'll find a lot of solid material to start with: translated articles from English blogs, tutorials grounded in the official docs, courses teaching Pandas on simple datasets. All of that has its place, it's where most people start, and the people producing it are doing important work.

What's still hard to find is someone telling you how they decided to use Delta Lake instead of Parquet in an environment processing hundreds of millions of daily transactions. Or when Medallion Architecture helps and when it just gets in the way. Or how LGPD (Brazil's data privacy law) actually changes the way you design an ingestion layer.

That's the gap I want to help fill.

![Empty bookshelf labeled "Data engineering · Português" with a silhouetted figure placing the first book](bookshelf.png)

## Who I am, by what I've built

I won't list certificates. I'll tell you what I've shipped.

I started at Itaú Unibanco, where I received the MÉRITO Prize for data quality work. Then moved to EBANX while it was still a fast-growing fintech, building ETL pipelines processing 100M+ daily transactions. After that, I led an international team at HCL Technologies on Apple projects in Silicon Valley, managing 500M+ daily events. Today I'm a senior data engineer at Bradesco, one of Brazil's largest banks.

My core stack is Databricks. Not because I read the docs. Because it's what runs in production where I've worked.

In 2024 I started a Master's in Numerical Methods in Engineering at UFPR (Federal University of Paraná). My research is on AI-driven predictive monitoring using LLMs for operational systems. Everything I learn there I plan to bring here, translated into something useful for engineers working with real data.

## Why crypto entered the story

A few years ago I started studying on-chain analytics. And I noticed something that few people seem to be saying clearly: crypto, in large part, is a data engineering problem that's still poorly solved.

The data is all there. On-chain, open, public. But most people investing in crypto don't know how to process it, and many data engineers still aren't looking at it.

So I decided to build a crypto AI agent from scratch. In public, documenting every architecture decision. Using the same tools I use at work: real pipelines, rigorous backtesting, actual statistical models. No hype, no get-rich-quick promises.

## What you'll find here

Three tracks, one newsletter.

The first is **production data engineering**: Databricks, Delta Lake, Spark, dbt, Airflow. Real architecture decisions, mistakes I made and what I learned, Brazilian context where it's relevant (LGPD in practice, cloud cost reality, what data actually looks like inside financial institutions).

The second is the **crypto AI agent**, built in public. Architecture, code, backtesting, on-chain analysis. Every step documented. If something breaks, you'll know why.

The third is the **master's research translated to practice**. What academic research has to say about the problems you face every day. No filter, no academic jargon.

Published in Portuguese and English, every week.

Hit reply and tell me: what's the hardest data problem you're dealing with right now? I read everything.

Thais Vaz

[Newsletter on Substack →](https://vazdeng.substack.com)
