# Workflow vs. agent: the line is a single back-edge

```yaml
title: "Workflow vs. agent: the line is a single back-edge"
keywords: workflow, agent, back-edge, cycle, dag, langgraph, types of loops, retry loop, evaluator-optimizer, when to use which, control, predictability, cost, latency, bridge to l12, building effective agents
estimated duration: 14
```

> **Lesson:** L05. **Roadmap:** Demo 4 in [demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L05/demos_or_activities.md).
> This is the closing lecture — mostly **diagram + discussion**, no live build. It recaps the
> compiled workflows from L04's and this lesson's demos ([L04's Demo 1](../L04/L0403_lecture.ipynb)
> / [this lesson's Demo](L0503_lecture.ipynb)) and *names* the one change that makes an agent.
> Building the agent is **L11's** job.
> **Anchor:** the workflow-vs-agent contrast, stated verbatim so it carries into L11.

## section 1. Recap — what a workflow is

### slide 1.1 Everything you built was acyclic

- Across [L04](../L04/objectives.md)'s and this lesson's demos and labs you built three graphs — a
  prompt chain (L04), a model-classified router (L05), and a user-input router (L05). **Every one
  was a DAG**: trace any path with your finger and every arrow goes forward; it always reaches
  `END`.
- diagram: L04's chain `parse → draft → policy_check → END` with a finger-trace arrow showing
  "forward only, always terminates." Render it to **visually match the L04 deck's chain** (same
  node shapes, cyan forward edges, `END` in ink-faint) — a cross-lesson motif, so students
  recognize the exact graph they built.
- The model did real work *inside* the nodes (parse, classify, draft), but **you wired every
  edge.** That's the definition of a workflow.

### slide 1.2 The primitives you now own

- table: the L04 + L05 primitives — and the note that **L11 reuses every one of them unchanged.**

| Primitive | What it is | Reused in L11? |
| --- | --- | --- |
| `StateGraph` | the builder | yes |
| node | typed function: state → update | yes |
| edge | fixed transition `A → B` | yes |
| conditional edge | routing function reads state → next node | yes |
| typed state + reducer | the data threaded through nodes | yes (message history) |
| `compile` / `invoke` | build + run | yes |
| Langfuse callback | watch the run | yes |

## section 2. The one change that makes an agent

### slide 2.1 Add a back-edge

- L11 keeps **all** of the above and adds exactly one thing: a **conditional edge that loops back
  to the model**. After the model node, the graph either routes to a `tools` node and **loops back
  to the model**, or routes to `END`.
- diagram: the acyclic chain on the left; on the right the same shape with one new **dashed cyan
  back-edge** curving from the model node to `tools` and back — labeled "the only thing L11 adds."
  The back-edge is **cyan, not coral**: it's the point of the slide — the one addition — not a
  failure; dashed says "you draw it in L11." These two shapes plus the back-edge are the deck's
  motif — 2.3 and 5.2 re-show them.
- That single back-edge hands the **model** control of the path: *it* decides whether to call a
  tool and go again, or stop. The acyclic **workflow** becomes a cyclic, model-driven **agent**.

### slide 2.2 You've seen this cycle before

- That model → tools → model loop is exactly the one you **hand-rolled in [L10](../L10/objectives.md)**
  — only there the `while`/`if` was plain Python, and in L11 it's a graph edge.
- diagram: side by side — L10's `while` loop pseudocode and L11's cyclic graph — captioned "same
  loop, now expressed as a graph."
- So L11 isn't a new world for you: it's **L04/L05's primitives + L10's loop**, written as one
  back-edge.

### slide 2.3 A conditional edge is still not "the model is an agent" by itself

- Be precise: a conditional edge in this course has so far **always** branched on **state you
  set** (L05's classifier label, or direct user input). It's an **agent** only when the conditional
  edge branches on **the model's own decision to keep going** *and* that edge **loops**.
- You might think "but the classifier was the model deciding" — it wasn't: the model produced a
  *label in state*; your routing function read that label and chose the edge. The model never
  chose the edge, and **it never looped.**
- diagram: two-up reusing both deck motifs — left, the L05 router in **cyan** (classifier writes
  a *label into state*, **you** own the conditional edge, no cycle anywhere); right, 2.1's agent
  shape with the **dashed cyan back-edge** (the model's own decision picks the edge, *and* it
  loops). Caption: a conditional edge alone isn't an agent — it takes both.

### slide 2.4 Loops aren't only for agents — three back-edges, one axis

- The agent's tool loop is the only cycle this course *builds* (L10/L11) — but it's not the only
  reason a graph ever loops back to an earlier node. Two loop shapes you'll meet in real
  workflows:
  - **Retry / self-correction:** `generate → validate`, and `validate` routes **back** to
    `generate` until a pass flag is set — or an attempt counter in state runs out.
  - **Evaluator–optimizer:** `draft → critique`, routing back to redraft until the critique's
    score clears a bar. Same shape, aimed at quality instead of errors.
- Ask the decider question for each: who decides whether to go around again? **A check you
  wrote** — a flag, a counter, a score bar. Loops and all, these are **still workflows.**
- So the honest version of L04's "a workflow never loops back": a workflow *can* loop back — but
  **you** authored its exit condition. It's an agent only when the routing function reads the
  **model's own decision** to keep going. The back-edge is necessary, not sufficient.
- diagram: three small cycles in a row, same node shapes as the deck motif — `generate ⇄ validate`
  with a **solid cyan** back-edge labeled "exit: your pass flag / attempt counter";
  `draft ⇄ critique` with a **solid cyan** back-edge labeled "exit: your score bar"; and 2.1's
  agent shape with the **dashed cyan** back-edge labeled "exit: the model stops asking for tools."
  Solid = you own the loop today; dashed = the one L11 draws. Caption: same edge three times,
  three deciders — only the third is an agent.

## section 3. When to use which

### slide 3.1 Prefer the simplest shape that solves the task

- table: pick the shape from the task, not from excitement.

| Use a **workflow** when… | Reach for an **agent** when… |
| --- | --- |
| the task has a **known shape** | the steps **can't be known in advance** |
| you want predictability + low cost | the model genuinely must decide its own path |
| you need it testable and easy to trace | open-ended exploration is the point |
| (most production "AI features") | (the minority — but the loud minority) |

- **Determinism is a feature, not a limitation.** A workflow takes the same path on the same input:
  predictable, cheaper, lower-latency, and trivially testable (which is why the L13 eval set drops
  straight onto it).

### slide 3.2 The common failure mode

- Watch for this failure mode: **reaching for an agent when a workflow would do.** It costs more,
  is less predictable, and is harder to debug — you'd be handing the model control you never
  needed to give away.
- The engineering skill is choosing the **simplest shape that solves the task** — and that's
  usually a workflow. (This is the thesis of Anthropic's *Building Effective Agents*.)

## section 4. Three routing gotchas, named

### slide 4.1 The pitfalls to catch when you wire your own conditional edge

- This lesson showed all three of these in passing — Demo 4's workflow-vs-agent line, Demo 2's
  ambiguous-ticket fallback, and Demo 1's five-hop trace. Here they are again as portable gotchas
  you can catch yourself committing the first time you wire a router. Two of them (#1 and #3) are
  the workflow-vs-agent line at **two altitudes**: #1 is choosing the wrong *shape* on purpose; #3
  is the mechanism *slipping* — the model taking the wheel by accident. #2 is a different axis
  entirely: routing *robustness*, not who decides.
- table: the gotcha, the one-line cure, and where you saw it.

| Gotcha | Cure | Where you saw it |
| --- | --- | --- |
| **Wrong shape** — reaching for an agent when the task has a known shape (more cost, less predictability, harder to debug), or forcing a rigid routed DAG when the steps genuinely can't be known ahead | default to the **simplest shape that fits**: a router is right whenever the set of paths is known ahead and picking among them is a classification, lookup, or user choice; a model-driven loop (agency) is a deliberate choice, not a nicety | §3 (when to use which) + slide 2.1 (the back-edge is the whole difference) |
| **Brittle branch conditions** — a routing function that assumes the classifier returns one of the expected labels and `KeyError`s (or silently mis-routes) on anything off-menu | validate the label is in the allowed set ([L02](../L02/objectives.md)'s enum-as-contract) and always wire a **default / `END`** branch — a router that only knows how to succeed isn't done | [L0502](L0502_lecture.md) §2.3 (the fallback branch) + Demo 2's ambiguous ticket |
| **The model owning the branch by accident** — routing on a *raw model output* (the free-form reply used as the destination) instead of on a small **validated label** your plain-Python code branches on — quietly handing the model the choice of path | the classifier writes a *constrained label* (again L02's enum-as-contract); your routing function reads *that* and owns the branch. If you actually want the model to choose the path, build an agent ([L11](../L11/objectives.md)) **on purpose** — don't back into one | [L0502](L0502_lecture.md) §1.2 (the decider reads state *you* control) + slide 2.3 (a label in state, not the model choosing) |

- #3 points straight forward to [L11](../L11/objectives.md), where reading the model's own decision
  is the whole point — on purpose. Keeping #1 and #3 sharp is exactly this lesson's spine (the
  back-edge in slide 2.1): a model *inside a node* is fine; the model *owning the edge* is the line.
- diagram: three coral vignettes in a row, each a broken version of a picture from this deck — (1)
  **wrong shape**: the §3 router in coral carrying an unnecessary dashed back-edge, tagged "a
  model-driven loop where a router would do"; (2) **brittle branch**: an off-menu label
  (`"refund??"`) in coral hitting a crossed-out `KeyError` box with no default branch (the L0502
  §2.3 picture, broken); (3) **accidental agency**: the routing function reading the model's raw
  reply directly (a coral arrow from the model's free-form output straight into the edge) instead
  of a cyan validated-label chip. Each vignette pairs with its cyan cure from the sections above;
  coral marks the mistake, the fix is the healthy version you already drew.

## section 5. Bridge to L11

### slide 5.1 What carries forward

- Everything. `StateGraph`, nodes, edges, typed state, reducers, `compile`/`invoke`, and the
  Langfuse hookup all reappear in L11 **unchanged**.
- L11 also re-teaches the primitives from scratch so that lesson stands alone — take the overlap
  as deliberate **reinforcement**, not repetition. The vocabulary is identical on purpose.

### slide 5.2 The one sentence to leave with

- **A workflow is a graph whose path you wire (acyclic); an agent is a graph whose path the model
  drives (cyclic). The line between them is a single back-edge.**
- Next lesson, you draw that edge. Everything else, you already built.
- diagram: motif bookend — re-show 2.1's two shapes small, side by side: the acyclic workflow
  ("path you wire") and the same shape with the **dashed cyan back-edge**, now tagged "you draw
  this edge next lesson." Nothing else changes between the panels — that's the sentence, drawn.
