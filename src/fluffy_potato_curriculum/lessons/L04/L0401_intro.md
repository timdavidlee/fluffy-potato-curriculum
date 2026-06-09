# Tool calling: a tool call is also just tokens

```yaml
title: Tool calling: a tool call is also just tokens
keywords: tool calling, tool use, tool_use, tool_result, tool definition, schema, round-trip, protocol, anthropic, claude
estimated duration: 10
```

> **Lesson:** L04 — Tool calling: how it works.
> **Roadmap:** see this lesson's [objectives.md](../../../../docs/origin/lesson_roadmaps/L04/objectives.md).
> This is a short framing piece. Read it before the written reference lecture
> ([L0402_lecture.md](L0402_lecture.md)) and the four teacher demo notebooks
> (a-tool-call-is-tokens [L0403_lecture.ipynb](L0403_lecture.ipynb), one-wired-round-trip
> [L0404_lecture.ipynb](L0404_lecture.ipynb), trace-the-round-trip [L0406_lecture.ipynb](L0406_lecture.ipynb),
> three-outcomes [L0408_lecture.ipynb](L0408_lecture.ipynb)).
> **Anchor model throughout: Claude Sonnet 4.6** (Claude Haiku 4.5 is the smaller-model contrast in the last demo).

## Where this lesson sits

L01–L03 covered everything a model can do that is purely *text-in, text-out*: tokenization and
cost (L01), prompting roles and structured output (L02), and getting the model to reason better
by changing the *content* of the prompt (L03). In every one of those lessons the model only ever
produced text, and your program read that text. Nothing the model said ever *ran*.

L04 is the first lesson where the model is given the ability to **act** — to request that your
application run a function and feed the result back. This is the bedrock of every agent in the
rest of the course. But the framing from L03 carries over almost word for word:

> *Reasoning is just more tokens. A `<thinking>` block is a contract about **shape**, not a new
> capability.*

becomes, in L04:

> *A tool call is also just more tokens. A tool definition is a contract about **shape**, not a new
> capability — and the model never runs anything; your application does.*

That last clause is the single most important sentence in the lesson. Keep it in mind through
every demo and lab.

## The one idea, said five ways

If you remember nothing else from L04, remember this: **the model does not run your tool.** It
emits a block of tokens that — by training — has the *shape* of a tool-call request. Your
application reads those tokens, decides what to do, runs the real function, and hands the result
back. Said five ways, because it reshapes how you debug, secure, and scale every agent later:

1. The model **proposes**; the application **disposes**. A tool call is a request, not an
   execution.
2. The tool **definition** is a contract about shape (like L03's `<thinking>` tags), not a
   guarantee about behavior. It does not force a call, validate arguments, or stop the model from
   inventing a tool that doesn't exist.
3. A single tool-using exchange is **at minimum four messages**: `user → assistant(tool_use) →
   user(tool_result) → assistant(final)`. Every tool call grows the history — that *is* the
   protocol, not a side effect.
4. The model is **stateless across calls**. The tool definitions and the full history ride along
   in *every* request; the model does not "remember" the tool from last turn.
5. Tools cost tokens **twice over**: the definition is re-sent on every request, and the result
   lives in the history forever after.

## Vocabulary this lesson lands

These five terms recur all the way through L05–L18, so we pin them now:

- **Tool** — a callable in your application (here, a plain Python function) that the model can
  *request* via the tool-call protocol.
- **Tool definition / schema** — a structured description (name, natural-language description,
  JSON-Schema input shape) you pass to the model alongside the prompt. It tells the model what
  tools exist and how to invoke them.
- **Tool call** (also *tool-use block*) — the block in a model response saying "I want to call
  tool X with arguments Y." A request, not an execution.
- **Tool result** (also *tool-result block*) — the block in the *next* user-side message carrying
  the output of running the requested tool. It closes the loop and references the call's id.
- **Round-trip** — one full `model → tool-call → application runs tool → tool-result → model`
  exchange. L04 deals only with *single* round-trips; multi-step loops arrive in L07.

## What L04 deliberately does *not* do

L04 is scoped tight on purpose, the same way L03 stayed prompt-only:

- **One tool, one round-trip.** Every demo and lab uses a single `calculator` tool and a single
  model→tool→model exchange. Multi-tool *selection* and tool-error *design* are **L05**; an agent
  loop over many calls is **L07**. Resisting "just one more tool" is what keeps the protocol legible.
- **Mechanics, not judgment.** L04's job is to make the protocol mechanically obvious — to let you
  *build* a tool-using exchange that works. **L05 ("Designing good tools")** asks the design
  questions: should this be a tool at all, what should it be named, what should the schema look
  like, how should it report failure? We share vocabulary with L05 exactly so you don't relearn
  terms.

## A note on the code you'll see

There is one wrinkle worth flagging up front. The course's `potato_llm` seam (the provider-agnostic
client you used in L02–L03) is **text-only** — its `Message` carries a string and cannot represent
tool-use or tool-result blocks. Because L04 is *about* those blocks, the L04 demos and the live labs
reach **under** the seam and call the raw Anthropic SDK directly:

```python
import anthropic
from fluffy_potato_curriculum.common.config import require_anthropic_key

client = anthropic.Anthropic(api_key=require_anthropic_key())
resp = client.messages.create(model="claude-sonnet-4-6", max_tokens=512, tools=[...], messages=[...])
```

This is the one lesson that legitimately bypasses `potato_llm`. The key still loads through the
config seam (`require_anthropic_key`) — we never hard-code it. Two of the labs are **offline pure
Python** (no key needed): they hand you a *crafted* `tool_use` block to dispatch on and validate, so
you can practice the mechanics deterministically.

The one sentence to leave L04 with:

> *A tool call is a block of tokens the model emitted; your application is the one that reads it,
> runs the function, and hands the result back — and that exchange is always at least four messages.*

Next: the written reference lecture in [L0402_lecture.md](L0402_lecture.md), then the live demos
(L0403 / L0404 / L0408) and the hands-on labs (L0405 / L0407 / L0409).
