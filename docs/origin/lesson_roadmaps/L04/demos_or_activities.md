# L04: Teacher-led demos — Directed graphs: sequential chaining (LangGraph workflows)

> Sibling docs: [objectives.md](objectives.md) (what the lesson aims for), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md).
>
> **Audience for this file:** the teacher running L04. Every demo below is *teacher-driven, no student participation*. Student-driven exercises live in the L04 labs (separate file, stage 2).
>
> **Anchor model: Claude Sonnet 4.6** for the heavy reasoning nodes (draft, policy-check), **Claude Haiku 4.5** for the light nodes (parse / extract / summarize). **L04 deliberately mixes models per node** — that mixing is the point of objective 1's per-node binding, *not* an accident. **This is the course's first framework lesson:** nodes call the **native LangChain `ChatAnthropic`** client directly, *not* the hand-rolled `potato_llm` seam used in L01–L02. Call that departure out loud — it's the single switch-over point: the seam carries the prompt-only lessons, the framework client takes over from L03 onward.
>
> **Scope (post-split):** L04 is **sequential prompt-chaining only** — a fixed, acyclic chain. **Routing, conditional edges, and user-input branching are not L04's** — they moved to **[L05](../L05/demos_or_activities.md)** in the [L04/L05 split](objectives.md). This file builds the chain and *names* (does not build) the workflow-vs-agent line.

## How to read this file

Each demo is a self-contained block with:

- **Goal** — the single insight the demo should land. Tied to a learning objective from [objectives.md](objectives.md).
- **Pre-flight** — what the teacher needs loaded before class.
- **Live script** — the order of operations during the demo. Treat it as a checklist, not a teleprompter.
- **What to highlight** — the moment(s) where the teacher should slow down and say the takeaway out loud.
- **If the demo misbehaves** — graceful fallback for when the model surprises you (it will).

The demos are ordered to match L04's learning objectives. Demo 1 builds a **prompt-chaining** workflow from scratch on `StateGraph` and lands "control flow as data" — including **per-node model binding** (Haiku on light nodes, Sonnet on heavy) and the `graph.stream(stream_mode="updates")` run-inspection beat (objectives 1 & 3). Demo 2 names the **workflow-vs-agent** line as a single back-edge and forward-points — routing is **[L05](../L05/objectives.md)**, the agent is **L11** (objective 4). The optional demo carries L13's eval discipline onto the workflow. They build on each other — Demo 2 and the optional eval reuse Demo 1's graph and the same support-ticket domain, never a fresh one. Run them in order on first delivery.

> **The spine of L04: graphs first, agency second.** L04 is the *first* LangGraph lesson and it deliberately builds a **workflow** (a developer-wired *acyclic* graph), not an agent. The model lives *inside* the nodes (parse, draft, policy-check); the **developer owns the edges**. Keep saying "in a workflow you wire the flow; in an agent (L11) the model drives the flow." The single thing that separates a workflow from an agent is a **back-edge** — Demo 2 names it explicitly and forward-points, so **[L05](../L05/objectives.md)** (routing, still developer-owned) and **L11** (the agent) feel like small steps, not a new world.

## Pre-flight (once, at the top of the lesson)

The teacher should have, before the first demo starts:

- **LangGraph + the native LangChain Claude client ready.** `from langgraph.graph import StateGraph, END` and `from langchain_anthropic import ChatAnthropic`. Both `langgraph` and `langchain-anthropic` are already project dependencies (added via `uv add` in the L11 decision); no install during class. The API key still loads through `common/config.py` (`ChatAnthropic` reads `ANTHROPIC_API_KEY` from the same environment the config seam populates) — key handling is unchanged, only the *client* is the framework's now.
- **Two model clients constructed and named:** `haiku = ChatAnthropic(model="claude-haiku-4-5-...")` for light nodes, `sonnet = ChatAnthropic(model="claude-sonnet-4-6-...")` for heavy nodes. Each node constructs/uses its own — that *is* objective 1's per-node binding. <!-- *NEED INPUT*: confirm exact model id strings for the Haiku 4.5 and Sonnet 4.6 snapshots used by ChatAnthropic, read from common/config.py rather than hard-coded in cells. -->
- **`graph.stream(stream_mode="updates")` ready as the run-inspection tool** — the same built-in call students met in L03, no external setup. Run the workflow with `stream` instead of `invoke` so the nodes' updates print in order as they fire. Langfuse is **not** wired up here: it is L12's tool and comes *later* in the course; "watch the workflow run" reuses the L03 `stream` skill, not a dashboard.
- **A graph-diagram renderer ready** — LangGraph's `compiled_graph.get_graph().draw_mermaid_png()` (or the Mermaid text) — so "control flow as data" is *literally visible* (a decided beat: render the workflow's diagram once). <!-- *NEED INPUT*: confirm the diagram render path works in the demo environment (draw_mermaid_png needs a renderer; the Mermaid-text or ASCII fallback is fine if the PNG path is awkward to set up live). -->
- **A small support-ticket dataset** for the running example (the decided domain): a handful of sample tickets, plus a short **policy snippet** the policy-check node checks a drafted reply against. <!-- *NEED INPUT*: confirm the exact sample tickets and the policy text. Recommendation: 2–3 tickets and a 4–5 line refund/escalation policy for the policy-check node. Stage 2 ships these as a small fixture. (The classifier-stressing "ambiguous ticket" belongs to L05's routing demos, not here.) -->
- **A completed prompt-chaining graph definition in a sibling file** to paste if live-coding falls behind — the Demo 1 chain.
- **`common/evals.py` importable** for the optional eval-the-workflow beat (the L13 harness — reused, not rebuilt).

> Why a support-ticket domain and not the L10/L12 tools: L04 is about graph *shape* — a fixed **parse → draft → policy-check** pipeline shows sequential chaining and developer-owned control flow naturally; the `calculator`/`lookup` tools were about *tool calls*, which L04 deliberately defers to L11. (Stage 2 *may* call a plain Python helper inside a node, but **the model never chooses a tool in L04** — that is the workflow/agent line.)

## Demo 1 — Prompt chaining: your first workflow graph (Objectives 1 & 3)

**Goal:** build a deterministic **prompt-chaining** workflow on `StateGraph` from scratch and land the headline framing — **a graph turns control flow into inspectable data, the model lives inside the nodes, and the developer owns the edges.** Land that an acyclic graph (no back-edge) is exactly what makes this a *workflow*, not an agent.

**Pre-flight:**

- An empty cell/file for the live build.
- The support-ticket sample on the slide and a single ticket chosen to run end-to-end.
- The pipeline shape on the board: **parse → draft → policy-check**, a fixed three-node chain.

**Live script:**

1. Sketch the chain on the board first: three boxes, two forward arrows, an entry and an `END`. Name it a **DAG** — every edge moves forward, no edge returns.
2. Live-code the **typed state** schema (a `TypedDict` / annotated state) carrying the fields that flow between steps: the raw ticket, the parsed fields, the drafted reply, the policy verdict. Note the **reducer** idea in passing (a field is overwritten or, for accumulating fields, appended) — the *same* state/reducer machinery L11 will reuse for an agent's message history.
3. Live-code the three **nodes** as plain typed functions, each reading state and returning an update:
   - `parse` — calls **Haiku** (`ChatAnthropic`) to extract structured fields from the ticket (a light step).
   - `draft` — calls **Sonnet** to write a reply (the heavy reasoning step).
   - `policy_check` — checks the draft against the policy snippet (a Sonnet call, or a plain Python check).
4. Wire it with the `StateGraph` builder: `add_node` ×3, `set_entry_point("parse")`, `add_edge("parse","draft")`, `add_edge("draft","policy_check")`, `add_edge("policy_check", END)`. **`compile()`**, then **`invoke()`** on the chosen ticket.
5. **Render the compiled graph diagram** (`draw_mermaid_png`/Mermaid text) and put it next to the code — "this picture *is* the control flow, as data."
6. Run it with `graph.stream(stream_mode="updates")`: one chunk per node, in order — `{"parse": {...}}` → `{"draft": {...}}` → `{"policy_check": {...}}`. Confirm the path was developer-determined. (Routing this *same* run to Langfuse for a structured, comparable trace is **L12** — forward-reference it, don't reach for it here.)

**What to highlight:**

- **Control flow is now data.** Nodes and edges can be listed, drawn, and streamed step by step — unlike `if`/`while` buried in Python. Show the diagram and the `stream` output as proof.
- **The model lives *inside* the nodes; the developer owns the edges.** The model does the smart per-step work (parse, draft); *what runs next* is decided by the edges *you* wired. This is the contrast you'll repeat all lesson.
- **First framework, native client.** Say the departure out loud: from L03 on, nodes call LangChain's `ChatAnthropic` directly, not the `potato_llm` seam from L01–L02 — "frameworks bring their own client abstraction."
- **Each node can bind its own model.** A node is an independent call, so a graph mixes models: **Haiku** on the light `parse` step, **Sonnet** on the heavy `draft` step. The `stream` output makes it tangible — each node's update shows which model produced it. This is the **mechanism** of mixed-model design; the *which-model decision framework* (capability/latency/cost, budgets) is **[L14](../L14/objectives.md)'s** job, not L04's — name the link, don't re-teach it.
- **Why decompose into three prompts instead of one mega-prompt?** Smaller focused prompts are more reliable and individually testable; the cost is more calls (the L01 cost trade). Name it honestly: for a strictly linear chain the graph is near break-even — its payoff shows with branching ([L05](../L05/objectives.md), next), visualization, shared state, and tracing.

**If the demo misbehaves:**

- If live-coding the builder falls behind, paste the completed graph and walk it node by node — but keep the **`stream` run and the diagram**, which is where "workflow" stops being abstract.
- If a node's structured extraction is flaky, tighten its prompt to return a small structured shape (callback to L02 structured-output-by-instruction) — don't reach for tool calling, which is L11's territory.
- If the `stream` output doesn't show distinct models per node, check that each node constructed its own `ChatAnthropic(model=...)` rather than sharing one client — that *is* the per-node-binding lesson surfacing as a bug.

## Demo 2 — Workflow vs. agent: the line is a single back-edge (Objective 4)

**Goal:** open the **workflow-vs-agent** contrast on the fixed chain you just built, and forward-point with precision: **everything in L04 carries forward unchanged; [L05](../L05/objectives.md) adds one primitive (the conditional edge, still developer-owned), and L11 adds the one thing that makes an agent — a conditional edge that loops back to the model.** That single back-edge is the line between a workflow and an agent. Do **not** build a router or an agent here — this demo is diagram + discussion, mirroring [L0402_lecture.md](../../../../src/fluffy_potato_curriculum/lessons/L04/L0402_lecture.md)'s §6 "Bridge to L05."

**Pre-flight:**

- The compiled prompt-chaining workflow from Demo 1, with its rendered (acyclic) diagram.
- A **sketch** (not a live build) of the L11 shallow-agent shape: an `agent` node, a `tools` node, and a conditional edge out of `agent` that loops back to `tools` or exits.

**Live script:**

1. Put the Demo 1 workflow diagram up: trace the path with your finger — `parse → draft → policy_check → END`, every arrow forward, it always reaches `END`. Name it: **DAG, acyclic, developer-wired = workflow.**
2. Now draw **one new edge** on the L11 sketch: a conditional edge out of the model node that routes *back* into the loop (call a tool) or to `END` (finish). That back-edge hands the *model* control of the path.
3. State the distinction verbatim (it reappears in L05 and L11): a **workflow** is a graph whose path is fixed or chosen by *developer logic* (acyclic, predictable, model inside nodes); an **agent** is a graph whose path is chosen by the *model*, via a **cycle** that loops model → tools → model until the model stops. That cyclic loop is exactly L10's hand-rolled loop, and L11's shallow agent.
4. Place the whole arc on the board so nothing in it is a surprise later: **L04** = a graph with no branches (this lesson, the fixed chain). **[L05](../L05/objectives.md)** = a graph with branches *you* own (a conditional edge whose routing function reads state you control — a computed value, a model *label*, or user input). **L11** = a graph with a branch the *model* owns, wired into a loop. *Same primitives the whole way; the only thing that ever changes is who decides the path.*
5. Reason about **when to use which**: prefer a **workflow** when the task has a known shape — predictable, cheaper, lower-latency, far easier to test and trace; reach for an **agent** only when the steps can't be known in advance and the model genuinely needs to decide its own path. Name the common failure mode out loud: **reaching for an agent when a workflow would do** (more cost, less predictability, harder to debug).

**What to highlight:**

- **The workflow→agent line is one back-edge — but routing comes first.** Don't let the agent feel like a new world: L05 and L11 both keep nodes, edges, typed state, reducers, compile/invoke, and the `stream` run-inspection *unchanged*. L05 adds only the conditional edge (still developer-owned); L11 adds only the cycle. Framing it this way is the whole reason L04 comes first.
- **Determinism is a feature, not a limitation.** Most production "AI features" are workflows, not agents. Choosing the simplest shape that solves the task — usually a workflow — *is* the engineering skill.
- Do **not** build a router or the agent here. Routing is **[L05](../L05/objectives.md)**; building the cycle is **L11**. L04 only *names* the back-edge and forward-points. (L04, L05, and L11 intentionally overlap on the primitives so each stands alone — but the cyclic agent belongs to L11.)

**If the demo misbehaves:**

- This demo is mostly diagram + discussion, so little can flake. If a student insists "but a model *inside* a node is already the model deciding," separate the two: a model doing work *inside* a node (parse, draft) is not agency; agency is the model choosing the *path* — the back-edge — and nothing in L04 has one. (When a model *label* later picks a branch — that's [L05](../L05/objectives.md)'s routing — the developer's routing function still reads the label and owns the edge; the model does not.)

## Common pitfalls coda — naming L04's two gotchas

**Shape note:** a short **"common pitfalls" coda**, not a new live demo — L04 already *touches* both of these across Demos 1 and 2. Its job is to **name** them as portable gotchas, restate the cure in a line, and pin each back to where the room saw it. Budget ~5 minutes as a recap slide. Follows the [L23 Demo 5](../L23/demos_or_activities.md#demo-5--the-three-composition-anti-patterns-objective-5) anti-pattern-beat template, like the [L01 coda](../L01/demos_or_activities.md#common-pitfalls-coda--naming-l01s-four-gotchas). **Two routing gotchas that used to live here — workflow-where-an-agent-is-needed and brittle-branch-conditions — moved to [L05's coda](../L05/demos_or_activities.md#common-pitfalls-coda--naming-l05s-three-gotchas) in the [L04/L05 split](objectives.md), since L05 now owns conditional routing; L04 keeps only its two sequential-DAG-native gotchas.**

**Goal:** name the two DAG gotchas that stay L04's own — a model-driven cycle sneaking into a "deterministic" DAG, and the wrong model per node — as portable pitfalls a student can catch when they wire their own graph.

**Pre-flight:**

- Nothing new to load. One recap slide; the Demo 1 chaining diagram and the Demo 2 back-edge sketch still on screen to point back at.

**Live script (recap — point back, don't re-run):**

1. **Model-driven looping sneaking into a "deterministic" DAG.** ❌ Believing the workflow is fully deterministic — but the *path* is fixed while each node's model output still varies (Demo 1 / pacing notes), and quietly adding a back-edge turns your workflow into an agent (Demo 2) without you deciding to. **Cure:** keep it acyclic on purpose; if you need to loop on the model's output, you've crossed into [L10](../L10/objectives.md)/[L11](../L11/objectives.md) territory — name the crossing.
2. **Wrong model per node (overpaying / underpowering).** ❌ Sonnet on the light `parse`/extract step, or Haiku on the hard reasoning (`draft`) step. Point back at Demo 1's per-node binding. **Cure:** cheap model for parse/extract, capable model for reasoning — the *mechanism* is Demo 1; the *decision framework* is [L14](../L14/objectives.md) (full course).

**What to highlight:**

- Gotcha #1 is where L04's spine blurs: **confusing "the developer owns the path" (workflow) with "the model owns the path" (agent)** — a back-edge added by reflex turns a workflow into an agent without you deciding to. Keeping that line sharp is the whole lesson. (The routing-side version of this fault — *reaching for* an agent, and letting the model own a branch — is now [L05's coda](../L05/demos_or_activities.md#common-pitfalls-coda--naming-l05s-three-gotchas).)
- #2 points forward — the *mechanism* of per-node model mixing is Demo 1, but the *decision framework* for which model goes where is [L14](../L14/objectives.md) (full course). Name the link, **don't re-teach it here.**

**If a student pushes back:**

- "My DAG has a Sonnet node, isn't that agency?" No — a model *inside a node* isn't agency; agency is the model choosing the *path* (the back-edge). That distinction is the lesson (Demo 1/2 highlight).

## Optional demo — evaluate the workflow (carry L13 forward)

If time allows, close by reinforcing L13's discipline on the cheapest possible target. A deterministic workflow is the *easiest* thing to evaluate — its **structure is fixed**, so you're only measuring a node's output, not chasing a moving control flow — which makes a tiny eval set over one node of the chain a natural, honest reinforcement of "evaluate everything you build."

1. Import the L13 harness from `common/evals.py` (reused, **not** rebuilt — recall it in one line; don't re-teach eval design).
2. Write ~3–4 `EvalCase`s over a node in the chain — e.g. a ticket in and the expected extracted fields out of `parse`, or a drafted reply in and the expected pass/fail verdict out of `policy_check`. Run `evaluate(...)` and read the pass rate.
3. Land two things: workflows are **trivially testable** (which is half the reason to prefer them), and L13's rule — *when you build or change something, you evaluate it* — applies to workflows just as much as agents. This is the same eval habit students will carry onto [L05](../L05/objectives.md)'s router next lesson and the **L11** LangGraph agent after that.

Don't re-teach eval mechanics here — that's L13. Just show the harness *pointing at a workflow* so the carry-forward habit stays visible.

<!-- *NEED INPUT*: include this eval beat in the lecture, or hold it for the L04 lab? Recommendation: keep it as a short optional closer — it reinforces L13 cheaply and sets up L05's/L11's "same eval habit, new implementation" beat. -->

## Pacing notes for the teacher

- **Per-demo time:** Demo 1 is the long one (18–25 minutes including the live `StateGraph` build + diagram + trace). Demo 2 is 8–12 (diagram + discussion, no build). Optional eval beat is 5–8. Total ~30–45 minutes plus discussion — a shorter single segment than the pre-split combined lesson, since routing moved to [L05](../L05/objectives.md). If it runs long, the natural cut is the optional eval beat (hold it for the L04 lab).
- **Live-coding budget:** only Demo 1's chain needs live-coding. Demo 2 is diagram + talk, and the optional eval beat reuses Demo 1's graph. Do **not** re-derive the `StateGraph` builder anywhere else — reuse Demo 1's.
- **Determinism is the point, but the *model inside nodes* still varies:** a node's Claude call is non-deterministic even though the *path* is fixed. Budget a re-run where a node's output quality matters (the draft, the extracted fields); the **path** will be stable, which is exactly the lesson.
- **The audience watches, doesn't participate.** Resist "what node should run next?" as a group question — that's a lab pattern. Hands-on graph-building is for the L04 labs. (The user-input-vs-classifier decider comparison is L05's, not L04's.)

## Open authoring questions

Most of L04's big decisions are already pinned in [objectives.md](objectives.md) (native `ChatAnthropic` not the seam; Haiku-light/Sonnet-heavy per-node mixing as *mechanism only*, with the decision framework deferred to L14; the support-ticket **parse → draft → policy-check** domain; `stream`-based run inspection with Langfuse tracing deferred to L12; render-the-diagram-once; the intentional L04↔L11 primitives overlap). Routing / conditional-edge / user-input-branching decisions now live in **[L05](../L05/objectives.md)**. The remaining open items are stage-2 mechanics:

- <!-- *NEED INPUT*: exact model id strings for the Haiku 4.5 and Sonnet 4.6 snapshots, read from common/config.py rather than hard-coded in cells. -->
- <!-- *NEED INPUT*: the sample support tickets (2–3) and the policy snippet for the policy-check node, shipped as a fixture. -->
- <!-- *NEED INPUT*: confirm the graph-diagram render path (draw_mermaid_png vs Mermaid text vs ASCII) works in the demo environment. -->
- <!-- *NEED INPUT*: per-node model assignment in the chaining demo — recommended parse=Haiku, draft=Sonnet, policy_check=Sonnet (or a plain Python check); confirm in stage 2. -->
- <!-- *NEED INPUT*: are the demos run in a projected Jupyter notebook, a slide-embedded REPL, or a demo-runner script? Mirrors the same open question in L10's and L13's demos. -->
- <!-- *NEED INPUT*: include the optional eval-the-workflow beat in the lecture or hold it for the lab? Recommendation: short optional closer (reinforces L13, sets up L05's router eval then L11). -->
