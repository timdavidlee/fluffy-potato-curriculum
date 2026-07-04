# TODO — Finish L13 Langfuse-forward regeneration (remaining 7 files)

Continuation of [2026-07-03-2306-l13-regenerate-materials.md](2026-07-03-2306-l13-regenerate-materials.md).
Work happens on branch/worktree `l13-regenerate-materials` (based on `main` @ `462dbea`, which
already carries the `require_langfuse()` + `common/evals.py` Langfuse bridge + tests — do **not**
reimplement those).

## Context (what's already true)

- **Prereqs are done and on `main`:** `require_langfuse() -> (host, public_key, secret_key)` in
  `common/config.py`; the bridge in `common/evals.py` — `upload_dataset(client, cases, *, name,
  description=None)`, `emit_score(client, result, *, trace_id)`, and the `LangfuseClient` Protocol.
  There is **no `run_experiment` wrapper** — an "experiment" = run the agent over each dataset item
  (optionally K times), push each scorer's `EvalResult` via `emit_score`, and read pass rates / the
  run comparison in the Langfuse UI.
- **The current L13 notebooks are already on the correct LangChain API** (`agent_loop.run(model,
  tools, user_msg, max_steps=8) -> RunResult`, `FakeModel` scripted with `text_reply`/`tool_reply`/
  `tool_call`, tools from `common/tools.py`, eval types from `common/evals.py`). They just **lack the
  Langfuse layer**. So this is **surgical augmentation, not a rewrite**: add the dataset/experiment/
  score/judge beats, reframe some prose, keep the working hand-rolled concept beats.
- **Batch 1 landed (DONE, verified):** `L1301_intro.md` (Langfuse-forward reframe), `L1302_lecture.ipynb`
  (added §4 "Now go tooled: a Langfuse Dataset"), `L1303_lab_empty/solutions.ipynb` (added Problem 5 —
  upload your eval set to Langfuse). Full suite green (276 passed), TOC-anchor guard passes.

## The gating pattern to reuse in every notebook (decided)

Mirror L11/L12's soft-gate so a keyless restart-run-all still passes:

```python
from fluffy_potato_curriculum.common.config import langfuse_configured, require_langfuse
# concept beats run OFFLINE on FakeModel and keep outputs.
# tooled cells:
if langfuse_configured():
    from langfuse import Langfuse
    host, public_key, secret_key = require_langfuse()
    client = Langfuse(host=host, public_key=public_key, secret_key=secret_key)
    ...  # upload_dataset / run agent per item / emit_score / client.flush()
    print(...)
else:
    print("Langfuse not configured — skipping ...")   # left un-run in class terms
```

- Concept cells: offline, deterministic, outputs retained in lectures/`_solutions`.
- Tooled cells: soft-skip when unset. Live model side also gated on `bool(get_settings().anthropic_api_key)`.
- Shared dataset name used across the lesson: **`l13-agent-evals`** (labs use `l13-lab-my-evals`).
- Shared fixtures already defined in L1302/L1303 (reuse verbatim): chaining task → `lookup(Tokyo)` +
  `lookup(Paris)` + `calculator(37000000+11000000)` = **48000000**, trajectory `["lookup","lookup",
  "calculator"]`; `flaky_fetch("https://ok")` → "the answer is 42"; runaway = repeated
  `lookup("Atlantis")` → `max_steps`; graceful give-up = `flaky_fetch("https://crash")`.

## Remaining files

- [ ] **`L1304_lecture.ipynb`** — *Non-determinism → pass rate, and a model A/B (Demo 3).* Keep the
      offline `evaluate(..., samples=K)` single→rate concept beats. **Add:** reframe the A/B as **two
      Langfuse Experiments over the same dataset** (Sonnet 4.6 vs Haiku 4.5) — a tooled cell that, per
      dataset item, runs the loop K times against each live model and calls `emit_score` for each
      scorer's `EvalResult`; then read the **run-comparison view** in Langfuse. Also frame the
      before/after prompt-edit run as the **regression** view. K = **3–5** (decided). Live models gated
      on the anthropic key; Langfuse gated on `langfuse_configured()`. Update TOC/anchors/takeaways +
      "next" pointer.
- [ ] **`L1305_lab_empty.ipynb` / `L1305_lab_solutions.ipynb`** — *Pass rates & regressions lab.* Keep
      the offline pass-rate/`compare()` problems. **Add a Problem** that pushes scores to Langfuse via
      `emit_score` (or reruns the `l13-agent-evals` dataset as an experiment) and reads the pass rate
      in the UI. TODO stub in `_empty`, answer in `_solutions`. Keep **identical cell count/ordering**;
      clear `_empty` outputs. Update TOC (renumber Self-check), objectives, header note.
- [ ] **`L1306_lecture.ipynb`** — *Eval cost + scorer spectrum → managed LLM-as-judge (Demo 4).* Keep
      the offline cost-formula + spectrum beats. **Add:** (a) read **real per-call token `usage` off a
      Langfuse experiment trace** and cross-check `cost ≈ cases × samples × avg model-calls/run ×
      per-call cost`; (b) turn on **Langfuse's managed LLM-as-judge** on **one** fuzzy quality — the
      `flaky_fetch` "**gave up gracefully**" answer (decided) — flagged clearly as "L25 adds rubrics +
      bias checks"; (c) place human review at the expensive end. Tooled/live cells gated. Update
      TOC/anchors/takeaways.
- [ ] **`L1307_lecture.md`** — *Carry the dataset forward (Objective 5 bridge).* Short slide-outline
      closer: **same Langfuse `l13-agent-evals` dataset** runs as an experiment against the LangGraph
      agent in **L11** (and L04's deterministic flow is trivially evaluable); signpost **L25** as where
      the rigor scales. Reframe any hand-rolled-`evaluate()` language to the Langfuse dataset/experiment
      framing. Keep the three-heading-level slide format + metadata block.
- [ ] **`PROCTOR_NOTES.md`** — Add the **Langfuse hard-dependency pre-flight** (dry-run connection +
      dataset upload + an experiment + the managed evaluator before class; keys via `common/config.py`).
      Add a section for **`L1303_lab problem 5`** and any new L1305 problem. Ensure one section per
      problem across all L13 labs.

## Verify / gate (per file + at the end)

- [ ] Each lecture / `_solutions` notebook: restart-run-all **offline** (no keys here) completes — the
      tooled cells take the soft-skip branch. `_empty` runs up to its first TODO.
- [ ] `_empty` ↔ `_solutions` identical cell count + ordering; `_empty` outputs cleared
      (`uv run jupyter nbconvert --clear-output --inplace <_empty>`).
- [ ] Every notebook keeps a `#top` anchor, a TOC cell in sync with headings, hierarchical numbered
      headings (≤3 levels), and `[↑ Back to top]` at each top-level section end.
- [ ] `uv run ruff format && uv run ruff check && uv run pyright && uv run pytest` (the TOC-anchor guard
      `tests/lessons/test_toc_anchors.py` must stay green — new TOC entries must resolve).

## Out of scope (tracked elsewhere)

- Cross-ref reconciliation (PRD L13 row, L11/L25 pointers, memory files) — per the parent TODO.
- `run_experiment`-based runner wrapper in `common/evals.py` — the current bridge (`upload_dataset` +
  `emit_score`) is sufficient; only add one if a later lesson needs it.
