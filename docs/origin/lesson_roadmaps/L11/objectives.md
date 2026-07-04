# L11: Shallow agents in LangGraph

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (lesson-plan row L11).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).
> Preceding lesson: [L10 Hand-rolled agent loop](../L10/objectives.md). Following lesson: [L12 What an agent generates: state, logs, traces & extracts](../L12/objectives.md).
>
> Conceptually L11 is the **payoff beat right after the hand-rolled loop**: in L10 students wrote the model → tool → model loop by hand; L11 shows the batteries-included one-liner — LangChain's **`create_agent`** — that produces *the same loop* in a single call. It also **closes the workflow-vs-agent arc opened by the early graph block** ([L04 sequential chaining](../L04/objectives.md) + [L05 conditional routing](../L05/objectives.md)): those lessons wired *acyclic*, developer-owned graphs (workflows); an agent adds the one thing that turns a graph into an agent — a **cycle** plus model-driven control (the model decides what runs next by emitting tool calls). `create_agent` hands you that cyclic, model-driven agent prebuilt.

## Where this lesson sits

This lands immediately after L10, on purpose. Students have just hand-built an agent from nothing: a single tool round-trip ([L07](../L07/objectives.md)), good tool design ([L08](../L08/objectives.md)), and then the **model → tool → model loop** in plain Python ([L10](../L10/objectives.md)) — `agent_loop.run(...)` returning a `RunResult(final_text, iterations, termination)`. L10's Demo 4 explicitly previewed this moment: the same task run on the hand-rolled loop *and* on a minimal framework version, with the punchline that **"every framework you will see is a fancier version of the loop you wrote."**

L11 cashes that in immediately. The pedagogical bet is that introducing a framework *right after* students have felt the loop by hand means the framework reads as a set of conveniences over a familiar skeleton, not as magic. Students take the *same agent they already understand* and rebuild it with **`from langchain.agents import create_agent`** — one call that returns a running shallow agent. The control flow does not change — it is still model → tool → model until termination. What changes is that the loop, the routing, the message-history bookkeeping, and the step cap are now the framework's job, not yours.

The lesson is deliberately **`create_agent`-first**. Students do **not** hand-assemble a `StateGraph` with explicit nodes, edges, and reducers here — that explicit, under-the-hood construction is the job of [L15 LangGraph design patterns](../../CURRICULUM_PRD.md), which owns the graph internals and the patterns you build once you drop below the one-liner. L11 keeps a *lightweight* conceptual diagram of the graph `create_agent` wraps (an `agent` node, a `tools` node, a back-edge, a conditional exit) so students can see what the one-liner is standing in for — but building that graph by hand is out of scope. The goal is: *you hand-rolled the loop; here is the one-line, production-shaped way to get it, and a mental picture of what it wraps.*

The title word **"shallow"** is load-bearing and should be defined early: a *shallow* agent is a single tool-calling loop — one model, one set of tools, one decision point that either calls a tool or finishes. It is exactly the L10 loop. This is contrasted with *deep* agents (planning, persistent memory, sub-todos, reflection), which the full plan covers later ([L18](../../CURRICULUM_PRD.md)) — named here only as "what we are **not** building yet." Shallow ≠ lesser: most production agents are shallow.

## Prerequisites

Students arriving at L11 should already be able to:

- Build and run a model→tool→model loop in plain Python, maintain the message-history invariant (every `tool_use` answered by a matching `tool_result`), and read a `RunResult` ([L10](../L10/objectives.md), objectives 1–2). `create_agent` automates each of these pieces — a student who hasn't internalized the loop can't see what the one-liner is replacing.
- Reason about termination as a *design decision* — natural vs. `max_steps`, plus token-budget and loop-detection as extensions (L10, objective 2). `create_agent` supplies its own recursion/step limit; students should recognize it as the framework's `max_steps`.
- Handle loop-level tool failures by converting them into `tool_result`s with `is_error: true` (L10, objective 3) — `create_agent` does the same inside its tool step.
- Design and bind plain-Python tools to a model ([L07](../L07/objectives.md)/[L08](../L08/objectives.md)); LangChain wraps the same plain functions, so the L10 tools bind straight into `create_agent`.

If a student is shaky on the L10 loop, redirect there first — L11 is a *re-expression* of that loop, and the whole lesson lands only if the original is solid.

> **Not prerequisites (deliberately):** tracing ([L12](../L12/objectives.md)) and evaluation ([L13](../L13/objectives.md)) come *after* L11 now. L11 does **not** lean on reading a structured trace or running an eval set — those lessons will later take *this* agent (and the L10 loop) as their subject. Keep L11's proof of correctness informal: run the agent on the L10 tasks and eyeball the same tool sequence and natural termination.

## Learning objectives

By the end of L11, a student should be able to:

1. **Recognize a shallow agent as the L10 loop, and `create_agent` as its one-liner.** Concretely:
   - State the definition of a *shallow* agent (one model, one tool set, one decision point) and that it is exactly the model → tool → model loop from L10.
   - Read a *lightweight* graph diagram of what `create_agent` wraps and name each piece against its L10 twin: an **`agent`** (model-call) step, a **`tools`** step, a **back-edge** from tools back to the model, and a decision point that either calls a tool or finishes. Point at the back-edge and say *"that cycle is the agent."* (Recall [L04](../L04/objectives.md)'s framing: a workflow is acyclic and developer-driven; the back-edge that hands the path to the model is what makes it an agent.)
   - Articulate that this diagram is a *mental model*, not something you build in L11 — assembling that graph node-by-node is L15's job. Here the point is only to see that `create_agent` is not magic: it is the loop you already wrote, packaged.

2. **Build and run a shallow agent with `create_agent`.** Concretely:
   - Use `from langchain.agents import create_agent` to construct an agent from a **model** (native LangChain `ChatAnthropic`, Sonnet 4.6) and the **L10 tools** (`calculator`, `lookup`, `flaky_fetch`), plus a system prompt — the whole agent in one call, returning a runnable.
   - Invoke it on the **L10 chaining task** and watch it issue the same tool sequence (`calculator` then `lookup`) and terminate naturally — behavioral equivalence to the hand-rolled loop, with none of the loop written by hand. Then invoke it on the **`flaky_fetch` failure task** and confirm tool-failure handling still works.
   - Read the agent's result: the returned **message history** (the same `tool_use`/`tool_result` sequence L10 produced), and pull the final answer out of it.
   - Name what `create_agent` gave you for free that L10 made you write by hand — the run/loop driver, the tool-call routing, the message-history bookkeeping, a recursion/step limit (the framework's `max_steps`), and tool execution — each against the L10 hand-rolled equivalent it replaces.

3. **Know the boundary of `create_agent` — and when you'd drop below it.** Concretely:
   - Enumerate `create_agent`'s config surface a shallow agent actually uses: the **model**, the **tools**, and the **system prompt** — and recognize that message-history state and the loop are managed for you (you don't hand-write a reducer or a `while`).
   - State plainly *when the one-liner stops being enough*: when the control flow stops being a single loop and you need custom nodes, branches, or state — which is exactly the moment you drop to explicit graph construction. That explicit `StateGraph` world (nodes, edges, reducers, state schema) and the named patterns built on it (ReAct, plan-and-execute, supervisor) are **L15's** territory; L11 points at the door without walking through it.
   - Keep model-power questions out of scope: L11 anchors on a single model (Sonnet 4.6) so `create_agent` is the only new thing on screen; which model to use for which step is [L14](../../CURRICULUM_PRD.md)'s job (full course; dropped in the mini cut).

## Vocabulary the lecture must establish

Define these explicitly and reuse them verbatim through the labs and into L15:

- **Shallow agent** — a single tool-calling loop (one model, one tool set, one decision point). Explicitly *not* a deep agent (planning / memory / reflection — L18).
- **`create_agent`** — LangChain's one-call constructor (`from langchain.agents import create_agent`) that returns a runnable shallow agent from a model + tools (+ prompt). The framework's replacement for L10's hand-written `while` loop, routing, and message bookkeeping.
- **Agent step / tool step** — the two units of work inside the agent: call the model, then run any tools it asked for. The names of the nodes in the graph `create_agent` wraps.
- **Back-edge / the cycle** — the transition from the tool step back to the model step; the single thing that turns L04/L05's acyclic *workflow* into an *agent*.
- **Recursion / step limit** — the framework's cap on how many loop turns run, the analogue of L10's `max_steps`; hitting it is still a signal worth investigating.

## Main points the lecture should land

- **It's the same loop, in one line.** L11 introduces no new *control flow* — model → tool → model until termination is exactly L10. What's new is that `create_agent` writes the loop, the routing, and the message bookkeeping for you. Open with L10's Demo 4 framing students already saw.
- **`create_agent` is not magic — it's your loop, packaged.** Show the lightweight diagram of what it wraps (agent step, tool step, back-edge, exit) and map each piece to an L10 line, so the one-liner reads as a convenience over a familiar skeleton.
- **The framework gives you the boring parts for free.** The run-driver loop, the step/recursion cap, the tool-call routing, the message-history append — all the scaffolding L10 made explicit is now supplied. That convenience *is* the value proposition; name each freebie against its L10 hand-rolled twin so the trade is concrete.
- **"Shallow" is a deliberate scope.** A single tool-calling loop is a complete, useful agent — most production agents are shallow. Deep agents (planning, memory, reflection) are a later, heavier choice (L18), not an upgrade everyone needs.
- **When the one-liner isn't enough, you drop to the graph — and that's L15.** Custom nodes, branches, and state are where you leave `create_agent` behind for an explicit `StateGraph`. L11 names that door; L15 opens it.

## Common student confusions to watch for

- *"`create_agent` is doing something fundamentally different from my loop."* No — it's the same model→tool→model flow with the loop driver, routing, and message-append supplied for you. If a student can't map the diagram back to an L10 line, slow down and do the mapping.
- *"I need to understand `StateGraph`/nodes/reducers to use `create_agent`."* Not for a shallow agent — that's exactly what the one-liner spares you. The graph internals are L15; here you configure model + tools + prompt and run it.
- *"The one-liner removed the need for a step cap."* It didn't — `create_agent` has a recursion/step limit that is the framework's `max_steps`. A runaway agent still hits a cap; hitting it is still a signal (the L10 lesson).
- *"Shallow means weak / a toy."* Shallow means *single-loop*, which is most real agents. Depth is a specific set of additions (planning, memory, reflection) with its own cost, covered later — not a quality grade.
- *"A framework is always better than a hand-rolled loop."* For a single shallow loop `create_agent` mostly buys you not maintaining boilerplate. The bigger payoff comes when control flow branches (L15) — reaching for a framework on a 50-line problem is the L10-objective-4 mistake, restated.

## Bridge to L12 (and forward to L15)

The immediate sequel is [L12 (What an agent generates: state, logs, traces & extracts)](../L12/objectives.md). Students can now build a shallow agent two ways — by hand (L10) and in one line (L11) — so L12 steps back and asks *what a run actually produces*: the state it threads, the logs and **traces** you read to debug it, and the **extracts / new records** it writes. L11's concrete handoff to L12: a working `create_agent` agent whose returned **message history** is the raw material L12 teaches you to read as a trace. (L13 then teaches you to *judge* that agent with an eval set.)

The forward pointer is [L15 (LangGraph design patterns)](../../CURRICULUM_PRD.md): once students have hit the ceiling of the one-liner, L15 drops below it to the explicit graph — nodes, edges, state, reducers — and the named patterns (ReAct, plan-and-execute, supervisor, …) built on those primitives. **Decided:** the L11→L15 boundary is "L11 owns `create_agent` and the shallow-agent mental model; L15 owns hand-assembled `StateGraph`, graph state/reducers, and named multi-node patterns." When L15's roadmap is authored, the `StateGraph` build that used to live in L11 (agent node, tools node, conditional edge, back-edge, add-messages reducer) should be re-homed there as the concrete under-the-hood of `create_agent`.

## Open authoring questions

- **Decided (`create_agent`-first, StateGraph deferred):** L11 leads with and centers on `from langchain.agents import create_agent`. Hand-assembling a `StateGraph` (explicit nodes/edges/reducers/state schema) is **not** taught here — it moves to L15. L11 keeps only a lightweight conceptual diagram of the graph the one-liner wraps.
- **Decided (dependencies):** `langgraph` (`>=1.2.4`) and `langchain-anthropic` (`>=1.4.4`) are project dependencies (added via `uv add`); `create_agent` is imported from `langchain.agents`. <!-- *NEED INPUT*: confirm `langchain` (the package exposing `langchain.agents.create_agent` in the v1 line) is pinned as a direct dependency via `uv add`, not just pulled in transitively, so the import is stable. -->
- **Decided (client — native, not the seam):** L11 (and the later framework lessons — Skills in [L22](../L22/objectives.md), multi-agent in L24) use the **native LangChain model (`ChatAnthropic`) directly**, *not* the repo's `PotatoLLMClient` seam. The lecture **explicitly calls out the departure** — "frameworks bring their own client abstraction" — as a teaching point. The API key still loads through `common/config.py` (`ChatAnthropic` reads `ANTHROPIC_API_KEY` from the same environment the config seam populates).
- **Decided (anchor model):** Claude **Sonnet 4.6** — the same model L10's demos used, so the `create_agent` rebuild is directly comparable to the hand-rolled original. Model-power trade-offs are L14's job (full course, out of the mini cut).
- **Decided (shared `common/`):** L11 imports the shared tools from `common/tools.py` (`calculator`, `lookup`, `flaky_fetch`) and reuses the two canonical L10 tasks (the chaining task and the `flaky_fetch` failure task). Rebuilding a *known* agent keeps the focus on `create_agent`, not new tools.
- **Decided (no eval / tracing carry-over):** the old L14 demos that ran an eval set and routed traces to Langfuse are **removed** from L11 — evaluation (L13) and tracing (L12) now come *after* this lesson. L11 proves equivalence informally (same tool sequence, natural termination) and hands the agent forward as the subject L12/L13 instrument.
- **Decided (lecture duration):** target ~60–90 minutes — a live `create_agent` build, two equivalence runs (chaining + `flaky_fetch`), and the "what it wraps" diagram. Shorter than the old node-by-node lesson because the hand-assembled `StateGraph` build moved to L15. <!-- *NEED INPUT*: confirm the trimmed scope still fills a coherent segment, or whether L11 should absorb a short "read the returned messages" activity to reach a full session. -->
- **Decided:** persistence / checkpointing is out of scope for L11 (shallow, single-run); named as a forward pointer toward deep agents / context management (L18/L19).
