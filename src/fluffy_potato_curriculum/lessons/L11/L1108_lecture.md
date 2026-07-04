# From one loop to many patterns: the bridge to L15

```yaml
title: "From one loop to many patterns: the bridge to L15"
keywords: shallow agent, react, create_agent, pattern, langgraph, design patterns, plan-and-execute, supervisor, bridge to l13, control flow as data, primitives
estimated duration: 8
```

> **Lesson:** L11. **Roadmap:** the optional forward-pointer in [demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L11/demos_or_activities.md).
> A short closing lecture — **diagram + discussion, no live build**. It reuses the compiled agent
> from the demos ([L1103](L1103_lecture.ipynb)) and *names* what comes next. Building the patterns is
> **L15's** job; don't teach them here.

## section 1. Recap — what you built

### slide 1.1 A shallow agent, as a graph

- You rebuilt the L10 hand-rolled loop as a **LangGraph graph**: an `agent` node, a `tools` node, a
  conditional edge, and the **back-edge** `tools → agent` that hands the model control of the path.
- diagram: the compiled shallow-agent graph — `agent` with a conditional edge to `tools`/`END`, and
  `tools → agent` closing the loop — captioned "one model, one tool set, one decision point."
- You also **evaluated** it (the L13 set passed unchanged) and **traced** it (the run landed in the
  L12 Langfuse). The skills travelled with the agent, not the implementation.

### slide 1.2 The primitives you now own

- table: the L11 vocabulary — every one of these is what L15 builds *patterns* on top of.

| Primitive | What it is |
| --- | --- |
| `StateGraph` | the builder |
| node | typed function: state → update |
| edge / conditional edge | fixed transition / routing function on state |
| back-edge | the cycle that makes the model drive the path |
| typed state + `add_messages` reducer | the message history, appended |
| `compile` / `invoke` | build + run |
| prebuilt `ToolNode` / `create_agent` | the loop, packaged |

## section 2. `create_agent` is a pattern, not magic

### slide 2.1 The one-liner you revealed is named: ReAct

- In [L1103](L1103_lecture.ipynb) you hand-built the graph, then revealed
  `create_agent("anthropic:claude-sonnet-4-6", tools)` — *the same graph, wrapped*.
- That whole-graph one-liner is the **ReAct** pattern: **reason** (the model decides) →
  **act** (call a tool) → observe → repeat. It is a **pattern over the primitives you just built**,
  not a new mechanism.
- The point of building it by hand first: when L15 says "ReAct," you already know it is your
  `agent → tools → agent` loop with a name — not a black box.

### slide 2.2 A pattern is a reusable graph shape

- Once control flow is **data** (nodes and edges), recurring shapes get **names** and become
  reusable. A *pattern* is just a graph shape that solved a class of problem well enough to name.
- ReAct is the first and simplest. The moment your control flow stops being one loop, other shapes
  earn their keep — which is exactly where L15 begins.

## section 3. The open question L15 answers

### slide 3.1 What else can this graph shape express?

- L11 owns **one graph, one loop, state mechanics.** L15 owns the **named patterns** and their
  trade-offs (latency, control, complexity).
- A taste of what's coming (do **not** teach these now — just name them):
  - **plan-and-execute** — make a plan first, then run the steps;
  - **supervisor** — a coordinator node routes work to specialist sub-agents;
  - **hierarchical** — graphs of graphs;
  - **state-machine routing** — explicit states and transitions.
- diagram: the single shallow-agent loop on the left; on the right, four small unlabeled graph
  shapes (a chain-with-planner, a hub-and-spoke supervisor, a nested graph, a state machine) under a
  shrug-emoji "what else?" — captioned "L15."

### slide 3.2 …and when *not* to reach for a pattern

- Carry the L11 caution forward: a fancier pattern is more cost, more latency, more to debug.
  **Reach for the simplest shape that solves the task** — often that's the shallow loop you already
  have, or even the plain L10 function before it.
- Patterns are tools for when the single loop genuinely isn't enough — not an upgrade everyone needs.

## section 4. The one sentence to leave with

### slide 4.1 You built the primitive; L15 builds the patterns

- **A shallow agent is a single tool-calling loop expressed as a graph; the patterns in L15 are
  bigger graph shapes built from the exact primitives you now own.**
- Everything carries forward unchanged — `StateGraph`, nodes, edges, typed state, reducers,
  `compile`/`invoke`, the eval set, the Langfuse hookup. L15 adds *shapes*, not new machinery.
