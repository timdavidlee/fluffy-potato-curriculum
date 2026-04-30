<!-- llm-status: draft, do not consume for now -->

# Lab Design Guidelines

A **lab** is a self-driven exercise where a student practices a concept
introduced in a lecture or experiments with a library hands-on. Labs are the primary
way students convert passive lecture material into working knowledge.

## File layout

Labs live alongside their parent lesson under
`src/fluffy_potato_curriculum/lessons/L<NN>/`. Each lesson can have one or more
labs, interleaved with lectures and (optionally) an intro.

```
src/fluffy_potato_curriculum/lessons/L01/
    objectives.md             # roadmap (see docs/origin/CLAUDE.md)
    demos_or_activities.md    # roadmap (see docs/origin/CLAUDE.md)
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
