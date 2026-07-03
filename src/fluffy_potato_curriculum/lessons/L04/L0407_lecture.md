# Workflow vs. agent: the line is a single back-edge

```yaml
title: "Workflow vs. agent: the line is a single back-edge"
keywords: workflow, agent, back-edge, cycle, dag, langgraph, when to use which, control, predictability, cost, latency, bridge to l12, building effective agents
estimated duration: 12
```

> **Lesson:** L04. **Roadmap:** Demo 4 in [demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L04/demos_or_activities.md).
> This is the closing lecture — mostly **diagram + discussion**, no live build. It reuses one of the
> compiled workflows from the demos ([L0403](L0403_lecture.ipynb) / [L0405](L0405_lecture.ipynb)) and
> *names* the one change that makes an agent. Building the agent is **L14's** job.
> **Anchor:** the workflow-vs-agent contrast, stated verbatim so it carries into L14.

## section 1. Recap — what a workflow is

### slide 1.1 Everything you built was acyclic

- Across the demos and labs you built three graphs — a prompt chain, a model-classified router, and
  a user-input router. **Every one was a DAG**: trace any path with your finger and every arrow
  goes forward; it always reaches `END`.
- diagram: the L0403 chain `parse → draft → policy_check → END` with a finger-trace arrow showing
  "forward only, always terminates."
- The model did real work *inside* the nodes (parse, classify, draft), but **the developer wired
  every edge.** That is the definition of a workflow.

### slide 1.2 The primitives you now own

- table: the L04 primitives — and the note that **L14 reuses every one of them unchanged.**

| Primitive | What it is | Reused in L14? |
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

- L14 keeps **all** of the above and adds exactly one thing: a **conditional edge that loops back
  to the model**. After the model node, the graph either routes to a `tools` node and **loops back
  to the model**, or routes to `END`.
- diagram: the acyclic chain on the left; on the right the same shape with one new **dashed
  back-edge** curving from the model node to `tools` and back — labeled "the only thing L14 adds."
- That single back-edge hands the **model** control of the path: *it* decides whether to call a
  tool and go again, or stop. The acyclic **workflow** becomes a cyclic, model-driven **agent**.

### slide 2.2 You have seen this cycle before

- That model → tools → model loop is exactly the one you **hand-rolled in [L10](../L10/objectives.md)**
  — only there the `while`/`if` was plain Python, and in L14 it's a graph edge.
- diagram: side by side — L10's `while` loop pseudocode and L14's cyclic graph — captioned "same
  loop, now expressed as a graph."
- So L14 is not a new world: it's **L04's primitives + L10's loop**, written as one back-edge.

### slide 2.3 A conditional edge is still not "the model is an agent" by itself

- Be precise: in L04 a conditional edge branched on **state the developer set** (a label, a user
  choice). It is an **agent** only when the conditional edge branches on **the model's own decision
  to keep going** *and* that edge **loops**.
- If a student says "but the classifier was the model deciding" — no: the model produced a *label
  in state*; the developer's routing function read that label and chose the edge. The model never
  chose the edge, and **it never looped.**

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
  predictable, cheaper, lower-latency, and trivially testable (which is why the L12 eval set drops
  straight onto it).

### slide 3.2 The common failure mode

- Name it out loud: **reaching for an agent when a workflow would do.** It costs more, is less
  predictable, and is harder to debug — you handed the model control you never needed to give away.
- The engineering skill is choosing the **simplest shape that solves the task** — and that is
  usually a workflow. (This is the thesis of Anthropic's *Building Effective Agents*.)

## section 4. Bridge to L14

### slide 4.1 What carries forward

- Everything. `StateGraph`, nodes, edges, typed state, reducers, `compile`/`invoke`, and the
  Langfuse hookup all reappear in L14 **unchanged**.
- L14 also re-teaches the primitives from scratch so the agent lesson stands alone — treat the
  overlap as deliberate **reinforcement**, not repetition. The vocabulary is identical on purpose.

### slide 4.2 The one sentence to leave with

- **A workflow is a graph whose path the developer wires (acyclic); an agent is a graph whose path
  the model drives (cyclic). The line between them is a single back-edge.**
- Next lesson, you draw that edge. Everything else, you already built.
