---
name: sync-lesson-numbering
description: Reconcile lesson directory names and L<NN> cross-references after the lesson-plan table in docs/origin/CURRICULUM_PRD.md is renumbered. Takes an explicit old→new remap and renames `docs/origin/lesson_roadmaps/L<NN>/` and `src/fluffy_potato_curriculum/lessons/L<NN>/` directories, updates content cross-references inside those trees, and verifies no stale refs remain. Use after inserting, removing, or reordering lessons in the PRD. Does not modify the PRD itself or scaffold new lesson directories — those are out of scope.
---

# Sync lesson numbering across the repo

After the **PRD lesson-plan table** is renumbered (lessons inserted, removed, or reordered), this skill brings the rest of the repo in sync. It is reconciliation, not authoring.

The PRD is the source of truth. This skill assumes the user (or Claude in a prior turn) has already updated `docs/origin/CURRICULUM_PRD.md`. The skill does **not** modify the PRD.

## Inputs

- `remap` — the old→new lesson-number mapping, as a list of pairs (e.g. `L08:L09, L09:L10, L10:L11, L11:L13, L12:L14, L13:L16, L14:L17, L15:L18`). Include **only** lessons whose number changed; omit lessons that kept their number. Newly inserted lessons (numbers that didn't exist before) are not part of the remap — they will be scaffolded later by `author-lesson-roadmap`.

If `remap` is missing or ambiguous, ask before doing anything else. Inferring the remap from `git diff` is brittle; require it explicitly.

## Files in scope (content cross-refs get rewritten)

- `docs/origin/lesson_roadmaps/**/*.md`
- `src/fluffy_potato_curriculum/lessons/**/*` (any text files, including `__init__.py`)

## Files out of scope (left untouched)

These files contain `L<NN>` tokens *as illustrative naming examples*, not as live cross-references. Do not rewrite them:

- Any `CLAUDE.md` (root or nested)
- `docs/origin/LECTURES.md`
- `docs/origin/LAB_DESIGN.md`
- Any `.claude/skills/**/SKILL.md`
- `docs/origin/CURRICULUM_PRD.md` (out of scope by design — the PRD drives the remap, not the other way around)

If you find an `L<NN>` reference in one of these files that genuinely *is* a live cross-reference (rare), surface it in the report-done message rather than rewriting it silently.

## Procedure

1. **Validate the remap.**
   - No duplicate `Lold` keys.
   - No duplicate `Lnew` values.
   - Every `Lnew` corresponds to a row in the PRD's "Lesson plan" table (read the PRD to confirm).
   - Every `Lold` corresponds to an existing directory under `docs/origin/lesson_roadmaps/` *or* `src/fluffy_potato_curriculum/lessons/` (one or both — a lesson may have a roadmap but no source dir yet, or vice versa). If an `Lold` has no directory in either tree, warn but continue (it may be a pure cross-reference rename).

2. **Plan a collision-free rename order.** A naive "rename L08→L09, then L09→L10" sequence will overwrite or fail on the second step because L09 already exists from step 1. Use one of:
   - **Two-pass:** rename every `Lold` directory to a temporary name (e.g. `L<old>__tmp`), then rename each temp to its `Lnew`.
   - **Topological:** if the remap forms a chain with no cycles, rename in reverse order (highest old → highest new first).

   Apply the same order to both the roadmap and source-lesson trees.

3. **Rename directories.** Use `git mv` so history follows the rename:
   - `docs/origin/lesson_roadmaps/L<old>/` → `L<new>/`
   - `src/fluffy_potato_curriculum/lessons/L<old>/` → `L<new>/`

   Skip a rename if the source directory doesn't exist.

4. **Rewrite cross-references inside in-scope files.** For every `Lold` in the remap, replace `L<old>` with `L<new>` in every in-scope file. Order matters here too — apply replacements in a way that doesn't double-rewrite (e.g. translate via a temp token, or do all reads before any writes).

   Be conservative about pattern matching: match `L` followed by exactly two digits as a whole token (boundary check on each side). Don't match inside larger identifiers like `L0103_lab` — those are item counters within a lesson, governed by `LECTURES.md`, and only the leading `L<NN>` portion should change. (In practice, the in-scope trees rarely contain item-numbered filenames, but flag any matches you find for the user to confirm.)

5. **Verify no stale references remain.** For each `Lold` in the remap, grep the in-scope trees for `L<old>` (whole-token). Expected count: zero. If any remain, surface them in the report-done message — usually a sign of an unexpected match (e.g. a quoted historical reference) that needs a human call.

6. **Report done.** Print:
   - The remap that was applied.
   - Directories renamed (roadmaps + source).
   - Files rewritten, with reference counts per file.
   - Any warnings (unmatched `Lold`, ambiguous matches, references found in out-of-scope files).

## Out of scope

- Do **not** modify `CURRICULUM_PRD.md`. The PRD drives the remap; the skill follows.
- Do **not** scaffold new lesson directories for inserted lessons. Use `author-lesson-roadmap` for that.
- Do **not** edit illustrative `L<NN>` examples in `CLAUDE.md`, `LECTURES.md`, `LAB_DESIGN.md`, or `SKILL.md` files.
- Do **not** rename item-level counters inside lesson filenames (e.g. `L0103_lab_empty.ipynb`) beyond their leading `L<NN>` portion. Item counters are governed by `LECTURES.md`.
- Do **not** run `uv add` or other side-effecting commands.
