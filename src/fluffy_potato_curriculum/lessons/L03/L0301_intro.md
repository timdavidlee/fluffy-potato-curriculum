# From one node to a chain: build a step, then wire several

```yaml
title: "From one node to a chain: build a step, then wire several"
keywords: langgraph, StateGraph, node, state, typed state, typeddict, edge, reducer, dag, workflow, prompt chaining, compile, ainvoke, astream, ChatAnthropic, mixed models, workflow vs agent, first framework
estimated duration: 10
```

> **Lesson:** L03 — Directed graphs: from one node to a sequential chain (the first LangGraph lesson).
> **Roadmap:** see this lesson's [objectives.md](../../../../docs/origin/lesson_roadmaps/L03/objectives.md).
> This is a short framing piece. Read it first, then the LangChain & LangGraph primer
> ([L0302_lecture.ipynb](L0302_lecture.ipynb)), the build-one-node demo
> ([L0303_lecture.ipynb](L0303_lecture.ipynb)), the sequential-chaining reference lecture
> ([L0304_lecture.md](L0304_lecture.md)), and the prompt-chaining demo
> ([L0305_lecture.ipynb](L0305_lecture.ipynb)). Hands-on practice is in the L03 lab
> ([L0306](L0306_lab_empty.ipynb)).
> **Anchor model:** the single-node movement uses **Claude Sonnet 4.6 — and only Sonnet** (keep the
> model constant while *the node* is the new idea). The chaining movement deliberately **mixes**
> models per node — **Haiku 4.5** for the light `parse` step, **Sonnet 4.6** for the heavy `draft` step.

## Where this lesson sits

This is the course's **first LangGraph lesson** and **first framework lesson**. In
[L01](../../../../docs/origin/lesson_roadmaps/L01/objectives.md) and
[L02](../../../../docs/origin/lesson_roadmaps/L02/objectives.md) you talked to the model through the
repo's own hand-rolled [`potato_llm`](../../potato_llm/CLAUDE.md) seam — reasoning about tokens,
cost, roles, and structured output. L03 is where that changes: you meet **LangGraph**, and inside a
LangGraph **node** you call the model through the **native LangChain `ChatAnthropic` client**, not
`potato_llm`. Name that departure to yourself as you read the demos — *"frameworks bring their own
client abstraction; this is the first of several you'll meet."*

The lesson runs in **two movements**:

1. **One node.** The smallest possible unit of a graph — one typed state, one node, wired straight to
   `END`. You'll build it, then run and inspect it in isolation.
2. **Several nodes.** That *same* node, wired — unchanged — into a fixed **directed acyclic graph
   (DAG)**: a **sequential prompt-chaining workflow** (*parse → draft → policy-check*) where *you*
   lay out the path and the model never decides what runs next.

[L05](../../../../docs/origin/lesson_roadmaps/L05/objectives.md) picks it up next and adds one
primitive — a **conditional** edge (routing) that's still developer-owned. Together L03 and L05
install the graph model using **plain LLM calls only** — no tools (those arrive at
[L07](../../../../docs/origin/lesson_roadmaps/L07/objectives.md)) and no agent loop (hand-rolled at
L10, as LangGraph at L11).

## The two ideas, said a few ways

**Movement 1 — a node is one LLM call you wire.** Said a few ways:

1. **State goes in, state comes out.** A node does not hand back "the answer" the way L01–L02 code
   did — it returns an *update to shared state* (a small dict of just the fields it changed), which
   LangGraph merges back in. That shift is what makes Movement 2's wiring possible without
   redesigning anything.
2. **A node is a pure function over state.** Given the same relevant slice of state, it does the same
   unit of work and returns the same *shape* of update — no hidden reads, no side effects beyond the
   one LLM call. (The model's sampling is non-deterministic; the *contract* is about what the
   function reads and returns.)
3. **A node's job is narrow on purpose.** One node does *one* unit of work — here, `parse` a support
   ticket into a few fields. Chaining narrow steps is Movement 2.

**Movement 2 — several nodes wired in order is a workflow you can inspect as data.** Said a few ways:

1. A **workflow** runs through predefined paths *you* lay out; an **agent** (L11) lets the *model*
   direct its own process. (The industry distinction from Anthropic's *Building Effective Agents*.)
2. **Prompt chaining** decomposes one task into a fixed sequence of focused steps — each a separate,
   small model call, not one mega-prompt doing everything.
3. **Each node can bind its own model.** Because a node is an independent call, you can mix a cheap
   model (Haiku) for light steps and a capable one (Sonnet) for heavy reasoning in the same graph.
4. **A graph turns control flow into inspectable data** — you can list, draw, and stream nodes and
   edges, unlike `if`/`while` buried in Python. And **determinism is a feature**: same input, same
   path — predictable, cheaper, and trivially testable.

## Be honest about one node — then watch it pay off

For a **single** node, the `StateGraph` ceremony (typed state, `compile`, `ainvoke`) is objectively
more setup than `result = call_model(prompt)`, and it does **not** obviously pay for itself. Say so
out loud. But you don't have to take the payoff on faith the way earlier drafts of this lesson did —
it arrives in the *next movement of this same lesson*: the identical ceremony takes a second and
third node with **zero** redesign of the first. The break-even is real, and it's one section away,
not one lesson away. That's the whole reason the two movements now live together.

## Vocabulary this lesson lands

You'll leave L03 able to define each of these — and they all reappear, unchanged, in L05 and L11:

- **Graph** — nodes connected by edges, compiled into a runnable. L03 starts at one node (no edges
  *between* nodes) and grows to a several-node chain.
- **Node** — a unit of work: a typed function that reads state and returns a **state update**. It may
  call the model (`ChatAnthropic`) internally, and each node may bind its own model.
- **State** — the shared, typed object passed into each node and updated by its return value.
- **Entry point / `END`** — where execution starts, and the sentinel where it stops.
- **Compile / invoke** — turning the declared graph into a runnable (`compile()`), then running it on
  an input (`await app.ainvoke(...)` — the async twin of `invoke()`, the course default). Two steps.
- **Pure function over state** — same relevant state in, same shape of update out, no hidden reads.
- **Edge** — a fixed transition between two nodes (`A → B`, taken every time). Appears in Movement 2.
- **Reducer** — the rule that merges a node's update into state *per field*. The default reducer
  **overwrites**; an `Annotated[list, add]` field **appends**. First matters once several nodes write.
- **DAG (directed acyclic graph)** — a graph with **no back-edges**: every edge moves forward to
  `END`. The absence of a back-edge is exactly what makes this a *workflow*, not an agent.
- **Prompt chaining** — a fixed chain of nodes where each step's output feeds the next.

Terms deliberately **not** introduced here — they're L05's: **conditional edge** (a routing function
chosen at runtime) and the deciders that can feed one (a model label, direct user input).

## A note on the client: first framework, native client, tracing still ahead

L01–L02 talked to the model through the hand-rolled `potato_llm` seam. From L03 on, the course
**reaches for a framework**, and frameworks bring their own client — so inside a graph node we call
LangChain's **`ChatAnthropic`** directly. The API key still loads through the same
[`common/config.py`](../../common/config.py) seam; only the *client* is the framework's now. The
tool-calling lessons (L07–L08) keep this same client, so the "which client, and why" story is
monotonic: the seam carries the prompt-only lessons, the framework client takes over from L03 onward.

The demos also show you how to **watch a graph run**: `graph.astream(stream_mode="updates")` prints
one update per node, in the order they fire — one step for the single node, then three for the chain.
Routing that same run to **Langfuse** for a structured, comparable trace is **L12's** job, still
several lessons away — nothing here depends on tracing being set up.

> Framework calls come in sync/async twins — `.invoke()` has `.ainvoke()`, `.stream()` has
> `.astream()`. The course defaults to the async ones, so you `await` your graph and model calls
> (a notebook cell can `await` at top level). *Why* async is the default is the K05 prework's
> "why async for agents."

The single sentence to leave L03 with: **"You wired several steps into a fixed chain — next lesson,
one of those edges gets to choose."**
