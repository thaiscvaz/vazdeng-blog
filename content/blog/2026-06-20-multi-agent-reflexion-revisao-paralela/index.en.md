---
title: "Why asking AI to review its own code does not work (and what does)"
slug: multi-agent-reflexion-revisao-paralela
date: 2026-06-20
publishDate: 2026-06-20
draft: false
description: "IA Foundations 03: asking the same model to self-correct can degrade reasoning. The multi-agent alternative reaches 82.6% on HumanEval."
tags: ["ia", "agentes"]
images:
  - cover.png
series: ["ia-foundations"]
episode: 3
---
There is a tempting pattern in AI pipelines: ask the model to generate, then ask the same model to review what it generated.

It sounds smart. The logic is appealing. The model will look with "fresh eyes" and catch what it got wrong on the first pass.

It does not work. I tested it, saw it in the results, and there is research showing that in some cases it makes things worse.

But there is a version that works. The difference is in who does the reviewing.

## What Reflexion is and why it fails

Reflexion is a framework published by Shinn et al. in 2023. The idea is simple: the agent generates an answer, receives feedback on what it got wrong, and tries again. Iterative, self-correcting.

It worked well enough to become standard in a lot of systems. The problem is what happens after the second or third iteration.

The model falls into what researchers call degeneration of thought. Instead of exploring different paths, the agent starts repeating the same mistakes with slightly different words. The self-critique becomes performative. The model "knows" it got it wrong, mentions the mistake, and makes it again.

Why does this happen? Because the same model with the same weights will have the same reasoning patterns. You can change the prompt, give explicit feedback, ask for different perspectives. Underneath, it is the same process generating variations of the same output.

Huang et al. 2023 (arXiv:2310.01798) showed that intrinsic self-correction, without external feedback, can actually degrade the model's reasoning. This is not marginal. In several cases, asking a model to review itself hurts more than it helps.

## MAR: multiple agents, multiple reasoning patterns

The MAR paper (arXiv 2512.20845) starts from a direct diagnosis: if the problem is that an LLM cannot escape its own patterns, the solution is to have different patterns.

MAR chains four stages with distinct agents:

**Actor:** generates the initial solution. It does not know it will be reviewed.

**Evaluator:** tests the output and flags when there is a failure. It is the trigger for the review, not the reviewer itself.

**Persona critics:** when the Evaluator flags a failure, multiple critics, each with a different persona, debate what broke. It is not a single critic handing down a verdict. It is distinct perspectives arguing with each other.

**Judge:** synthesizes the critics' debate into a Consensus Reflection, the consolidated diagnosis that instructs the Actor to redo the work.

The separation forces different perspectives. Each critic attacks the problem from a different angle, the debate exposes blind spots a single reviewer would miss, and the judge has no authorship bias because it did not generate the original solution.

The results: HumanEval (a coding benchmark) went from 76.4% to 82.6%. HotPotQA reached 47% exact match. Both beat single-agent Reflexion.

## The real cost and when it is not worth it

MAR is not free. The overhead is roughly 3x in API calls compared to plain Reflexion. In a pipeline that uses an LLM on every event, that changes the operational cost significantly.

When it makes sense: code going to production where mistakes are expensive, decisions that touch customer data, complex SQL generation that will run on financial data, situations where reviewing manually afterward costs more than 3x the API bill.

When it does not: simple one-shot tasks, extracting structured fields from standardized documents, any case where you already have automated tests that catch the errors that matter.

The logic is the same as any cost decision in engineering: the extra cost has to be lower than the cost of the error you are preventing.

IA Foundations 02 showed that the model does nothing. The harness does. This post is the next step: when the harness asks the model to review itself, results are poor. When the harness orchestrates multiple roles with independent perspectives, results improve.

The pattern is not "AI reviews AI". The pattern is different roles with different responsibilities producing reasoning that no single role can.

It is what I use in production today. The paper confirms why it works.
