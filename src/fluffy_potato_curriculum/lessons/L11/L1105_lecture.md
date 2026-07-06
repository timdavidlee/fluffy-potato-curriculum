# The config surface, and where the one-liner ends

```yaml
title: "The config surface, and where the one-liner ends"
keywords: create_agent, config surface, model, tools, system prompt, recursion limit, shallow agent, StateGraph, L15, ceiling, over-engineering, ReAct, plan-and-execute, supervisor, when to drop to a graph
estimated duration: 15
```

> **Lesson:** L11. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L11/objectives.md),
> [demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L11/demos_or_activities.md) (Demo 3).
> This is a **slide outline** for the closing demo. It runs after the build-and-run notebook
> ([L1103_lecture.ipynb](L1103_lecture.ipynb)) and reuses that same `create_agent` agent — it
> assumes the agent from Demo 2 is still in scope. It also closes the lab loop
> ([L1104](L1104_lab_empty.ipynb)), whose last problem exercises the config surface below.
> **Anchor model: Claude Sonnet 4.6.**

## section 1. The three knobs a shallow agent uses

### slide 1.1 Model, tools, system prompt — that's the surface

- On the same agent from the build demo, walk the config surface a **shallow** agent actually uses:

```python
agent = create_agent(
    model,                                 # 1. the model  (ChatAnthropic, Sonnet 4.6)
    [calculator, lookup, flaky_fetch],     # 2. the tools  (a plain list of callables)
    system_prompt="You are a precise assistant. Use the tools; do not answer from memory.",  # 3.
)
```

- table: the three knobs and what each controls.

| Knob | What it controls | L10 equivalent |
| --- | --- | --- |
| **model** | which chat model runs the `agent` node | the `model` you bound in the `agent` node |
| **tools** | the callables the model may invoke | the `TOOLS` list your `ToolNode` ran |
| **system prompt** | the standing instruction prepended to the conversation | the system message you prepended by hand |

- **That's it.** Three knobs. Everything else `create_agent` handles.

### slide 1.2 Swap one knob, same agent

- Change the **system prompt** once and re-run the *same* task: same agent, different instruction.
- diagram: two runs of the identical `create_agent` call side by side — left prompt *"answer in one
  sentence"*, right prompt *"show your reasoning step by step"* — same tools, same loop, different
  final-answer shape.
- The point is *"same agent, new instruction,"* not a dramatic behavior change. If a behavior swap
  doesn't show, swap the *format* of the answer — that always lands.

[↑ Back to top](#the-config-surface-and-where-the-one-liner-ends)

## section 2. What you did NOT have to touch

### slide 2.1 The graph and the state are managed for you

- State plainly what a shallow agent *doesn't* configure and doesn't need to:
  - **no graph to wire** — the `agent` node, the `ToolNode`, and the `tools → agent` back-edge are the framework's;
  - **no `route` to write** — the conditional exit is the prebuilt `tools_condition`;
  - **no `add_messages` reducer, no state schema** — the message list is threaded for you (`MessagesState`);
  - **no message-history bookkeeping** — the `ToolMessage` append after each tool call is automatic.
- diagram: the shallow-agent graph (agent / tools / back-edge, the L1102 motif) drawn inside a
  large ink-faint *"managed by `create_agent`"* bracket — nodes, back-edge, `tools_condition`
  routing, and `MessagesState` all shaded neutral as the framework's. Outside the bracket, three
  cyan plugs feeding in: **model**, **tools**, **system prompt** — the only parts that are yours.
- Contrast with L10, where **all** of that was yours to wire. That is the trade: you give up the
  knobs, you get the boilerplate for free.

### slide 2.2 The step cap is still there, just a default now

- In L10 you set `recursion_limit` on `invoke` yourself; here you don't have to — the cap still
  exists as the framework's **recursion / step limit** (LangGraph's default is 25 steps; set
  `recursion_limit` in the run config to change it).
- A runaway agent still trips it, and tripping it is **still a signal worth investigating** — the
  L10 lesson didn't go away, it moved inside the framework.

[↑ Back to top](#the-config-surface-and-where-the-one-liner-ends)

## section 3. The ceiling: when you'd drop below the one-liner

### slide 3.1 The question that ends the one-liner

- Ask it out loud: **"what would make you outgrow this one line?"**
- text: the moment your control flow stops being a *single tool-or-finish loop*. Concretely:
  - a **second model** for one step (a cheap router, an expensive planner);
  - a **branch** that isn't just "tool or finish";
  - a **custom node** (validate, summarize, call a sub-agent);
  - **state beyond the message list** (a running budget, a scratchpad, a plan).
- Any one of those is the signal: you have left the shallow single-loop shape.
- diagram: the single tool-or-finish loop drawn small and cyan at center, with four coral arrows
  breaking out of it, one per signal — *second model*, *non-tool branch*, *custom node*, *state
  beyond messages*. Caption: *"any one arrow means you've outgrown the one-liner."*

### slide 3.2 That's exactly the door into L15

- diagram: a "ceiling" line. Below it, labeled *`create_agent` (shallow, single loop)*: model,
  tools, prompt. Above it, labeled *explicit `StateGraph` (L15)*: custom nodes, branches, reducers,
  state schema, and the named patterns (**ReAct, plan-and-execute, supervisor, …**).
- When the control flow branches, you **drop to an explicit `StateGraph`** and wire nodes / edges /
  reducers yourself. Building that graph — and the patterns on top of it — is
  **[L15](../../CURRICULUM_PRD.md)**. L11 names the door; L15 opens it.

### slide 3.3 Knowing where the ceiling is *is* the skill

- Two opposite mistakes bracket the line:
  - **Over-engineering:** reaching for a hand-built graph on a single loop — the L10-objective-4
    mistake (a framework where 50 lines would do).
  - **Under-engineering:** refusing to leave the one-liner when the flow genuinely branches.
- L11 teaches the **shallow** side of that line: *use `create_agent` until the control flow stops
  being a single loop.* L15 teaches the other side.

### slide 3.4 Where you land

- You can now build a shallow agent **two ways**: by hand (L10) and in one line (L11), and you know
  they're the *same loop*.
- The returned **message history** from your `create_agent` run is the raw material the next
  lessons read as a **trace** ([L12](../L12/objectives.md)) and judge with an **eval set**
  ([L13](../L13/objectives.md)).
- The mental model you now hold — the shallow agent as *the ReAct pattern, prebuilt* — is the thing
  **L15** builds on top of. Ask its opening question and stop there: *what do you build when a
  single tool-calling loop isn't the right shape?*
- diagram: a ladder of the arc — **L10** hand-built loop → **L11** `create_agent` (you are here,
  cyan) → **L12** read the run as a trace → **L13** judge it with an eval set → **L15** explicit
  `StateGraph`. Future rungs dashed (deferred), the L11 rung solid cyan.

### slide 3.5 Three shallow-agent gotchas, named

- Before you leave, name the three ways `create_agent` lulls you into forgetting the L10 machinery is
  still underneath. All three are the same trap: **the convenience hides the machinery, but the
  machinery is still there** — having built the L10 loop by hand, read `create_agent` as *that,
  packaged.*
- table: the three gotchas, the one-line cure, and where you saw it.

| Gotcha | Cure | Where you saw it |
| --- | --- | --- |
| **Assuming the one-liner can't run away** — trusting a prebuilt agent not to loop forever "because it's prebuilt" | the step cap didn't vanish, it moved behind the constructor — know where it lives and treat hitting it as a **signal**, exactly as in L10 | slide 2.2 (the step cap is still there, just a default) |
| **Treating `create_agent` as un-debuggable magic** — can't map the one-liner back to agent → tools → back-edge, so a bad run is unexplainable | debug the shallow agent *as the L10 loop it is* — read the returned `messages`, find the turn that went wrong; the framework hid the wiring, not the behavior | section 2 + slide 1.1 (every knob has an L10 twin) |
| **Wrong altitude** — hand-building a `StateGraph` when the one-liner fits (over-engineering), *or* clinging to it after the flow outgrows a single loop (under-engineering) | stay on `create_agent` until the control flow stops being one loop (a second model, a non-tool branch, custom state) — then drop to an explicit graph (**L15**) | section 3 (the ceiling) — this whole discussion |

- Knowing where the ceiling is *is* the shallow-agent skill — neither reflex (always hand-build, or
  never leave the one-liner) is right.

[↑ Back to top](#the-config-surface-and-where-the-one-liner-ends)
