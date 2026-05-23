---
title: "Twenty AI concepts you need to understand in 2026"
description: "The complete visual guide to how AI works, from the basics to the frontier. Six sections, twenty concepts, no spare jargon."
tags: ["ai", "llm", "fundamentals", "rag", "agents", "embeddings"]
images:
  - cover.png
---

![Twenty AI concepts you need to understand in 2026](images/infografo.png)

Every week a new AI term shows up. Agent, RAG, fine-tuning, embedding, top-p, RLHF. You open LinkedIn and three people are already "building autonomous agents" before breakfast. Over on Twitter someone complains their RAG hallucinates while the next post debates whether it's worth fine-tuning Llama 3. Then you head to the API docs you were going to test for something simple and walk into a hundred-word glossary before the first useful call.

The problem isn't the number of terms. It's that nobody stops to draw how they connect.

This infographic is my attempt at a map. Twenty concepts, six sections, a sequence that makes sense if you go from the base to the frontier. It's nowhere near everything that exists in AI. But you can open it in a technical meeting in 2026 and understand what people are talking about, or read the code of an agentic system and identify what each piece is doing in the flow.

## How AI works (1 to 4)

It all starts with **neural networks**. Layers of neurons connected by weights, adjusted during training to make predictions. That's the only primitive of all this. Models that see images, models that write text, models that understand audio: all variations of the same thing, with different architectural choices on top.

For language to enter that network, it needs to become a number. That's what **tokenization** does: break text into chunks the model can chew on. AI doesn't read words. It reads tokens. Then each token becomes a vector in a space of hundreds of dimensions, and that's an **embedding**. Similar meanings sit close together. It's what makes semantic search, recommendation, and RAG work.

On top of those three comes **attention**. The mechanism that lets each word look at every other word in the input and decide what matters to it. Before attention, models read text in sequence and forgot the beginning by the middle of the sentence. Attention broke that bottleneck. Without it, the rest of contemporary AI simply wouldn't exist in the form we know today.

## The magic behind it (5 to 8)

**Transformers** are the architecture that packaged attention into something trainable in parallel. Before them, language models were slow and short. After them, they became GPT, Claude, Gemini.

But architecture without data is nothing. **Pre-training** is the phase where the model reads the equivalent of the Library of Alexandria. Trillions of tokens. This is where it absorbs syntax, grammar, facts about the world, and the patterns of reasoning that humans left in writing. **Fine-tuning** is what comes next: take that general model and specialize it on specific tasks with specific data. And **RLHF** is the stage that took models that could answer anything and taught them to answer in a way that's actually useful to someone. Real people compare outputs, say which one is better, the model learns the preference. It's what separates "a model that knows a lot" from "a model that converses well."

## Beyond the models (9 to 12)

No model goes to production on its own. Around it sits a layer of **safeguards**: filters and classifiers built on explicit rules, to keep the system from saying something that hurts someone or reproduces an obvious bias. That's the boring part nobody wants to build and that every serious product needs to have.

And when the model needs to know something that wasn't in pre-training, in comes **RAG**. Retrieval-Augmented Generation. The system fetches relevant documents, injects them into the context, and the model answers grounded in them. RAG depends on two close relatives: **vector databases** (which store embeddings in a way that lets you find the nearest match in milliseconds) and **chunking** (which breaks large documents into indexable pieces). RAG without good chunking is RAG that hallucinates elegantly.

## How AI generates output (13 to 14)

When the model answers, it doesn't write the whole sentence at once. It predicts one token, then the next, then the next. That's **decoding**. And how it picks each next token completely changes the character of the output. High **temperature** gives creativity and variation. Low **top-p** sharpens focus on the most likely tokens. Tuning these two parameters is the difference between a model that writes poetry and a model that writes technical documentation.

## How AI acts (15 to 16)

Up to here the model only responds. **Agents** are the next step: it decides and acts. Receives an objective, breaks it into steps, picks which tool to use, executes, observes the result, adjusts the next step. **Tools and functions** are the hands we give to that agent: API, calculator, search, code execution, database access. Without them, the agent gets stuck in its own head talking to itself. The part that actually matters about agentic systems starts when the model can finally call something that changes state in the real world.

## Improvement and evaluation (17 to 20)

Agentic systems without explicit **planning** turn into chaos fast. Without rigorous **evaluation**, any claim about the model just became cheerleading. **Iterative improvement** is what separates a pretty prototype from a system that survives in production: test, measure, adjust, repeat. And **bias and fairness** has an inconvenient property: if you ignore it at design time, it will find you in the incident.

## Closing

AI isn't magic. It's math with data on top, logic around it, and iteration at the center. People who understand these twenty concepts read agentic system architecture without getting lost in the glossary. They can debug weird model behavior from real hypotheses instead of guesses. And in a technical conversation, they speak like someone who took part in the build, not like someone who read the release.

Take the infographic. Save it on your phone, print it and put it on the wall, drop it in Notion. Come back to it every time a term that feels new shows up. And more important than any of that: build something with it. You only discover what each of these words really means when you try to make a RAG actually work.

---

*This is the first post in the AI Foundations track at [VazDEng](https://vazdeng.substack.com). Three posts a week on data engineering in Portuguese (and English), at the senior level Brazil was missing.*
