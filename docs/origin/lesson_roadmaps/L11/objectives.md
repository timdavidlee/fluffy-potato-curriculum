# L11: Shallow agents in LangGraph

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (lesson-plan row L11).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).
> Preceding lesson (mini cut): [L09 Evaluation — first pass](../L09/objectives.md). In the full plan, L10 (Choosing model power) sits between L09 and L11; its roadmap is not yet written. Following lesson: L12 LangGraph design patterns (roadmap not yet written).

## Where this lesson sits

This is the lesson the whole first arc has been building toward. Students have hand-built an agent from nothing: a single tool round-trip (L04), good tool design (L05), and then the **model → tool → model loop** in plain Python (L07) — `agent_loop.run(...)` returning a `RunResult(final_text, iterations, termination)`. They then learned to *observe* that loop with a structured trace (L08) and to *judge* it with a minimal eval set (L09). L07's Demo 4 explicitly previewed this moment: the same task run on the hand-rolled loop *and* on a minimal framework version, with the punchline that **"every framework you will see is a fancier version of the loop you wrote."** L08 reinforced it — built-in observability is one of the named reasons a team reaches for a framework.

L11 cashes that in. Students rebuild the *same agent they already understand* as a **LangGraph graph**. The pedagogical bet is that introducing a framework only *after* students have hand-rolled the loop means the framework reads as a set of conveniences over a familiar skeleton, not as magic. The control flow does not change — it is still model → tool → model until termination. What changes is the *shape*: an explicit loop becomes an explicit **graph** of nodes and edges over a shared **state** object, and LangGraph supplies the runtime that drives it.

The title word **"shallow"** is load-bearing and should be defined early: a *shallow* agent is a single tool-calling loop — one model, one set of tools, one decision point that either calls a tool or finishes. It is exactly the L07 loop, now expressed as a graph. This is contrasted with *deep* agents (planning, persistent memory, sub-todos, reflection) which the full plan covers later (L14) — named here only as "what we are **not** building yet." L12 immediately follows by surveying the *patterns* you can build once you think in graphs (ReAct, plan-and-execute, supervisor, …); L11's job is to make the graph mental model and the single-loop mechanics solid first.

## Prerequisites

Students arriving at L11 should already be able to:

- Build and run a model→tool→model loop in plain Python, maintain the message-history invariant (every `tool_use` answered by a matching `tool_result`), and read a `RunResult` (L07, objectives 1–2). L11 maps each of these pieces onto a graph node — a student who hasn't internalized the loop can't see what the graph is replacing.
- Reason about termination as a *design decision* — natural vs. `max_steps`, plus token-budget and loop-detection as extensions (L07, objective 2). In LangGraph this becomes a **conditional edge** that routes back to the model or to the end.
- Handle loop-level tool failures by converting them into `tool_result`s with `is_error: true` (L07, objective 3) — the same handling lives inside the tool node.
- Emit and read a **structured trace** of a run, and locate a failure from it (L08). LangGraph produces its own execution trace; L11 connects "the graph's trace" back to "the hand-rolled trace you already know how to read."
- Build and run a **minimal eval set** against an agent and flag regressions (L09). L11's strongest reinforcement of L09's "carry it forward" rule is running the *same eval set* against the LangGraph rebuild.
- Use the project's `potato_llm` seam and config for model calls (L02 onward). Note that LangGraph introduces its own model-client abstraction (a LangChain chat model); reconciling that with the project's seam is an explicit design question below.

If a student is shaky on the L07 loop, redirect there first — L11 is a *re-expression* of that loop, and the whole lesson lands only if the original is solid.

## Learning objectives

By the end of L11, a student should be able to:

1. **Model an agent as a graph.** Concretely:
   - Translate the L07 loop into the graph vocabulary and use the terms verbatim: a **node** (a unit of work — e.g. "call the model", "run the tools"), an **edge** (a fixed transition from one node to the next), a **conditional edge** (a transition chosen at runtime by a routing function — e.g. "did the model ask for a tool? → tool node, else → end"), the **state** (the shared object every node reads and writes), and the **entry point** / **END** (where the graph starts and stops).
   - Draw the shallow-agent graph and explain it: an `agent` (model-call) node, a `tools` node, an edge from `tools` back to `agent`, and a conditional edge out of `agent` that routes either to `tools` (the model emitted a `tool_use`) or to `END` (natural termination). Point at each piece and name the L07 equivalent it replaces.
   - Articulate *why a graph at all*: a loop encodes control flow implicitly in Python statements; a graph makes control flow **data** — nodes and edges you can inspect, visualize, reroute, and (later) extend with branches the plain loop couldn't express cleanly. State plainly that for a *single* loop the graph is roughly break-even; its payoff shows up when the control flow stops being a single loop (the motivation for L12).

2. **Build a single-loop LangGraph agent.** Concretely:
   - Use LangGraph's builder to assemble the graph: define the state schema, add the `agent` and `tools` nodes, set the entry point, wire the conditional edge with a routing function, wire the `tools → agent` edge, and compile the graph into something runnable.
   - Implement the two nodes: the `agent` node calls the model with the current messages and tool schemas and appends the response to state; the `tools` node executes every requested `tool_use` and appends matching `tool_result`s — *the same message-history invariant from L07*, now localized to one node. Reuse the L07/L08 tools (`calculator`, `lookup`, `flaky_fetch`) so the agent under construction is one students already know.
   - Run the compiled graph on the L07 chaining task and watch it issue the same tool sequence and terminate naturally — demonstrating behavioral equivalence to the hand-rolled loop. Then run it on the `flaky_fetch` failure task and confirm tool-failure handling still works inside the tool node.
   - Recognize what LangGraph *gives* you for free that L07 made you write by hand: the run loop / recursion driver, a built-in execution trace, a recursion/step limit (the framework's analogue of L07's `max_steps` cap), and prebuilt helpers (e.g. a ready-made tool node). Name each against the L07 hand-rolled equivalent it replaces. <!-- *NEED INPUT*: decide how much to lean on LangGraph prebuilts (e.g. `create_react_agent` / a prebuilt ToolNode) vs. hand-assembling nodes with `StateGraph`. Recommendation: hand-assemble `StateGraph` with explicit nodes/edges first so the L07→graph mapping is visible, then *show* the prebuilt one-liner as "the same thing, packaged" — mirroring L07's hand-rolled-then-framework arc. -->

3. **Reason about graph state.** Concretely:
   - Explain that the **state** is the single object threaded through every node — for a shallow agent it is essentially the running **message history** (plus optional extras like a step counter or token tally), the same list L07 mutated in place, now a typed, framework-managed value.
   - Understand **how nodes update state**: a node returns an update that LangGraph merges into the state via per-field **reducers** — most importantly that the `messages` field *appends* rather than *overwrites* (the add-messages reducer). Connect this directly to the L07 invariant: the reducer is what guarantees each `tool_use` and its `tool_result` accumulate in order instead of clobbering each other. State why getting the reducer wrong reproduces the single most common L07 bug, now in graph form.
   - Define the state schema with the project's typed style (a `TypedDict` / annotated state), so students see graph state as *typed data*, not a loose dict — consistent with the repo's pyright-strict conventions.
   - Distinguish **what belongs in state** (data that flows between nodes and must persist across the loop — messages, counters) from **what doesn't** (the model client, the tool registry — dependencies, not state). Getting this boundary right is the difference between a clean graph and a tangled one. <!-- *NEED INPUT*: how far to go on state beyond messages — keep L11 to "state == messages (+ maybe a counter)", or also introduce a custom state field to make the typed-state point vivid? Recommendation: keep the running agent's state to messages plus one counter, and use the counter purely to make reducers/typing concrete; richer state belongs to L12+ patterns and L15 context management. -->

## What a LangGraph agent is (vocabulary the lecture must establish)

Define these explicitly and reuse them verbatim through the labs and into L12:

- **Graph** — the agent expressed as nodes connected by edges, compiled into a runnable. The framework's replacement for L07's `while` loop.
- **Node** — a unit of work that reads state and returns a state update. Here: the `agent` (model-call) node and the `tools` node.
- **Edge** — a fixed transition between nodes (e.g. `tools → agent`).
- **Conditional edge** — a runtime-chosen transition: a routing function inspects state and returns the next node's name (e.g. `agent → tools` if a `tool_use` is present, else `agent → END`). This is L07's "is there a `tool_use`?" branch, lifted out of Python control flow into the graph.
- **State** — the shared, typed object passed through every node; for a shallow agent, the message history (plus optional counters).
- **Reducer** — the rule that merges a node's returned update into state per field; the add-messages reducer *appends* to `messages`, preserving the L07 ordering invariant.
- **Entry point / END** — where execution starts and the sentinel that stops it (the graph's natural-termination target).
- **Shallow agent** — a single tool-calling loop (one model, one tool set, one decision point). Explicitly *not* a deep agent (planning / memory / reflection — L14).

## Main points the lecture should land

- **It's the same loop, drawn as a graph.** L11 introduces no new *control flow* — model → tool → model until termination is exactly L07. What's new is expressing that flow as inspectable data (nodes, edges, state) and letting LangGraph drive it. Open with this, reusing L07's Demo 4 framing students already saw.
- **A graph makes control flow into data.** A `while` loop hides the routing in Python statements; a graph turns "what runs next" into edges you can read, draw, and reroute. That's worth little for one loop and a lot once the flow branches — which is precisely why L12 (patterns) follows.
- **State is the message history, now typed and framework-managed.** The thing every node shares is the same list L07 mutated. The reducer (append, don't overwrite) is what preserves the `tool_use`/`tool_result` pairing invariant — the framework enforcing by construction the rule L07 made you remember.
- **The framework gives you the boring parts for free.** The run-driver loop, the step/recursion cap, the execution trace, a prebuilt tool node — all the scaffolding L07 made explicit is now supplied. That convenience *is* the value proposition; name each freebie against its L07 hand-rolled twin so the trade is concrete.
- **"Shallow" is a deliberate scope.** A single tool-calling loop is a complete, useful agent — most production agents are shallow. Deep agents (planning, memory, reflection) are a later, heavier choice (L14), not an upgrade everyone needs. Define the word so students don't think "shallow" means "lesser."
- **Bring your eval set across.** The cleanest proof that the rebuild is correct is running L09's eval set against the LangGraph agent and seeing the same cases pass. This is L09's "carry it forward" rule in action, one lesson later — make it a visible beat, not an afterthought.
- **Tracing transfers, too.** LangGraph emits its own execution trace; it shows the same model-call / tool-call / state-update story L08 taught students to read. The skill is portable — only the trace's packaging changed.

## Common student confusions to watch for

- *"LangGraph is doing something fundamentally different from my loop."* No — it's the same model→tool→model flow with the loop driver, routing, and state-merging supplied for you. If a student can't map each graph piece back to an L07 line, slow down and do the mapping explicitly.
- *"A node 'sets' the state."* Not quite — a node *returns an update* that a **reducer** merges into state. For `messages` the reducer appends; returning a value without understanding the reducer is how students accidentally overwrite history (the L07 invariant bug, reborn). Teach the reducer, not just "return a dict."
- *"State should hold everything — the model client, the tools, config."* No — state is the data that *flows between nodes*; clients and tool registries are dependencies wired in at build time, not state. Conflating them produces a tangled graph.
- *"The graph removed the need for a step cap."* It didn't — LangGraph has a recursion/step limit that is the framework's version of L07's `max_steps`. A runaway graph still hits a cap; students should know where that cap lives and that hitting it is still a signal worth investigating (the L07 lesson).
- *"A graph is always better than a loop."* For a single shallow loop it's roughly break-even — more setup for equivalent behavior. The graph earns its keep when control flow branches (L12) or needs the framework's built-ins (tracing, persistence). Over-reaching for a framework on a 50-line problem is the L07-objective-4 mistake, restated.
- *"Shallow means weak / a toy."* Shallow means *single-loop*, which is most real agents. Depth is a specific set of additions (planning, memory, reflection) with its own cost, covered later — not a quality grade.

## Bridge to L12 (and the deferred L10)

L12 (LangGraph design patterns) is the direct sequel: once students can think in nodes, edges, and state, L12 surveys the *patterns* those primitives compose into — ReAct, plan-and-execute, supervisor, hierarchical, state-machine routing — and when to reach for each. L11's job is to make the **primitives and the single-loop graph** second nature so L12 can move at the level of *patterns* without re-teaching graph mechanics. The concrete handoff: at the end of L11 students have a compiled, working shallow-agent graph with typed state and a passing eval set; L12 starts by asking "what else can this graph shape express?" <!-- *NEED INPUT*: confirm the L11→L12 boundary — L11 owns "one graph, one loop, state mechanics"; L12 owns "named multi-node patterns and their trade-offs." When L12's roadmap is authored, ensure ReAct in particular is framed there as a *pattern over* the L11 primitives, not re-introduced from scratch. -->

> Note on lesson numbering: in the full 20-lesson plan, **L10 (Choosing model power for the task)** precedes L11. It is dropped from the mini cut, so L11 follows L09 directly. If L10's roadmap is later authored, revisit this lesson's model-selection asides — L11 deliberately keeps "which model to use" out of scope (it anchors on one model for clarity), and that choice should hand cleanly to L10 in the full course. <!-- *NEED INPUT*: confirm L11 anchors on a single model and defers all model-power trade-offs to L10 (full course) — in the mini cut, model selection is simply not covered. Recommendation: yes; keep L11 about graph mechanics, one model only. -->

## Open authoring questions

- **Decided (dependencies):** `langgraph` (`>=1.2.4`) and `langchain-anthropic` (`>=1.4.4`) are added as project dependencies via `uv add` (done when this decision was recorded — they were not present before; only `langchain-mcp-adapters` from L06 was). These are the LangGraph runtime and the native LangChain Claude chat model the graph nodes call.
- **Decided (client — native, not the seam):** L11 (and the later framework lessons — the shallow agent here, Skills in L18, multi-agent in L19) use the **native LangChain model (`ChatAnthropic`) directly inside the graph nodes**, *not* the repo's `PotatoLLMClient` seam. Forcing the `potato_llm` seam into the graph would fight the framework and obscure the lesson; instead the lecture **explicitly calls out the departure** — "frameworks bring their own client abstraction" — as a teaching point. The hand-rolled `potato_llm` seam remains the abstraction for L01–L09; from the framework lessons on, the framework's own client is used. The API key still loads through `common/config.py` (`ChatAnthropic` reads `ANTHROPIC_API_KEY` from the same environment the config seam populates), so key handling is unchanged.
- <!-- *NEED INPUT*: estimated lecture duration — best guess 90–120 minutes including a live build of the `StateGraph` shallow agent and a run of L09's eval set against it. Possibly split into "graph model + build" and "state/reducers + eval carry-over." -->
- <!-- *NEED INPUT*: which Claude model anchors the lesson — mirrors L07/L08/L09. L11 deliberately uses a single model (model-power trade-offs are L10's job, out of the mini cut). Recommendation: anchor on the same model L07's demos used so the rebuilt agent's behavior is directly comparable to the hand-rolled original. -->
- <!-- *NEED INPUT*: prebuilt vs. hand-assembled graph (see objective 2). Recommendation: hand-assemble `StateGraph` first for the L07 mapping, then reveal the prebuilt react-agent helper as "the same thing packaged." Confirm this two-step framing fits the time budget. -->
- **Decided (shared `common/`):** L11 imports the shared tools from `common/tools.py` (`calculator`, `lookup`, `flaky_fetch`) and reuses the L09 eval harness from `common/evals.py` against the LangGraph rebuild. Rebuilding a *known* agent as a graph keeps the focus on LangGraph, not new tools, and lets the L09 eval set transfer unchanged as the equivalence check. (LangChain wraps plain Python tools, so the same `common/tools.py` functions bind into the graph's tool node.)
- <!-- *NEED INPUT*: how much LangGraph execution-trace / visualization to show (e.g. a rendered graph diagram, or the streamed step trace) as the L08 callback. Recommendation: show the rendered graph once (it makes "control flow as data" literal) and one streamed trace mapped back to the L08 trace shape; keep it light — full observability tooling is not the lesson. -->
- <!-- *NEED INPUT*: persistence / checkpointing — LangGraph offers a checkpointer (memory across runs). Recommendation: out of scope for L11 (shallow, single-run); name it as a forward pointer toward deep agents / context management (L14/L15). Confirm it stays deferred. -->
- <!-- *NEED INPUT*: overlap check with L07 — L07's Demo 4 already previews a minimal framework agent beside the hand-rolled loop. Confirm L11 *delivers* that framework rebuild in full (it's the lesson's whole point) while treating L07's preview as the teaser it was, not re-explaining the hand-rolled loop from scratch. -->
