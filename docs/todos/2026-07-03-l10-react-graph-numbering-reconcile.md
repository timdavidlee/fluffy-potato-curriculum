# TODO — reconcile L10 ReAct-graph rewrite with the L14→L11 renumbering (after merge)

**Date:** 2026-07-03
**Branch:** `feat/l10-react-cyclic-graph` (worktree off `main`, base `d16d15c`)
**Blocked on:** the `l14-to-l11-create-agent` branch landing (it moves shallow agents/`create_agent` from L14 → L11, pushing tracing L11 → L12, eval L12 → L13).

## Context

L10 was rewritten from "Hand-rolled agent loop" → **"Cyclic graphs: the ReAct agent loop"** — students build the ReAct agent as a real LangGraph `StateGraph` (agent node → conditional `route` → `ToolNode` → back-edge), instead of a plain-Python `while` loop. Plus two optional stretch extensions (a `respond` node; an `interrupt`/`human_approval` preview of L17).

This branch was cut **off `main`** (user chose "worktree off current main, reconcile later"), so it does **not** contain the `l14-to-l11-create-agent` renumbering. To keep the lesson forward-consistent, the **L10 roadmap prose was already remapped** to the post-restructure numbering:

- shallow agents / `create_agent`: L14 → **L11**
- tracing / "what an agent generates": L11 → **L12**
- eval: L12 → **L13**
- (L17 interrupt/HITL and L18 deep agents unchanged)

Files remapped: `docs/origin/lesson_roadmaps/L10/objectives.md`, `docs/origin/lesson_roadmaps/L10/demos_or_activities.md`. Verified zero `L14` refs remain there.

## The interim inconsistency to fix after merge

The **shared design tables on this branch are still OLD-numbered** (deliberately not touched, to avoid duplicating/conflicting with the restructure branch):

- `docs/origin/CURRICULUM_PRD.md` — master + mini lesson tables still list `L11 = What an agent generates`, `L14 = Shallow agents`; the "orchestration before tools" narrative note I edited still contains an `L14` mention. Only the **L10 row** was retitled to "Cyclic graphs: the ReAct agent loop".
- `src/fluffy_potato_curriculum/lessons/tracks.toml` — `[titles]` still old-numbered except the retitled `L10`.
- `src/fluffy_potato_curriculum/lessons/SYLLABUS.md` — table still old-numbered except the retitled `L10` row.

So right now the L10 **prose** points at new numbering while these **tables** show old numbering. This resolves at merge with `l14-to-l11-create-agent`.

## Checklist (do after `l14-to-l11-create-agent` is merged into `main`)

- [ ] Merge/rebase this branch onto the post-restructure `main`.
- [ ] Resolve conflicts in `CURRICULUM_PRD.md` (the restructure renumbers the tables; keep the L10 row's new "Cyclic graphs: the ReAct agent loop" title + the ReAct-graph subgoals from this branch).
- [ ] Confirm `tracks.toml` `[titles]` and `SYLLABUS.md` show `L10 = "Cyclic graphs: the ReAct agent loop"` alongside the restructure's `L11 = Shallow agents`, `L12 = What an agent generates`, `L13 = Evaluation`.
- [ ] Re-fix the PRD "orchestration before tools" narrative note: its stale `L14` (shallow agents) → `L11`, and drop the now-resolved `<need input>` about hand-rolling L10 (already partly done on this branch).
- [ ] Re-run the verification sweep: `grep -rn "L14" docs/origin/lesson_roadmaps/L10/` should stay empty; spot-check that L10 prose ↔ the renumbered tables agree.
- [ ] Sanity-check the neighbor hand-off: L10 (build the graph by hand) → L11 (shallow agents reveals `create_agent` as "that graph, packaged") → L12 (trace it). The `l14-to-l11` branch already edited the *old* L10 roadmap toward this; make sure our StateGraph rewrite supersedes it cleanly (ours should win — it's the newer direction).

## Also pending on this branch (separate from renumbering)

- [ ] **Stage 2 not started** — L10 student materials (intro, 2 lectures, 2 lab pairs, PROCTOR_NOTES) still need regenerating from the new roadmap via `generate-materials-from-roadmap`. The current notebooks are the old hand-rolled-loop versions.
- [ ] **L12 (tracing) seam** — L12's materials still import `common/agent_loop.py` (the plain-Python loop) and its prose references "the loop from L10". After L10 becomes a graph, decide whether L12 re-points to instrumenting the L10 *graph* or keeps the plain-loop reference. Light-touch prose fix vs. deeper rework — flagged, not yet done.
