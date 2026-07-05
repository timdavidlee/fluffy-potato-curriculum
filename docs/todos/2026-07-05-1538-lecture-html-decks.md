# 2026-07-05 — Lecture → HTML deck rollout ("Graph Canvas")

Tracking the effort to give each `L<NN><II>_lecture.md` slide-outline a themed **HTML deck**
(`L<NN><II>_lecture_deck.html`) in the shared **"Graph Canvas"** system.

**Build path is now a skill.** [`build-lecture-deck`](../../.claude/skills/build-lecture-deck/SKILL.md)
generates a deck by **copying [`slide_theme/sample_deck.html`](../../src/fluffy_potato_curriculum/lessons/slide_theme/sample_deck.html)**
and mapping the outline onto it, building every `diagram:` directive as a real CSS/SVG visual per
[`slide_theme/FRONTEND-STYLE.md`](../../src/fluffy_potato_curriculum/lessons/slide_theme/FRONTEND-STYLE.md).
(The old python-pptx `build_deck.py` was retired in `25a76e5`.) HTML decks are **committed source**.

**Theme is at a classroom type-scale** (25–40 seat room, back-of-row legible): bullets 29px, table
cells 24px, captions 25px, headlines 62px, `--edge-bottom: 64px`. Any deck must match — this is the
recurring drift risk below.

## Status (19 lecture outlines)

| Lesson item | Deck? | Scale | Note |
| --- | --- | --- | --- |
| L0202 | ✅ | classroom | done + consistent with outline (persona slide, 38 total) |
| L1002 | ⚠️ | **OLD** | **known off** — built pre-classroom-scale; needs the rescale below |
| L0102, L0304, L0402, L0502, L0505, L0602, L0702, L0802, L0902, L0905, L1102, L1105, L1206, L1307, L2202, L2205, L2302 | ❌ | — | no deck yet (17 outlines) |

## Open items

- **[known off] Rescale L1002 deck to the classroom type-scale.** It sits at the old sizes
  (`--edge-bottom: 90px`, bullets 25px, cells 21px, SVG labels 18–24px). Apply the same transform
  used on L02: shared-CSS type bump + reclaim vertical space (`--edge-bottom` 90→64, `body-area`
  top 322→312, `.point` margin 22→15, `td` padding 18→11), bump `.node-label`/`.edge-label` and any
  L10-specific diagram-helper classes + inline SVG `font-size="N"` attributes, then **verify no slide
  overflows** the stage (L10 has a 7-row arc table + several SVG diagrams — the dense ones to watch).
  L10's diagrams are hand-crafted and good; **hand-scale, don't regenerate** (preserves the art).
- **Build decks for the 17 remaining outlines.** Each via the `build-lecture-deck` skill (copy the
  sample, map the outline, build diagrams, verify). Rough priority: the built-out core arc first
  (L01, L03–L09, L11–L13), then the mini/standalone items (L22, L23). No hard dependency between
  them — can be done incrementally, one lesson at a time.

## Verify (per deck, before committing)

- Open in a browser / preview; page through: **no slide overflows** the 1920×1080 stage; nav
  (← → Space, arrows, progress bar) works; cover + closing render.
- **Slide count** = cover + one per `## section` + one per `### slide` + closing; `.chrome-page`
  `NN / TOTAL` sequential and matches the outline's `### slide N.M` headings.
- Self-contained: unique `localStorage` key `l<NN><II>-deck-content`; all CSS/JS/fonts inline; every
  `diagram:` rendered as a real visual (none left as printed text).
- Type matches the theme (spot-check `--edge-bottom: 64px`, bullets 29px) so it doesn't drift back to
  the old scale — the L10 lesson learned here.

## Notes / risks

- **Theme drift is the main hazard.** A re-theme (tokens/type) is a curriculum-wide change to
  `FRONTEND-STYLE.md` + `sample_deck.html` (+ every existing deck), not a per-deck edit. When the
  theme moves, existing decks must be re-swept — exactly why L10 is currently off.
- If this grows past a couple of sessions, graduate it to a `handoffs/` spec.
