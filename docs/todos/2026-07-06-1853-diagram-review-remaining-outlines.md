# Diagram-coverage review — the 5 unbuilt outlines (L1206, L1307, L2202, L2205, L2302)

Point-in-time review (2026-07-06) of the five lecture outlines that still lack decks (per the
[deck rollout todo](2026-07-05-1538-lecture-html-decks.md)) against the diagram guidance in
[LECTURES.md](../origin/LECTURES.md) and
[FRONTEND-STYLE.md](../../src/fluffy_potato_curriculum/lessons/slide_theme/FRONTEND-STYLE.md) §5 —
the same bar and method as the two prior passes
([L01–L07](2026-07-06-1408-diagram-review-l01-l07.md),
[L08–L11](2026-07-06-1439-diagram-review-l08-l11.md)): five parallel per-outline review agents;
findings verbatim-condensed.

Checked boxes were applied to the five outlines in the same session (**36 `diagram:` directives
added, 15 reworded** for colour intent / motif declaration). Unlike the prior passes there were no
deck colour bugs to sweep — these five have no decks yet; the builds follow in the same session.

## Cross-cutting patterns (third pass, same story)

1. **Colour intent still absent from pre-existing directives** — the 15 pre-existing directives
   nearly all needed colour encoding; several were latent L0505-bugs (coral on a happy path) or
   pseudocode-prints (the L01-8.1 class, e.g. L1206 3.1).
2. **Every lesson had its motif already on the page, used once**: L1206 the source→pipe→dashboard
   export fan; L1307 the eval ratchet; L2202 the context-window column; L2205 the three-homes row;
   L2302 the center-of-gravity triangle. Each now recurs 3+ beats.
3. **Cost claims without charts** again: L2202 3.2 (the roadmap's own "money slide" was
   table-only), L2205 5.1, L1307 1.2's asymmetric-cost bar pair.
4. **Bridge slides now re-draw the earlier lesson's picture** (the established cross-lesson rule):
   L1307 2.1 re-draws the L04 chain and 2.2 the L10 cycle + L11 bracket; L2202 2.3 the L08 MCP
   envelope and 5.2 the L11 bracket; L2302 1.1 L22's placement strip and 3.2 the L01 context-window
   bar; L2205 4.1 the L11 bracket + L2202's SKILL.md card.

## L12 — `L1206_lecture.md` (was 4/13 → now 12/13; two motifs existed, each used exactly once)

- [x] 1.1 hand-built artifact — `TraceEvent` pill-stack, shared `trace_id` as one cyan thread; ink-faint `.jsonl` chip. Motif debut, re-shown 3.1.
- [x] 3.2 two ways in — the 1.2 pipe split into two lanes reconverging: SDK lane cyan (the demo's route), OTLP solid ink-faint (*not* dashed — available now, just dimmer); no coral, neither lane fails.
- [x] 4.1 locate a failure — mock waterfall, ink-faint latency bars, one coral error badge (the deck's only earned coral until 6.3), cyan filter→expand path.
- [x] 4.2 compare two runs — 4.1's waterfall two-up + paired token bars; the one real change cyan (signal), small deltas ink-faint (noise); no coral — a difference is not a failure.
- [x] 5.1 additive, never a gate — the pipe split at the source: `.to_jsonl()` leg solid cyan "objectives 1–4 — already done", export leg dashed ink-faint.
- [x] 5.2 one observability home — the 1.2 fan as bookend: today's trace solid cyan, L11 LangGraph trace dashed ink-faint, "datasets/experiments → L13" dashed chip.
- [x] 2.2 three names, one structure — `TraceEvent` card, `run_type` row lit cyan forking to GENERATION/SPAN chips; three ink-faint vendor name-tags at the same card.
- [x] 6.3 cross the streams — 6.1's fan broken twice, two-up (persist arrow missing → coral "TTL expired"; persist bent into Langfuse → coral struck serve/join/backup chips); intact cyan fan small beneath. The L1105-3.3 "both mis-placements" shape.
- [x] Directive fixes: 1.2 (export arrow cyan; **pipe declared the lesson motif** for 3.2/5.1/5.2), 3.1 (pseudocode-print → one-to-one pill→observation mapping, code demoted to a chip), 6.1 (both arrows cyan *on purpose*; **fan declared the §6 motif**), 6.2 (snippet lines pinned as code chips on 6.1's arrows; datastore internals dashed "→ L20/L21").
- [x] **Stale-order prose fixed in the same session:** 5.2's "returns in **L11**" predated the 2026-07-04 reorder (L11 now precedes L12) — reworded to "the LangGraph agent you built in L11 can land its auto-emitted trace here". The roadmap's own `demos_or_activities.md:229` has the same stale phrasing (filed as a follow-up, not this branch).
- 2.1 left table-only deliberately — the 7-row vocabulary table *is* the visual and already exceeds the classroom table budget; split 2.1 rather than shrink type if it overflows at build.

## L13 — `L1307_lecture.md` (was 2/7 → now 7/7; the ratchet is the closer's motif, both bridges re-draw earlier pictures)

- [x] 1.2 ratchet vs one-time test — ink-faint static unit-test check vs the 1.1 ratchet turning across change 1→2→3, coral slip-back arrow caught by the cyan pawl; asymmetric-cost bar pair (short cyan "write the case" vs tall coral "rediscover in production"). Motif beat two.
- [x] 2.1 L04 bridge — the L04 acyclic chain exactly as L04's deck renders it (all cyan, no back-edge), cyan dataset chip feeding entry, checkmarks off END; explicitly no coral.
- [x] 3.1 first pass on purpose — scope fence beside the table: solid cyan "L13 — first pass" box, dashed ink-faint ghost chips "→ at-scale eval lesson". Lower priority; the designated drop if the slide overflows.
- [x] 3.2 tooling forward pointer — dashed ink-faint `common/evals.py` sketch beneath a cyan Langfuse layer, cyan tie-lines pairing `EvalCase`↔dataset item, `EvalResult`↔score, run↔experiment (the L1002-5.1 tie-line move).
- [x] 4.1 five anti-patterns — five coral chips under two cyan-bracket families ("eval design starts in the trace" / "don't trust one number"), cyan cure tags; chip #5 carries a pawl-less ratchet glyph (motif beat three).
- [x] Directive fixes: 1.1 ratchet had no colour intent (slip-back arrow a latent L0505 bug — now wheel/pawl cyan, coral only the caught slip-back; **motif declared**); 2.2 rewritten as the course's own pictures — L10 cycle (cyan back-edge) vs L11 `create_agent` bracket over one shared `l13-agent-evals` dataset chip, run grid with exactly one coral pass→fail cell.
- Build notes: crib the L04/L10/L11 shapes from the `L0402`/`L1002`/`L1102` decks rather than re-inventing; 2.2's one coral cell should be captioned as "what the comparison *would* flag", not as a fact about L11's agent.

## L22 — `L2202_lecture.md` (was 4/12 → now 11/12; the window column is the lesson's motif and appeared only once)

- [x] 1.2 the relief valve — window beat two: 1.1's column slimmed — ten cyan one-line catalog entries, one body arriving from the disk shelf, nine bodies dashed ink-faint (dormant, not failed); explicitly no coral — this is the fix.
- [x] 3.2 the payoff in tokens — the roadmap's money slide, table-only before. Bar chart: "10 tools" a coral stack of fat schema segments vs "10 skills" thin cyan description slivers + one body segment on the call that loaded it; the chart the demo's `rough_tokens` numbers land on.
- [x] 3.3 cheap, not free — third chart beat: the skills bar at 30 skills, top slivers turning coral (the catalog itself becoming bloat), coral chips "extra turn to load" / "needed skill never fired".
- [x] 2.1 called vs read vs always-seen — three verbs around one window column: tool chip + prompt block welded in (ink-faint), skill card outside on the shelf with a dashed read-on-demand arrow (cyan lane); no coral.
- [x] 2.3 MCP aside — re-draws L08's 9.1 bridge: spec card unchanged in a dashed ink-faint MCP envelope; 2.2's cyan skill card beside it (orthogonal axes).
- [x] 4.2 JIT failure modes — three coral failure strips under one cyan reference strip (4.1's healthy fire): body never arrives / body loading every turn with savings struck / coral "?" at context the agent no longer has.
- [x] 5.2 bridge — the L11 `create_agent(...)` bracket re-drawn: loop unchanged, cyan `load_skill` tool chip + cyan catalog-as-system-prompt chip the only new parts, dashed arrow to a `SKILL.md` card "the real thing — L2205".
- [x] Directive fixes: 1.1 (needed schema cyan, unused schemas/prompt coral "paid for, unused"; **window motif declared**), 2.2 (skill-card motif debut — name+description bands cyan, body neutral, scripts dashed), 3.1 (concentric rings → the 2.2 card as a three-step disclosure ladder with a rising token-cost meter — motif reuse over a one-off shape), 4.1 (cyan-discriminating vs coral-vague panels; seeds 4.2).
- 5.1 (vocabulary table) left diagram-less deliberately; if sparse at build, a miniature triptych of the three motifs fits without new vocabulary.

## L22 — `L2205_lecture.md` (was 2/9 → now 9/9; decision capstone had no picture of the decision)

- [x] 1.1 the heuristic — **motif debut: the three-homes row** — capability chip forking to tool box ("called") / system-prompt band ("always seen") / skill card ("read on demand"), edges labeled with the table's discriminators; all cyan — no home is a failure; recurs 1.2/3.1/5.1.
- [x] 1.2 four capabilities classified — the same row, Demo 4's four chips landed in their homes; all cyan, coral reserved for §3.
- [x] 2.2 push work into a script — 2.1 extended: coral struck-through prose-token-arithmetic path vs cyan `refund_amount.py` path; script chip dashed until invoked (echoes L2202's progressive disclosure).
- [x] 3.1 three anti-patterns — third motif beat: three coral chips sitting in the *wrong* home, cyan relocation arrows to the right one; homes stay cyan; caption "cost follows placement".
- [x] 4.2 meta-punchline — the course-spine ladder: three "you built → the product" rungs (L12 trace→Langfuse, L11 loop→LangGraph, `load_skill`+catalog→Agent Skills); earlier rungs ink-dim, today's rung cyan.
- [x] 5.1 closer — motif bookend: the three-homes row with a context-cost bar under each (prompt/schema full-width ink-faint always-on; skill a thin cyan sliver + dashed body that pops in on load). L2202's stuffed-window opener, now solved.
- [x] 5.2 what's next — cyan "you are here" L22 node → dashed L23 / L50 chips; L24/L19/L09 ink-faint dashed ghosts; explicitly nothing coral. If it overflows, shrink the ghosts to labeled chips.
- [x] Directive fixes: 2.1 (skill card cyan = the orchestration point, tool boxes ink-faint L07/L08 plumbing, explicit no-coral), 4.1 (left side the L1102 bracket, right side **L2202's four-band `SKILL.md` card** for sibling consistency; both cyan, cyan `=`).
- Cross-checked against the parallel L2202 pass: the four-band card and stuffed-window shapes both survived there — the handshake holds; build L2202's deck first and crib.

## L23 — `L2302_lecture.md` (was 3/14 → now 12/14; the center-of-gravity triangle is now the deck's spine)

- [x] 1.2 triangle **motif debut** (reworded) — ink-faint edges, cyan archetype chips, resource-centric chip dashed ("the aside — §3"); recurrence plan declared (1.3, insets on 2.1–2.3/3.1, bookend 5.2).
- [x] 1.3 why classify first — the three mis-classifications as coral dots at the *wrong* corners with symptom tags, cyan arrows relocating each.
- [x] 2.1 script-centric (reworded) — thin wrapper ink-faint, fat `get_order_api.py` box cyan (the center of gravity); mini triangle inset, `scripts` corner lit.
- [x] 2.2 principle-centric — cyan rule-list card against an ink-faint work artifact via judgment arrows; triangle inset; explicitly no coral.
- [x] 2.3 procedure-centric — cyan numbered-step flow (decision diamond, "done when…" terminator) delegating sideways to an ink-faint script chip ("the 2.1 shape, borrowed").
- [x] 3.1 resource-centric — fourth triangle beat: `resources` corner cyan, archetype chip dashed (aside, not authored today); facts card fitting whole inside an ink-faint window bar.
- [x] 3.2 skill-vs-RAG — the L01 segmented context-window bar re-shown: glossary chip fits cyan, document corpus spills past the bar coral, dashed `RAG` box "L21 — full course".
- [x] 4.1 same format, different body — three `SKILL.md` cards, identical ink-faint frontmatter bands, three differently-shaped cyan bodies miniaturizing 2.1/2.2/2.3.
- [x] 4.2 descriptions across a set — registry strip of distinct cyan description pills; dashed preview of two overlapping pills, coral confined to the overlap, "→ L2305".
- [x] 4.3 wrong-shape panels (reworded) — both panels explicitly **coral** (both are the failure — the L0505 guard), each with a small cyan cure chip.
- [x] 5.2 closer — triangle bookend: a real skill as an *interior* dot, strong cyan pull to its primary corner, ink-faint pulls to the other two ("borrows as needed"); dashed onward chip "L2303 lab → L2304/L2305".
- [x] 1.1 recap bridge — L22's placement strip re-drawn, the skill card the only cyan element.
- 2.4 and 5.1 left table-only deliberately (4- and 5-row ledgers at the stage floor).
- The composition visuals in L2304/L2305 are `.ipynb` — outside this pass, same status as the notebooks note in both prior reviews.

## Order of attack for the builds (same session)

1. **Wave 1 — L1206, L1307, L2202** (core arc first per the rollout todo; L2202 leads L22 so its
   motif renderings exist to crib from).
2. **Wave 2 — L2205, L2302** (both re-draw L2202 pictures: the four-band card / placement strip —
   build after L2202's deck exists).
