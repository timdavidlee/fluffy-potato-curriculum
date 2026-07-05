# Handoff: re-review & revoice all lesson materials to the student-POV registers

**Status: DONE**
**Date:** 2026-07-04
**Branch:** direct commits/merges on local `main`, pushed to `origin/main`. Landed: `06a920e` L10,
`8d5dc0b` L03, `dc60c90` L04, `d088b4c` L05, `bbcd198` L02, `c402559` L01, `7a7c2fd` L08, `efdff16`
L07, `9d796ad` L06, `c53cdaa` L13, `12e0af3` L11, `c31392a` L09, `e39272a` L12, `3465a38` L22,
`e0ce885` L23. K01–K06 were spot-checked and found already clean — no commit needed. The two
"Also open" skill edits (`generate-materials-from-roadmap/SKILL.md`, `review-lesson/SKILL.md`) and
a deck-build spot-check on `L10/L1002_lecture.md` (29 slides — 5 sections + 23 content, matching
the outline exactly) round this out. The `student-pov-lectures` worktree/branch this doc originally
pointed at no longer exists — the work landed straight on `main` instead; treat that branch
reference as stale.

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
- ✅ **L10 — fully done** (`06a920e`, on top of the earlier partial pilot). All 3 lectures, the intro,
  and both lab pairs are Coach/Punchy. This is the reference example — `L10/L1002_lecture.md`
  (Coach) and `L10/L1004_lab_empty.ipynb` (Punchy) are the concrete models to copy.
- ✅ **L02 — fully done** (`bbcd198`), including the proper Coach re-pass on `L0202_lecture.md` that
  the earlier light touch-up needed.
- ✅ **L03 — fully done** (`8d5dc0b`). Mostly already clean; only 2 small presenter-tell fixes needed.
- ✅ **L04 — fully done** (`dc60c90`). Flags a pre-existing gap worth a follow-up: `L0402_lecture.md`
  has **no `[↑ Back to top]` anchors at all** (unlike the L10 model) — a structural gap, not a voice
  issue, left alone since this effort is voice-only.
- ✅ **L05 — fully done** (`d088b4c`). Lab pair (`L0504`) was already clean Punchy, untouched.

These 5 lessons were done by concurrent Sonnet subagents sharing one working tree (no worktree
isolation) — it mostly worked but caused a couple of near-miss races (agents transiently reverting
each other's in-progress edits before recognizing the pattern and re-verifying). No data was lost,
but the next batch switched to per-agent git worktree isolation to remove the race outright (see
below).

- ✅ **L01 — fully done** (`c402559`). Notebook-heavy as flagged; found and fixed several "teacher
  demo N" tells across `L0103`/`L0104`/`L0106`/`L0107`/`L0109`/`L0110`. All 3 lab pairs were already
  clean Punchy, untouched.
- ✅ **L08 — fully done** (`7a7c2fd`, merge commit). Light touch-up pass — material was already close
  to Coach/Punchy. All 4 lab pairs were already clean, untouched.
- ✅ **L07 — fully done** (`efdff16`, merge commit). Light touch-up pass; only `L0705_lab_solutions`
  needed a one-word fix, the other 2 lab pairs were already clean.
- ✅ **L06 — fully done** (`9d796ad`, merge commit). One lab pair (`L0608`) was already clean and
  left untouched; caught and fixed an inconsistency where 3 of 4 lecture notebooks still had
  "Teacher demo — Demo N" headers after a first pass, plus a stray HTML-escaped anchor tag
  introduced then self-corrected mid-task.

L01/L06/L07/L08 ran as a second batch with **per-agent worktree isolation** (`isolation: "worktree"`
on the Agent tool) — each agent worked in its own git worktree/branch and committed there, then the
orchestrating session merged each branch back into local `main` one at a time (fast-forward when
possible, otherwise a merge commit with an explicit Conventional-Commit `-m` message, since the
default auto-generated merge message fails the repo's `cz check` commit-msg hook). This fully
eliminated the shared-working-tree races from the first batch.

- ✅ **L13 — fully done** (`c53cdaa`). Was already largely in-register; only one presenter tell
  ("name them now") fixed in `L1307_lecture.md`.
- ✅ **L11 — fully done** (`12e0af3`, merge commit). Two small tells fixed (`L1102`, `L1103`); the
  intro, `L1105`, and the lab pair were already clean.
- ✅ **L09 — fully done** (`c31392a`, merge commit). Several "teacher demo N" / "teacher-narration"
  tells fixed across `L0902`/`L0903`/`L0905`/`L0906`; both lab pairs already clean.
- ✅ **L12 — fully done** (`e39272a`, merge commit). The tracing (Langfuse) lesson; already largely
  clean — a handful of third-person "student(s)" tells fixed in `L1201`/`L1204`/`L1206`. Both lab
  pairs already clean.

L09/L11/L12/L13 ran as a third batch, also with per-agent worktree isolation.

- ✅ **L22 — fully done** (`3465a38`, merge commit). Mostly already clean; 3 small tells fixed
  (`L2202`, `L2203`, `L2205`). Both lab pairs already clean.
- ✅ **L23 — fully done** (`e0ce885`, merge commit). Almost entirely already clean — only one
  "Teacher demo notebook" tell fixed in `L2304_lecture.ipynb`. Everything else, including both lab
  pairs, was already clean.
- ✅ **K01–K06 — spot-checked, no changes needed.** All 6 `_guide.md` files and the 2 demo notebooks
  (`K03`/`K05`) were already in clean Runbook/second-person voice. No commit made (nothing to
  change).

L22/L23/K01-K06 ran as a fourth and final batch, also with per-agent worktree isolation. This
completes every lesson row in the §4 checklist table.

## 4. What REMAINS (the checklist)

Per-lesson counts of student-facing artifacts to revoice. **Lectures + intros → Coach; labs →
Punchy** (each lab = an `_empty` **and** a `_solutions`, revoiced identically). `PROCTOR_NOTES.md`
is **teacher-facing and OUT OF SCOPE** — leave it in presenter voice.

| Lesson | Lectures (Coach) | Intro (Coach) | Lab pairs (Punchy, ×2 files) | Notes |
| --- | --- | --- | --- | --- |
| L01 | ✅ done (`c402559`) | ✅ | ✅ | notebook-heavy; several "teacher demo N" tells fixed |
| L02 | ✅ done (`bbcd198`) | ✅ | ✅ | |
| L03 | ✅ done (`8d5dc0b`) | ✅ | ✅ | |
| L04 | ✅ done (`dc60c90`) | ✅ | ✅ | missing `[↑ Back to top]` anchors in `L0402` — pre-existing, not fixed here |
| L05 | ✅ done (`d088b4c`) | ✅ | ✅ | |
| L06 | ✅ done (`9d796ad`) | ✅ | ✅ | one lab pair (`L0608`) already clean, untouched |
| L07 | ✅ done (`efdff16`) | ✅ | ✅ | light touch-up, mostly already clean |
| L08 | ✅ done (`7a7c2fd`) | ✅ | ✅ | light touch-up, mostly already clean |
| L09 | ✅ done (`c31392a`) | ✅ | ✅ | several "teacher demo N" tells fixed |
| L10 | ✅ done (`06a920e`) | ✅ | ✅ | reference example other lessons copy |
| L11 | ✅ done (`12e0af3`) | ✅ | ✅ | light touch-up, mostly already clean |
| L12 | ✅ done (`e39272a`) | ✅ | ✅ | tracing (Langfuse) lesson; light touch-up, mostly already clean |
| L13 | ✅ done (`c53cdaa`) | ✅ | ✅ | light touch-up, mostly already clean |
| L22 | ✅ done (`3465a38`) | ✅ | ✅ | light touch-up, mostly already clean |
| L23 | ✅ done (`e0ce885`) | ✅ | ✅ | almost entirely already clean, one tell fixed |
| K01–K06 | ✅ spot-checked | ✅ | n/a | all 6 guides + 2 demo notebooks already clean, no commit needed |

**Remaining totals:** none — every lesson row above is done. What's left is the "Also open" section
below (skill wiring) and a deck-build spot-check, not more lesson content.

L10/L1002_lecture.md (Coach) and L10/L1004_lab_empty.ipynb (Punchy) remain the concrete reference
models, for anyone auditing the finished work or authoring new lessons going forward.

### Also open (make the convention self-enforcing) — ✅ done

- ✅ **`generate-materials-from-roadmap/SKILL.md`** — now points at `CURRICULUM_PRD.md`'s
  `### Voice & point of view` in its "Read first" list and requires the assigned register
  (Coach/Punchy) from the first draft in its "Author each artifact" step.
- ✅ **`review-lesson/SKILL.md`** — added lens 6, "Voice / point of view," checking student POV,
  correct register, and no presenter meta-instructions; renumbered the neighbor-hand-off and
  code/reproducibility lenses to 7/8.

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

## 9. Definition of done — ✅ met

Every file in the §4 table revoiced to its register (✅), the two skills wired (✅ §4 "Also open"),
the full gate green (✅, re-run after every merge across all four batches), one deck spot-checked
(✅ `L10/L1002_lecture.md` → 29 slides, 5 sections + 23 content, matching the outline exactly), and
this handoff marked **Status: DONE** (✅, see top).
