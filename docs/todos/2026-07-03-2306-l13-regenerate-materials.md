# TODO — Regenerate L13 materials (Langfuse-forward)

The L13 roadmap is already re-spined to a Langfuse-forward hybrid and merged
([PR #52](https://github.com/timdavidlee/fluffy-potato-curriculum/pull/52)). This TODO tracks
**stage-2**: regenerating the student-facing materials so they match the new roadmap. The current
`src/fluffy_potato_curriculum/lessons/L13/` files still teach the old hand-rolled `evaluate()`
harness and contradict the roadmap.

## The regeneration

- [ ] Run `generate-materials-from-roadmap` for L13 from
      `docs/origin/lesson_roadmaps/L13/{objectives,demos_or_activities}.md`.
- [ ] Regenerated artifacts (10 files):
  - [ ] `L1301_intro.md`
  - [ ] `L1302_lecture.ipynb` — concept in ~15 lines → upload a Langfuse **Dataset** (Demo 1)
  - [ ] `L1303_lab_empty.ipynb` / `L1303_lab_solutions.ipynb`
  - [ ] `L1304_lecture.ipynb` — two experiments (Sonnet/Haiku) compared in the Langfuse UI (Demo 3)
  - [ ] `L1305_lab_empty.ipynb` / `L1305_lab_solutions.ipynb`
  - [ ] `L1306_lecture.ipynb` — cost off the trace + managed LLM-as-judge (Demo 4)
  - [ ] `L1307_lecture.md` — carry-forward bridge (same Langfuse dataset → L11)
  - [ ] `PROCTOR_NOTES.md` — note Langfuse is a hard pre-flight dependency

## Blocked-on: resolve these `<need input>` first (else regen guesses)

- [ ] Langfuse config surface in `common/config.py` (host + public/secret key env vars) and the
      `require_langfuse()`-style guard notebooks call at top. **Decided:** notebooks require a live
      Langfuse (no offline fallback), so restart-run-all depends on the cohort instance.
- [ ] Final eval-case list + `reference_outputs` → Langfuse `expected_output` mapping (6–8 cases rec.).
- [ ] Two-or-three saved L12 failure runs Demo 2 converts to dataset items (one runaway/`max_steps`,
      one flaky_fetch tool-error rec.).
- [ ] Sample count K for the toy set (3–5 rec.).
- [ ] The deliberately-flaky case for Demo 3 (must flake reliably on Sonnet on a dry-run).
- [ ] The one quality the Demo 4 managed LLM-as-judge scores + evaluator config
      ("gave up gracefully" rec.).
- [ ] Experiments launched purely via Langfuse SDK (`langfuse>=4.7.1`, already a dep) vs. partly clicked in UI.

## Depends-on / must land alongside

- [ ] **`common/evals.py`** must gain the Langfuse bridge (upload `list[EvalCase]` as a Dataset;
      emit `EvalResult` as a Langfuse score) *before* the notebooks import it. Keep the
      `EvalCase` / `Scorer` / `EvalResult` types (L11 imports them).

## Verify / gate

- [ ] `uv run ruff format && uv run ruff check && uv run pyright && uv run pytest`.
- [ ] Restart-run-all each regenerated notebook with the shared Langfuse instance **reachable**
      (or live cells gated behind `require_langfuse()` and left un-run).
- [ ] Clear outputs of `_empty` student notebooks before committing (see `.claude/rules/notebooks.md`).

## Notes

- Do this on a branch/worktree, not `main`.
- Cross-ref reconciliation (PRD L13 row, L11/L25 pointers, memory files) is related but tracked
  separately — not part of this regeneration TODO.
