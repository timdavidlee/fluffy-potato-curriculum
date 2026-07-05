---
name: build-lecture-deck
description: Convert a curriculum lecture slide-outline (a `L<NN><II>_lecture.md` / `K<NN><II>_lecture.md` file under src/fluffy_potato_curriculum/lessons/) into a self-contained HTML slide deck (`L<NN><II>_lecture_deck.html`) in the shared "Graph Canvas" theme — copying slide_theme/sample_deck.html and filling each `## section N.` / `### slide N.M` in, building every `diagram:` directive as a real CSS/SVG visual per slide_theme/FRONTEND-STYLE.md. Use when the user asks to turn a lesson lecture outline into slides, an HTML deck, or a browser presentation.
---

# Build an HTML lecture deck from a slide-outline

Turn one **markdown lecture slide-outline** into a self-contained **HTML deck**
(`L<NN><II>_lecture_deck.html`) rendered in the curriculum's shared **"Graph Canvas"** theme.

This is the curriculum's themed counterpart to the generic `frontend-slides` skill: reuse that
skill's self-contained, animation-rich HTML-presentation mechanics, but the house style here is
**fixed**. [`slide_theme/FRONTEND-STYLE.md`](../../../src/fluffy_potato_curriculum/lessons/slide_theme/FRONTEND-STYLE.md)
and [`slide_theme/sample_deck.html`](../../../src/fluffy_potato_curriculum/lessons/slide_theme/sample_deck.html)
are authoritative — so **skip the aesthetic-exploration step** and copy the sample.

This is a **model-driven authoring task, not a script.** You copy the sample deck, map the outline
onto it, and — the part a script can't do — **build each `diagram:` directive as a real CSS-block or
SVG visual** and keep every slide from overflowing the fixed 1920×1080 stage.

## Read first (authoritative, in order)

1. **`slide_theme/FRONTEND-STYLE.md`** — the spec: the fixed stage, design tokens, the four slide
   types, content components, how to build diagrams (§5), chrome/nav, and the per-deck checklist
   (§7). Follow it exactly; do not invent styling.
2. **`slide_theme/sample_deck.html`** — the copy-from starting point. Every deck copies its tokens,
   canvas, components, and nav JS **byte-for-byte**; you change only the per-deck content.
3. **The target `.md` outline** — the content source of truth.
4. **[`docs/origin/LECTURES.md`](../../../docs/origin/LECTURES.md)** — the slide-outline format
   (`## section N.` + `### slide N.M`, bullets, tables, `diagram:` / `table:` directives).

## Inputs

- `lecture` — path to a lecture slide-outline, e.g.
  `src/fluffy_potato_curriculum/lessons/L02/L0202_lecture.md`. If the user names a lesson (e.g.
  "L02") without a file, list that lesson's `*_lecture.md` files and pick/confirm the slide-outline
  one (an `.ipynb` lecture is **not** a slide-outline — see scope).
- `out` *(optional)* — output path. Default: the deck alongside the outline, named
  `L<NN><II>_lecture_deck.html`. **HTML decks are committed source** (unlike the retired `.pptx`
  build artifacts) — this file is meant to be committed.

## Only `.md` slide-outlines are convertible

The `.ipynb` lectures, `_intro.md` framing files, and `K<NN><II>_guide.md` runbooks are **not**
slide-outlines and are out of scope. Only the `L<NN><II>_lecture.md` / `K<NN><II>_lecture.md` files
written in the `## section N.` + `### slide N.M` format convert.

## Procedure

1. **Copy** `sample_deck.html` to the `out` path. Everything below edits *only* the per-deck content
   the spec's §7 checklist lists — tokens, canvas, components, and nav JS stay identical.
2. **Set the per-deck chrome:** the `<title>`, the `.chrome-tag` topic label (`L<NN> · <b>TOPIC</b>`),
   and the `InlineEditor` `localStorage` key → `l<NN><II>-deck-content` (unique per deck, or decks
   clobber each other's saved edits).
3. **Cover slide** from the outline's `# <title>` + ` ```yaml ` block + leading `>` blockquote:
   eyebrow, big Fraunces `h1`, the one-line claim, the meta-row (lesson · duration · anchor model),
   and a `cover-diagram` SVG.
4. **One slide per heading, in order:** each `## section N.` → a `slide-chapter` divider; each
   `### slide N.M` → one content slide (`topbar` eyebrow + headline over a `body-area`).
5. **Fill each content slide's body** with the right component (mapping below), building diagrams as
   real visuals.
6. **Number the chrome:** `.chrome-page` `NN / TOTAL` on every slide (cover = `01`; TOTAL = cover +
   dividers + content + closing), and fill the **closing** slide's `closing-statement` + 3-column
   `closing-grid`.
7. **Verify** (below), then hand back the deck path and slide count.

## How the outline maps to slides

| Outline element | Becomes |
| --- | --- |
| `# <title>` + ` ```yaml ` block + leading `>` blockquote | the **cover** (`slide-cover`): eyebrow, `h1`, one-line claim, meta-row, `cover-diagram` |
| `## section N. <title>` | a **section divider** (`slide-chapter`): ghost numeral, eyebrow, title, one-line sub |
| `### slide N.M <title>` | one **content slide** — `topbar` (`Slide N.M` eyebrow + `h2.headline`, ~half wrapped in `.it`) over `body-area` |
| `-` / `*` / `1.` bullets | `ul.points > li.point` (default body); `**bold**`→`<b>`, `` `code` ``→`<code>`, warnings→`.warn` |
| A GitHub-style markdown table, or a `- table: …` directive | `table.ledger` (uppercase-cyan `th`, first col `td.tag`, coral cells `td.warn-cell`) |
| `- diagram: …` directive | a **built visual** in `.diagram-frame` + short `.diagram-caption` — CSS-block or SVG per §5, **never the directive text printed** |
| A ` ```text ` ASCII sketch in the outline | rebuild as a real CSS/SVG diagram — don't paste the ASCII |
| A single load-bearing claim | optionally a `.callout` instead of bullets |
| `[↑ Back to top]` links | dropped |

## Diagrams are the point — build them

A `diagram:` line (and any ` ```text ` ASCII sketch) in the outline is a **visual to build**, never
text to print or park in notes. Render it per FRONTEND-STYLE.md §5: **CSS block diagrams** for
boxes/stacks/grids/contrasts, **SVG** for anything with arrows, curves, or a cycle. Hold the colour
discipline — cyan = happy path, coral = the failure branch only, `--ink-faint` = neutral plumbing,
dashed = deferred / out-of-scope.

## Overflow discipline

The stage is a **fixed 1920×1080** at a back-of-room type scale — a slide holds only ~4 tight
bullets or a ~4–6 row table. **One `### slide` heading → exactly one slide.** If content won't fit,
**tighten the copy or split the outline slide — never shrink the type** below the spec's sizes. If a
split is genuinely needed, flag it rather than silently overflowing.

## Verify before handing back

- **Open the deck in a browser / preview** and page through it: no slide overflows the stage, nav
  (← → Space, arrows, progress bar) works, the cover and closing render.
- **Slide count** = cover + one per `## section` + one per `### slide` + closing; the `.chrome-page`
  `NN / TOTAL` matches and is sequential. Sanity-check against the outline's `### slide N.M` headings.
- **Self-contained:** unique `localStorage` key (`l<NN><II>-deck-content`), all CSS/JS/fonts inline,
  every `diagram:` rendered as a real visual (none left as printed text).

## Out of scope

- **No source edits.** This skill reads the `.md` outline and writes the `.html` deck; it never
  modifies the outline. Reshaping the outline is a normal materials edit
  (`generate-materials-from-roadmap`), not this skill.
- **No re-theming.** Changing tokens/type is a curriculum-wide change to FRONTEND-STYLE.md +
  `sample_deck.html` (spec's "To re-theme" note), not a per-deck edit.
- **No invented content.** Every slide's text comes from the outline; if the outline is thin, the
  fix is in the outline, not padding here.
