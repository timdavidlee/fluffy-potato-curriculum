# Workflows before agents: you wire the flow, the model works inside the nodes

```yaml
title: "Workflows before agents: you wire the flow, the model works inside the nodes"
keywords: langgraph, workflow, agent, dag, directed acyclic graph, stategraph, node, edge, conditional edge, state, reducer, prompt chaining, routing, control flow as data, chatanthropic
estimated duration: 10
```

> **Lesson:** L11 — Explicit graphs & workflows in LangGraph (deterministic DAGs).
> **Roadmap:** see this lesson's [objectives.md](../../../../docs/origin/lesson_roadmaps/L11/objectives.md).
> This is a short framing piece. Read it before the written reference lecture
> ([L1102_lecture.md](L1102_lecture.md)) and the two teacher demo notebooks
> (prompt chaining [L1103_lecture.ipynb](L1103_lecture.ipynb), routing + user-input branching
> [L1105_lecture.ipynb](L1105_lecture.ipynb)), with the workflow-vs-agent wrap-up in
> [L1107_lecture.md](L1107_lecture.md). Hands-on practice is in the L11 labs (L1104, L1106).
> **Anchor model: Claude Sonnet 4.6** for the heavy reasoning nodes, **Claude Haiku 4.5** for the
> light nodes (classify / route / extract). L11 deliberately *mixes* models per node.

## Where this lesson sits

This is the course's **first LangGraph lesson**, and it deliberately does *not* build an agent.
Up to here you have written control flow as plain Python: a single call (L01–L03), a single tool
round-trip (L04–L05), and in L07 a hand-rolled **model → tool → model loop** whose path your own
Python `while`/`if` decided. L11 introduces LangGraph by building a **workflow** — a fixed,
**directed acyclic graph (DAG)** of explicit nodes where *you* wire the path and the model never
decides what runs next. L12 then takes the *same* primitives and adds the one thing that turns a
workflow into an agent: a cycle.

That ordering is the whole point. "Learn a graph framework" and "let the model drive its own
process" are **two** hard ideas. Teaching the deterministic workflow first means that when L12
hands the model control of the path, you will see *exactly* what changed — an acyclic graph gained
a back-edge — instead of meeting graphs and agency fused into one intimidating thing.

## The one idea, said five ways

If you remember nothing else from L11, remember this: **in a workflow, the model lives *inside*
the nodes; the developer owns the edges.** The model still does the smart per-step work — classify
a ticket, draft a reply, summarize — but *what runs next* is decided by code you wrote, not by the
model. Said five ways, because it is the line between this lesson and the next:

1. A **workflow** runs through predefined paths *you* laid out. An **agent** lets the *model*
   direct its own process — choosing tools and looping until it decides it's done. (This is the
   industry distinction from Anthropic's *Building Effective Agents*.)
2. LangGraph expresses **both**. A graph is just wired nodes; it is an *agent* only when the
   **model** drives the path. L11's graphs are **workflows**.
3. A **conditional edge is not the model deciding.** In L11 a routing function branches on
   **state you set** — derived data, a model *classification label*, or **direct user input**.
   In L12 it branches on whether the model asked for a tool. Same mechanism, different decider.
4. **Determinism is a feature, not a limitation.** A workflow takes the same path on the same
   input: predictable, cheaper, lower-latency, and trivially testable. Most production "AI
   features" are workflows, not agents.
5. **The workflow → agent line is a single back-edge.** Everything you build here carries into
   L12 unchanged; the only addition is a conditional edge that loops back to the model.

## Vocabulary this lesson lands

You will leave L11 able to define each of these — and they all reappear, unchanged, in L12:

- **Graph** — a task expressed as nodes connected by edges, compiled into a runnable.
- **Node** — a typed function that reads state and returns a state update; may call the model
  (`ChatAnthropic`) internally, and **each node may bind its own model**.
- **Edge** — a fixed transition (`A → B`, always).
- **Conditional edge** — a routing function reads **state** and returns the next node's name.
- **State** — the shared, typed object threaded through every node.
- **Reducer** — the rule that merges a node's returned update into state per field.
- **DAG (directed acyclic graph)** — a graph with no back-edges; the defining shape of a workflow.
- **Workflow vs. agent** — workflow = developer wires the (acyclic) path; agent = the model drives
  the (cyclic) path. The lesson's headline contrast.

## A note on the client: first framework, native client

L01–L09 talked to the model through the hand-rolled `potato_llm` seam, so swapping providers was a
one-line change. From L11 on, the course **reaches for a framework**, and frameworks bring their
own client abstraction. So inside graph nodes we call LangChain's **`ChatAnthropic`** directly,
not `potato_llm`. The API key still loads through the same `common/config.py` seam — only the
*client* is the framework's now. Watch for that departure called out in the first demo.
