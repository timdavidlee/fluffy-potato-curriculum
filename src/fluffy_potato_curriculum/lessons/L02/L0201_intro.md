# Prompting fundamentals: structure changes the answer

```yaml
title: Prompting fundamentals: structure changes the answer
keywords: prompting, roles, system message, structured output, json, few-shot, anthropic, claude
estimated duration: 10
```

> **Lesson:** L02 — Prompting fundamentals.
> **Roadmap:** see this lesson's [objectives.md](../../../../docs/origin/lesson_roadmaps/L02/objectives.md).
> This is a short framing piece. Read it before the written reference lecture
> ([L0202_lecture.md](L0202_lecture.md)) and the three teacher demo notebooks
> (roles [L0203_lecture.ipynb](L0203_lecture.ipynb), structured output
> [L0205_lecture.ipynb](L0205_lecture.ipynb), few-shot [L0207_lecture.ipynb](L0207_lecture.ipynb)).
> **Anchor model throughout: Claude Sonnet 4.6.**

## Where this lesson sits

L01 answered *what an API call costs and how the model produces its output* — tokens, the context
window, temperature, cost. Those four primitives describe the **container**. L02 is the first
lesson about what you **put in the container**: the *prompt*.

The whole lesson rests on one claim, which the demos make concrete:

> *The same content, arranged differently, produces a different answer. Prompt structure is not
> decoration — it is a lever.*

## The three levers, in one breath

L02 hands you exactly three tools. They are the minimum prompting toolkit every later lesson
assumes you already own.

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

Each demo lands one sentence. If you remember nothing else, remember these:

1. **The system message is *always-true context*, not an *inviolable rule*.** It is strongly
   weighted, but it is still just text the model reads. Durable identity-and-policy content goes
   in `system`; per-call data goes in `user`. Putting per-call data in `system` poisons reuse.
2. **Structured output is a *negotiation*, not a *guarantee*.** Ask for structure, parse
   defensively, fail loudly when the parse fails. "The model agreed to a contract" is not "the
   model honored the contract."
3. **Few-shot is a *context-window-priced behavior nudge*.** Diversity beats volume; every example
   costs input tokens on every call. Reach for it when an instruction alone fails — and weigh the
   bill.

## How L01 carries forward

Every L02 lever has an L01 cost shadow, and we keep printing the numbers:

- The **system message is re-sent on every turn** — keep it lean, or the L01 cost staircase steepens.
- **Structured output is often a cost win** — a tight schema usually means fewer output tokens than
  prose (and output is the expensive direction).
- **Few-shot examples are paid for every call** — they are a real cost-vs-quality dial, not free.

## What L02 deliberately does *not* teach

This lesson is narrow on purpose. It does **not** cover:

- **Chain-of-thought / scratchpad reasoning** — that is L06. L02 teaches the *structured-answer*
  half of `<thinking>…</thinking><answer>{…}</answer>`; L06 teaches the thinking half.
- **Tool calling / forcing schema-conformant output via tool-use** — that is L07. Here we ask for
  JSON *by instruction only* and parse defensively. In production you would use Anthropic's
  tool-use mechanism for stricter structure — you will see it in L07, and the parsing discipline
  you learn here still applies.

The one sentence to leave L02 with:

> *You now know how to ask the model for what you want, in the shape you want — L06 is about making
> it think harder before it answers.*

Next: the written reference lecture in [L0202_lecture.md](L0202_lecture.md), then the live demos
(L0203 / L0205 / L0207) and the hands-on labs (L0204 / L0206 / L0208).
