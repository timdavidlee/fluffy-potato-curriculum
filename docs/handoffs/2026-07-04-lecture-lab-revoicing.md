# Handoff: re-review & revoice all lesson materials to the student-POV registers

**Status: IN PROGRESS** (conventions, L10 reference, and 8 of 15 lessons landed; L06 in flight, the
rest of the checklist remains)
**Date:** 2026-07-04
**Branch:** direct commits/merges on local `main`, not yet pushed to `origin/main`. Landed so far:
`06a920e` L10, `8d5dc0b` L03, `dc60c90` L04, `d088b4c` L05, `bbcd198` L02 (pushed to origin at
`763e558`), then `c402559` L01, `7a7c2fd` L08, `efdff16` L07 (local only, not yet pushed). The
`student-pov-lectures` worktree/branch this doc originally pointed at no longer exists — the work
landed straight on `main` instead; treat that branch reference as stale.

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

L01/L06/L07/L08 ran as a second batch with **per-agent worktree isolation** (`isolation: "worktree"`
on the Agent tool) — each agent worked in its own git worktree/branch and committed there, then the
orchestrating session merged each branch back into local `main` one at a time (fast-forward when
possible, otherwise a merge commit with an explicit Conventional-Commit `-m` message, since the
default auto-generated merge message fails the repo's `cz check` commit-msg hook). This fully
eliminated the shared-working-tree races from the first batch.

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
| L06 | 🔄 in progress | 🔄 | 🔄 | third agent of the worktree-isolated batch, not yet landed |
| L07 | ✅ done (`efdff16`) | ✅ | ✅ | light touch-up, mostly already clean |
| L08 | ✅ done (`7a7c2fd`) | ✅ | ✅ | light touch-up, mostly already clean |
| L09 | 4 | 1 | 2 | |
| L10 | ✅ done (`06a920e`) | ✅ | ✅ | reference example other lessons copy |
| L11 | 3 | 1 | 1 | |
| L12 | 3 | 1 | 2 | |
| L13 | 4 | 1 | 2 | |
| L22 | 3 | 1 | 2 | |
| L23 | 3 | 1 | 2 | |
| K01–K06 | — | — | — | 6 `_guide.md`; verify Runbook + student POV (light touch, low priority) |

**Remaining totals:** L06 (in flight), L09, L11–L13, L22, L23 — 22 lecture files, 6 intros, 12 lab
pairs (24 notebooks) — plus the 6 K-guides. `.md` lectures are straight `Edit`s; `.ipynb`
lectures/labs need `NotebookEdit` on **markdown cells only**.

L10/L02/L03/L04/L05 are done — use `L10/L1002_lecture.md` (Coach) and `L10/L1004_lab_empty.ipynb`
(Punchy) as the concrete models for the rest.

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
