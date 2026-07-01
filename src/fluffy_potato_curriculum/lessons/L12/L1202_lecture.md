# Shallow agents in LangGraph: the model drives the graph

```yaml
title: "Shallow agents in LangGraph: the model drives the graph"
keywords: langgraph, agent, shallow agent, stategraph, node, edge, conditional edge, back-edge, state, reducer, add_messages, toolnode, create_agent, message history invariant, recursion limit, control flow as data, eval carry-over, langfuse, chatanthropic
estimated duration: 80
```

> **Lesson:** L12. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L12/objectives.md).
> This is the written reference lecture — thorough on purpose, so a student who missed the live
> delivery can rebuild the lesson from the page. The live demos are notebooks
> ([L1203](L1203_lecture.ipynb) build the agent, [L1205](L1205_lecture.ipynb) state & reducers,
> [L1207](L1207_lecture.ipynb) eval carry-over + tracing); the bridge to L13 is
> [L1208](L1208_lecture.md); hands-on practice is in the L12 labs (L1204, L1206).
> **Anchor model: Claude Sonnet 4.6** — a single model throughout, so the *only* variable versus
> the L07 hand-rolled loop is the graph shape.

## section 1. The lesson in one claim

### slide 1.1 It's the same loop, drawn as a graph

- L12 introduces **no new control flow**. Model → tool → model until termination is *exactly* the
  loop you hand-rolled in [L07](../L07/objectives.md).
- What's new is the **shape**: an explicit `while` loop becomes an explicit **graph** of nodes and
  edges over a shared **state**, and LangGraph supplies the runtime that drives it.
- You met every primitive already in [L11](../L11/objectives.md) — `StateGraph`, node, edge,
  conditional edge, typed state, reducer. L12 reuses them unchanged and adds **one** thing.
- The pedagogical bet: meeting the framework *after* hand-rolling the loop means the framework
  reads as **conveniences over a familiar skeleton**, not as magic.

### slide 1.2 The one thing L12 adds: a back-edge

- L11's graphs were **acyclic** (DAGs): the developer wired every edge, the model never chose the
  path. L12 adds a **conditional edge that loops back to the model** — a **back-edge**.
- That single edge hands control of the path to the *model*: *it* decides whether to call another
  tool and go again, or to stop. The acyclic **workflow** becomes a cyclic, model-driven **agent**.
- diagram: L11's acyclic chain on the left; on the right the same primitives with one new dashed
  back-edge curving from a `tools` node back to the `agent` node — labeled "the only thing L12 adds."

### slide 1.3 Workflow vs. agent — the line is who drives the path

- table: the one difference, carried verbatim from L11.

| | **Workflow** (L11) | **Agent** (L12) |
| --- | --- | --- |
| Who decides the path? | the **developer** (fixed/derived logic) | the **model** |
| Graph shape | **acyclic** (DAG) — always reaches `END` | **cyclic** — loops `agent → tools → agent` |
| Where the model works | *inside* nodes | inside nodes **and** chooses the path |
| Predictability | same input → same path | varies; the model may loop |

- The model is involved in **both**. Agency is about who controls the *path*, not whether a model
  is called somewhere.

## section 2. The shallow-agent graph (objective 1)

### slide 2.1 What "shallow" means — define it now

- A **shallow agent** is a *single tool-calling loop*: **one** model, **one** set of tools, **one**
  decision point that either calls a tool or finishes. It is the L07 loop, now a graph.
- "Shallow" is a **scope, not a grade.** Most production agents are shallow.
- *Deep* agents add planning, persistent memory, sub-todos, and reflection — a heavier, later
  choice (L16). Named here only as "what we are **not** building yet."

### slide 2.2 Draw it: four pieces

- diagram: an entry arrow into an **`agent`** node; a **conditional edge** out of `agent` that
  forks to a **`tools`** node (when the model emitted a `tool_use`) or to **`END`** (no tool_use);
  and a fixed **edge** `tools → agent` — the back-edge that closes the loop.
- The pieces, named with the vocabulary you reuse into L13:
  - **`agent` node** — calls the model on the current messages; may emit `tool_use` blocks.
  - **`tools` node** — runs every requested tool and appends a matching `tool_result`.
  - **conditional edge** — a routing function reads state and returns the next node's name.
  - **edge `tools → agent`** — the back-edge; after tools run, go back to the model.

### slide 2.3 Map every piece back to an L07 line

- table: the graph is the L07 loop, re-expressed. If you can't map a piece to an L07 line, slow
  down — *this mapping is objective 1.*

| L07 hand-rolled loop | L12 graph piece |
| --- | --- |
| "call the model" | the `agent` node |
| "run every `tool_use`, append a `tool_result`" | the `tools` node |
| loop back after running tools (`while`) | the edge `tools → agent` |
| `if there's a tool_use: … else: return` | the conditional edge out of `agent` |
| the `messages` list, mutated in place | the **state**, merged by a **reducer** |
| `max_steps` cap | LangGraph's **recursion limit** |

- The **conditional edge is the L07 branch**, lifted out of Python control flow into the graph.
  "Is there a `tool_use`?" used to be an `if`; now it's a routing function on an edge. The decision
  is identical; only its *location* moved.

### slide 2.4 Why a graph at all?

- A `while` loop encodes control flow **implicitly**, in Python statements. A graph makes control
  flow **data** — nodes and edges you can inspect, draw, reroute, and extend.
- Be honest about the trade: for a **single** loop the graph is roughly **break-even** — more
  setup for equivalent behavior.
- The payoff shows up when the control flow stops being one loop — branches, multiple tools nodes,
  sub-graphs — which is precisely the motivation for **L13 (patterns)**.

## section 3. Build it on StateGraph (objective 2)

### slide 3.1 The state schema — messages plus one counter

- The **state** is a typed object threaded through every node. For a shallow agent it is
  essentially the running **message history** — the same list L07 mutated — plus one `step` counter
  we keep purely to make reducers and typing concrete.
- diagram: an `AgentState` box with two fields: `messages: Annotated[list, add_messages]` tagged
  "append reducer", and `step: int` tagged "default reducer (overwrite)".

```python
from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]  # APPENDS (see section 4)
    step: int                                             # overwrites (default reducer)
```

### slide 3.2 The two nodes

- The `agent` node calls the model (bound with the tool schemas) on the current messages and
  returns the response **to be appended**. The `tools` node runs every requested tool and returns
  the matching `tool_result`s — *the same message-history invariant from L07*, now localized to one
  node.
- A node returns a **partial update** (just the fields it changed), never the whole state — exactly
  as in L11.

```python
def agent_node(state: AgentState) -> dict[str, object]:
    """The L07 'call the model' step, as a node."""
    response = model.invoke(state["messages"])      # model is ChatAnthropic bound with tools
    return {"messages": [response], "step": state["step"] + 1}
```

- For the `tools` node we use LangGraph's **prebuilt `ToolNode`** (section 5) — it runs each
  `tool_use` and appends a `tool_result`, the L07 dispatch step packaged for you.

### slide 3.3 Wire it, compile it

- The same `StateGraph` recipe as L11, plus the **back-edge**:

```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

def route(state: AgentState) -> str:
    last = state["messages"][-1]
    # the L07 'is there a tool_use?' branch, now a routing function
    return "tools" if getattr(last, "tool_calls", None) else END

builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools, handle_tool_errors=True))
builder.set_entry_point("agent")
builder.add_conditional_edges("agent", route, {"tools": "tools", END: END})
builder.add_edge("tools", "agent")        # <-- the back-edge: the only thing L12 adds
app = builder.compile()
```

- diagram: the rendered Mermaid of the compiled graph (`app.get_graph().draw_mermaid()`) next to
  the hand-drawn diagram from slide 2.2 — they match. The render needs **no API key**: the control
  flow *is* data.

### slide 3.4 Run it — behavioral equivalence with L07

- Invoke the compiled graph on the **L07 chaining task** ("compute, then look up a population"):
  it issues `calculator` then `lookup` and terminates naturally — the *same tool sequence* the
  hand-rolled loop produced.
- Invoke it on the **`flaky_fetch` failure task**: tool-failure handling still works, now inside
  the `tools` node (slide 5.3).
- The agent under construction is the one you already know — we reuse the **shared tools** from
  [`common/tools.py`](../../common/tools.py) (`calculator`, `lookup`, `flaky_fetch`), so the only
  new thing on screen is LangGraph itself.

## section 4. State and reducers (objective 3)

### slide 4.1 A node returns an update; a reducer merges it

- The trap is to think a node **sets** state. It does not — a node *returns an update* that
  LangGraph merges into state via a per-field **reducer**.
- For most fields (like `step`) the **default reducer overwrites** (last write wins). For
  `messages`, the **`add_messages` reducer appends**.
- Say it plainly: the node doesn't *set* the history, it *contributes* to it.

### slide 4.2 `add_messages` is what preserves the L07 invariant

- L07 made you *manually* keep every `tool_use` paired, in order, with its `tool_result`. Get it
  wrong and the model loses the thread — the single most common L07 bug.
- The `add_messages` reducer **appends**, so each assistant `tool_use` turn and the following
  `tool_result` turn accumulate in order **by construction**. The framework now *enforces* the rule
  L07 made you remember.
- diagram: the `messages` list growing across a run — `Human → AI(tool_use) → Tool(result) →
  AI(tool_use) → Tool(result) → AI(text)` — each arrow labeled "append".

### slide 4.3 Break the reducer on purpose (the L07 bug, reborn)

- Swap `Annotated[list, add_messages]` for a plain `list[BaseMessage]` (the **default overwrite**
  reducer) and the `agent` node's returned `{"messages": [response]}` **clobbers** the whole
  history each turn.
- What you observe: the prior `tool_use` turn vanishes before its `tool_result` can pair with it.
  The loop can't make progress, re-issues the same call, and — having no stop condition it can
  reach — **hits LangGraph's recursion limit** and raises `GraphRecursionError`. *The L07
  invariant bug, in graph form.*
- Restore `add_messages` and it works again. (You'll do exactly this break/restore in
  [L1205](L1205_lecture.ipynb) and the L1206 lab.)

### slide 4.4 What belongs in state — and what doesn't

- **In state:** data that *flows between nodes and must persist across the loop* — the `messages`,
  the `step` counter.
- **Not in state:** the **model client** and the **tool registry** — those are *dependencies*
  wired in at build time (constructed once, closed over by the nodes), not data that flows.
- Conflating the two is how a graph gets tangled. Keep the running agent's state to **messages plus
  one counter**; richer state is L13's (patterns) and L17's (context management) territory.

## section 5. What the framework gives you for free

### slide 5.1 Name each freebie against its L07 twin

- table: the scaffolding L07 made you write by hand, now supplied. That convenience *is* the value
  proposition — name each freebie against its hand-rolled twin so the trade is concrete, not magic.

| L07 made you write… | LangGraph supplies… |
| --- | --- |
| the `while` run-driver | the compiled graph's run loop |
| the `max_steps` cap | the **recursion limit** (`GraphRecursionError`) |
| a hand-emitted `TraceEvent` list | a **built-in execution trace** (section 6) |
| the `dispatch()` tool runner | the prebuilt **`ToolNode`** |

### slide 5.2 Hand-assemble first, then reveal the one-liner

- We build the graph with **explicit nodes and edges first** (sections 3–4), so the L07→graph
  mapping is visible. *Then* we reveal the prebuilt shortcuts as "the same thing, packaged."
- **Smallest step:** the prebuilt **`ToolNode`** drops straight into the hand-wired graph in place
  of a hand-written tools node — same graph, less code.
- **Whole-graph one-liner:** `from langchain.agents import create_agent` builds *this entire graph*
  — agent node, tool node, conditional edge, back-edge — in a single call. It reads as "the graph I
  just built, wrapped," not a black box. (`langgraph.prebuilt.create_react_agent` is the older,
  now-deprecated name for the same idea.)

```python
from langchain.agents import create_agent
app = create_agent("anthropic:claude-sonnet-4-6", tools)   # the whole shallow agent, one line
```

- That one-liner is also the lead-in to **L13**: it is the **ReAct** pattern — *a pattern over*
  these primitives, not a new mechanism (see [L1208](L1208_lecture.md)).

### slide 5.3 The step cap didn't go away — and tool errors still need handling

- A runaway graph still halts: LangGraph's **recursion limit** is the framework's `max_steps`.
  Hitting it is still a **signal worth investigating** (the L07 lesson), not noise.
- `ToolNode` does **not** swallow arbitrary tool failures by default — you opt in with
  `handle_tool_errors=True`, which turns any tool exception into a `ToolMessage(status="error")`.
  That is the L07 `dispatch()` "convert any exception into a `tool_result(is_error=True)`" behavior,
  now a constructor flag. The model still decides what to do next.

## section 6. Carry your eval set across, and tracing transfers

### slide 6.1 Bring the L09 eval set onto the rebuild

- The cleanest proof the rebuild is correct: run the **same L09 eval set** against the LangGraph
  agent and watch the same cases pass. *Same cases, different implementation, nothing regressed.*
- The graph returns a **state dict** (a `messages` list); the L09 scorers expect a `RunResult`
  (`final_text`, `trace`). A thin **adapter** maps one to the other so the *same* `EvalCase`s and
  scorers from [`common/evals.py`](../../common/evals.py) run unchanged.
- diagram: `graph.invoke(...) → {messages, step} → to_run_result() → RunResult → common/evals.py
  scorers → pass table`.

```python
def to_run_result(final_state) -> RunResult:
    """Map the graph's output into the shape common/evals.py scores."""
    msgs = final_state["messages"]
    trajectory = [c["name"] for m in msgs for c in getattr(m, "tool_calls", [])]
    final_text = next((m.text for m in reversed(msgs)
                       if isinstance(m, AIMessage) and not m.tool_calls), "")
    # ... build a RunResult whose .trace carries one 'tool' span per tool call ...
```

- This is L09's **"carry it forward"** rule cashing out one lesson later — make it a *visible* beat,
  not an afterthought.

### slide 6.2 Tracing transfers, too

- Attach the **Langfuse callback** (the same self-hosted instance from [L08](../L08/objectives.md))
  and the graph's run lands in the **same dashboard**, next to your hand-rolled L08 traces.
- You see the **same spans** you already know: a **GENERATION** for each model call, a **SPAN** for
  each tool call. The skill is portable — only the trace's *packaging* changed.
- One honest caveat: the framework's auto-trace is *shaped* by LangGraph, so span names and nesting
  differ slightly from your hand-rolled `TraceEvent`s. The **structure** (generation/tool, tokens,
  args) is the same — that recognition *is* the payoff.

## section 7. When to use which — and the failure mode

### slide 7.1 A graph is break-even for one loop, and earns its keep when flow branches

- For a *single* shallow loop, the graph is roughly break-even versus L07's plain Python — honestly,
  a bit more ceremony for the same behavior.
- It earns its keep when control flow **branches** (L13 patterns), or when you want the framework's
  **built-ins** — tracing, persistence/checkpointing, a prebuilt tool node, visualization.

### slide 7.2 The failure mode: reaching for a framework too early

- Name it out loud: **over-reaching for a framework on a 50-line problem** — the L07-objective-4
  mistake, restated. A graph you don't need is more setup, more concepts, harder to debug.
- The engineering skill is choosing the **simplest shape that solves the task**: a single function
  when one will do, the L07 loop when you want to *see* every moving part, a graph when the control
  flow or the built-ins justify it.

### slide 7.3 What you can do now

- **Model an agent as a graph** — name each of `agent` node, `tools` node, edge, conditional edge,
  state, reducer, entry point / `END`, and the L07 piece each replaces (objective 1).
- **Build a single-loop LangGraph agent** — assemble the `StateGraph`, wire the back-edge, compile,
  run it to behavioral equivalence with L07, and recognize the prebuilt one-liner (objective 2).
- **Reason about graph state** — messages-as-state, the `add_messages` reducer that preserves the
  L07 pairing invariant, and the state-vs-dependency boundary (objective 3).
- Next: **L13** surveys the *patterns* these primitives compose into — and frames `create_agent` as
  **ReAct, a pattern over what you just built**. See [L1208](L1208_lecture.md).
