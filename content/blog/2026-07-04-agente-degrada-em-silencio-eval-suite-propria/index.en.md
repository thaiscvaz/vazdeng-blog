---
title: "Your agent is degrading in silence. I built a 9-eval suite to prove it"
slug: agente-degrada-em-silencio-eval-suite-propria
date: 2026-07-04
publishDate: 2026-07-04
draft: false
description: "Measuring only the final output hides regression. Without per-step, per-role evals, agents get worse unseen. The 9 golden cases that stop it."
tags: ["ia", "agentes"]
images:
  - cover.png
series: ["ia-foundations"]
episode: 5
---
You ship an agent, it works, you tweak the system prompt to improve one thing. The final answer still looks good. You deploy. Three weeks later the security reviewer stops catching a hardcoded key in a diff it would have caught blindfolded last month. Nobody saw it happen. The final output never looked wrong.

This is the most expensive failure mode in agentic systems, and the least discussed. The agent does not break loudly. It degrades in silence, and the only evidence shows up when the error has already reached the customer.

I built my own eval suite to stop finding out too late. Nine golden cases, three agents, deterministic grading. I calibrated it against real responses and it passes 9 out of 9 today. The value is not in the number, it is in what each case protects.

## Why the final output lies

> In one sentence: evaluating an agent means auditing the entire trajectory (every reasoning step, every tool call, every intermediate decision), not just checking whether the last token came out right.

An agentic system takes N reasoning steps and K tool calls before producing the output. Measuring only the end is a poor metric for three concrete reasons:

- The agent gets the output right for the wrong reason. It passes the test, breaks on the next case.
- The agent calls the wrong tool, gets garbage back, recovers, and still lands on the result. It passed, but it cost 3x, and the next recovery may not happen.
- The agent hallucinates an intermediate decision and reaches the right answer by luck. That is a time bomb with an approval stamp.

The analogy I use: a reviewer who only reads the last commit of a PR sees the result, not the process. They miss that the dev tried three wrong approaches, pasted a sketchy snippet in commit 2, and only got it right at the end. A good eval reads the diff of every commit. You can say "step 4 is where it broke, even though the final output looked OK".

This is not my personal theory. The paper that coined TRACE, "Beyond the Final Answer: Evaluating the Reasoning Trajectories of Tool-Augmented Agents", opens with exactly this critique: evaluation stays stuck on matching the final answer and ignores critical aspects of the trajectory such as efficiency, hallucination, and adaptability. The τ-bench benchmark went after the same hole from another angle, multi-turn conversations against a simulated user, measuring whether the agent sustains the domain policy throughout the dialogue instead of just looking good on turn 1.

## What to measure when "it passed" is not enough

The agent-eval literature separates three metrics that look the same and are not:

| Metric | What it measures | Why it matters in production |
|---|---|---|
| Pass@K | Getting it right in at least 1 of K attempts | Good for offline batch where you run K times and pick the best. Lies about production. |
| Pass^K | Getting it right in all K attempts in a row | Consistency. An agent in production needs to be right repeatedly, not once in the lab. |
| Avg@K | Average score across K attempts | Stability. High variance between attempts is a red flag. |

τ-bench uses Pass@k and Pass^k precisely to expose inconsistency across seeds. High Pass@1 with high variance hides fragility, and the agent's customer will hit the bad execution, not the good one. When you only look at "it passed once", you are measuring the best case of a system that will run in the worst.

## Inside the suite: cases, agents, and deterministic answer keys

My suite covers the three agents that carry the most risk in my data engineering squad. Each one gets three cases, and picking those three is not "three variations of the same test". It is detection plus a false-positive guard, always.

The rule I learned and that holds everything up: an agent that rejects everything also passes a naive detection-only eval. If you only test "does it catch the vulnerability?", the easiest way to pass is to scream vulnerability on every diff. That is why every agent has at least one case where the right behavior is to approve or stay quiet.

| Agent | 3 cases | What a failure means |
|---|---|---|
| `qa-security-reviewer` | planted hardcoded secret, planted SQL injection, clean diff (false-positive guard) | the QA gate stopped catching basic vulnerabilities, or started making them up |
| `qa-critic` (mode B) | scope drift, faithful contract (false-positive guard), vague verification | the Reflexion layer stopped protecting the Sprint Contract |
| `discovery-compliance` | personal context (must not inflate regulation), banking PII (must trigger LGPD+BACEN), public context | the compliance axis regressed on the anti-inflation rule or on a real banking obligation |

Let me open one case to show the level of fidelity. `case-01-hardcoded-secret` injects a Silver ingestion diff with a storage key and an API token embedded in the code, plus a `verify=False` on the HTTPS call. The answer key does not check free text. It requires, via regex, that the response contain: the notion of a hardcoded secret (bilingual, because the agent answers in PT-BR with the word order inverted, "chave em texto plano"), a mention of a secret vault or environment variable as the remedy, the disabled-TLS problem, and severity at blocker or critical. Four anchors. If any of them fails after a prompt bump, the bump regressed the agent.

The mirrored case, `case-03-clean-diff`, does the opposite. It sends a pure, clean transform, and the answer key has an empty `must_find` and a `must_not_find` that forbids the response from mentioning "sql injection", "hardcoded secret", or "remote code execution". A style nit is tolerable. A fabricated security finding is not. That pair is what actually measures calibration: detecting what exists without inventing what does not.

In `discovery-compliance` the detail gets even finer. The personal-context case forbids the response from applying banking regulation to a local personal project, but the regex was calibrated to allow the agent to cite BACEN or PCI-DSS in order to mark them as "does not apply". Punishing the mention was a grading artifact. The forbidden pattern matches the application verb ("subject to", "mandatory", "requires"), not the name of the norm. The banking-PII case requires the exact inverse: LGPD, BACEN, the notion of personal data/CPF, all at high risk. The same agent has to know the difference between the two contexts. That is what no final-output metric captures.

## Deterministic on purpose, and why I live with the low ceiling

The grading is pure regex. All `must_find` patterns match, no `must_not_find` matches, case-insensitive, against the agent's response.

| | Deterministic (what I use) | LLM-as-judge |
|---|---|---|
| Cost | Zero, runs in seconds | Tokens per evaluation |
| Reproducibility | 100% | Not reproducible |
| Coverage | Only what you anticipated | Semantic nuance, free-form output |
| Its own risk | Fails on valid output with unexpected format | The judge's own bias |

I do not use LLM-as-judge here on purpose, and it is not laziness. Judge bias is documented and large. The literature measures position bias reaching 75% preference for the first-positioned response, and self-preference bias of 10 to 25% when the judge evaluates content from its own model. A 2026 RAND study found that no judge is uniformly reliable across benchmarks. Bringing a judge like that into my pipeline without a deterministic anchor would be trading one measurement problem for a worse one. The discipline I follow: deterministic wherever possible, LLM-as-judge only enters when the regex proves insufficient in a real regression. Evidence first, not hypothesis.

The cost of this rigor is honest: the regex covers "missed the planted vulnerability" and "inflated regulation on a personal project". It does not measure subtle reasoning quality. I accept that ceiling because the class of error that hurts me most is the gross and silent one, not the subtle one.

One operational detail that saves money: the full run costs nine LLM calls and does not live in CI. What lives in CI is the `--dry-run`, which validates the structure of the cases without spending tokens. The process rule is manual and explicit: every PR that changes the `prompt_version` of a covered agent has to paste the output of the full run into the description. CI guarantees the structure, the operator guarantees the semantic verification at the right moment, which is the prompt bump.

## Anti-patterns I have seen up close

- Evaluating only the final output. You are measuring the best case of a system that runs in the worst. High Pass@1 with high variance is fragility disguised as quality.
- A detection-only suite, with no false-positive guard. A paranoid agent that rejects everything passes those tests and is useless. Always pair detection with a case where the right answer is to approve.
- LLM-as-judge as the first choice. You inherit position bias and self-preference bias before having any deterministic anchor. Start with regex, escalate to the judge only with evidence that regex cannot handle it.
- A giant synthetic golden dataset. Fifty to two hundred hand-curated cases, covering real error types seen in production, are worth more than ten thousand generated cases covering abstract structure.
- Fragile regex that breaks in silence. In my case, escaping layers between YAML and Python's `re` killed a pattern without warning. Calibrate every regex against a real response before trusting it, otherwise your eval degrades along with the agent.

## Checklist to build yours before the next prompt bump

If you run agents in production and have never measured trajectory, start here:

- [ ] Did I list the 2 or 3 agents that carry the most risk if they regress? (Do not try to cover them all.)
- [ ] Does each one have at least one detection case with a deliberately planted vulnerability or error?
- [ ] Does each one have at least one false-positive guard case, where the right answer is to approve or stay silent?
- [ ] Is the grading deterministic wherever possible, with no premature LLM-as-judge?
- [ ] Was every regex calibrated against a real response, not written from memory?
- [ ] Is the full run tied to the right trigger (a `prompt_version` bump), instead of running pointlessly in CI burning tokens?
- [ ] Is the golden dataset versioned alongside the agent's code?

When a golden case starts failing, the question is not "how do I make it pass". It is "is the golden outdated, or did the agent regress?". Answering that consciously, case by case, is the difference between an eval suite and eval theater.
