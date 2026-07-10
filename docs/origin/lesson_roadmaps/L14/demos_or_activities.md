# L14: Teacher-led demos — Choosing models & providers for the task

> Sibling doc: [objectives.md](objectives.md) (what the lesson aims for), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (lesson-plan row L14).
> Preceding lesson demos: [L13 demos_or_activities.md](../L13/demos_or_activities.md) (the eval instrument these demos reuse to *decide* a model). Following lesson: L15 LangGraph design patterns (roadmap not yet written). **Track:** full-track only (the mini cut drops L14).
>
> **Audience for this file:** the teacher running L14. Every demo below is *teacher-driven, no student participation*. Student-driven exercises live in the L14 labs (separate file, produced by stage 2).

## How to read this file

Each demo is a self-contained block with:

- **Goal** — the single insight the demo should land. Tied to a learning objective from [objectives.md](objectives.md).
- **Pre-flight** — what the teacher needs loaded before class.
- **Live script** — the order of operations during the demo. Treat it as a checklist, not a teleprompter.
- **What to highlight** — the moment(s) where the teacher slows down and says the takeaway out loud.
- **If the demo misbehaves** — graceful fallback for when a live model surprises you (it will), or a key/provider isn't reachable on the day.

The demos follow the lesson's **concept-first, then design** spine and the objectives' opening map. **Demo 0** draws the map (providers × power tiers — objective 1, the frame). Demo 1 makes the **tier** decision *within* one provider concrete by reusing L13's eval as the decision procedure (objective 2). Demo 2 then exposes a **capability-class gap** that no tier of one provider closes — the reason to reach across *providers* (objective 1). Demo 3 is the live-code payoff: **bind a model per graph node** to build a mixed-model agent (objective 3). Demo 4 reads the **mixed cost + latency budget** off the trace (objective 4). Demo 5 is the optional live **cross-provider** swap (objective 3's mixed-*provider* half), gated on a second provider key. Run them in order on first delivery.

> **A note on what L14 reuses.** L14 introduces almost no new machinery — it is a *design* lesson built on parts students already have. It reuses: the LangChain `init_chat_model("provider:model")` / `bind_tools(...)` seam and `common/config.py` keys (the tool lessons L07/L08); an existing **graph** to bind models onto (an L05 router and/or the L10 ReAct agent, its `common/agent_graph.py` reference copy); the **trace** with per-call token usage (L12, `common/tracing.py`); and the **eval set + Langfuse experiment** (L13, `common/evals.py`, the `l13-agent-evals` dataset). The one genuinely new idea is *binding a different model per node* and *budgeting a heterogeneous run* — everything else is a callback. Reference these by name as stable imports; the one live-code beat is Demo 3's per-node binding.

## Naming and tooling reconciliation (read before building any demo)

- **Model handles.** Bind models with `init_chat_model("provider:model")` (keys through `common/config.py`, never hard-coded). The course's tier ladder for the running example is **Haiku 4.5 → Sonnet 4.6 → a higher-power tier**; the Claude-tier A/B (Demos 1, 3, 4) needs only `ANTHROPIC_API_KEY`. Cross-provider demos (2, 5) need a second provider key and are explicitly gated.
- **The graph to bind onto.** Reuse a graph students built earlier rather than wiring a new one: an L05 router (a conditional graph, cheapest to reason about) as the warm-up, and/or the L10 ReAct agent (`common/agent_graph.build_agent(...)`) as the "mixed-model *agent*" the PRD targets. <!-- *NEED INPUT*: which graph the hands-on binds onto — an L03/L05 workflow vs the L10 agent (must match objective 3's decision in the sibling objectives.md). -->
- **The decision instrument.** To *choose* a model, reuse L13's eval set (`common/evals.py`, the `l13-agent-evals` dataset) and Langfuse experiments — L14 adds no new scoring machinery, it applies L13's to the model-selection question.
- **Reproducibility stance (inherited from L12/L13).** *Reading/deciding* demos are clearest on fixed artifacts: pre-capture the eval-experiment results and the traces before class so pass rates and token counts are deterministic on the day. **Latency is the exception** — it is inherently live and variable, which is itself the lesson of Demo 4, so read latency off a real (optionally pre-captured) run and treat its exact numbers as illustrative.

## Pre-flight (once, at the top of the lesson)

- A working notebook/REPL on the project `uv` env that can `init_chat_model(...)`, import `common.agent_graph` / `common.tracing` / `common.evals` / `common.tools`, and read keys through `common/config.py`. `ANTHROPIC_API_KEY` set for the Claude-tier demos.
- The **`l13-agent-evals`** dataset available in the cohort Langfuse (uploaded in L13), plus the two scorers from L13 (`answer_correct`, `no_runaway`) — the decision instrument for Demo 1.
- A **capability-class task** for Demo 2 that a cheap text model provably cannot do — e.g. a scanned-invoice image (vision/OCR) or a corpus that overflows the cheap model's context window (long-context). Prepare it as a fixed, committed input so the failure is reproducible. <!-- *NEED INPUT*: the exact Demo 2 artifact (an image for OCR vs an over-long document for context) and whether it ships committed in the lesson folder or is fetched at runtime. -->
- For Demos 2 and 5 only: a second provider's key (a vision-capable / alternate provider). If it isn't available, both degrade to a **screenshot / canned-response** walk-through (see each demo's misbehave note). <!-- *NEED INPUT*: which second provider(s) the cohort has keys for, and whether the live cross-provider call runs on the day or ships as a canned/screenshot fallback so a keyless run still completes. Surface any new SDK dep to add via uv rather than assuming it. -->
- Pre-captured, committed **traces** for one mixed-model agent run (Demo 4), so the per-node token counts and the trajectory are deterministic; a slide of the trace waterfall for reading latency.
- A slide/whiteboard with the **provider × power-tier grid** (columns: vision/OCR · long-context · reasoning/planning · cheap high-throughput; rows: cheap/fast tier · balanced · top tier).

## Demo 0 — The map: providers × power tiers (Objective 1, the opening frame)

**Goal:** in ~4 minutes, before any code, give the class the map the whole lesson hangs on — choosing a model is **two decisions** (which provider, which power tier), and you sort by **capability class**, not brand. Land the one rule: *match the task to the cell of the grid, at the lowest tier that passes.*

**Pre-flight:**

- The provider × tier grid on a whiteboard/slide. No code.

**Live script:**

1. Ask: *"Every agent step so far has quietly used one model — Sonnet 4.6, with Haiku as a cheap contrast in L13. When would you use a **different** model for a step?"* Collect answers.
2. Draw the two axes. **Provider** across the top as **capability classes** — vision/OCR, long-context, reasoning/planning, cheap high-throughput. **Power tier** down the side — cheap/fast → balanced → top. Put the course's Claude tiers (Haiku 4.5 → Sonnet 4.6 → a higher tier) on the rows so students see the ladder they already know.
3. Sort four example tasks into cells, live: "read a scanned invoice" → vision/OCR; "summarize a 300-page contract" → long-context; "route to one of six handlers" → cheap high-throughput; "plan a multi-tool research task" → reasoning/planning.
4. State the rule: *"Pick the provider whose strength fits the class, at the **lowest tier that still passes your eval**. Defaulting every step to your favorite provider's top tier is the expensive mistake."*

**What to highlight:**

- Two decisions, not one — and the second (tier) is *not just "big vs small Claude,"* it's "which rung, on whichever provider fits the class."
- This map is the lesson: Demos 1–5 each fill in one part of it.

**If the demo misbehaves:**

- Purely conceptual. If the class sorts tasks fast, move to Demo 1; if someone insists "just always use the best model," flag it — that's the cost/latency confusion Demo 4 pays off.

## Demo 1 — Same task, two tiers: let the eval decide (Objective 2)

**Goal:** make the **tier** decision concrete and *measured*. Reuse L13's eval set against the *same* task at two Claude tiers (Haiku 4.5 vs Sonnet 4.6) and pick the **lowest tier that passes**. Land the through-line from L13: *measure the choice, don't assert it.*

**Pre-flight:**

- The `l13-agent-evals` dataset + the L13 scorers in Langfuse; `ANTHROPIC_API_KEY` set. Ideally the two experiment runs **pre-captured** so pass rates are deterministic in class (the live A/B is L13's Demo; here the point is *reading it as a selection method*).

**Live script:**

1. Recall L13 in one line: *"You already ran this exact A/B — the same dataset against Sonnet and Haiku, two Langfuse experiments. In L13 it was 'is B worse?'. Today it's the **decision procedure**."*
2. Show the two runs' pass rates side by side in Langfuse's run comparison. Read where Haiku holds up and where it drops.
3. Apply the rule out loud: on the cases where **Haiku's pass rate clears the bar, Haiku is the right choice** — cheaper and faster for no capability loss. On the cases where it drops, **escalate to Sonnet**. The eval, not a hunch, drew the line.
4. Name the reverse move: if Sonnet passes everywhere, *try Haiku and downgrade wherever it still passes* — the L13 ratchet, aimed at cost.

**What to highlight:**

- **The eval is the decision procedure.** Benchmarks are a prior; *your* cases pick the tier.
- **Lowest tier that passes** — capability you don't need is wasted cost and latency. This is the antidote to "just use the best model."

**If the demo misbehaves:**

- Reads pre-captured experiments, so it's stable. If you run it live and a rate comes out different from last cohort, that's fine — the *method* (read the rate, pick the cheapest that passes) is the content, not the exact number.

## Demo 2 — A capability-class gap: where no tier of one provider is enough (Objective 1)

**Goal:** show a task where the problem is **not the tier but the class** — a text model of *any* Claude tier can't read an image, and a small-context model can't fit a long document. This is *why* you reach across **providers**, not just up the tier ladder.

**Pre-flight:**

- The committed capability-class artifact (a scanned-invoice image for vision/OCR, or an over-long document for context). A vision-capable / alternate-provider model handle, **or** a canned result + screenshot if no second key.

**Live script:**

1. Hand the artifact to the anchor model (Sonnet 4.6, a text model in this course) and show it **fail on the class, not the tier**: it can't see the image / the input overflows the window. Escalating Claude tiers wouldn't help — the strength needed isn't on that ladder.
2. Hand the same artifact to a model in the right **capability class** (a vision model for the invoice; a long-context model for the document) and show it succeed.
3. Say the point: *"This is a **class** gap, not a **tier** gap. No amount of 'bigger Claude' reads an image it can't take as input. This is exactly when a mixed-**provider** agent earns its keep."*

**What to highlight:**

- The two axes are independent: tier is capability-vs-cost *within* a class; class is *which* strength. Demo 1 moved down a column; Demo 2 moves across columns.
- Mixing providers is justified by a **class gap**, not novelty — pre-empt "more providers is always better."

**If the demo misbehaves:**

- If the second provider isn't reachable, run the *failure* live (the anchor model genuinely can't do it) and show the success as a **committed canned response / screenshot**. The teachable content is the class gap, not the live cross-provider call.

## Demo 3 — Bind a model per node: build a mixed-model agent (Objective 3)

**Goal:** the live-code beat. Take a graph students already have and **bind a different model to different nodes**, so one agent runs several models. Land that *"choose a model for the task"* means, concretely, *"bind a model per node"* — a one-line change at the `init_chat_model` seam, not a rewrite.

**Pre-flight:**

- The chosen graph open (an L05 router as warm-up and/or the L10 `common/agent_graph.build_agent(...)` agent). `ANTHROPIC_API_KEY` set; a scripted/`FakeModel` fallback ready so the wiring is demonstrable keyless.

**Live script:**

1. Recall the node model from L03 & L05: *"A node is a function over state; the **model is a parameter of the node**. We've always passed the same one. Watch what happens when we don't."*
2. Warm-up on the L05 router: bind the **routing/classification node to Haiku 4.5** (cheap, fast, high-throughput — the class it fits) and a **downstream reasoning node to Sonnet 4.6**. Run one input; show the cheap model routing and the strong model doing the hard step.
3. Scale to the L10 agent: bind the small model where the work is mechanical (routing/execution) and the strong model where it's planning. Point at the `init_chat_model("provider:model")` call at each node — *"same node, different bound model; the graph didn't change."*
4. Say it: *"This is the whole lesson made concrete — a mixed-model agent is a graph whose nodes bind different models. L03 & L05 made the node the unit of orchestration precisely so this would be a parameter, not a rewrite."*

**What to highlight:**

- **Choose per node, not per agent.** The routing node and the planning node have different capability classes and should not share a tier by default.
- The binding is a **parameter at the seam** — the payoff of the course teaching `init_chat_model` and the node abstraction earlier.

**If the demo misbehaves:**

- If a live model takes a different path, that's fine — *any* successful run shows the per-node binding. Only Demo 4's budget needs a *specific* run, and that reads a pre-captured trace. If keys are tight, wire the binding against `FakeModel` handles so the *structure* is visible without a live call.

## Demo 4 — The mixed budget: cost is a sum, latency is a path (Objective 4)

**Goal:** budget the mixed-model agent from Demo 3. Land the two distinct computations: **cost is a sum over heterogeneous nodes** (each at its own model's price), **latency is the time along the critical path** (one slow node can dominate). Decide **which node to downgrade first**.

**Pre-flight:**

- The pre-captured trace of one mixed-model run (Demo 3's agent), with per-call token `usage` on each `llm` span (L12). Illustrative per-tier prices (flag them as example numbers, as L13 did). The trace waterfall on a slide for reading latency.

**Live script:**

1. Read the **cost** off the trace: for each node, `its model's price × its tokens`, then **sum across nodes**. Contrast with L13's single-model cost (`one rate × total calls`) — *"here the rate is per node, because the models differ."* Show the strong-reasoner node dominating the dollar cost even though it's one node.
2. Read the **latency** off the waterfall: the run's wall-clock is the **slowest path**, not the sum of every call. Show the top-tier node dominating the *seconds* — and note it may or may not be the same node that dominates the *dollars*.
3. Make the decision: *"If this is too slow, the fix is the node on the critical path; if it's too expensive, the fix is the node with the biggest token×price. They can be different nodes."* Point at which one you'd downgrade first, and confirm with Demo 1's method that the cheaper model still passes.

**What to highlight:**

- **Cost (a sum) and latency (a path) are different budgets on different math** — the single most important new idea in the lesson. A cheaper model can be slower; a faster one pricier.
- The numbers come straight off the **L12 trace** — the observability you built two lessons ago is what makes the budget real instead of guessed.

**If the demo misbehaves:**

- Cost reads deterministically off the fixed trace. Latency is inherently variable — if a live re-run comes out different, *that variance is the point*: budget latency as a distribution, not a single number.

## Demo 5 — (Optional, live) reach across providers for a capability class (Objective 3, the mixed-provider half)

**Goal:** close the loop from Demo 2. Swap **one node** of the Demo 3 agent to a **different provider** that leads on that node's capability class (e.g. a vision node on a vision-strong provider), so the agent is now mixed-**provider**, not just mixed-tier. Land that the per-node seam makes crossing providers the *same one-line move* as crossing tiers.

**Pre-flight:**

- A second provider key and model handle for the target class; the Demo 3 agent open. Fallback: a canned response + screenshot.

**Live script:**

1. Point at the node from Demo 2's class gap (the OCR/vision step). Change only its `init_chat_model("provider:model")` to the cross-provider handle — nothing else in the graph moves.
2. Run the agent end-to-end; show the vision node handled by the other provider and the rest still on Claude tiers.
3. Say it: *"Crossing a provider is the same one-line change as crossing a tier — the node doesn't care. The design work was **deciding** (Demos 1–2); the wiring is trivial."*

**What to highlight:**

- The `init_chat_model` seam makes **provider** and **tier** the same kind of choice mechanically — the hard part is the decision, not the plumbing.
- This is the PRD's literal target: *a mixed-model, mixed-provider agent, different models on different nodes.*

**If the demo misbehaves:**

- Fully optional and the most key-dependent demo. If the second provider is down, narrate the swap against a **screenshot** of a prior successful run — the point (one-line provider swap at the node) survives without the live call.

## Pacing notes for the teacher

- **Per-demo time (targets the objectives' ~75–100 minute, one-lecture budget):** Demo 0 ~4 min (whiteboard). Demo 1 ~12–15 min (reading the eval as a decision — the core method). Demo 2 ~8–10 min (the class gap; run the failure live, success can be canned). Demo 3 is the long live-code beat, ~18–22 min (per-node binding on a warm-up router then the agent). Demo 4 ~12–15 min (cost sum + latency path off the trace — the new idea; don't rush it). Demo 5 ~6–8 min and is the **trimmable/optional** one (drop to a screenshot or cut if keys/time are tight). Total ~60–75 min of demo, fitting the block with discussion.
- **If the lecture must split:** break after Demo 2 — part one is "the decision" (map, tier-by-eval, class gap; mostly reading, minimal live model), part two is "the build" (bind per node, budget, cross-provider — the live-code half).
- **Live-model / key budget:** Demos 1, 3, 4 need only `ANTHROPIC_API_KEY` (Claude tiers). Demos 2 and 5 need a second provider and are the ones to pre-can if keys are uncertain. Budget one re-run for Demo 3; Demo 4 reads a fixed trace.
- **The audience watches, doesn't participate.** Resist "which model would you pick here?" as a class exercise — that's the L14 lab pattern (stage 2), not a demo.

## Open authoring questions

- **Resolved (reuse, don't rebuild):** L14 reuses the `init_chat_model` seam, an existing graph (L05 router / L10 agent), the L12 trace, and the L13 eval set — see "Naming and tooling reconciliation." The only new machinery is per-node model binding and the heterogeneous cost/latency budget.
- **Decided (Claude-tier A/B is the cheap spine):** Demos 1, 3, 4 run on `ANTHROPIC_API_KEY` alone (Haiku 4.5 vs Sonnet 4.6). The cross-provider demos (2, 5) are gated and degrade to canned/screenshot, so a single-key or keyless run still teaches the whole lesson.
- <!-- *NEED INPUT*: the exact "higher-power tier" model for the strong-reasoner node (the course pinned Sonnet 4.6 + Haiku 4.5 but never committed a top tier). Matches the same marker in objectives.md. -->
- <!-- *NEED INPUT*: which second provider(s) the cohort has keys for, the exact Demo 2 capability-class artifact (vision image vs over-long document), and whether Demos 2/5 run live or ship canned. Matches the provider-keys marker in objectives.md. -->
- <!-- *NEED INPUT*: which graph the hands-on binds onto — an L03/L05 workflow vs the L10 agent — kept identical to objective 3's marker in objectives.md so stage 2 sees one decision, not two. -->
- <!-- *NEED INPUT*: overlap check with L25 (Evaluation revisited) once its roadmap exists — L14 uses eval to *choose* a model; L25 evaluates systems at scale. Keep the split so neither re-teaches the other. Matches objectives.md. -->
