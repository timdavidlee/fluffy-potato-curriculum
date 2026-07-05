# Handoff: re-review & revoice all lesson materials to the student-POV registers

**Status: IN PROGRESS** (pilot + conventions landed; the bulk revoicing remains)
**Date:** 2026-07-04
**Branch / worktree:** `student-pov-lectures` at `.claude/worktrees/student-pov-lectures` (not yet
PR'd). All work below lives on this branch; diff against `main` to see everything done so far.

---

## 1. Goal

Rewrite every **student-facing** lesson artifact so its point of view is the **student** (second
person, "you"), in a register chosen per material type:

- **Lectures → Coach** — warm, mentor tone, medium length; thorough but sounds like a person guiding you.
- **Labs → Punchy** — terse, energetic, high-signal task prompts with momentum.
- **Prework `K` guides → Runbook** — procedural "do this → here's why" (mostly already in this voice).

The problem being fixed: the generated materials are littered with **presenter/author
meta-instructions** — "Teach *what the invariant is*," "name them now," "Defend the choice
against…," "(do not teach here)," reference-header notes that talk *about* students in the third
person ("so a student who missed the verbal delivery…"), and notebook headers like "teacher demo 1
of the chain." These read as an instructor's script, not material addressed to the learner.

## 2. The decision (already codified — read these first)

The conventions are authoritative and live in `docs/origin/` (all on this branch):

- **[CURRICULUM_PRD.md](../origin/CURRICULUM_PRD.md) `## Target audience` → `### Voice & point of
  view`** — the course-wide rule: student POV, the register-per-material-type table, "register
  controls *how it reads*, not *how much it teaches*," and "keep table-related text as concise as
  possible in both lectures and labs."
- **[LECTURES.md](../origin/LECTURES.md) `## Voice`** — the Coach register + a ✗/✓ before/after
  table + what scaffolding to preserve.
- **[LAB_DESIGN.md](../origin/LAB_DESIGN.md) `## Voice`** — the Punchy register + a ✗/✓ table + the
  `_empty`/`_solutions` lockstep rule.

Both format guides were previously `<!-- llm-status: draft -->`; that marker was removed as part of
this work so they can be cited as authority.

## 3. What is DONE

- ✅ Conventions codified (PRD + both format guides, §2 above).
- ✅ **L10 pilot, partial** — the reference example the guides point to:
  - `L10/L1002_lecture.md` → **Coach** (full rewrite; the heaviest teacher-voice file — good model
    for what "remove the meta-instructions" looks like).
  - `L10/L1004_lab_empty.ipynb` → **Punchy** (markdown cells only; code + `# TODO`s untouched).
- ⚠️ **L02 early pilot (needs a re-pass)** — `L02/L0202_lecture.md` got a *light* student-POV touch-up
  **before** the Coach register was chosen. It is student-addressed but not fully Coach. Treat it as
  **not done**: give it a proper Coach pass like L1002.

## 4. What REMAINS (the checklist)

Per-lesson counts of student-facing artifacts to revoice. **Lectures + intros → Coach; labs →
Punchy** (each lab = an `_empty` **and** a `_solutions`, revoiced identically). `PROCTOR_NOTES.md`
is **teacher-facing and OUT OF SCOPE** — leave it in presenter voice.

| Lesson | Lectures (Coach) | Intro (Coach) | Lab pairs (Punchy, ×2 files) | Notes |
| --- | --- | --- | --- | --- |
| L01 | 7 | 1 | 3 | notebook-heavy; check "teacher demo N" headers |
| L02 | 5 | 1 | 4 | L0202 needs a Coach re-pass (see §3) |
| L03 | 2 | 1 | 1 | |
| L04 | 2 | 1 | 1 | |
| L05 | 3 | 1 | 1 | |
| L06 | 5 | 1 | 4 | |
| L07 | 5 | 1 | 3 | |
| L08 | 6 | 1 | 4 | |
| L09 | 4 | 1 | 2 | |
| L10 | 3 (1 done) | 1 | 2 (½ done) | **finish first** as the worked example |
| L11 | 3 | 1 | 1 | |
| L12 | 3 | 1 | 2 | |
| L13 | 4 | 1 | 2 | |
| L22 | 3 | 1 | 2 | |
| L23 | 3 | 1 | 2 | |
| K01–K06 | — | — | — | 6 `_guide.md`; verify Runbook + student POV (light touch, low priority) |

**Totals:** 58 lecture files, 15 intros, 34 lab pairs (68 notebooks), 6 K-guides. `.md` lectures are
straight `Edit`s; `.ipynb` lectures/labs need `NotebookEdit` on **markdown cells only**.

**Finish L10 first** (it's the reference the guides cite): `L1001_intro.md` (Coach),
`L1003_lecture.ipynb` + `L1006_lecture.ipynb` (Coach), `L1004_lab_solutions.ipynb` (Punchy — mirror
the already-done `_empty`), `L1005_lab_empty.ipynb` + `L1005_lab_solutions.ipynb` (Punchy).

### Also open (make the convention self-enforcing)

- **`generate-materials-from-roadmap/SKILL.md`** — add an explicit "apply the register assigned in
  CURRICULUM_PRD.md `### Voice & point of view`" line so **new** lessons are authored in-voice, not
  just existing ones revoiced.
- **`review-lesson/SKILL.md`** — add a voice check to its audit (student POV? correct register? no
  presenter meta? tables terse?).

## 5. The transformation, precisely

**Both registers, always:**
- Second person, addressed to the student. No third-person "the student" / "students should…".
- Remove presenter/author meta-instructions entirely (the ✗ column in each format guide's `## Voice`
  table is the canonical list of tells).
- Rewrite reference-header blockquotes and notebook headers to speak to the reader ("This page is
  your written reference… if you missed the live session you can rebuild it," not "so a student who
  missed the verbal delivery can…"; "the first demo in the chain," not "teacher demo 1 of the chain").
- Keep **table-related text terse**: `table:` lead-ins and cells are fragments, not sentences.

**Preserve (do NOT touch) — this is where revoicing breaks things:**
- Lecture `.md`: the `## section` / `### slide` headings, the `text:` / `diagram:` / `table:`
  directives (the deck-builder consumes them), YAML metadata, ASCII diagrams, tables, code fences,
  cross-reference links, and `[↑ Back to top]` anchors.
- Notebooks: **all code cells and `# TODO` markers**, and the markdown **headings** — headings feed
  the `## Contents` TOC anchors, so changing heading text breaks the in-notebook links. Revoice the
  prose under a heading, not the heading itself.
- Labs: `_empty` and `_solutions` must stay prose-identical (LAB_DESIGN rule). Revoice both in the
  same pass.

**Concrete models to copy:** `git diff main -- L10/L1002_lecture.md` (Coach) and the L1004 lab cells
(Punchy) show exactly the intended before→after. The ✗/✓ tables in LECTURES.md / LAB_DESIGN.md are
the quick reference.

## 6. Suggested per-lesson workflow

1. Read the lesson's roadmap (`docs/origin/lesson_roadmaps/L<NN>/`) only if you need context; you're
   changing **voice, not content**.
2. `.md` lectures: `Edit` the prose bullets/blockquotes; leave every directive/heading/table alone.
3. `.ipynb` lectures/labs: `Read` the notebook (for cell IDs), then `NotebookEdit` the prose markdown
   cells. Skip `## Contents`, back-to-top cells, and all code cells.
4. Labs: revoice `_empty`, then apply the identical prose to `_solutions`.
5. Verify (next section), then move on. Consider committing per-lesson so the diff stays reviewable.

## 7. Verification

- **Structure intact (lecture .md):** section/slide counts and directive counts unchanged, e.g.
  `grep -c '^### slide' <file>` and `grep -cE '^- (text|table|diagram):' <file>` before vs after.
- **Notebook still valid + TOC intact:** load JSON, confirm the `## ` headings still match the
  `## Contents` links (heading text unchanged). Code cells / `# TODO`s byte-identical.
- **Labs:** `_empty` and `_solutions` markdown-prose cells match; `_solutions` still runs top-to-bottom.
- **Restart-and-run-all** any notebook whose *code* you touched (you shouldn't have — prose only —
  but confirm). Re-clear `_empty` outputs if needed
  (`uv run jupyter nbconvert --clear-output --inplace <_empty>`).
- **Full gate** before committing (from CLAUDE.md):
  `uv run ruff format && uv run ruff check && uv run pyright && uv run pytest`. (Prose-only changes
  won't move these, but run them.)
- **Deck build** still works for a revoiced `.md` lecture (the `build-lecture-deck` skill) — the
  directives were preserved, so it should; spot-check one.

## 8. Gotchas / decisions already made

- **PROCTOR_NOTES.md is teacher-facing** — intentionally *not* revoiced. Same for anything under
  `docs/`.
- **Intros (`_intro.md`) are lightweight lectures** → Coach.
- **K-guides already read as Runbooks** — likely just need a student-POV spot-check, not a rewrite.
- **Register ≠ depth.** Do not shorten a lecture's *content* to sound "Coach"; keep it thorough and
  change the tone. Do not drop a lab's *steps* to sound "Punchy"; trim words only.
- The two format guides were **un-drafted** in this effort. If anyone objects to treating the rest of
  those docs as authoritative, that's the one reversible decision to revisit.

## 9. Definition of done

Every file in the §4 table revoiced to its register, the two skills wired (§4 "Also open"), the full
gate green, one deck spot-checked, and this handoff marked **Status: DONE** (or deleted).
