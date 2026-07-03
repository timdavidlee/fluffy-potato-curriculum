# L14 Proctor Notes

Covers both L14 labs: **L1404** (build the shallow agent as a graph) and **L1406** (graph state and
reducers). Both run **fully offline** — a deterministic `StubChat` stands in for `ChatAnthropic` and
the **real** prebuilt `ToolNode` runs the **real** `common/tools.py` tools, so no API key is needed
and every run is reproducible. The focus is the **graph mental model and the message-history
reducer**, not model output. The lecture demos ([L1403](L1203_lecture.ipynb),
[L1405](L1205_lecture.ipynb), [L1407](L1207_lecture.ipynb)) use the real `ChatAnthropic` client where
they make live calls; the labs deliberately don't, so the wiring and state are the only variables.

> Keep repeating the lesson's spine: **it's the same model → tool → model loop from L10, now drawn as
> a graph.** The one new thing versus an L04 workflow is the **back-edge** `tools → agent`, which
> hands the model control of the path. If a student can't map a graph piece back to an L10 line,
> slow down and do the mapping out loud — that mapping *is* objective 1.

---

## L1204_lab problem 1 — The typed state

COMMON GOTCHAS:
- Forgetting the `add_messages` reducer — writing `messages: list[BaseMessage]` instead of
  `messages: Annotated[list[BaseMessage], add_messages]`. Without it the default reducer
  **overwrites**, the history gets clobbered, and the agent loops to the recursion cap. They'll see
  this break on purpose in L1406 — name the link now.
- Dropping the `step` field, or annotating `step` with a reducer it doesn't need (it should just
  overwrite — the default).
- `add_messages` import path: `from langgraph.graph.message import add_messages` (already in the
  given setup cell).

UNBLOCKERS: Point at the L1403/L1405 state schema — two fields, only `messages` is annotated. A
`TypedDict` is just a class with typed attributes.

TIME: 3–5 min. STRETCH: ask *why* messages must append and step may overwrite (the
`tool_use`/`tool_result` pairing invariant).

## L1204_lab problem 2 — The agent node and the router

COMMON GOTCHAS:
- Returning the **whole state** instead of a partial update. A node returns only the fields it
  changed — `{"messages": [response], "step": state["step"] + 1}` — and LangGraph merges it.
- Wrapping `response` in a bare `{"messages": response}` (not a list). It must be a list —
  `{"messages": [response]}` — because `add_messages` appends an iterable of messages.
- `route` checking the wrong thing. It inspects the **last** message and returns `"tools"` only when
  that message is an `AIMessage` **with** `tool_calls`; otherwise `END`. A common slip is returning
  the string `"END"` instead of the imported `END` sentinel.
- Forgetting `bind_tools` — calling `model.invoke(...)` without binding the tools first. With the
  stub it happens to still work (it ignores schemas), but it's wrong for a real client; correct it.

UNBLOCKERS: Have them say each line's L10 equivalent aloud: `agent_node` = "call the model",
`route` = "is there a tool_use?". The `tools` node is given (prebuilt `ToolNode`).

TIME: 6–10 min. STRETCH: ask what `handle_tool_errors=True` does (turns a tool exception into an
error `ToolMessage` — L10's `is_error`).

## L1204_lab problem 3 — Wire, compile, render

COMMON GOTCHAS:
- Omitting the **back-edge** `add_edge("tools", "agent")`. Without it the graph runs the tools once
  and stops — it's a workflow, not an agent. The diagram will show no cycle. This is *the* teaching
  moment: the back-edge is the whole lesson.
- Mismatched conditional-edge mapping: `add_conditional_edges("agent", route, {"tools": "tools",
  END: END})`. The dict maps each value `route` can return to a destination node; `END` maps to
  `END`.
- Forgetting `set_entry_point("agent")`, or never calling `compile()` and trying to `invoke` the
  builder.

UNBLOCKERS: The render needs no API key — if `draw_mermaid()` prints a graph with the `tools → agent`
arrow, the wiring is right. Compare it to the L1403 diagram.

TIME: 5–8 min. STRETCH: render `draw_mermaid_png()` for an image instead of the text.

## L1204_lab problem 4 — Run the agent

COMMON GOTCHAS:
- Forgetting `step` (or `messages`) in the initial state — `invoke` needs both keys present
  (`{"messages": [HumanMessage(TASK)], "step": 0}`). A missing `step` raises a `KeyError` inside
  `agent_node`.
- Reading the tool path wrong. The path is the tool **names** across the `AIMessage`s'
  `tool_calls` — expect `['calculator', 'lookup']`. If it's empty, the back-edge or `route` is
  wrong.
- `result["messages"][-1].text` — use the `.text` **property** (not `.text()` — that's deprecated).

UNBLOCKERS: If the run hits a recursion error, the reducer or the route is wrong — jump to the L1406
"break the reducer" framing. If the path is `['calculator']` only, the back-edge is missing.

TIME: 4–6 min. STRETCH: invoke on the crash task (`flaky_fetch https://crash`) and watch the error
`ToolMessage` flow back through the loop.

## L1204_lab problem 5 — What makes it an agent? (written)

COMMON GOTCHAS:
- Answering "the conditional edge" for Q1. Close, but the precise answer is the **back-edge**
  `tools → agent`: a conditional edge alone (as in L04) is still a workflow; the *cycle* is what
  makes the model drive the path.
- For Q2, missing that the node depends on the **interface** (`bind_tools(...).invoke(...)`), not the
  concrete client — which is exactly why swapping `StubChat` for `ChatAnthropic` is a one-line
  change.

UNBLOCKERS: Point back to L04's "the line between a workflow and an agent is a single back-edge."

TIME: 3–5 min. STRETCH: ask where the recursion limit (the framework's `max_steps`) would catch a
runaway.

---

## L1206_lab problem 1 — Define the state

COMMON GOTCHAS:
- Same as L1404 problem 1: forgetting `add_messages`. Here it matters even more — problem 3 *depends*
  on first having the correct reducer to contrast against the broken one.

UNBLOCKERS: The given `build_agent(state_cls)` helper takes the state class as an argument — they
only write the schema, not the graph.

TIME: 2–4 min.

## L1206_lab problem 2 — Watch the history grow

COMMON GOTCHAS:
- Iterating but not distinguishing message types — the cleanest read prints `type(m).__name__` and,
  for `AIMessage`, the tool names from `m.tool_calls`.
- Expecting a fixed *length* but getting confused by content. The history should be 6 messages:
  `Human → AI(calculator) → Tool → AI(lookup) → Tool → AI(text)`, with `steps: 3`.

UNBLOCKERS: If the length is wrong or it errors, the reducer from problem 1 is the cause — send them
back one cell.

TIME: 4–6 min. STRETCH: print `m.tool_calls` fully to see the args the (stub) model chose.

## L1206_lab problem 3 — Break it, then fix the reducer

COMMON GOTCHAS:
- Surprise that the **given** `BrokenState` cell raises `GraphRecursionError` — that's the point, and
  it's caught. Make sure students read *why*: the overwrite reducer clobbers history, the
  `tool_use`/`tool_result` pairing breaks, the loop never reaches `END`.
- For the fix, `FixedState` must be **identical** to `BrokenState` except the `messages` annotation
  (`Annotated[list[BaseMessage], add_messages]`). Students sometimes also change `step` or the task —
  keep the diff to the one line.
- The `recursion_limit` is passed as the second arg to `invoke` (`{"recursion_limit": 8}`); it's set
  low so the bug surfaces fast.

UNBLOCKERS: This is the single most important beat of the lab — the L10 invariant bug, reborn in
graph form. Have them state the connection out loud.

TIME: 5–8 min. STRETCH: lower `recursion_limit` to 2 and watch it trip even sooner; raise it and note
it still never terminates.

## L1206_lab problem 4 — State or dependency? (written)

COMMON GOTCHAS:
- Putting the **client** or the **tools** in state. They're dependencies wired in at build time
  (closed over by the nodes), not data that flows between nodes. This is the boundary that keeps a
  graph from getting tangled.
- Treating the API key as "state" — it's config/secret, loaded once via `common/config.py`.

UNBLOCKERS: The test is "does it *flow between nodes and change across the loop*?" Yes → state
(messages, step). No → dependency (client, tools, key).

TIME: 3–5 min. STRETCH: ask what *would* belong in state for a deeper agent (a plan, a scratchpad, a
todo list — the L18/L19 forward pointer).
