# Hand-rolled agent loop: an agent is a loop, not a model

```yaml
title: "Hand-rolled agent loop: an agent is a loop, not a model"
keywords: agent loop, model tool model, termination, iteration cap, max steps, tool failure, tool_result, is_error, hand-rolled, anthropic, claude
estimated duration: 10
```

> **Lesson:** L07 — Hand-rolled agent loop.
> **Roadmap:** see this lesson's [objectives.md](../../../../docs/origin/lesson_roadmaps/L07/objectives.md).
> This is a short framing piece. Read it before the written reference lecture
> ([L0702_lecture.md](L0702_lecture.md)), the stub-model demo notebook
> ([L0703_lecture.ipynb](L0703_lecture.ipynb)), the two hands-on labs
> ([L0704](L0704_lab_empty.ipynb), [L0705](L0705_lab_empty.ipynb)), and the one live multi-step demo
> ([L0706_lecture.ipynb](L0706_lecture.ipynb)).
> **Anchor model for the live demo: Claude Sonnet 4.6.**

## Where this lesson sits

By L07 you have seen the *mechanics* of tool calling — wiring a single tool and tracing one
round-trip ([L04](../L04/L0401_intro.md)) — and the *design* of good tools, including what a tool
should return when it can't do its job ([L05](../L05/objectives.md)). What you have **not** built is
the *outer loop* that turns one tool-call round-trip into something that resembles an agent.

L07 closes that gap. You assemble a minimal **model → tool → model** loop in plain Python and learn
to reason about the two non-obvious questions that loop raises:

1. **When does it stop?**
2. **What happens when a tool fails?**

This is the first lesson where you write code that *keeps calling the model on its own*. Everything
before this was a single API call (L01–L05) or a single tool round-trip (L04). After this lesson you
have a working agent — small, hand-built, no framework — that can chain multiple tool calls toward a
goal.

## The one idea, said three ways

If you remember nothing else from L07, remember this: **an agent is a loop, not a model.**

1. The **model** is a stateless function call. You send it the whole conversation plus the tool
   definitions; it emits one response. It does not remember the last turn, and it does not run your
   tools — that framing is straight from [L04](../L04/L0401_intro.md).
2. The **loop** is what makes it an agent. The loop calls the model, executes any tool the model
   requested, appends the result, and calls the model *again* — over and over — until the model
   stops asking for tools or a safety cap fires.
3. **Every framework you will meet later is a fancier version of this loop.** LangGraph
   ([L11](../../CURRICULUM_PRD.md)) reframes the same model→tool→model skeleton as a graph; deep
   agents add planning and memory around it. Hand-rolling it once demystifies all of them.

## The three rules this lesson lands

These three rules are the spine of the lesson — the lecture, the demo, and both labs return to them:

- **The message-history invariant is load-bearing.** Every `tool_use` block the model emits must be
  answered by a matching `tool_result` block — same id, in the *next* user-role message — before you
  call the model again. Get this wrong and the API rejects the request or produces garbage. This is
  the single most common bug in hand-rolled loops.
- **Termination is a design decision, not a default.** Left alone, the model will happily call tools
  forever. A loop with no cap is not "minimal" — it is *broken*. Every loop you write has at least a
  `max_steps` cap. Hitting the cap always means something is worth investigating.
- **Tool failures are messages, not exceptions.** When a tool raises, the loop's job is to convert
  that exception into a well-formed `tool_result` with `is_error: true` and hand it back to the
  model — not to crash, and not to decide the recovery itself. The model is often the best component
  to decide whether to retry, swap tools, or give up. This builds directly on L05's
  error-handling thinking: L05 taught the *tool author* what to return on failure; L07 teaches the
  *loop* what to do when the tool can't even return.

## How we teach it: a stub model, then one live run

The hard part of an agent loop is the **control flow** — iterate until done, trip the cap, handle a
failure — not the live model. So most of L07 is built on a tiny **stub model**: a fake whose
`.create(...)` pops the next *scripted* response off a list (a `tool_use` turn, then another, then a
final text turn). With a scripted model:

- the loop is fully **deterministic** — it runs the same way every time, no API key, no cost;
- you can script a runaway (the model "never stops") and watch the `max_steps` cap *catch* it;
- you can script a tool that raises and watch the loop turn the exception into a `tool_result`.

That is how the demo ([L0703](L0703_lecture.ipynb)) and both labs ([L0704](L0704_lab_empty.ipynb),
[L0705](L0705_lab_empty.ipynb)) work — **offline and verifiable**. Exactly **one** notebook
([L0706](L0706_lecture.ipynb)) swaps the stub for the real Anthropic SDK and runs a genuine
multi-step loop, so you see the same code drive a live model.

## A note on the code you'll see

The same wrinkle from [L04](../L04/L0401_intro.md) applies. The course's `potato_llm` seam is
**text-only** — its `Message` carries a string and cannot represent `tool_use` / `tool_result`
blocks. The agent loop is *built on* those blocks, so the **live** demo reaches under the seam and
calls the raw Anthropic SDK directly (the key still loads through the config seam,
`require_anthropic_key` — never hard-coded). The stub-model notebooks don't call any SDK at all; the
stub mimics the SDK's response shape with `SimpleNamespace`, so the loop code is identical whether a
fake or a real client is plugged in. That interchangeability is the whole point.

The one sentence to leave L07 with:

> *An agent is a loop around a stateless model: call the model, run the tool it asked for, feed the
> result back, repeat — until the model stops asking or a cap you chose fires; and when a tool
> breaks, the loop turns the break into a message, not a crash.*

Next: the written reference lecture in [L0702_lecture.md](L0702_lecture.md), then the stub-model demo
([L0703](L0703_lecture.ipynb)), the labs ([L0704](L0704_lab_empty.ipynb),
[L0705](L0705_lab_empty.ipynb)), and the live multi-step run ([L0706](L0706_lecture.ipynb)).
