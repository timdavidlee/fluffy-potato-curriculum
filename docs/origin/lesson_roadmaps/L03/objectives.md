# L03: Directed graphs — from one node to a sequential chain (LangGraph workflows)

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (lesson-plan row L03).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).
> Preceding lesson: [L02 Prompting fundamentals](../L02/objectives.md) — roles, structured output, few-shot. Following lesson: [L05 Conditional graphs — routing & branching](../L05/objectives.md) — adds a *conditional* edge (routing) on top of the sequential chain built here.

> **Merged lesson (2026-07-09).** This lesson is the union of the former **L03 "Single-node operations"** and **L04 "Directed graphs: sequential chaining."** The two were split during the 2026-07-02 reorder, but single-node-in-isolation proved too thin to stand alone: its whole payload was one idea — *"a node is one LLM call you wire"* — whose payoff (wiring several) only arrives with a second node. Merging puts that payoff in the same lesson: **build one node, then immediately wire several into a chain.** The old L03's standalone "why wire a node at all?" justification beat is dropped — the chain *is* the justification. **The `L04` slot is now a reserved gap** (no cascade-renumber of L05+); conditional graphs remain **[L05](../L05/objectives.md)**, the source of truth for routing.

## Where this lesson sits

L03 is the course's **first graph lesson** and **first framework lesson**. [L01](../L01/objectives.md) and [L02](../L02/objectives.md) taught students to reason about tokens, cost, roles, and structured output while talking to the model through the repo's own [`potato_llm`](../../../src/fluffy_potato_curriculum/potato_llm/CLAUDE.md) seam — a hand-rolled client built for the course. L03 is where that changes: students meet **LangGraph**, and inside a LangGraph node they call the model through the **native LangChain `ChatAnthropic` client**, not `potato_llm`. Name this departure out loud — *"frameworks bring their own client abstraction; this is the first of several you'll meet."* `langgraph` and `langchain-anthropic` are already project dependencies (added via `uv add`), so no install happens live.

The lesson has two movements:

- **One node.** The smallest possible unit of a graph — one typed state, one node, wired straight to `END`. A student should be able to say, in one sentence, *"a node is one LLM call you wire — state goes in, state comes out."*
- **Several nodes.** Immediately, that same node design is **multiplied**: wire several nodes into a fixed **directed acyclic graph (DAG)** — a **sequential prompt-chaining workflow** (e.g. *parse → draft → policy-check*) where *you* wire the path and the model never decides what runs next.

The framing the second movement installs is the industry's **workflow vs. agent** distinction (as in Anthropic's *Building Effective Agents*): a **workflow** runs through predefined code paths the developer laid out; an **agent** lets the *model* direct its own process. LangGraph expresses **both**. This contrast **opens here** (you wire the flow) and **closes at [L11 Shallow agents](../L11/objectives.md)**, which adds the one thing that turns a workflow into an agent: a **cycle** plus model-driven control. [L05](../L05/objectives.md) sits between them, adding a *conditional* edge (routing) that is still developer-owned.

The throughline the PRD names: **"you wire the graph (L03, L05); the model drives the loop (from L10)."** Together **L03 and L05 install the graph/workflow model using plain LLM calls only** — no tools yet (tools arrive at [L07](../L07/objectives.md)) and no agent loop yet (hand-rolled at [L10](../L10/objectives.md), as LangGraph at [L11](../L11/objectives.md)).

This is where the course **first reaches for a framework** and its own model client. The **tool-calling lessons (L07–L08) keep that same client** — they bind tools to it with `bind_tools` and read the model's `AIMessage.tool_calls` — so the "which client, and why" story is **monotonic**: the `potato_llm` seam carries the prompt-only lessons (through L02), then the framework client takes over from L03 onward. Name that single switch-over point explicitly.

L03 is kept in the mini course cut (see [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md), "Condensed Mini Lesson Plan") — the orchestration unit and the first workflow, on which L05 and the whole agent arc build.

## Prerequisites

Students arriving at L03 should already be able to:

- Send a chat completion and reason about tokens, context window, temperature, and per-call cost (L01) — a node's body is still just an API call, and a prompt-chaining workflow makes *several* such calls in sequence (the per-step cost is what the "why decompose?" discussion weighs).
- Construct a prompt with roles and request **structured output** by prompt instruction, then parse it defensively (L02, Subgoal 2) — a node's body is essentially "the L02 structured-output pattern, now living inside a framework-managed function," and a chain step often returns structured data the next step consumes.
- Read and write basic typed Python — functions with type-annotated parameters and return values, simple typed containers (`dict`, `TypedDict`-shaped data), and basic control flow — general programming prerequisite, not lesson-specific.

L03 does **not** prerequisite anything from L05 onward. In particular, it does not assume:

- **Conditional edges / routing / branching** — that is [L05](../L05/objectives.md)'s job; L03's graph is strictly acyclic and every edge is fixed (`A → B`, always). Routing appears here only as a one-line forward pointer.
- **Tool calling** — that's L07; nodes here only ever call the model directly, never a tool.
- **The agent loop or any cyclic control flow** — that's L10 (the cyclic ReAct graph) and L11 (the prebuilt shallow agent); nothing in L03 loops.
- **Real trace tooling** — Langfuse arrives at L12. To "watch a graph run," this lesson uses LangGraph's own built-in `stream(stream_mode="updates")`, not a tracing platform.
- **A mixed-model *decision* framework** — that's L14. L03 demonstrates the *mechanism* of per-node model binding (a cheap model on a light node, a capable model on a heavy one) with a light cost/latency aside; *which* model each step deserves is L14's topic.

## Learning objectives

By the end of L03, a student should be able to:

1. **Wrap a single LLM call as a reusable, typed node — a pure function over shared state.** Concretely:
   - Define a typed **state** schema for a small graph — a `TypedDict` (or annotated state, matching the repo's typed style) with a handful of fields, e.g. an input field (`raw_text: str`) and an output field the node populates (`extracted_fields: dict`).
   - Write a **node** as a plain typed function: it takes the state (or the relevant slice) as input, calls `ChatAnthropic` once to do one unit of work, and **returns a state update** — a `dict` containing only the fields it changed, not the whole state object back. Reuse L02's structured-output discipline (ask for a shape, parse defensively) so the update is well-typed rather than a raw string.
   - Articulate the **purity contract**: given the same relevant slice of state, the node does the same unit of work and returns the same *shape* of update — no hidden reads from outside state, no side effects beyond the LLM call. (The model's sampling is non-deterministic at the token level — that's fine; the *contract* is about what the function reads and returns.)
   - Explain why the signature (state in, state-update out) is exactly what makes the node **reusable**: it doesn't know or care what called it or what reads its output next — that decoupling is what lets the *next* movement wire several of these into a sequence without changing any node's internals. Distinguish what belongs **inside** a node (prompt, parsing, the one LLM call) from what belongs **outside** it (client construction, configuration, the graph wiring) — dependencies are set up once at build time; state flows through at run time.

2. **Run and inspect one node in isolation.** Concretely:
   - Use LangGraph's `StateGraph` builder at its smallest: declare the state schema, `add_node` for the single node, `set_entry_point`, wire the node straight to `END`, and `compile()` into a runnable.
   - `invoke()` the compiled graph on a sample input and inspect the returned state — confirm the output field is present and well-formed, and the input field is still there unchanged. Land that `invoke()` returns the **whole state** (input intact, output populated), not "just the answer."
   - Use LangGraph's **built-in run/stream output** (not a tracing platform) to watch the single node execute — `graph.stream(input, stream_mode="updates")`, which yields one chunk per node (`{node_name: state_update}`). This is the **same call, in the same `stream_mode`, that the rest of the lesson and course reuse** — to watch a chain fire in sequence (next movement), a branch (L05), the agent loop (L10). Name explicitly that *real* trace tooling is [L12](../L12/objectives.md)'s job; here you only need "did my node run, and what did it return."
   - Recognize that a one-node `StateGraph` is deliberately more ceremony than calling the function directly — and be honest that at one node it does **not** obviously pay for itself. The payoff is not a promise to take on faith: it arrives in the *very next section* of this same lesson, when the identical ceremony scales to several nodes with no per-node redesign.

3. **Wire several nodes into a directed acyclic graph with fixed edges and shared state.** Concretely:
   - Take the one node from objective 1 and add more: use the `StateGraph` builder to `add_node` several times, wire **fixed edges** (`add_edge("parse", "draft")`, taken every time), set the entry point, and `compile`/`invoke`. The typed state now threads through *every* node.
   - Define **edge** (a fixed transition between two nodes) and **DAG** (a graph with no back-edges — every edge moves forward to `END`). State that the absence of a back-edge is exactly what makes this a *workflow*, not an agent.
   - Explain how a node **returns an update** that LangGraph merges into state via per-field **reducers** — the default reducer **overwrites**; an `Annotated[list, add]` field **appends**. You didn't need a reducer at one node (nothing to merge); this is where it first matters. This is the *same* state/reducer machinery L11 reuses for an agent's message history — learned first on a simpler acyclic graph.
   - Articulate *why a graph instead of a function that calls things in order*: the graph makes control flow **inspectable data** (nodes and edges you can list, visualize, stream) rather than imperative statements buried in Python. Name the honest trade — for a strictly linear chain the graph is near break-even; its value shows with branching (L05), visualization, shared state, and tracing (L12).

4. **Build a deterministic prompt-chaining workflow where the developer controls the path.** Concretely:
   - Build a **prompt-chaining** workflow: a fixed sequence of nodes where each step's output feeds the next (e.g. *parse a support ticket → draft a reply → check the reply against a policy*), each node a separate model call with a focused prompt. Explain *why decompose* — smaller focused prompts are more reliable and individually testable than one mega-prompt, at the cost of more calls (the L01 cost trade).
   - **Bind a different model per node.** Because each node is its *own* independent model call, each can construct its own `ChatAnthropic(model=...)` — a **cheap, fast model** (Claude **Haiku 4.5**) for the light steps (parse/extract) and a **capable model** (Claude **Sonnet 4.6**) for the heavy reasoning steps (draft/analyze). Inspect the `stream(stream_mode="updates")` output to see which model ran where. This is the **mechanism** of mixed-model design; *which* model each step deserves (capability/latency/cost, budgets) is **L14's** topic — L03 just makes concrete that a graph lets you mix models per node.
   - Keep the graph **acyclic** — every edge moves forward; no edge returns to an earlier node.
   - Run the workflow and **watch it run** with `graph.stream(stream_mode="updates")` — a straight sequence of node updates confirming the path was developer-determined. Render the compiled graph's diagram once so "control flow as data" is literally visible. (Routing this same run to the shared **Langfuse** instance for a structured trace is **L12** — forward-reference it, don't depend on it here.)
   - *Optionally* carry the L13 eval discipline forward: a deterministic workflow is the *easiest* thing to evaluate (same input → same path), so a tiny eval set over one node of the chain reusing `common/evals.py` reinforces "evaluate everything you build."

5. **Contrast a workflow (you wire the flow) with an agent (the model drives the flow).** Concretely:
   - State the distinction crisply and reuse it verbatim into L11: a **workflow** is a graph whose path is fixed or chosen by *developer logic* (acyclic, predictable, the model lives inside nodes); an **agent** is a graph whose path is chosen by the *model*, typically via a **cycle** that loops model → tools → model until the model stops (L10's ReAct graph, L11's prebuilt shallow agent).
   - Reason about *when to use which*: prefer a **workflow** when the task has a known shape — predictable, cheaper, lower-latency, far easier to test and trace; reach for an **agent** only when the steps can't be known in advance. Name the common failure mode: reaching for an agent when a workflow would do (more cost, less predictability, harder to debug).
   - Point forward precisely: **[L05](../L05/objectives.md)** keeps everything from this lesson and adds exactly one primitive — a **conditional edge** whose routing function reads state *you* control (a computed value, a model *label*, or user input); it is still a workflow. **L11** adds the one thing that makes an agent — a conditional edge that **loops back to the model**, handing the model control of the path. That single back-edge is the line between a workflow and an agent.

## What this lesson's graphs are (vocabulary the lecture must establish)

Define these explicitly and reuse them verbatim into L05 and L11 (their vocabulary lists match):

- **Graph** — a task expressed as nodes connected by edges, compiled into a runnable. The framework's structured replacement for imperative control flow. This lesson starts at the smallest possible graph (one node, no edges *between* nodes) and grows to a several-node chain.
- **Node** — a unit of work: a typed function that reads state and returns a state update. May call the model (`ChatAnthropic`) internally — and **each node may bind its own model** (a cheap model for light steps, a capable model for heavy ones), since each node is an independent call.
- **State** — the shared, typed object passed into each node and updated by its return value; carries the data that flows between steps.
- **Entry point / `END`** — where execution starts and the sentinel where it stops.
- **Compile / invoke** — turning the declared graph (nodes + edges) into a runnable (`compile()`), then running it on an input (`invoke()`). Two separate steps.
- **Pure function over state** — the discipline a node follows: same relevant state in, same shape of update out, no hidden reads or side effects beyond its one LLM call.
- **Edge** — a fixed transition between two nodes (`A → B`, always). (Appears once there is more than one node.)
- **Reducer** — the rule that merges a node's returned update into state per field (overwrite, or append for accumulating fields). Same mechanism L11 reuses for message history. First matters once several nodes write state.
- **DAG (directed acyclic graph)** — a graph with no back-edges: every path moves forward to `END`. The defining shape of a *workflow*.
- **Prompt chaining** — a fixed chain of nodes where each step's output feeds the next.
- **Workflow vs. agent** — workflow = developer wires the (acyclic) path; agent = the model drives the (cyclic) path. The lesson's headline contrast.

Terms deliberately **not** introduced here — they are L05's: **conditional edge** (a routing function chosen at runtime) and the deciders that can feed one (a model label, direct user input). L03's graph is fixed and acyclic throughout.

## Main points the lecture should land

- **A node is one LLM call you *wire*.** The state schema, the `StateGraph` ceremony, compile/invoke — all of it exists to make one call *reusable and inspectable* rather than a one-off. Say this sentence more than once.
- **State goes in, state comes out.** A node doesn't return "the answer" — it returns an *update to shared state*, which LangGraph merges back in. This small shift from L01–L02 is exactly what makes multi-node wiring possible without redesigning anything.
- **One node is more ceremony than a plain function — and the payoff arrives on the next slide, not on faith.** At one node the `StateGraph` setup genuinely isn't worth it; say so plainly. Then *show* the payoff in the same lesson by wiring a second and third node with zero redesign of the first. (This is why the lesson no longer needs a standalone "why bother?" argument — the chain is the argument.)
- **LangGraph is not just for agents.** A graph can be a plain deterministic **workflow** — no agency required. Introducing graphs this way separates "learn the framework's primitives" from "let the model drive," which is two hard ideas, not one.
- **In a workflow, the model lives *inside* the nodes; the developer owns the edges.** The model does the smart per-step work (parse, draft); *what runs next* is decided by code. In an agent (L11), the model owns the edges too. Say this contrast early and often.
- **This is the first framework lesson.** The client switches from `potato_llm` to LangChain's `ChatAnthropic` inside nodes. Name it as a deliberate departure, not a silent swap.
- **A graph turns control flow into inspectable data.** Nodes and edges can be listed, drawn, streamed — unlike `if`/`while` buried in Python. Near break-even for one linear chain; it pays off with branching, visualization, shared state, and tracing.
- **Determinism is a feature.** A workflow takes the same path on the same input: predictable, cheaper, lower-latency, and trivially testable (which is why the L13 eval discipline fits it so neatly). Most production "AI features" are workflows, not agents.
- **Each node can use its own model.** A node is an independent call, so a graph can mix models — Haiku for light steps, Sonnet for reasoning. This is the *mechanism*; the *when/why* is L14's.
- **The workflow→agent line is a single back-edge.** Everything built here carries into L05 and L11 unchanged; L05 adds a developer-owned conditional edge, L11 adds a model-owned cycle. Framing it this way makes each next lesson one small step, not a new world.

## Common student confusions to watch for

- *"Why not just call `ChatAnthropic` directly instead of all this `StateGraph` setup?"* At one node, that instinct is basically correct — the ceremony doesn't pay for itself yet. But the answer isn't a distant promise anymore: it's the next section, where the same setup takes a second and third node for free. Don't pretend one node is obviously worth it; show the payoff instead of asserting it.
- *"A node returns the final answer."* No — a node returns a **state update** (a dict of the fields it changed), which LangGraph merges into shared state. The distinction matters the moment there's more than one node.
- *"This is basically the same as calling `potato_llm` from L01–L02."* The underlying API call is the same shape; the *client* is different (native `ChatAnthropic`) and the *wrapping* is different (a typed function LangGraph invokes). Both changed — call out both.
- *"A LangGraph graph is an agent."* No — a graph is a wired set of nodes. It's an **agent** only when the **model** drives the path (usually via a loop). L03's graphs are workflows: the developer drives the path.
- *"State is just a fancy dictionary — why not a plain dict / global?"* The typed shape is the contract a *downstream* node reads without opening this node's source. A plain dict or global loses that contract — discoverable only by inspection, not by type.
- *"Decomposing into multiple prompts is wasteful — one big prompt is cheaper."* Sometimes cheaper in tokens, usually worse in reliability and much harder to test or fix. Chaining trades some cost for focused, individually-verifiable steps.
- *"My workflow needs a loop."* If it genuinely needs the model to keep going until *it* decides to stop, that's an agent (L11) — don't force a cycle into a workflow. Branching on developer-owned state is L05, and it's still a workflow.
- *"I need to see this node's trace / spans to know it worked."* Not yet — full trace tooling is L12. For this lesson, `invoke()`'s return value and the `stream` output answer "did it run, and what came back."

## Bridge to L05 (and on to L11)

[L05 (Conditional graphs — routing & branching)](../L05/objectives.md) is the direct sequel and reuses **everything** from this lesson unchanged — the typed-state idea, the node-as-pure-function contract, the `StateGraph`/compile/invoke mechanics, fixed edges, reducers, the `stream` run-inspection, and the native `ChatAnthropic` client. L05 adds exactly one primitive: a **conditional edge** whose routing function reads state *you* control (a computed value, a model classification *label*, or direct user input) and returns the name of the next node. The path is still developer-owned — L05 is still a workflow.

The agent arc (L10 hand-rolled, L11 as a prebuilt `create_agent`) then reuses these same primitives and makes one more change: a conditional edge that **loops back to the model**, converting the acyclic **workflow** into the cyclic, model-driven **agent**. That single back-edge is the line between this lesson's world and the agent's.

Per the project decision, **L11 keeps its own self-contained primitives intro** rather than depending on this lesson — so a student who only takes the agent lesson still gets nodes/edges/state from scratch. The intentional overlap reads as reinforcement: L05 and L11 agree on the vocabulary above verbatim, and L11's intro explicitly calls back to this lesson's workflow-vs-agent framing ("you saw the acyclic version earlier; here's the cycle").

The single sentence to leave students with at the end of L03: *"You wired several steps into a fixed chain — next lesson, one of those edges gets to choose."*

## Open authoring questions

- <!-- *NEED INPUT*: confirm the running example is a **support-ticket** domain end-to-end — the single node built first is a `parse`/extract step over a ticket, which then becomes step 1 of the *parse → draft → policy-check* chain. This continuity is the whole reason the merge reads as one lesson; keep it. -->
- <!-- *NEED INPUT*: exact model id strings for the Sonnet 4.6 and Haiku 4.5 snapshots, read from common/config.py rather than hard-coded in cells. The single-node movement uses Sonnet only (keep the model constant while "the node" is the new idea); per-node Haiku/Sonnet mixing is introduced only in the chaining movement. -->
- <!-- *NEED INPUT*: merged lecture duration — the single-node movement (~35–42 min of demo/primer) plus the chaining movement (~30–45 min) is a full ~2 h lesson. Confirm the trim targets in stage 2 keep it to ~2 h rather than a firehose; the written chaining lecture must not re-derive the StateGraph/single-node basics the build-one-node demo now owns. -->
- <!-- *NEED INPUT*: include the optional eval-the-workflow beat in the lecture or hold it for the lab? Recommendation: short optional closer — reinforces L13 cheaply and sets up L05's router eval. -->
