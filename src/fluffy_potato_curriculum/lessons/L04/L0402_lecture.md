# Directed graphs: sequential chaining — wire several nodes into a fixed pipeline

```yaml
title: "Directed graphs: sequential chaining — wire several nodes into a fixed pipeline"
keywords: langgraph, StateGraph, workflow, dag, node, edge, state, reducer, prompt chaining, per-node model, mixed models, control flow as data, determinism, ChatAnthropic
estimated duration: 55
```

> **Lesson:** L04. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L04/objectives.md).
> This page is your written reference — thorough on purpose, so if you missed the live session you
> can rebuild the whole lesson from it. The live demo is
> [L0403_lecture.ipynb](L0403_lecture.ipynb) (prompt chaining), and you get hands-on practice in the
> L04 lab (L0404). [L05](../L05/objectives.md) picks these same primitives up and adds a
> conditional edge.
> **Anchor model: Claude Sonnet 4.6** (heavy nodes), **Claude Haiku 4.5** (light nodes) — L04
> deliberately mixes models per node.

## section 1. The lesson in one claim

### slide 1.1 One node becomes several, wired in order

- In [L03](../L03/objectives.md) you built a `StateGraph` at its smallest: one typed node. Now
  you'll wire **several** such nodes into a fixed sequence — a **workflow**, not an agent.
- From L01–L02 your control flow was plain Python: a single call, then in L03 one wrapped node.
  Here you'll turn a *sequence* of steps into a **graph**: explicit nodes wired by edges *you* lay
  out. The model lives *inside* the nodes; it never decides what runs next.
- [L05](../L05/objectives.md) adds a **conditional** edge on the same primitives; L11 later reuses
  everything here and adds exactly one more thing — a back-edge — to make an agent.
- diagram: L03's single `node` box on the left growing into L04's fixed chain on the right — one box
  `node`, an arrow, then three wired boxes `parse → draft → policy_check → END`, captioned "one node
  (L03) → several wired in order (L04)."

### slide 1.2 Workflow vs. agent — the headline distinction (first pass)

- This is the industry distinction from Anthropic's *Building Effective Agents*, and it'll carry
  unchanged into L05 and L11.

| | **Workflow** (L04–L05) | **Agent** (L11) |
| --- | --- | --- |
| Who decides the path? | the **developer** (fixed/derived logic) | the **model** |
| Graph shape | **acyclic** (DAG) — always reaches `END` | **cyclic** — loops model → tools → model |
| Where the model works | *inside* nodes (extract, draft) | inside nodes **and** chooses the path |
| Predictability | same input → same path | varies; the model may loop |

- The model is involved in **both**. Agency is about who controls the *path*, not whether a model
  is called somewhere. Here you're building the **simplest** workflow shape — no branches at all yet.

### slide 1.3 The sentence to carry through the lesson

- **In a workflow, the model lives inside the nodes; you own the edges.**
- Every edge you write in L04 is **fixed** — `A → B`, always. There's nothing to branch on yet;
  that arrives in L05.
- diagram: a fixed acyclic chain `parse → draft → policy_check → END`, each node showing a small
  "model" chip *inside* it and the forward edges labeled "you own these (fixed)"; a faint dashed
  back-edge from the last node curving to the first is crossed out and labeled "no back-edge yet — a
  loop here would make it L11's agent."

## section 2. The StateGraph primitives (vocabulary, continued from L03)

### slide 2.1 The five-line build

- Every graph in this lesson is built with the same `StateGraph` recipe. Get this shape into
  muscle memory:
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

- You built exactly this recipe in L03 with **one** node and one edge straight to `END`. Here
  you're using the same recipe with **several** nodes and edges *between* them — new wiring, no new
  primitive.

### slide 2.2 Node — a typed function that returns an update (recap)

- A **node** is a plain function: it reads the state and returns a **partial update** (a dict of
  just the fields it changed), *not* the whole state. LangGraph merges the update for you.
- A node does **one unit of work** and hands back an update — nothing more. That's unchanged from
  L03; what's new here is that *several* nodes now share one state object.

```python
def parse(state: TicketState) -> dict[str, object]:
    """Extract structured fields from the raw ticket (a light step → Haiku)."""
    reply = haiku.invoke(f"Extract the customer's issue from: {state['ticket']}")
    return {"parsed": reply.content}        # only the field this node changed
```

### slide 2.3 State and reducer — the data that flows between nodes

- **State** is a typed object (a `TypedDict`) threaded through every node. In L03 your state had
  two fields and one node touching them; here your state is threaded through **several** nodes in
  turn.
- A **reducer** is the rule that merges a node's returned update into state, *per field*. The
  default reducer **overwrites**; an `Annotated[list, add]` field **appends** instead. This is your
  first genuinely new primitive in L04 — you never needed one in L03 (one node, nothing to merge).
- diagram: a `TicketState` box with fields `ticket: str`, `parsed: str`, `draft: str`,
  `steps: Annotated[list[str], add]` — the last one tagged "append reducer".
- This is the **same** state/reducer machinery you'll reuse in L11 for an agent's *message
  history* — you're meeting it here first, on a simpler acyclic graph.

### slide 2.4 What belongs in state — and what doesn't

- **In state:** data that flows between nodes — the extracted fields, intermediate drafts.
- **Not in state:** the model client and configuration. Those are **dependencies you wire in at
  build time**, not data that flows. You construct a `ChatAnthropic` client once and close over it
  in the node — you don't thread it through `invoke`.

### slide 2.5 Edge, entry point, END, DAG

- **Edge** — a fixed transition, `A → B`, taken every time: `add_edge("parse", "draft")`. Every
  edge in L04 is this kind; L05 adds a second kind (the conditional edge).
- **Entry point** — where execution starts (`set_entry_point`).
- **END** — the sentinel where execution stops; every path in a workflow reaches it.
- **DAG (directed acyclic graph)** — a graph with **no back-edges**: every edge moves forward to
  `END`. The absence of a back-edge is exactly what makes this a *workflow*, not an agent.

## section 3. The pattern — prompt chaining

### slide 3.1 Decompose a task into a fixed sequence

- **Prompt chaining**: a fixed chain of nodes where each step's output feeds the next. Your running
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

- Here's the honest trade-off: for a *strictly linear* three-step task the graph is near
  break-even. Its real payoff shows up once you add **branching** ([L05](../L05/objectives.md),
  next), shared state, and tracing ([L12](../L12/objectives.md), later).

## section 4. Each node can bind its own model

### slide 4.1 The mechanism: a node is an independent call

- Because each node is its *own* model call, you can construct your own
  `ChatAnthropic(model=...)` for each one. That lets you **mix models per node**.
- Use a **cheap, fast model** (Claude **Haiku 4.5**) for light steps — extract a field, summarize —
  and a **capable model** (Claude **Sonnet 4.6**) for heavy reasoning — draft, analyze.
- diagram: the chaining graph with each node tagged by model — `parse` = Haiku, `draft` /
  `policy_check` = Sonnet.

### slide 4.2 Mechanism here; the decision framework is L14's

- Here you're seeing only **that** you can mix and **how** (per-node `ChatAnthropic(model=...)`),
  with a light cost/latency aside: the extraction step is cheap, the reasoning step is where the
  spend goes.
- The full *which-model* decision framework — capability vs. latency vs. cost axes, budgets,
  "small model for routing, capable for reasoning" — is **[L14's](../L14/objectives.md)** job
  (Choosing model power). The two reinforce; neither re-teaches the other.
  [L05](../L05/objectives.md) reuses this same mechanism for its classifier node.

## section 5. Why a graph: control flow as data, and determinism

### slide 5.1 A graph turns control flow into inspectable data

- You can **list, draw, and reason about** nodes and edges — unlike `if`/`while` buried in Python.
- LangGraph renders the compiled graph for you: `app.get_graph().draw_mermaid()` (text) or
  `draw_mermaid_png()` (image). The picture *is* the control flow, and needs no API key.
- diagram: side by side — a block of imperative sequential Python vs. the rendered graph diagram —
  captioned "same logic; the graph is data you can inspect."

### slide 5.2 A first taste of tracing (not a prerequisite)

- The demo gives you an **optional** taste of routing spans to Langfuse, the same self-hosted
  instance **[L12](../L12/objectives.md)** will teach in full — reading a structured trace,
  comparing runs, diagnosing failures from a trace alone is entirely L12's job, several lessons
  away.
- If Langfuse isn't configured on your machine, the workflow runs exactly the same; you simply
  won't see the spans. Nothing in L04 depends on tracing being set up.

### slide 5.3 Determinism is a feature, not a limitation

- Your workflow takes the **same path** on the same input: predictable, cheaper, lower-latency,
  and **trivially testable**.
- That testability is half the reason to prefer workflows: a tiny eval set (the
  [L13](../L13/objectives.md) discipline, same input → same path) is cheap and honest.
- Notice the model *inside* a node is still non-deterministic — a draft's wording varies. The
  **path** is what's stable, and that's the whole lesson.

## section 6. Two DAG gotchas, named

### slide 6.1 The two pitfalls to catch when you wire your own workflow

- text: this lesson showed both of these *positively* — determinism as a feature (§5) and per-node
  model binding (§4). Here they are again as portable pitfalls you can catch yourself committing
  the first time you wire your own graph. Both share one root: **in a workflow you own two things
  the model does not — the path, and which model runs each node — and each gotcha is forgetting
  that you own one of them.**
- text: these are the two *sequential-DAG* gotchas. The two *routing* pitfalls — reaching for an
  agent where a workflow fits, and brittle branch conditions — belong to
  [L05](../L05/objectives.md), which owns the conditional edge; hold onto the split, you'll meet
  those there.
- table: the two gotchas, the one-line cure, and where you saw it.

| Gotcha | Cure | Where you saw it |
| --- | --- | --- |
| **"My DAG is deterministic"** — trusting the *whole* workflow to reproduce, or quietly adding a back-edge without deciding to | the **path** is fixed; the model's output *inside* each node still varies. Keep the graph acyclic **on purpose** — the moment you loop on the model's own output you've built an agent ([L10](../L10/objectives.md)/[L11](../L11/objectives.md)), so name the crossing instead of sliding into it | §5.3 (determinism is the *path*, not the wording) + §2.5 (a DAG is exactly "no back-edge") + slide 1.2 (acyclic workflow vs. cyclic agent) |
| **Wrong model per node** — Sonnet on the label step (overpaying), or Haiku on the hard reasoning step (underpowering) | cheap model for classify / extract, capable model for reasoning. The *mechanism* is per-node `ChatAnthropic(model=...)` (§4); the *which-model decision framework* is [L14](../L14/objectives.md) — hold onto the link, you'll get the full framework there | §4 (each node binds its own model) + the `parse`=Haiku / `draft`=Sonnet chain in the [L0403](L0403_lecture.ipynb) demo |

- text: the first gotcha is where this lesson's spine can blur — **confusing "the developer owns
  the path" (a workflow) with "the model owns the path" (an agent).** A model *inside* a node isn't
  agency; agency is the model choosing the *path*, which is exactly the back-edge L11 adds. Keep
  that line sharp and you've got the whole lesson.

## section 7. Bridge to L05

### slide 7.1 One more primitive, then the workflow-vs-agent close

- Everything you built here — `StateGraph`, nodes, fixed edges, typed state, reducers,
  compile/invoke — carries into [L05](../L05/objectives.md) **unchanged**. L05 adds exactly one
  new primitive: the **conditional edge**, a routing function chosen at runtime instead of a fixed
  `A → B`.
- L05 is also where the full **workflow vs. agent** contrast closes out, once you've seen both a
  fixed chain (this lesson) and a routed branch (L05) — the two things that make "developer wires
  every path" concrete before L11 hands the model that control.
