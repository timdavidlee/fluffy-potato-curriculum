# Conditional graphs: the routing pattern and who gets to decide

```yaml
title: "Conditional graphs: the routing pattern and who gets to decide"
keywords: langgraph, routing, conditional edge, classifier, mixed models, per-node model, user-input branching, deterministic, decider, ChatAnthropic
estimated duration: 45
```

> **Lesson:** L05. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L05/objectives.md).
> This is the written reference lecture. The live demo is
> [L0503_lecture.ipynb](L0503_lecture.ipynb) (routing + user-input branching), hands-on practice is
> the L05 lab (L0504), and the workflow-vs-agent close is
> [L0505_lecture.md](L0505_lecture.md).
> **Anchor model: Claude Sonnet 4.6** (branch nodes), **Claude Haiku 4.5** (classifier) — the same
> mixed-model mechanism from [L03](../L03/objectives.md).

## section 1. The one new primitive

### slide 1.1 Fixed edge vs. conditional edge

- In [L03](../L03/objectives.md) you only used **fixed** edges: `add_edge("parse", "draft")`,
  taken every time, no exceptions.
- Now you're adding the **conditional edge**: a **routing function** reads state at runtime and
  returns the *name* of the next node, wired with `add_conditional_edges("classify", route,
  {...})`.
- diagram: two edge types side by side — on the left a solid **fixed** edge `A → B` (taken every
  time, tagged "L03"); on the right a dashed **conditional** edge where one `classify` node forks to
  three schematic branches that reconverge to `END`, tagged "new: a routing function picks the
  branch at runtime."

### slide 1.2 The decider — what your routing function is allowed to read

- Here are the three things a conditional edge's routing function can read in this lesson:
  **derived/computed data** already in state, a **model classification result** (a label a node
  wrote to state), or **direct user input** (a value supplied as part of the initial state).
- One thing it's never allowed to read: whether **the model asked for a tool**. That's L11.
- Say this line every time you write one: **here you (the developer) own the branch; in an agent,
  the model owns it.**

```python
def route(state: TicketState) -> str:
    # branches on a label already in state — not on the model choosing a tool
    return state["category"]   # "billing" | "technical" | "general"

builder.add_conditional_edges("classify", route,
    {"billing": "billing", "technical": "technical", "general": "general"})
```

- diagram: a central `route(state)` function with three **cyan** allowed inputs feeding into it —
  "derived / computed state", "a model's classification label", "direct user input" — and one
  **coral** input "did the model ask for a tool?" crossed out and tagged "L11 only." Caption: three
  things the decider may read; one it may not.

## section 2. The routing pattern — classify, then branch

### slide 2.1 An entry classifier that fans out

- **Routing**: an entry **classifier** node labels the input, and a **conditional edge** sends it
  down one of several specialized branches that converge to an exit.
- Example: a ticket gets classified **billing / technical / general**; each branch has its own
  focused prompt; all three converge to `END`.
- Per-node models, reused from L03: `classify` only needs to emit a label, so run it on the
  **cheap, fast model** (Haiku 4.5); the branches do the real reasoning, so run those on the
  **capable model** (Sonnet 4.6). This is the *mechanism* of mixed-model design — you'll get the
  full decision framework in **[L14](../L14/objectives.md)**.
- diagram: the concrete router — a `classify` node badged **Haiku 4.5** ("cheap: just emits a
  label") fanning via a **dashed** conditional edge to three branch nodes `billing` / `technical` /
  `general`, each badged **Sonnet 4.6** ("capable: the real reasoning"), all converging into `END`.
  Colour intent: the Sonnet badges are **cyan** (the real reasoning is the point); the Haiku badge
  is **ink-faint / neutral** — cheap is a design choice, **not coral** (coral means failure, and
  nothing here fails). This router is the section's motif: 2.2 and 2.3 re-show it with one thing
  changed.

### slide 2.2 Determinism: the workhorse proof

- Re-run the same ticket through your router and confirm the **same branch** executes every time.
  The branch *wording* may vary (the model is still non-deterministic inside a node); the **path**
  doesn't.
- This is what separates a workflow's routing from an agent's: a conditional edge, even though
  it's "runtime-chosen," is a deterministic function of state, not a coin flip.
- diagram: the 2.1 router drawn twice side by side ("run 1" / "run 2"), the **same cyan `billing`
  path** lit in both runs; under each, a short reply snippet in **ink-faint** whose wording
  differs slightly. Motif repeat of 2.1 with one thing changed — the wording varies, the path
  doesn't.

### slide 2.3 The fallback / default branch

- Your router needs a **defined behavior for every possible label**, not just the expected ones.
  When a classification doesn't cleanly match a branch, route it to a default/`general` fallback
  rather than letting the routing function raise.
- Treat this as a first-class design requirement, not an afterthought — it's a habit worth having
  before you run into messier real-world classifiers.
- diagram: third beat of the 2.1 router motif — an unexpected label (e.g. `"refund??"`) arrives
  in **coral** and is routed via a **coral dashed** edge into the **cyan** `general` fallback
  node, which still converges to `END`; beside it, a crossed-out **coral** `KeyError` box shows
  the alternative when no default branch exists. Coral = the surprise and the crash you avoided;
  cyan = the fallback that handles it.

## section 3. Branch on the user, not the model

### slide 3.1 The purest contrast with an agent

- A conditional edge can also branch on a value the **user** supplied directly — a menu choice, a
  form field — rather than a model classification: `if state["user_choice"] == "escalate": return
  "human_review"`.
- **No model is involved in the routing decision at all.** This is the sharpest possible contrast
  with an agent: the user picked the path, you wired the options.
- Here this user input arrives **as part of the initial state**; the graph then runs straight
  through. The *interactive* version — a graph that **pauses mid-run to ask** and resumes on the
  answer — needs LangGraph's `interrupt` plus a checkpointer, and you'll get that in
  **[L17](../L17/objectives.md)** (human-in-the-loop).
- diagram: the router motif with a different decider — a **cyan** initial-state chip
  (`user_choice: "escalate"`) feeding the conditional fork directly, with **no model node** in
  the decision path; off to the side, a **dashed ink-faint ghost** box "pause mid-run and ask →
  `interrupt`, lands in L17." Cyan = the user's value driving the edge; dashed faint = deferred,
  not this lesson.

### slide 3.2 Same shape, different decider — and they compose

- Put model-classification routing (section 2) and user-input routing side by side: *same graph
  shape — an entry point, a conditional edge, converging branches — different decider.*
- The general pattern for most real conditional workflows: route on the user's choice first, then
  run a model-driven **node** inside the chosen branch. Keep this rule in mind: **the user (or your
  own logic) owns the edge; the model can still do work inside a node.**
- diagram: two identical router shapes side by side — same entry → conditional edge → converging
  branches — differing only in the **decider**: the left one's fork is tagged "model classification
  (§2)", the right one's "direct user input (§3) — no model in the decision." Caption: same shape,
  different decider.

## section 4. When developer-controlled branching is enough

### slide 4.1 Reach for a router, not an agent, when the paths are known

- A router/switch is the right tool whenever the *set of possible paths is known in advance* and
  picking among them is a classification, lookup, or user choice — cheap, predictable, testable.
- Reach for an agent only when the model must decide *which and how many* steps to take, and that
  set of steps isn't enumerable ahead of time.
- Watch for the common failure mode: building an agent to do what a two-branch router would do
  just as well, at a fraction of the cost and unpredictability.
- diagram: two-up with paired bars — left panel, the known-paths **router** in **cyan** with a
  short cost bar; right panel, an **agent** doing the same two-branch job in **coral** with a
  visibly taller cost bar, tagged "open-ended steps, priced every run." Cyan = the right-sized
  tool; coral = the cost of handing over control you never needed to give away.

### slide 4.2 Bridge to L0505

- You haven't built a cycle yet — every graph in this lesson is still a DAG, still a workflow, no
  matter how many branches it has.
- You'll get the full workflow-vs-agent recap and close — what carries into L11, what precisely
  changes, and when to reach for which — in [L0505_lecture.md](L0505_lecture.md).
- diagram: a triptych of tiny graphs — L03's chain, this lesson's model-classified router, and
  the user-input router — all drawn **cyan** and all acyclic ("still workflows, however many
  branches"); floating beside them, one unattached **dashed ink-faint** back-edge tagged
  "→ L0505 / L11" — the only piece you haven't drawn yet. Dashed faint = deferred; nothing here
  is a failure, so no coral.
