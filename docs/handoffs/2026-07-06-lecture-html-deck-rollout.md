# Handoff: Lecture → HTML deck rollout ("Graph Canvas")

**Status: DONE (2026-07-06).** All 19 lecture outlines now have decks — the last five (L1206,
L1307, L2202, L2205, L2302) landed in `3b3b82c` ("build the last 5 lecture decks, closing the
rollout"), each preceded by a diagram-coverage densify of its outline (see
[2026-07-06-1853-diagram-review-remaining-outlines.md](../todos/2026-07-06-1853-diagram-review-remaining-outlines.md)).
The tracking todo [2026-07-05-1538-lecture-html-decks.md](../todos/2026-07-05-1538-lecture-html-decks.md)
has the full 19-row status table. **The per-lesson cycle below is kept as durable reference** — a
future theme change (see "theme drift" in the tracking todo) would re-run it across every deck.
The earlier `l01-deck` worktree loose-end is gone (no longer in `git worktree list`).

Give every `L<NN><II>_lecture.md` slide-outline a themed HTML deck
(`L<NN><II>_lecture_deck.html`) in the shared **"Graph Canvas"** system. This handoff is the *how*,
written so a cold session can run any lesson end-to-end.

## Process reference (how to build/rebuild a deck)

One process note from the L11 run: the background deck-builder subagents repeatedly stalled trying
to emit the whole deck in one giant Write — brief them to build the file **incrementally** (head/CSS
+ cover first, then append 3–5 slides per Edit), which got both decks out cleanly. Port allocation
so far: L09 → 8132, L11 → 8133, next lesson takes 8134, …

## The per-lesson cycle (repeat verbatim)

1. **Review the outline's `diagram:` coverage** (`src/.../lessons/L<NN>/L<NN><II>_lecture.md`).
   Look for load-bearing slides with bullets only, and whole sections with zero diagrams. Add
   `- diagram: …` directives (one-line visual descriptions, colour intent included — cyan happy /
   coral failure / ink-faint neutral / dashed deferred). Typical add: 1–4 per outline. Edit on main
   is fine — you'll move it in step 3.
2. **`EnterWorktree`** (name `l<NN>-deck(s)`). It branches fresh from origin/main, so:
3. **Move the outline edits in**: `cp` the edited outline(s) from main into the worktree, then
   `git -C <main> restore <outline>` so main stays clean and outline+deck land in one PR.
4. **Delegate the build to a background subagent** (general-purpose, `run_in_background`), one per
   deck — two decks (an L05/L09-style lesson) run in parallel. The prompt must include, with
   absolute worktree paths: read the `build-lecture-deck` skill → FRONTEND-STYLE.md →
   sample_deck.html → the outline; output path; chrome (`.chrome-tag`, unique localStorage key
   `l<NN><II>-deck-content`); slide-count math (cover + one per `## section` + one per `### slide` +
   closing — but tell the agent to count the headings itself; **the outline wins** over your count);
   the colour discipline; and the two hard-won warnings:
   - **SVG text sizing:** theme classes `.node-label` (27px) / `.edge-label` (20px) **override**
     inline `font-size` attributes (stylesheet beats presentation attribute). Budget IBM Plex Mono
     ≈ 16.2px/char at 27px, ≈ 12px/char at 20px, ≥16px padding per side, and demand the width math
     for the tightest labels in the report.
   - **No git, no launch.json edits, don't touch the other agent's deck.** (The L07 builder edited
     main's launch.json and deleted the worktree's — brief explicitly against it since.)
5. **Launch config**: while the build runs, add the committed relative `static-preview-l<NN>` entry
   to the **worktree's** `.claude/launch.json` (next port: L09 took 8132 → L11 gets 8133, …).
6. **QA in a real browser** (the preview tool reads **main's** launch.json, not the worktree's):
   append a temp `static-preview-l<NN>-worktree` entry with an **absolute path into the worktree**
   to main's launch.json, `preview_start` it, navigate to the deck, then:
   - **Sweep** every slide with `preview_eval`: (a) HTML overflow — any descendant's
     `getBoundingClientRect()` bottom/right beyond its slide's rect; (b) SVG text vs `viewBox`
     bounds via `getBBox()` — **skip `transform`ed text** (getBBox ignores transforms → false
     positives) and treat text-in-rect heuristics as *leads*, not verdicts (tall unrelated rects
     false-positive; L08 threw 14 phantoms).
   - **Spot-check screenshots**: cover, closing, every new-diagram slide, densest tables. The
     reveal animation races the screenshot after rapid keydowns — if a slide screenshots empty,
     run any trivial `preview_eval` and re-shoot.
   - Nav quirk: dispatch keydowns on `document.body` (the handler reads
     `e.target.getAttribute`, which `document` lacks). `Home`/`End` jump to cover/closing.
   - Fix issues by editing the deck file (widen rects / shorten labels — never shrink type), clear
     the deck's localStorage key, reload, re-sweep.
7. **Clean up QA config**: `preview_stop`, then revert main's launch.json (see loose-ends caveat).
8. **Tick the rollout todo** *in the worktree*: bump the built count, add the ✅ row (with a short
   note: what was added, diagram/table/slide counts), shrink the pending row + the "Build decks for
   the N remaining" open item.
9. **`pr-push-and-merge`** (the skill): commit all (`feat(L<NN>): build lecture HTML deck + add …
   diagrams`, one-line, with the `Co-Authored-By: Claude Opus 4.8 (1M context)` trailer), push, PR,
   `gh pr merge --squash --delete-branch`. **Known failure:** the merge command exits 1 with
   `fatal: 'main' is already used by worktree…` — the GitHub-side merge still succeeds. Verify with
   `gh pr view <n> --json state,mergeCommit`, then manually `git push origin --delete <branch>`.
   Wait for CI's bump run on the merge SHA (`gh run list --workflow=bump.yml` → `gh run watch`),
   then `git -C <main> pull --ff-only --tags`. Finish: `ExitWorktree` (action remove — needs
   `discard_changes: true` after a squash-merge), `git fetch --prune && git worktree prune`.

## Verify (per deck, before committing)

The todo's "Verify" section is authoritative; the short list: no slide overflows the 1920×1080
stage; slide count = cover + dividers + content + closing with sequential `NN / TOTAL`; unique
localStorage key; every `diagram:` a real visual (never printed directive text); type at classroom
scale (`--edge-bottom: 64px`, 29px bullets — don't drift back to the old L10 sizes).

## Key files

- Skill: `.claude/skills/build-lecture-deck/SKILL.md`
- Theme spec + copy-from: `src/fluffy_potato_curriculum/lessons/slide_theme/FRONTEND-STYLE.md`,
  `…/slide_theme/sample_deck.html`
- Outline format: `docs/origin/LECTURES.md`
- Tracking: `docs/todos/2026-07-05-1538-lecture-html-decks.md`
