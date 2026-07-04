# L14: Choosing models & providers for the task

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (lesson-plan row L14).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).
> Preceding lesson: [L13 Evaluation: first pass](../L13/objectives.md). Following lesson: L15 LangGraph design patterns (roadmap not yet written). **Track:** L14 is **full-track only** — the mini cut drops it (in the mini plan L13 hands directly to L04), so this lesson can assume the full arc around it.

> **Framing (read first).** Up to here the course has run on **one anchor model — Claude Sonnet 4.6 — with Haiku 4.5 as a cheap contrast** (the L13 A/B). L14 is where **model and provider choice becomes a first-class design decision** rather than a fixed default. The reframe to land: an agent is not "a model plus a graph" — it is a **graph whose nodes can each bind a different model**, and picking the right one per node — across **providers** (who is differentially strong) and **power tiers** (how capable/expensive within a provider) — is an engineering choice you **measure with the L13 eval instrument**, not one you assert. This is a **concept + a design method**, not a vendor tour: the durable skill is matching a task to a capability class and a tier and defending it on capability, latency, cost, and context — not memorizing today's model roster.

## Where this lesson sits

By L13, students can **build an agent (L10/L11), trace it (L12), and evaluate it (L13)** — including L13's headline move: running the *same* eval set against **two models (Sonnet 4.6 vs Haiku 4.5)** as two Langfuse experiments and reading which one's pass rate holds up. L14 picks up exactly that thread. L13 answered "is model A better than model B *here*?" with a number; L14 turns that one A/B into a **general selection method**: for each task — or each *step* of an agent — which provider and which power tier is the right tool, and how do you defend the choice?

L14 also pays off a foreshadow planted all the way back in **[L01](../L01/objectives.md)**: the local GPT-2 124M → 355M → 774M ladder (a bigger model sharpening the next-token distribution) was taught as an intuition pump for *"model scale changes capability."* L14 is where that intuition becomes a design decision across real models and providers. And it builds directly on the **graph model** the course has used since L03: [L03](../L03/objectives.md) made a single LLM call a **node**; [L04](../L04/objectives.md)/[L05](../L05/objectives.md) wired nodes into forward graphs; [L10](../L10/objectives.md) made the agent a *cyclic* graph. Because a model is bound **at the node**, "choose a model for the task" becomes, concretely, **"bind a model per node"** — a small fast model on a routing node, a strong reasoner on a planning node, a vision model on an OCR node — all inside one graph.

Up to now the course has been deliberately **single-provider** (Claude, reached through the `common/config.py` key seam and the LangChain `init_chat_model` / `bind_tools` API the tool lessons adopted). L14 is where the aperture opens to **multiple providers**, because no single provider is best at everything: one may lead on vision/OCR, another on very-long-context, another on cheap high-throughput execution. The lesson teaches students to **reason in capability classes and tiers**, so the skill survives the next model release.

## The landscape: two axes — provider × power tier (the organizing map)

Before any code, the lecture draws the map the lesson hangs on. "Choosing a model" is **two decisions, not one**:

- **Which provider** — providers are *differentially strong*. Sort the decision by **capability class**, not brand loyalty:
  - **vision / OCR / document understanding** — reading images, scans, PDFs, charts, screenshots;
  - **very-long-context** — fitting a large corpus (a whole codebase, a long contract) in one window;
  - **reasoning / planning** — multi-step decomposition, hard logic, careful tool orchestration;
  - **cheap, high-throughput execution** — fast, low-cost calls for routing, classification, extraction, and the boring middle of a pipeline.
- **Which power tier** — *within* a provider, and the point the PRD stresses: the choice is **not just a size class inside one vendor**. Every major provider ships a **tier ladder** — roughly a *small/fast/cheap* tier, a *balanced* tier, and a *large/most-capable* tier (for Claude in this course: **Haiku 4.5 → Sonnet 4.6 → a higher-power tier**). The tier trades **capability against latency and cost**.

**The one rule to teach:** match the task (or the agent *step*) to the **cell** of that grid — the provider whose strength fits the capability class, at the *lowest tier that still passes your eval*. Defaulting every node to your favorite provider's top tier is the common, expensive mistake; forcing a task onto one provider when another is plainly better at that capability class is the other.

## Prerequisites

Students arriving at L14 should already be able to:

- Build and run an agent as a graph — a forward workflow (L04/L05) and the ReAct cyclic graph (L10), or its `create_agent` form ([L11](../L11/objectives.md)) — and understand that a **node** is the unit of orchestration (L03). L14 binds models *at the node*, so a student shaky on the node abstraction should revisit L03–L05 first.
- Drive a chat model through the course seam: `init_chat_model("provider:model")` / `bind_tools(...)`, with keys loaded via `common/config.py` (the tool lessons L07/L08 and the agent lessons). Binding a *different* model is a one-line change at that seam — the mechanical enabler of this whole lesson.
- Trace a run and read per-call **token usage** and latency off it (L12), and **evaluate** a run with an eval set + Langfuse experiment — including the **Sonnet-vs-Haiku A/B** and the cost reasoning (L13, objectives 3–4). L14 turns that A/B into a selection *method*; a student who cannot run the L13 experiment cannot do L14's core move.
- Estimate per-call cost from tokens (L01, L13). L14 sums this across *heterogeneous* nodes.

## Learning objectives

By the end of L14, a student should be able to:

1. **Survey the major model providers by differential strength, in capability classes.** Concretely:
   - Name the **capability classes** a task can fall into — vision/OCR & document understanding, very-long-context, reasoning/planning, cheap high-throughput execution — and, for each, the *kind* of provider/model that tends to lead. Teach these as **classes**, not a vendor leaderboard that dates the moment it's written.
   - Read a task and say *which class it is*: "extract fields from a scanned invoice" → vision/OCR; "summarize a 300-page contract" → long-context; "route a request to one of six handlers" → cheap high-throughput; "plan a multi-tool research task" → reasoning/planning.
   - State plainly *why single-provider defaulting fails*: no one provider tops every class, so an all-Claude (or all-anyone) agent leaves capability, cost, or latency on the table for at least some steps.
   - <!-- *NEED INPUT*: the concrete provider/model roster the cohort should name per capability class, and whether to name specific non-Anthropic models at all given they date fast. Recommendation: teach the classes durably and keep a short, clearly-dated "current picks" callout the instructor refreshes each cohort, rather than baking a roster into this roadmap. -->

2. **Match a task or agent step to a provider *and* a power tier — the lowest tier that still passes.** Concretely:
   - Make the **two-axis choice** explicit (provider by capability class, tier by capability-vs-cost) and defend it against the alternatives, out loud.
   - Reuse **L13's instrument to decide, not guess**: run the *same* eval set against a candidate model at two tiers (the L13 Sonnet-vs-Haiku experiment, generalized) and pick the cheapest tier whose **pass rate** clears the bar. "Measure, don't assume" is the direct through-line from L13.
   - Weigh **capability against latency, cost, and context length** as first-class constraints: a stronger tier that doubles latency on the user's hot path may lose to a weaker tier that passes; a cheaper model with a smaller context window may not even *fit* the task, which is a hard disqualifier before capability is even discussed.
   - Name when to **escalate** a tier (the eval fails at the cheap tier) and when to **downgrade** (the eval still passes at a cheaper one) — the L13 ratchet, applied to model choice instead of regressions.

3. **Design a mixed-model, mixed-provider agent by binding a model per graph node.** Concretely:
   - Take a graph students already have — a forward workflow from L04/L05 or the ReAct agent from L10 — and **bind a different model to different nodes**: a small fast model on a routing/classification node, a strong reasoner on a planning node, a vision model on an OCR/ingest node, a cheap model on the high-volume execution node.
   - Do it through the seam the course already uses: `init_chat_model("provider:model")` (keys via `common/config.py`), so a node's model is a **parameter, not a rewrite** — the same node, a different bound model. This is the concrete meaning of "choose a model for the task": **choose it per node**.
   - Recognize that this is *why* L03–L05 made the node the unit of orchestration and *why* the model binds at the node — a foreshadow the course planted at L04 (a per-node cheap-model contrast) now paid off in full.
   - <!-- *NEED INPUT*: which graph the hands-on binds models onto — a simple L04/L05 forward workflow (no tools, cheapest to run and reason about) or the L10 ReAct agent graph (richer, and a mixed-model *agent* is the PRD's stated target). Recommendation: demo on the L10 agent so "mixed-model agent" is literal, with a simpler L05 router as a warm-up. -->
   - <!-- *NEED INPUT*: real multi-provider calls need more than ANTHROPIC_API_KEY (e.g. an OpenAI key, or a vision-capable provider's key). Confirm which provider keys the cohort has, and whether the live mixed-provider demo runs for real or ships with a scripted/canned fallback (the FakeModel stance from L12/L13) so a keyless restart-and-run-all still completes. Surface any new SDK dependency to add via uv rather than assuming it. -->

4. **Estimate the cost and latency budget of a multi-step, multi-model agent.** Concretely:
   - Extend L13's eval-cost arithmetic and L01's per-call cost to a *mixed-model* run: each node contributes **its own model's price × its calls**, so the agent's cost is a **sum over heterogeneous nodes**, not one model's rate × total calls.
   - Add **latency** as a first-class budget the course hasn't foregrounded: the wall-clock of an agent is the time along its **critical path**, so a top-tier reasoner on the hot path can dominate latency even as one node among many. Contrast **"cost per run" (a sum)** with **"latency per run" (a path)** — different arithmetic, different design levers.
   - Read the real numbers where they already live — the **per-node token counts on the Langfuse trace** (L12) — and multiply through, then sanity-check against a back-of-envelope (per node: `calls × price`; latency: the slowest path). Grounded in trace data, not hand-waving, exactly as L13 did for a single model.
   - Decide, for a concrete agent, *where each dollar and each second goes* and **which node to downgrade first** — the design payoff of the whole lesson.

## What "choosing a model" is (vocabulary the lecture must establish)

Define these explicitly and reuse them verbatim through the labs and into L15:

- **Provider** — the vendor/API behind a model (Anthropic, OpenAI, Google, …); reached in this course through `init_chat_model("provider:model")` and the `common/config.py` key seam. Choosing a provider is choosing *whose* strength you're buying.
- **Power tier** — a provider's capability ladder (small/fast/cheap → balanced → large/most-capable); for Claude in this course, **Haiku 4.5 → Sonnet 4.6 → a higher-power tier**. The tier is the capability-vs-cost dial *within* a provider.
- **Capability class** — the kind of strength a task needs: vision/OCR, long-context, reasoning/planning, cheap high-throughput execution. You pick a provider by matching its strength to the task's class.
- **Model-per-node binding** — binding a specific model to a specific graph node (L03–L05 / L10), so one agent runs several models. The concrete unit of "choose a model for the task."
- **Mixed-model / mixed-provider agent** — one agent whose nodes bind different models and/or providers (e.g. vision on the OCR node, a strong reasoner on the planning node, a cheap model on execution).
- **Cost budget vs latency budget** — cost is a **sum** over the run's calls (each at its node's model price); latency is the time along the **critical path**. Two different computations that a mixed-model agent forces you to reason about separately.
- **"Lowest tier that passes"** — the selection rule: the cheapest/fastest model whose eval **pass rate** clears the bar for that step. The L13 ratchet, aimed at model choice.

## Main points the lecture should land

- **No single provider wins every class.** Vision/OCR, long-context, reasoning, and cheap throughput are *different* strengths; an agent that defaults every step to one provider is leaving capability, cost, or latency on the table somewhere. Say this first — it's the reason the lesson exists.
- **Choose per node, not per agent.** Because the model binds at the graph node (L03–L05), "which model?" is answered *per step*. A routing node and a planning node have different needs and should not share a tier by default.
- **Measure the choice; don't assert it.** L13's eval set *is* the decision procedure — run the candidates, read the pass rates, pick the cheapest that passes. Public benchmarks are a prior, not a verdict for *your* task. This is the L12→L13→L14 spine: trace it, judge it, *then* choose with the judgment.
- **The lowest tier that passes.** Escalate only when the eval fails; downgrade whenever it still passes. Reaching for the top tier "to be safe" is the most common and most expensive default.
- **Cost is a sum; latency is a path.** They are different budgets on different math. A cheaper model can be slower; a faster model can be pricier. A mixed-model agent makes you compute both — cost across all nodes, latency along the critical path.
- **The method outlives the roster.** Capability classes and tier ladders are durable; specific model names and prices date fast. Teach the *reasoning*, and keep any concrete roster as a dated, refreshable callout — not a fact baked into the curriculum.

## Common student confusions to watch for

- *"Bigger is always better."* No — a top-tier model on a routing node burns cost and latency for no capability gain. The eval tells you when the cheap tier already passes; capability you don't need is waste.
- *"Pick one model for the whole agent."* That's the single-provider default the lesson exists to break. Different nodes have different capability classes; one model rarely fits them all at the right cost.
- *"More providers is inherently better (or inherently worse)."* Mixing providers is justified by a **capability-class gap**, not novelty — and not fear of complexity. If one provider passes every step at the right tier, use it; if a step needs vision another provider leads on, reach across.
- *"Cost and latency are the same knob."* They are not. Budget them separately — a sum of per-node prices vs the time along the critical path — because the cheapest model is not always the fastest.
- *"The benchmark leaderboard picks my model."* Public benchmarks are a *prior*. Your eval set on *your* cases is the decision (the L13 lesson, restated for model choice).
- *"Context length is free."* A bigger context window costs tokens and latency, and doesn't help if the model is weaker at the task. **Fitting the input is necessary, not sufficient** — a model can fit a 300-page contract and still summarize it worse than a stronger one.

## Bridge to L15

L15 (**LangGraph design patterns**) names the agent architectures — ReAct, plan-and-execute, supervisor, hierarchical, state-machine routing — and their trade-offs. L14 hands L15 the **model-selection layer underneath those patterns**: once you can *bind a model per node*, patterns like supervisor/hierarchical become the natural place to apply it — a cheap router-supervisor delegating to a strong-reasoner worker is a mixed-model design, not just a topology. Say the split plainly: **L14 = which model per node; L15 = how the nodes are arranged.**

Also signpost **L25 (Evaluation revisited)**: it scales L13/L14's model comparison to multi-step and multi-agent systems (per-node vs end-to-end metrics, LLM-as-judge done rigorously). L14's per-node model choice is exactly what L25 later evaluates at scale — so L14 is where students *make* the choice, L25 is where they *audit* it on complex systems. Encourage students to keep the mixed-model agent they build here as an L25 subject.

## Open authoring questions

- **Decided (track):** L14 is **full-track only** — the mini cut drops it (in mini, L13 hands directly to L04). Keep the lesson self-contained so the full track reads continuously; do not make any later *mini* lesson depend on L14.
- **Decided (anchor + contrast carried in):** teach tiers with the course's own models as the running example — **Haiku 4.5 (cheap/fast) → Sonnet 4.6 (balanced anchor) → a higher-power tier** — inheriting the L01–L13 precedent, then open the aperture to other providers as *capability classes*. **Do not re-anchor the course** off Sonnet 4.6.
- **Decided (method over roster):** L14 teaches a **selection method** (capability class × tier, decided by eval), not a memorize-this-table vendor tour. Specific cross-provider model names and pricing belong in a dated, refreshable callout, not in this roadmap.
- **Decided (measure with L13's instrument):** the way to *choose* is to run L13's eval set across candidates — L14 **reuses `common/evals.py` + the Langfuse experiment**, it does not invent a new decision procedure. This keeps the L12→L13→L14 arc tight.
- **Decided (duration, consistent with the arc):** one lecture in the L12/L13 range (~75–100 minutes) including a code-along that binds two or three models to nodes of an existing graph and reads the mixed cost/latency budget off the trace. If keys or time are tight, trim the *live multi-provider* call to a demo and keep the Claude-tier A/B (which needs only `ANTHROPIC_API_KEY`).
- <!-- *NEED INPUT*: the exact "higher-power tier" model the cohort will use for the strong-reasoner example — the course pinned Sonnet 4.6 + Haiku 4.5 but never committed to a top tier. -->
- <!-- *NEED INPUT*: the concrete non-Anthropic providers/models to name per capability class, or whether to stay provider-agnostic in the roadmap and only *demo* across Claude tiers, describing other providers in the abstract. -->
- <!-- *NEED INPUT*: which graph the hands-on binds models onto — an L04/L05 workflow vs the L10 agent (see objective 3) — and the provider keys / offline fallback for a live mixed-provider run (see objective 3's second marker). -->
- <!-- *NEED INPUT*: overlap check with L25 (Evaluation revisited) once its roadmap exists — L14 uses eval to *choose* a model, L25 evaluates systems at scale. Confirm the split so neither re-teaches the other. -->
