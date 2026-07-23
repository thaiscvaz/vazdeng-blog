---
title: "You're running everything on the most expensive model: routing by role cuts 60-70% of your agent bill"
slug: roteamento-de-modelo-corta-70-custo-agente
date: 2026-06-30
publishDate: 2026-06-30
draft: false
description: "In an agent swarm, only irreversible decisions justify the frontier model. Everything else is coordination, implementation, artifact transformation."
tags: ["engenharia-de-dados"]
images:
  - cover.png
---
The question nobody asks when building a multi-agent system is the most expensive one: which model runs each agent?

The default answer is silent and devastating. You open the session on the strongest model you have, and every sub-agent it spawns inherits that model by inertia. The agent that writes the final runbook runs at the same reasoning level as the agent that decides the data lake architecture. You are paying surgeon rates for someone to fill out a form.

When I built my data engineering squad with 16 agents, this was the first bill that bothered me.

## The cost lives in the agent, not the call

> In one sentence: in a hierarchical swarm, most of the token volume is coordination and routine implementation, and running that on the frontier model is pure waste.

Let me separate this from a previous post I wrote about prompt caching, because it is easy to confuse the two. Caching attacks the **prefix**: you reuse the repeated chunk of the prompt (system prompt, context, documents) and pay a fraction on the re-read. That is one axis. Model routing attacks a completely different axis: **which brain** processes each task. Caching makes the same call cheaper. Routing chooses not to use the R$ 25 brain when the R$ 5 one delivers the same result.

The two stack. But confusing one with the other makes you optimize half the problem and think you are done.

The model bill on Anthropic's API makes the waste glaring. Public prices today:

| Model | Input (US$/M tokens) | Output (US$/M tokens) |
|---|---|---|
| Opus 4.8 | 5.00 | 25.00 |
| Sonnet 4.6 | 3.00 | 15.00 |
| Haiku 4.5 | 1.00 | 5.00 |

Opus output costs 5x Haiku output. If half your swarm is people writing final documents, handoffs and runbooks (transformation work on content already decided), you are paying 5x more per output token for tasks Haiku does with sufficient quality. Multiply that by thousands of runs a month and the bill stops being noise.

## The decision: 16 agents routed by type of cognitive work

The principle I adopted has a name in the swarm literature: Heterogeneous Agentic Mesh, or Executive-Worker. The Executive (frontier model) decides. The Workers (smaller models) execute. The rule I wrote for my squad was: **each agent explicitly declares the model that runs it, according to the type of cognitive work of the role**, and that declaration has to match between the agent's frontmatter and the audit record it emits. If they diverge, the phase gate locks.

I classified the work into three types:

| Type of work | Model | Why |
|---|---|---|
| Irreversible decision (framing, architecture, security gate) | Opus | An error contaminates the whole chain or violates compliance. Worth maximum capability. |
| Coordination and structured implementation (breaking down issues, standard code, IaC) | Sonnet | Pattern is defined, demands consistency, does not demand frontier reasoning. |
| Transformation of finished artifacts (final doc, runbook, handoff) | Haiku | Content already decided. Speed and cost matter, reasoning does not. |

In practice that became 4 Opus, 10 Sonnet, 2 Haiku. Who got Opus in my squad:

- The **product owner**, who frames the problem. An error in the PRD contaminates architecture, plan and code downstream. It is the most upstream decision of all.
- The **data architect**, who decides Medallion, partitioning and governance. Those are irreversible choices, they become permanent records.
- The **AI engineer**, who decides RAG architecture, multi-agent design and guardrails.
- The **QA and security reviewer**, the last gate before deploy. A false negative here is critical.

Notice the criterion. It is not "this agent is important". Every agent is important, otherwise I would not have it. The criterion is: **is this role's error reversible?** If the architect gets the partitioning wrong, I reprocess terabytes and rebuild pipelines. If the tech writer gets a sentence wrong in the runbook, I fix the sentence. Error costs in different orders of magnitude justify models in different orders of magnitude of price.

The 10 Sonnets are the body of the work: the project manager breaking down issues, the Python and PySpark developers implementing transformations, the discovery agents sweeping the idea in parallel fan-out, the reasoners exploring architecture options. Structured work, clear pattern, high quality without needing the frontier.

The 2 Haikus are the tech writer and the QA critic, which applies a fixed checklist over an already consolidated report. Critique of a finished artifact, not a gate decision.

## Frontmatter as a cost contract

The part that makes this real, and not just good intentions, is that the model choice became a versioned, auditable field. In the agent:

```yaml
---
name: data-architect
tools: Read, Write, Edit, Grep, Glob
version: v1.1.0
model: opus
---
```

And when the agent finishes, it records in the audit envelope which model actually ran it. If the orchestrator detects that the frontmatter says Opus and the envelope says Sonnet, it locks until I confirm. That closes the classic hole: someone edits an agent, forgets the model field, and three months later you find out half the swarm drifted to the wrong model and nobody saw it on the bill.

The table is not eternal. I left it written that it gets reevaluated when an agent accumulates evidence of underperformance on its assigned model, or when Anthropic ships a generation that shifts the price/capability frontier. But changing it requires an explicit argument in the commit. "Felt like a good idea" does not count. "I saw this artifact fail X times on Haiku" does.

## Why this matters for the bill in reais

The point that connects to the reality of anyone paying cloud bills in Brazil: LLM cost in production is a recurring expense in dollars, and the dollar keeps climbing. Every agent you bump up a tier without need is a multiplier on the end-of-month bill, converted at the day's exchange rate.

The 2026 swarm literature points to cuts in the range of 60 to 70% in token cost when model choice respects the type of work of each role, without losing quality on the decisions that matter. That is not a number I measured on my squad (it is a blueprint, it does not run production volume yet), it is the range the literature on the pattern reports, which is why I treat it as a market estimate. The mechanism, though, is arithmetic: if 12 of the 16 agents moved from Opus to Sonnet or Haiku, and Sonnet costs 60% of Opus while Haiku costs 20%, the aggregate drops on its own. The only question is whether quality holds, and it holds as long as the irreversible decision stays on the frontier.

An honest caveat about a number that circulates a lot. The MIT report (Project NANDA, "State of AI in Business 2025") found that 95% of generative AI pilots in companies produce no measurable return, based on more than 300 implementations. The data is real, but the cause the report points to is the "learning gap" and poor workflow integration, not cost discipline. So I do not attribute the 95% to cost, because MIT does not. What I do claim, on engineering grounds, is more modest: a system whose economics do not close does not survive next year's budget cut, no matter how good it is technically. Cost discipline is a survival condition, not an elegance condition.

## Anti-patterns

- **Opening the session on the strongest model and letting every sub-agent inherit it.** It is the silent default. You never decided to run the tech writer on Opus, you simply never decided otherwise.
- **Routing by agent "importance" instead of error reversibility.** Every agent is important. The right question is the cost of being wrong, not the prestige of the role.
- **Leaving the model choice implicit in the code.** If it is not in a versioned, auditable field, it will drift with nobody watching, and you find out on the bill.
- **Confusing routing with caching.** They are orthogonal axes. Doing one and thinking you covered the other leaves half the savings on the table.
- **Cutting Opus from the irreversible decision to save money.** The inverse of waste is equally dumb. Saving on problem framing is where the error gets most expensive.

## Checklist before your next agent deploy

- [ ] Does each agent have its model declared in an explicit field, not inherited by inertia?
- [ ] Does each model choice pass the "is this role's error reversible?" test?
- [ ] Are the irreversible decisions (framing, architecture, security gate) on the frontier, and only them?
- [ ] Is there any mechanism that locks when the model that actually ran diverges from the declared one?
- [ ] Can you say, without opening the bill, what fraction of your swarm runs on each tier?

If you answered no to any of these, you are probably paying Opus prices for Haiku work. Which agent in your system runs on the most expensive model without needing to?
