---
name: review-lesson
description: Review a single L<NN> lesson end-to-end for pedagogical soundness, roadmap-vs-materials consistency, format-guide compliance, and clean neighbor hand-offs. Reads the lesson's roadmap docs, student materials, and the relevant specs from known locations (no searching), then reports ranked findings. Read-only — it diagnoses and recommends; it does not edit lesson files. Use when the user asks to review, critique, audit, or sanity-check a lesson.
---

# Review a single lesson

Assess one curriculum lesson (`L<NN>`) as a whole and report what's wrong or weak, ranked by
impact. This skill is **read-only**: it produces a findings report, it does not modify lesson
files. Fixing is a follow-up the user drives (often via `author-lesson-roadmap` for roadmap
issues or `generate-materials-from-roadmap` for material issues).

This is the quality-gate counterpart to the two authoring skills:

- `author-lesson-roadmap` (stage 1) writes the roadmap docs.
- `generate-materials-from-roadmap` (stage 2) writes the student materials.
- **`review-lesson` (this skill)** reads both and tells you where they've drifted, where the
  narrative breaks, and where a format or neighbor convention is violated.

## Inputs

- `lesson` — the `L<NN>` identifier (e.g. `L01`). Must correspond to a row in
  `docs/origin/CURRICULUM_PRD.md`'s "Lesson plan" table.
- `focus` *(optional)* — narrow the review to one lens, e.g. `narrative` (flow/backdrop gaps),
  `consistency` (roadmap vs. materials), `format` (spec compliance), `neighbors` (overlap /
  hand-off). Default: review all lenses.

If `lesson` is missing, ask before doing anything else.

## File map — read these, in this order (no searching needed)

All paths are repo-relative. `<NN>` is the zero-padded lesson number; `LL` is the same number
used as the filename prefix (so `L01` → files `L01<NN>_...`).

**1. Course context + specs (the rubric):**

- `docs/origin/CURRICULUM_PRD.md` — course intent, target audience, "Lecture Materials"
  depth-bias, and the lesson-plan row for `L<NN>` (title + subgoals). This row is the contract
  the lesson must satisfy.
- `docs/origin/CLAUDE.md` — roadmap folder conventions and the one-line spec for each roadmap
  artifact.
- `docs/origin/LECTURES.md` — lecture + intro format spec (metadata, slide-outline vs. notebook,
  heading/TOC rules).
- `docs/origin/LAB_DESIGN.md` — lab format spec (`_empty`/`_solutions` parity, problem structure,
  proctor notes).
- `.claude/rules/notebooks.md`, `.claude/rules/python-style.md`, `.claude/rules/pytest.md` —
  code + notebook conventions the materials must model.

  > These specs (`LECTURES.md`, `LAB_DESIGN.md`) may carry an HTML-comment draft marker. Treat
  > them as **authoritative format guides anyway** — the draft-ignore rule governs lesson
  > *content*, not the specs that shape it (same exception the stage-2 skill uses).

**2. The lesson's roadmap docs** — `docs/origin/lesson_roadmaps/L<NN>/`:

- `objectives.md` — learning goals, main points, prerequisites, bridges to neighbors.
- `demos_or_activities.md` — teacher-led demos.
- `external_or_additional_resources.md` — optional; read if present.

**3. The lesson's student materials** — `src/fluffy_potato_curriculum/lessons/L<NN>/`:

- `L<LL><NN>_intro.md` — optional framing piece.
- `L<LL><NN>_lecture.{md,ipynb}` — one or more taught artifacts (slide-outline or notebook).
- `L<LL><NN>_lab_empty.ipynb` + `L<LL><NN>_lab_solutions.ipynb` — matched lab pairs (one shared
  `<NN>` per pair).
- `PROCTOR_NOTES.md` — exactly one per lesson; one section per lab problem.

  The `<NN>` item index is a **shared, contiguous** counter across all artifact types, so an
  alphabetical filename sort gives teaching order. Read the files in that sorted order — it is
  the sequence a student experiences.

**4. Track placement:**

- `src/fluffy_potato_curriculum/lessons/tracks.toml` and
  `src/fluffy_potato_curriculum/lessons/SYLLABUS.md` — whether `L<NN>` is in the mini track or
  full-only, and where it sits in the arc (mini ⊆ full).

**5. Neighboring lessons (for overlap + hand-off checks)** — the preceding and following lessons
that exist:

- Roadmaps: `docs/origin/lesson_roadmaps/L<NN-1>/`, `docs/origin/lesson_roadmaps/L<NN+1>/`.
- Materials: `src/fluffy_potato_curriculum/lessons/L<NN-1>/`,
  `src/fluffy_potato_curriculum/lessons/L<NN+1>/`.

  Lesson numbering is not always contiguous — if `L<NN±1>` doesn't exist, use the nearest
  existing lower/higher lesson dir instead. Read enough to know what students *arrive* knowing
  and what comes *next*; you don't need every file.

## Draft-marker handling

Honor the project's draft-ignore rule for roadmap **content**: if `objectives.md`,
`demos_or_activities.md`, or `external_or_additional_resources.md` opens with an HTML-comment
draft marker (e.g. `<!-- llm-status: draft, do not consume for now -->`), don't treat its
content as settled. Note it as a finding ("roadmap still draft — review is provisional") rather
than critiquing prose that isn't ready. The format specs in step 1 are exempt (see above).

## Review lenses

Evaluate the lesson along these lenses (all by default, or just the one named in `focus`):

1. **Subgoal coverage (contract).** Every subgoal in the PRD lesson-plan row must be taught
   *and* practiced — reachable from a lecture and exercised by a lab. Flag any subgoal that is
   stated but never landed, or material that teaches something the row doesn't list.

2. **Narrative / backdrop.** Read the materials in teaching order as a student would. Flag
   abrupt topic jumps with no connective "why this comes next" beat, concepts used before
   they're introduced, and sections that read as an unmotivated list when the roadmap's Main
   Points claim they form a connected system. (Classic smell: the roadmap says "these primitives
   are connected" but the lecture presents them as independent topics.)

3. **Roadmap ↔ materials consistency.** The materials must implement the roadmap. Flag drift:
   objectives or demos in the roadmap with no corresponding material; materials that teach
   beyond or against the roadmap; vocabulary, examples, or the bridge sentence to the next
   lesson worded differently between roadmap and materials.

4. **Internal ordering coherence.** Lecture order and lab order should tell the same story. Flag
   a lecture that sequences topics one way while the labs sequence them another (e.g. a lecture
   interleaves a topic that the labs group at the end) — pick which order is right and say so.

5. **Format-guide compliance.** Against `LECTURES.md` / `LAB_DESIGN.md` / `notebooks.md`:
   metadata block present and `title` matches the `H1`; notebooks have a `#top` anchor, a TOC
   cell, hierarchically numbered headings (≤ three levels), and `[↑ Back to top]` links;
   `_empty`/`_solutions` pairs have identical cell count/ordering/prose with only TODO cells
   differing; `_empty` outputs cleared; slide-outlines use exactly three heading levels;
   notebooks within the length cap; `PROCTOR_NOTES.md` has a section per lab problem.

6. **Neighbor hand-off.** Reinforcing an earlier lesson's concept by name + link is good;
   re-teaching it end-to-end is a bug, as is pre-empting the next lesson's material. Flag full
   double-coverage in either direction, and a bridge sentence that doesn't match what the
   neighbor actually does.

7. **Code / reproducibility (spot-check, don't run).** Teaching code should model the strict
   style (typed defs, `potato_llm` seam not raw SDKs, clarity over cleverness). Notebooks should
   be authored for linear restart-run-all. Flag obvious violations from reading; note that a live
   restart-run-all / `uv` gate was *not* executed (this skill is read-only) so the user can run
   it if a finding warrants.

## Procedure

1. **Load the file map** (all four/five groups above) in order. If the lesson has no roadmap
   dir, or no materials dir, say so up front — a review of half a lesson is still useful, but
   name what's missing.
2. **Walk the materials in teaching order** (alphabetical filename sort), holding the PRD row
   and roadmap beside them.
3. **Apply the lenses**, gathering concrete findings. Each finding names the specific
   file(s) and, where useful, the section/cell — cite `path:line` or `path` + heading so the
   user can jump straight there.
4. **Rank and report** (see below).

## Report format

Lead with a one-paragraph verdict: is the lesson solid, has-gaps, or needs-rework, and the
single most important issue. Then:

- **Findings, ranked most- to least-impactful.** For each: a one-line summary, the file(s) +
  location, *why it's a problem* (tie back to a lens), and a concrete suggested direction. Keep
  pedagogy findings and mechanical/format findings distinguishable (group or label them).
- **What's working** — a short list, so a good lesson isn't drowned in nitpicks and the user
  knows what not to disturb.
- **Not checked** — anything the read-only nature left unverified (notebook execution, the
  `uv run` gate), so the user can close the loop.

Do not print the full contents of files back to the user — reference them by path and section.

## Out of scope

- **No edits.** This skill does not modify roadmap docs, materials, specs, or the PRD. It
  reports; the user (or a follow-up authoring-skill run) fixes.
- **No running code.** Don't execute notebooks or the `uv` gate; recommend it where a finding
  needs confirmation.
- **No renumbering / scaffolding.** Numbering reconciliation is `sync-lesson-numbering`; new
  content is the two authoring skills.
- **One lesson per invocation.** To review several, run the skill once per `L<NN>`.
