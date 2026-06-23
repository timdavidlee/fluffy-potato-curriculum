# Explicit graphs & workflows in LangGraph: you wire the flow

```yaml
title: "Explicit graphs & workflows in LangGraph: you wire the flow"
keywords: langgraph, stategraph, workflow, agent, dag, node, edge, conditional edge, state, reducer, prompt chaining, routing, user-input branching, per-node model, mixed models, control flow as data, determinism, chatanthropic, langfuse
estimated duration: 75
```

> **Lesson:** L11. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L11/objectives.md).
> This is the written reference lecture — thorough on purpose, so a student who missed the live
> delivery can rebuild the lesson from the page. The live demos are notebooks
> ([L1103](L1103_lecture.ipynb) prompt chaining, [L1105](L1105_lecture.ipynb) routing + user-input
> branching), the workflow-vs-agent wrap-up is [L1107](L1107_lecture.md), and hands-on practice is
> in the L11 labs (L1104, L1106).
> **Anchor model: Claude Sonnet 4.6** (heavy nodes), **Claude Haiku 4.5** (light nodes) — L11
> deliberately mixes models per node.

## section 1. The lesson in one claim

### slide 1.1 First a framework, and deliberately not an agent

- This is the course's **first LangGraph lesson**, and it builds a **workflow**, not an agent.
- From L01–L07 your control flow was plain Python: a single call, a single tool round-trip, and
  in [L07](../L07/objectives.md) a hand-rolled **model → tool → model loop** whose path your
  `while`/`if` decided.
- L11 turns that control flow into a **graph**: explicit nodes wired by edges *you* lay out. The
  model lives *inside* the nodes; it never decides what runs next.
- L12 reuses every primitive from this lesson and adds exactly one thing — a back-edge — to make
  an agent. Learning the workflow first means L12 is one small step, not a new world.

### slide 1.2 Workflow vs. agent — the headline distinction

- This is the industry distinction from Anthropic's *Building Effective Agents*, and we reuse it
  verbatim into L12.
- table: the one difference that separates a workflow from an agent.

| | **Workflow** (L11) | **Agent** (L12) |
| --- | --- | --- |
| Who decides the path? | the **developer** (fixed/derived logic) | the **model** |
| Graph shape | **acyclic** (DAG) — always reaches `END` | **cyclic** — loops model → tools → model |
| Where the model works | *inside* nodes (classify, draft) | inside nodes **and** chooses the path |
| Predictability | same input → same path | varies; the model may loop |

- The model is involved in **both**. Agency is about who controls the *path*, not whether a model
  is called somewhere.

### slide 1.3 The sentence to carry all lesson

- **In a workflow, the model lives inside the nodes; the developer owns the edges.**
- Say it whenever a branch appears. Every conditional edge in L11 is decided by *code you wrote*,
  reading *state you set* — never by the model deciding to call a tool. That last case is L12.

## section 2. The StateGraph primitives (vocabulary)

### slide 2.1 The five-line build

- Every graph in this lesson is built with the same `StateGraph` recipe. Memorize the shape:
- diagram: a flow `StateGraph(State) → add_node ×N → set_entry_point → add_edge / add_conditional_edges → compile() → invoke(input)`.

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

### slide 2.2 Node — a typed function that returns an update

- A **node** is a plain function: it reads the state and returns a **partial update** (a dict of
  just the fields it changed), *not* the whole state. LangGraph merges the update for you.
- A node does **one unit of work** and hands back an update — nothing more.
- A node *may* call the model (`ChatAnthropic`), or it may be plain Python. "Has a model in it"
  is not what makes something a node.

```python
def parse(state: TicketState) -> dict[str, object]:
    """Extract structured fields from the raw ticket (a light step → Haiku)."""
    reply = haiku.invoke(f"Extract the customer's issue from: {state['ticket']}")
    return {"parsed": reply.content}        # only the field this node changed
```

### slide 2.3 State and reducer — the data that flows between nodes

- **State** is a typed object (a `TypedDict`) threaded through every node. It carries the data
  that flows between steps: the raw input, intermediate results, the final answer.
- A **reducer** is the rule that merges a node's returned update into state, *per field*. The
  default reducer **overwrites**; an `Annotated[list, add]` field **appends** instead.
- diagram: a `TicketState` box with fields `ticket: str`, `parsed: str`, `draft: str`,
  `steps: Annotated[list[str], add]` — the last one tagged "append reducer".
- This is the **same** state/reducer machinery L12 reuses for an agent's *message history* — you
  meet it here, on a simpler acyclic graph.

### slide 2.4 What belongs in state — and what doesn't

- **In state:** data that flows between nodes — the extracted fields, the classification label,
  intermediate drafts.
- **Not in state:** the model client and configuration. Those are **dependencies wired in at
  build time**, not data that flows. A `ChatAnthropic` client is constructed once and closed over
  by the node, not threaded through `invoke`.

### slide 2.5 Edge, conditional edge, entry point, END

- **Edge** — a fixed transition, `A → B`, taken every time: `add_edge("parse", "draft")`.
- **Conditional edge** — a runtime choice: a routing function reads **state** and returns the
  *name* of the next node: `add_conditional_edges("classify", route_fn, {...})`.
- **Entry point** — where execution starts (`set_entry_point`).
- **END** — the sentinel where execution stops; every path in a workflow reaches it.
- **DAG (directed acyclic graph)** — a graph with **no back-edges**: every edge moves forward to
  `END`. The absence of a back-edge is exactly what makes this a *workflow*, not an agent.

## section 3. Pattern one — prompt chaining

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
  payoff shows up with **branching, visualization, shared state, and built-in tracing** (next).

## section 4. Pattern two — routing (and who gets to decide)

### slide 4.1 Classify, then branch

- **Routing**: an entry **classifier** node labels the input, and a **conditional edge** sends it
  down one of several specialized branches that converge to an exit.
- Example: a ticket is classified **billing / technical / general**; each branch has its own
  focused prompt; all three converge to `END`.
- diagram: `classify` fanning out via a dashed conditional edge to `billing` / `technical` /
  `general`, all three arrows converging into `END`.

### slide 4.2 A conditional edge is NOT the model deciding

- The routing function reads `state["category"]` — a **label the developer's code put in state** —
  and returns the matching branch name. The classification *result* picks the branch.
- Re-run the same ticket and it takes the **same path**: deterministic.
- This is the critical L11-vs-L12 point: in L11 the routing function branches on **state you set**.
  In L12 it branches on whether the **model asked for a tool**. *Same mechanism, different
  decider* — say which it is every time.

```python
def route(state: TicketState) -> str:
    # branches on a label already in state — not on the model choosing a tool
    return state["category"]   # "billing" | "technical" | "general"

builder.add_conditional_edges("classify", route,
    {"billing": "billing", "technical": "technical", "general": "general"})
```

### slide 4.3 A branch can be decided by data, a model label, or the user

- A conditional edge can route on **derived data**, on a **model classification**, or on **direct
  user input** — none of which is the model driving a *loop*.
- **User-input branching** is the purest "you wire the flow": the routing function reads a value
  the *user* supplied (a menu choice, a form field) — **no model in the routing decision at all**.

```python
def route_by_user(state: TicketState) -> str:
    # the USER picked the path; no model call in this decision
    return state["user_choice"]   # supplied in the initial state

builder.add_conditional_edges("start", route_by_user, {...})
```

- **Same graph shape, different decider.** Model-classified routing and user-input routing are
  *both* workflows, because the developer wired every branch. Most real "AI workflows" mix the two:
  route on the user's choice first, then run a model-driven *node* inside the chosen branch —
  **user owns the edge, model works inside the node**.
- Forward pointer (one line, don't teach it): the *interactive* version — a graph that **pauses to
  ask** the user and resumes on their answer — needs LangGraph's `interrupt` + a checkpointer and
  is **L15's** territory. In L11 the user input arrives in the **initial state**, so the graph runs
  straight through.

## section 5. Each node can bind its own model

### slide 5.1 The mechanism: a node is an independent call

- Because each node is its *own* model call, each can construct its own
  `ChatAnthropic(model=...)`. A graph can **mix models per node**.
- Use a **cheap, fast model** (Claude **Haiku 4.5**) for light steps — classify, route, extract a
  field — and a **capable model** (Claude **Sonnet 4.6**) for heavy reasoning — draft, analyze.
- diagram: the routing graph with each node tagged by model — `classify` = Haiku, `billing` /
  `technical` / `general` = Sonnet.

### slide 5.2 Mechanism here; the decision framework is L10's

- L11 shows only **that** you can mix and **how** (per-node `ChatAnthropic(model=...)`), with a
  light cost/latency aside read off the trace: the label step is cheap, the reasoning step is where
  the spend goes.
- The full *which-model* decision framework — capability vs. latency vs. cost axes, budgets,
  "small model for routing, capable for reasoning" — is **L10's** job (Choosing model power). The
  two reinforce; they do not re-teach each other.

## section 6. Why a graph: control flow as data, and determinism

### slide 6.1 A graph turns control flow into inspectable data

- Nodes and edges can be **listed, drawn, traced, and reasoned about** — unlike `if`/`while`
  buried in Python.
- LangGraph renders the compiled graph for you: `app.get_graph().draw_mermaid()` (text) or
  `draw_mermaid_png()` (image). The picture *is* the control flow.
- diagram: side by side — a block of imperative `if/elif` Python vs. the rendered graph diagram —
  captioned "same logic; the graph is data you can inspect."

### slide 6.2 Tracing: watch the workflow run

- Run the graph with a **Langfuse callback** and the spans land in the *same* self-hosted Langfuse
  instance you met in [L08](../L08/objectives.md) — "watch the workflow run" reuses an L08 skill.
- A prompt-chaining run shows a **linear chain** of generation spans; a routing run shows the
  **one chosen branch**. The trace confirms the path was developer-determined.
- Each span shows its **own model and cost** — that is where the per-node model mixing becomes
  tangible.

### slide 6.3 Determinism is a feature, not a limitation

- A workflow takes the **same path** on the same input: predictable, cheaper, lower-latency, and
  **trivially testable**.
- That testability is half the reason to prefer workflows: a tiny eval set over the classifier
  node (the [L09](../L09/objectives.md) discipline, same input → same path) is cheap and honest.
  The L11 routing lab includes an optional eval beat.
- Note the model *inside* a node is still non-deterministic — a draft's wording varies. The
  **path** is what's stable, and the path is the lesson.

## section 7. Workflow vs. agent — the single back-edge (preview of L1107)

### slide 7.1 The line is one edge

- Everything you built here — `StateGraph`, nodes, edges, typed state, reducers, compile/invoke,
  the Langfuse hookup — carries into L12 **unchanged**.
- L12 adds exactly one thing: a **conditional edge that loops back to the model**, handing the
  model control of the path. That single back-edge converts the acyclic workflow into the cyclic,
  model-driven agent (the same loop you hand-rolled in L07).
- diagram: the L11 acyclic chain, then the same graph with one new dashed edge curving from the
  model node back into the loop — labeled "the only thing L12 adds."

### slide 7.2 When to use which

- Prefer a **workflow** when the task has a **known shape**: predictable, cheaper, lower-latency,
  far easier to test and trace.
- Reach for an **agent** only when the steps **can't be known in advance** and the model genuinely
  needs to decide its own path.
- Name the common failure mode out loud: **reaching for an agent when a workflow would do** — more
  cost, less predictability, harder to debug. Choosing the simplest shape that solves the task *is*
  the engineering skill. The full treatment is in [L1107_lecture.md](L1107_lecture.md).
