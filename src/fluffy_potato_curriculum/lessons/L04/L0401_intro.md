# Sequential chaining: wire several nodes into a fixed pipeline

```yaml
title: "Sequential chaining: wire several nodes into a fixed pipeline"
keywords: langgraph, workflow, dag, directed acyclic graph, StateGraph, node, edge, state, reducer, prompt chaining, control flow as data, ChatAnthropic, mixed models
estimated duration: 10
```

> **Lesson:** L04 — Directed graphs: sequential chaining.
> **Roadmap:** see this lesson's [objectives.md](../../../../docs/origin/lesson_roadmaps/L04/objectives.md).
> This is a short framing piece. Read it before the written reference lecture
> ([L0402_lecture.md](L0402_lecture.md)) and the demo notebook
> ([L0403_lecture.ipynb](L0403_lecture.ipynb)). Hands-on practice is in the L04 lab (L0404).
> **Anchor model: Claude Sonnet 4.6** for the heavy reasoning nodes, **Claude Haiku 4.5** for the
> light nodes (extract / summarize). L04 deliberately *mixes* models per node.

## Where this lesson sits

In [L03](../L03/objectives.md) you wrapped a *single* LLM call as a typed node. Now you'll wire
**several** nodes into a fixed, **directed acyclic graph (DAG)** — a **workflow**, where *you* wire
the path and the model never decides what runs next. [L05](../L05/objectives.md) adds a
**conditional** edge (routing) on top of the same primitives; L11 later adds the one thing that
turns a workflow into an agent: a cycle.

Up to here you've written control flow as plain Python: a single call (L01–L02), one wrapped node
(L03). Continuing from L03, the model still lives *inside* the nodes — parse, draft, summarize —
but now you're wiring *several* nodes together, and *what runs next* is decided by the edges you lay
out, not by the model.

## The one idea, said a few ways

If you remember nothing else from L04, remember this: **several nodes, wired in a fixed order, is
a pipeline you can inspect as data.** Here it is said a few ways:

1. A **workflow** runs through predefined paths *you* lay out. An **agent** (L11) lets the *model*
   direct its own process. (The industry distinction from Anthropic's *Building Effective Agents*.)
2. **Prompt chaining** decomposes one task into a fixed sequence of focused steps — each a
   separate, small model call, not one mega-prompt doing everything.
3. **Each node can bind its own model.** Because a node is an independent call, you can mix a cheap
   model (Haiku) for light steps and a capable model (Sonnet) for heavy reasoning in the same graph.
4. **A graph turns control flow into inspectable data.** You can list and draw nodes and edges —
   unlike `if`/`while` buried in Python.
5. **Determinism is a feature.** Your workflow takes the same path on the same input: predictable,
   cheaper, and trivially testable.

## Vocabulary this lesson lands

Building on L03's vocabulary (graph, node, state, entry point/END, compile/ainvoke, pure function
over state), here's what you're adding in L04:

- **Edge** — a fixed transition, `A → B`, taken every time: `add_edge("parse", "draft")`.
- **Reducer** — the rule that merges a node's returned update into state, *per field*. The default
  reducer **overwrites**; an `Annotated[list, add]` field **appends** instead. You didn't need a
  reducer in L03 (one node, nothing to merge) — this is where it first matters.
- **DAG (directed acyclic graph)** — a graph with **no back-edges**: every edge moves forward to
  `END`. The absence of a back-edge is exactly what makes this a *workflow*, not an agent.
- **Prompt chaining** — a fixed chain of nodes where each step's output feeds the next.

Two terms you won't meet yet — they're L05's: **conditional edge** (a routing function chosen at
runtime) and the deciders that can feed one (a model label, direct user input).

## A note on the client: continuing the framework, tracing still ahead

Since [L03](../L03/objectives.md), you've been calling the native LangChain **`ChatAnthropic`**
client from your nodes, not the hand-rolled `potato_llm` seam from L01–L02 — no new departure here,
just more of it.

L04's demo also shows you how to **watch a workflow run**: `graph.astream(stream_mode="updates")` —
the same built-in call you used in L03 — prints one update per node, in the order they fire, which
confirms the path was developer-determined.

> Framework calls come in sync/async twins — `.invoke()` has `.ainvoke()`, `.stream()` has
> `.astream()`. The course defaults to the async ones, so you `await` your graph and model calls
> (a notebook cell can `await` at top level). *Why* async is the default is the K05 prework's
> "why async for agents." Routing that same run to **Langfuse** for a structured,
comparable trace (reading a trace, comparing runs, diagnosing failures) is **L12's** job, still
several lessons away — nothing in L04 depends on tracing being set up.

The single sentence to leave L04 with: **"You just wired several steps together — next lesson, one
of those edges gets to choose."**
