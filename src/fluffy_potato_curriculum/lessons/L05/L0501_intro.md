# Conditional graphs: routing & branching — one new primitive, the same graph

```yaml
title: "Conditional graphs: routing & branching — one new primitive, the same graph"
keywords: langgraph, conditional edge, routing, classifier, user-input branching, deterministic, decider, workflow vs agent, chatanthropic, mixed models
estimated duration: 10
```

> **Lesson:** L05 — Conditional graphs: routing & branching.
> **Roadmap:** see this lesson's [objectives.md](../../../../docs/origin/lesson_roadmaps/L05/objectives.md).
> This is a short framing piece. Read it before the written reference lecture
> ([L0502_lecture.md](L0502_lecture.md)), the demo notebook
> ([L0503_lecture.ipynb](L0503_lecture.ipynb)), and the workflow-vs-agent wrap-up
> ([L0505_lecture.md](L0505_lecture.md)). Hands-on practice is in the L05 lab (L0504).
> **Anchor model: Claude Sonnet 4.6** for the branch nodes, **Claude Haiku 4.5** for the
> classifier — the same mixed-model mechanism from [L04](../L04/objectives.md).

## Where this lesson sits

L05 is the **third graph lesson**. [L03](../L03/objectives.md) wrapped a *single* LLM call as a
typed node; [L04](../L04/objectives.md) wired **several** nodes into a fixed sequence where the
developer hard-codes what runs next. L05 adds the one remaining primitive needed before the course
can talk about agents: the **conditional edge** — a transition chosen at *runtime* by a routing
function that inspects state and returns the name of the next node. With L05, the **L03–L05 graph
ramp is complete**: single node → fixed sequence → runtime-chosen branch, all still without tools
([L07](../L07/objectives.md)) and without an agent loop ([L10](../L10/objectives.md) /
[L14](../L14/objectives.md)).

L05 does **not** re-teach L04's sequential chaining — you arrive already able to build a fixed-edge
`StateGraph`; L05's entire job is the one new primitive, the conditional edge, and what can decide
it.

## The one idea, said a few ways

If you remember nothing else from L05, remember: **a conditional edge is not the model deciding.**
Said a few ways:

1. A **conditional edge** — wired with `add_conditional_edges` — reads **state** and returns the
   name of the next node, at runtime. L04 used only **fixed** edges (`A → B`, always); this is the
   second, runtime-chosen kind.
2. The decider can be **derived data**, a **model classification label**, or **direct user
   input** — never whether the model asked for a tool. That last case is the agent, taught at
   [L14](../L14/objectives.md).
3. **"Runtime-chosen" does not mean "unpredictable."** Re-run the same input and it takes the
   **same** branch, every time — a conditional edge is still a deterministic function of state.
4. **User-input branching is the purest contrast with an agent.** No model is anywhere near the
   routing decision — the user (or the developer's code) picked the path.
5. **Same mechanism, different decider, is the whole story.** L05's conditional edge and L14's
   conditional edge use the identical LangGraph API; only *what the routing function is allowed to
   read* changes.

## Vocabulary this lesson lands

Reuses L03/L04's vocabulary (graph, node, state, edge, reducer, entry point/END, DAG, workflow vs.
agent) and adds:

- **Conditional edge** — a runtime-chosen transition: a routing function reads **state** and
  returns the next node's name, wired with `add_conditional_edges`. In L05 the routing function
  reads developer-owned inputs to state; in L14 it reads whether the model asked for a tool.
- **Routing function** — the plain Python function (an `if`/`match`, not a model call) that
  implements a conditional edge's decision.
- **Router / switch** — the recurring shape: one entry node (often a classifier) whose conditional
  edge fans out to several specialized branch nodes that converge to a single exit.
- **Classification label** — a small structured value a node writes into state for a routing
  function to read. Produced with L02's structured-output-by-instruction discipline.
- **User-input branching** — a conditional edge whose routing function branches on a value the
  *user* supplied, arriving in the **initial state** (no mid-run pause; that's L17's `interrupt`).
- **Fallback / default branch** — the node execution goes to when a classification label doesn't
  match any known branch. A router must define behavior for the unmatched case.

## A note on the client and tracing: no new departures

Like L03/L04, L05's nodes call the native LangChain **`ChatAnthropic`** — no new departure here.
Tracing is still a forward reference: the full skill is **[L11's](../L11/objectives.md)** job.

The single sentence to leave L05 with: **"L04 showed you a graph with no branches; L05 showed you
a graph with developer-owned branches; L14 shows you a graph whose branches the model owns. Same
primitives throughout — the only thing that ever changes is who decides."**
