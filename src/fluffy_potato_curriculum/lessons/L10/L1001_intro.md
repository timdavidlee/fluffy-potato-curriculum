# Hand-rolled agent loop: an agent is a loop, not a model

```yaml
title: "Hand-rolled agent loop: an agent is a loop, not a model"
keywords: agent loop, model tool model, termination, iteration cap, max steps, tool failure, ToolMessage, status error, hand-rolled, langchain, anthropic, claude
estimated duration: 10
```

> **Lesson:** L10 — Hand-rolled agent loop.
> **Roadmap:** see this lesson's [objectives.md](../../../../docs/origin/lesson_roadmaps/L10/objectives.md).
> This is a short framing piece. Read it before the written reference lecture
> ([L1002_lecture.md](L1002_lecture.md)), the stub-model demo notebook
> ([L1003_lecture.ipynb](L1003_lecture.ipynb)), the two hands-on labs
> ([L1004](L1004_lab_empty.ipynb), [L1005](L1005_lab_empty.ipynb)), and the one live multi-step demo
> ([L1006_lecture.ipynb](L1006_lecture.ipynb)).
> **Anchor model for the live demo: Claude Sonnet 4.6.**

## Where this lesson sits

By L10 you have seen the *mechanics* of tool calling — wiring a single tool and tracing one
round-trip ([L07](../L07/L0701_intro.md)) — and the *design* of good tools, including what a tool
should return when it can't do its job ([L08](../L08/objectives.md)). What you have **not** built is
the *outer loop* that turns one tool-call round-trip into something that resembles an agent.

L10 closes that gap. You assemble a minimal **model → tool → model** loop in plain Python and learn
to reason about the two non-obvious questions that loop raises:

1. **When does it stop?**
2. **What happens when a tool fails?**

This is the first lesson where you write code that *keeps calling the model on its own*. Everything
before this was a single API call (L01–L08) or a single tool round-trip (L07). After this lesson you
have a working agent — small, hand-built, no framework — that can chain multiple tool calls toward a
goal.

## The one idea, said three ways

If you remember nothing else from L10, remember this: **an agent is a loop, not a model.**

1. The **model** is a stateless function call. You send it the whole conversation plus the tool
   definitions; it emits one response. It does not remember the last turn, and it does not run your
   tools — that framing is straight from [L07](../L07/L0701_intro.md).
2. The **loop** is what makes it an agent. The loop calls the model, executes any tool the model
   requested, appends the result, and calls the model *again* — over and over — until the model
   stops asking for tools or a safety cap fires.
3. **Every framework you will meet later is a fancier version of this loop.** LangGraph
   ([L04](../../CURRICULUM_PRD.md)) reframes the same model→tool→model skeleton as a graph; deep
   agents add planning and memory around it. Hand-rolling it once demystifies all of them.

## The three rules this lesson lands

These three rules are the spine of the lesson — the lecture, the demo, and both labs return to them:

- **The message-history invariant is load-bearing.** Every tool call the model makes must be
  answered by a matching `ToolMessage` — same `tool_call_id`, appended before you call the model
  again. Skip one, or mismatch an id, and the next request is rejected or the model produces
  garbage. This is the single most common bug in hand-rolled loops.
- **Termination is a design decision, not a default.** Left alone, the model will happily call tools
  forever. A loop with no cap is not "minimal" — it is *broken*. Every loop you write has at least a
  `max_steps` cap. Hitting the cap always means something is worth investigating.
- **Tool failures are messages, not exceptions.** When a tool raises, the loop's job is to convert
  that exception into a well-formed `ToolMessage` with `status="error"` and hand it back to the
  model — not to crash, and not to decide the recovery itself. The model is often the best component
  to decide whether to retry, swap tools, or give up. This builds directly on L08's
  error-handling thinking: L08 taught the *tool author* what to return on failure; L10 teaches the
  *loop* what to do when the tool can't even return.

## How we teach it: a stub model, then one live run

The hard part of an agent loop is the **control flow** — iterate until done, trip the cap, handle a
failure — not the live model. So most of L10 is built on a tiny **stub model** (the course's
`FakeModel`): a fake whose `.invoke(...)` returns the next *scripted* `AIMessage` off a list (a
tool-call turn, then another, then a final text turn). With a scripted model:

- the loop is fully **deterministic** — it runs the same way every time, no API key, no cost;
- you can script a runaway (the model "never stops") and watch the `max_steps` cap *catch* it;
- you can script a tool that raises and watch the loop turn the exception into a `ToolMessage`.

That is how the demo ([L1003](L1003_lecture.ipynb)) and both labs ([L1004](L1004_lab_empty.ipynb),
[L1005](L1005_lab_empty.ipynb)) work — **offline and verifiable**. Exactly **one** notebook
([L1006](L1006_lecture.ipynb)) swaps the stub for a real model and runs a genuine multi-step loop, so
you see the same code drive a live model.

## A note on the code you'll see

From here on the course drives models through a **LangChain chat model**, not the raw Anthropic SDK —
that is what makes the loop provider-agnostic. The loop only ever touches a tiny slice of the
interface: `model.bind_tools(tools)`, then `.invoke(messages)` → an `AIMessage` whose `.tool_calls`
say which tools to run, each answered by a `ToolMessage`. Because that slice is all the loop needs,
the **live** demo (a real `ChatAnthropic` via `init_chat_model("anthropic:…")`, key through the
config seam — never hard-coded) and the stub-model notebooks (the course's `FakeModel`, which
implements the same `.bind_tools()` / `.invoke()`) run the **identical** loop code. That
interchangeability is the whole point — swap the model object, keep the loop. (Swap the provider
prefix to `"openai:…"` and the same loop drives a different vendor.)

The one sentence to leave L10 with:

> *An agent is a loop around a stateless model: call the model, run the tool it asked for, feed the
> result back, repeat — until the model stops asking or a cap you chose fires; and when a tool
> breaks, the loop turns the break into a message, not a crash.*

Next: the written reference lecture in [L1002_lecture.md](L1002_lecture.md), then the stub-model demo
([L1003](L1003_lecture.ipynb)), the labs ([L1004](L1004_lab_empty.ipynb),
[L1005](L1005_lab_empty.ipynb)), and the live multi-step run ([L1006](L1006_lecture.ipynb)).
