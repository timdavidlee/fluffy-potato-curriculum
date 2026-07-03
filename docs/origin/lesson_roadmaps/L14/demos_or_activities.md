# L14: Teacher-led demos — Shallow agents in LangGraph

> Sibling docs: [objectives.md](objectives.md) (what the lesson aims for), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md).
>
> **Audience for this file:** the teacher running L14. Every demo below is *teacher-driven, no student participation*. Student-driven exercises live in the L14 labs (separate file, stage 2).
>
> **Anchor model: Claude Sonnet 4.6 — a *single* model throughout.** Unlike [L04](../L04/objectives.md) (which mixed Haiku/Sonnet per node to show the mechanism), L14 holds the model fixed so the **graph shape is the only variable** versus the L10 hand-rolled loop. Model-power trade-offs are L13's job (full course; dropped in the mini cut). Nodes call the **native LangChain `ChatAnthropic`** client (continuing the framework-client departure begun in L04, *not* the `potato_llm` seam).

## How to read this file

Each demo is a self-contained block with:

- **Goal** — the single insight the demo should land. Tied to a learning objective from [objectives.md](objectives.md).
- **Pre-flight** — what the teacher needs loaded before class.
- **Live script** — the order of operations during the demo. Treat it as a checklist, not a teleprompter.
- **What to highlight** — the moment(s) where the teacher should slow down and say the takeaway out loud.
- **If the demo misbehaves** — graceful fallback for when the model surprises you (it will).

The demos are ordered to match the three learning objectives from [objectives.md](objectives.md). Demo 1 *draws* the shallow agent as a graph and maps each piece to its L10 equivalent (objective 1); Demo 2 *builds* it live on `StateGraph`, runs it to behavioral equivalence with L10, and reveals the prebuilt one-liner (objective 2); Demo 3 dwells on **state and reducers** and breaks the message reducer on purpose (objective 3); Demo 4 carries L12's **eval set** onto the rebuild and lands the trace in L11's **Langfuse** — the "carry it forward" payoff. The optional demo points forward to L15 patterns. They build on each other — every demo reuses Demo 2's compiled graph and the shared `common/tools.py` tools, never a fresh one. Run them in order on first delivery.

> **The spine of L14: it's the same loop, drawn as a graph.** L14 introduces no new *control flow* — model → tool → model until termination is exactly the L10 loop. What changes is the *shape*: an explicit `while` loop becomes an explicit **graph** of nodes and edges over a shared **state**, and LangGraph drives it. Open with L10's Demo 4 framing students already saw — *"every framework you'll see is a fancier version of the loop you wrote"* — and L04's framing — *"you built the acyclic workflow; here's the **back-edge** that makes it an agent."* Reinforce the primitives from L04; do **not** re-derive the hand-rolled loop from scratch (that's L10, assumed solid here).

## Pre-flight (once, at the top of the lesson)

The teacher should have, before the first demo starts:

- **LangGraph + the native LangChain Claude client ready** — `from langgraph.graph import StateGraph, END` and `from langchain_anthropic import ChatAnthropic`. Both `langgraph` (`>=1.2.4`) and `langchain-anthropic` (`>=1.4.4`) are already project dependencies (added via `uv add`); no install during class. The key loads through `common/config.py` as before — only the *client* is the framework's. <!-- *NEED INPUT*: confirm the exact Sonnet 4.6 model id string passed to ChatAnthropic, read from common/config.py rather than hard-coded in cells. Mirrors the same open item in L04's demos. -->
- **The shared tools imported, not rebuilt:** `from fluffy_potato_curriculum.common.tools import calculator, lookup, flaky_fetch`. Rebuilding the *same* agent students already know (L10/L11) as a graph is the whole point — new tools would dilute it. (LangChain wraps plain Python tools, so the same `common/tools.py` functions bind straight into the graph's tool node.)
- **The L10 hand-rolled loop visible in scrollback** (or its `common/agent_loop.py` reference copy) as the side-by-side the whole lesson maps against — `agent_loop.run(...)` → `RunResult(final_text, iterations, termination, trace)`.
- **The two canonical L10/L11 tasks ready:** the **chaining task** (*"the population of the city whose name is the answer to `17**2 - 1`"* → `calculator` then `lookup`, natural termination) and the **`flaky_fetch` failure task** (walk the four URL behaviors, exercise tool-failure handling).
- **The shared Langfuse callback handler wired up**, pointing at the *same* self-hosted Langfuse instance from L11 (LangChain/LangGraph callback handler; keys via `common/config.py`), so the graph's auto-emitted spans land in the dashboard students already know, next to their hand-rolled L11 traces.
- **A graph-diagram renderer ready** (`compiled_graph.get_graph().draw_mermaid_png()` or the Mermaid text) — rendering the compiled agent graph once makes "control flow as data" literal. <!-- *NEED INPUT*: confirm the diagram render path works in the demo environment; Mermaid-text/ASCII fallback is fine. Mirrors L04's demos. -->
- **The L12 eval harness importable** — `from fluffy_potato_curriculum.common.evals import EvalCase, evaluate` — plus the L12 eval cases, for Demo 4's carry-forward. <!-- *NEED INPUT*: the L12 scorers read `run.final_text` / `run.trace` off the hand-rolled `RunResult`; the LangGraph agent returns a state dict (a `messages` list). Confirm the adapter that maps the compiled graph's output into the shape `common/evals.py` scorers expect (a thin `RunResult`-like wrapper), so the *same* L12 EvalCases run unchanged against the rebuild. This adapter is the concrete mechanism behind objective "bring your eval set across." -->
- **Completed graph definitions in a sibling file** to paste if live-coding falls behind — the hand-assembled `StateGraph` agent (Demo 2) and the prebuilt-helper version.

> Why rebuild a *known* agent: L14 is about the **graph mental model and single-loop mechanics**, not new capabilities. Reusing L10/L11's tools and tasks means the only new thing on screen is LangGraph itself — so when the rebuild issues the same tool sequence and the L12 eval set passes, the framework reads as *conveniences over a familiar skeleton*, exactly the lesson's pedagogical bet.

## Demo 1 — From loop to graph: draw the shallow agent (Objective 1)

**Goal:** before any code, *draw* the shallow-agent graph and map every piece back to its L10 equivalent. Land the headline — **it's the same model→tool→model loop, now expressed as inspectable data (nodes, edges, state)** — and recall L04's framing that the line between a workflow and an agent is a single **back-edge**.

**Pre-flight:**

- A whiteboard / slide with the L10 loop pseudocode on the left, empty graph space on the right.
- L04's acyclic workflow diagram available for the callback.

**Live script:**

1. Recall L04 in one line: *"you wired an **acyclic** workflow — the developer owned the path. An agent adds one thing: a **back-edge** that hands the path to the model."* Put L04's DAG up, then draw the cycle.
2. Draw the shallow-agent graph piece by piece, naming each and its L10 twin:
   - an **`agent`** (model-call) node — the L10 "call the model" step;
   - a **`tools`** node — the L10 "execute every `tool_use`, append a matching `tool_result`" step;
   - a fixed **edge** `tools → agent` — the L10 "loop back after running tools";
   - a **conditional edge** out of `agent` → `tools` (the model emitted a `tool_use`) or → `END` (natural termination) — the L10 `if there's a tool_use: … else: return` branch, *lifted out of Python into the graph.*
3. Trace a run on the diagram with your finger: agent → (tool_use?) → tools → agent → (no tool_use) → END. Point at the **back-edge** and say: *that cycle is the agent.*
4. State **why a graph at all**: a loop encodes control flow implicitly in Python statements; a graph makes control flow **data** — nodes and edges you can inspect, visualize, reroute, and later extend. Be honest: for a *single* loop it's roughly break-even; the payoff shows up when the flow stops being one loop (the motivation for L15).

**What to highlight:**

- **Same loop, new shape.** If a student can't map each graph piece back to an L10 line, slow down and do the mapping explicitly — that mapping *is* objective 1.
- **The conditional edge is the L10 branch.** "Is there a `tool_use`?" used to be an `if` in your Python; now it's a routing function on an edge. The decision is identical; only its location moved.
- **"Shallow" is a deliberate scope, defined now:** one model, one tool set, one decision point that either calls a tool or finishes. *Not* a deep agent (planning / memory / reflection — L18). Shallow ≠ lesser; most production agents are shallow.

**If the demo misbehaves:**

- Pure diagram + discussion, so little can flake. If students fixate on "where's the loop variable?", point at the `tools → agent` edge: the framework's run-driver *is* the `while`, supplied for you (Demo 2 makes that concrete).

## Demo 2 — Build the single-loop agent on StateGraph, then reveal the prebuilt one-liner (Objective 2)

**Goal:** live-build the shallow agent on `StateGraph`, run it to **behavioral equivalence** with the L10 loop, then reveal the prebuilt helper as *"the same thing, packaged."* Land what the framework gives you **for free** that L10 made you write by hand.

**Pre-flight:**

- An empty cell/file for the live build, Demo 1's diagram beside it.
- The shared tools (`calculator`, `lookup`, `flaky_fetch`) imported.
- Both canonical tasks ready to run.

**Live script:**

1. Live-code the **state schema** (a `TypedDict` / annotated state): a `messages` field (with the **add-messages reducer** — flag it now, *unpack it in Demo 3*) and one `step` counter. Keep it minimal — messages plus one counter (a decided scope).
2. Live-code the two **nodes**:
   - `agent` — calls `ChatAnthropic` (Sonnet 4.6) bound with the tool schemas on the current `messages`, returns the response to be appended.
   - `tools` — executes every requested `tool_use` and returns matching `tool_result`s — *the same message-history invariant from L10*, now localized to one node (including the L10 convert-exception-to-`tool_result(is_error=True)` handling).
3. Wire it with the builder: `add_node("agent", …)`, `add_node("tools", …)`, `set_entry_point("agent")`, `add_conditional_edges("agent", route_fn, {"tools": "tools", END: END})` where `route_fn` returns `"tools"` if the last message has a `tool_use` else `END`, and `add_edge("tools", "agent")` — the **back-edge**. `compile()`.
4. **Render the compiled graph diagram** and put it next to Demo 1's hand-drawn one — they match.
5. **Run for equivalence.** `invoke()` on the **chaining task** → watch it issue `calculator` then `lookup` and terminate naturally — the *same sequence* L10 produced. Then `invoke()` on the **`flaky_fetch` failure task** → confirm tool-failure handling still works inside the `tools` node.
6. **Name the freebies against their L10 twins:** the run-driver loop (L10's `while`), a **recursion/step limit** (L10's `max_steps` cap — show where it lives), the built-in execution trace (L11, see Demo 4), and a prebuilt tool node. Then **reveal the one-liner:** the prebuilt react-agent helper builds *this same graph* in a single call — *"the same thing, packaged."*

**What to highlight:**

- **The framework gives you the boring parts for free** — run-driver, step cap, trace, prebuilt tool node. That convenience *is* the value proposition; name each freebie against the L10 hand-rolled twin so the trade is concrete, not magic.
- **Hand-assemble first, *then* reveal the prebuilt.** Students see the explicit nodes/edges before the one-liner, so `create_react_agent` reads as "the graph I just built, wrapped," not a black box — mirroring L10's hand-rolled-then-framework arc. <!-- *NEED INPUT*: confirm which prebuilt to reveal — `create_react_agent` (whole-agent one-liner) vs a prebuilt `ToolNode` dropped into the hand-wired graph. Recommendation: show the prebuilt `ToolNode` swap first (smallest diff to the hand build), then mention `create_react_agent` as the whole-graph one-liner and the natural L15 lead-in. -->
- **The step cap didn't go away.** A runaway graph still hits LangGraph's recursion limit — the framework's `max_steps`. Hitting it is still a signal worth investigating (the L10 lesson), not noise.

**If the demo misbehaves:**

- If live-coding the builder falls behind, paste the completed graph and walk it node by node — but **keep both runs**; behavioral equivalence with L10 is the demo's proof.
- If the rebuild's tool sequence differs from L10's on the day, that's run-to-run variance (L11's lesson), not a bug — re-run, and note that the *eval set* (Demo 4), not a single run, is how you actually confirm equivalence.

## Demo 3 — State and reducers: the message history, now typed (Objective 3)

**Goal:** make graph **state** concrete and show *why the reducer matters* by breaking it. Land that **state is the same message history L10 mutated, now typed and framework-managed, and the add-messages reducer *appends* — which is what preserves the `tool_use`/`tool_result` pairing invariant.**

**Pre-flight:**

- Demo 2's compiled agent and its state schema.
- A deliberately-wrong variant of the `agent`/`tools` node whose returned update **overwrites** `messages` instead of appending.

**Live script:**

1. Inspect the state mid-run: print `messages` after each node. Show it growing — user, assistant-with-`tool_use`, tool-result, assistant… the *same list* L10 mutated in place, now a typed value LangGraph threads through every node.
2. Explain **how nodes update state**: a node *returns an update* that LangGraph merges via per-field **reducers**. For `messages`, the **add-messages reducer appends**. Say it plainly: the node doesn't *set* state, it *contributes* to it.
3. **Break it on purpose.** Swap in the overwrite variant (wrong/absent reducer) and re-run: history gets clobbered, a `tool_use` loses its matching `tool_result`, the run breaks — *the single most common L10 bug, reborn in graph form.* Restore the append reducer; it works again.
4. Draw the **state boundary**: what belongs in state (the `messages`, the `step` counter — data that *flows between nodes*) vs. what does **not** (the model client, the tool registry — *dependencies* wired in at build time). Conflating them is how a graph gets tangled.

**What to highlight:**

- **A node returns an update; a reducer merges it.** "Return a dict and hope" is the trap — teach the reducer, not just the return. The append-vs-overwrite distinction is the whole objective.
- **The reducer enforces by construction the rule L10 made you remember.** L10 made you *manually* keep each `tool_use` paired with its `tool_result` in order; the add-messages reducer guarantees it. That's the framework earning its keep.
- **State is data that flows; clients and tools are dependencies.** Getting this boundary right is the difference between a clean graph and a tangled one.

**If the demo misbehaves:**

- If the overwrite variant happens to *not* break on a short run (the clobber lands harmlessly), use a multi-tool task so a `tool_use`/`tool_result` pair is visibly orphaned. The point is to *show* the invariant breaking, not to argue it in the abstract.

## Demo 4 — Carry the eval set across, and find the trace in the same Langfuse (the payoff)

**Goal:** make L12's **"carry it forward"** rule and L11's **portable tracing** concrete in one beat — run the *same* L12 eval set against the LangGraph rebuild (it passes → behavioral equivalence proven), and watch the graph's auto-emitted spans land in the *same* Langfuse dashboard next to the hand-rolled L11 traces. This is the strongest possible reinforcement that evaluation and tracing travel with the agent, not the implementation.

**Pre-flight:**

- The L12 eval set and the `common/evals.py` harness, with the adapter that feeds the graph's output into the L12 scorers (see pre-flight `NEED INPUT`).
- The Langfuse callback handler attached to Demo 2's compiled agent.

**Live script:**

1. Recall L12 in one line — *"when you build or change an agent, you run its eval set"* — then run the **same L12 eval set** against the LangGraph rebuild. Read the pass table: the cases that passed on the L10 loop pass on the graph. *Same cases, different implementation, nothing regressed* — the cleanest proof the rebuild is correct.
2. Open **Langfuse**: the graph's run is *already there* (the callback emitted it), rendered as the **same spans** students know — a GENERATION for each model call, a SPAN for each tool call — sitting next to their hand-rolled L11 traces in the same project. The skill is portable; only the trace's packaging changed.
3. Re-do one L11 reading task in the Langfuse UI on the *graph's* trace — locate the tool calls, read the arguments, confirm termination — to feel that "read the trace" works identically whether the trace came from the hand-rolled loop or the framework.

**What to highlight:**

- **Bring your eval set across — make it a *visible* beat, not an afterthought.** The eval set is the regression ratchet from L12; running it against the rebuild is L12's whole "carry it forward" thesis cashing out one lesson later.
- **Tracing transfers, too.** LangGraph emits the same model-call / tool-call / state-update story L11 taught students to read — in the same dashboard. The graph didn't make you relearn observation; it reused it.
- One honest caveat: the framework's auto-trace is *shaped* by LangGraph, so span names/nesting differ slightly from the hand-rolled `TraceEvent`s — the *structure* (GENERATION/SPAN, tokens, args) is the same, which is the recognition payoff.

**If the demo misbehaves:**

- If a couple of eval cases flake on the rebuild, that's L12's non-determinism lesson, not a port bug — bump samples and read the **pass rate**, don't chase a single red.
- If the Langfuse instance is down, fall back to the graph's in-memory/auto-emitted trace object and read it inline; the carry-forward point stands without the dashboard (Langfuse is the *payoff*, not a hard dependency — same stance as L11).

## Optional demo — toward L15 patterns

If time allows, point forward without teaching it: the prebuilt react-agent one-liner you revealed in Demo 2 *is* a named pattern (**ReAct**) — a *pattern over* the L14 primitives, not a new mechanism. L15 surveys the others (plan-and-execute, supervisor, hierarchical, state-machine routing) and *when* to reach for each. Ask the open question that L15 answers — *"what else can this graph shape express once control flow stops being a single loop?"* — and stop there.

Don't teach any pattern here — L14 owns *one graph, one loop, state mechanics*; L15 owns the named patterns and their trade-offs. Just land that the graph mental model students now have is the thing L15 builds *patterns* on top of.

<!-- *NEED INPUT*: include this forward pointer in the lecture, or save it as L15's opener? Recommendation: a 60-second close — it frames create_react_agent as "a pattern, not magic" and motivates L15. -->

## Pacing notes for the teacher

- **Per-demo time:** Demo 1 is 10–15 minutes (diagram + L10 mapping, no build). Demo 2 is the long one, 25–35 minutes (live `StateGraph` build + two equivalence runs + the prebuilt reveal). Demo 3 is 12–18 (state inspection + the reducer-break). Demo 4 is 10–15 (eval carry-over + Langfuse). Optional close is 5–8. Total ~65–95 minutes plus discussion — fits the **~90–120 minute** lecture pinned in [objectives.md](objectives.md). If it runs long, split at the Demo 2/3 boundary: "graph model + build" then "state/reducers + eval carry-over."
- **Live-coding budget:** only Demo 2's graph needs a full live build. Demo 3 is a small edit (the reducer swap) to Demo 2; Demos 1 and 4 are diagram/run, not build. Do **not** re-derive the graph in each demo — reuse Demo 2's compiled agent.
- **Single model, on purpose:** L14 holds the model at Sonnet 4.6 so the only variable vs. L10 is the *shape*. Resist mixing models here — that was L04's mechanism demo; the *which-model* decision is L13's.
- **Variance budget:** the agent loop is non-deterministic (L11) — budget a re-run wherever a specific tool sequence matters, and lean on the **eval set** (Demo 4), not a single run, for the equivalence claim.
- **The audience watches, doesn't participate.** Resist "what should the routing function return here?" as a group question — that's a lab pattern. Hands-on graph-building and the eval carry-over are for the L14 labs.

## Open authoring questions

Most of L14's big decisions are already pinned in [objectives.md](objectives.md) (native `ChatAnthropic` not the seam; single anchor model Sonnet 4.6 with model-power deferred to L13; `langgraph` + `langchain-anthropic` deps already added; reuse `common/tools.py` and the L12 `common/evals.py` against the rebuild; Langfuse callback into L11's instance; hand-assemble `StateGraph` then reveal the prebuilt; state kept to messages + one counter; persistence/checkpointing out of scope as a forward pointer to L17/L18/L19; the intentional L04↔L14 primitives overlap). The remaining open items are stage-2 mechanics:

- <!-- *NEED INPUT*: the exact Sonnet 4.6 model id string passed to ChatAnthropic, read from common/config.py. Mirrors L04's demos. -->
- <!-- *NEED INPUT*: the adapter mapping the compiled graph's output (a messages-list state dict) into the shape `common/evals.py` scorers expect (a RunResult-like wrapper exposing final_text + trace), so the L12 EvalCases run unchanged against the rebuild. This is the concrete mechanism behind "bring your eval set across." -->
- <!-- *NEED INPUT*: which prebuilt to reveal in Demo 2 — a prebuilt ToolNode swapped into the hand-wired graph (smallest diff) and/or the create_react_agent whole-graph one-liner. Recommendation: ToolNode first, then mention create_react_agent as the L15 lead-in. -->
- <!-- *NEED INPUT*: confirm the graph-diagram render path (draw_mermaid_png vs Mermaid text vs ASCII) works in the demo environment. Mirrors L04's demos. -->
- <!-- *NEED INPUT*: are the demos run in a projected Jupyter notebook, a slide-embedded REPL, or a demo-runner script? Mirrors the same open question in L10's, L12's, and L04's demos. -->
- <!-- *NEED INPUT*: include the optional L15 forward-pointer in the lecture or hold it for L15's opener? Recommendation: a 60-second close. -->
