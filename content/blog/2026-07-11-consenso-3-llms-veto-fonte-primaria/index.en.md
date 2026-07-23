---
title: "Your LLM agrees with what you want to hear. And that is an architecture bug, not a prompt bug"
slug: consenso-3-llms-veto-fonte-primaria
date: 2026-07-11
publishDate: 2026-07-11
draft: false
description: "Sycophancy is automated confirmation bias. You fix it with architecture: independent models, confidence-weighted consensus and a primary source that vetoes the rest."
tags: ["ia", "agentes"]
images:
  - cover.png
series: ["ia-foundations"]
episode: 6
---
You can prove it in ten seconds. Paste a controversial article into your assistant and tell it to tear the piece apart. It does. Paste the same article and ask for a defense. It defends it with the same conviction. Same text, opposite answer, and you picked which one without noticing. The model is not searching for the truth. It is predicting which answer you probably want to hear, given how you phrased the question.

This has a name: sycophancy. And the most honest way to describe it is automated confirmation bias. When I use an LLM to evaluate anything, a blog pitch, a reading note, a piece of code, I had to face the uncomfortable fact that my question almost always carries the answer I already want. The model senses that and delivers.

I learned the structure of the defense by reading Frank Investigator, an open source project by Fabio Akita that analyzes news. It does not say whether a story is true or false. It exposes what the article chose to omit. And the most interesting part for anyone building systems with AI is not the subject, it is the anti-bias architecture behind it.

## Why a better prompt does not fix it

The temptation is to believe there is a magic prompt. "Be impartial", "actually be critical", "do not take my side". It does not work, because the problem is not in the wording, it is in the relationship. If the operator has an opinion, the model knows which side to please.

Frank's insight is that no human ever asks the model an open question. Every stage of the pipeline has a closed, specific prompt, like "list the rhetorical fallacies in this excerpt" or "extract the factual claims from this sentence". The operator never states an opinion, so there is no side to please. Neutrality comes from taking human preference out of the loop, not from politely asking the model to be neutral.

## The three parts that lock out the flattery

The defense is architectural, and it has three gears that apply to any evaluation pipeline, not just news.

First, consensus across models from different companies. Frank runs the same question through three LLMs from distinct vendors. A single model carries its house biases. Three of them disagreeing exposes where the answer is fragile.

Second, the consensus is weighted by confidence, not by majority. If two models say "supported" with 70% certainty and one says "mixed" with 95%, the "mixed" weighs more. Simple majority would let the weak guess beat the confident judgment. A model that stays inconsistent across rounds goes into quarantine.

Third, and most important, the primary source veto. If official data, a court ruling or an original study contradicts the claim, confidence is capped at 60% and the verdict is forced to "mixed", even if all three models say "supported" in unison. Truth over consensus. Ten newspapers citing each other with no primary source are worth zero. And the system even detects when "five sources confirm" but all of them belong to the same editorial group, like Folha and UOL, or Globo and G1. It knows that is one voice disguised as five, and reduces the weight.

The project's central message is that the strongest signal of manipulation is not the lie, it is the omission. None of the cases it analyzed contained a fabricated fact. The game was in what each outlet chose not to say.

## What this teaches anyone building agents

The pattern is the same one that sustains good AI systems in general: the LLM proposes, a deterministic mechanism verifies and measures before closing. The primary source veto, the circular citation detection and the weighted consensus are all deterministic. None of them is "AI judging AI", which would only stack bias on bias.

I use this in practice every time a model evaluates something for me. The question can never carry the answer I want. The output needs an external veto anchored in hard evidence. And if the only proof of a claim is the model itself repeating it with confidence, that is not evidence, it is an echo.

To give a sense of scale, Frank has 19,444 lines of Ruby and 9,190 of tests, 15 analyzers and three models in consensus, all open under AGPL. It is not a prompt toy. It is decision engineering, and the lesson that sticks is short: if you want AI to tell you the truth, the last thing you can do is let it guess which truth you prefer.
