# Prompting fundamentals: structure changes the answer

```yaml
title: Prompting fundamentals: structure changes the answer
keywords: prompting, roles, system message, structured output, json, few-shot, task shapes, extraction, classification, ranking, summarization, anthropic, claude
estimated duration: 12
```

> **Lesson:** L02 — Prompting fundamentals.
> **Roadmap:** see this lesson's [objectives.md](../../../../docs/origin/lesson_roadmaps/L02/objectives.md).
> This is a short framing piece. Read it before the written reference lecture
> ([L0202_lecture.md](L0202_lecture.md)) and the four teacher demo notebooks
> (roles [L0203_lecture.ipynb](L0203_lecture.ipynb), structured output
> [L0205_lecture.ipynb](L0205_lecture.ipynb), few-shot [L0207_lecture.ipynb](L0207_lecture.ipynb),
> the task catalog [L0209_lecture.ipynb](L0209_lecture.ipynb)).
> **Anchor model throughout: Claude Sonnet 4.6.**

## Where this lesson sits

In L01 you learned *what an API call costs and how the model produces its output* — tokens, the
context window, temperature, cost. Those four primitives describe the **container**. Now, in L02,
you get to what you **put in the container**: the *prompt*.

The whole lesson rests on one claim, and the demos will make it concrete for you:

> *The same content, arranged differently, produces a different answer. Prompt structure is not
> decoration — it is a lever.*

## The three levers, in one breath

Here you'll pick up three tools — plus a catalog of what they let a single call *do*. These three
levers are the minimum prompting toolkit every later lesson assumes you already have in hand.

- **Roles** — who said what. A prompt is not one blob of text; it is a list of `{role, content}`
  messages with three roles: `system` (the always-true steering), `user` (the per-call request),
  and `assistant` (the model's prior replies — *or* fake examples you plant). Where content lands
  changes how the model treats it.
- **Structured output** — asking the model to answer in a *shape* (JSON, fixed fields, tagged
  blocks) instead of free prose, so your code can read the answer programmatically. The catch:
  the model *agrees* to the shape but does not *guarantee* it. You parse defensively.
- **Few-shot examples** — showing the model a few worked input→output pairs before the real input,
  to nudge its behavior. Powerful, but priced in tokens on *every* call and brittle if the
  examples are too similar. A precision tool, not a default.

## Three mental models to carry out of L02

Each demo lands one sentence for you. If you remember nothing else, hold onto these:

1. **The system message is *always-true context*, not an *inviolable rule*.** It's strongly
   weighted, but it's still just text the model reads. Durable identity-and-policy content goes
   in `system`; per-call data goes in `user`. Put per-call data in `system` and you poison reuse.
2. **Structured output is a *negotiation*, not a *guarantee*.** Ask for structure, parse
   defensively, fail loudly when the parse fails. "The model agreed to a contract" is not "the
   model honored the contract."
3. **Few-shot is a *context-window-priced behavior nudge*.** Diversity beats volume; every example
   costs input tokens on every call. Reach for it when an instruction alone fails — and weigh the
   bill.

## And what one call can do: the task catalog

The three levers are *mechanics* — where content goes, how to get a parseable answer, how to nudge
behavior. Point them at a goal and you get the everyday jobs a **single LLM call** does. Learn to
name the shape — naming it tells you which lever to reach for and what to validate:

- **Extraction** — pull structured fields out of text (one fixed schema, or a mixed bag of items).
- **Classification** — sort an input into a fixed label set (flat, a category→subcategory taxonomy,
  or multi-label).
- **Ranking / recommendation** — order a list of candidates, or pick the top-N, by a stated criterion.
- **Constrained generation** — produce output under a hard, checkable rule: *exactly N* items, a
  length cap, a required format.
- **Summarization / transformation** — compress or restyle text while keeping its meaning
  (summarize, rewrite, normalize, translate).

Every one of these is the *same three levers* aimed at a different **output contract** — and the
contract is the thing you *validate*, not just the thing you ask for. Each is also one **node** in
disguise: L03 takes exactly one of these shapes (extraction) and wraps it as a reusable graph node,
and L03 & L05 chain several into a pipeline.

## How L01 carries forward

Every L02 lever has an L01 cost shadow, and you'll keep seeing the numbers:

- The **system message is re-sent on every turn** — keep it lean, or the L01 cost staircase steepens.
- **Structured output is often a cost win** — a tight schema usually means fewer output tokens than
  prose (and output is the expensive direction).
- **Few-shot examples are paid for every call** — they are a real cost-vs-quality dial, not free.

## What L02 deliberately does *not* teach

This lesson stays narrow on purpose. You won't cover:

- **Chain-of-thought / scratchpad reasoning** — that's L06. Here you get the *structured-answer*
  half of `<thinking>…</thinking><answer>{…}</answer>`, and you'll see the channel split (the demo
  parses the answer straight past a thinking block); L06 is where you pick up the thinking half —
  what to reason about and when it helps. (Mini-track note: the mini skips L06, so that small beat
  is your only look at the thinking channel.)
- **Tool calling / forcing schema-conformant output via tool-use** — that's L07. Here you ask for
  JSON *by instruction only* and parse defensively. In production you'd reach for Anthropic's
  tool-use mechanism for stricter structure — you'll get there in L07, and the parsing discipline
  you build here still applies.
- **Orchestration — chaining several single steps into a pipeline** — that's L03 & L05. The task
  catalog above is the menu of what *one* call (one node) can do; wiring several together into a
  graph is the next two lessons for you.

The one sentence to leave L02 with:

> *You now know how to ask the model for what you want, in the shape you want — L06 is about making
> it think harder before it answers.*

Next up for you is [L03](../../../../docs/origin/lesson_roadmaps/L03/objectives.md) (Directed
graphs: from one node to a sequential chain), which takes one task shape from the catalog —
extraction — and wraps it as a reusable graph node.

Read next: the written reference lecture in [L0202_lecture.md](L0202_lecture.md), then the live demos
(roles [L0203](L0203_lecture.ipynb), structured output [L0205](L0205_lecture.ipynb), few-shot
[L0207](L0207_lecture.ipynb), the task catalog [L0209](L0209_lecture.ipynb)) and the hands-on labs
(L0204 / L0206 / L0208 / L0210).
