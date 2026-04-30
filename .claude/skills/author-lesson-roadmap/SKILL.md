---
name: author-lesson-roadmap
description: Draft one of a lesson's two roadmap artifacts (objectives.md or demos_or_activities.md) under docs/origin/lesson_roadmaps/L<NN>/, following the project's authoring docs in docs/origin/. Use when the user asks to draft, scaffold, or plan lesson roadmap content. Takes a mode (objectives|demos_or_activities) and a lesson identifier (L<NN>). Stage 1 of a two-stage authoring flow — student-facing materials (lectures, labs) are produced by the separate `generate-materials-from-roadmap` skill in stage 2.
---

# Author a single lesson-roadmap artifact

Drafts exactly one *roadmap* artifact for a curriculum lesson, following the canonical guidance in `docs/origin/`. Run the skill once per artifact.

This skill is **stage 1** of a two-stage authoring flow:

1. **`author-lesson-roadmap` (this skill)** — produces the planning docs that describe *what* a lesson should teach: `objectives.md` (learning goals + main points) and `demos_or_activities.md` (teacher-led demos).
2. **`generate-materials-from-roadmap`** — consumes the roadmap docs and produces the student-facing materials (lectures, labs, proctor notes). Out of scope for this skill.

## Vocabulary (matches CURRICULUM_PRD.md)

- **Lesson** — the high-level unit. One `L<NN>/` directory; one row in the PRD's lesson-plan table.
- **Roadmap artifact** — one of the planning docs at the root of `L<NN>/`: either `objectives.md` or `demos_or_activities.md`.
- **Lecture** — one taught artifact within a lesson. Out of scope for this skill (handled by stage 2).
- **Lab** — one self-driven student exercise within a lesson. Out of scope for this skill (handled by stage 2).

## Inputs

- `lesson` — the `L<NN>` identifier (e.g. `L03`). Must correspond to a row in `docs/origin/CURRICULUM_PRD.md`'s "Lesson plan" table.
- `mode` — exactly one of:
  - `objectives` — draft the lesson's `objectives.md` (learning goals, main points, prerequisites, bridges).
  - `demos_or_activities` — draft the lesson's `demos_or_activities.md` (teacher-led demos, no student participation).

If either input is missing, ask for it before doing anything else.

## Procedure

1. **Read the canonical guidance, in order**:
   1. `docs/origin/CURRICULUM_PRD.md` — course intent, target audience, "Lecture Materials" depth-bias, and the lesson-plan row for the requested lesson (title + subgoals).
   2. `docs/origin/CLAUDE.md` — folder conventions for `docs/origin/lesson_roadmaps/L<NN>/` and the one-line specs for both roadmap artifacts.
   3. The sibling roadmap artifact, **if it already exists**. For example, if drafting `demos_or_activities.md`, read the existing `objectives.md` first so the demos align with the stated objectives (and vice versa). The two artifacts must agree on subgoals, vocabulary, and open-question wording.
   4. **The neighboring lessons' roadmaps, if they exist** — i.e. `docs/origin/lesson_roadmaps/L<NN-1>/` (preceding) and `docs/origin/lesson_roadmaps/L<NN+1>/` (following). Read both `objectives.md` and `demos_or_activities.md` where present. The goal is to understand what students will already have seen and what is coming next, so this lesson can build on prior concepts and hand off cleanly to the next.

2. **Honor the draft-ignore rule.** Before consuming any file in `docs/origin/`, check its first non-empty lines for an HTML-comment draft marker, e.g. `<!-- llm-status: draft, do not consume for now -->`. Skip any file marked draft. (For roadmap artifacts the format guide is `docs/origin/CLAUDE.md`, which is not draft today — but the check still applies if the user later marks it or adds new format guides.)

3. **Draft the artifact** following the format guide. Apply the PRD's "Lecture Materials" bias: written content should be thorough enough that a student who missed a verbal explanation — *or* a downstream stage-2 author working from the roadmap — can rebuild the lesson from the page. Back-reference earlier lessons by name and link, reusing the original wording so students recognize it. When in doubt, include more detail, more clarifications, more examples. For genuine uncertainties, leave `<need input: ...>` markers rather than asking the user up-front (per the project's scaffolding-style convention).

4. **Cross-check before reporting done**:
   - Path matches `docs/origin/lesson_roadmaps/L<NN>/<mode>.md` exactly.
   - Subgoals from the PRD lesson-plan row are each addressable from this artifact (or noted as deferred to its sibling).
   - If both roadmap artifacts now exist for this lesson, their `<need input>` markers and open-question lists are *consistent* — same questions, same wording, no contradictions. Mismatches between siblings will confuse stage 2.
   - The artifact stays in its lane: `objectives.md` is the *what* and *why*; `demos_or_activities.md` is the *teacher-led how*. No student-driven exercises in either — those belong in labs, produced by stage 2.
   - **No full double-coverage with neighboring lessons.** If the preceding (`L<NN-1>`) or following (`L<NN+1>`) roadmaps exist, scan them against this draft. Concepts introduced earlier *should* be reinforced here — referenced by name, briefly recalled, and built upon — but should not be re-taught from scratch. Likewise, do not pre-empt the next lesson by fully teaching what it is meant to introduce. If you find a concept being covered end-to-end in two lessons, either (a) demote one occurrence to a one-line callback with a link to the other lesson, or (b) leave a `<need input: overlap with L<NN±1> on <topic> — reinforce vs. re-teach?>` marker for the author to resolve. Reinforcement is good; full re-teach is a bug.

## Out of scope

- Do **not** modify `CURRICULUM_PRD.md`, `CLAUDE.md`, `LECTURES.md`, or `LAB_DESIGN.md` from this skill.
- Do **not** produce lectures, labs, `PROCTOR_NOTES.md`, or any student-facing material. Those are stage 2 (`generate-materials-from-roadmap`).
- Do **not** run `uv add` or any other side-effecting command. If a dependency is implied by a planned demo, surface it in the report-done message rather than installing it.
- Do **not** generate multiple artifacts in one invocation. If the user wants both `objectives` and `demos_or_activities`, run the skill twice.
