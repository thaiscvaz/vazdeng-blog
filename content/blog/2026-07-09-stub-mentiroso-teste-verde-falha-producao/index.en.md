---
title: "Green build, production on fire: when the test stub teaches a lie about the real lib"
slug: stub-mentiroso-teste-verde-falha-producao
date: 2026-07-09
publishDate: 2026-07-09
draft: false
description: "A frontier model scored low on a coding benchmark with a 100% green CI. The bug was shielded by its own mock. A green test does not prove correct integration."
tags: ["ferramentas"]
images:
  - cover.png
---
A coding agent delivered the whole project. Docker building, Compose up, green CI, clean RuboCop, Brakeman with no alerts, a polished README, test suite passing. On paper, senior work. On the app's first real conversation, `NoMethodError`. The core feature, the one thing the product needed to do, was broken since the first commit. And no test caught it.

This case is not hypothetical. It is what Fabio Akita documented in his July 2026 coding benchmark, reading the code by hand instead of trusting the automated score. And it exposes the trap I fear most when reviewing AI-generated code: the test that passes right on top of the bug.

## The mock that validates the hallucination

Akita's benchmark is always the same request: build, unassisted, a ChatGPT-style chat in Rails 8 with RubyLLM, Hotwire and Docker, with tests and CI. He then reads the result by hand and grades it from 0 to 100.

Sonnet 5, a model with a strong name, scored 58 out of 100, Tier C, position 25. The shell was flawless. The core, dead. The model called `chat.messages = history`, a setter that RubyLLM version 1.16 simply does not have. In production, that blows up on the first message.

Here is the part that matters to anyone who writes tests. The bug did not slip through despite the suite. It slipped through because of the suite. `FakeChat`, the test double (mock, or stub) the project itself created to test without hitting the real API, defined `attr_accessor :messages`. In other words, the mock invented the setter the real library does not offer. The test ran against an idealized version of the lib, confirmed an API that does not exist, and painted everything green.

The mock did not fail to catch the bug. It taught the bug to the test.

## Green is not a sign of integration, it is a sign of agreement with the double

The lesson is not about Ruby or about one specific model. It is about what a green test actually measures. It measures that your code agrees with the double you wrote. If the double mimics the dependency's real contract, great, the green is worth something. If the double mimics a version you imagine the lib has, the green is a polite lie.

The contrast in the same benchmark shows the difference. Gemini 3.5 Flash scored 93, Tier A, using RubyLLM's real API: `with_instructions`, history replay with `add_message`, `complete`, `response.content`. Everything exists, everything integrates. Sakana Fugu Ultra scored 79 with an app that booted and chatted, but only sent the last message to the model. The interface looked like a chat. The model worked as if every message were the first. Green on the outside, no memory on the inside.

Three models, three degrees of "it works". Only reading the code by hand separated what integrates from what pretends to integrate.

## What I changed in how I test LLMs

I read generated code and I do not trust an agent's green suite without looking at the mock first. I started treating the double as the most dangerous part of the test, not the most boring one. The question I ask on every LLM integration stub is a single one: does this fake mimic the real library, or a version that happened to be convenient for the test to pass?

In practice that becomes three habits. Pin the exact version of the dependency and generate the double from its contract, not from memory. Keep at least one test that brings up the real integration, even if it runs slowly and outside the per-commit CI. And distrust every green that arrives too fast at a touchpoint with an external library.

In Brazil this weighs more than it seems. A bug shielded by a mock does not show up in a green pipeline. It shows up on the customer's first real interaction. And then the cost is not the missing test, it is the incident the suite promised would never happen.

The verdict is simple and uncomfortable. A green build proves your code agrees with your assumptions. It does not prove your assumptions about the lib are right. As long as the grade comes from inside your own world of doubles, it may be congratulating you on the bug. The only audit that catches this is still reading the code and running the real thing. No green replaces that.
