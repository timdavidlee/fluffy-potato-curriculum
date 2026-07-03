# Designing good tools: an API for an LLM to consume

```yaml
title: Designing good tools: an API for an LLM to consume
keywords: tool design, tool description, json schema, validation errors, idempotency, side effects, tool-or-no-tool, anthropic, claude
estimated duration: 10
```

> **Lesson:** L08 — Designing good tools.
> **Roadmap:** see this lesson's [objectives.md](../../../../docs/origin/lesson_roadmaps/L08/objectives.md).
> This is a short framing piece. Read it before the written reference lecture
> ([L0802_lecture.md](L0802_lecture.md)) and the four teacher demo notebooks
> (tool-or-no-tool [L0803_lecture.ipynb](L0803_lecture.ipynb), the description-is-the-tool
> [L0805_lecture.ipynb](L0805_lecture.ipynb), schemas-as-a-teaching-tool
> [L0807_lecture.ipynb](L0807_lecture.ipynb), errors-and-side-effects
> [L0809_lecture.ipynb](L0809_lecture.ipynb)).
> **Anchor model throughout: Claude Sonnet 4.6**, with one Haiku 4.5 contrast in
> [L0805](L0805_lecture.ipynb) to show the design gap widens on a smaller model.

## Where this lesson sits

L07 covered the *mechanics* of tool calling: how a single tool is wired to a model call, what the
tool-call round-trip looks like on the wire, and the protocol the model and runtime use to negotiate
a call. By the end of L07 a student can make a tool *work*.

L08 takes the next step: making a tool *good*. The protocol is settled — the open question now is
*what to expose, how to name and shape it, and how to fail gracefully* when the world disagrees with
the model. This is the first lesson in the course where you design **an interface for an LLM to
consume** rather than for a human to consume, and the design pressures are genuinely different.

The whole lesson rests on one claim, which the demos make concrete:

> *A tool is an API for an LLM consumer, not a human consumer. The model has no IDE, no
> autocomplete, no Stack Overflow, no co-worker to ask. Its entire understanding of the tool is the
> name, the description, the parameter schema, and the shape of what comes back.*

Every design choice in L08 follows from that one sentence.

## The four judgment calls L08 builds

L07 gave you the wiring. L08 gives you four design decisions you make *every time* you add a tool.
Each maps to one learning objective and one demo + lab pair.

- **Tool, or no tool?** ([Demo 1](L0803_lecture.ipynb) / [L0804 lab](L0804_lab_empty.ipynb)) — adding
  a tool is an architectural decision, not a convenience. A tool is warranted when the answer depends
  on data the model can't have memorized, requires precise computation it's bad at, has a side effect
  outside the conversation, or must be verified against ground truth. When the model already knows the
  answer cold, a tool is pure overhead — and a wrong-tool option to pick by mistake.
- **The description is the tool.** ([Demo 2](L0805_lecture.ipynb) / [L0806 lab](L0806_lab_empty.ipynb))
  — same name, same schema, *different description* → dramatically different model behavior. The
  description is the model's only training signal at inference time for *when* to reach for the tool
  and *when not to*. It is the single most important field, and the most common cause of an unused or
  misused tool.
- **Schemas are a contract, not a suggestion.** ([Demo 3](L0807_lecture.ipynb) /
  [L0808 lab](L0808_lab_empty.ipynb)) — the model is a *fuzzy* producer of structured output
  (back-reference [L02](../L02/L0201_intro.md)). A tight schema — required fields, enums, narrow types,
  per-field descriptions — converts ambiguity into validation errors the model can correct on the next
  turn. A loose schema pushes that ambiguity into the tool implementation, which then fails in ad-hoc
  ways the model can't anticipate.
- **Errors are part of the interface.** ([Demo 4](L0809_lecture.ipynb) /
  [L0810 lab](L0810_lab_empty.ipynb)) — the model treats a tool error as *new context*, not as an
  exception. A well-shaped error (`{"error": "validation", "field": "user_id", "message": "must be a
  UUID"}`) teaches the model to fix its call; a bare stack trace teaches it nothing and it guesses.
  This is also where idempotency and side effects live: the model *will* retry on its own when a
  result looks ambiguous, regardless of whether retry is safe.

## Three mental models to carry out of L08

Each demo lands one sentence. If you remember nothing else, remember these:

1. **Write the description for the model, not the human reader.** Code comments are for the human
   reading the source; the tool description is for the model's selection step at inference time. They
   are different audiences and want different things.
2. **A tight schema is a teaching tool, not just a type-checker.** The shape and per-field
   descriptions tell the model what's expected — often more reliably than the top-level description
   alone — and turn bad calls into recoverable validation errors.
3. **An error message is a prompt for the model's next turn.** Write it as if it were a system
   message, not a Python traceback. Informative errors close the loop; opaque errors send the model
   into a blind retry loop with the same wrong arguments.

## How L01–L07 carry forward

- **L01 (context-window cost).** Each additional tool eats system-prompt tokens and dilutes the
  model's attention across the tool list. A 20-tool agent that could be a 5-tool agent is harder for
  the model to navigate. *More tools ≠ more capable agent* — usually the opposite.
- **L02 (structured output).** A tool schema is a special case of the structured-output contract from
  L02. The model agreed to the shape; it did not guarantee it — so the schema validates *shape*, not
  *truth*, and you still parse and validate defensively.
- **L06 (reasoning is tokens).** Choosing *whether* to call a tool is itself a reasoning step. A good
  description and a clean error are the tokens the model conditions that decision on.
- **L07 (the protocol).** L08 assumes the wiring works. We do **not** re-teach the round-trip — if you
  are shaky on the mechanics, redirect to the L07 lab before continuing. L08 is about *design
  judgment* on top of a protocol you already understand.

## A note on the code seam

L08's demos register tools and observe the model *choose* and *call* them, so — like L07 — they drive
the model through a **LangChain chat model** (`ChatAnthropic`, swappable for any provider) rather than
the text-only `potato_llm` seam. A tool is a **plain typed Python function**: `model.bind_tools([fn])`
derives the tool's name, description, and JSON-Schema from the function's signature and docstring, so
*designing the tool* becomes *writing the function and its docstring well* — which is exactly what this
lesson is about. You can always inspect the derived schema with `convert_to_openai_tool(fn)` to see the
contract the model receives. The API key still loads through the config seam
(`require_anthropic_key()`) — we change the *client*, not where secrets come from. The **labs** stay
pure-Python and offline wherever the concept allows (designing a schema, rewriting an error,
classifying a task) so you can practice the *design* without spending a token.

## What L08 deliberately does *not* teach

- **Not the MCP wire format.** L09 packages these exact design choices — names, descriptions, schemas,
  error shapes — as a portable contract across clients. Everything L08 teaches applies **unchanged** to
  an MCP tool; MCP only standardizes the *transport* and *discovery*, not the design. A poorly designed
  tool exposed via MCP is still a poorly designed tool.
- **Not the agent loop.** Composing one tool's output into the next call is what L10 (the hand-rolled
  agent loop) makes first-class. L08 designs the individual tool well so L10's loop has good parts to
  work with.

The one sentence to leave L08 with:

> *You can now design a tool a model can choose and use correctly on first read — and recognize when
> the best tool is no tool at all.*

Next: the written reference lecture in [L0802_lecture.md](L0802_lecture.md), then the live demos
(L0803 / L0805 / L0807 / L0809) and the hands-on labs (L0804 / L0806 / L0808 / L0810).
