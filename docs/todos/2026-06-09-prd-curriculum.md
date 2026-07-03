# 2026-06-09 — Mini-cut roadmap open items

Tracking list for the mini-cut roadmap authoring (L11 Tracing, L12 Evaluation,
**L04 Explicit graphs & workflows / DAGs (NEW)**, L14 Shallow LangGraph agent). Each item notes the
doc it lives in and the in-doc recommendation. Resolve items here or migrate them into the roadmap
docs as decisions land.

> **⚠️ Renumber done (this session):** a new **L04 "Explicit graphs & workflows (deterministic DAGs)"**
> lesson was inserted before the ReAct/shallow-agent lesson (workflows-before-agents). The old
> L04–L23 shifted to **L14–L24** across the PRD, roadmap docs, memory, and this file. The shallow
> agent is now **L14**. Separately discovered: an external merge (PR #10) had already added an
> **L16 Agent middleware** lesson and put Skills in the mini cut. **Also fixed (this session):** the
> pre-existing cross-ref drift in the L01–L10 roadmaps (older stale refs — e.g. L10 calling the
> shallow agent "L13"/deep agents "L15", L01 calling context-mgmt "L16", "evals (L11)") was
> reconciled semantically against the current PRD. Whole-tree topic↔number audit is clean.

> **Headline:** none of the items below block taking **L11 into stage 2**
> (`generate-materials-from-roadmap`). All four schema/structure blockers are resolved (see
> "Already decided"). What remains is cross-cutting defaults + lecture-pacing/teaching-depth,
> which a stage-2 author can settle while drafting.

---

## ✅ Already decided (for context — don't re-litigate)

- **Promote shared code to `common/`** — `common/agent_loop.py` (L10 loop → `run()`/`RunResult`),
  `common/tracing.py` (`TraceEvent`), `common/evals.py` (`EvalCase`/`Scorer`/runner),
  `common/tools.py` (`calculator`/`lookup`/`flaky_fetch`). L10 keeps the **inline build** (the
  teaching artifact); `common/` holds the **canonical reference copy** L11+ import.
- **LangGraph + native client** — framework lessons (L04, L14, L22, L23) use native `ChatAnthropic`
  inside graph nodes, NOT `PotatoLLMClient`; the departure is taught explicitly. Deps added:
  `langgraph>=1.2.4`, `langchain-anthropic>=1.4.4` (via `uv add`).
- **Trace schema** — approximate OpenTelemetry/Langfuse shape; `RunResult.trace: list[TraceEvent]` +
  `.to_jsonl()`; entry called a **span** (class `TraceEvent`, field `run_type: llm|tool|chain`).
- **Tracing tool = self-hosted Langfuse** (open-source, MIT). One shared instructor instance the
  cohort points at (no per-student seats). L11 adds a hands-on "export your trace → read it in
  Langfuse" step (objective 5); L14's LangGraph traces route to the SAME instance via the Langfuse
  callback handler. `langfuse` dep added via `uv add`. Infra → `docs/classroom-llm-management.md`.
- **Eval schema** — approximate LangSmith shape; `EvalCase` (Example: `inputs` +
  `reference_outputs`), `Scorer` (Evaluator → `EvalResult{key, score, comment}`),
  `evaluate(cases, scorers, samples=K)` → per-case pass rates.

---

## 🟡 Cross-cutting — decide once, applies to L11/L12/L04/L14

- [x] **Anchor model — DECIDED: Sonnet 4.6** for L11/L12/L04/L14 (inherits L01–L10 precedent; L04 additionally mixes Haiku 4.5 per node — see L04 block).
      **L12 uses Haiku 4.5 as a confirmed contrast** in the A/B demo: same eval set on both models,
      cheaper model's pass rate visibly drops → concrete, quantified "what a lower-powered model
      can/cannot do" (also grounds L12 objective-4 cost/capability reasoning; foreshadows L13).
      Sonnet-vs-Sonnet still covers the pure regression framing. Markers resolved in all three docs.
- [x] **Lecture durations — DECIDED** (in each lesson's doc): L11 ~75–100m · L12 ~75–100m · L04 ~75–100m · L14 ~90–120m, each one lecture with a split option if long.

---

## 🟢 Teaching-depth — all have an in-doc recommendation (safe to batch-accept)

### L11 (Tracing) — ✅ ALL RESOLVED
- [x] Hosted-tracer hands-on? → **DECIDED: yes — self-hosted Langfuse** (objective 5), concept-first then tooled. Additive/gated; objectives 1–4 stand alone.
- [x] Two-trace comparison: by eye vs. diff helper → **DECIDED: by eye first, then ~10-line diff helper**.
- [x] Trace minimalism vs. completeness → **DECIDED: small defensible field set; name what to leave out (prompt bodies, tracebacks, intermediate vars)**.
- [x] Industry standards depth → **DECIDED: real hands-on Langfuse** (supersedes "name-drop + screenshot"); schema is OTel/Langfuse-shaped.
- [x] Who authors the `common/` reference modules → **DECIDED: the L11 stage-2 pass** (owns `common/agent_loop.py` + `common/tools.py`, verifies parity with L10 inline build).
- [x] L10 bridge-demo overlap → **DECIDED: reinforce/extend, don't re-teach; L10 bridge stays a teaser**.
- [x] Lecture duration → **DECIDED: ~75–100 min, one lecture** (Langfuse step ~10–15 min, trimmable to a demo).
- [x] Langfuse instance: shared vs. local → **DECIDED: one shared instructor instance; local-Docker fallback for solo learners**.

### L12 (Evaluation) — ✅ ALL RESOLVED
- [x] Harness stays hand-rolled, Langfuse/hosted-eval → L24 → **DECIDED: yes** (name-drop only here).
- [x] How to quantify cost → **DECIDED: both — formula, then read live token numbers off a trace**.
- [x] Samples-per-case + when to introduce pass rate → **DECIDED: single pass/fail first, let a flaky case force sampling**.
- [x] LLM-as-judge depth → **DECIDED: one minimal illustrative judge, flagged "L24 is more rigorous"**.
- [x] Reuse L10/L11 tools → **DECIDED: yes, from `common/tools.py`**.
- [x] L11 overlap → **DECIDED: formalize the two-trace compare into an eval set; don't re-teach trace reading**.
- [x] L14 reuses L12 harness → **DECIDED: yes** (settled by shared `common/evals.py`).
- [x] L13 pre-link in mini cut → **DECIDED: parenthetical only; bridge points at L14**.
- [x] Lecture duration → **DECIDED: ~75–100 min, one lecture**.

### L04 (Explicit graphs & workflows / DAGs — NEW) — ✅ ALL RESOLVED
- [x] **User-input branching → DECIDED: included.** A conditional edge can route on derived data, a model classification, OR **direct user input** (the purest "you wire the flow" — no model in the routing decision). Added to objectives 2 & 3, vocabulary, main points, confusions. Interactive pause-and-ask-the-user variant (needs `interrupt` + checkpointer) deferred to **L17** (human-in-the-loop).
- [x] **Per-node model selection → DECIDED: included.** Each node binds its own `ChatAnthropic(model=...)` — **Haiku 4.5** for light steps (classify/route/extract), **Sonnet 4.6** for heavy steps. Shown via a mixed-model routing workflow + read off the Langfuse trace (each span shows its model + cost). L04 shows the *mechanism*; the *decision framework* (capability/latency/cost, budgets) stays **L13's** (Choosing model power). ⚠️ Overlap-with-L13 marker left in the doc; in the mini cut (L13 dropped) this is the first mixed-model exposure — kept light.
- [x] Anchor model → **DECIDED: Sonnet 4.6** (consistent with L14 for the workflow→agent compare).
- [x] Client → **DECIDED: native `ChatAnthropic`** — L04 is the *first* framework lesson, so the seam-departure now starts at L04 (provider-abstraction memory updated L14+→L04+).
- [x] Tracing → **DECIDED: route workflow traces to L11's shared Langfuse** (callback handler).
- [x] Running-example domain → **DECIDED: support-ticket pipeline (chaining) + billing/technical/general (routing)**; stage 2 may reuse L10/L11 tools inside nodes (optional).
- [x] Do workflow nodes reuse `common/tools.py`? → **DECIDED: L04 nodes are LLM-calls + plain Python; defer model-driven tool-calling to L14** (keeps the workflow/agent line clean).
- [x] Optional "eval-the-workflow" beat reusing `common/evals.py` → **DECIDED: one short optional beat** (deterministic = trivially testable).
- [x] Graph visualization → **DECIDED: render each workflow's diagram once** ("control flow as data").
- [x] Parallel branches (fan-out/in) → **DECIDED: forward-pointer only; build stays linear chain + single-choice routing**.
- [x] L10 prereq → **DECIDED: reference for contrast, don't depend on it** (a workflow is upstream of an agent).
- [x] L04↔L14 overlap → **DECIDED: intentional** per "keep both self-contained"; vocab agrees verbatim; L14 intro calls back to L04.
- [x] Lecture duration → **DECIDED: ~75–100 min** (chaining + routing builds).

### L14 (Shallow LangGraph agent) — ✅ ALL RESOLVED
- [x] Prebuilt vs. hand-assembled `StateGraph` → **DECIDED: hand-assemble first, then reveal prebuilt as "same thing packaged"**.
- [x] State beyond messages → **DECIDED: messages + one counter (for reducers/typing); richer state → L15+/L19**.
- [x] Single-model anchor → **DECIDED: Sonnet 4.6**, defer model-power to L13 (full course).
- [x] How much graph viz / streamed trace to show → **DECIDED: route graph traces to L11's same self-hosted Langfuse** (callback handler) + render the graph diagram once.
- [x] Tracing integration path → **DECIDED: Langfuse callback handler** (course-wide tracer; LangSmith's tighter integration is the accepted trade-off).
- [x] Persistence / checkpointing → **DECIDED: out of scope; forward-pointer to L18/L19** (also the mechanism behind L17's interrupt/resume).
- [x] L10 Demo-4 overlap → **DECIDED: deliver the framework rebuild in full; L10 was the teaser**.
- [x] L14→L15 boundary → **DECIDED: L14 owns one-graph/one-loop/state; L15 owns named patterns**; ReAct framed in L15 as a *pattern over* L14 primitives (revisit when L15 roadmap is authored).

---

## 🔵 Forward-coordination (resolve when later roadmaps are written)

- [x] L12→L14 harness reuse — **DECIDED: yes** (settled by `common/evals.py`; confirmed in L12 doc).
- [x] L12 pre-linking L13 in the mini cut → **DECIDED: parenthetical mention only**.
- [x] L14→L15 boundary — **DECIDED** in the L14 doc: L14 owns one-graph/one-loop/state, L15 owns named patterns; ReAct framed as a *pattern over* L14 primitives. *(applies when the L15 roadmap is authored)*

---

## ⚪ Classroom infra (separate track — `docs/classroom-llm-management.md`, not curriculum)

- [ ] **Stand up the shared Langfuse instance** — Docker Compose (Langfuse + Postgres + ClickHouse)
      on an always-on VM; decide host/owner; issue per-student project keys; wire URL+keys through
      `common/config.py`. *(DECIDED tool; deployment is the open work.)*
- [ ] Re-check Langfuse license/terms post-ClickHouse-acquisition (Jan 2026) before a cohort relies on it.
- [ ] One shared instance vs. per-student local Docker → **rec: shared instance, local as solo fallback**.
- [ ] Verify current **OpenRouter BYOK surcharge %**.
- [ ] **Cohort size + per-student budget** → drives soft (Workspaces) vs. hard (proxy) caps.
- [ ] **Key provisioning/rotation owner** — manual Console vs. Admin API automation.
- [ ] **Anthropic-only vs. multi-provider** in practice (if Anthropic-only, OpenRouter's edge doesn't apply).

---

## Not-yet-written roadmap artifacts (stage 1 remaining)

- [x] **L22 (Skills) — STAGE 1 COMPLETE** (objectives + demos, this session). Mini-cut capstone (final
      lesson); concept-first (hand-roll a JIT skill loader on the L14 agent) then real Anthropic Agent
      Skills `SKILL.md`. Taxonomy: tool = *called*, skill = *read on demand*, system prompt = *always seen*.
      Markers open in both docs (tooling, exact SKILL.md format, depth/duration target).
      ⚠️ L22's "final lesson / capstone" self-framing is now **stale** — L23 follows it in the mini cut;
      reconcile when L22 is regenerated (see L23 item 1).
- [x] **L23 (Skill patterns & composition) — STAGE 1 COMPLETE** (objectives + demos, 2026-07-01).
      Composition capstone of the skills thread; classify 3 archetypes → author each → compose (sequential
      handoff + shared sub-skill) → reason about the dependency graph & JIT loading → 3 anti-patterns.
      Runtime = L04/L14 LangGraph agent + `list_skills`/`load_skill` LangChain tools. Open items tracked
      in **[2026-07-01-l21-skill-composition.md](2026-07-01-l21-skill-composition.md)** (~15 items; 3 need a
      human call, rest confirm-the-default).
- [ ] `demos_or_activities.md` for **L11**, **L12**, **L04**, **L14** (objectives done; demos not started).
- [ ] Stage 2 (`generate-materials-from-roadmap`) for L11/L12/L04/L14/L22 — also authors the `common/`
      reference modules per the decided schemas.
- [x] **Pre-existing cross-ref drift in L01–L10 roadmaps** — DONE: reconciled semantically against
      the current PRD (43 refs across 11 files); whole-tree topic↔number audit clean.
