# L10: Cyclic graphs — the ReAct agent loop

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (lesson-plan row L10).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).

## Where this lesson sits

By L10, students have built forward-only graphs: L04 wired a **directed graph** that runs nodes in sequence (`StateGraph`, `add_node`, `add_edge`, typed state, `compile`, `invoke`), and L05 added **conditional edges** (`add_conditional_edges` + a routing function) so a graph can branch. They have also seen the *mechanics* of tool calling (L07: `bind_tools`, `.tool_calls`, `ToolMessage`), the *design* of good tools (L08), and the *packaging* of tools as a portable contract via MCP (L09). What every graph so far has in common is that it flows **forward and stops** — a DAG, no node ever runs twice.

L10 adds the one primitive those graphs lacked: a **back-edge**. An agent is a graph with a cycle. The model proposes tool calls (the *reason/act* step), a tool node runs them (the *observe* step), and an edge loops **back to the model** so it can react to what it just saw — over and over until it stops asking for tools. That loop-shaped graph is the **ReAct agent**, and building it node by node is the whole lesson. Students assemble it from the exact `StateGraph` primitives they already know, plus the cycle, and learn to reason about the two non-obvious questions the cycle raises — *when does it stop?* and *what happens when a tool fails inside the loop?*

This is the first lesson where the student's graph **calls the model on its own, repeatedly**. Everything before was a single API call (L01–L08), a single tool round-trip (L07), or a forward pass through a graph (L04–L05). After this lesson the student has a working agent — small, built by hand from nodes and edges — that chains multiple tool calls toward a goal. L11 immediately follows by revealing that LangGraph's prebuilt `create_agent` packages this exact graph into one line; L12 then teaches how to *read* what that graph did via tracing (every node becomes a span).

## Prerequisites

Students arriving at L10 should already be able to:

- Build and run a directed `StateGraph`: define a typed state, `add_node`, wire nodes with `add_edge`, `compile()`, and `invoke(...)` it (L04).
- Add a **conditional edge**: write a routing function that inspects state and returns the name of the next node, and wire it with `add_conditional_edges(source, route, {...})` (L05).
- Wire a single tool to a model call and trace one tool-call round-trip end-to-end (L07). Concretely: bind a typed tool to the model, send the request, detect that the reply's `.tool_calls` is non-empty, execute the tool, and append a matching `ToolMessage` back to the message list.
- Decide when a tool is needed vs. model-alone, name and schema-design a tool, and decide what a tool should *return* on failure at the *tool* level (L08).
- Recognize that an MCP-exposed tool and an inline Python tool present the same `.tool_calls`/`ToolMessage` shape to a graph, even though their packaging differs (L09).

If a student is shaky on the L05 conditional edge or the L07 single round-trip in particular, redirect to those labs before continuing — L10 assumes both are muscle memory; the agent is just a conditional edge that loops back on itself.

## Learning objectives

By the end of L10, a student should be able to:

1. **Build a ReAct agent as a cyclic `StateGraph`, node by node.** Concretely:
   - Define an agent state whose `messages` field uses the `add_messages` reducer, so each node *appends* to the running conversation instead of overwriting it (this is why the graph accumulates history — contrast with the plain overwrite state from L04).
   - Write the **agent node**: a function that binds the tools to the model (`model.bind_tools(...)`), calls `.invoke(state["messages"])`, and returns `{"messages": [reply]}` (one `AIMessage`, possibly carrying `.tool_calls`).
   - Add the **tool node** using LangGraph's prebuilt `ToolNode(tools)`, which reads the last message's `.tool_calls`, runs each tool, and appends one `ToolMessage` per call — the message-history bookkeeping you would otherwise do by hand.
   - Wire the **cycle**: `add_conditional_edges("agent", route, {"tools": "tools", END: END})`, where `route` returns `"tools"` when the last message has `.tool_calls` and `END` otherwise, and `add_edge("tools", "agent")` — the **back-edge** that makes it a loop. Set the entry point to `agent`, `compile()`, and `invoke(...)`.
   - Run the compiled graph on a small concrete task (e.g. "use the calculator and the lookup tool to answer X") and **watch the loop turn** with `graph.stream(stream_mode="updates")` — the same run-inspection call students have used since L03 (L04 for a sequence, L05 for a branch), now emitting one chunk per node: agent → tools → agent → tools → agent (final text). Name where the cycle turned; contrast with `invoke()`, which hands back only the final `messages`. This stream is the L12 tracing on-ramp — the same run, routed to a structured tracer later.

2. **Reason about termination in a cyclic graph.** Concretely:
   - Name at least four termination conditions and explain when each fires:
     - **Natural termination** — the agent node returns an `AIMessage` with empty `.tool_calls`, so `route` returns `END`. This is the "happy path" and the *only* condition that means the model thinks it's done.
     - **Recursion limit** — the graph took more steps than `recursion_limit` allows and raises `GraphRecursionError`. This is the graph's version of an iteration cap; it forces a halt even if the model still wants tools. Show setting it via `invoke(..., {"recursion_limit": N})`.
     - **Token budget** — cumulative input+output tokens (or cost) exceed a threshold; sketch adding it as a counter in state that `route` checks.
     - **Loop detection** — the model calls the same tool with the same arguments repeatedly without progress; sketch catching it by keeping recent `(tool_name, args)` tuples in state and having `route` bail to `END`.
   - Rely on the built-in `recursion_limit` and natural termination in code; sketch how token-budget and loop-detection would be added as **custom routing on the conditional edge** — reinforcing that in a graph, *termination is just another routing decision* (the L05 skill, now pointed at `END`).
   - Decide what the graph should surface when it terminates *non-naturally* (let `GraphRecursionError` propagate, or route to a "give the model one last chance to summarize" node). Defend the choice against a downstream consumer's needs.

3. **Handle tool failures inside the loop.** Concretely:
   - Distinguish three failure modes at the *graph* level (not the tool-design level from L08):
     - **The tool raises a Python exception** during execution (network error, division by zero, an unhandled edge case).
     - **The tool returns a structured error result** — a `ToolMessage` whose content describes a failure (e.g. `{"error": "row not found"}`). This is the L08-recommended pattern; the graph must still carry it back to the agent node.
     - **The tool's output is malformed** — the wrong shape, an unparseable string, missing fields the model expected.
   - For each, decide: does the graph convert it into an error `ToolMessage` and loop back so the model can recover, halt, or retry? Show that `ToolNode(handle_tool_errors=True)` does the default move for you — it catches a raised exception and appends a `ToolMessage(..., status="error")` so the back-edge feeds the model a message, not a crash. Contrast with `handle_tool_errors=False`, where the exception escapes and kills the graph.
   - Explain that the structured-error case needs *no* graph changes (the tool followed the L08 pattern; the `ToolMessage` just flows back), and decide where a minimum output-shape check belongs.

4. **See that the graph *is* the loop — and know why you built it by hand before reaching for the prebuilt.** Concretely:
   - Trace the compiled graph against the plain model→tool→model loop and see they are the same skeleton: the agent node is "call the model," the tool node is "run the tools," the conditional back-edge is "got tool calls? go again : stop." The graph didn't add behavior; it drew the control flow as data.
   - Name what the graph form buys you that a bare `while` loop does not: a routing seam you can extend (L05-style), a prebuilt `ToolNode` that owns the message-history invariant, and — critically — a structure L11 can hand you prebuilt and L12 can instrument node by node.
   - Recognize that L11 (shallow agents) reveals `create_agent`, which builds *this exact graph* in one line, and L18 (deep agents) nests it — the graph shape is the constant; the amount you type shrinks.

## Optional extensions (stretch — only if the core four land first)

These are **optional** and clearly marked as such in the materials. Neither is assessed; both exist to show that *the graph is a surface you extend by adding a node and re-pointing an edge* — the payoff of having built it by hand. Skip either without breaking the lesson.

- **A dedicated `respond` node (self-contained; uses only primitives students already have).** Instead of the `END` branch of `route` returning the raw final `AIMessage`, point it at a small `respond` node that shapes the user-facing answer (e.g. strips interim narration, or coerces the reply into a fixed format), then edges to `END`. Concretely: `add_conditional_edges("agent", route, {"tools": "tools", "respond": "respond"})` and `add_edge("respond", END)`. The teaching point is that **the terminal branch of a conditional edge can point at another node, not just `END`** — a direct reuse of the L05 routing skill, and a first taste of the "structured final response" idea L11's `create_agent(response_format=...)` will formalize. Keep it tiny: one node, one extra edge.

- **An optional `human_approval` / `interrupt` node (a *preview* of L17, not L10's to own).** Insert a node on the path to `tools` that **pauses the graph** so a human can approve or edit the model's proposed tool calls before they run — the classic approval gate. This is where `interrupt()` first appears in the course, so it must be framed as a forward-reference: it requires LangGraph's `interrupt` plus a **checkpointer** (`MemorySaver`) and resuming with `Command(resume=...)`, and **L17 ("Human-in-the-loop and approval gates") teaches it properly.** In L10, keep it to a single minimal runnable example that shows *where in the cycle the pause goes* (between "the model asked for tools" and "the tools run") and *why an agent is the natural place to want one* — then explicitly defer the mechanics (checkpointers, thread IDs, resume semantics) to L17. Do **not** let this extension grow into a checkpointer lesson.
  - Authoring note: because L17's roadmap is not yet written, this preview is the course's first `interrupt` mention. When L17 is authored, it should back-reference this L10 extension ("you saw the shape in L10; here is the full mechanism"). Flag the dependency so the two stay consistent.

## Main points the lecture should land

- **An agent is a graph with a cycle.** L04 and L05 graphs flow forward and stop; the agent adds a single **back-edge** from the tool node to the agent node. That one edge is the entire difference between "a pipeline" and "an agent." Everything else — nodes, typed state, conditional routing — students already have.
- **`route` is a conditional edge, and termination is one of its branches.** The routing function from L05 is exactly what decides "loop again (`"tools"`) or stop (`END`)." Framing termination as *a branch of a conditional edge* (not a special mechanism) is the payoff of teaching L05 first.
- **The `add_messages` reducer is why the loop accumulates.** In L04, returning a state key overwrote it. The agent's `messages` field uses the `add_messages` reducer so every node *appends* — the agent node adds one `AIMessage`, the tool node adds one `ToolMessage` per call, and the conversation grows each turn. This reducer is *how* the message-history invariant is maintained without hand-written bookkeeping.
- **`ToolNode` owns the message-history invariant.** After an assistant `AIMessage` with `.tool_calls`, every entry must be answered by a matching `ToolMessage` (paired by `tool_call_id`) before the next model call. In a hand loop you write that pairing yourself and it's the #1 bug; the prebuilt `ToolNode` does it for you. Teach *what the invariant is* (so students can debug it) even though `ToolNode` enforces it.
- **Termination is a design decision, not a default.** The model will happily call tools forever. `recursion_limit` is the graph's built-in safety cap; hitting it (a `GraphRecursionError`) always means something went wrong worth investigating. Real agents add token/time caps on top, as custom routing.
- **Tool failures are messages, not exceptions.** `ToolNode(handle_tool_errors=True)` converts a raised exception into a `ToolMessage(status="error")` that the back-edge hands back to the model — which is often the best component to decide whether to retry, swap tools, or give up. The graph's job is mostly to translate exceptions into well-formed messages, not to make the recovery decision.
- **The same graph runs MCP tools and inline tools.** From the graph's perspective a tool is a name + schema + function. Whether it dispatches over MCP (L09) or runs in-process is invisible — `ToolNode` only ever sees a `.tool_calls` entry to run and a `ToolMessage` to append.
- **Streaming and parallelism are out of scope.** The graph in L10 is invoked synchronously and non-streaming. `ToolNode` may run multiple `.tool_calls` from one reply, but parallel *execution* (async) and streaming are deferred. Get the simple cycle right first.

## Common student confusions to watch for

- *"A graph can't loop — L04/L05 were all forward."* It can, and that's the new idea: a conditional edge can point back to an earlier node. The agent is a graph whose `route` sends control back to the agent node until the model stops asking for tools.
- *"The loop ends when the answer is right."* No — it ends when `route` returns `END` (the reply had no `.tool_calls`) or `recursion_limit` fires. Whether the answer is "right" is a downstream concern (eval, L12 traces, human review).
- *"`ToolNode` is magic / a black box."* It isn't — it does exactly the `.tool_calls` → run → append-`ToolMessage` step students traced by hand in L07, once per call. Open it up conceptually so they know what it's doing.
- *"I should retry every failed tool call."* Sometimes; often not. A `404 row not found` is not a `503 service unavailable`. Blind retries waste tokens. Default to surfacing the error `ToolMessage` to the model via the back-edge and letting it decide.
- *"The model needs to see my Python traceback."* It doesn't. `handle_tool_errors=True` gives it a short error string; a full traceback is noise for the model and a stack-detail leak.
- *"My agent is broken because the model called the same tool three times."* Maybe — or maybe it's correctly exploring. Loop-detection has to look at *arguments and progress*, not just count turns; that's custom routing, not the default `recursion_limit`.

## Bridge to L11

L11 (shallow agents in LangGraph) is the immediate next step, and it reveals the prebuilt: `create_agent` builds *the exact graph students wired by hand here* in a single call, and the prebuilt `ToolNode` they used is the same one it wraps. Because L10 built the agent/tools/back-edge explicitly, L11's "here's the one-liner" lands as "the thing you already built, packaged" — not a black box. Keep L10 building the graph by hand **on purpose**, so the prebuilt reveal in L11 is a payoff, not a leap.

## Bridge to L12

L12 (what an agent generates: state, logs, traces & extracts) turns to tracing: reading what an agent did, locating failures from a trace alone, comparing traces across runs. The cyclic graph built in L10 is the natural subject — every node is an obvious place to instrument (each agent-node model call, each tool-node run, each routing decision becomes a span), and a raw compiled graph has no built-in observability yet. L12 starts by wrapping *this exact graph* with structured traces and grows from there. Encourage students to keep their L10 graph accessible; they'll instrument it in L12.

A small concrete handoff: at the end of L10, students should be able to read the returned `messages` list and narrate the run turn by turn — agent, tools, agent, tools, agent — and state the termination cause. That turn-by-turn narration is a minimum-viable trace and exactly what L12 replaces with something structured.

## Authoring decisions (resolved)

- **The graph shape is fixed and matches L11's vocabulary** so the by-hand→prebuilt bridge is exact: typed state with `messages: Annotated[list, add_messages]`; an `agent` node calling a `bind_tools`-bound model; a `tools` node = `ToolNode(tools, handle_tool_errors=True)`; `add_conditional_edges("agent", route, {"tools": "tools", END: END})`; `add_edge("tools", "agent")` back-edge; entry point `agent`.
- **Labs stay offline and deterministic.** The agent node drives the course's scripted `FakeModel` (from `common/fake_model.py`), which already mimics a LangChain chat model (`bind_tools` → `invoke` → scripted `AIMessage.tool_calls`); it drops straight into an agent node. `ToolNode` runs real inline LangChain tools. A restart-and-run-all needs no API key for the lab notebooks; the one live demo notebook reads the key through `common/config.py`.
- **Termination in code uses `recursion_limit`** (the built-in) plus natural termination via `route`; token-budget and loop-detection are *sketched* as custom routing, not implemented in full.
- **Parallel tool calls** are in scope only at the "`ToolNode` runs all of them" level; async parallel execution and streaming are out of scope.
- **`common/agent_loop.py` (the plain-Python instrumented loop) is not what L10 teaches anymore** — L10 builds the graph inline. That module remains the instrumented reference used downstream (L12/L13); L10's canonical artifact is now the compiled `StateGraph` in its notebooks.
