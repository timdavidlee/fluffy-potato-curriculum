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

**Progress: 19 built — all outlines have decks as of 2026-07-06.**

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
| L1002 | ✅ | classroom | done 2026-07-06 — rescaled to classroom type-scale (hand-scaled, art preserved) + rebuilt to the densified outline (+9 visuals incl. the cyan back-edge fixes; 30 slides) |
| L1102 | ✅ | classroom | done (loop→graph; 6 diagrams — 4 added: L10 loop recap, back-edge-on-the-DAG, numbered run trace, step-cap-at-25; 1 mapping table, 16 slides) |
| L1105 | ✅ | classroom | done (config surface + ceiling; 5 diagrams — 3 added: managed-by-create_agent bracket, outgrow break-out arrows, L10→L15 ladder; 3 tables, 14 slides) |
| L1206 | ✅ | classroom | done 2026-07-06 (Langfuse export + data-plane close; outline densified 4→12 diagrams first — see the [remaining-outlines review](2026-07-06-1853-diagram-review-remaining-outlines.md); pipe + fan motifs; 21 slides) |
| L1307 | ✅ | classroom | done 2026-07-06 (eval-ratchet closer; densified 2→7; cribs L04 chain / L10 cycle / L11 bracket; outline 4.1 split into two slides at build (flagged, content intact); 14 slides) |
| L2202 | ✅ | classroom | done 2026-07-06 (skills/progressive disclosure; densified 4→11; window-column + SKILL.md-card motifs, 3.2 money chart; 19 slides) |
| L2205 | ✅ | classroom | done 2026-07-06 (placement capstone; densified 2→9; three-homes motif, cribs L2202 card + L11 bracket; 16 slides) |
| L2302 | ✅ | classroom | done 2026-07-06 (skill archetypes; densified 3→12; center-of-gravity triangle spine, cribs L22 strip + L01 window bar; 21 slides) |

## Open items

- ~~**[drift] The 2026-07-06 diagram-coverage reviews densified all built outlines**~~ —
  **resolved 2026-07-06, both rebuild passes landed.** The eight L01–L07 decks were rebuilt to
  their densified outlines (merged in `c6571ad`; see
  [2026-07-06-1408-diagram-review-l01-l07.md](2026-07-06-1408-diagram-review-l01-l07.md)), and the
  six L08–L11 decks (L0802 +8 visuals, L0902 +9, L0905 +6, L1002 +9, L1102 +4, L1105 +3) were
  rebuilt and browser-verified in this pass (stage-overflow + chrome-collision sweeps, slide counts
  vs outlines, classroom type-scale; see
  [2026-07-06-1439-diagram-review-l08-l11.md](2026-07-06-1439-diagram-review-l08-l11.md)). Every
  ✅ row above now matches its densified outline, though row diagram-counts predate the rebuilds.
- ~~**[known off] Rescale L1002 deck to the classroom type-scale.**~~ **Done 2026-07-06** in the
  L08–L11 rebuild: same transform as L02 (`--edge-bottom` 90→64, type bump, spacing reclaim),
  diagrams hand-scaled (art preserved), no slide overflows the stage.
- ~~**Build decks for the 5 remaining outlines.**~~ **Done 2026-07-06** — all five (L1206, L1307,
  L2202, L2205, L2302) built via `build-lecture-deck` in one pass, core arc first, each preceded by
  a diagram-coverage densify of its outline (36 directives added, 15 reworded; see
  [2026-07-06-1853-diagram-review-remaining-outlines.md](2026-07-06-1853-diagram-review-remaining-outlines.md)).
  Browser-verified per the checklist below (per-slide stage-overflow sweep clean, nav OK, sequential
  numbering, classroom type-scale spot-checked, no directive text printed). One structural flag:
  L1307's outline slide 4.1 (table + multi-part diagram) required a two-slide split at build
  ("Slide 4.1" / "Slide 4.1 · continued") — content intact.

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
