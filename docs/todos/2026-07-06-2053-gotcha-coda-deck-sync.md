# 2026-07-06 — Deck sync for the two gotcha-coda stragglers (L2205, L0505)

**Follow-up to** the gotcha carry-over effort
([2026-07-04-1531-gotcha-beat-materials-audit.md](2026-07-04-1531-gotcha-beat-materials-audit.md),
[2026-07-01-mini-cut-gotcha-antipattern-demos.md](2026-07-01-mini-cut-gotcha-antipattern-demos.md)).
The two remaining coda stragglers landed in the lecture **markdown** on branch
`worktree-gotcha-carryover` (markdown-only PR, by design — that's how every sibling coda landed).
Their **HTML decks are now stale** and need a rebuild pass. This note tracks that pass.

## What changed in the outlines (what the decks must catch up to)

- **`L2205_lecture.md` §3** — was a single slide 3.1 ("Three ways to put a capability in the wrong
  home", a 3-row table). Now two slides:
  - **3.1 "The description decides whether the skill loads"** — two description faults (too-vague /
    too-broad-or-colliding), promoted up from `L2202` §4.2. Diagram: two coral failure strips under
    one cyan healthy fire (mirrors `L2202` slide 4.2).
  - **3.2 "The container decides whether it should be a skill at all"** — two container faults
    (tool↔skill blur incl. the new **skill→tool** direction; skill↔system-prompt blur), the
    `cost follows placement` line, and the **L23 Demo 5** collision handoff. Diagram: the
    three-homes-row third beat (coral mis-placed chips + cyan relocation arrows).
  - Also: slide 1.1's motif cross-ref updated ("recurs in 1.2, **3.2**, and 5.1").
  - **No parallel conflict** — `L2205_lecture_deck.html` has no other in-flight edits.
- **`L0505_lecture.md`** — new **§4 "Three routing gotchas, named"** (slide 4.1: wrong-shape /
  brittle-branch / accidental-agency, a 3-row table + a three-coral-vignette diagram). The old
  §4 "Bridge to L11" became **§5** (slides 5.1/5.2); the slide-2.1 motif ref "2.3 and 4.2" became
  "2.3 and **5.2**".
  - **⚠️ Coordinate with in-flight work:** the main checkout had **uncommitted** L0505 edits at the
    time of this PR — a new **slide 2.4 "Loops aren't only for agents"** (retry / evaluator-optimizer
    back-edges) plus its own `L0505_lecture_deck.html` changes (+~94 lines) and a yaml
    `keywords`/`duration` bump. That work is independent of this coda (different section), but the
    **L0505 deck must be rebuilt from the merged outline** (coda §4 + renumbered §5 **and** slide
    2.4), not from either branch alone. Rebuild only after both land.

## Do this

Run the standard deck cycle from
[../handoffs/2026-07-06-lecture-html-deck-rollout.md](../handoffs/2026-07-06-lecture-html-deck-rollout.md)
(the `build-lecture-deck` skill → FRONTEND-STYLE.md → sample_deck.html), per deck:

- [ ] **L2205 deck** — rebuild §3 as two slides (3.1 description strips, 3.2 three-homes container
      row + handoff); renumber the deck's section/slide counters and the `NN / TOTAL` footer to
      match the added slide. Safe to do now (no conflict).
- [ ] **L0505 deck** — rebuild **after** main's slide-2.4 work lands, from the merged outline: add
      the §4 coda slide (three coral vignettes) and the renumbered §5 bridge. Reconcile with the
      slide-2.4 deck edits in the same pass.
- [ ] Browser-QA both per the handoff (overflow sweep, SVG `getBBox` bounds, classroom-scale type,
      unique localStorage key, sequential `NN / TOTAL`).

## Verify

Each deck: every `diagram:` directive rendered as a real CSS/SVG visual (never printed directive
text), no slide overflows the 1920×1080 stage, slide count = cover + one per `## section` + one per
`### slide` + closing, and the coda's colour discipline holds (coral = the fault, cyan = the cure).
