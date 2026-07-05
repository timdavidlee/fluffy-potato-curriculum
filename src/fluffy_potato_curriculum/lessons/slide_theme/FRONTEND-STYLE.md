# Lecture deck frontend style — "Graph Canvas"

The shared visual system for the **HTML lecture decks** (`L<NN><II>_lecture_deck.html`) that
render a lesson's slide-outline as a browser presentation. Every deck uses this one system so the
curriculum reads as a single course, not a pile of one-off decks.

This folder is the theme's home:

- **`FRONTEND-STYLE.md`** (this file) — the spec: tokens, components, and authoring rules.
- **[`sample_deck.html`](sample_deck.html)** — a self-contained **generic** reference deck (cover,
  section divider, content slides showing points / callout / ledger table / CSS-block diagram / SVG
  flow, and a closing slide). It is the copy-from starting point and the living proof of the tokens
  below. Open it in a browser; copy it to start a new deck.

> This is the **HTML-deck** style. It is separate from the `build-lecture-deck` skill, which emits a
> plain, unstyled `.pptx` from the same `L<NN><II>_lecture.md` outline. The `.md` outline is the
> source of truth for *content* (sections, slides, bullets, tables, and `diagram:` directives); this
> doc governs how a hand-built or generated **HTML** deck should *look*.

**To re-theme the whole curriculum**, change the tokens in §2 here and in `sample_deck.html`, then
re-verify the sample renders — every deck copies from the sample, so they move together. Nothing in
this doc points at a specific lesson deck on purpose.

---

## 1. The fixed stage (non-negotiable)

Every deck is authored on a fixed **1920×1080** canvas that scales *as a whole unit* to the
viewport — it never reflows for small screens; it letterboxes/pillarboxes instead.

- `.deck-viewport` fills the window; `.deck-stage` is the 1920×1080 canvas, `transform-origin: 0 0`.
- A tiny controller scales the stage: `factor = min(innerWidth/1920, innerHeight/1080)`, then
  `translate(x, y) scale(factor)` centres it. (See `SlidePresentation.setupStageScale`.)
- Slide switching uses `.active` / `.visible` toggling **`visibility` + `opacity` + `pointer-events`**
  — never `display:none/block` (a later `display:flex` rule would reveal every slide at once).
- Author at the real 1920×1080 pixel sizes. Do **not** add responsive breakpoints to rearrange slide
  content. One `### slide N.M` heading → exactly one slide; if a slide overflows, tighten the copy or
  drop a bullet — do not shrink text below the sizes here.
- Include `@media (prefers-reduced-motion: reduce)`.
- Never negate a CSS function directly (`-clamp(...)` is silently dropped) — use `calc(-1 * ...)`.

---

## 2. Design tokens

All colour/type/spacing lives in `:root`. Do not hard-code hex values in slide markup — reference the
variables so a re-theme is one edit.

```css
:root {
    --stage-bg:   #05070a;   /* outside the slide */
    --slide-bg:   #0a0e13;   /* the slide surface */
    --cyan:       #52e8c8;   /* PRIMARY accent — happy path, highlights, headings' .it */
    --cyan-dim:   #1f6f60;
    --cyan-faint: rgba(82,232,200,0.16);
    --cyan-rule:  rgba(82,232,200,0.22);  /* hairline rules */
    --coral:      #ff6b57;   /* SECONDARY — failure / warning / the "error" path only */
    --coral-dim:  #7a3229;
    --ink:        #eef2f0;   /* primary text */
    --ink-dim:    #8a9490;   /* body / secondary text */
    --ink-faint:  #4c5652;   /* neutral edges, page numbers, ghosts */

    --font-display: 'Fraunces', Georgia, serif;        /* headings, cover, chapter, callouts */
    --font-body:    'IBM Plex Mono', ui-monospace, monospace;  /* everything else */

    --edge-x: 130px;         /* left/right content margin */
    --edge-top: 96px;
    --edge-bottom: 90px;
    --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
    --duration-normal: 0.7s;
}
```

Fonts load from Google Fonts (`Fraunces` italic+opsz+weight axes, `IBM Plex Mono` 400–700). Keep the
same two families — **Fraunces (display serif) + IBM Plex Mono (body/mono)** is the signature.

**Colour discipline (this is what keeps diagrams legible):**
`--cyan` = normal / happy path / "this is the point." `--coral` = failure, warning, the error branch,
the thing to avoid. `--ink-faint` = neutral/plumbing edges. Never use coral decoratively — a coral
arrow *means* "this path is the failure."

### The permanent canvas

The stage carries a dot-grid + two corner glows via `.deck-stage` background and `::before`, so every
(transparent) slide floats on the same atmosphere:

```css
.deck-stage {
    background:
        radial-gradient(ellipse 900px 700px at 82% 12%, rgba(82,232,200,0.10) 0%, transparent 60%),
        radial-gradient(ellipse 900px 700px at 10% 92%, rgba(255,107,87,0.07) 0%, transparent 60%),
        var(--slide-bg);
}
.deck-stage::before {          /* dot grid */
    content: ""; position: absolute; inset: 0; z-index: 0;
    background-image: radial-gradient(rgba(82,232,200,0.14) 1.4px, transparent 1.4px);
    background-size: 64px 64px;
}
```

---

## 3. Slide types

Four kinds of slide, each a `<section class="slide …">`. The first slide adds `active`.

| Type | Class | Use |
| --- | --- | --- |
| Cover | `slide-cover` | one per deck — eyebrow, big Fraunces `h1`, one-line claim, meta-row, a `cover-diagram` SVG |
| Section divider | `slide-chapter` | one per `## section N.` — giant ghost numeral, `chapter-eyebrow`, `chapter-title`, one-line `chapter-sub` |
| Content | *(none)* | one per `### slide N.M` — `topbar` (eyebrow + headline) over a `body-area` |
| Closing | `slide-closing` | one per deck — a Fraunces italic `closing-statement` + a 3-column `closing-grid` |

**Content slide skeleton:**

```html
<section class="slide">
    <div class="chrome-tag">L&lt;NN&gt; &middot; <b>TOPIC</b></div>
    <div class="topbar reveal">
        <div class="eyebrow">Slide 1.1</div>
        <h2 class="headline">A representative <span class="it">headline</span></h2>
    </div>
    <div class="body-area">
        <!-- one of: ul.points / table.ledger / diagram-frame+diagram-caption -->
    </div>
    <div class="chrome-page">03 / NN</div>
    <div class="chrome-nav">← → navigate</div>
</section>
```

`h2.headline .it` = italic cyan — wrap ~half the title in it. Chapter titles put their second half in
**cyan, non-italic** (`<span style="color:var(--cyan);font-style:normal;">…</span>`).

---

## 4. Content components

- **`ul.points > li.point`** — the default body. Cyan ring bullet, 25px. Emphasis: `<b>`/`.k` = ink,
  `<code>` = cyan-on-faint inline code, `.warn` = coral. Keep to ~4 tight points; reading-first, but
  never overflow.
- **`.callout`** — one emphasis sentence, cyan left-border, Fraunces italic 32px. Use for a slide's
  single load-bearing claim.
- **`table.ledger`** — for any markdown table or `table:` directive. Uppercase-cyan `th`, 21px `td`,
  first column `td.tag` (cyan, `nowrap`). `td.warn-cell` for coral cells.
- **`.diagram-frame` + `.diagram-caption`** — for any `diagram:` directive. See §5.

Reveal animation: add `reveal` to top-level blocks for a staggered fade-and-rise on slide entry;
`ul.points.reveal` staggers its own `.point` children. Don't put `reveal` on tiny chrome.

---

## 5. Diagrams — "show, not tell"

A `diagram:` directive in the outline is a *visual to build*, never text to print. Render it inside a
`.diagram-frame` with a short `.diagram-caption`. Two techniques (both shown in `sample_deck.html`):

- **CSS block diagrams** (preferred for boxes/stacks/grids) — plain `<div>`s with the box style below.
  More robust than hand-plotted SVG; use for nested boxes, two-up contrasts, pill lists, stacked
  message blocks, bipartite lists.
- **SVG** (for anything with arrows, curves, or a cycle) — `<circle>` nodes, `<path>` edges with
  `marker-end` arrowheads, `class="node-label"` (`--font-body`, 600, 24px, `fill:var(--ink)`) and
  `class="edge-label"` (`--font-body`, 18px). Animate a flow with a `<circle>` + `<animateMotion>`
  along the edge path. Define arrowhead `<marker>`s in `<defs>` (one cyan, one coral).

**Box vocabulary:**

```css
/* a normal node */          border: 2px solid var(--cyan);      border-radius: 10px;
                             background: #12181a; padding: 22px 26px;
/* a failure/warning node */ border-color: var(--coral);
/* a "not yet / ghost" node */ border-style: dashed; border-color: var(--ink-faint); background: transparent;
```

Rules of thumb: cyan node/edge = normal path; coral node/edge = the failure branch; `--ink-faint`
edges = neutral plumbing; dashed = deferred / out-of-scope ("this lands in a later lesson"). Append
any small helper classes you need to the end of the `<style>` block — don't edit the shared rules
above them.

---

## 6. Chrome, navigation, and inline editing

- **Chrome** on every slide: `.chrome-tag` (top-left, `L<NN> · <b>TOPIC</b>`), `.chrome-page`
  (bottom-right, `NN / TOTAL` — number every slide in order, cover = `01`), `.chrome-nav`
  (bottom-left hint on content slides).
- **Outside the stage** (kept out of `.deck-stage` per the fixed-stage rules): `.deck-progress` bar,
  `.deck-arrow.prev/.next` buttons, and the inline-edit controls (`edit-hotzone`, `edit-toggle`,
  `save-toast`).
- **`SlidePresentation`** (JS) wires keyboard (← → Space PageUp/Down Home End), touch-swipe, wheel,
  the arrow buttons, and the progress bar. Copy verbatim.
- **`InlineEditor`** (JS) — hover the top-left hotzone or press **E** to toggle edit mode, click any
  text to edit, **Ctrl/Cmd+S** to save to `localStorage`. Copy verbatim **but give each deck its own
  storage key** (`save()` + `restore()`): the sample uses `slide-theme-sample`; a real deck should use
  `l<NN><II>-deck-content`. If two decks share a key they clobber each other's saved edits.

---

## 7. Per-deck checklist

Start a new deck by copying [`sample_deck.html`](sample_deck.html), then change only:

1. `<title>` and the `.chrome-tag` topic label.
2. The cover (eyebrow, `h1`, claim, meta-row, `cover-diagram`).
3. Every slide's content + the `.chrome-page` `NN / TOTAL` (total = cover + dividers + content + closing).
4. The `InlineEditor` `localStorage` key.
5. The closing `closing-grid` columns.

Everything else — tokens, canvas, type primitives, components, nav JS — stays byte-for-byte identical
so the decks stay a set.

**`.pptx` decks are build artifacts (gitignored); the HTML decks are committed source.** Keep the deck
self-contained (all CSS/JS inline, fonts from Google Fonts) so a single file opens anywhere.
