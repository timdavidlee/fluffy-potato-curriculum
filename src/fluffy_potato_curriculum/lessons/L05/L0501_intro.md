# Conditional graphs: routing & branching — one new primitive, the same graph

```yaml
title: "Conditional graphs: routing & branching — one new primitive, the same graph"
keywords: langgraph, conditional edge, routing, classifier, user-input branching, deterministic, decider, workflow vs agent, ChatAnthropic, mixed models
estimated duration: 10
```

> **Lesson:** L05 — Conditional graphs: routing & branching.
> **Roadmap:** see this lesson's [objectives.md](../../../../docs/origin/lesson_roadmaps/L05/objectives.md).
> This is a short framing piece. Read it before the written reference lecture
> ([L0502_lecture.md](L0502_lecture.md)), the demo notebook
> ([L0503_lecture.ipynb](L0503_lecture.ipynb)), and the workflow-vs-agent wrap-up
> ([L0505_lecture.md](L0505_lecture.md)). Hands-on practice is in the L05 lab (L0504).
> **Anchor model: Claude Sonnet 4.6** for the branch nodes, **Claude Haiku 4.5** for the
> classifier — the same mixed-model mechanism from [L03](../L03/objectives.md).

## Where this lesson sits

You're on the **second graph lesson**. In [L03](../L03/objectives.md) you wrapped a *single* LLM
call as a typed node, then wired **several** nodes into a fixed
sequence where you hard-coded what runs next. Here you add the one remaining primitive you need
before you can talk about agents: the **conditional edge** — a transition chosen at *runtime* by a
routing function that inspects state and returns the name of the next node. With L05 done, you've
completed the **L03 & L05 graph ramp**: single node → fixed sequence → runtime-chosen branch, all
still without tools ([L07](../L07/objectives.md)) and without an agent loop
([L10](../L10/objectives.md) / [L11](../L11/objectives.md)).

You won't re-cover L03's sequential chaining here — you already know how to build a fixed-edge
`StateGraph`. This lesson's entire job is the one new primitive, the conditional edge, and what
gets to decide it.

## The one idea, said a few ways

If you remember nothing else from this lesson, remember this: **a conditional edge is not the
model deciding.** Here it is said a few ways:

1. A **conditional edge** — wired with `add_conditional_edges` — reads **state** and returns the
   name of the next node, at runtime. L03 used only **fixed** edges (`A → B`, always); this is the
   second, runtime-chosen kind.
2. The decider can be **derived data**, a **model classification label**, or **direct user
   input** — never whether the model asked for a tool. That last case is the agent, and you'll
   meet it at [L11](../L11/objectives.md).
3. **"Runtime-chosen" doesn't mean "unpredictable."** Re-run the same input and you'll get the
   **same** branch, every time — a conditional edge is still a deterministic function of state.
4. **User-input branching is the purest contrast with an agent.** No model is anywhere near the
   routing decision — you (or the code you wrote) picked the path.
5. **Same mechanism, different decider — that's the whole story.** This lesson's conditional edge
   and L11's conditional edge use the identical LangGraph API; only *what the routing function is
   allowed to read* changes.

## Vocabulary you're picking up here

You already have L03's vocabulary (graph, node, state, edge, reducer, entry point/END, DAG,
workflow vs. agent). Here's what you're adding:

- **Conditional edge** — a runtime-chosen transition: a routing function reads **state** and
  returns the next node's name, wired with `add_conditional_edges`. Here the routing function reads
  inputs to state that you own; in L11 it reads whether the model asked for a tool.
- **Routing function** — the plain Python function (an `if`/`match`, not a model call) that
  implements a conditional edge's decision.
- **Router / switch** — the recurring shape: one entry node (often a classifier) whose conditional
  edge fans out to several specialized branch nodes that converge to a single exit.
- **Classification label** — a small structured value a node writes into state for a routing
  function to read. You'll produce it with L02's structured-output-by-instruction discipline.
- **User-input branching** — a conditional edge whose routing function branches on a value the
  *user* supplied, arriving in the **initial state** (no mid-run pause; that's L17's `interrupt`).
- **Fallback / default branch** — where execution goes when a classification label doesn't match
  any known branch. Any router you build needs a defined behavior for the unmatched case.

## The client and tracing: nothing new yet

Like in L03, your nodes call the native LangChain **`ChatAnthropic`** — no new departure here.
Tracing is still a forward reference: you'll get the full skill in **[L12](../L12/objectives.md)**.

Here's the one sentence to leave this lesson with: **"L03 showed you a graph with no branches;
L05 showed you a graph with branches you own; L11 shows you a graph whose branches the model owns.
Same primitives throughout — the only thing that ever changes is who decides."**
