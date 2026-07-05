# Cyclic graphs: the ReAct agent loop

```yaml
title: "Cyclic graphs: the ReAct agent loop"
keywords: ReAct agent, cyclic graph, StateGraph, back-edge, cycle, add_messages reducer, ToolNode, message history invariant, conditional edge, route, tools_condition, termination, recursion_limit, GraphRecursionError, token budget, loop detection, handle_tool_errors, ToolMessage, status error, create_agent, langgraph, langchain, claude
estimated duration: 75
```

> **Lesson:** L10. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L10/objectives.md).
> This is the written reference lecture — thorough on purpose, so a student who missed the verbal
> delivery can rebuild the lesson from the page. The runnable companion is the stub-model demo
> ([L1003_lecture.ipynb](L1003_lecture.ipynb)); the live multi-step run is
> ([L1006_lecture.ipynb](L1006_lecture.ipynb)); hands-on practice is the two L10 labs
> ([L1004](L1004_lab_empty.ipynb) build-the-graph + termination, [L1005](L1005_lab_empty.ipynb) tool
> failures). **Anchor model for the live demo: Claude Sonnet 4.6.**

## section 1. The lesson in one claim

### slide 1.1 An agent is a graph with a cycle

- The graphs you built in [L04](../L04/objectives.md)/[L05](../L05/objectives.md) flowed **forward
  and stopped** — a DAG, no node ever ran twice. *You* owned every edge.
- An **agent** takes those same primitives — typed state, nodes, a conditional edge — and adds
  exactly **one** new thing: a **back-edge** from the tool node to the model node. That edge hands
  the model the decision of what runs next.
- Said as a chant: **the back-edge is the cycle, and the cycle is the agent.** Everything in this
  lecture is a picture of that one edge — how it loops, when it *stops* looping, and what happens
  when a tool breaks mid-cycle.

### slide 1.2 Where L10 sits in the arc

- table: what each neighbouring lesson contributed, and what L10 adds on top.

| Lesson | What it built | What L10 reuses |
| --- | --- | --- |
| [L04](../L04/objectives.md) | a directed `StateGraph`: typed state, `add_node`, `add_edge`, `compile`, `invoke` | the same primitives — now with a cycle |
| [L05](../L05/objectives.md) | the **conditional edge**: `add_conditional_edges` + a routing function | `route` *is* an L05 conditional edge; termination is one of its branches |
| [L07](../L07/L0701_intro.md) | one tool-call round-trip; `.bind_tools()` + `.tool_calls` + `ToolMessage` | the exact interface, now repeated inside the cycle |
| [L08](../L08/objectives.md) | tool design; what a tool *returns* on failure | the error-as-data idea, now carried back by the graph |
| [L09](../L09/objectives.md) | tools packaged over MCP | the graph runs MCP tools and inline tools identically |
| **L10** | the ReAct **cyclic graph**: back-edge, termination, loop-level failure handling | — |
| L11 (next) | `create_agent` builds *this exact graph* in one line | the by-hand graph is the payoff that makes the one-liner legible |
| L12 (later) | tracing what the graph did — each node a span | the graph becomes the thing you instrument |

- The graph you wire here is **reused, not replaced**, by the lessons that follow. That is why it is
  worth building by hand once.

### slide 1.3 The three rules, up front

- This whole lecture lands three rules. Read them now; every section returns to one of them.
- **Rule 1 — the message-history invariant, maintained by the graph.** The `add_messages` reducer
  makes every node *append*; the prebuilt `ToolNode` answers each `.tool_calls` entry with a matching
  `ToolMessage`. (section 2)
- **Rule 2 — termination is a design decision, and it is a branch of `route`.** Natural termination
  is `route` returning `END`; `recursion_limit` is the built-in cap for everything else. (section 3)
- **Rule 3 — tool failures are messages, not exceptions.** `ToolNode(handle_tool_errors=True)`
  converts a raised exception into a `ToolMessage(status="error")` the back-edge hands back. (section 4)

[↑ Back to top](#cyclic-graphs-the-react-agent-loop)

## section 2. Building the graph node by node

### slide 2.1 The whole graph in one picture

- Before any Python, the entire agent fits in two nodes and two edges plus a conditional exit.
- diagram: `__start__ → agent`; a **conditional edge** out of `agent` (`route`: has `.tool_calls`?
  → `tools` : → `__end__`); the **back-edge** `tools → agent`. Label the `tools → agent` arrow **"the
  back-edge / the cycle."**

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

- text: read it as a sentence — *the `agent` node calls the model; `route` asks "any tool calls?";
  the `tools` node runs them; the back-edge loops to `agent`; and when there are no tool calls,
  `route` exits to `__end__`.* That is the model→tool→model loop, drawn.

### slide 2.2 The state: the `add_messages` reducer

- text: the agent's state is a `TypedDict` with one field — `messages: Annotated[list, add_messages]`.
- text: in L04, returning a state key **overwrote** it. The `add_messages` **reducer** changes that:
  each node's returned `messages` are **appended** to the running conversation, not substituted. That
  is *why* the conversation grows every turn — the `agent` node adds one `AIMessage`, the `tools`
  node adds one `ToolMessage` per call.
- text: `add_messages` also pairs messages by id, so the history stays well-formed as it accumulates.
  This reducer is **half** of Rule 1 — it is *how* the message-history invariant is maintained without
  hand-written bookkeeping.

### slide 2.3 The `agent` node

- text: the `agent` node is a plain function `state → {"messages": [reply]}`. Its body is one line
  you already know from L07: `model.bind_tools(tools).invoke(state["messages"])`.
- text: it returns the model's single `AIMessage` (possibly carrying `.tool_calls`) wrapped in the
  `messages` key, and the reducer appends it. The model is **not** aware of the graph — from its
  seat, every visit to the `agent` node is one independent round-trip. The loop lives in the edges.

### slide 2.4 The `tools` node = prebuilt `ToolNode`

- text: the `tools` node is LangGraph's prebuilt **`ToolNode(tools)`**. It reads the last message's
  `.tool_calls`, runs each requested tool, and appends **one `ToolMessage` per call** — the exact
  `.tool_calls` → run → append step you traced by hand in L07, once per call.
- text: this is the other **half of Rule 1**. After an `AIMessage` with `.tool_calls`, every call must
  be answered by a matching `ToolMessage` (paired by `tool_call_id`) before the next model call. In a
  hand loop that pairing is the #1 bug; `ToolNode` owns it. Teach *what the invariant is* so you can
  debug it — even though the prebuilt enforces it.
- diagram: two columns. Left "correct": `AIMessage[tool_calls #a, #b]` → `ToolMessage #a` →
  `ToolMessage #b`. Right "broken": `AIMessage[tool_calls #a, #b]` → `ToolMessage #a` with a red X
  and the caption "missing #b → API error". `ToolNode` always does the left column.
- text: `ToolNode` is **not magic** — open it up conceptually. It is the L07 dispatch step, prebuilt.
  The same `ToolNode` runs L09's MCP-exposed tools unchanged; only the tool objects differ.

### slide 2.5 The wiring: `route` (a conditional edge) + the back-edge

- text: two edges finish the graph. `route` is the L05 conditional edge — a function returning the
  name of the next node — and the back-edge is a plain `add_edge`.
- text: `route(state)` returns `"tools"` when the last message has `.tool_calls`, and `END`
  otherwise. Wire it with `add_conditional_edges("agent", route, {"tools": "tools", END: END})`, then
  `add_edge("tools", "agent")` — the **back-edge**. Set the entry point to `agent`, `compile()`, and
  `invoke(...)`.
- text: you write `route` by hand in L10. In L11 you will meet LangGraph's prebuilt
  **`tools_condition`** — the *same* "has tool calls? → tools : → end" function, packaged. Writing it
  by hand first is what makes the prebuilt land as "the thing I already wrote."
- text: watch the cycle turn with `graph.stream(task, stream_mode="updates")` — the same
  run-inspection call you have used since L03, now emitting one chunk per node:
  `{"agent": …}` → `{"tools": …}` → `{"agent": …}` … Name each time control crossed the back-edge.
  This stream is the L12 tracing on-ramp — the same run, routed to a structured tracer later.

[↑ Back to top](#cyclic-graphs-the-react-agent-loop)

## section 3. Termination: a branch of `route`

### slide 3.1 Termination is a design decision

- text: the model has no idea a graph exists. It will keep emitting tool calls as long as it thinks
  more of them help. **Nothing stops the cycle unless `route` says stop or a cap fires.**
- text: a cyclic graph with no cap is not "minimal" — it is a **runaway waiting to happen**. Even a
  toy agent gets a `recursion_limit`.
- text: there are four termination conditions worth naming. You will *rely on* the first two and
  *sketch* the other two as custom routing.

### slide 3.2 Four termination conditions

- table: the four conditions, when each fires, and how L10 handles it.

| Condition | Fires when | In L10 |
| --- | --- | --- |
| **Natural termination** | the `agent` node returns an `AIMessage` with **no `.tool_calls`**, so `route` returns `END`. The happy path — the only condition that means "the model thinks it's done." | rely on `route` |
| **Recursion limit** | the graph took more steps than `recursion_limit` allows and raises `GraphRecursionError`. Forces a halt even if the model still wants tools. Set it via `invoke(..., {"recursion_limit": N})`. | rely on the built-in |
| **Token budget** | cumulative input+output tokens (or cost) crosses a threshold. | sketch as custom routing |
| **Loop detection** | the model calls the *same tool with the same arguments* repeatedly without progress. Needs the call *history*, not just a counter. | sketch as custom routing |

- text: **natural** is the only condition that means "the answer is ready." Every other condition
  means "we stopped it" — a halt, not a completion.

### slide 3.3 `recursion_limit` is a safety net, not a correctness tool

- text: the cap bounds the damage when something goes wrong — a runaway model, a tool that always
  looks unfinished, a prompt that never converges. It does **not** make answers correct.
- text: **hitting the cap is always a signal worth investigating.** Either the task genuinely needs a
  higher cap, or the agent is misbehaving (fix the prompt, the tools, or the model). A
  `GraphRecursionError` is an alert, not noise.
- text: `recursion_limit` lives on `invoke`, not in the graph shape — the *same* compiled graph runs
  with any cap. It counts **super-steps** (node visits), so an agent that calls one tool per turn
  gets roughly two steps (`agent`, `tools`) per cycle.
- diagram: a runaway trace — cycles 1..3 each showing a `lookup(args=…)` with identical args, then
  step 7 boxed in red with "recursion_limit=6 exceeded → GraphRecursionError".

### slide 3.4 What to surface on a non-natural stop

- text: when the graph stops because the cap fired (not because the model finished), you decide what
  the caller sees. Two reasonable choices:
- text: **(a) let `GraphRecursionError` propagate** — loudest; good when a cap-hit is a true error
  your caller must handle. **(b) route to a "give the model one last chance to summarize" node** —
  friendliest output, costs one more call. Defend the choice against *who consumes the result* — a
  batch job wants (a); a chat UI may want (b).

### slide 3.5 Sketching the other two caps as custom routing

- text: the payoff of building `route` by hand: extra termination conditions are just **more branches
  of the conditional edge**. You don't need a new mechanism — you extend `route`.
- text: **token budget** — carry a running token sum in state (from `reply.usage_metadata`); `route`
  returns `END` when it crosses a threshold.
- text: **loop detection** — carry a short history of `(tool_name, json.dumps(args))` tuples in
  state; `route` returns `END` if the last *k* are identical. This catches "same call, again" that a
  step counter alone misses — and note it needs *arguments and progress*, not just call counts: a
  model calling the same tool three times with *different* args may be correctly exploring.
- text: this reinforces the section-1 framing — **in a graph, termination is just another routing
  decision** (the L05 skill, now pointed at `END`).

[↑ Back to top](#cyclic-graphs-the-react-agent-loop)

## section 4. Tool failures: messages, not exceptions

### slide 4.1 Two layers of failure handling

- text: L08 taught the **tool author** what to *return* when something goes wrong — the
  error-as-data pattern, e.g. returning `{"error": "row not found"}` from the tool itself.
- text: L10 teaches the **graph** what to do when the tool *can't even return* — it raised, or it
  returned the wrong shape. These are **different layers**, and the graph owns the second one.
- diagram: a stack — top box "tool author (L08): return errors as data" over a bottom box "graph
  (L10): `ToolNode` catches raises, sets `status='error'`" — with the model sitting above both.

### slide 4.2 Three failure modes at the graph level

- table: the three failure modes the graph must distinguish, and the default response to each.

| Failure mode | What it looks like | Default graph response |
| --- | --- | --- |
| **Tool raises an exception** | `network error`, `ZeroDivisionError`, an edge case the author missed — a Python traceback | `ToolNode(handle_tool_errors=True)` catches it and appends a `ToolMessage(status="error")` with a short message |
| **Tool returns a structured error** | a successful `ToolMessage` whose content says `{"error": "..."}` (the L08 pattern) | **no graph change** — it flows back through the back-edge as-is; the tool already did the right thing |
| **Tool output is malformed** | wrong type, unparseable, missing a field the model expected | it flows back too; decide where a minimum output-shape check belongs |

- text: the unifying move: **the failure becomes a `ToolMessage` and the back-edge hands it to the
  model.** The graph translates; it does not (by default) decide the recovery.

### slide 4.3 `handle_tool_errors=True` — one argument

- text: the whole exception-to-`ToolMessage` behavior is a single constructor argument:
  `ToolNode(tools, handle_tool_errors=True)`. A tool that raises inside the node becomes a
  `ToolMessage(status="error")` fed back through the back-edge, and the model decides what to do next.
- text: contrast `handle_tool_errors=False`: the exception **escapes the node and kills the whole
  `invoke`.** One buggy tool crashes the agent. Toggling this argument is the live beat of the failure
  demo — one word, crash vs. recover.
- text: a buggy tool now **degrades into a message** instead of crashing the agent. The model receives
  the error and can retry with corrected arguments, try a different tool, or apologise to the user —
  its call, not the graph's.

### slide 4.4 Don't dump tracebacks at the model

- text: feed the model a **short, descriptive** error string — `"connection reset by peer"`, not a
  40-line Python traceback.
- text: three reasons: tracebacks are **token-expensive**, they are **noise** the model can't act on,
  and they **leak** stack details (file paths, internals) you'd rather not expose. `ToolNode`'s
  default error text is already short — a class name plus a one-line message.

### slide 4.5 Retries are a decision, not a default

- text: `ToolNode` does **not** auto-retry. Surfacing the error to the model and letting it decide is
  the default — the model often knows whether a retry could possibly help.
- text: not all failures are alike. A `404 row not found` will *never* succeed on retry; a `503
  service unavailable` *might*. Blind retries waste tokens and can mask bugs — and an idempotency-
  violating tool (one that charges a card, sends an email) makes auto-retry actively dangerous.
- text: if you *do* want auto-retry, add it **deliberately**, with its own budget — never as a
  reflex. For L10, surface-and-let-the-model-decide is the stance.

[↑ Back to top](#cyclic-graphs-the-react-agent-loop)

## section 5. The graph *is* the loop; the prebuilt is one line

### slide 5.1 The graph didn't add behavior — it drew control flow as data

- text: put the hand-wired graph next to a bare `while` loop doing the same model→tool→model round.
  They are the **same skeleton**: the `agent` node is "call the model," the `tools` node is "run the
  tools," the conditional back-edge is "got tool calls? go again : stop."
- text: the graph form didn't change *what* happens — it drew the control flow as **data** (nodes and
  edges). That is exactly what makes it packageable (L11) and inspectable (L12).

### slide 5.2 What the graph buys over a bare `while` loop

- table: what you get for drawing the loop as a graph.

| The graph gives you | A bare `while` loop does not |
| --- | --- |
| a **routing seam** you can extend (add a `respond` node, an approval node) | control flow tangled in `if`/`break` |
| a prebuilt **`ToolNode`** that owns the message-history invariant | you write the `ToolMessage` pairing yourself (the #1 bug) |
| a structure **L11 can hand you prebuilt** (`create_agent`) | nothing to package |
| a structure **L12 can instrument node by node** (each node a span) | you thread logging through the loop by hand |

### slide 5.3 Common confusions to leave behind

- table: the misconception and the correction (each recurs in the labs).

| "I think..." | Actually |
| --- | --- |
| "a graph can't loop — L04/L05 were all forward" | a conditional edge can point *back*; the agent is a graph whose `route` sends control to an earlier node until the model stops asking |
| "the loop ends when the answer is right" | it ends when `route` returns `END` or `recursion_limit` fires; *correctness* is a downstream concern (L12 traces, L13 eval) |
| "`ToolNode` is magic / a black box" | it's the L07 `.tool_calls` → run → append-`ToolMessage` step, prebuilt — open it up so you can debug it |
| "I should retry every failed tool call" | usually not — a `404` is not a `503`; default to surfacing the error and letting the model decide |
| "the model needs my Python traceback" | it doesn't — a short error `ToolMessage` is better signal and cheaper |
| "my agent is broken because the model called the same tool 3×" | maybe — or it's correctly exploring; loop-detection needs *args + progress*, not just counts |

### slide 5.4 Three agent-loop gotchas, named

- text: the loop's failure modes were shown across the build — name them now as portable gotchas
  you'll hit the first time you hand-roll (or misuse) a loop. The first two are the axes this lecture
  stresses on purpose (*when does it stop?* and *what happens when a tool breaks?*); the third is the
  quiet one — nothing errors, the bill just climbs. (Distinct from slide 5.3's *misconceptions* — these
  are the mistakes, not the misreadings.)
- table: the three gotchas, the one-line cure, and where you saw it.

| Gotcha | Cure | Where you saw it |
| --- | --- | --- |
| **No termination guard (infinite loop)** — a cycle with no cap and no `END` branch runs forever on one confused turn | every agent gets an iteration cap on `invoke`; **hitting it is a signal to investigate** (hard task → raise it; misbehaving → fix prompt/tools/model), never noise to swallow | section 3 — `recursion_limit` caught the runaway; natural termination is `route` returning `END` |
| **Not handling tool failures** — a raised exception escapes `ToolNode` and crashes the whole `invoke` | `ToolNode(handle_tool_errors=True)` turns the raise into a `ToolMessage(status="error")` the back-edge hands back — and don't dump tracebacks at the model | section 4 (slides 4.2–4.3) |
| **Unbounded context growth** — `add_messages` **appends every turn**, so the history plus re-sent tool schemas inflate cost and drift toward the window limit | watch cumulative tokens across turns; trimming / summarizing the history is **L19** (context management, full course) — name it, don't build it here | slide 2.2 (the `add_messages` reducer) |

- text: the first two are crashes/runaways you can *see*; **#3 is silent** — the same
  no-memory / re-send cost from L01 and L07, now compounding once per loop iteration. And note the cap
  bounds the *number* of turns, not the *size* of each turn's history — a short run on a huge context
  still overflows. Different budgets.

### slide 5.5 The minimum-viable trace, and the bridge to L11 and L12

- text: by the end of L10 you can read the returned `messages` and narrate the run turn by turn —
  `agent`, `tools`, `agent`, `tools`, `agent` — and state the termination cause. That narration is a
  **minimum-viable trace**, and exactly what L12 replaces with something structured (each node a
  span). Keep your L10 graph accessible — you instrument *this exact graph* in L12.
- text: **bridge to L11** — the next lesson reveals `create_agent`, which builds *this exact graph* in
  one line: `MessagesState` is your `add_messages` state, its tool node is the same `ToolNode`, its
  routing is the prebuilt `tools_condition` you wrote by hand as `route`, and the back-edge is built
  in. Because you wired it yourself, the one-liner lands as "the thing I already built, packaged" —
  not a black box.
- text: one sentence to leave L10 with: *an agent is a cyclic graph around a stateless model — an
  `agent` node calls the model, `route` asks "any tool calls?", a `tools` node runs them, and a
  back-edge loops around — until `route` returns `END` or `recursion_limit` fires; and when a tool
  breaks, `ToolNode` turns the break into a message, not a crash.*

[↑ Back to top](#cyclic-graphs-the-react-agent-loop)
