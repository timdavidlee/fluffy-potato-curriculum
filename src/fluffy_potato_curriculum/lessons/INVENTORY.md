# Inventory & time estimates — mini track

A per-lesson time estimate for the **mini** course, derived bottom-up from the
material that currently exists on disk (not a top-down target). It counts each
lesson's items by type and applies a fixed per-item weight. Re-run the counts and
re-total whenever a lesson's item set changes.

Track membership and titles are owned by [tracks.toml](tracks.toml) /
[SYLLABUS.md](SYLLABUS.md); this file only adds the timing view.

## How the estimate is built

Each item type gets a fixed weight, anchored to the repo's own conventions:

| Item type | Weight | Basis |
| --- | --- | --- |
| `*_intro.md` | 5 min | short framing read |
| `*_lecture.md` (outline / slide notes) | 12 min | one short lecture segment |
| `*_lecture.ipynb` (live/teacher demo) | 15 min | the "~15-min focused segment" cap in [.claude/rules/notebooks.md](../../../.claude/rules/notebooks.md) |
| `*_lab` pair (`_empty` + `_solutions`) | 20 min | sum of the per-problem times in each lesson's `PROCTOR_NOTES.md` (~4–7 min × ~4 problems) |

These are **pure content/work minutes** for a semi-technical student — they do
not include breaks, room setup, Q&A, or slack. Treat each figure as a floor and
pad ~20–30% for a real class clock.

## Per-lesson estimate (mini track)

| #   | Title                                        | intro | lec.md | lec.ipynb | labs | Est. time |
| --- | -------------------------------------------- | :---: | :----: | :-------: | :--: | --------: |
| L01 | LLM and token basics                         |   1   |   1    |     6     |  3   |   2 h 45 m |
| L02 | Prompting fundamentals                       |   1   |   1    |     4     |  4   |   2 h 35 m |
| L03 | Directed graphs: from one node to a sequential chain |   1   |   1    |     3     |  1   |   1 h 20 m |
| L05 | Conditional graphs: routing & branching      |   1   |   2    |     1     |  1   |   1 h 05 m |
| L06 | Teaching an LLM to think via prompting       |   1   |   1    |     4     |  4   |   2 h 35 m |
| L07 | Tool calling: how it works                   |   1   |   1    |     4     |  3   |   2 h 15 m |
| L08 | Designing good tools                         |   1   |   1    |     4     |  4   |   2 h 35 m |
| L10 | Hand-rolled agent loop                       |   1   |   1    |     2     |  2   |   1 h 30 m |
| L11 | Shallow agents in LangGraph                  |   1   |   2    |     3     |  2   |   1 h 55 m |
| L12 | Tracing: reading what your agent did         |   1   |   1    |     2     |  2   |   1 h 30 m |
| L13 | Evaluation: first pass                       |   1   |   1    |     3     |  2   |   1 h 40 m |
| L22 | Skills: just-in-time capabilities for agents |   1   |   2    |     1     |  2   |   1 h 25 m |
| L23 | Skill patterns & composition                 |   —   |   —    |     —     |  —   | not built yet |

**Built mini lessons (12): ≈ 23.2 hours of content time.**

## Notes

- **L23 is not yet generated** (no `L23/` directory exists), so it carries no
  estimate. When built, expect it to land near L22's size (~1.5 h), pushing the
  mini total to roughly **25 h** of content time.
- The ~32 h figure quoted in [SYLLABUS.md](SYLLABUS.md) / the PRD is the
  *planned* clock including breaks, setup, discussion, and buffer; the ~23.5 h
  here is bottom-up content-only work, so the two are consistent (the gap is the
  pad).
- The lesson sizes are uneven by design: L05 (conditional graphs) is a short
  single-lab lesson, while L03 — after the 2026-07-09 merge of single-node +
  sequential chaining — carries three demos and a lab; L01/L02/L06/L08 remain
  the heavy multi-demo lessons.
