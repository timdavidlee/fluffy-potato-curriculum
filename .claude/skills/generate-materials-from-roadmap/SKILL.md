---
name: generate-materials-from-roadmap
description: Generate a lesson's student-facing materials (intro, lecture notebooks/slide-outlines, lab _empty/_solutions pairs, PROCTOR_NOTES.md) under src/fluffy_potato_curriculum/lessons/L<NN>/ from its roadmap docs in docs/origin/lesson_roadmaps/L<NN>/, following LECTURES.md and LAB_DESIGN.md. Use when the user asks to implement, build, or generate the actual coding/teaching files for a lesson from its docs. Takes a lesson identifier (L<NN>) and an optional artifact filter. Stage 2 of the two-stage authoring flow (the stage author-lesson-roadmap hands off to).
---

# Generate a lesson's materials from its roadmap

Consumes the **roadmap docs** for one lesson and produces the **student-facing materials** that
implement it: an optional intro, lectures (slide-outline `.md` and/or teacher notebooks),
lab `_empty`/`_solutions` pairs, and a single `PROCTOR_NOTES.md`. Everything lands under
`src/fluffy_potato_curriculum/lessons/L<NN>/`.

This skill is **stage 2** of the two-stage authoring flow:

1. **`author-lesson-roadmap`** — produces the planning docs that describe *what* a lesson teaches:
   `objectives.md` and `demos_or_activities.md` under `docs/origin/lesson_roadmaps/L<NN>/`.
2. **`generate-materials-from-roadmap` (this skill)** — consumes those roadmap docs and produces
   the runnable, student-facing artifacts. This is the stage `author-lesson-roadmap` hands off to.

## Vocabulary (matches CURRICULUM_PRD.md, LECTURES.md, LAB_DESIGN.md)

- **Lesson** — the high-level `L<NN>/` unit; one row in the PRD lesson-plan table.
- **Roadmap artifact** — the input planning docs (`objectives.md`, `demos_or_activities.md`,
  optionally `external_or_additional_resources.md`) under `docs/origin/lesson_roadmaps/L<NN>/`.
- **Intro** — short optional opening artifact (`L<LL><NN>_intro.md`), a 1–2 page framing piece.
- **Lecture** — one teacher-presented artifact: a slide-outline `.md` *or* a teacher notebook
  `.ipynb` (`L<LL><NN>_lecture.{md,ipynb}`).
- **Lab** — one self-driven student exercise, shipped as a matched pair
  `L<LL><NN>_lab_empty.ipynb` + `L<LL><NN>_lab_solutions.ipynb`.
- **Item index `<NN>`** — the two-digit counter **shared across all artifact types** in a lesson,
  so alphabetical filename sort gives teaching order. A lab pair shares one `<NN>` (one item, two
  files).

## Inputs

- `lesson` — the `L<NN>` identifier (e.g. `L01`). Must have a roadmap directory at
  `docs/origin/lesson_roadmaps/L<NN>/` and correspond to a row in `docs/origin/CURRICULUM_PRD.md`.
- `only` *(optional)* — restrict output to a subset of artifact types, e.g. `lectures`,
  `labs`, `intro`, `proctor`. Default: generate the full material set the roadmap calls for.

If `lesson` is missing, or its roadmap directory doesn't exist, ask before doing anything else.
(A missing roadmap means stage 1 hasn't run — point the user at `author-lesson-roadmap`.)

## Read first, in order

1. **`docs/origin/CURRICULUM_PRD.md`** — course intent, target audience, the "Lecture Materials"
   depth-bias, and the lesson-plan row for the requested lesson (title + subgoals).
2. **The lesson's roadmap docs** — `objectives.md`, then `demos_or_activities.md`, then
   `external_or_additional_resources.md` if present. These define *what* to build.
3. **The format guides** — `docs/origin/LECTURES.md` (lecture + intro conventions, slide-outline
   and notebook formats, metadata) and `docs/origin/LAB_DESIGN.md` (lab structure, `_empty`/
   `_solutions` parity, proctor notes, authoring checklist).
4. **Neighboring lessons' materials, if they exist** — `src/fluffy_potato_curriculum/lessons/
   L<NN-1>/` and `L<NN+1>/`. Understand what students have already built and what comes next, so
   this lesson builds on prior code and hands off cleanly (no full re-teach of a neighbor's topic).
5. **The repo's code-style rules** — `.claude/rules/python-style.md`, `.claude/rules/pytest.md`,
   and `.claude/rules/notebooks.md` (notebook length cap, structure/navigation, output hygiene).
6. **Reusable library code** — scan `src/fluffy_potato_curriculum/common/` and
   `src/fluffy_potato_curriculum/potato_llm/` before writing any helper. If a lesson needs to talk
   to an LLM, use the existing `potato_llm` client (`PotatoLLMClient`, `AnthropicClient`,
   `Message`, …) — do not hand-roll a new client.

## Draft-marker handling

Honor the project's draft-ignore rule for roadmap **content** files: if `objectives.md`,
`demos_or_activities.md`, or `external_or_additional_resources.md` open with an HTML-comment draft
marker (e.g. `<!-- llm-status: draft, do not consume for now -->`), skip that file and surface it —
you can't implement from a roadmap that isn't ready.

**Exception — format-spec guides.** `LECTURES.md` and `LAB_DESIGN.md` are *format specifications*,
not content. Consume them as authoritative even though they currently carry a draft marker. The
draft-ignore rule governs lesson content, not the specs that say how to shape it.

## Procedure

1. **Plan the artifact list.** From the roadmap, decide which artifacts the lesson needs and in
   what teaching order. The `demos_or_activities.md` entries usually map to lectures; objectives
   that say "students will be able to…" usually map to labs. Decide notebook vs. slide-outline per
   `LECTURES.md` ("Slide Outline Markdown vs. Jupyter Notebook"): default to slide outlines, reach
   for a notebook only for live programmatic illustration, interactive segments, or a library demo
   before a lab. Lectures and their companion labs interleave; a lecture always precedes its lab
   numerically.

2. **Assign `<NN>` item indices.** Continue the **shared, contiguous** counter across all artifact
   types — inspect any files already in `L<NN>/` and pick up where they leave off; never restart at
   `01` per type. A lab pair consumes a single `<NN>`. Filenames follow `L<LL><NN>_<type>...`:
   `L0101_intro.md`, `L0102_lecture.ipynb`, `L0103_lab_empty.ipynb` + `L0103_lab_solutions.ipynb`,
   etc. `LL` is the zero-padded lesson number.

3. **Author each artifact** to its format guide:
   - **Metadata first.** Every lecture and lab declares `title` / `keywords` / `estimated
     duration` — a fenced YAML block under the `#` title for `.md`, or the first markdown cell for
     `.ipynb`. `title` must match the `H1`.
   - **Slide-outline lectures** — exactly three heading levels (`#` title, `##` section, `###`
     slide); bullets default to text, with `diagram:` / `table:` one-line prefixes per `LECTURES.md`.
   - **Notebook lectures** — alternate concise markdown (concept) and code (demo) cells; first code
     cell is a self-contained setup cell (imports + data) that runs without edits; fully
     type-hinted (pyright strict), generous docstrings/comments; self-contained — define helper
     functions inline rather than importing from `src/` (per `LECTURES.md`). Must run top-to-bottom
     on a fresh kernel; outputs may be retained. Keep within the length cap in
     `.claude/rules/notebooks.md` — split into another lecture item rather than overflow.
   - **Notebook navigation (every `.ipynb`, lecture *and* lab)** — per `.claude/rules/notebooks.md`:
     put a `<a id="top"></a>` anchor in the title cell; make the cell after title/metadata a
     **table of contents** linking each numbered section; number section headings hierarchically
     (`## 1. …` → `### 1.1 …` → `#### 1.1.1 …`, max three levels); and end each top-level section
     with a `[↑ Back to top](#top)` link. Keep the TOC in sync with the headings you emit.
   - **Labs** — open with title + pointer to `objectives.md`, learning objectives (a subset of the
     lesson's), a setup cell, then numbered "Problem N" exercises (prose + `# TODO` cells), then a
     self-check note (solutions are the answer key; no automated grading). `_solutions` is `_empty`
     with the gaps filled — **identical cell count, ordering, and prose**; only TODO cells differ.
     Clear outputs in `_empty`; retain them in `_solutions` to show expected results.
   - **Intro** — short 1–2 page framing piece, treated as a lightweight lecture (same metadata).
   - **PROCTOR_NOTES.md** — exactly one per lesson, one section per problem keyed by
     `L<LL><NN>_lab problem <n>`, covering common gotchas, unblockers, approximate time, and stretch
     hints.

4. **Honor the curriculum style.** Teaching code: clarity over cleverness, explicit readable steps,
   comment the *why*. Anchor on the course's standard model where a lesson calls an LLM (see the
   PRD / project conventions), reusing `potato_llm` rather than the raw SDKs. Reinforce concepts
   from earlier lessons by name and link; don't re-teach them end-to-end, and don't pre-empt the
   next lesson.

5. **Dependencies via `uv add`.** Any third-party package a lecture or lab imports must be installed
   with `uv add <pkg>` (dev-only with `--dev`) so `pyproject.toml` / `uv.lock` stay in sync. Never
   rely on inline `%pip install` cells. Most LLM deps already exist via `potato_llm` — only add
   genuinely new ones.

6. **Verify before reporting done:**
   - Filenames match `L<LL><NN>_...` with a correct, contiguous shared `<NN>` counter; alphabetical
     sort yields teaching order.
   - Code style gate on any `.py` touched: `uv run ruff format && uv run ruff check && uv run
     pyright`. (Notebooks aren't linted by the gate, but their code should still satisfy the style
     rules and type-check cleanly.)
   - Each notebook executes top-to-bottom on a fresh kernel without errors — run it (e.g.
     `uv run jupyter execute <nb>` or `uv run jupyter nbconvert --to notebook --execute`). `_empty`
     must at least run cleanly up to its first TODO; `_solutions` must run end-to-end.
   - `_empty` and `_solutions` have matching cell count and ordering; `_empty` outputs cleared.
   - Every notebook has a TOC cell, a `#top` anchor with `[↑ Back to top]` links at section ends,
     and hierarchically numbered headings (≤ three levels); TOC entries match the actual headings.
   - `PROCTOR_NOTES.md` has a section for every problem in every lab in this lesson.
   - Every artifact's metadata block is present and its `title` matches the `H1`.

7. **Report done.** List the files created/updated (with their `<NN>` indices), any dependency
   added via `uv add`, any roadmap file skipped for a draft marker, and any verification step that
   could not run (e.g. notebook execution needing API keys) so the user can finish it.

## Out of scope

- Do **not** modify `CURRICULUM_PRD.md`, the roadmap docs, `LECTURES.md`, or `LAB_DESIGN.md`. This
  skill *reads* the roadmap and specs; it does not edit them. (Roadmap authoring is stage 1.)
- Do **not** invent ad-hoc artifact types or naming — only `_intro`, `_lecture`, `_lab` with the
  shared `<NN>` counter.
- Do **not** restart the `<NN>` counter per artifact type, and do **not** let `_empty`/`_solutions`
  drift in structure.
- Do **not** hit a live LLM API as part of *generating* the files; if a notebook is designed to
  call an LLM at run time, write it against `potato_llm` and note in the report that execution
  needs API keys.
- Do **not** hand-edit `pyproject.toml` for dependencies — use `uv add`.
