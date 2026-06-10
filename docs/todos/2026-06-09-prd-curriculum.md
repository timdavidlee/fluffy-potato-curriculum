# 2026-06-09 — Mini-cut roadmap open items

Tracking list for the mini-cut roadmap authoring (L08 Tracing, L09 Evaluation,
L11 Shallow LangGraph agent). Each item notes the doc it lives in and the in-doc recommendation.
Resolve items here or migrate them into the roadmap docs as decisions land.

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
- **LangGraph + native client** — framework lessons (L11, L18, L19) use native `ChatAnthropic`
  inside graph nodes, NOT `PotatoLLMClient`; the departure is taught explicitly. Deps added:
  `langgraph>=1.2.4`, `langchain-anthropic>=1.4.4` (via `uv add`).
- **Trace schema** — approximate LangSmith shape; `RunResult.trace: list[TraceEvent]` +
  `.to_jsonl()`; entry called a **span** (class `TraceEvent`, field `run_type: llm|tool|chain`).
- **Eval schema** — approximate LangSmith shape; `EvalCase` (Example: `inputs` +
  `reference_outputs`), `Scorer` (Evaluator → `EvalResult{key, score, comment}`),
  `evaluate(cases, scorers, samples=K)` → per-case pass rates.

---

## 🟡 Cross-cutting — decide once, applies to L08/L09/L11

- [ ] **Anchor model.** Effectively decided by precedent (`project_anchor_model` memory:
      Sonnet 4.6 anchor L01–L07; Haiku 4.5 cheap-contrast for L03/L09). Implied default:
      **L08 & L11 → Sonnet 4.6; L09 → Sonnet 4.6 + Haiku 4.5 for the A/B regression demo.**
      → Just needs "yes, inherit precedent." (L08/L09/L11 open Qs)
- [ ] **Lecture durations** — L08 ~75–100m · L09 ~75–100m · L11 ~90–120m. Confirm or split each.

---

## 🟢 Teaching-depth — all have an in-doc recommendation (safe to batch-accept)

### L08 (Tracing)
- [ ] Hosted-tracer hands-on? → **rec: no**, name-drop forward pointer only.
- [ ] Two-trace comparison: by eye vs. diff helper → **rec: by eye first, then ~10-line diff helper**.
- [ ] Trace minimalism vs. completeness → **rec: small defensible field set; name what to leave out**.
- [ ] Industry standards depth → **rec: name-drop + at most one annotated screenshot**.
- [ ] Who authors the `common/` reference modules → **rec: the L08 stage-2 pass**.
- [ ] L07 bridge-demo overlap → **rec: reinforce/extend, don't re-teach the loop**.

### L09 (Evaluation)
- [ ] Stays framework-free, hosted-eval → L20 → **rec: yes**.
- [ ] How to quantify cost → **rec: show formula, then read live token numbers off a trace**.
- [ ] Samples-per-case + when to introduce pass rate → **rec: single pass/fail first, let a flaky case force sampling**.
- [ ] LLM-as-judge depth → **rec: one tiny example, flagged "L20 is more rigorous"**.
- [ ] Reuse L07/L08 tools → **rec: yes**.
- [ ] L08 overlap → **rec: formalize the two-trace compare into an eval set; don't re-teach trace reading**.

### L11 (Shallow LangGraph agent)
- [ ] Prebuilt vs. hand-assembled `StateGraph` → **rec: hand-assemble first, then reveal prebuilt as "same thing packaged"**.
- [ ] State beyond messages → **rec: messages + one counter (for reducers/typing); richer state → L12+/L15**.
- [ ] Single-model anchor → **rec: yes, defer model-power to L10 (full course)**.
- [ ] How much graph viz / streamed trace to show → **rec: render the graph once + one trace mapped to L08 shape**.
- [ ] Persistence / checkpointing → **rec: out of scope; forward-pointer to L14/L15**.
- [ ] L07 Demo-4 overlap → **rec: deliver the framework rebuild in full; L07 was the teaser**.

---

## 🔵 Forward-coordination (resolve when later roadmaps are written)

- [ ] L09→L11 harness reuse — **largely settled** by `common/evals.py`; needs a confirming line.
- [ ] L09 pre-linking L10 in the mini cut → **rec: parenthetical mention only**.
- [ ] L11→L12 boundary — frame ReAct in L12 as a *pattern over* L11 primitives, not a re-intro.

---

## ⚪ Classroom infra (separate track — `docs/classroom-llm-management.md`, not curriculum)

- [ ] Verify current **OpenRouter BYOK surcharge %**.
- [ ] **Cohort size + per-student budget** → drives soft (Workspaces) vs. hard (proxy) caps.
- [ ] **Key provisioning/rotation owner** — manual Console vs. Admin API automation.
- [ ] **Anthropic-only vs. multi-provider** in practice (if Anthropic-only, OpenRouter's edge doesn't apply).

---

## Not-yet-written roadmap artifacts (stage 1 remaining)

- [ ] `demos_or_activities.md` for **L08**, **L09**, **L11** (objectives done; demos not started).
- [ ] Stage 2 (`generate-materials-from-roadmap`) for L08/L09/L11 — also authors the `common/`
      reference modules per the decided schemas.
