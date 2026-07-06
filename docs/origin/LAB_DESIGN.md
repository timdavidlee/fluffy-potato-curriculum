# Lab Design Guidelines

A **lab** is a self-driven exercise where a student practices a concept
introduced in a lecture or experiments with a library hands-on. Labs are the primary
way students convert passive lecture material into working knowledge.

## Voice

Labs are written **to the student, in the second person** — see the course-wide rule in
[CURRICULUM_PRD.md](CURRICULUM_PRD.md#voice--point-of-view). The lab-specific register is **Punchy**:
terse, energetic, high-signal. A lab is a list of things to *do*, so the prose keeps momentum and
gets out of the way.

**Punchy in practice**

- Lead with the action; cut hedging and throat-clearing. Short sentences, strong verbs.
- Trim *words*, never *substance* — every function name, argument, step, and acceptance check a
  student needs stays exactly as precise as before.

| ✗ Flat / wordy | ✓ Punchy |
| --- | --- |
| "Script a stub that never stops — many distinct `lookup` turns. Invoke with `{"recursion_limit": 6}` and confirm a `GraphRecursionError` fires." | "**Now break it on purpose.** Script a stub that never stops… Invoke with `{"recursion_limit": 6}` and **watch `GraphRecursionError` fire.**" |
| "After this lab you can: wire a ReAct agent as a cyclic `StateGraph`…" | "**You'll walk out able to** build a ReAct agent as a cyclic `StateGraph`…" |
| "If it's an `AIMessage` whose `.tool_calls` is non-empty, return `\"tools\"`; otherwise return `END`." | "Tool calls waiting? Return `\"tools\"`. Anything else? Return `END`." |

- **Table-related text stays terse** (course-wide rule) — fragments in the cells, not sentences.
- **Preserve the scaffolding.** Revoice prose only: leave code cells, `# TODO` markers, and section
  **headings** untouched — headings feed the Contents/TOC anchors, so changing them breaks the links.
- **Keep `_empty` and `_solutions` in lockstep.** Their prose and ordering must match exactly, so when
  you revoice one, mirror it into the other in the same pass.

## File layout

Labs live alongside their parent lesson under
`src/fluffy_potato_curriculum/lessons/L<NN>/`. Each lesson can have one or more
labs, interleaved with lectures and (optionally) an intro.

```
src/fluffy_potato_curriculum/lessons/L01/
    L0101_intro.md            # see LECTURES.md
    L0102_lecture.ipynb       # see LECTURES.md
    L0103_lab_empty.ipynb
    L0103_lab_solutions.ipynb
    L0104_lecture.md          # see LECTURES.md
    L0105_lab_empty.ipynb
    L0105_lab_solutions.ipynb
    PROCTOR_NOTES.md
```

The numeric `<LL><NN>` prefix keeps every artifact in teaching order when sorted alphabetically. The type suffix (`_intro` / `_lecture` / `_lab`) is just a hint to the reader and does **not** affect sorting. A lab `_empty`/`_solutions` pair shares a single `<NN>` — it counts as one item, two files.

## Naming

Lab files follow `L<LL><NN>_lab_<variant>.ipynb`, where:

- `LL` — two-digit lesson number, matching the parent `L<NN>/` directory.
- `NN` — two-digit *item* index within that lesson, starting at `01`. The `NN` counter is **shared across all artifact types** (lectures, labs, intros), so sorting by filename gives teaching order.
- `<variant>` — either `empty` or `solutions` (see below).

Examples:

| File                          | Meaning                                      |
| ----------------------------- | -------------------------------------------- |
| `L0103_lab_empty.ipynb`       | Lesson 01, item 03, the lab — student copy   |
| `L0103_lab_solutions.ipynb`   | Lesson 01, item 03, the lab — solutions copy |
| `L0207_lab_empty.ipynb`       | Lesson 02, item 07, the lab — student copy   |

## Variants: `_empty` and `_solutions`

Every lab ships as a matched pair:

- **`_empty`** — the version handed to students. Contains prose, scaffolding,
  and cells with `# TODO` markers (or blank answer cells) where students write
  code or written responses.
- **`_solutions`** — the same notebook with every TODO filled in with a working
  reference answer. Cell structure, prose, and ordering must match `_empty`
  exactly so a student can diff their work against the solutions.

> Rule of thumb: `_solutions` is `_empty` with the gaps filled in — not a
> different document.

## Runtime

- Python 3.13 or greater (matches the project's `.python-version`).
- Designed to run in Jupyter notebooks via `uv run jupyter lab` (or equivalent).
- Any third-party dependency a lab uses **must** be added to the project with
  `uv add <pkg>` so it appears in `pyproject.toml` / `uv.lock`. Do not rely on
  inline `%pip install` cells.

## Notebook structure

Each `_empty` notebook should open with, in order:

1. **Title + lesson link** — `# Lab L<LL><NN>: <short title>` and a one-line
   pointer back to the lesson's `objectives.md`.
2. **Learning objectives** — bulleted list of what the student will be able to
   do after finishing. These should be a subset of the parent lesson's
   objectives.
3. **Setup cell** — imports and any data loading. Should run top-to-bottom
   without student edits.
4. **Exercises** — alternating prose + TODO cells. Each exercise is numbered
   ("Problem 1", "Problem 2", …) and states the task in one or two sentences.
5. **Self-check / Verification** —
   No automated checking will be applied; the solutions will serve as the
   student's answer sheet to check against if they desire.

## Proctor notes

Each lesson directory contains exactly one `PROCTOR_NOTES.md` covering every
lab in that lesson. It is organized with one section per problem, keyed by the
lab's `L<LL><NN>` identifier and problem number, e.g.:

```markdown
## L0103_lab problem 4

COMMON GOTCHAS: ...
UNBLOCKERS: ...
```

Each section should cover, where applicable:

- Common student mistakes and how to redirect.
- Environment or data gotchas.
- Approximate time-to-complete.
- Stretch hints for students who finish early.

## Metadata

The top of every lab must declare metadata in its first markdown cell (applies to both `_empty` and `_solutions` variants).

Required fields:

- **title** — matches the notebook's `H1`.
- **keywords** — comma-separated list for searchability.
- **estimated duration** — in minutes.


## Authoring checklist

Before a lab is considered done:

- [ ] `_empty` runs top-to-bottom on a fresh kernel without errors *up to* the
      first TODO cell.
- [ ] `_solutions` runs top-to-bottom on a fresh kernel with no errors.
- [ ] Cell count and ordering match between `_empty` and `_solutions`.
- [ ] Outputs cleared in `_empty`; outputs may be retained in `_solutions` to
      show expected results.
- [ ] Any new dependency was added via `uv add`.
- [ ] `PROCTOR_NOTES.md` has a section for every problem in this lab.
