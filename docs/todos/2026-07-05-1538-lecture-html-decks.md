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

**Progress: 11 built (L0102, L0202, L0305, L0402, L0502, L0505, L0602, L0702, L0802, L0902, L0905) · 1 needs rescale (L1002) · 7 pending.**

| Lesson item | Deck? | Scale | Note |
| --- | --- | --- | --- |
| L0102 | ✅ | classroom | done + consistent with outline (13 diagrams built, 36 total) |
| L0202 | ✅ | classroom | done + consistent with outline (persona slide, 38 total) |
| L0305 | ✅ | classroom | done (was L0304; L03 renumbered for a new L0302 LangChain/LangGraph primer notebook; outline reshaped prose→slides, 4 diagrams, 12 slides) |
| L0402 | ✅ | classroom | done (7 diagrams incl. 2 added to §1; 3 ledger tables, 2 code blocks, 26 slides) |
| L0502 | ✅ | classroom | done (routing; 4 diagrams — 1 enhanced + 3 added to a diagram-starved outline; 1 code block, 15 slides) |
| L0505 | ✅ | classroom | done (workflow-vs-agent close; 3 diagrams incl. the back-edge money slide, 2 ledger tables, 15 slides) |
| L0602 | ✅ | classroom | done (reasoning; 6 diagrams — 3 added incl. self-critique + when-it-hurts; 2 ledger tables, 28 slides) |
| L0702 | ✅ | classroom | done (tool calling; 8 diagrams — 4 added incl. two-era lanes, bind_tools boundary, cost-twice, three-outcome fan; 6 ledger tables, 30 slides) |
| L0802 | ✅ | classroom | done (tool design; 7 diagrams — 2 added: worked-test flow + hidden-side-effect panels; 6 ledger tables, 37 slides) |
| L0902 | ✅ | classroom | done (MCP contract + boundary; 6 diagrams — 1 added: §5.2 break-even chart; 9 ledger tables, 32 slides) |
| L0905 | ✅ | classroom | done (MCP wire-shape walkthrough; 3 diagrams — 1 added: §4.1 boundary-failure timeline; 2 ledger tables, 16 slides) |
| L1002 | ⚠️ | **OLD** | **known off** — built pre-classroom-scale; needs the rescale below |
| L1102, L1105, L1206, L1307, L2202, L2205, L2302 | ❌ | — | no deck yet (7 outlines) |

## Open items

- **[known off] Rescale L1002 deck to the classroom type-scale.** It sits at the old sizes
  (`--edge-bottom: 90px`, bullets 25px, cells 21px, SVG labels 18–24px). Apply the same transform
  used on L02: shared-CSS type bump + reclaim vertical space (`--edge-bottom` 90→64, `body-area`
  top 322→312, `.point` margin 22→15, `td` padding 18→11), bump `.node-label`/`.edge-label` and any
  L10-specific diagram-helper classes + inline SVG `font-size="N"` attributes, then **verify no slide
  overflows** the stage (L10 has a 7-row arc table + several SVG diagrams — the dense ones to watch).
  L10's diagrams are hand-crafted and good; **hand-scale, don't regenerate** (preserves the art).
- **Build decks for the 7 remaining outlines.** Each via the `build-lecture-deck` skill (copy the
  sample, map the outline, build diagrams, verify). Rough priority: the rest of the core arc first
  (L11–L13), then the mini/standalone items (L22, L23). No hard dependency between
  them — can be done incrementally, one lesson at a time.
  - **First, review the outline's `diagram:` coverage** — an outline may under-specify diagrams on
    visual slides, and the deck is only as good as its directives. L01 needed 4 added (slides 1.3,
    2.1, 2.3, 6.1) before building; expect similar gaps elsewhere. Enhance the `.md` outline first
    (a normal materials edit), then build.

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
