# From loop to graph: draw what `create_agent` wraps

```yaml
title: "From loop to graph: draw what create_agent wraps"
keywords: shallow agent, create_agent, langgraph, MessagesState, tools_condition, agent node, tools node, back-edge, cycle, conditional exit, workflow vs agent, acyclic, recursion_limit, ToolNode, add_messages, L10 graph mapping, L15 StateGraph, ReAct
estimated duration: 15
```

> **Lesson:** L11. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L11/objectives.md),
> [demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L11/demos_or_activities.md) (Demo 1).
> This is a **slide outline** for the opening demo — *drawn before any code is written*. It sets up
> the build-and-run notebook that follows ([L1103_lecture.ipynb](L1103_lecture.ipynb)), where the
> diagram sketched here is rendered from a real `create_agent` result.
> **Anchor model: Claude Sonnet 4.6** — a single model throughout, so `create_agent` is the only
> new thing on screen versus the L10 agent graph you wired by hand.

## section 1. Recap: an agent is a loop you already wrote

### slide 1.1 One sentence from L10

- You ended L10 with this: *an agent is a loop around a stateless model — call the model, run the
  tool it asked for, feed the result back, repeat, until the model stops asking or a cap fires.*
- L10's last demo previewed today: **"every framework you'll meet is a fancier version of the loop
  you wrote."** L11 is that fancier version, in one line.
- Today introduces **no new control flow.** Model → tool → model until termination is the L10
  skeleton, unchanged. The only new thing is *who writes the loop.*
- diagram: the bare L10 loop as a circular flow — `model` → `tool` → back to `model`, the loop
  arrow in cyan, a small **ink-faint** exit arrow to *done* when the model stops asking (the cyan
  cycle stays the only emphasized path); caption *"the loop you wrote by hand in L10."* This motif
  repeats all lesson — this is its plainest form.

### slide 1.2 The one-liner, named now

- The whole lesson is one function call:

```python
from langchain.agents import create_agent

agent = create_agent(model, [calculator, lookup, flaky_fetch], system_prompt=...)
```

- `create_agent` returns a **running shallow agent**: the loop, the routing, the message
  bookkeeping, and the step cap — all supplied.
- **Shallow agent, defined:** one model, one tool set, one decision point that either calls a tool
  or finishes. That is *exactly* the L10 agent graph. Not a deep agent (planning / memory /
  reflection — L18). Shallow ≠ lesser; most production agents are shallow.
- diagram: one cyan box holding the shallow agent's three chips — *model · tools · one decision
  point* — beside a **dashed ink-faint ghost box** of deep-agent chips (*planning / memory /
  reflection → L18*). explicitly no coral — deep isn't a failure, just later. Pre-echoes the
  container framing slide 4.1 lands on.

[↑ Back to top](#from-loop-to-graph-draw-what-create_agent-wraps)

## section 2. Recall L04: the line between a workflow and an agent

### slide 2.1 A workflow is acyclic; you drive it

- In [L04](../L04/objectives.md)/[L05](../L05/objectives.md) you wired a **workflow** — a directed
  *acyclic* graph. *You* owned the path; the model never decided what ran next.
- diagram: L04's DAG — `start → step A → step B → end`, straight arrows, no loop back, every
  chain edge drawn **cyan** ("the developer owns every edge" — it's the cyan dropping to ink-faint
  in 2.2 that makes the back-edge read as the change). Caption: *"the developer owns every edge."*

### slide 2.2 An agent adds exactly one thing: a back-edge

- An **agent** takes those same primitives and adds **one edge**: a transition that loops back to
  the model and hands it the decision of what runs next.
- text: *a workflow is acyclic and developer-driven; the **back-edge** that hands the path to the
  model is what makes it an agent.*
- diagram: the *same* DAG as slide 2.1 (same boxes, same positions, edges now ink-faint) with
  exactly **one new edge** drawn in: a cyan arrow curving from the last step back up to the model
  step. Nothing else changes. Caption: *"one edge — the model now owns the path."*
- **The back-edge is the cycle, and the cycle is the agent.** Keep this sentence; the rest of the
  lesson is a picture of it.

[↑ Back to top](#from-loop-to-graph-draw-what-create_agent-wraps)

## section 3. Draw the graph `create_agent` wraps

### slide 3.1 The two nodes and two edges

- Draw the shallow-agent graph piece by piece — this is a *picture of the L10 graph you wired by
  hand*, not something you build today.
- diagram: two nodes and the wiring — nodes as cyan boxes: `__start__ → agent`; a **conditional
  exit** out of `agent`: (tool call) → `tools`, (plain text) → `__end__` with the exit path
  **ink-faint**; and a fixed **back-edge** `tools → agent` emphasized **cyan** — it *is* the point.
  No coral anywhere. Label the `tools → agent` arrow **"the back-edge / the cycle."** This is the
  motif 3.2 and 3.3 reuse — draw it to be redrawn.

```text
        ┌─────────────────────────────┐
        │                             │  back-edge (the cycle)
        ▼                             │
   ┌─────────┐   tool call?   ┌──────────┐
─▶ │  agent  │ ─────yes─────▶ │  tools   │
   └─────────┘                └──────────┘
        │
        │ no tool call
        ▼
     __end__  (natural termination)
```

### slide 3.2 Map every piece back to what you wired in L10

- table: each piece you wired **by hand** in L10's `StateGraph`, and what `create_agent` gives you
  for it. If you can't make this mapping yet, slow down — *this mapping is the objective.* Two rows
  are the payoff: your hand-written `route` **is** the prebuilt `tools_condition`, and your
  `ToolNode` is the *same* `ToolNode` — the framework just packaged what you already wrote.
- diagram: the slide-3.1 graph re-drawn with the graph plumbing dropped to **ink-faint** and a
  **cyan argument chip** pinned to each piece — `model` on the agent node, `tools` on the ToolNode,
  `tools_condition` on the conditional exit, *"built in"* on the back-edge, and `system_prompt` /
  `recursion_limit` chips at the margins. Cyan = what you pass in, ink-faint = wiring the framework
  owns; no coral. Middle of the 3.1 (bare) → 3.2 (annotated) → 3.3 (traced) triple — the payoff
  picture above the table.

| You wired by hand in L10 | `create_agent` gives you |
| --- | --- |
| `TypedDict` state + the `add_messages` reducer | `MessagesState` — the same thing, prebuilt (you don't declare it) |
| the `agent` node: `model.bind_tools(...).ainvoke(...)` | the **`model`** argument |
| `ToolNode(tools, handle_tool_errors=True)` | the **`tools`** argument (the *same* `ToolNode` inside) |
| your hand-written `route` function | the prebuilt **`tools_condition`** |
| `add_edge("tools", "agent")` — the back-edge | built in |
| the system message you prepended | the **`system_prompt`** argument |
| `recursion_limit` on `ainvoke` | the same knob, on the run config (default 25) |

- **The two "oh — it just packaged what I wrote" beats.** In L10 you already saw `ToolNode` revealed
  as "the message-history bookkeeping, prebuilt." The same move applies to the *edge*: the `route`
  function you wrote by hand is exactly `langgraph.prebuilt.tools_condition`. Node and edge — both
  the thing you built, packaged. (LangGraph labels the model-call node `model` in the rendered
  graph; we called it `agent` in L10. Same node.)

### slide 3.3 Trace one run on the diagram

- Follow a run with your finger: `agent` → (tool call?) → `tools` → back-edge → `agent` → (no tool
  call) → `__end__`.
- diagram: the slide-3.1 graph repeated, with one run traced onto it as numbered cyan step badges —
  ① `agent`, ② yes → `tools`, ③ the back-edge (emphasized), ④ `agent` again, ⑤ no tool call →
  `__end__`. Untraveled edges stay ink-faint; the back-edge carries the *"the cycle is the agent"*
  label.
- Point at the back-edge and say it out loud: **that cycle is the agent.**
- The conditional exit *is* the L10 branch. "Is there a tool call?" used to be an `if` in your
  Python; `create_agent` makes it a routing decision inside the graph. **The decision is identical;
  only who writes it changed.**

[↑ Back to top](#from-loop-to-graph-draw-what-create_agent-wraps)

## section 4. This is a mental model, not a build

### slide 4.1 You will not wire this graph by hand today

- `create_agent` **builds exactly this graph for you.** You configure model + tools + prompt and
  run it; you do not assemble nodes, edges, or reducers.
- **You do not need to understand `StateGraph` to use `create_agent`** — that is precisely what the
  one-liner spares you. Assembling the graph node-by-node (state schema, `add_messages` reducer,
  explicit conditional edges) is **[L15](../../CURRICULUM_PRD.md)'s** job.
- The point of the diagram is only this: `create_agent` is **not magic** — it is the graph you
  already wired, packaged.
- diagram: an outer cyan `create_agent(model, [tools], system_prompt=…)` box physically containing
  the small slide-3.1 graph, plus one **dashed ink-faint ghost chip** — *"assemble it node-by-node:
  StateGraph → L15."* Block/nested; no coral. The loop motif's "shrunk inside a wrapper" beat —
  the literal picture of the lecture title.

### slide 4.2 The step cap did not disappear

- A common misread: *"the one-liner removed the need for a step cap."* It didn't.
- `create_agent` ships a **recursion / step limit** — the same `recursion_limit` you set on
  `ainvoke` in L10 (LangGraph's default is 25 loop steps; you can raise or lower it in the run config).
- A runaway agent still hits that cap, and **hitting it is still a signal worth investigating** —
  exactly the L10 lesson, restated.
- diagram: the loop motif again with a step counter ticking up beside it — `1, 2, 3, …` in
  ink-faint, a hard coral cap line at **25** labeled `recursion_limit` (run config), and a coral
  *"runaway run stops here — investigate, don't just raise the cap"* callout where the ticks hit
  the line.

### slide 4.3 What's next

- Next demo ([L1103](L1103_lecture.ipynb)): *build* this agent in one `create_agent` call, run it on
  the two L10 tasks for behavioral equivalence, read the returned messages, and render this exact
  graph from the real agent — it matches the sketch above.
- A quick look ahead, no need to chase it yet: the shallow agent `create_agent` gives you *is* a
  named pattern — **ReAct** (reason, act, repeat). L15 drops below the one-liner to build that
  graph explicitly and surveys the others (plan-and-execute, supervisor, …). Today you have the
  one-liner and a picture of what it wraps.
- diagram: the loop motif small, in cyan, with a **"ReAct"** label pinned on it, and beside it a
  **dashed ink-faint row** of sibling patterns — *plan-and-execute · supervisor → L15*. Bookends
  slide 1.1's plainest-form loop.

[↑ Back to top](#from-loop-to-graph-draw-what-create_agent-wraps)
