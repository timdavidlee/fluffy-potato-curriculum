# Anatomy of an LLM API call

```yaml
title: Anatomy of an LLM API call
keywords: llm, api call, token, context window, temperature, cost, mental model, anthropic, claude
estimated duration: 10
```

> **Lesson:** L01 — LLM and token basics.
> **Roadmap:** see this lesson's [objectives.md](../../../../docs/origin/lesson_roadmaps/L01/objectives.md).
> This is a short framing piece. Read it before the main lecture
> ([L0102_lecture.md](L0102_lecture.md)) and the four teacher demo notebooks
> (tokens [L0103_lecture.ipynb](L0103_lecture.ipynb), context window
> [L0105_lecture.ipynb](L0105_lecture.ipynb), cost [L0106_lecture.ipynb](L0106_lecture.ipynb),
> temperature [L0108_lecture.ipynb](L0108_lecture.ipynb)).

## Why this lesson exists

This is the first lesson of the course. Before we can build agents, prompt well, or wire up
tools, we need a working mental model of what an LLM *is at the API level* — not the math
inside it, but the contract you interact with when your code talks to a model.

Everything from L02 onward assumes you can look at a prompt and answer three questions almost
reflexively:

- **How many tokens is this?** (roughly)
- **How much will it cost?** (roughly)
- **Will it fit in the model's context window, with room for the answer?**

If those questions feel like magic, the rest of the course will feel like magic too. The goal of
L01 is to turn them into back-of-envelope engineering.

## The mechanical picture: one API call

When your program "calls an LLM," nothing mysterious happens at the boundary. It is an ordinary
network request:

```
your code  ──HTTP request──▶  the provider  ──▶  the model
   ▲                                                  │
   └──────────────  HTTP response  ◀──────────────────┘
```

1. **You send** a request: a list of messages (the conversation so far), plus settings like
   `max_tokens` and `temperature`.
2. **The model reads** all of that text — *all* of it, every time — as a sequence of **tokens**.
3. **The model generates** a reply, one token at a time, until it decides to stop or hits your
   `max_tokens` limit.
4. **You get back** the reply text *and* an accounting of how many tokens went in and came out.

In this course we make that call through a tiny wrapper,
[`PotatoLLMClient`](../../potato_llm/__init__.py), so the code reads the same whether we talk to
Claude or to an OpenAI model:

```python
from fluffy_potato_curriculum.potato_llm import AnthropicClient, Message

client = AnthropicClient()  # reads ANTHROPIC_API_KEY from the environment
reply = client.chat([Message.user("Say hello in one word.")])
print(reply.text)            # the assistant's answer
print(reply.usage)           # input_tokens / output_tokens — the bill
```

The `usage` field is the through-line of this whole lesson: it is the receipt for the call.

## Two facts that surprise almost everyone

These two come up again and again, so we name them now and spend the rest of the lesson making
them concrete:

- **The model has no memory.** It does not "remember" your previous messages. The *only* reason a
  chat feels like a continuous conversation is that your client re-sends the entire history on
  every call. That history is re-read — and re-billed — every single time.
- **A token is not a word.** It is whatever the model's tokenizer decides, learned from training
  data. Plain English is dense (≈4 characters per token); code, JSON, and non-English text can be
  2–10× worse. Eyeballing character counts will mislead you exactly where agents spend most of
  their tokens.

## The four primitives — one system, not four topics

L01 installs four primitives. They are **connected**, not independent — a change to one cascades
into the others:

- **Tokens** — the unit the model reads and bills in. Everything else is measured in tokens.
- **Context window** — the hard ceiling on how many tokens (input *and* output, combined) one
  call can involve.
- **Temperature & sampling** — the knobs that decide how the model picks each next token, and
  therefore how varied its answers are.
- **Cost** — you pay per token, in both directions, on every call. Tokens feed window math; window
  math and token counts feed cost.

By the end of the lesson the sentence to carry forward is:

> *From here on, every prompt you write is a budget decision — token count, dollar count, and
> context-window count, all at once.*

Next: the full lecture in [L0102_lecture.md](L0102_lecture.md), then the live demos
(L0103 / L0105 / L0106 / L0108) and the hands-on labs (L0104 / L0107 / L0109).
