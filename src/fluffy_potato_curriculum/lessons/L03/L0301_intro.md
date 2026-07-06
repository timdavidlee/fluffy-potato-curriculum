# A node is one LLM call you wire: state goes in, state comes out

```yaml
title: "A node is one LLM call you wire: state goes in, state comes out"
keywords: langgraph, StateGraph, node, state, typed state, typeddict, compile, invoke, pure function, ChatAnthropic, single node, extract, first framework
estimated duration: 8
```

> **Lesson:** L03 — Single-node operations (the first LangGraph lesson).
> **Roadmap:** see this lesson's [objectives.md](../../../../docs/origin/lesson_roadmaps/L03/objectives.md).
> This is a short framing piece. Read it first, then the LangChain & LangGraph primer
> ([L0302_lecture.ipynb](L0302_lecture.ipynb)), the build demo
> ([L0303_lecture.ipynb](L0303_lecture.ipynb)), and the "why wire a node at all?" wrap-up
> ([L0305_lecture.md](L0305_lecture.md)). Hands-on practice is in the L03 lab (L0304).
> **Anchor model: Claude Sonnet 4.6 — and only Sonnet.** L03 keeps the model constant so the
> *node* is the only new thing to track.

## Where this lesson sits

This is the course's **first LangGraph lesson** and the **first framework lesson**. In
[L01](../../../../docs/origin/lesson_roadmaps/L01/objectives.md) and
[L02](../../../../docs/origin/lesson_roadmaps/L02/objectives.md) you talked to the model through the
repo's own hand-rolled [`potato_llm`](../../potato_llm/CLAUDE.md) seam — reasoning about tokens,
cost, roles, and structured output. L03 is where that changes: you meet **LangGraph**, and inside a
LangGraph **node** you call the model through the **native LangChain `ChatAnthropic` client**, not
`potato_llm`. Name that departure to yourself as you read the demo — *"frameworks bring their own
client abstraction; this is the first of several you'll meet."*

L03's scope is deliberately the **smallest possible unit of a graph: one typed state, one node,
nothing wired to it.** If you finish L03 able to say one sentence — *"a node is one LLM call you
wire; state goes in, state comes out"* — you have the entire payload of this lesson.
[L04](../../../../docs/origin/lesson_roadmaps/L04/objectives.md) picks it up immediately and wires
**several** nodes into a fixed sequence; L05 adds conditional branching. Together L03–L05 install the
graph model using **plain LLM calls only** — no tools (those arrive at
[L07](../../../../docs/origin/lesson_roadmaps/L07/objectives.md)) and no agent loop (hand-rolled at
L10, as LangGraph at L11).

## The one idea, said a few ways

If you remember nothing else from L03, remember: **a node is one LLM call, wrapped so an orchestrator
can plug it in.** Said a few ways, because it is the whole lesson:

1. **State goes in, state comes out.** A node does not hand back "the answer" the way L01–L02 code
   did — it returns an *update to shared state* (a small dict of just the fields it changed), which
   LangGraph merges back in. That shift is what makes L04's multi-node wiring possible without
   redesigning anything.
2. **A node is a pure function over state.** Given the same relevant slice of state, it does the same
   unit of work and returns the same *shape* of update — no hidden reads, no side effects beyond the
   one LLM call. (The model's sampling is non-deterministic; the *contract* is about what the
   function reads and returns, not about the tokens the model picks.)
3. **A node's job is narrow on purpose.** One node does *one* unit of work — here, **extract** a few
   fields from a support ticket. Chaining narrow steps together is L04's entire subject; L03 just
   makes sure you can build *one* narrow step cleanly first.
4. **One node is more ceremony than just calling a function — and that's the point.** A single-node
   `StateGraph` (typed state, `compile`, `invoke`) is objectively more setup than
   `result = call_model(prompt)`. The payoff isn't visible yet at one node; it shows up in L04, when
   the *same* ceremony scales to many nodes with no per-node redesign. The payoff is coming, not yet
   arrived.
5. **This is not yet an agent, and not yet a workflow with more than one step.** No tool call, no
   loop, no second node, no branching. Everything beyond "one wired step" belongs to later lessons.

## Vocabulary this lesson lands

You will leave L03 able to define each of these — and they all reappear, unchanged, in L04:

- **Graph** — a task expressed as nodes connected by edges, compiled into a runnable. L03 builds the
  smallest possible graph: one node, no edges *between* nodes (just entry → node → `END`).
- **Node** — a unit of work: a typed function that reads state and returns a **state update**. It may
  call the model (`ChatAnthropic`) internally. In L03 there is exactly one.
- **State** — the shared, typed object passed into a node and updated by its return value. In L03, a
  small schema with an input field and an output field.
- **Entry point / `END`** — where execution starts, and the sentinel where it stops. In a one-node
  graph, the entry point *is* the node, and the node's only edge goes to `END`.
- **Compile / invoke** — turning the declared graph into a runnable (`compile()`), then running it on
  an input (`invoke()`). Two separate steps.
- **Pure function over state** — the discipline a node follows: same relevant state in, same shape of
  update out, no hidden reads or side effects beyond its one LLM call.

Terms deliberately **not** introduced here — they are L04's, not L03's: **edge** (a transition
*between* two nodes; L03 has none), **conditional edge**, **reducer** (merging *multiple* nodes'
updates), and **DAG** (the term implies more than one node).

## A note on the client: first framework, native client

L01–L02 talked to the model through the hand-rolled `potato_llm` seam. From L03 on, the course
**reaches for a framework**, and frameworks bring their own client. So inside a graph node we call
LangChain's **`ChatAnthropic`** directly, not `potato_llm`. The API key still loads through the same
[`common/config.py`](../../common/config.py) seam (`ChatAnthropic` reads `ANTHROPIC_API_KEY` from the
same environment the config seam populates) — only the *client* is the framework's now. You meet
`ChatAnthropic` hands-on in the L0302 primer, then use it inside a node in the build demo.

The single sentence to leave L03 with: **"You just wired one step — next lesson, you wire several of
them together."**
