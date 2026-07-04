# L03: Single-node operations

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (lesson-plan row L03).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).
> Preceding lesson: [L02 Prompting fundamentals](../L02/objectives.md) — roles, structured output, few-shot. Following lesson: [L04 Directed graphs — sequential chaining](../L04/objectives.md) — wires *several* nodes from this lesson into a fixed DAG.

> **New lesson (reorder 2026-07-02).** L03 did not exist before the reorder. It is carved out as the first rung of a three-lesson orchestration ramp — **L03 single-node → L04 sequential graphs → L05 conditional graphs** — inserted between prompting fundamentals (L02) and the return to chain-of-thought/tools (L06–L07). See the PRD's "Ordering note — orchestration before tools" for the full rationale.

## Where this lesson sits

L03 is the **first graph lesson** and the **first framework lesson** in the course. [L01](../L01/objectives.md) and [L02](../L02/objectives.md) taught students to reason about tokens, cost, roles, and structured output while talking to the model through the repo's own [`potato_llm`](../../../src/fluffy_potato_curriculum/potato_llm/CLAUDE.md) seam — a hand-rolled client built for the course. L03 is where that changes: students meet **LangGraph**, and inside a LangGraph node they call the model through the **native LangChain `ChatAnthropic` client**, not `potato_llm`. Name this departure out loud in the lecture — *"frameworks bring their own client abstraction; this is the first of several you'll meet."* `langgraph` and `langchain-anthropic` are already project dependencies (added via `uv add`), so no install happens live.

L03's scope is deliberately the smallest possible unit of a graph: **one typed state, one node, nothing wired to it.** A student who finishes L03 should be able to say, in one sentence, *"a node is one LLM call you wire — state goes in, state comes out."* That sentence is the entire payload of this lesson. [L04](../L04/objectives.md) picks it up immediately and wires **several** nodes into a fixed sequence (prompt chaining); L05 (conditional graphs — routing & branching; roadmap not yet written) adds conditional edges. Together L03–L05 install the graph/orchestration model using **plain LLM calls only** — no tools (those arrive at [L07](../L07/objectives.md)) and no agent loop (hand-rolled at [L10](../L10/objectives.md), as LangGraph at [L11](../L11/objectives.md)).

The throughline the PRD names for this three-lesson ramp: **"you wire the graph (L03–L05); the model drives the loop (from L10)."** L03 is where "wiring" starts — at the smallest possible scale, a single wire with nothing on the other end yet.

L03 is kept in the mini course cut (see [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md), "Condensed Mini Lesson Plan") — the PRD lists it as *"the orchestration unit — a node is one LLM call you wire; every graph builds on it"* — because L04 and L05 both depend on it and neither can be dropped without breaking what follows.

## Prerequisites

Students arriving at L03 should already be able to:

- Send a chat completion and reason about tokens, context window, temperature, and per-call cost (L01) — a node's body is still just an API call; nothing about that changes.
- Construct a prompt with roles and request **structured output** by prompt instruction, then parse it defensively (L02, Subgoal 2) — L03's node body is essentially "the L02 structured-output pattern, now living inside a framework-managed function" rather than a standalone script.
- Read and write basic typed Python — functions with type-annotated parameters and return values, and simple typed containers (`dict`, `TypedDict`-shaped data) — general programming prerequisite, not lesson-specific.

L03 does **not** prerequisite anything from L04 onward. In particular, it does not assume:

- Multiple nodes, edges, or any notion of "wiring things together" — that is L04's job, introduced here only as a one-line forward pointer.
- Tool calling — that's L07; the node in this lesson only ever calls the model directly, never a tool.
- The agent loop or any cyclic control flow — that's L10 (hand-rolled) and L11 (LangGraph); nothing in L03 loops.
- Real trace tooling — Langfuse arrives at L12. If students want to "watch the node run," this lesson uses LangGraph's own built-in invoke/stream output, not a tracing platform.
- Any mixed-model decision framework — that's L14. If a cheap-vs-capable model contrast comes up at all in this lesson, it is a single forward-pointing sentence, not a taught idea.

## Learning objectives

By the end of L03, a student should be able to:

1. **Wrap a single LLM call as a reusable, typed node with explicit input/output state.** Concretely:
   - Define a typed **state** schema for a small graph — a `TypedDict` (or annotated state, matching the repo's typed style) with a handful of fields, e.g. an input field (`raw_text: str`) and an output field the node will populate (`summary: str`).
   - Write a **node** as a plain typed function: it takes the state (or the relevant slice of it) as input, calls `ChatAnthropic` once to do one unit of work, and **returns a state update** — a `dict` containing only the fields it changed, not the whole state object back.
   - Pick **one** running example task for the node's single job — classify, extract, summarize, or draft (pick one, consistently, for the whole lesson) — and implement it as a focused, single-purpose prompt, reusing L02's structured-output discipline (ask for a shape, parse defensively) so the state update is well-typed rather than a raw string.
   - Explain why the function signature (state in, state-update out) is exactly what makes the node **reusable**: it doesn't know or care what called it or what will read its output next — that decoupling is what lets L04 wire several of these into a sequence without changing any node's internals.

2. **Treat a node as a pure function over shared state (state in → state out).** Concretely:
   - Articulate the **purity contract** a node should honor: given the same relevant slice of state, it should do the same unit of work and return the same *shape* of update — no hidden reads from outside state, no side effects beyond the LLM call itself. (The LLM call itself is non-deterministic at the token level — that's fine; the *contract* is about what the function reads and returns, not about the model's sampling.)
   - Distinguish what belongs **inside** a node's function body (the prompt, the parsing logic, the one LLM call) from what belongs **outside** it (the model client construction, configuration, the graph wiring itself) — dependencies are set up once, at build time; state is what flows through at run time.
   - Contrast this with an ordinary Python function calling the model directly (as in L01–L02): the *node* version is the same underlying call, wrapped so a future orchestrator (L04) can plug it into a graph without rewriting it. Land the point that "pure function over state" is a discipline worth having even before there's a second node to wire it to.

3. **Run and inspect one node in isolation.** Concretely:
   - Use LangGraph's `StateGraph` builder at its smallest: declare the state schema, `add_node` for the single node, `set_entry_point`, wire the node straight to `END`, and `compile()` the graph into a runnable.
   - `invoke()` the compiled graph on a sample input and inspect the returned state — confirm the output field the node was supposed to populate is present and well-formed, and that the input field is still there unchanged.
   - Use LangGraph's own **built-in run/stream output** (not a tracing platform) to watch the single node execute — e.g. `stream()` and observe the one step fire. Name explicitly that *real* trace tooling — reading a full run as a structured trace, comparing runs, diagnosing failures from a trace alone — is [L12](../L12/objectives.md)'s job; this lesson only needs "did my one node run, and what did it return."
   - Recognize that running a **one-node graph** through `StateGraph` is deliberately more ceremony than just calling the function directly — and be able to say *why* it's still worth it: the ceremony (typed state, compile, invoke) is the same shape L04 will reuse for five nodes, ten nodes, a whole workflow. Paying the setup cost once, on the simplest possible graph, is the pedagogical point.

4. **Understand *why* an explicit step is the unit you orchestrate.** Concretely:
   - Explain the core framing this lesson exists to install: once a piece of work is wrapped as a node — typed input, typed output, no hidden dependencies — it becomes something you can **compose**, **reorder**, **test in isolation**, and **swap out**, in ways a same-file sequence of function calls resists. This is *why* the course reaches for the node/graph abstraction instead of just writing more Python.
   - Contrast an **explicit node** with the alternative a student might reach for instead: one long function (or notebook cell) that does several things in a row with intermediate variables. Name the concrete costs of the long-function version — harder to test one step alone, harder to swap a step's model or prompt without touching neighbors, harder to see the shape of the pipeline at a glance — and the concrete benefit a node buys back.
   - State plainly, as a forward pointer and not a taught mechanism, that **L04 is exactly this idea multiplied**: the same typed-state-in/typed-state-out node design, several of them, wired with fixed edges into a sequence. A student who understands *one* node's contract already understands *most* of what L04 needs — L04 is mostly wiring, not new node design.

## What a single-node graph is (vocabulary the lecture must establish)

Define these explicitly and reuse them verbatim into L04 (L04's own vocabulary list matches these terms):

- **Graph** — a task expressed as nodes connected by edges, compiled into a runnable. L03 builds the smallest possible graph: one node, no edges between nodes (just entry → node → `END`).
- **Node** — a unit of work: a typed function that reads state and returns a state update. In L03 there is exactly one; it may call the model (`ChatAnthropic`) internally.
- **State** — the shared, typed object passed into a node and updated by its return value. In L03, a small schema with an input field and an output field.
- **Entry point / `END`** — where execution starts and the sentinel where it stops. In a one-node graph, entry point and the node coincide, and the node's only edge goes to `END`.
- **Compile / invoke** — turning the declared graph (nodes + edges) into a runnable (`compile()`), then running it on an input (`invoke()`).
- **Pure function over state** — the discipline a node should follow: same relevant state in, same shape of update out, no hidden reads or side effects beyond its one LLM call.

Terms deliberately **not** introduced here (L04's vocabulary, not L03's): **edge** (a fixed transition *between* nodes — L03 has no such transition, only entry→node→END), **conditional edge**, **reducer** (merging *multiple* nodes' updates), **DAG** (the term implies more than one node).

## Main points the lecture should land

- **A node is one LLM call you *wire*.** Everything else in this lesson — the state schema, the `StateGraph` ceremony, compile/invoke — exists to make that one call *reusable and inspectable* rather than a one-off function call. Say this sentence more than once.
- **State goes in, state comes out.** The node doesn't return "the answer" — it returns an *update to shared state*. This is a small shift in mental model from L01–L02 (where the model's response was the thing students worked with directly) and it's the shift that makes L04's multi-node wiring possible without redesigning anything.
- **This is the first framework lesson.** Up to now, every model call went through the repo's own `potato_llm` seam. Inside a LangGraph node, the call goes through LangChain's `ChatAnthropic` instead. Name it as a deliberate departure — *"the framework brings its own client"* — not a silent swap the student is meant to not notice.
- **One node is more ceremony than just calling a function — and that's the point.** A single-node `StateGraph` is objectively more setup than `result = call_model(prompt)`. The payoff isn't visible yet at one node; it shows up at L04 when the *same* ceremony scales to many nodes without per-node redesign. Tell students the payoff is coming, not yet arrived.
- **A node's job is narrow on purpose.** One node does one unit of work — classify, or extract, or summarize, or draft, not several. Chaining narrow steps together is L04's entire subject; L03 just makes sure students can build *one* narrow step cleanly first.
- **This is not yet an agent, and not yet a workflow with more than one step.** There's no tool call, no loop, no second node, no branching. Everything beyond "one wired step" is later lessons' job — L03's restraint here is deliberate, matching L02's "narrow on purpose" framing of foundational lessons.

## Common student confusions to watch for

- *"Why not just call `ChatAnthropic` directly instead of all this `StateGraph` setup?"* For one node, that instinct is basically correct — the ceremony doesn't pay for itself yet. The answer is explicitly a forward pointer: *"you're paying setup cost now so L04 doesn't have to redesign anything when it adds a second, third, and fourth node."* Don't pretend the one-node case is obviously worth it; be honest that the payoff is coming.
- *"A node returns the final answer."* No — a node returns a **state update** (a dict of the fields it changed), which LangGraph merges into the shared state. The distinction matters the moment there's more than one node (L04), so it's worth being precise about it even at one node.
- *"This is basically the same thing as calling `potato_llm` from L01–L02."* The underlying API call is the same shape; the *client* is different (native `ChatAnthropic`, not the course's own seam) and the *wrapping* is different (a typed function LangGraph can invoke, not a bare script). Both things changed — call out both.
- *"A `StateGraph` with one node is already an agent."* No. Nothing here loops, and nothing here lets the model choose what happens next — there isn't a "next" yet. Agency is introduced at L11 with a back-edge that lets the *model* decide to keep going; L03 has no edges to speak of.
- *"State is just a fancy dictionary, why not use a regular dict / global variable?"* State's typed shape is what lets a future node (L04) know exactly what it can read and must return, without reading this node's source code. A plain dict or a global loses that contract — it's discoverable only by inspection, not by type.
- *"I need to see this node's trace / spans to know it worked."* Not yet — full trace tooling is L12. For one node, `invoke()`'s return value and LangGraph's own stream output are enough to answer "did it run, and what came back."

## Bridge to L04

[L04 (Directed graphs — sequential chaining)](../L04/objectives.md) is the direct sequel and reuses **everything** from this lesson without changing it: the same typed-state idea, the same node-as-pure-function contract, the same `StateGraph`/compile/invoke mechanics, the same native `ChatAnthropic` client. The only thing L04 adds is **more than one node, wired together with fixed edges** — turning "one wired step" into "several wired steps in sequence." A student who leaves L03 able to write one clean node has already done most of the conceptual work L04 needs; L04 is primarily about *wiring*, not about redesigning what a node is.

The single sentence to leave students with at the end of L03: *"You just wired one step — next lesson, you wire several of them together."*

## Open authoring questions

- <!-- *NEED INPUT*: pick the single running-example task for L03's one node — classify, extract, summarize, or draft — and confirm it's a *different* domain/example than L04's support-ticket running example, or deliberately the same domain so L04 can literally lift L03's node into a longer chain. Leaving this open lets stage 2 decide based on what reads best as a live demo. -->
- <!-- *NEED INPUT*: estimated lecture duration — best guess 40–55 minutes given the deliberately narrow scope (one state schema, one node, compile/invoke, inspect output). Shorter than L02 and L04; confirm this fits the course's per-lesson time budget. -->
- <!-- *NEED INPUT*: should L03 show LangGraph's `get_graph().draw_mermaid_png()` diagram render for a one-node graph (as L04 plans to do for its multi-node graphs), or is a one-node diagram too trivial to be worth the setup? If shown, it should be a light preview of a beat L04 does for real. -->
- <!-- *NEED INPUT*: confirm exact model id string for the Sonnet 4.6 snapshot used by `ChatAnthropic`, read from `common/config.py` rather than hard-coded in cells — mirrors the same open question L04 left for its own model ids. -->
- <!-- *NEED INPUT*: should this lesson's node use Sonnet 4.6 only (matching the course anchor and keeping the model constant so "one node" is the only variable), or is a brief, non-taught Haiku 4.5 aside worth including as a preview of L04's per-node model mixing? Current draft assumes Sonnet-only to avoid pulling L14/L04 content forward. -->
