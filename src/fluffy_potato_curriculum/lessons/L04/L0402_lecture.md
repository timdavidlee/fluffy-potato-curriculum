# Directed graphs: sequential chaining — wire several nodes into a fixed pipeline

```yaml
title: "Directed graphs: sequential chaining — wire several nodes into a fixed pipeline"
keywords: langgraph, stategraph, workflow, dag, node, edge, state, reducer, prompt chaining, per-node model, mixed models, control flow as data, determinism, chatanthropic
estimated duration: 55
```

> **Lesson:** L04. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L04/objectives.md).
> This is the written reference lecture — thorough on purpose, so a student who missed the live
> delivery can rebuild the lesson from the page. The live demo is
> [L0403_lecture.ipynb](L0403_lecture.ipynb) (prompt chaining), and hands-on practice is in the
> L04 lab (L0404). [L05](../L05/objectives.md) picks these same primitives up and adds a
> conditional edge.
> **Anchor model: Claude Sonnet 4.6** (heavy nodes), **Claude Haiku 4.5** (light nodes) — L04
> deliberately mixes models per node.

## section 1. The lesson in one claim

### slide 1.1 One node becomes several, wired in order

- [L03](../L03/objectives.md) built a `StateGraph` at its smallest: one typed node. L04 wires
  **several** such nodes into a fixed sequence — a **workflow**, not an agent.
- From L01–L02 your control flow was plain Python: a single call, then in L03 one wrapped node.
  L04 turns a *sequence* of steps into a **graph**: explicit nodes wired by edges *you* lay out.
  The model lives *inside* the nodes; it never decides what runs next.
- [L05](../L05/objectives.md) adds a **conditional** edge on the same primitives; L14 later reuses
  everything here and adds exactly one more thing — a back-edge — to make an agent.

### slide 1.2 Workflow vs. agent — the headline distinction (first pass)

- This is the industry distinction from Anthropic's *Building Effective Agents*, and it carries
  unchanged into L05 and L14.

| | **Workflow** (L04–L05) | **Agent** (L14) |
| --- | --- | --- |
| Who decides the path? | the **developer** (fixed/derived logic) | the **model** |
| Graph shape | **acyclic** (DAG) — always reaches `END` | **cyclic** — loops model → tools → model |
| Where the model works | *inside* nodes (extract, draft) | inside nodes **and** chooses the path |
| Predictability | same input → same path | varies; the model may loop |

- The model is involved in **both**. Agency is about who controls the *path*, not whether a model
  is called somewhere. L04 builds the **simplest** workflow shape — no branches at all yet.

### slide 1.3 The sentence to carry through the lesson

- **In a workflow, the model lives inside the nodes; the developer owns the edges.**
- Every edge in L04 is **fixed** — `A → B`, always. There is nothing to branch on yet; that arrives
  in L05.

## section 2. The StateGraph primitives (vocabulary, continued from L03)

### slide 2.1 The five-line build

- Every graph in this lesson is built with the same `StateGraph` recipe. Memorize the shape:
- diagram: a flow `StateGraph(State) → add_node ×N → set_entry_point → add_edge → compile() → invoke(input)`.

```python
from langgraph.graph import StateGraph, END

builder = StateGraph(TicketState)        # 1. declare the typed state schema
builder.add_node("parse", parse)         # 2. add nodes (each a typed function)
builder.add_node("draft", draft)
builder.set_entry_point("parse")         # 3. where execution starts
builder.add_edge("parse", "draft")       # 4. wire edges
builder.add_edge("draft", END)
app = builder.compile()                  # 5. compile to a runnable
result = app.invoke({"ticket": "..."})   #    invoke on an input
```

- L03 built exactly this recipe with **one** node and one edge straight to `END`. L04 is the same
  recipe with **several** nodes and edges *between* them — new wiring, no new primitive.

### slide 2.2 Node — a typed function that returns an update (recap)

- A **node** is a plain function: it reads the state and returns a **partial update** (a dict of
  just the fields it changed), *not* the whole state. LangGraph merges the update for you.
- A node does **one unit of work** and hands back an update — nothing more. This is unchanged from
  L03; what's new is that *several* nodes now share one state object.

```python
def parse(state: TicketState) -> dict[str, object]:
    """Extract structured fields from the raw ticket (a light step → Haiku)."""
    reply = haiku.invoke(f"Extract the customer's issue from: {state['ticket']}")
    return {"parsed": reply.content}        # only the field this node changed
```

### slide 2.3 State and reducer — the data that flows between nodes

- **State** is a typed object (a `TypedDict`) threaded through every node. L03's state had two
  fields and one node touching them; L04's state is threaded through **several** nodes in turn.
- A **reducer** is the rule that merges a node's returned update into state, *per field*. The
  default reducer **overwrites**; an `Annotated[list, add]` field **appends** instead. This is
  L04's first genuinely new primitive — L03 never needed one (one node, nothing to merge).
- diagram: a `TicketState` box with fields `ticket: str`, `parsed: str`, `draft: str`,
  `steps: Annotated[list[str], add]` — the last one tagged "append reducer".
- This is the **same** state/reducer machinery L14 reuses for an agent's *message history* — you
  meet it here, on a simpler acyclic graph.

### slide 2.4 What belongs in state — and what doesn't

- **In state:** data that flows between nodes — the extracted fields, intermediate drafts.
- **Not in state:** the model client and configuration. Those are **dependencies wired in at
  build time**, not data that flows. A `ChatAnthropic` client is constructed once and closed over
  by the node, not threaded through `invoke`.

### slide 2.5 Edge, entry point, END, DAG

- **Edge** — a fixed transition, `A → B`, taken every time: `add_edge("parse", "draft")`. Every
  edge in L04 is this kind; L05 adds a second kind (the conditional edge).
- **Entry point** — where execution starts (`set_entry_point`).
- **END** — the sentinel where execution stops; every path in a workflow reaches it.
- **DAG (directed acyclic graph)** — a graph with **no back-edges**: every edge moves forward to
  `END`. The absence of a back-edge is exactly what makes this a *workflow*, not an agent.

## section 3. The pattern — prompt chaining

### slide 3.1 Decompose a task into a fixed sequence

- **Prompt chaining**: a fixed chain of nodes where each step's output feeds the next. Our running
  example is a support-ticket pipeline: **parse → draft → policy-check**.
- diagram: three boxes `parse → draft → policy_check → END`, two forward arrows, no back-edge.
- Each node is a **separate model call with a focused prompt**, not one mega-prompt doing
  everything.

### slide 3.2 Why decompose instead of one big prompt?

- **Reliability:** smaller, focused prompts are more dependable than one prompt asked to parse,
  draft, *and* police a reply at once.
- **Testability:** you can evaluate each step in isolation — feed the `parse` node a ticket and
  check just the extraction.
- table: the honest trade-off.

| For | Against |
| --- | --- |
| each prompt is small and reliable | more model calls = more cost/latency (the [L01](../L01/objectives.md) trade) |
| each step is individually testable | a strictly linear chain is near break-even vs. a plain function |
| failures are localized to one node | |

- Name it honestly: for a *strictly linear* three-step task the graph is near break-even. Its real
  payoff shows up with **branching** ([L05](../L05/objectives.md), next), shared state, and tracing
  ([L11](../L11/objectives.md), later).

## section 4. Each node can bind its own model

### slide 4.1 The mechanism: a node is an independent call

- Because each node is its *own* model call, each can construct its own
  `ChatAnthropic(model=...)`. A graph can **mix models per node**.
- Use a **cheap, fast model** (Claude **Haiku 4.5**) for light steps — extract a field, summarize —
  and a **capable model** (Claude **Sonnet 4.6**) for heavy reasoning — draft, analyze.
- diagram: the chaining graph with each node tagged by model — `parse` = Haiku, `draft` /
  `policy_check` = Sonnet.

### slide 4.2 Mechanism here; the decision framework is L13's

- L04 shows only **that** you can mix and **how** (per-node `ChatAnthropic(model=...)`), with a
  light cost/latency aside: the extraction step is cheap, the reasoning step is where the spend
  goes.
- The full *which-model* decision framework — capability vs. latency vs. cost axes, budgets,
  "small model for routing, capable for reasoning" — is **[L13's](../L13/objectives.md)** job
  (Choosing model power). The two reinforce; they do not re-teach each other. [L05](../L05/objectives.md)
  reuses this same mechanism for its classifier node.

## section 5. Why a graph: control flow as data, and determinism

### slide 5.1 A graph turns control flow into inspectable data

- Nodes and edges can be **listed, drawn, and reasoned about** — unlike `if`/`while` buried in
  Python.
- LangGraph renders the compiled graph for you: `app.get_graph().draw_mermaid()` (text) or
  `draw_mermaid_png()` (image). The picture *is* the control flow, and needs no API key.
- diagram: side by side — a block of imperative sequential Python vs. the rendered graph diagram —
  captioned "same logic; the graph is data you can inspect."

### slide 5.2 A first taste of tracing (not a prerequisite)

- The demo shows an **optional** taste of routing spans to Langfuse, the same self-hosted instance
  **[L11](../L11/objectives.md)** will teach in full — reading a structured trace, comparing runs,
  diagnosing failures from a trace alone is entirely L11's job, several lessons away.
- If Langfuse isn't configured, the workflow runs exactly the same; you simply won't see the
  spans. Nothing in L04 depends on tracing being set up.

### slide 5.3 Determinism is a feature, not a limitation

- A workflow takes the **same path** on the same input: predictable, cheaper, lower-latency, and
  **trivially testable**.
- That testability is half the reason to prefer workflows: a tiny eval set (the
  [L12](../L12/objectives.md) discipline, same input → same path) is cheap and honest.
- Note the model *inside* a node is still non-deterministic — a draft's wording varies. The
  **path** is what's stable, and the path is the lesson.

## section 6. Bridge to L05

### slide 6.1 One more primitive, then the workflow-vs-agent close

- Everything you built here — `StateGraph`, nodes, fixed edges, typed state, reducers,
  compile/invoke — carries into [L05](../L05/objectives.md) **unchanged**. L05 adds exactly one
  new primitive: the **conditional edge**, a routing function chosen at runtime instead of a fixed
  `A → B`.
- L05 is also where the full **workflow vs. agent** contrast closes out, once you've seen both a
  fixed chain (this lesson) and a routed branch (L05) — the two things that make "developer wires
  every path" concrete before L14 hands the model that control.
