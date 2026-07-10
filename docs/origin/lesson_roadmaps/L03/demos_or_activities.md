# L03: Teacher-led demos — Directed graphs: from one node to a sequential chain

> Sibling docs: [objectives.md](objectives.md) (what the lesson aims for), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md).
>
> **Audience for this file:** the teacher running L03. Every demo below is *teacher-driven, no student participation*. Student-driven exercises live in the L03 lab (separate file, stage 2).
>
> **Anchor model:** the **single-node movement** (primer + Demos 1–2) uses **Claude Sonnet 4.6, and only Sonnet** — keep the model constant so the *node* is the only new variable. The **chaining movement** (Demos 3–4) deliberately **mixes models per node** — **Haiku 4.5** for light nodes (parse/extract), **Sonnet 4.6** for heavy nodes (draft/policy-check) — because per-node binding is one of the chaining objectives, not an accident. **This is the course's first framework lesson:** nodes call the **native LangChain `ChatAnthropic`** client directly, *not* the hand-rolled `potato_llm` seam from L01–L02. Call that departure out loud — it's the single switch-over point.
>
> **Merged lesson (2026-07-09):** this file is the union of the former L03 (single-node) and L04 (sequential-chaining) demo scripts. The old L03 "Demo 3 — why wire a node at all?" is **dropped** — the chaining movement *is* the answer, so there is no standalone justification beat. Routing / conditional edges / user-input branching remain **[L05](../L05/demos_or_activities.md)**'s.

## How to read this file

Each demo is a self-contained block with:

- **Goal** — the single insight the demo should land. Tied to a learning objective from [objectives.md](objectives.md).
- **Pre-flight** — what the teacher needs loaded before class.
- **Live script** — the order of operations during the demo. Treat it as a checklist, not a teleprompter.
- **What to highlight** — the moment(s) where the teacher should slow down and say the takeaway out loud.
- **If the demo misbehaves** — graceful fallback for when the model surprises you (it will).

The lesson runs in **two movements**. A short **framework primer** (a read/run-alone student notebook) precedes everything. Then **Movement 1 — one node** (Demos 1–2): wrap a single LLM call as a typed node, then compile/invoke/inspect it in isolation. Then **Movement 2 — several nodes** (Demos 3–4): wire that *same* node into a fixed chain, and name the workflow-vs-agent line. They build on each other continuously — **Demo 3's chain reuses Demo 1's node unchanged as its first step** (`parse`), so the room literally watches one node become a pipeline. Run them in order.

> **The spine of L03.** Movement 1: *"a node is one LLM call you wire — state goes in, state comes out."* Movement 2: *"several nodes, wired in a fixed order, is a workflow you can inspect as data — you own the edges; the model lives inside the nodes."* The bridge sentence to leave students with: *"you wired several steps into a fixed chain — next lesson, one of those edges gets to choose."* The single-node movement is honest that at one node the ceremony doesn't pay off — and then pays it off in the same lesson by wiring the chain. Do **not** relitigate "why bother with a node" as its own beat; the chain is the answer.

## Pre-flight (once, at the top of the lesson)

The teacher should have, before the first demo starts:

- **LangGraph + the native LangChain Claude client ready.** `from langgraph.graph import StateGraph, END` and `from langchain_anthropic import ChatAnthropic`. Both `langgraph` and `langchain-anthropic` are already project dependencies (added via `uv add`); no install during class. The API key still loads through `common/config.py` (`ChatAnthropic` reads `ANTHROPIC_API_KEY` from the same environment the config seam populates) — key handling is unchanged, only the *client* is the framework's now.
- **Model clients constructed and named.** For Movement 1: one client, `sonnet = ChatAnthropic(model="claude-sonnet-4-6-...")` — keep it that simple. For Movement 2, add `haiku = ChatAnthropic(model="claude-haiku-4-5-...")` for the light nodes; each node uses its own — that *is* the per-node-binding beat. <!-- *NEED INPUT*: confirm exact model id strings for the Sonnet 4.6 and Haiku 4.5 snapshots, read from common/config.py rather than hard-coded in cells. -->
- **A small support-ticket dataset** for the running example (the decided domain). A handful of sample tickets for the `parse`/extract node, plus a short **policy snippet** the policy-check node checks a drafted reply against. <!-- *NEED INPUT*: confirm the exact sample tickets and the policy text — recommend 2–3 tickets and a 4–5 line refund/escalation policy. Stage 2 ships these as a small fixture. -->
- **A graph-diagram renderer ready** for Movement 2 — LangGraph's `compiled_graph.get_graph().draw_mermaid_png()` (or the Mermaid text) — so "control flow as data" is *literally visible*. <!-- *NEED INPUT*: confirm the diagram render path works in the demo environment; the Mermaid-text / ASCII fallback is fine if the PNG path is awkward live. -->
- **The one-node graph and the completed chain definitions in a sibling file** to paste if live-coding falls behind.
- LangGraph's own run/stream output ready to call (`stream(stream_mode="updates")` on the compiled graph) — **not** Langfuse. Real trace tooling is [L12](../L12/objectives.md); name it as a forward pointer, don't reach for it.
- **`common/evals.py` importable** for the optional eval-the-workflow beat (the L13 harness — reused, not rebuilt).

> Why one running example, grown from one node to a chain: the pedagogical job of Movement 1 is to make "what is a node" land cleanly; Movement 2 then shows the payoff *on the same node* by wiring it into a pipeline. Keeping the domain constant (support tickets throughout) means Movement 2 never spends attention on a fresh example — it spends it on the *wiring*.

## Framework primer — Meet LangChain & LangGraph (before Demo 1)

**Format:** a short **student-facing primer notebook** ([L0302_lecture.ipynb](../../../../src/fluffy_potato_curriculum/lessons/L03/L0302_lecture.ipynb)), read/run before the build demos — not a teacher-driven demo. It isolates *what a framework is* and the minimal **LangChain** surface the demos assume, so Demo 1 can spend its time on the *node*, not on "what is `ChatAnthropic`."

**Goal:** bridge the L02→L03 cliff. Students leave the hand-rolled `potato_llm` seam and meet a framework, a native client, and graph vocabulary all at once; this primer separates "call LangChain's model client" from "wire a LangGraph node" so neither lands cold.

**What it covers (≈12 min):**

1. **Why a framework now?** — from the `potato_llm` seam to a framework's own client abstraction; still just an API call underneath, same key through `common/config.py`.
2. **`ChatAnthropic` live** — build one client, `.invoke()` a plain string, read `.content`.
3. **Messages in, message out** — `SystemMessage`/`HumanMessage` are L02's system/user roles as objects; `.invoke([...])` returns one `AIMessage`.
4. **LangChain vs LangGraph** — the load-bearing distinction: *LangChain talks to the model; LangGraph wires steps.* A node is one LangChain call wrapped so an orchestrator can plug it in.

**What to highlight:**

- **Keep "framework" concrete** — scaffolding for a common job, not magic. The primer's whole job is to make "LangChain vs LangGraph" a clean two-box picture before Demo 1 fuses them inside a node.
- **Reserve "harness."** Say plainly that the model-driven **agent loop** (often called a *harness*) is **L10–L11**, not now — L03 and L05 are **workflows** you wire. Naming the boundary here keeps "harness" from leaking into the graph lessons.

**If it misbehaves:** the two live calls are tiny and gated on a key — with no key set the primer still runs (the calls skip) and the concepts stand on their own; run the calls later when a key is available.

---

## Movement 1 — one node

### Demo 1 — Wrapping one LLM call as a typed node (Objective 1)

**Goal:** take a plain L01/L02-style model call and show, step by step, what changes when it becomes a **node**: a typed state schema appears, the function signature becomes state-in/state-out, and the model client switches from `potato_llm` to native `ChatAnthropic`. Land the **purity contract** — same relevant state in, same shape of update out, no hidden reads or side effects beyond the one LLM call.

**Pre-flight:**

- A short reminder cell showing the L01/L02-style call: a plain function that takes a string, builds a prompt, calls `potato_llm`, and returns a parsed dict. Keep this on screen as the "before."
- The `parse` task's target fields and one sample ticket ready to paste. **This is the node Movement 2 reuses as step 1 of the chain — name it `parse` (or the chain's first node's name) from the start** so the continuity is explicit.

**Live script:**

1. Put the "before" cell on screen: a bare function calling `potato_llm` and returning a dict. Point at it: "this is everything you already know how to do."
2. Live-code the **typed state** schema: a `TypedDict` with an input field (e.g. `raw_text: str`) and the output field the node populates (e.g. `parsed_fields: dict`). Keep it to two or three fields — the smallest state that makes the point.
3. Live-code the **node** as a plain typed function: `def parse_node(state: TicketState) -> dict:`. Inside, build the same structured-output prompt from L02, but call it through **`ChatAnthropic`** instead of `potato_llm`. Say the departure out loud: *"the framework brings its own client — this is the first of a few you'll meet."*
4. Parse the response defensively (the L02 discipline — `json.loads` first, a regex fallback second) and **return a state update**, not the raw response: `return {"parsed_fields": parsed}`. Underline that the function returns *an update*, not "the answer."
5. Put "before" and "after" side by side. Walk the diff: same underlying API call, same structured-output discipline — what changed is the *signature* (state in, state-update out) and the *client* (`ChatAnthropic`, not `potato_llm`).

**What to highlight:**

- **State goes in, state comes out.** The node hands back an *update* to a shared object, not "the answer." A small but real shift in mental model from L01–L02.
- **The purity contract.** Same relevant state in, same *shape* of update out. What's non-deterministic is the model's sampling, not the function's contract — no hidden globals, no side effects, no dependence on call order.
- **This is the first framework lesson.** Name the client swap explicitly: `potato_llm` was the course's own seam; `ChatAnthropic` is LangChain's. Both are still "just an API call" underneath.
- **The node's job is narrow on purpose.** One node does one unit of work — here, parsing/extraction. Chaining several narrow steps is Movement 2.

**If the demo misbehaves:**

- If the structured output comes back malformed, that's a free bonus — run the L02 defensive parser live and show it absorbing the failure.
- If a student asks "why a `TypedDict`, a dict would work" — answer honestly: for *one* node it mostly would; the typed shape is the contract the *next* node (Movement 2, minutes from now) reads without opening this node's source. The payoff is imminent, not hypothetical.

### Demo 2 — Compile, invoke, and inspect one node in isolation (Objective 2)

**Goal:** take Demo 1's node and put it through the smallest possible `StateGraph`: one node, entry point, straight to `END`. Compile, invoke, inspect the returned state. Use LangGraph's own stream output to "watch it run," and name — but do not use — real trace tooling as an L12 forward pointer.

**Pre-flight:**

- Demo 1's `parse_node` function and state schema, already defined and on screen.
- Two or three sample tickets of varying difficulty (one clean, one with a missing/ambiguous field) to invoke against.

**Live script:**

1. Live-code the graph: `builder = StateGraph(TicketState)`, `builder.add_node("parse", parse_node)`, `builder.set_entry_point("parse")`, `builder.add_edge("parse", END)`. Say out loud that there is exactly **one** node and **one** edge, straight to `END` — nothing to wire yet, on purpose.
2. `graph = builder.compile()`. Note this turns the *declaration* into a *runnable* — nothing has executed yet.
3. `graph.invoke({"raw_text": ticket_1})`. Show the returned state: `raw_text` still there unchanged, `parsed_fields` now populated. Point at both — the input survived, the output appeared.
4. Re-run with a harder ticket (missing/ambiguous field). Show the returned state again — reinforce that "state comes out" every time, even when extraction quality varies.
5. Call `graph.stream({"raw_text": ticket_1}, stream_mode="updates")` and watch the single step fire — one chunk, `{"parse": {...}}` (node name → the state update it wrote). Say: *"this is LangGraph's own way to watch a run, one update per node — for one node it's almost overkill, but it's the **same call you'll reuse minutes from now** to watch a whole chain fire in order, then a branch (L05), then the agent loop (L10)."*
6. Forward-pointer, one line, do not demo: *"Later, in L12, you'll route runs like this to a real tracing platform — for now the return value and the stream answer 'did my node run, and what came back.'"*

**What to highlight:**

- **Compile then invoke is two separate steps.** Compiling declares the runnable; invoking runs it on an input.
- **The returned state has both the old and the new.** `invoke()` returns the *whole* state — input intact, output populated. The hands-on version of "state comes out."
- **More ceremony than calling the function — and that's the point, about to pay off.** Be honest: for one node, `graph.invoke(...)` is more setup than `parse_node_plain(ticket_1)`. Don't defend it in the abstract — the very next demo wires a second and third node onto this exact graph with no redesign, and *that's* the payoff.
- **This is not tracing.** `stream()` shows *that* the node ran; it's not the structured, comparable traces L12 will teach.

**If the demo misbehaves:**

- If `stream()`'s single-step output feels anticlimactic (it will), lean in: *"one node, one step — in the next demo this same call shows three steps firing in order, and it looks a lot more interesting."*
- If a student asks to see the graph diagram, it's fine to show it as a curiosity, but a one-node diagram is nearly content-free — the diagram earns its keep in Movement 2.

---

## Movement 2 — several nodes

### Demo 3 — Prompt chaining: wire the node into a workflow (Objectives 3 & 4)

**Goal:** take Demo 1's `parse` node and wire it, unchanged, into a deterministic **prompt-chaining** workflow on `StateGraph` — then land the headline framing: **a graph turns control flow into inspectable data, the model lives inside the nodes, and the developer owns the edges.** An acyclic graph (no back-edge) is exactly what makes this a *workflow*, not an agent. **This demo is the payoff Demos 1–2 promised** — say so.

**Pre-flight:**

- Demo 1's `parse_node` and state schema, already on screen and compiled-in-isolation (Demo 2).
- The support-ticket sample on the slide and a single ticket chosen to run end-to-end.
- The pipeline shape on the board: **parse → draft → policy-check**, a fixed three-node chain — with `parse` circled as "the node you already built."

**Live script:**

1. Sketch the chain on the board: three boxes, two forward arrows, entry and `END`. Name it a **DAG** — every edge moves forward, none returns. Circle `parse`: "we built this in the last two demos; today we add two siblings."
2. **Grow the typed state** to carry the new fields that flow between steps: the parsed fields (already there), the drafted reply, the policy verdict. Introduce the **reducer** idea here — the default overwrites; an `Annotated[list, add]` field appends — and note you didn't need one at a single node.
3. Live-code the two **new nodes** as plain typed functions, each reading state and returning an update, and **bind a model per node**:
   - `draft` — calls **Sonnet** (the heavy reasoning step) to write a reply from the parsed fields.
   - `policy_check` — checks the draft against the policy snippet (a Sonnet call, or a plain Python check).
   - Rebind `parse` to **Haiku** (a light step) — the same node, now with a cheaper model — to make per-node binding concrete.
4. Wire it: `add_node` for `draft` and `policy_check`, `add_edge("parse","draft")`, `add_edge("draft","policy_check")`, `add_edge("policy_check", END)`, keep `set_entry_point("parse")`. **`compile()`**, then **`invoke()`** on the chosen ticket. Emphasize: **`parse_node`'s body did not change** — we only wired around it.
5. **Render the compiled graph diagram** and put it next to the code — "this picture *is* the control flow, as data."
6. Run it with `graph.stream(stream_mode="updates")`: one chunk per node, in order — `{"parse": {...}}` → `{"draft": {...}}` → `{"policy_check": {...}}`. Confirm the path was developer-determined, and point out each node's update reveals which model produced it. (Routing this same run to Langfuse is **L12** — forward-reference it.)

**What to highlight:**

- **This is the payoff.** The `StateGraph` ceremony from Demos 1–2 just scaled to three nodes with *zero* redesign of the first — that is exactly the return on the setup cost that one node couldn't show.
- **Control flow is now data.** Nodes and edges can be listed, drawn, streamed — unlike `if`/`while` in Python. Show the diagram and the `stream` output as proof.
- **The model lives *inside* the nodes; the developer owns the edges.** The model does the smart per-step work; *what runs next* is decided by the edges *you* wired. Repeat this all through Movement 2.
- **Each node can bind its own model.** Haiku on the light `parse` step, Sonnet on the heavy `draft` step — the `stream` output makes it tangible. This is the *mechanism* of mixed-model design; the *decision framework* (capability/latency/cost) is **[L14](../L14/objectives.md)**'s — name the link, don't re-teach it.
- **Why decompose into three prompts instead of one mega-prompt?** Smaller focused prompts are more reliable and individually testable; the cost is more calls (the L01 trade). For a strictly linear chain the graph is near break-even — its bigger payoff shows with branching ([L05](../L05/objectives.md), next), visualization, shared state, and tracing.

**If the demo misbehaves:**

- If live-coding the builder falls behind, paste the completed graph and walk it node by node — but keep the **`stream` run and the diagram**, which is where "workflow" stops being abstract.
- If a node's structured extraction is flaky, tighten its prompt (callback to L02 structured-output) — don't reach for tool calling, which is L11's.
- If the `stream` output doesn't show distinct models per node, check each node constructed its own `ChatAnthropic(model=...)` rather than sharing one — that *is* the per-node-binding lesson surfacing as a bug.

### Demo 4 — Workflow vs. agent: the line is a single back-edge (Objective 5)

**Goal:** open the **workflow-vs-agent** contrast on the fixed chain you just built, and forward-point with precision: **everything here carries forward unchanged; [L05](../L05/objectives.md) adds one primitive (the conditional edge, still developer-owned), and L11 adds the one thing that makes an agent — a conditional edge that loops back to the model.** That single back-edge is the line. Do **not** build a router or an agent here — this demo is diagram + discussion.

**Pre-flight:**

- The compiled prompt-chaining workflow from Demo 3, with its rendered (acyclic) diagram.
- A **sketch** (not a live build) of the L11 shallow-agent shape: an `agent` node, a `tools` node, and a conditional edge out of `agent` that loops back to `tools` or exits.

**Live script:**

1. Put the Demo 3 workflow diagram up: trace the path — `parse → draft → policy_check → END`, every arrow forward, always reaches `END`. Name it: **DAG, acyclic, developer-wired = workflow.**
2. Draw **one new edge** on the L11 sketch: a conditional edge out of the model node that routes *back* into the loop (call a tool) or to `END` (finish). That back-edge hands the *model* control of the path.
3. State the distinction verbatim (it reappears in L05 and L11): a **workflow** is a graph whose path is fixed or chosen by *developer logic* (acyclic, predictable, model inside nodes); an **agent** is a graph whose path is chosen by the *model*, via a **cycle** that loops model → tools → model until the model stops.
4. Place the whole arc on the board so nothing is a surprise later: **L03** = a fixed chain, no branches (this lesson). **[L05](../L05/objectives.md)** = a graph with branches *you* own (a conditional edge whose routing function reads state you control — a computed value, a model *label*, or user input). **L11** = a graph with a branch the *model* owns, wired into a loop. *Same primitives the whole way; the only thing that changes is who decides the path.*
5. Reason about **when to use which**: prefer a **workflow** when the task has a known shape — predictable, cheaper, lower-latency, far easier to test and trace; reach for an **agent** only when the steps can't be known in advance. Name the common failure mode: **reaching for an agent when a workflow would do**.

**What to highlight:**

- **The workflow→agent line is one back-edge — but routing comes first.** L05 and L11 both keep nodes, edges, typed state, reducers, compile/invoke, and `stream` *unchanged*. L05 adds only the conditional edge (still developer-owned); L11 adds only the cycle. This is the whole reason L03 comes first.
- **Determinism is a feature, not a limitation.** Most production "AI features" are workflows, not agents. Choosing the simplest shape that solves the task — usually a workflow — *is* the engineering skill.
- Do **not** build a router or the agent here. Routing is **[L05](../L05/objectives.md)**; the cycle is **L11**. L03 only *names* the back-edge and forward-points.

**If the demo misbehaves:**

- Mostly diagram + discussion, so little can flake. If a student insists "a model *inside* a node is already the model deciding," separate the two: a model doing work *inside* a node is not agency; agency is the model choosing the *path* (the back-edge), and nothing here has one.

## Common pitfalls coda — naming L03's two gotchas

**Shape note:** a short **"common pitfalls" coda**, not a new live demo — Movement 2 already *touches* both across Demos 3 and 4. Its job is to **name** them as portable gotchas, restate the cure in a line, and pin each back to where the room saw it. Budget ~5 minutes as a recap slide. (These are the two *sequential-DAG-native* gotchas; the routing gotchas — workflow-where-an-agent-is-needed, brittle-branch-conditions — belong to [L05's coda](../L05/demos_or_activities.md#common-pitfalls-coda--naming-l05s-three-gotchas).)

**Live script (recap — point back, don't re-run):**

1. **Model-driven looping sneaking into a "deterministic" DAG.** ❌ Believing the workflow is fully deterministic — the *path* is fixed, but each node's model output still varies (Demo 3), and quietly adding a back-edge turns your workflow into an agent (Demo 4) without you deciding to. **Cure:** keep it acyclic on purpose; if you need to loop on the model's output, you've crossed into [L10](../L10/objectives.md)/[L11](../L11/objectives.md) territory — name the crossing.
2. **Wrong model per node (overpaying / underpowering).** ❌ Sonnet on the light `parse`/extract step, or Haiku on the hard `draft` reasoning. Point back at Demo 3's per-node binding. **Cure:** cheap model for parse/extract, capable model for reasoning — the *mechanism* is Demo 3; the *decision framework* is [L14](../L14/objectives.md) (full course).

**What to highlight:**

- Gotcha #1 is where the lesson's spine blurs: **confusing "the developer owns the path" (workflow) with "the model owns the path" (agent)** — a back-edge added by reflex turns a workflow into an agent without you deciding to. Keeping that line sharp is the whole lesson.
- #2 points forward — the *mechanism* of per-node model mixing is Demo 3; the *decision framework* is [L14](../L14/objectives.md). Name the link, **don't re-teach it here.**

## Optional demo — evaluate the workflow (carry L13 forward)

If time allows, close by reinforcing L13's discipline on the cheapest possible target. A deterministic workflow is the *easiest* thing to evaluate — its **structure is fixed**, so you're only measuring a node's output, not chasing a moving control flow.

1. Import the L13 harness from `common/evals.py` (reused, **not** rebuilt — recall it in one line; don't re-teach eval design).
2. Write ~3–4 `EvalCase`s over a node in the chain — e.g. a ticket in and the expected fields out of `parse`, or a drafted reply in and the expected pass/fail out of `policy_check`. Run `evaluate(...)` and read the pass rate.
3. Land two things: workflows are **trivially testable** (half the reason to prefer them), and L13's rule — *when you build or change something, you evaluate it* — applies to workflows as much as agents. The same eval habit carries onto [L05](../L05/objectives.md)'s router next lesson and the L11 agent after.

Don't re-teach eval mechanics — that's L13. Just show the harness *pointing at a workflow* so the carry-forward habit stays visible.

<!-- *NEED INPUT*: include this eval beat in the lecture, or hold it for the L03 lab? Recommendation: short optional closer. -->

## Pacing notes for the teacher

- **Movement 1 (~30–35 min):** primer (≈12, read-alone) + Demo 1 (15–20, the before/after walkthrough and client-swap) + Demo 2 (10–12, compile/invoke/inspect is mechanically quick). Movement 1 is honest that the ceremony hasn't paid off yet — resist the urge to justify it in the abstract.
- **Movement 2 (~30–45 min):** Demo 3 is the long one (18–25, live `StateGraph` build + diagram + trace, reusing the node) + Demo 4 (8–12, diagram + discussion) + coda (~5) + optional eval beat (5–8, the natural cut if long).
- **Total ~1 h 45 m–2 h plus discussion.** This is a full lesson, not a short one — the merge traded two thin single-lab lessons for one that lands the node *and* its payoff. If it runs long, cut the optional eval beat to the lab.
- **Reuse the node, don't rebuild it.** Demo 3 must wire Demo 1's `parse` node in *unchanged* — the "one node became a pipeline" continuity is the merged lesson's whole argument. Do **not** re-derive the `StateGraph` builder from scratch in Demo 3; extend Demo 2's graph.
- **Determinism is the point, but the model inside nodes still varies:** a node's Claude call is non-deterministic even though the *path* is fixed. Budget a re-run where a node's output quality matters (the draft); the **path** stays stable — exactly the lesson.
- **Reinforce L01/L02 vocabulary throughout.** Tokens, cost, structured-output-by-instruction, defensive parsing. Every node should read as "the thing you already know, now inside a node."
- **The audience watches, doesn't participate.** Hands-on graph-building is for the L03 lab. (The user-input-vs-classifier decider comparison is L05's, not L03's.)

## Open authoring questions

- <!-- *NEED INPUT*: confirm the support-ticket domain end-to-end and the exact sample tickets + policy snippet (fixture). The `parse` node built in Demo 1 must be the literal first node of Demo 3's chain — that continuity is the merge's payoff. -->
- <!-- *NEED INPUT*: exact model id strings for the Sonnet 4.6 and Haiku 4.5 snapshots, read from common/config.py rather than hard-coded in cells. -->
- <!-- *NEED INPUT*: confirm the graph-diagram render path (draw_mermaid_png vs Mermaid text vs ASCII) works in the demo environment. -->
- <!-- *NEED INPUT*: are the demos run in a projected Jupyter notebook, a slide-embedded REPL, or a demo-runner script? Mirrors the same open question in L02's demos. -->
- <!-- *NEED INPUT*: include the optional eval-the-workflow beat in the lecture or hold it for the lab? -->
