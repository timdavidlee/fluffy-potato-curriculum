# L10 Proctor Notes

Notes for whoever runs the L10 labs. One section per problem, keyed by lab id and problem number.
Times are rough and assume a semi-technical student with basic Python who completed L01–L09.

> **Both L10 labs are OFFLINE — no API key needed.** They drive a *scripted stub model* (`FakeModel`),
> so the cycle, the `recursion_limit`, and tool-failure handling are fully deterministic and run the
> same way every time. The only **live** notebook in L10 is the [L1006](L1006_lecture.ipynb) demo
> (a real LangChain chat model, `ANTHROPIC_API_KEY` required) — that's a teacher demo, not a lab.
>
> **Why a stub model?** L10 is about GRAPH CONTROL FLOW (the model→tool→model cycle; termination; the
> cap; failure handling). Scripting the model is the cleanest way to exercise that offline and
> reproducibly — the same mocking stance as the project's tests. The `FakeModel` mimics a LangChain
> chat model (`.bind_tools()` then an awaited `.ainvoke()` → a scripted `AIMessage`), and the prebuilt
> `ToolNode` runs the *real* tools against those scripted calls, so the graph students wire is
> identical to the live version in L1006.
>
> **Async, as everywhere in the course:** the `agent` node is `async def` (it awaits
> `model.bind_tools(...).ainvoke(...)`), and runs are driven with `await graph.ainvoke(...)` /
> `async for ... in graph.astream(...)` from the cell. The "forgot to `await`" symptom is a printed
> coroutine object (or a LangGraph error about the sync path) instead of a state dict — see the K05
> prework for the why.
>
> **New in L10 vs. L04/L05: the back-edge.** Students have built forward-only graphs (L04 `StateGraph`,
> L05 conditional edge). The one new primitive is `add_edge("tools", "agent")` — the edge that loops
> back and makes the graph a **cycle**. If a student is shaky on the L05 conditional edge or the L07
> single tool round-trip, redirect there first; the agent is just a conditional edge that loops.
>
> **Two `add_messages` gotchas to pre-empt (they bite the whole cohort):**
> 1. The state's `messages` field **must** use `Annotated[list, add_messages]`. Without the reducer,
>    each node *overwrites* the list (L04 behavior) and the conversation never accumulates — the graph
>    breaks in confusing ways.
> 2. `add_messages` de-duplicates messages **by id**. That is why the L1004 runaway scripts *distinct*
>    `lookup` turns (`r0`, `r1`, …): repeating the *same* `AIMessage` object would be de-duped and the
>    loop would not actually run away. Call this out at P4.
>
> The labs map to the L10 objectives: **L1004** → wire the ReAct graph + reason about termination;
> **L1005** → handle tool failures at the graph level with `ToolNode(handle_tool_errors=...)`.

## L1004_lab problem 1 — Write `route` (the conditional edge)

- **Common gotchas:** checking a `stop_reason`/`response_metadata` string instead of `.tool_calls`
  (the lesson wants students to see that *no tool call* is the real signal); forgetting that a reply
  can carry text **and** tool calls at once — any tool call means "go to tools," regardless of the
  text; returning the string `"end"` instead of the imported `END` sentinel.
- **Unblockers:** "Look at `state["messages"][-1]`; if it's an `AIMessage` with `.tool_calls`, return
  `"tools"`, else return `END`." This *is* an L05 conditional-edge function — remind them they wrote
  one in L05.
- **Time:** ~5 min.
- **Key point:** termination is a **branch of `route`**, not a special mechanism. `END` is one of the
  two things `route` can return.

## L1004_lab problem 2 — Wire the graph: `build_agent`

- **Common gotchas:** **(the big one)** forgetting the **back-edge** `add_edge("tools", "agent")` — the
  graph then runs `agent → tools` once and stops, an L04 pipeline, not an agent. Other gotchas:
  returning the reply from `agent_node` as a bare `AIMessage` instead of `{"messages": [reply]}` (the
  node must return a state update dict); forgetting the `await` on `.ainvoke(...)` inside `agent_node`
  (the node then returns a coroutine, not an `AIMessage`); passing the tools dict/among nodes wrong —
  `ToolNode(TOOLS)` takes the *list*; forgetting `set_entry_point("agent")`; mismatched routing map
  keys (the dict must map `"tools" → "tools"` and `END → END`).
- **Unblockers:** walk the six wiring steps in the prompt in order. If stuck, point them at the L1003
  demo's `build_agent` cell — the structure is identical. The confirmation cell prints the nodes and
  checks `("tools", "agent")` is an edge; if the back-edge check is `False`, they dropped the
  `add_edge`.
- **Time:** ~15 min. This is the heart of the lab.
- **Key point:** the graph *is* the loop — two nodes, a conditional exit, and the back-edge. The
  cycle is the agent.

## L1004_lab problem 3 — Drive it: natural termination

- **Common gotchas:** passing `happy_script` directly to `build_agent` instead of wrapping it in
  `FakeModel(...)`; invoking with a bare string instead of `{"messages": [HumanMessage(...)]}`;
  expecting a different tool order (it's exactly `calculator` then `lookup`, then a text turn).
- **Unblockers:** "`graph = build_agent(FakeModel(happy_script))`, then
  `await graph.ainvoke({"messages": [HumanMessage(content=...)]})`." The asserts pin the tool sequence to
  `['calculator', 'lookup']` and the last message to a plain-text `AIMessage` (no tool calls).
- **Time:** ~5 min.
- **Key point:** natural termination = `route` returned `END` because the last reply had no tool
  calls. It's the only stop that means "the model thinks it's done."

## L1004_lab problem 4 — The `recursion_limit` catches a runaway

- **Common gotchas:** scripting a **single** repeated `tool_reply` object and being surprised the
  runaway *self-terminates* — that's the `add_messages` id de-dup gotcha; the runaway needs *distinct*
  turns (`r0`, `r1`, …), which is exactly why the prompt uses a comprehension. Passing `recursion_limit`
  as a positional arg instead of in the config dict (`ainvoke(state, {"recursion_limit": 6})`).
  Expecting the error to be a plain `RuntimeError` — it's a `GraphRecursionError` (from
  `langgraph.errors`).
- **Unblockers:** "Comprehension of ~8 distinct `lookup` turns; `await` an
  `ainvoke(state, {"recursion_limit": 6})` inside `try/except GraphRecursionError` → `raised = True`."
  The assert pins `raised`.
- **Time:** ~5 min.
- **Key point:** a cyclic graph with no cap is a runaway waiting to happen. Hitting the cap is an
  **alert** worth investigating, not normal operation.

## L1004_lab problem 5 — The message-history invariant (written)

- **Common gotchas:** naming only one of the two prebuilt pieces; confusing the reducer (state) with
  the node (`ToolNode`); answering "the model handles it" — it does not, the *graph* does.
- **Unblockers:** expected: after an `AIMessage` with two tool calls, both must be answered by a
  matching `ToolMessage` (paired by `tool_call_id`) appended before the next model call. The two
  pieces: the **`add_messages` reducer** (each node appends) and the prebuilt **`ToolNode`** (one
  `ToolMessage` per call). In a hand loop this pairing is the #1 bug.
- **Time:** ~4 min.

## L1005_lab problem 1 — `handle_tool_errors=False`: one bad tool crashes the agent

- **Common gotchas:** building the graph with the default (`handle_tool_errors=True`) and being
  confused when nothing crashes — the whole point is to pass `False` here; scripting a tool that
  *returns an error as data* (`https://error`) instead of one that **raises** (`https://crash`) — only
  a raise escapes; forgetting to wrap the crash script in `FakeModel`.
- **Unblockers:** "`build_agent(FakeModel(crash_script), handle_tool_errors=False)`, then `await` the
  `ainvoke` inside `try/except RuntimeError` and set `escaped = True`." The assert pins `escaped`.
- **Time:** ~7 min.
- **Key point:** with error handling off, one buggy tool kills the whole `ainvoke`. That's the
  motivation for the `True` case in Problem 2.

## L1005_lab problem 2 — `handle_tool_errors=True`: the crash becomes a message

- **Common gotchas:** the run still crashing means they left `handle_tool_errors=False` — check the
  `build_agent` call; expecting the error `ToolMessage` to have `status="success"` — a *raised*
  exception becomes `status="error"`; some students look for the error text to match exactly (it's
  `ToolNode`'s wrapper string, e.g. `"Error: RuntimeError(...)"` — they should check `status`, not
  content).
- **Unblockers:** "Same crash call, then a retry (`https://ok`), then a text reply;
  `handle_tool_errors=True`; assert there's a `ToolMessage` with `status == 'error'` and the last
  message is a plain-text `AIMessage`." The back-edge is what hands the error back to the model.
- **Time:** ~7 min.
- **Key point:** `ToolNode(handle_tool_errors=True)` turns a raise into a `ToolMessage(status="error")`
  the back-edge feeds the model — crash becomes recoverable, one argument.

## L1005_lab problem 3 — error-as-data needs no graph change

- **Common gotchas:** expecting `https://error` to *raise* or produce a `status="error"` message — it
  does neither; the call **succeeds** (`status="success"`) and the *content* is the error string
  (the L08 pattern). This is the key distinction from Problem 2 and the most common point of
  confusion — draw it out: *raise* → graph must catch it; *error-as-data* → nothing to catch, it
  just flows back.
- **Unblockers:** "Script `https://error` then `https://ok`; `handle_tool_errors=True`; the first
  `ToolMessage` has `status == 'success'` because no exception was raised." The assert pins that
  status.
- **Time:** ~6 min.
- **Key point:** L08's "errors as values" tools need **no** graph change — the graph only has to
  handle the tool that *can't even return*.

## L1005_lab problem 4 — Why not dump the traceback? (written)

- **Common gotchas:** "the model needs the full traceback to debug" — backwards; the traceback is
  noise for the model.
- **Unblockers:** expected (any two): tracebacks are **token-expensive**; they are **noise** the model
  can't act on (it can't read your stack frames); they **leak** internal details (file paths, library
  internals). A short class-name-plus-one-line message is the right amount of signal.
- **Time:** ~3 min.

## L1005_lab problem 5 — Should the graph auto-retry? (written)

- **Common gotchas:** "always retry, retries are free" — wrong on both counts.
- **Unblockers:** expected: not all failures are alike — a `404 not found` will never succeed on
  retry, a `503` might; blind retries waste tokens and can mask bugs; and an idempotency-violating tool
  (charges a card, sends an email) makes auto-retry actively dangerous. Default: surface the error to
  the model and let *it* decide; add auto-retry only deliberately, with its own budget.
- **Time:** ~3 min.
