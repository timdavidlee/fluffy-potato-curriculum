# Conditional graphs: the routing pattern and who gets to decide

```yaml
title: "Conditional graphs: the routing pattern and who gets to decide"
keywords: langgraph, routing, conditional edge, classifier, mixed models, per-node model, user-input branching, deterministic, decider, chatanthropic
estimated duration: 45
```

> **Lesson:** L05. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L05/objectives.md).
> This is the written reference lecture. The live demo is
> [L0503_lecture.ipynb](L0503_lecture.ipynb) (routing + user-input branching), hands-on practice is
> the L05 lab (L0504), and the workflow-vs-agent close is
> [L0505_lecture.md](L0505_lecture.md).
> **Anchor model: Claude Sonnet 4.6** (branch nodes), **Claude Haiku 4.5** (classifier) — the same
> mixed-model mechanism from [L04](../L04/objectives.md).

## section 1. The one new primitive

### slide 1.1 Fixed edge vs. conditional edge

- [L04](../L04/objectives.md) used only **fixed** edges: `add_edge("parse", "draft")`, taken every
  time, no exceptions.
- L05 adds the **conditional edge**: a **routing function** reads state at runtime and returns the
  *name* of the next node, wired with `add_conditional_edges("classify", route, {...})`.
- diagram: `classify` fanning out via a dashed conditional edge to `billing` / `technical` /
  `general`, all three arrows converging into `END`.

### slide 1.2 The decider — what a routing function is allowed to read

- Three things a conditional edge's routing function may read in this lesson: **derived/computed
  data** already in state, a **model classification result** (a label a node wrote to state), or
  **direct user input** (a value supplied as part of the initial state).
- One thing it is never allowed to read: whether **the model asked for a tool**. That's L14.
- Say the line every time: **here you (the developer) own the branch; in an agent, the model
  owns it.**

```python
def route(state: TicketState) -> str:
    # branches on a label already in state — not on the model choosing a tool
    return state["category"]   # "billing" | "technical" | "general"

builder.add_conditional_edges("classify", route,
    {"billing": "billing", "technical": "technical", "general": "general"})
```

## section 2. The routing pattern — classify, then branch

### slide 2.1 An entry classifier that fans out

- **Routing**: an entry **classifier** node labels the input, and a **conditional edge** sends it
  down one of several specialized branches that converge to an exit.
- Example: a ticket is classified **billing / technical / general**; each branch has its own
  focused prompt; all three converge to `END`.
- Per-node models, reused from L04: `classify` only needs to emit a label, so it runs on the
  **cheap, fast model** (Haiku 4.5); the branches do the real reasoning, so they run on the
  **capable model** (Sonnet 4.6). This is the *mechanism* of mixed-model design — the full
  decision framework is **[L13's](../L13/objectives.md)** job.

### slide 2.2 Determinism: the workhorse proof

- Re-run the same ticket through the router and confirm the **same branch** executes every time.
  The branch *wording* may vary (the model is still non-deterministic inside a node); the **path**
  does not.
- This is what separates a workflow's routing from an agent's: a conditional edge, even though it
  is "runtime-chosen," is a deterministic function of state, not a coin flip.

### slide 2.3 The fallback / default branch

- A router needs a **defined behavior for every possible label**, not just the expected ones. When
  a classification doesn't cleanly match a branch, route it to a default/`general` fallback rather
  than letting the routing function raise.
- Treat this as a first-class design requirement, not an afterthought — a habit worth installing
  before students meet messier real-world classifiers.

## section 3. Branch on the user, not the model

### slide 3.1 The purest contrast with an agent

- A conditional edge can also branch on a value the **user** supplied directly — a menu choice, a
  form field — rather than a model classification: `if state["user_choice"] == "escalate": return
  "human_review"`.
- **No model is involved in the routing decision at all.** This is the sharpest possible contrast
  with an agent: the user picked the path, the developer wired the options.
- In L05 this user input arrives **as part of the initial state**; the graph then runs straight
  through. The *interactive* version — a graph that **pauses mid-run to ask** and resumes on the
  answer — needs LangGraph's `interrupt` plus a checkpointer, and is **[L17's](../L17/objectives.md)**
  job (human-in-the-loop).

### slide 3.2 Same shape, different decider — and they compose

- Put model-classification routing (section 2) and user-input routing side by side: *same graph
  shape — an entry point, a conditional edge, converging branches — different decider.*
- The general pattern for most real conditional workflows: route on the user's choice first, then
  run a model-driven **node** inside the chosen branch. Rule: **the user (or developer logic) owns
  the edge; the model can still do work inside a node.**

## section 4. When developer-controlled branching is enough

### slide 4.1 Reach for a router, not an agent, when the paths are known

- A router/switch is the right tool whenever the *set of possible paths is known in advance* and
  picking among them is a classification, lookup, or user choice — cheap, predictable, testable.
- Reach for an agent only when the model must decide *which and how many* steps to take, and that
  set of steps isn't enumerable ahead of time.
- Name the common failure mode: building an agent to do what a two-branch router would do just as
  well, at a fraction of the cost and unpredictability.

### slide 4.2 Bridge to L0505

- L05 never builds a cycle — every graph in this lesson is still a DAG, still a workflow, no
  matter how many branches it has.
- The full workflow-vs-agent recap and close — what carries into L14, what precisely changes, and
  when to reach for which — is [L0505_lecture.md](L0505_lecture.md).
