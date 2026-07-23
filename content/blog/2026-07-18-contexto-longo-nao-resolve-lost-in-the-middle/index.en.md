---
title: "IA Foundations 07: a 1M token window solves nothing if the information lands in the middle"
slug: contexto-longo-nao-resolve-lost-in-the-middle
date: 2026-07-18
publishDate: 2026-07-18
draft: false
description: "Lost in the middle is not a bug, it is an attention pattern. Position beats context size, and a critical rule on line 300 is accuracy thrown away."
tags: ["ia", "agentes"]
images:
  - cover.png
series: ["ia-foundations"]
episode: 7
---

There is a promise sold in every new model release in 2026: "now with 1 million tokens of context, the model reads your entire repository". The correct reading is different. The model reads everything, but it uses what sits at the beginning and at the end far better. What lands in the middle gets ignored at a rate most teams never measure, and then debug as if it were a reasoning failure.

This is not opinion. It is [Liu et al. 2023](https://arxiv.org/abs/2307.03172), the paper that became known as "Lost in the Middle: How Language Models Use Long Contexts".

## What the paper showed

The authors ran two controlled tasks: multi-document QA and key-value retrieval. In both, they placed the key information at different positions in the context and measured accuracy. The result was consistent: a U-shaped curve. Accuracy is high when the answer is at the beginning, high when it is at the end, and drops 20 to 30 percentage points when the answer sits in the middle.

This holds for GPT-3.5, Claude 1.3, and open models with explicitly long context (MPT, LongChat). It is not a problem of one specific model. It is a pattern of the Transformer architecture: tokens at the beginning are attended to by every subsequent token. Tokens at the end attend strongly to each other. Tokens in the middle receive proportionally less attention during generation. It is attention geometry, not bad engineering.

![The U-shaped curve from Liu et al. 2023. Model accuracy is high when the key information is at the beginning of the context, high when it is at the end, and drops 20 to 30 percentage points when the information lands in the middle. The pattern holds for GPT-3.5, Claude 1.3 and open long-context models. A critical rule in the middle of the file is accuracy thrown away.](images/01-curva-em-u.png)

## Why this is the opposite of what the market promises

Every large-window release in 2026 is sold as "everything fits, you no longer need to organize". That is a half-truth that misleads the team. Yes, it fits. No, the model does not use the middle the same way it uses the edges. Whoever feeds in an entire 800 thousand token codebase trusting the model to reason about line 400 thousand is sitting in the deepest valley of the U curve.

Anthropic and OpenAI document this in their own guidelines: critical instructions belong at the top, and control information should be "concise and high priority". It is not a style suggestion. It is a direct consequence of the paper.

## Where I saw this show up in practice

My global `CLAUDE.md` grew by accumulation. Identity, matrix rule, world-class standard, vault policy, meal system, date rule, privacy policy. It all ended up in the same file, and the file became a thousands-of-lines encyclopedia. While it was small, everything worked. After it passed a few hundred lines, I started noticing that the model applied the rules at the top and at the end with precision, and frequently ignored the ones in the middle.

The fix was not shrinking it by forcing a summary. It was changing the file's architecture: the entry file became a ~150 line router with identity, ten inviolable rules and links to thematic policies loaded on demand. The rules that were stacked in the middle migrated to dedicated files in `~/.claude/policies/`. Each policy declares its own trigger. The model loads it when needed, and the entry file stays short enough to fit inside the high-attention region.

## The anti-pattern I see most

"The context is big now. I'll just throw everything in."

If you have 300 documents and the information needed to answer sits in document 150, the probability of the model picking it up is significantly lower than if it were in document 1 or document 300. Putting 300 documents in a large window does not solve retrieval. It is retrieval done in the worst possible attention geometry.

What solves it is preserving the hierarchy of importance. Critical information at the top. Secondary information can go at the end. What is left goes to an external file loaded on demand, or to a short index pointing to the detail. This is what the harness engineering community calls "entry file = router, not encyclopedia".

## What to do with this in practice

Three simple decisions, in order:

1. **Measure the size of your instruction files.** Any entry file (CLAUDE.md, AGENTS.md, system prompt) above 300 lines is an immediate refactoring candidate. It is not an arbitrary target, it is the empirical limit where the middle region starts to hurt.

2. **Put the non-negotiable rules at the top of the file, always.** Do not trust writing order. Order is the model's attention wavelength.

3. **Document why each rule is there.** Without origin history, nobody removes a rule from the middle or moves it to an external file, because it feels dangerous. A rule without origin context rots in the middle of the file.

A 1M token window is not a solution. It is an opportunity to better structure the context you already had, or it is laziness dressed up as progress. That part is up to you.
