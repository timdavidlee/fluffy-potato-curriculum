# Shallow agents in LangGraph: the same loop, now drawn as a graph

```yaml
title: "Shallow agents in LangGraph: the same loop, now drawn as a graph"
keywords: langgraph, agent, shallow agent, stategraph, node, edge, conditional edge, back-edge, state, reducer, add_messages, toolnode, message history, control flow as data, chatanthropic, langfuse, eval carry-over
estimated duration: 10
```

> **Lesson:** L11 — Shallow agents in LangGraph.
> **Roadmap:** see this lesson's [objectives.md](../../../../docs/origin/lesson_roadmaps/L11/objectives.md).
> This is a short framing piece. Read it before the written reference lecture
> ([L1102_lecture.md](L1102_lecture.md)), then the three teacher demo notebooks —
> build the agent ([L1103_lecture.ipynb](L1103_lecture.ipynb)), state & reducers
> ([L1105_lecture.ipynb](L1105_lecture.ipynb)), eval carry-over + tracing
> ([L1107_lecture.ipynb](L1107_lecture.ipynb)) — with the bridge to L15 in
> [L1108_lecture.md](L1108_lecture.md). Hands-on practice is in the L11 labs (L1104, L1106).
> **Anchor model: Claude Sonnet 4.6** — a *single* model throughout, so the graph shape is the
> only thing that changed versus the L10 hand-rolled loop. (Mixing models per node was L04's demo;
> *which* model to use is L14's topic.)

## Where this lesson sits

This is the lesson the whole first arc has been building toward. You hand-built an agent from
nothing: a single tool round-trip ([L07](../L07/objectives.md)), good tool design
([L08](../L08/objectives.md)), and then the **model → tool → model loop** in plain Python
([L10](../L10/objectives.md)) — `agent_loop.run(...)` returning a
`RunResult(final_text, iterations, termination, trace)`. You then learned to *observe* that loop
with a structured trace ([L12](../L12/objectives.md)) and to *judge* it with a minimal eval set
([L13](../L13/objectives.md)).

L11 cashes that in. You rebuild the **same agent you already understand** as a **LangGraph graph**.
The control flow does not change — it is still model → tool → model until termination. What changes
is the *shape*: an explicit `while` loop becomes an explicit **graph** of nodes and edges over a
shared **state**, and LangGraph supplies the runtime that drives it. Meeting the framework only
*after* you hand-rolled the loop is the whole bet of this arc: the framework reads as a set of
conveniences over a familiar skeleton, not as magic.

## The one idea: it's the same loop, drawn as a graph

In [L04](../L04/objectives.md) you built a **workflow** — a directed *acyclic* graph (a DAG) where
*you* wired every edge and the model never decided what ran next. L11 takes those exact same
primitives — `StateGraph`, nodes, edges, typed state, reducers — and adds **one thing**: a
**conditional edge that loops back to the model**. That single **back-edge** hands control of the
path to the *model*, and an acyclic workflow becomes a cyclic, model-driven **agent**.

- **L04 owns:** *you* drive the graph (acyclic).
- **L11 owns:** the *model* drives the graph (cyclic).
- **The line between them is a single back-edge.**

Map every graph piece back to an L10 line and the lesson lands:

| L10 hand-rolled loop | L11 LangGraph graph |
| --- | --- |
| "call the model" step | the **`agent`** node |
| "run every `tool_use`, append a `tool_result`" step | the **`tools`** node |
| `while` / loop back after running tools | the **edge** `tools → agent` (the back-edge) |
| `if there's a tool_use: … else: return` | the **conditional edge** out of `agent` |
| the `messages` list you mutated in place | the **state**, merged by the `add_messages` **reducer** |
| `max_steps` cap | LangGraph's **recursion limit** |

## What "shallow" means (define it early)

A **shallow agent** is a *single tool-calling loop*: one model, one set of tools, one decision
point that either calls a tool or finishes. It is exactly the L10 loop, now expressed as a graph.
"Shallow" is **not** "lesser" — most production agents are shallow. *Deep* agents (planning,
persistent memory, sub-todos, reflection) are a later, heavier choice (L18) — named here only as
"what we are **not** building yet."

## A note on the client: still the framework's, not the seam

Continuing the departure that began in L04: inside graph nodes we call LangChain's
**`ChatAnthropic`** directly, **not** the hand-rolled `potato_llm` seam from L01–L13 — "frameworks
bring their own client abstraction." The API key still loads through the same `common/config.py`
seam; only the *client* is the framework's. And the things you carry forward are exactly the
skills from L12–L13: the **same** L13 eval set runs against this rebuild (it passes → the rebuild is
correct), and the graph's run lands in the **same** L12 Langfuse dashboard. Evaluation and tracing
travel with the agent, not the implementation.
