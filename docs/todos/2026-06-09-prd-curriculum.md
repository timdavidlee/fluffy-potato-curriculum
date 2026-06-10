# 2026-06-09 — Mini-cut roadmap open items

Tracking list for the mini-cut roadmap authoring (L08 Tracing, L09 Evaluation,
**L11 Explicit graphs & workflows / DAGs (NEW)**, L12 Shallow LangGraph agent). Each item notes the
doc it lives in and the in-doc recommendation. Resolve items here or migrate them into the roadmap
docs as decisions land.

> **⚠️ Renumber done (this session):** a new **L11 "Explicit graphs & workflows (deterministic DAGs)"**
> lesson was inserted before the ReAct/shallow-agent lesson (workflows-before-agents). The old
> L11–L21 shifted to **L12–L22** across the PRD, roadmap docs, memory, and this file. The shallow
> agent is now **L12**. Separately discovered: an external merge (PR #10) had already added an
> **L14 Agent middleware** lesson and put Skills in the mini cut. **Also fixed (this session):** the
> pre-existing cross-ref drift in the L01–L07 roadmaps (older stale refs — e.g. L07 calling the
> shallow agent "L10"/deep agents "L13", L01 calling context-mgmt "L14", "evals (L08)") was
> reconciled semantically against the current PRD. Whole-tree topic↔number audit is clean.

> **Headline:** none of the items below block taking **L08 into stage 2**
> (`generate-materials-from-roadmap`). All four schema/structure blockers are resolved (see
> "Already decided"). What remains is cross-cutting defaults + lecture-pacing/teaching-depth,
> which a stage-2 author can settle while drafting.

---

## ✅ Already decided (for context — don't re-litigate)

- **Promote shared code to `common/`** — `common/agent_loop.py` (L07 loop → `run()`/`RunResult`),
  `common/tracing.py` (`TraceEvent`), `common/evals.py` (`EvalCase`/`Scorer`/runner),
  `common/tools.py` (`calculator`/`lookup`/`flaky_fetch`). L07 keeps the **inline build** (the
  teaching artifact); `common/` holds the **canonical reference copy** L08+ import.
- **LangGraph + native client** — framework lessons (L11, L12, L20, L21) use native `ChatAnthropic`
  inside graph nodes, NOT `PotatoLLMClient`; the departure is taught explicitly. Deps added:
  `langgraph>=1.2.4`, `langchain-anthropic>=1.4.4` (via `uv add`).
- **Trace schema** — approximate OpenTelemetry/Langfuse shape; `RunResult.trace: list[TraceEvent]` +
  `.to_jsonl()`; entry called a **span** (class `TraceEvent`, field `run_type: llm|tool|chain`).
- **Tracing tool = self-hosted Langfuse** (open-source, MIT). One shared instructor instance the
  cohort points at (no per-student seats). L08 adds a hands-on "export your trace → read it in
  Langfuse" step (objective 5); L12's LangGraph traces route to the SAME instance via the Langfuse
  callback handler. `langfuse` dep added via `uv add`. Infra → `docs/classroom-llm-management.md`.
- **Eval schema** — approximate LangSmith shape; `EvalCase` (Example: `inputs` +
  `reference_outputs`), `Scorer` (Evaluator → `EvalResult{key, score, comment}`),
  `evaluate(cases, scorers, samples=K)` → per-case pass rates.

---

## 🟡 Cross-cutting — decide once, applies to L08/L09/L11/L12

- [x] **Anchor model — DECIDED: Sonnet 4.6** for L08/L09/L11/L12 (inherits L01–L07 precedent; L11 additionally mixes Haiku 4.5 per node — see L11 block).
      **L09 uses Haiku 4.5 as a confirmed contrast** in the A/B demo: same eval set on both models,
      cheaper model's pass rate visibly drops → concrete, quantified "what a lower-powered model
      can/cannot do" (also grounds L09 objective-4 cost/capability reasoning; foreshadows L10).
      Sonnet-vs-Sonnet still covers the pure regression framing. Markers resolved in all three docs.
- [x] **Lecture durations — DECIDED** (in each lesson's doc): L08 ~75–100m · L09 ~75–100m · L11 ~75–100m · L12 ~90–120m, each one lecture with a split option if long.

---

## 🟢 Teaching-depth — all have an in-doc recommendation (safe to batch-accept)

### L08 (Tracing) — ✅ ALL RESOLVED
- [x] Hosted-tracer hands-on? → **DECIDED: yes — self-hosted Langfuse** (objective 5), concept-first then tooled. Additive/gated; objectives 1–4 stand alone.
- [x] Two-trace comparison: by eye vs. diff helper → **DECIDED: by eye first, then ~10-line diff helper**.
- [x] Trace minimalism vs. completeness → **DECIDED: small defensible field set; name what to leave out (prompt bodies, tracebacks, intermediate vars)**.
- [x] Industry standards depth → **DECIDED: real hands-on Langfuse** (supersedes "name-drop + screenshot"); schema is OTel/Langfuse-shaped.
- [x] Who authors the `common/` reference modules → **DECIDED: the L08 stage-2 pass** (owns `common/agent_loop.py` + `common/tools.py`, verifies parity with L07 inline build).
- [x] L07 bridge-demo overlap → **DECIDED: reinforce/extend, don't re-teach; L07 bridge stays a teaser**.
- [x] Lecture duration → **DECIDED: ~75–100 min, one lecture** (Langfuse step ~10–15 min, trimmable to a demo).
- [x] Langfuse instance: shared vs. local → **DECIDED: one shared instructor instance; local-Docker fallback for solo learners**.

### L09 (Evaluation) — ✅ ALL RESOLVED
- [x] Harness stays hand-rolled, Langfuse/hosted-eval → L22 → **DECIDED: yes** (name-drop only here).
- [x] How to quantify cost → **DECIDED: both — formula, then read live token numbers off a trace**.
- [x] Samples-per-case + when to introduce pass rate → **DECIDED: single pass/fail first, let a flaky case force sampling**.
- [x] LLM-as-judge depth → **DECIDED: one minimal illustrative judge, flagged "L22 is more rigorous"**.
- [x] Reuse L07/L08 tools → **DECIDED: yes, from `common/tools.py`**.
- [x] L08 overlap → **DECIDED: formalize the two-trace compare into an eval set; don't re-teach trace reading**.
- [x] L12 reuses L09 harness → **DECIDED: yes** (settled by shared `common/evals.py`).
- [x] L10 pre-link in mini cut → **DECIDED: parenthetical only; bridge points at L12**.
- [x] Lecture duration → **DECIDED: ~75–100 min, one lecture**.

### L11 (Explicit graphs & workflows / DAGs — NEW) — ✅ ALL RESOLVED
- [x] **User-input branching → DECIDED: included.** A conditional edge can route on derived data, a model classification, OR **direct user input** (the purest "you wire the flow" — no model in the routing decision). Added to objectives 2 & 3, vocabulary, main points, confusions. Interactive pause-and-ask-the-user variant (needs `interrupt` + checkpointer) deferred to **L15** (human-in-the-loop).
- [x] **Per-node model selection → DECIDED: included.** Each node binds its own `ChatAnthropic(model=...)` — **Haiku 4.5** for light steps (classify/route/extract), **Sonnet 4.6** for heavy steps. Shown via a mixed-model routing workflow + read off the Langfuse trace (each span shows its model + cost). L11 shows the *mechanism*; the *decision framework* (capability/latency/cost, budgets) stays **L10's** (Choosing model power). ⚠️ Overlap-with-L10 marker left in the doc; in the mini cut (L10 dropped) this is the first mixed-model exposure — kept light.
- [x] Anchor model → **DECIDED: Sonnet 4.6** (consistent with L12 for the workflow→agent compare).
- [x] Client → **DECIDED: native `ChatAnthropic`** — L11 is the *first* framework lesson, so the seam-departure now starts at L11 (provider-abstraction memory updated L12+→L11+).
- [x] Tracing → **DECIDED: route workflow traces to L08's shared Langfuse** (callback handler).
- [x] Running-example domain → **DECIDED: support-ticket pipeline (chaining) + billing/technical/general (routing)**; stage 2 may reuse L07/L08 tools inside nodes (optional).
- [x] Do workflow nodes reuse `common/tools.py`? → **DECIDED: L11 nodes are LLM-calls + plain Python; defer model-driven tool-calling to L12** (keeps the workflow/agent line clean).
- [x] Optional "eval-the-workflow" beat reusing `common/evals.py` → **DECIDED: one short optional beat** (deterministic = trivially testable).
- [x] Graph visualization → **DECIDED: render each workflow's diagram once** ("control flow as data").
- [x] Parallel branches (fan-out/in) → **DECIDED: forward-pointer only; build stays linear chain + single-choice routing**.
- [x] L07 prereq → **DECIDED: reference for contrast, don't depend on it** (a workflow is upstream of an agent).
- [x] L11↔L12 overlap → **DECIDED: intentional** per "keep both self-contained"; vocab agrees verbatim; L12 intro calls back to L11.
- [x] Lecture duration → **DECIDED: ~75–100 min** (chaining + routing builds).

### L12 (Shallow LangGraph agent) — ✅ ALL RESOLVED
- [x] Prebuilt vs. hand-assembled `StateGraph` → **DECIDED: hand-assemble first, then reveal prebuilt as "same thing packaged"**.
- [x] State beyond messages → **DECIDED: messages + one counter (for reducers/typing); richer state → L13+/L17**.
- [x] Single-model anchor → **DECIDED: Sonnet 4.6**, defer model-power to L10 (full course).
- [x] How much graph viz / streamed trace to show → **DECIDED: route graph traces to L08's same self-hosted Langfuse** (callback handler) + render the graph diagram once.
- [x] Tracing integration path → **DECIDED: Langfuse callback handler** (course-wide tracer; LangSmith's tighter integration is the accepted trade-off).
- [x] Persistence / checkpointing → **DECIDED: out of scope; forward-pointer to L16/L17** (also the mechanism behind L15's interrupt/resume).
- [x] L07 Demo-4 overlap → **DECIDED: deliver the framework rebuild in full; L07 was the teaser**.
- [x] L12→L13 boundary → **DECIDED: L12 owns one-graph/one-loop/state; L13 owns named patterns**; ReAct framed in L13 as a *pattern over* L12 primitives (revisit when L13 roadmap is authored).

---

## 🔵 Forward-coordination (resolve when later roadmaps are written)

- [x] L09→L12 harness reuse — **DECIDED: yes** (settled by `common/evals.py`; confirmed in L09 doc).
- [x] L09 pre-linking L10 in the mini cut → **DECIDED: parenthetical mention only**.
- [x] L12→L13 boundary — **DECIDED** in the L12 doc: L12 owns one-graph/one-loop/state, L13 owns named patterns; ReAct framed as a *pattern over* L12 primitives. *(applies when the L13 roadmap is authored)*

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

- [ ] `demos_or_activities.md` for **L08**, **L09**, **L11**, **L12** (objectives done; demos not started).
- [ ] Stage 2 (`generate-materials-from-roadmap`) for L08/L09/L11/L12 — also authors the `common/`
      reference modules per the decided schemas.
- [x] **Pre-existing cross-ref drift in L01–L07 roadmaps** — DONE: reconciled semantically against
      the current PRD (43 refs across 11 files); whole-tree topic↔number audit clean.
