# L10: Teacher-led demos — Cyclic graphs: the ReAct agent loop

> Sibling docs: [objectives.md](objectives.md) (what the lesson aims for), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md).
>
> **Audience for this file:** the teacher running L10. Every demo below is *teacher-driven, no student participation*. Student-driven exercises live in the L10 labs (separate file).

## How to read this file

Each demo is a self-contained block with:

- **Goal** — the single insight the demo should land. Tied to a learning objective from [objectives.md](objectives.md).
- **Pre-flight** — what the teacher needs loaded before class.
- **Live script** — the order of operations during the demo. Treat it as a checklist, not a teleprompter.
- **What to highlight** — the moment(s) where the teacher should slow down and call out the takeaway out loud.
- **If the demo misbehaves** — graceful fallback for when the model surprises you (because it will).

The demos are ordered to match the four learning objectives from [objectives.md](objectives.md). Demo 1 wires the graph node by node; Demo 2 stresses termination; Demo 3 stresses failure handling; Demo 4 shows the graph *is* the loop and previews the prebuilt. They build on each other — Demos 2 and 3 deliberately reuse Demo 1's compiled graph so students see it stretched and broken, not replaced. Run them in order on first delivery.

## Pre-flight (once, at the top of the lesson)

The teacher should have, before the first demo starts:

- A working notebook with the project's LangChain chat-model setup (per the project's `uv` env), LangGraph imported (`from langgraph.graph import StateGraph, END`; `from langgraph.prebuilt import ToolNode`; `from langgraph.graph.message import add_messages`), and an L05 conditional-edge graph in scrollback as a warm-up reference. The agent is "that, but the edge points back."
- Two pre-defined inline LangChain tools reused across all demos:
  - `calculator(expression: str) -> str` — evaluates a small arithmetic expression. Cheap, deterministic.
  - `lookup(key: str) -> str` — returns a value from a tiny in-memory dict (e.g. city → population). A couple of keys present, a couple deliberately missing, so "key not found" is reachable.
- A third tool that will *fail on demand*, used only in Demo 3:
  - `flaky_fetch(url: str) -> str` — one tool keyed on the URL: `https://ok` returns a value, `https://error` returns a structured error, `https://crash` raises an exception, `https://garbage` returns malformed output. Keeps the demo prompt natural.
- A small `build_agent(model, tools, *, handle_tool_errors=True)` helper that the teacher will *write live* in Demo 1 (the agent node, the `route` function, the `StateGraph` wiring) and *reuse unchanged* through Demos 2 and 3. Keep a "completed" version in a sibling cell the teacher can paste if live-coding falls behind.
- A `draw` of the compiled graph (`graph.get_graph().draw_ascii()` or the Mermaid render) ready to project — the picture of agent → tools → agent is the demo's spine.
- **`graph.stream(task, stream_mode="updates")` — the same run-inspection call students have used since L03**, now watching the *loop* turn: each chunk is one node firing (`{"agent": {...}}`, then `{"tools": {...}}`, then `{"agent": {...}}`, …), so the cycle is legible turn by turn. Pair it with a tiny helper that pretty-prints each chunk's new message(s): role, `.tool_calls` (name + args), and `ToolMessage` content. This stream is the closest thing to a "trace" the lesson exposes; L12 routes this *same* run to a structured tracer. Foreshadow that.

> Why pre-defined tools: the lesson is about the *graph/cycle*, not about tool design. L08 already covered tool design. Re-litigating tool schemas mid-demo eats time and dilutes the message. Spend tool-design time only on `flaky_fetch` (Demo 3), where the failure modes *are* the point.

## Demo 1 — The agent graph, wired node by node (Objective 1)

**Goal:** build the ReAct agent as a `StateGraph` in front of the class. Land the framing from [objectives.md](objectives.md): *"an agent is a graph with a cycle."* Show the back-edge as the one new primitive over L03/L05.

**Pre-flight:**

- An empty cell for `build_agent(...)`.
- The `calculator` and `lookup` tools defined and importable.
- A starter task on the slide: *"What is the population of the city whose name is the answer to 17 squared minus 1?"* — chosen because it forces (1) a calculator call, then (2) a lookup using the calculator's result, then (3) a final assistant answer. Confirm the lookup table has an entry keyed to the calculator's result, or swap the puzzle; the point is two sequential tool calls plus a natural-termination model message.

**Live script:**

1. Draw the graph on the whiteboard before typing: three boxes — `agent`, `tools`, `END` — with a **conditional edge** out of `agent` (`route`: has `.tool_calls`? → `tools` : → `END`) and a plain **back-edge** `tools → agent`. Say out loud: "L03 gave us nodes and edges; L05 gave us the conditional edge; the only new thing is *this edge points backward*."
2. Live-code it:
   - The **state**: a `TypedDict` with `messages: Annotated[list, add_messages]`. Pause on `add_messages` — "this reducer *appends*; in L03 returning a key overwrote it. That's why the conversation grows every turn."
   - The **agent node**: `def agent_node(state): return {"messages": [model.bind_tools(tools).invoke(state["messages"])]}`.
   - The **route function**: return `"tools"` if the last message has `.tool_calls`, else `END`.
   - The **wiring**: `StateGraph(State)`, `add_node("agent", ...)`, `add_node("tools", ToolNode(tools))`, `set_entry_point("agent")`, `add_conditional_edges("agent", route, {"tools": "tools", END: END})`, `add_edge("tools", "agent")`, `compile()`. **Do not set a `recursion_limit` yet** — that's Demo 2's punchline.
3. Project the compiled graph's diagram. Point at the back-edge. "That is the agent."
4. `stream` the starter task (`stream_mode="updates"`) and walk the chunks with the pretty-printer: `{"agent": …}` (calculator call) → `{"tools": …}` → `{"agent": …}` (lookup call) → `{"tools": …}` → `{"agent": …}` (final text). Name each time control crossed the back-edge.

**What to highlight:**

- The **back-edge** is the whole idea. Remove it (make `tools` go to `END`) and you're back to an L03 pipeline that can't react to its tools.
- **`ToolNode` maintains the message-history invariant for you.** After an `AIMessage` with `.tool_calls`, every call must be answered by a matching `ToolMessage` (by `tool_call_id`) before the next model call. In a hand loop that's the #1 bug; the prebuilt node does it. Say what the invariant *is* so they can debug it later — don't let it stay hidden.
- The model is *not* aware of the graph. From its perspective every agent-node visit is one round-trip. The loop lives entirely in the edges.
- The same graph will run MCP-exposed tools from L09 unchanged — only the tool objects handed to `ToolNode` differ.

**If the demo misbehaves:**

- If live-coding falls behind, paste the prepared `build_agent` and walk it line by line. Don't sacrifice the `invoke` runs — the runs are where the cycle becomes concrete.
- If the model answers from prior knowledge without calling tools, tighten the system prompt (*"You may only answer using the tools provided"*) and rerun.
- If a reply carries both `.tool_calls` and final text, that's a real protocol nuance — `route` still sends it to `tools` (there are calls to answer); the text is interim narration.

## Demo 2 — Termination: `route` to `END`, and the recursion limit (Objective 2)

**Goal:** show natural termination, a `recursion_limit` rescue, and a runaway in the same demo. Land that *termination is a design decision* and *it's just a branch of the conditional edge.*

**Pre-flight:**

- Demo 1's compiled graph, unchanged.
- A "looping" task designed to provoke the model into calling the same tool repeatedly (e.g. asking it to "keep re-checking" a value via `lookup`, or a tool whose result is ambiguous so the model retries). Dry-run before class; behavior is model-dependent.
- A side-by-side panel ready: turn number on the left, tool-call args on the right, so "same call, again" lands visually.

**Live script:**

1. Re-run Demo 1's starter task. It terminates naturally in 2–3 turns. Read the cause out loud: *"`route` returned `END` — the last reply had empty `.tool_calls`."* Emphasize: that is the *only* condition meaning "the model thinks it's done."
2. Run the looping task with a generous `graph.invoke(task, {"recursion_limit": 25})`. Watch the model call the same tool 8+ times, then a `GraphRecursionError` fires. *"That's the graph's iteration cap — non-natural termination."*
3. Re-run the looping task with `{"recursion_limit": 6}`. It bails faster. Discuss: the cap caught the runaway; smaller caps cost less when things go wrong.
4. Sketch (don't fully implement) two more conditions as **custom routing** — reinforcing "termination is just another branch of `route`":
   - **Token budget:** carry a running token count in state; `route` returns `END` if over budget.
   - **Loop detection:** carry the last few `(tool_name, args)` tuples in state; `route` returns `END` if the last 3 are identical.

**What to highlight:**

- `recursion_limit` *is* the safety net, and it lives on `invoke`, not in the graph shape. Hitting it (a `GraphRecursionError`) is always a signal worth investigating — the task is too hard (raise the cap) or the agent is misbehaving (fix the prompt/tools/model).
- **Natural termination = `route` returns `END` because `.tool_calls` was empty.** Tie that phrase to the routing function students wrote in Demo 1. Termination isn't a separate mechanism; it's the `END` branch of an L05 conditional edge.
- A graph with no cap is not "minimal" — it's a runaway waiting to happen. Even a toy agent gets a `recursion_limit`.

**If the demo misbehaves:**

- If the model refuses to loop (gives up after a retry or two), force it with a tool whose result is deliberately unhelpful (`lookup` returning `"unknown — try again"`). The point is to show the cap *catching* something.
- If the natural-termination run hits the cap on the day, raise `recursion_limit` and rerun. Don't accidentally teach "natural termination is rare."

## Demo 3 — Tool failure as a message: `handle_tool_errors` (Objective 3)

**Goal:** show all three failure modes flowing back through the back-edge as `ToolMessage`s, and watch the model recover. Land that *the graph's job is mostly translating exceptions into well-formed messages.*

**Pre-flight:**

- Demo 1's graph, built once with `ToolNode(tools, handle_tool_errors=False)` and once with `handle_tool_errors=True` — the toggle is the live beat.
- The `flaky_fetch` tool with the four URL behaviors from pre-flight.
- A small task on the slide: *"Fetch the value at https://ok. Then try https://crash, then https://error, then give up gracefully."* — chosen so the model walks every failure mode in one run, with explicit recovery instructions so the demo doesn't depend on the model improvising.

**Live script:**

1. Run the task with `handle_tool_errors=False`. The call to `https://crash` raises inside `ToolNode`; the exception escapes and the graph `invoke` crashes. Walk the traceback. Punchline: *one buggy tool killed the whole agent.*
2. Rebuild the graph with `ToolNode(tools, handle_tool_errors=True)`. One argument.
3. Re-run the same task. Read the returned `messages` and watch the model:
   - `https://ok` → success → back-edge → continue.
   - `https://crash` → exception → `ToolNode` appends a `ToolMessage(status="error")` → back-edge → model sees the error, can't recover that URL, moves on.
   - `https://error` → tool *returns* a structured error result as its `ToolMessage` content — point out this case needed *no* graph change, because the tool followed the L08 "errors as data" pattern.
   - `https://garbage` → malformed output — show what the model does with it, and note where a minimum output-shape check could live.
   - final `AIMessage` (empty `.tool_calls`) acknowledging the failures — natural termination.
4. Quick aside — what *not* to do: a custom error handler that dumps the full traceback into the `ToolMessage`. Note token cost, irrelevance to the model, and the stack-trace leak.

**What to highlight:**

- `handle_tool_errors=True` is the default move: convert the raised exception into a `ToolMessage(status="error")` and let the **back-edge** hand it to the model, which is often the best component to decide retry vs. swap vs. give up.
- Graph-level and tool-level failure handling are *different layers*. L08 taught the tool author what to *return* on failure; L10 teaches the graph what to do when the tool *can't even return* (raises, malformed).
- Don't dump tracebacks at the model. A short descriptive error string is better signal and cheaper.
- Retries are a model-side decision here. `ToolNode` doesn't auto-retry. Auto-retry is a deliberate add — with a budget — and it will bite you on the first non-idempotent tool.

**If the demo misbehaves:**

- If the model gives up after the first failure instead of trying the next URL, strengthen the prompt's recovery instructions and rerun. The point is the graph *enabling* recovery.
- If `https://garbage` is handled gracefully, mention it and skip the malformed beat. Don't manufacture a failure that doesn't occur.

## Demo 4 — The graph *is* the loop; the prebuilt is one line (Objective 4)

**Goal:** show that the hand-wired graph and a bare `while` loop are the same skeleton, then preview that L11's `create_agent` builds this exact graph in a line. Land that *every framework students will see (L11, L18) is this graph, packaged.*

**Pre-flight:**

- Demo 1–3's `build_agent` graph (agent node + `ToolNode` + conditional back-edge, ~25 lines of wiring).
- A tiny plain-Python `while` loop doing the same model→tool→model round (pre-written) — the "before graphs" version, for contrast only.
- `create_agent` (or the prebuilt `create_react_agent`) pre-imported for a *look, don't teach* one-liner. **Do not teach the prebuilt's mechanics here — that's L11's job.** A 30-second "this one line builds the graph you just wired" is the whole beat.
- The starter task from Demo 1, runnable against all three.

**Live script:**

1. Put three things on one screen: the `while` loop, the hand-wired graph, and `agent = create_agent(model, tools)`. Map them: the loop body's "call model" = the agent node; "run tools" = the tool node; "more tool calls?" = the conditional back-edge.
2. Run the *same task* on the hand-wired graph and on `create_agent`. Same final answer, same tool-call sequence. Different amount of code typed.
3. Discuss what the graph form buys over the bare loop: a routing seam you can extend, a prebuilt `ToolNode` that owns the invariant, and a structure L11 can hand you prebuilt and L12 can instrument.
4. Foreshadow: L11 reveals `create_agent` as *this exact graph, packaged*; L12 instruments *this exact graph* node by node with structured traces; L18 nests it. The graph shape is the constant.

**What to highlight:**

- The graph didn't add behavior — it drew the control flow as data. That's what makes it packageable (L11) and inspectable (L12).
- Building it by hand first is *on purpose*: when L11 shows the one-liner, students see "the thing I already built," not a black box.

**If the demo misbehaves:**

- If `create_agent` / the prebuilt import flakes on the day, skip the live run and show the one line on the slide next to the wiring. The point is the shape match, not a live race.

## Common pitfalls coda — naming L10's three gotchas

**Shape note:** a short **"common pitfalls" coda**, not a new live demo — L10 already *shows* the first two (Demos 2–3) and *implies* the third (Demo 1). Its job is to **name** them as portable gotchas, restate the cure in a line, and pin each back to where the room saw it. Budget ~5 minutes as a recap slide. Follows the [L23 Demo 5](../L23/demos_or_activities.md#demo-5--the-three-composition-anti-patterns-objective-5) template, like the [L01 coda](../L01/demos_or_activities.md#common-pitfalls-coda--naming-l01s-four-gotchas). Per the cross-cutting gotcha effort, the infinite-loop case stays **shown-with-a-cap**, never actually hung — exactly how Demo 2 already runs it.

**Goal:** consolidate the loop demos into three named agent-loop gotchas a student will hit the first time they hand-roll (or misuse) a loop.

**Pre-flight:**

- Nothing new to load. One recap slide; Demo 2's turn-by-turn panel and Demo 3's error trace still on screen to point back at.

**Live script (recap — point back, don't re-run):**

1. **No termination guard (infinite loop).** ❌ A loop with no cap and no `END` branch — one confused model turn and it runs forever. Point back at Demo 2: `recursion_limit` caught the runaway, and natural termination is `route` returning `END` on empty `.tool_calls`. **Cure:** every agent gets an iteration cap on `invoke`; hitting it is a signal to investigate (hard task → raise it; misbehaving → fix prompt/tools/model), never noise to swallow.
2. **Not handling tool failures.** ❌ Letting a raised exception escape `ToolNode` and crash the whole `invoke` (Demo 3, `handle_tool_errors=False`). **Cure:** `handle_tool_errors=True` converts the exception to a `ToolMessage(status="error")` and the back-edge hands it to the model to decide retry / swap / give up — and don't dump tracebacks at the model (token cost + stack-trace leak).
3. **Unbounded context growth.** ❌ Forgetting that `add_messages` **appends every turn** (Demo 1) — the message list, plus the re-sent tool schemas (L07's "tokens twice over"), grow every loop, so a long run silently inflates cost and drifts toward the window limit. **Cure:** watch cumulative tokens across turns; trimming / summarizing the history is [L19](../L19/objectives.md) (context management, full course) — name it, don't build it here.

**What to highlight:**

- The first two are the loop's two failure axes L10 already stresses on purpose — *when does it stop?* (Demo 2) and *what happens when a tool breaks?* (Demo 3). The coda just gives them names.
- #3 is the quiet one: nothing errors, the bill just climbs. It's the same no-memory / re-send cost from [L01](../L01/objectives.md) and [L07](../L07/objectives.md), now compounding once per loop iteration.

**If a student pushes back:**

- "Doesn't `recursion_limit` also fix context growth?" No — the cap bounds the *number* of turns, not the *size* of each turn's history. A short run on a huge context still overflows. Different budgets (L01's space vs. count).

## Optional bridge demo — toward tracing (L12)

If time allows, run one final beat that previews L12: wrap the agent node so it appends a structured dict (`{"event": "model_call", "turn": i, "tool_calls": [...]}`) to a list on each visit. Show the list after a run. That's the simplest possible trace — one span per node.

Don't teach trace analysis here — that's L12. Just show the *shape* of what's coming, so students see the tracing lesson as a natural extension.

## Optional extension demos (stretch — only if the core four land with time to spare)

Both are **optional** and tied to the stretch extensions in [objectives.md](objectives.md). Each is a small addition to Demo 1's compiled graph — one node, one edge — reinforcing that the graph is a surface you extend. Skip either freely.

### Optional A — a dedicated `respond` node (self-contained)

**Goal:** show that the terminal branch of `route` can point at *another node*, not just `END` — a direct reuse of the L05 routing skill.

**Live script:**

1. Take Demo 1's graph. Add a tiny `respond` node that shapes the final answer (e.g. strips interim narration, or wraps the reply in a fixed `"Final answer: …"` format).
2. Re-point the routing map: `route` now returns `"respond"` instead of `END` when there are no tool calls; wire `add_conditional_edges("agent", route, {"tools": "tools", "respond": "respond"})` and `add_edge("respond", END)`.
3. Re-run Demo 1's task. Same tool-call sequence; the difference is the last hop — `agent → respond → END` — and a cleaned-up final message.

**What to highlight:** the cycle didn't change; you added a terminal node on the `END` branch. This is the same "structured final response" idea L11's `create_agent(response_format=...)` will formalize — you just wired it by hand.

### Optional B — a `human_approval` / `interrupt` node (a preview of L17)

**Goal:** show *where in the cycle* a human-approval pause goes, and *why an agent is the natural place to want one*. This is the course's first `interrupt` — frame it as a forward-reference, not a lesson.

**Pre-flight:** a checkpointer (`from langgraph.checkpoint.memory import MemorySaver`), the graph compiled with `checkpointer=MemorySaver()`, and a `thread_id` config. Keep this pre-written; do not derive it live.

**Live script:**

1. Insert a `human_approval` node **between the agent's tool request and the tool run** — i.e. `route` sends tool-call replies to `human_approval` first, which calls `interrupt(...)` to surface the proposed tool calls, then edges to `tools`.
2. `invoke` the graph; it **pauses** at `interrupt`. Show that the run halted with the proposed tool calls surfaced for a human.
3. Resume with `graph.invoke(Command(resume="approved"), config)` and watch it continue into `tools` and back around the cycle.

**What to highlight:**

- The pause lives exactly where you'd want a human in the loop: *after* the model proposes an action, *before* it executes. That placement is only possible because the agent is a graph you can splice a node into.
- **Say the boundary out loud:** "this needs a checkpointer and resume semantics — that's [L17](../L17/objectives.md)'s whole lesson. Today we're just seeing the *shape*." Do **not** teach thread IDs, checkpointer backends, or resume internals here.

**If the demo misbehaves:** if the checkpointer/resume flakes on the day, skip the live run and show the graph diagram with the `human_approval` node spliced in — the placement is the point, not a live pause.

> **Authoring note:** L17's roadmap is not yet written, so this is the course's first `interrupt` appearance. When L17 is authored it should back-reference this preview. Keep the two consistent.

## Pacing notes for the teacher

- **Per-demo time:** Demo 1 is the long one (15–25 minutes including the live wiring). Demos 2 and 3 are 10–15 minutes each. Demo 4 is 8–12 minutes. Total: 45–75 minutes for the four demos plus the optional bridge. Fits a 90-minute block with discussion.
- **Live-coding budget:** Demo 1's `build_agent` is the only place to live-code. Demos 2–4 reuse it with small changes (a `recursion_limit`, an `handle_tool_errors` toggle); do *not* re-wire the graph in each demo.
- **Variance budget:** the model's tool-call patterns are not deterministic. Budget at least one re-run per demo for tasks that depend on specific tool calls.
- **The audience watches, doesn't participate.** Resist asking "what should `route` return here?" — that's a lab pattern. Hands-on wiring is for the L10 labs.

## Open authoring questions

- <!-- *NEED INPUT*: which model class anchors the live demo notebook — the graph is model-agnostic but chaining depth varies. Course anchor is Sonnet 4.6; Haiku 4.5 chains more shallowly on the same task. -->
- <!-- *NEED INPUT*: should Demo 4 use `langchain.agents.create_agent` or `langgraph.prebuilt.create_react_agent` for the one-liner preview? Match whichever the (concurrently-rewritten) L11 shallow-agents lesson lands on, so the "you already built this" bridge stays exact. -->
- <!-- *NEED INPUT*: should Demo 3 use one of L09's MCP-exposed tools as the failing tool, to reinforce "the graph runs both kinds"? Adds setup overhead; reinforces the L09 framing. -->
- <!-- *NEED INPUT*: a pointer/link to where the demo prompts and the `flaky_fetch` tool live as code (a `demos/` subdir? inline in a notebook?) — not yet decided. -->
