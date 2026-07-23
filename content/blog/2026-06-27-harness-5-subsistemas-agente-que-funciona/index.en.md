---
title: "The 5 subsystems that separate an agent that works from one that only looks like it works"
slug: harness-5-subsistemas-agente-que-funciona
date: 2026-06-27
publishDate: 2026-06-27
draft: false
description: "Last week I wrote that the LLM does nothing, the harness does. This post opens the hood: the five subsystems every working agent needs."
tags: ["ia", "agentes"]
images:
  - cover.png
series: ["ia-foundations"]
episode: 4
---
Last week I wrote that the LLM does nothing, the harness does. I got several messages agreeing, and one that stuck with me: "ok, I get that the harness matters. But what IS the harness, in practice?". Fair. That post proved THAT the harness is what moves the agent. This one opens the hood and shows WHAT is inside. There are five subsystems. Miss one, and you get the agent I call "only looks like it works": beautiful demo on Friday, broken on Monday in production.

I use this five-piece model as a checklist every time I build a new agent, and it has already saved me from more than one pipeline that looked ready and was not.

## The model: five pieces, none optional

Picture a new cook in your kitchen. To deliver a dish, they need five things. Take any one away and the best chef in the world becomes useless. An agent is the same.

**1. Instructions.** The house recipe book. Not the world's menu, but what THIS kitchen does: overview, commands, constraints, links. In the agent, that is the `CLAUDE.md` or `AGENTS.md`. It answers "what is the universe of rules I operate in?". Without it, the agent generates generic solutions instead of reasoning about YOUR code.

**2. Tools.** The knives, the pans, the stove. The actions the agent knows how to execute: shell, edit files, search, run tests. It answers "what can I do?". Without tools, there is no point asking it to "try harder".

**3. Environment.** The stocked pantry, the gas turned on. The self-explanatory state of the environment: `pyproject.toml`, `.python-version`, Docker. It answers "where am I, is everything installed?". Without it, the agent spends half the session getting organized before starting.

**4. State.** The note the previous shift's cook left about the half-finished dish. Where we stopped, why we decided X: `PROGRESS.md`, `feature_list.json`, commits. It answers "what happened before this session?". Without State, every session starts from zero.

**5. Feedback.** The trained palate, the thermometer, the timer. What counts as "it worked": `pytest`, `mypy`, `make check`, declared upfront. It answers "how do I know I finished well?". Without Feedback, the agent serves the dish "thinking it tastes fine".

![The five harness subsystems in the kitchen analogy: Instructions (the recipe book), Tools (the knives and pans), Environment (the stocked pantry), State (the previous shift's note) and Feedback (the palate and the thermometer). Feedback is the piece that is almost always missing; without it the agent only looks like it works.](images/01-cinco-subsistemas.png)

## The agent that only looks like it works

Almost always, the same subsystem is missing: **Feedback**.

The agent without Feedback is the most dangerous one because it is convincing. It writes the code, marks the task as done, returns exit 0. Everything looks fine. Then you inspect the trace and discover that half the files were written by another model in a silent fallback, or that the tests are coverage theater that never exercises the real logic. Akita documented exactly this in a recent benchmark: a model in opencode kept hitting a protocol error that the harness buried in the event stream and fell back silently. The run "completed", the files were written, and only in the trace could you see that the real author was someone else. Exit 0 is not success.

![Exit 0 is not success: what you see (exit 0, task done, beautiful demo) versus what the trace reveals (silent fallback to another model, tests that never exercise the logic, code written by someone else, broken in production). 65% of enterprise AI failures are harness defects, not model defects.](images/02-exit-zero.png)

The lesson I carried into my own data engineering pipelines: never trust "returned without error". I instrument verification of expected output, not just exit codes.

And the numbers I saw this week back it up: [Atlan's analysis of harness failures](https://atlan.com/know/agent-harness-failures-anti-patterns/) attributes 65% of enterprise AI failures to harness defects (context drift, schema misalignment, state degradation), not to the model. And [LangChain's ablation study](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering) took a fixed GPT-5.2-codex from 52.8% to 66.5% on Terminal Bench 2.0 by changing only the surrounding infrastructure, without touching the model. The missing piece is always one of these five subsystems.

## When you do NOT need all five

This matters, because the opposite is a trap too. If what you want is a one-shot script, "summarize this text", "classify these 50 emails", one call and done, you need no harness at all. There is no next session, so no need for State. There is no environment to navigate, so Environment is irrelevant. Assembling all five subsystems for a one-shot task is pure overengineering. The full harness pays off when the agent operates continuously, over a real environment, across multiple sessions. My open-source projects, a data engineering agent and my crypto project, are those cases. A summarization prompt is not.

## The mental model that stays

The five subsystems are not a rigid recipe, they are an inventory. Before approving a new agent, I run the checklist: does it have Instructions? Tools? Environment? State? Feedback? If one is missing, the harness is incomplete, and the agent will let you down exactly when you start trusting it. The difference between working and looking like it works almost always lives in the fifth piece, the one nobody wants to build because it takes effort and never shows up in the demo.
