---
name: build-lecture-deck
description: Convert a curriculum lecture slide-outline (a `L<NN><II>_lecture.md` / `K<NN><II>_lecture.md` file under src/fluffy_potato_curriculum/lessons/) into a PowerPoint (.pptx) deck. Runs a deterministic python-pptx script that maps the outline's `## section N.` dividers, `### slide N.M` slides, bullets, and markdown tables onto slides, and routes `diagram:`/`table:` authoring directives to speaker notes. Use when the user asks to turn a lesson lecture outline into slides, a PowerPoint, a .pptx, or a deck.
---

# Build a lecture deck from a slide-outline

Turn one **markdown lecture slide-outline** into a `.pptx` slide deck. The conversion is a
deterministic script (`build_deck.py`, python-pptx) — this skill decides *which* file to convert
and *where* to write it, then runs the script and reports the result. It does not hand-author
slides or edit the source outline.

Only the **`.md` lecture outlines** are convertible — the ones written in the slide-outline
format (`## section N.` + `### slide N.M`, per [LECTURES.md](../../../docs/origin/LECTURES.md)).
The `.ipynb` lectures, `_intro.md` framing files, and `K<NN>_guide.md` runbooks are *not*
slide-outlines and are out of scope.

## Inputs

- `lecture` — path to a lecture slide-outline, e.g.
  `src/fluffy_potato_curriculum/lessons/L02/L0202_lecture.md`. If the user names a lesson
  (e.g. "L02") without a file, list that lesson's `*_lecture.md` files and pick/confirm the
  slide-outline one.
- `out` *(optional)* — output `.pptx` path. Default: alongside the input with a `.pptx`
  suffix. **`.pptx` files are build artifacts** — they're gitignored; don't commit them.

## How the outline maps to slides

| Outline element | Becomes |
| --- | --- |
| `# <title>` + ```` ```yaml ```` block + leading `>` blockquote | one **title slide** (subtitle = lesson · duration · anchor model; blockquote → notes) |
| `## section N. <title>` | one **section-divider slide** |
| `### slide N.M <title>` | one **content slide** |
| `-` / `*` / `1.` bullets (nesting by indent) | slide bullets (2-space indent → sub-bullet) |
| GitHub-style markdown tables | native PowerPoint tables (bold header row) |
| `**bold**`, `*italic*`, `` `code` `` | matching runs (code → monospace) |
| `- diagram: …` / `- table: …` lead bullets | **speaker notes** (authoring directives, not slide text) |
| `[↑ Back to top]` links | dropped |

## How to run

```sh
uv run python .claude/skills/build-lecture-deck/build_deck.py <lecture.md> [--out <deck.pptx>]
```

The script prints the output path and a slide count (`N slides (S sections, C content)`). Sanity-
check that count against the outline's `### slide N.M` headings before handing the deck back.

Requires the `python-pptx` dev dependency (already in `pyproject.toml`); run everything through
`uv` so the pinned `.venv` is used.

## Out of scope / known limits

- **Styling is intentionally plain** — python-pptx's default template, 16:9, no brand theme. It's
  a faithful structural draft, not a designed deck; polish (theme, colors, logos) is a follow-up.
- **Diagrams are not drawn.** `diagram:` lines in the outline describe a visual the author still
  needs to make; the script parks them in speaker notes rather than inventing a picture.
- **Very dense slides can overflow.** A slide with many long bullets *and* a large table may run
  past the slide edge. The fix is in the *outline* (split one `### slide` into two), not the
  script — keep this skill's mapping 1 slide-heading → 1 slide.
- **No source edits.** This skill reads the outline and writes a `.pptx`; it never modifies the
  lecture `.md`. Reshaping the outline is a normal materials edit
  (`generate-materials-from-roadmap`), not this skill.
