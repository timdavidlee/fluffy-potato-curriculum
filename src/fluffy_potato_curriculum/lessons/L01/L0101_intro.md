# Anatomy of an LLM API call

```yaml
title: Anatomy of an LLM API call
keywords: llm, next-word prediction, api call, token, sub-word, preamble, context window, temperature, cost, mental model, anthropic, claude
estimated duration: 10
```

> **Lesson:** L01 — LLM and token basics.
> **Roadmap:** see this lesson's [objectives.md](../../../../docs/origin/lesson_roadmaps/L01/objectives.md).
> This is a short framing piece. Read it before the main lecture
> ([L0102_lecture.md](L0102_lecture.md)); the teacher demos and hands-on labs then walk the same
> chain in order (see the lesson's
> [demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L01/demos_or_activities.md)).

## Why this lesson exists

This is the first lesson of the course. Before we can build agents, prompt well, or wire up tools,
we need a working mental model of what an LLM *is at the API level* — not the math inside it, but
the contract you interact with when your code talks to a model.

L01 tells **one connected story**, not a list of four facts. Each idea is the reason the next one
exists:

> An LLM **predicts the next token** → the pieces are **sub-word tokens** → real strings (names,
> code, JSON) **fragment** into more tokens than you'd guess → a bigger **model** and better
> **front-loaded context** sharpen the prediction → **temperature** reshapes it → you **reuse a
> preamble** to keep quality high → and because the model has **no memory**, you re-send and
> **re-pay** all that overhead on every call — against both the **window** and the **bill**.

By the end you should be able to look at a prompt and answer three questions almost reflexively:
**how many tokens is this? how much will it cost? will it fit in the window, with room for the
answer?** If those feel like magic now, the goal of L01 is to turn them into back-of-envelope
engineering.

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
2. **The model reads** all of that text — *all* of it, every time — as a sequence of **tokens**,
   and predicts the next token over and over.
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

## The one fact to carry through the whole lesson

Almost every surprise in L01 traces back to a single fact:

- **The model has no memory.** It does not "remember" your previous messages. The *only* reason a
  chat feels like a continuous conversation is that your client re-sends the entire history — and
  any reusable preamble — on every call. That text is re-read, re-counted against the window, and
  re-billed every single time.

Everything else in the lesson — why front-loading works, why a preamble is overhead, why the window
fills, why a conversation's cost climbs — is a consequence of that one fact. The sentence to carry
out of L01:

> *Everything you front-load to make the model predict better is overhead you re-send, re-count, and
> re-pay on every call — so every prompt is a budget decision in tokens, dollars, and window space
> at once.*

Next: the full lecture in [L0102_lecture.md](L0102_lecture.md), then the live demos and hands-on
labs, which follow the same chain end to end.
