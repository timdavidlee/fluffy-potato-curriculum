# lessons/

Student-facing lesson materials. Each `L<NN>/` directory holds the generated teaching
artifacts for one lesson (zero-padded, monotonically increasing — `L01` is taught first).

## Mini vs full tracks

Lesson directories stay **flat** (`L01/` … `L23/`) — there is no `mini/` or `full/`
subfolder. Track membership is data, not directory structure: [tracks.toml](tracks.toml)
is the single source of truth for which lessons belong to the mini vs full course
(`mini` is always a subset of `full`), and [SYLLABUS.md](SYLLABUS.md) is the readable
view. Both mirror the master + "Condensed Mini Lesson Plan" tables in
`docs/origin/CURRICULUM_PRD.md` — keep the PRD and `tracks.toml` in sync when lessons
change.

## Where the source material lives

These directories are **generated from roadmaps**, not authored by hand. The source of truth
for what a lesson teaches is its roadmap:

```
docs/origin/lesson_roadmaps/L<NN>/objectives.md            # learning goals + main points
docs/origin/lesson_roadmaps/L<NN>/demos_or_activities.md   # teacher-led demos / activities
docs/origin/lesson_roadmaps/L<NN>/external_or_additional_resources.md  # optional links
```

The two-stage authoring flow:

1. **Roadmap (stage 1)** — `author-lesson-roadmap` skill writes the `docs/origin/lesson_roadmaps/L<NN>/` artifacts.
2. **Materials (stage 2)** — `generate-materials-from-roadmap` skill reads that roadmap and produces the files in this directory.

The conventions that govern generation live in `docs/origin/`: `CURRICULUM_PRD.md` (the primary
design file), `LECTURES.md`, and `LAB_DESIGN.md`. Read the roadmap and those docs before
editing materials here — don't reverse-engineer intent from the generated files.

## File layout inside each L<NN>/

Items are numbered `L<NN><II>` where `<II>` is the item's order within the lesson:

- `L<NN>01_intro.md` — lesson intro / framing
- `L<NN>NN_lecture.md` / `L<NN>NN_lecture.ipynb` — lecture content (markdown outline or notebook)
- `L<NN>NN_lab_empty.ipynb` / `L<NN>NN_lab_solutions.ipynb` — paired student / solution lab notebooks
- `PROCTOR_NOTES.md` — teaching notes for whoever runs the lesson
- `__init__.py` — keeps the lesson importable as a package

## Conventions

- Notebook authoring rules: [.claude/rules/notebooks.md](../../../.claude/rules/notebooks.md).
- Python style / typing: [.claude/rules/python-style.md](../../../.claude/rules/python-style.md).
- Notebooks are live-by-default and load API keys through the `common/config.py` config seam —
  never hard-code keys.
