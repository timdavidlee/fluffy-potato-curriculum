# L04: Teacher-led demos — Explicit graphs & workflows in LangGraph (deterministic DAGs)

> Sibling docs: [objectives.md](objectives.md) (what the lesson aims for), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md).
>
> **Audience for this file:** the teacher running L04. Every demo below is *teacher-driven, no student participation*. Student-driven exercises live in the L04 labs (separate file, stage 2).
>
> **Anchor model: Claude Sonnet 4.6** for the heavy reasoning nodes, **Claude Haiku 4.5** for the light nodes (classify / route / extract). **L04 deliberately mixes models per node** — that mixing is the point of objective 1's per-node binding, *not* an accident. **This is the course's first framework lesson:** nodes call the **native LangChain `ChatAnthropic`** client directly, *not* the hand-rolled `potato_llm` seam used in L01–L12. Call that departure out loud.

## How to read this file

Each demo is a self-contained block with:

- **Goal** — the single insight the demo should land. Tied to a learning objective from [objectives.md](objectives.md).
- **Pre-flight** — what the teacher needs loaded before class.
- **Live script** — the order of operations during the demo. Treat it as a checklist, not a teleprompter.
- **What to highlight** — the moment(s) where the teacher should slow down and say the takeaway out loud.
- **If the demo misbehaves** — graceful fallback for when the model surprises you (it will).

The demos are ordered to match the four learning objectives from [objectives.md](objectives.md). Demo 1 builds a **prompt-chaining** workflow from scratch on `StateGraph` and lands "control flow as data" (objectives 1 & 3a); Demo 2 builds a **routing** workflow and uses it to show **per-node model mixing** (objectives 1, 2 & 3b); Demo 3 swaps the router's decider to **user input** and puts the two side by side (objectives 2 & 3c); Demo 4 names the **workflow-vs-agent** line as a single back-edge and points it forward to L14 (objective 4). The optional demo carries L12's eval discipline onto the workflow. They build on each other — Demos 2–4 reuse Demo 1's graph and the same support-ticket domain, never a fresh one. Run them in order on first delivery.

> **The spine of L04: graphs first, agency second.** L04 is the *first* LangGraph lesson and it deliberately builds a **workflow** (a developer-wired *acyclic* graph), not an agent. The model lives *inside* the nodes (classify, draft, summarize); the **developer owns the edges**. Keep saying "in a workflow you wire the flow; in an agent (L14) the model drives the flow." The single thing that separates this lesson from L14 is a **back-edge** — Demo 4 names it explicitly so L14 feels like one small step, not a new world.

## Pre-flight (once, at the top of the lesson)

The teacher should have, before the first demo starts:

- **LangGraph + the native LangChain Claude client ready.** `from langgraph.graph import StateGraph, END` and `from langchain_anthropic import ChatAnthropic`. Both `langgraph` and `langchain-anthropic` are already project dependencies (added via `uv add` in the L14 decision); no install during class. The API key still loads through `common/config.py` (`ChatAnthropic` reads `ANTHROPIC_API_KEY` from the same environment the config seam populates) — key handling is unchanged, only the *client* is the framework's now.
- **Two model clients constructed and named:** `haiku = ChatAnthropic(model="claude-haiku-4-5-...")` for light nodes, `sonnet = ChatAnthropic(model="claude-sonnet-4-6-...")` for heavy nodes. Each node constructs/uses its own — that *is* objective 1's per-node binding. <!-- *NEED INPUT*: confirm exact model id strings for the Haiku 4.5 and Sonnet 4.6 snapshots used by ChatAnthropic, read from common/config.py rather than hard-coded in cells. -->
- **The shared Langfuse callback handler wired up**, pointing at the *same* self-hosted Langfuse instance students met in L11 (LangChain/LangGraph callback handler; keys via `common/config.py`). The workflows run with this callback so their spans land in the dashboard students already know — "watch the workflow run" reuses an L11 skill, it is not new.
- **A graph-diagram renderer ready** — LangGraph's `compiled_graph.get_graph().draw_mermaid_png()` (or the Mermaid text) — so "control flow as data" is *literally visible* (a decided beat: render each workflow's diagram once). <!-- *NEED INPUT*: confirm the diagram render path works in the demo environment (draw_mermaid_png needs a renderer; the Mermaid-text or ASCII fallback is fine if the PNG path is awkward to set up live). -->
- **A small support-ticket dataset** for the running example (the decided domain): a handful of sample tickets that clearly fall into **billing / technical / general**, plus a short **policy snippet** the policy-check node checks a drafted reply against. <!-- *NEED INPUT*: confirm the exact sample tickets and the policy text. Recommendation: 3–4 tickets (one obviously billing, one technical, one general, one ambiguous to stress the classifier) and a 4–5 line refund/escalation policy for the policy-check node. Stage 2 ships these as a small fixture. -->
- **Completed graph definitions in a sibling file** to paste if live-coding falls behind — the prompt-chaining graph (Demo 1), the routing graph (Demo 2), and the user-input-branching graph (Demo 3).
- **`common/evals.py` importable** for the optional eval-the-workflow beat (the L12 harness — reused, not rebuilt).

> Why a support-ticket domain and not the L10/L11 tools: L04 is about graph *shape* (chaining, routing) and developer-owned control flow, which a parse→draft→check pipeline shows naturally; the `calculator`/`lookup` tools were about *tool calls*, which L04 deliberately defers to L14. (Stage 2 *may* call a plain Python helper inside a node, but **the model never chooses a tool in L04** — that is the workflow/agent line.)

## Demo 1 — Prompt chaining: your first workflow graph (Objectives 1 & 3a)

**Goal:** build a deterministic **prompt-chaining** workflow on `StateGraph` from scratch and land the headline framing — **a graph turns control flow into inspectable data, the model lives inside the nodes, and the developer owns the edges.** Land that an acyclic graph (no back-edge) is exactly what makes this a *workflow*, not an agent.

**Pre-flight:**

- An empty cell/file for the live build.
- The support-ticket sample on the slide and a single ticket chosen to run end-to-end.
- The pipeline shape on the board: **parse → draft → policy-check**, a fixed three-node chain.

**Live script:**

1. Sketch the chain on the board first: three boxes, two forward arrows, an entry and an `END`. Name it a **DAG** — every edge moves forward, no edge returns.
2. Live-code the **typed state** schema (a `TypedDict` / annotated state) carrying the fields that flow between steps: the raw ticket, the parsed fields, the drafted reply, the policy verdict. Note the **reducer** idea in passing (a field is overwritten or, for accumulating fields, appended) — the *same* state/reducer machinery L14 will reuse for an agent's message history.
3. Live-code the three **nodes** as plain typed functions, each reading state and returning an update:
   - `parse` — calls **Haiku** (`ChatAnthropic`) to extract structured fields from the ticket (a light step).
   - `draft` — calls **Sonnet** to write a reply (the heavy reasoning step).
   - `policy_check` — checks the draft against the policy snippet (a Sonnet call, or a plain Python check).
4. Wire it with the `StateGraph` builder: `add_node` ×3, `set_entry_point("parse")`, `add_edge("parse","draft")`, `add_edge("draft","policy_check")`, `add_edge("policy_check", END)`. **`compile()`**, then **`invoke()`** on the chosen ticket.
5. **Render the compiled graph diagram** (`draw_mermaid_png`/Mermaid text) and put it next to the code — "this picture *is* the control flow, as data."
6. Open the run in **Langfuse**: a linear chain of GENERATION spans, one per node, in order. Confirm the path was developer-determined.

**What to highlight:**

- **Control flow is now data.** Nodes and edges can be listed, drawn, and traced — unlike `if`/`while` buried in Python. Show the diagram and the trace as proof.
- **The model lives *inside* the nodes; the developer owns the edges.** The model does the smart per-step work (parse, draft); *what runs next* is decided by the edges *you* wired. This is the contrast you'll repeat all lesson.
- **First framework, native client.** Say the departure out loud: from L04 on, nodes call LangChain's `ChatAnthropic` directly, not the `potato_llm` seam from L01–L12 — "frameworks bring their own client abstraction."
- **Why decompose into three prompts instead of one mega-prompt?** Smaller focused prompts are more reliable and individually testable; the cost is more calls (the L01 cost trade). Name it honestly: for a strictly linear chain the graph is near break-even — its payoff shows with branching, visualization, shared state, and tracing.

**If the demo misbehaves:**

- If live-coding the builder falls behind, paste the completed graph and walk it node by node — but keep the **`invoke()` run, the diagram, and the trace**, which is where "workflow" stops being abstract.
- If a node's structured extraction is flaky, tighten its prompt to return a small structured shape (callback to L02 structured-output-by-instruction) — don't reach for tool calling, which is L14's territory.

## Demo 2 — Routing + mixed models: classify, then branch (Objectives 1, 2 & 3b)

**Goal:** build a **routing** workflow — an entry classifier labels the ticket and a **conditional edge** sends it down one of several specialized branches — and use it to show **each node can bind its own model** (cheap classifier on Haiku, capable branches on Sonnet). Land the critical L04-vs-L14 point: **the conditional edge branches on a model *classification result in state*, not on the model deciding to call a tool.**

**Pre-flight:**

- Demo 1's state schema, extended with a `category` field.
- The billing / technical / general branches sketched, each with its own focused prompt, converging to a single exit.

**Live script:**

1. Add a `classify` entry node that calls **Haiku** and writes a `category` label into state (billing / technical / general). Cheap model, because the job is just a label.
2. Add three specialized branch nodes (`billing`, `technical`, `general`), each a **Sonnet** call with its own prompt. They converge to `END`.
3. Wire the **conditional edge**: a routing function reads `state["category"]` and returns the matching branch name — `add_conditional_edges("classify", route_fn, {...})`. Say the line out loud: *the **classification result in state** picks the branch; re-running the same ticket takes the same path.*
4. `compile()`, render the diagram (now it visibly **branches**), and `invoke()` on one ticket per category. Re-run the *same* ticket and show the path is identical — **deterministic**.
5. Open **Langfuse**: the `classify` span shows **Haiku** (and its cost); the chosen branch span shows **Sonnet** (and its cost). Point at the two different models on two spans. A light cost/latency aside: the label step is cheap, the reasoning step is where the spend goes.

**What to highlight:**

- **A conditional edge is *not* the model deciding** — in L04 the routing function branches on **state the developer set** (here a model *classification label*). In L14 the routing function branches on whether the **model asked for a tool**. Same mechanism, different decider — call out which it is *every time*.
- **Each node can use its own model.** A node is an independent call, so a graph mixes models: Haiku where you need a label, Sonnet where you need quality. The trace makes it tangible — each span shows its own model and cost. This is the **mechanism** of mixed-model design.
- **The *which-model* decision framework is L13's job, not L04's.** L04 shows only *that* you can mix and *how*; the capability/latency/cost axes and budgets ("small model for routing, capable for reasoning") are L13 (Choosing model power). In the mini cut L13 is dropped, so this is students' first and only mixed-model exposure — keep it light but make it land.

**If the demo misbehaves:**

- If Haiku mis-classifies the ambiguous ticket, **keep it** — it's a perfect lead-in to the optional eval beat ("a deterministic workflow is trivially testable; let's measure the classifier") and a callback to L12. Don't paper over it.
- If the trace doesn't show distinct models per span, check that each node constructed its own `ChatAnthropic(model=...)` rather than sharing one client — that *is* the per-node-binding lesson surfacing as a bug.

## Demo 3 — Same graph, different decider: user-input branching (Objectives 2 & 3c)

**Goal:** take the routing graph's shape and swap the decider from a model classifier to **direct user input**, then put the two head to head. Land the purest form of "you wire the flow": **a conditional edge can route on a value the *user* supplied, with no model in the routing decision at all.**

**Pre-flight:**

- Demo 2's routing graph.
- A version where the branch is chosen by a `user_choice` field supplied in the **initial state** (a menu choice / structured selection), not by a `classify` node.

**Live script:**

1. Show the change: replace the `classify` node with a `user_choice` value that arrives **as part of the initial state**, and a routing function that reads it directly — `if state["user_choice"] == "billing": return "billing"`. No model call in the routing decision.
2. `invoke()` with different `user_choice` values and watch the deterministic branch each time.
3. Put the **two graphs side by side**: Demo 2 (model-classifier routing) and Demo 3 (user-input routing). *Same graph shape, different decider* — the **user** chose the path here, the **model classification** chose it there. **Both are still workflows** because the developer wired every branch.
4. Show a natural **combined** shape in one line: route on the user's choice *first*, then run a model-driven *node* inside the chosen branch — **user owns the edge, model works inside the node.**

**What to highlight:**

- **Routing can be driven by derived data, a model label, or a human choice** — and user input is the sharpest contrast with an agent: here the *user/developer* decides the path; in L14 the *model* does. Most real "AI workflows" mix model-classified routing with plain user-input routing.
- **No model in the routing decision** is allowed and common — agency is about who controls the *path*, not whether a model is called somewhere in the graph.
- **Forward pointer, one line, don't teach it:** the *interactive* version — a graph that **pauses to ask** the user and resumes on their answer — needs LangGraph's `interrupt` + a checkpointer and is **L17's** territory (human-in-the-loop). In L04 the user input arrives in the initial state, so the graph runs straight through.

**If the demo misbehaves:**

- If students conflate "user-input branch" with "the agent asked the user," re-draw the side-by-side: in Demo 3 the value is *already in state* before the run; nothing is asked mid-run. The asking-mid-run version is L17.

## Demo 4 — Workflow vs. agent: the line is a single back-edge (Objective 4)

**Goal:** make the **workflow-vs-agent** distinction crisp and concrete, and point it forward to L14 with surgical precision: **everything built in L04 carries into L14 unchanged; L14 adds exactly one thing — a conditional edge that loops back to the model.** That single back-edge is the line between the two lessons.

**Pre-flight:**

- One of the compiled workflows from Demos 1–2, with its rendered (acyclic) diagram.
- A **sketch** (not a live build) of the L14 shallow-agent shape: an `agent` node, a `tools` node, and a conditional edge out of `agent` that loops back to `tools` or exits.

**Live script:**

1. Put the L04 workflow diagram up: trace any path with your finger — every arrow goes forward, it always reaches `END`. Name it: **DAG, acyclic, developer-wired = workflow.**
2. Now draw **one new edge** on top of the sketch: a conditional edge out of the model node that routes *back* into the loop (call a tool) or to `END` (finish). That back-edge hands the *model* control of the path.
3. State the distinction verbatim (it reappears in L14): a **workflow** is a graph whose path is fixed or chosen by *developer logic* (acyclic, predictable, model inside nodes); an **agent** is a graph whose path is chosen by the *model*, via a **cycle** that loops model → tools → model until the model stops. That cyclic loop is exactly L10's hand-rolled loop, and L14's shallow agent.
4. Reason about **when to use which**: prefer a **workflow** when the task has a known shape — predictable, cheaper, lower-latency, far easier to test and trace; reach for an **agent** only when the steps can't be known in advance and the model genuinely needs to decide its own path. Name the common failure mode out loud: **reaching for an agent when a workflow would do** (more cost, less predictability, harder to debug).

**What to highlight:**

- **The workflow→agent line is one back-edge.** Don't let it feel like a new world — L14 keeps nodes, edges, typed state, reducers, compile/invoke, and the Langfuse hookup *unchanged*, and adds only the cycle. Framing it this way is the whole reason L04 comes first.
- **Determinism is a feature, not a limitation.** Most production "AI features" are workflows, not agents. Choosing the simplest shape that solves the task — usually a workflow — *is* the engineering skill.
- Do **not** build the agent here. Building the cycle is **L14's** lesson; L04 only *names* the back-edge. (L04 and L14 intentionally overlap on the primitives so each stands alone — but the cyclic agent belongs to L14.)

**If the demo misbehaves:**

- This demo is mostly diagram + discussion, so little can flake. If a student insists "but the classifier *is* the model deciding," reach back to Demo 2's highlight: the model produced a *label in state*; the developer's routing function read that label and chose the edge. The model didn't choose the edge — and it never loops.

## Optional demo — evaluate the workflow (carry L12 forward)

If time allows, close by reinforcing L12's discipline on the cheapest possible target. A deterministic workflow is the *easiest* thing to evaluate — **same input → same path** — so a tiny eval set over the routing classifier is a natural, honest reinforcement of "evaluate everything you build."

1. Import the L12 harness from `common/evals.py` (reused, **not** rebuilt — recall it in one line; don't re-teach eval design).
2. Write ~3–4 `EvalCase`s over the `classify` node: a labeled ticket in, the expected `category` out. Run `evaluate(...)` and read the pass rate.
3. Land two things: workflows are **trivially testable** (which is half the reason to prefer them), and L12's rule — *when you build or change something, you evaluate it* — applies to workflows just as much as agents. This is the same eval set students will carry onto the **L14** LangGraph agent next lesson.

Don't re-teach eval mechanics here — that's L12. Just show the harness *pointing at a workflow* so the carry-forward habit stays visible.

<!-- *NEED INPUT*: include this eval beat in the lecture, or hold it for the L04 lab? Recommendation: keep it as a short optional closer — it reinforces L12 cheaply and sets up L14's "same eval set, new implementation" beat. -->

## Pacing notes for the teacher

- **Per-demo time:** Demo 1 is the long one (18–25 minutes including the live `StateGraph` build + diagram + trace). Demo 2 is 12–18 (routing + per-node models). Demo 3 is 8–12 (the decider swap + side-by-side). Demo 4 is 8–12 (diagram + discussion, no build). Optional eval beat is 5–8. Total ~50–75 minutes plus discussion — fits the **~75–100 minute** single lecture pinned in [objectives.md](objectives.md). If it runs long, split at the Demo 2/3 boundary: "graph primitives + prompt chaining" then "routing (incl. user-input branching + per-node models) + workflow-vs-agent."
- **Live-coding budget:** only Demo 1's chain and Demo 2's routing additions need live-coding. Demo 3 is a small edit to Demo 2; Demo 4 is diagram + talk. Do **not** re-derive the `StateGraph` builder in each demo — reuse Demo 1's.
- **Determinism is the point, but the *model inside nodes* still varies:** a node's Claude call is non-deterministic even though the *path* is fixed. Budget a re-run where a node's output quality matters (the draft, the classification label); the **path** will be stable, which is exactly the lesson.
- **The audience watches, doesn't participate.** Resist "what node should run next?" as a group question — that's a lab pattern. Hands-on graph-building and the user-input-vs-classifier comparison are for the L04 labs.

## Open authoring questions

Most of L04's big decisions are already pinned in [objectives.md](objectives.md) (native `ChatAnthropic` not the seam; Haiku-light/Sonnet-heavy per-node mixing as *mechanism only*, with the decision framework deferred to L13; the support-ticket domain; Langfuse tracing via the L11 instance; render-the-diagram-once; user-input branching in the initial-state form with `interrupt`/checkpointer deferred to L17; parallel branches as a forward-pointer mention only; the intentional L04↔L14 primitives overlap). The remaining open items are stage-2 mechanics:

- <!-- *NEED INPUT*: exact model id strings for the Haiku 4.5 and Sonnet 4.6 snapshots, read from common/config.py rather than hard-coded in cells. -->
- <!-- *NEED INPUT*: the sample support tickets (3–4, including one ambiguous to stress the classifier) and the policy snippet for the policy-check node, shipped as a fixture. -->
- <!-- *NEED INPUT*: confirm the graph-diagram render path (draw_mermaid_png vs Mermaid text vs ASCII) works in the demo environment. -->
- <!-- *NEED INPUT*: per-node model assignment in the chaining demo — recommended parse=Haiku, draft=Sonnet, policy_check=Sonnet (or a plain Python check); confirm in stage 2. -->
- <!-- *NEED INPUT*: the user_choice shape in Demo 3 (a menu string / structured selection) and the combined "user picks branch, model works inside node" example. -->
- <!-- *NEED INPUT*: are the demos run in a projected Jupyter notebook, a slide-embedded REPL, or a demo-runner script? Mirrors the same open question in L10's and L12's demos. -->
- <!-- *NEED INPUT*: include the optional eval-the-workflow beat in the lecture or hold it for the lab? Recommendation: short optional closer (reinforces L12, sets up L14). -->
