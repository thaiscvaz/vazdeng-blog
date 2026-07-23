---
title: "Stop writing prompts by hand: DSPy and TextGrad treat prompts as compilable code"
slug: dspy-textgrad-pare-de-promptar-na-mao
date: 2026-07-02
publishDate: 2026-07-02
draft: false
description: "Improving a prompt is not manual copywriting, it is compilation against a metric. Two Stanford frameworks prove it, and one landed in Nature."
tags: ["ferramentas"]
images:
  - cover.png
---
Every time I watch someone tweaking a sentence in a prompt, running it, checking the result and going back to tweak the sentence again, I see the same scene from fifteen years ago: a guy editing server config over SSH in production, saving, reloading, praying. We stopped doing that with infrastructure. We invented Terraform, declared the desired state, and let the tool apply it. With prompts, most teams are still on production SSH, turning knobs by eye.

The thesis of this post is uncomfortable on purpose: improving a prompt should not be manual writing work. It should be compilation against a metric. You describe the behavior you want, define what counts as success, and let an optimizer discover the text that maximizes it. DSPy and TextGrad, both out of the Stanford ecosystem, are the two serious implementations of that idea I would look at today.

## The handcrafted prompt is software without tests

Let me be blunt about why the current state bothers me technically. A hand-written prompt has every sin we fought against in code and pretended not to see in LLMs.

It is not versionable in any meaningful way. The diff of a prompt is a diff of prose, and nobody can tell whether the new version is better or worse without running it by hand. It is not testable: you adjust the sentence, improve one case, break three others you did not notice. It is not reproducible: the person who wrote it knew why that word was there, they left the company, and now that line is tacit knowledge embedded in a string. That is the literal definition of fragile software. The difference is that we normalized it.

> In one sentence: hand-written prompts are the last stronghold of non-declarative configuration that engineering still tolerates, and DSPy and TextGrad are the serious attempt to kill it.

The inversion both of them propose is the same one that happened with compilers. You do not write assembly. You describe the logic in a high-level language and let the toolchain generate the low-level code, better than you would write by hand and in a reproducible way. DSPy and TextGrad want to do that with the prompt: the prompt becomes the assembly you never edit directly again.

## DSPy: you declare the contract, the optimizer compiles the prompt

DSPy is maintained by Stanford NLP and the name stands for **Declarative Self-improving Python**. The official README describes itself, word for word, as "the framework for *programming, rather than prompting, language models*". The concrete proposal is that you stop writing the prompt text and declare three things in Python.

**Signature** is the input and output contract of an LLM call, like `context, question -> answer`. It says what the call does, not how to prompt it. **Module** is the block that implements an inference strategy on top of the signature, such as `Predict`, `ChainOfThought` or `ReAct`, and you compose modules in a normal Python program with loops and conditionals. **Optimizer** is where the magic happens: it takes your program, a metric function that scores the output and a few examples, and automatically adjusts the instructions and selects the few-shot demonstrations to maximize the metric.

The optimizer I would cite as the state of the practice is MIPROv2. The official documentation describes what it does with no hedging: "Generates instructions *and* few-shot examples in each step. The instruction generation is data-aware and demonstration-aware. Uses Bayesian Optimization to effectively search over the space of generation instructions/demonstrations across your modules." In plain terms: it generates instructions and examples, takes your data into account, and uses Bayesian optimization to sweep the space of possible prompts efficiently.

The final step is called `compile`. And the name is honest: what comes out is an executable pipeline with the prompts already optimized, frozen, versionable. You compiled your prompt from code, data and a metric. You did not write a single sentence.

```python
import dspy

class GerarResposta(dspy.Signature):
    """Answer the question using the retrieved context."""
    contexto = dspy.InputField()
    pergunta = dspy.InputField()
    resposta = dspy.OutputField()

otimizador = dspy.MIPROv2(metric=minha_metrica_de_acerto)
rag_compilado = otimizador.compile(programa, trainset=exemplos)
# rag_compilado carries instructions + few-shot optimized by the metric
```

## TextGrad: same goal, via textual gradients

TextGrad attacks the same problem from another angle, and this one deserves a pause because it came out in Nature. The paper is called "Optimizing generative AI by backpropagating language model feedback", published in *Nature* in 2025, volume 639, pages 609 to 616, from James Zou's group at Stanford. I made a point of checking this on Nature itself before writing, because "published in Nature" is the kind of claim that turns into LinkedIn legend far too fast.

The insight is to replicate the mechanics of PyTorch's autograd, except the gradient is not a number but natural-language feedback generated by an LLM. You wrap the text to optimize in a `Variable` with `requires_grad=True`, define a loss in natural language ("evaluate whether this answer is correct and complete"), and when you call `.backward()` an LLM produces a textual critique of how that variable should change. The TGD optimizer (Textual Gradient Descent) applies that critique and rewrites the text. Forward, loss, backward, step. The same choreography as neural network training, with prose in place of numbers.

The practical timing difference between the two matters when choosing. **DSPy optimizes at compile time**: you compile once against a set of examples and freeze the program for production. **TextGrad optimizes per feedback iteration**: each cycle refines the variable, and it can run in a loop. Conceptually both do the same deep thing, training the LLM system without touching the model's weights, by changing the text that orchestrates it.

## Manual versus compiled, side by side

| Dimension | Hand-written prompt | DSPy / TextGrad |
|---|---|---|
| How it improves | editing prose by eye | optimizing against a metric/loss |
| Versionable | text diff with no meaning | compiled, reproducible artifact |
| Testable | "I ran it and it looked better" | explicit metric scores the output |
| Who holds the knowledge | tacit, in the writer's head | code + data + metric |
| Model swap | rewrite everything by hand | recompile against the same metric |
| Cost | cheap per iteration, expensive in aggregate | expensive at compile, cheap after (DSPy) |

And a quick table of DSPy versus TextGrad, because they are not interchangeable:

| | DSPy | TextGrad |
|---|---|---|
| Timing | compile-time, freeze and serve | iterative, critique loop |
| Unit | program of modules + signatures | text variable + natural-language loss |
| Natural fit | pipelines (RAG, classification, agents) | optimizing an output/code/solution via critique |
| Origin | Stanford NLP | Zou Group, Nature 2025 |

## The honest verdict: when it pays off and when it is overkill

I am professionally skeptical of tool hype, so the verdict comes with the downside spelled out.

It pays off when the prompt is **repeated, measurable and high-volume**. A pipeline that runs every day, that you can score objectively, where a quality gain multiplies across thousands of executions. That is exactly where handcrafted prompts accumulate the most silent debt, and where compiling pays back the investment. For classification, structured extraction, RAG with verifiable answers, it is the golden case.

It does not pay off, and here is the heart of the Tool Verdict, in three situations I would refuse outright.

**One-off.** If the prompt runs once or ten times, the cost of building a metric, a trainset and running the optimizer (which makes many LLM calls in the process) exceeds the cost of just writing a decent prompt by hand. Compiling to throw away is waste.

**Weak metric.** The entire value depends on a metric function that captures real quality. If the metric is bad or biased, the optimizer maximizes the wrong metric with frightening competence. It is pure Goodhart: the measure becomes the target and stops being a good measure. For subjective output with no reliable labels, the gain evaporates.

**No volume.** Without repetition to dilute the compile cost, the math does not work. Bayesian optimization and textual gradient loops burn API calls. If you will not amortize that at scale, it ends up more expensive than the problem.

Another point of technical honesty: neither of them changes the model's weights. They optimize the text that orchestrates the LLM, they do not do fine-tuning. If the bottleneck is the base model's capability, recompiling the prompt will not fix it. And the tooling still evolves fast, so for a critical pipeline I would pin versions and test, without treating it as stable long-term infrastructure.

## Anti-patterns

- Adopting DSPy for a one-line classifier that already works. Dependency and complexity with no return.
- Compiling against a metric you do not trust. You will beautifully optimize the wrong thing.
- Thinking "compiled" means forever. The artifact depends on the model that generated it; swapped models, recompile.
- Blindly trusting the TextGrad loop. It is stochastic (an LLM evaluating an LLM) and can oscillate or regress between iterations. It needs verification on top.
- Running the optimizer without budgeting the API cost first. The compile makes many calls; measure before.
- Repeating the mantra "prompt engineering is dead". It is not. It became compilation in the right case, and it stays handcrafted in the small case.

If you maintain any LLM pipeline in production, the checklist question is a single one: is my prompt an artifact compiled against a metric I trust, or a magic string someone tuned by eye that nobody dares to touch? If it is the second, you do not have a prompt. You have technical debt that looks like text.
