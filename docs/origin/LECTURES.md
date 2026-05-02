<!-- llm-status: draft, do not consume for now -->

# Lecture Material Guidelines

A **lecture** is teacher-presented material *within a lesson*, in the form of:

- slide-deck outlines in markdown files
- teacher-led jupyter notebooks
- the files are provided to the students for reference

(See [CURRICULUM_PRD.md](CURRICULUM_PRD.md) for the lesson-vs-lecture distinction: a *lesson* is the high-level `L<NN>/` unit and one row in the lesson plan; a *lecture* is one teacher-presented artifact inside it.)

## File layout

Lectures live alongside their parent lesson under
`src/fluffy_potato_curriculum/lessons/L<NN>/`. They share the directory with labs, roadmap docs, and (optionally) intros.

```
src/fluffy_potato_curriculum/lessons/L01/
    objectives.md             # roadmap (see docs/origin/CLAUDE.md)
    demos_or_activities.md    # roadmap (see docs/origin/CLAUDE.md)
    L0101_intro.md
    L0102_lecture.ipynb
    L0103_lab_empty.ipynb     # see LAB_DESIGN.md
    L0103_lab_solutions.ipynb
    L0104_lecture.md
    L0105_lab_empty.ipynb     # see LAB_DESIGN.md
    L0105_lab_solutions.ipynb
    PROCTOR_NOTES.md          # see LAB_DESIGN.md
```

The numeric `<LL><NN>` prefix keeps every artifact in teaching order when sorted alphabetically. The type suffix (`_intro` / `_lecture` / `_lab`) is just a hint to the reader and does **not** affect sorting.

## Naming

Lecture files follow `L<LL><NN>_lecture.{md,ipynb}`, where:

- `LL` — two-digit lesson number, matching the parent `L<NN>/` directory.
- `NN` — two-digit *item* index within that lesson, starting at `01`. The `NN` counter is **shared across all artifact types in the lesson** (lectures, labs, intros), so sorting by filename gives teaching order.
- `_lecture` — a reader hint that this artifact is a lecture. Recognized type suffixes are `_intro`, `_lecture`, and `_lab` (see [LAB_DESIGN.md](LAB_DESIGN.md) for `_lab`).

Examples:

| File                  | Meaning                                                              |
| --------------------- | -------------------------------------------------------------------- |
| `L0101_lecture.ipynb` | Lesson 01, item 01, a lecture                                        |
| `L0102_lecture.md`    | Lesson 01, item 02, a lecture (item 02 may sit between two labs)     |
| `L0503_lecture.ipynb` | Lesson 05, item 03, a lecture                                        |

> The `<NN>` counter is contiguous across artifact types. If `L0101_intro.md` and `L0102_lab_empty.ipynb` already exist in `L01/`, the next lecture is `L0103_lecture.*`, not `L0102_lecture.*`. A lab `_empty`/`_solutions` pair shares a single `<NN>` — it counts as one item, two files.

## Relationship to labs and intros

Lectures, labs, and intros share the same `L<NN>/` directory and the same monotonic `<NN>` counter. See [LAB_DESIGN.md](LAB_DESIGN.md) for lab conventions; intros are described below.

Within a lesson, lectures and labs typically interleave so a lecture introduces a concept and the immediately-following lab lets students practice it. Because the `<NN>` counter is shared, teaching order is encoded directly in the filename. For example:

```
L0101_intro.md
L0102_lecture.ipynb       # concept A
L0103_lab_empty.ipynb     # practice concept A
L0103_lab_solutions.ipynb
L0104_lecture.md          # concept B
L0105_lab_empty.ipynb     # practice concept B
L0105_lab_solutions.ipynb
```

A lecture always precedes its companion lab numerically (so a `_lecture` at NN=02 precedes a `_lab` at NN=03), but a lesson may have a lecture without a lab (or a lab without an immediately-preceding lecture) when the topic doesn't warrant both.

### `_intro` artifacts

`_intro` is a short, optional opening artifact for a lesson — a one- to two-page framing piece (markdown or notebook) that sets context before any deeper lecture or lab. Treat it as a lightweight lecture: same authoring conventions, same metadata fields, just shorter. <!-- *NEED INPUT*: should `_intro` get its own dedicated format guide (e.g. `INTRO_DESIGN.md`), or stay co-spec'd here? Default for now: stay here. -->

## Runtime

- Python 3.13 or greater (matches the project's `.python-version`).
- Designed to run in Jupyter notebooks via `uv run jupyter lab` (or equivalent).
- Any third-party dependency a lecture uses **must** be added to the project with
  `uv add <pkg>` so it appears in `pyproject.toml` / `uv.lock`. Do not rely on
  inline `%pip install` cells.

## Slide Outline Markdown vs. Jupyter Notebook

Rules:

- Default to slide outlines for most lecture material.
- Only use Jupyter Notebooks:
    - to show live programmatic illustrations, e.g. plotting the weights on vectors
    - interactive lecture segments e.g. how a string is tokenized
    - demonstrate a popular python library + its functions before a lab


## Slide Outline Markdown Format


Rule 1: Use exactly three heading levels — lecture title (`#`), section (`##`), slide (`###`). E.g.

```md
# Lecture Title: LLM building blocks

## section 1. What is a token?

### slide 1.1 History

### slide 1.2 History part 2

### slide 1.3 Today how its used

## section 2. What is an embedding?

### slide 2.1 How to choose the size

### slide 2.2 How the weights are determined

```

Rule 2: under the sections define the following slide elements:

- **text**: the default content. If no prefix is added, the bullet is assumed to be text.

- **diagram**: a one-line description of what the diagram is showing

- **table**: a one-line description of what the table is showing

A short example

```md
### slide 1.1 History

table: a table of key dates and milestones

<markdown table here>


### slide 1.2 History part 2

- the first token used to be a word
- but consider different forms of the word "manage"
- diagram: show `manage`, `manager`, `management`, `managing` with each of the suffixes highlighted in a different color
```


## Jupyter Notebook Lecture Format

A notebook lecture alternates markdown cells (concept) with code cells (demonstration). The example below shows the markdown-cell content; `<code block ...>` placeholders mark where a code cell sits.

```md
# Lecture Title: Tokenizers

## Concepts and Goals

- understand how tokens are split
- try different tokenizers and examine how various phrases are split up
- understand how phrases can be encoded to IDs and back again

<setup cell: imports and any data loading; runs top-to-bottom without edits>


## Concept 1: Whole-word tokenizers

- Demonstrate a whole-word tokenizer

<code block using a whole-word tokenizer to process 3 different phrases>


## Concept 2: Character-based tokenizers

<code block using a character-based tokenizer to process the same 3 phrases>
```

**General notebook rules**

- Markdown cells are concise and stay on point — they frame the demo, not replace it.
- The notebook is self-contained: define helper functions inline rather than importing from `src/fluffy_potato_curriculum/`.
- The first code cell is a setup cell (imports + data loading) that runs without student edits.
- Code is fully type-hinted (the project runs pyright in `strict` mode) and uses docstrings + inline comments generously to aid student reading.
- The notebook must run top-to-bottom on a fresh kernel without errors.
- Outputs may be retained in the committed copy — these are the teacher's reference notebooks, not student-handed-out files.


## Metadata

The top of every lecture must declare metadata. For `.md` lectures this is a fenced YAML block under the title; for `.ipynb` lectures it is the first markdown cell.

Required fields:

- **title** — matches the file's `H1`.
- **keywords** — comma-separated list for searchability.
- **estimated duration** — in minutes.
