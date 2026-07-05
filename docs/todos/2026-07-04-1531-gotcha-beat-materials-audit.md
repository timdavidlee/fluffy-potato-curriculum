# 2026-07-04 — Audit: gotcha/anti-pattern roadmap beats vs. existing materials

**Status: DONE (2026-07-04) — all 11 lessons audited; gap-ordered carry-over rolled up in the
[Output](#output) section below.** Follow-on to
[2026-07-01-mini-cut-gotcha-antipattern-demos.md](2026-07-01-mini-cut-gotcha-antipattern-demos.md)
(stage-1 DONE). That pass added a gotcha/anti-pattern beat to each mini-cut lesson's
**roadmap** (`demos_or_activities.md`) but deliberately did **not** touch stage-2 student
materials. This todo tracks the **examination step that comes before carry-over**: read each
updated roadmap beat against the lesson's *existing* assets and decide what (if anything) the
materials need.

This is a **read-only diagnosis pass** — it produces a per-lesson finding + recommended action,
not edits. Actual material edits/regeneration are a separate follow-up (per lesson, via the
`generate-materials-from-roadmap` skill or a targeted notebook edit).

## The examination question (per lesson)

For each lesson, read the roadmap's gotcha/anti-pattern beat and the existing assets, then answer:

1. **Already covered?** Do the existing lecture/lab materials already *show* or *name* these
   gotchas (even informally), or is the failure mode entirely absent from student-facing content?
2. **Where should it land?** Which existing asset is the natural home for the beat — a coda
   cell/section in a specific lecture, a lab step, PROCTOR_NOTES, or a genuinely new demo
   notebook? (The parent todo's coda-vs-full-demo call is the starting point.)
3. **Gap + action.** One line: `covered` / `add coda to <file>` / `new demo needed` /
   `lab tweak` — plus anything the roadmap beat assumes that the materials don't yet support
   (e.g. a running example, a fixture, a capped-iteration guard).

Reuse the roadmap's own form note (coda vs full demo) and the L23 Demo 5 template as the bar.

## Per-lesson checklist

Scope = the 10 lessons that got roadmap beats, plus L23 as the reference/control.
Roadmap beat lives in `docs/origin/lesson_roadmaps/<L>/demos_or_activities.md`.

- [x] **L01 — token basics** (coda, names 4). Assets: `L0102_lecture.md`,
      `L0103/L0104/L0106/L0107/L0109/L0110_lecture.ipynb`, `PROCTOR_NOTES.md`.
      Roadmap says the demos already *show* each — confirm, then decide the naming home.
      **Finding: `add-coda` → `L0110_lecture.ipynb`.** All four are already *shown* in the chain
      (and several already *named* in labs/PROCTOR): word≠token = `L0104` + `L0105` lab P3/P4;
      temp-0≠deterministic = `L0107` §2 + `L0108` lab P4 ("Why temperature 0 still varies");
      output-costs-more = `L0110` + `L0111` lab P3 (~5×); silent overflow/truncation = `L0110` +
      `L0111` lab P2 (names hard-reject / silent-truncation / degradation). **Gap:** no *student-facing*
      cell names the four as one portable pitfalls set — the only "gotcha" wording is in
      `PROCTOR_NOTES.md`, and that's *setup* gotchas (model downloads), not these four. **Action:**
      append a non-executable "Common pitfalls — L01's four gotchas" recap markdown section to the end
      of `L0110_lecture.ipynb` (name + one-line cure + point back to Demos 3/3.6/5; forward-link L13
      reproducibility & L19/L21 context, named not taught), + a one-line `PROCTOR_NOTES.md` pointer.
      No new fixture/running example needed (roadmap: "nothing new to load").
- [x] **L02 — prompting** (coda, names 4). Assets: `L0202_lecture.md`,
      `L0203/L0205/L0207/L0209_lecture.ipynb`, `L0206_lab_*` (the defensive-parsing fixtures
      the beat calls back to). **Finding: `add-coda` → `L0202_lecture.md` §6 (existing wrap-up) — light lift.**
      More covered than L01: three of the four are already *named* in individual slides — wrong-role =
      §2.3 "two mis-attribution footguns" (+ §2.4 "weighted, not enforced"); trusting-structured-output =
      §3.3/§3.4 (the model agrees but doesn't enforce → defensive parser, backed by the `L0206` lab
      fixtures the beat calls back to); few-shot leak/bias = §4.3 "diversity beats volume". **Gap:** (a) no
      single slide consolidates the four as a portable "anti-patterns to catch yourself" set with the shared
      root ("treating a strong nudge as a hard guarantee"); (b) anti-pattern #4 **bloated always-on system
      prompt** is only *implicit* (per-call cost in §2.5/§4.4) — never named as a fault. **Action:** add one
      recap slide to `L0202_lecture.md` §6 (the "three levers reconnected" wrap-up already *is* the closing
      slide) naming all four + one-line cures + forward-links (defensive-parsing → L07 tool args; lean-system
      → L19/L22), and explicitly name #4. No new fixture needed.
- [x] **L04 — DAGs** (coda, names 4). Assets: `L0402_lecture.md`, `L0403_lecture.ipynb`,
      `L0404_lab_*`. **Finding: `add-coda` (partial, ~2 of 4) + FLAG mis-scope.** ⚠️ L04 is mid-split:
      `objectives.md` carries a "Split note (reorder 2026-07-02)" — L04 was the former combined L12
      (chaining **+** routing); it's now **sequential-chaining-only**, routing moved to the new **L05**.
      `objectives.md` **and the built materials** (`L0402`/`L0403`/`L0404`) are already trimmed to
      chaining-only, but the `demos_or_activities.md` (where this coda was added) is **still the pre-split
      broad version** with Demos 2–4 = routing/branching/workflow-vs-agent — those now live in L05.
      Effect on the four gotchas: **#2 deterministic-DAG/accidental-back-edge** (shown `L0403` §4 "no
      back-edge = workflow" + `L0402` §5.3) and **#3 wrong-model-per-node** (shown `L0403` per-node
      Haiku/Sonnet binding + `L0402` §4) are **L04-native and already *shown* positively** (not yet
      *named* as pitfalls) → clean coda targets. But **#1 workflow-vs-agent** and **#4 brittle branch
      conditions/fallback** rest on routing/branch demos **L04 no longer contains** — they're **L05**
      material (L05 roadmap Demo 2 router+fallback, Demo 4 close). **Actions:** (a) when L04 stage-2
      regenerates sequential-only, add a coda naming just **#2 + #3** (both already shown); (b) **FLAG**:
      trim `L04/demos_or_activities.md` to match the `objectives.md` split note (it still describes routing
      as L04) — a reconciliation this coda sits on top of; (c) **new follow-up**: give **L05** its own
      gotcha coda for #1 + #4 — L05 was *out of the original beat scope* but its materials already show
      routing + fallback + the workflow-vs-agent close, so it's the honest home. **Assumption the
      materials don't support:** the coda's point-backs to "Demo 2 routing" / "Demo 4 back-edge" don't
      exist in L04's built materials.
- [x] **L07 — tool calling** (coda, names 4). Assets: `L0702_lecture.md`,
      `L0703/L0704/L0706/L0708_lecture.ipynb`, `L0705/L0707/L0709_lab_*`. **Finding: `covered`
      (optional light merge into `L0702_lecture.md` §6.1).** Best-covered coda lesson so far. All four
      gotchas are *shown* (Demos 1–4 = `L0703`/`L0704`/`L0706`/`L0708`; the "three outcomes" demo
      `L0708` shows the hallucinated-call **and** no-call outcomes by design) **and mostly *named*** in
      `L0702_lecture.md`: §6.1 "The misconceptions, named" is a 6-row confusion→correction table that
      already covers #4 ("if I define a tool it'll use it" → not necessarily; "deterministic" → no) and #3
      ("tool result is part of the assistant message" → no, `ToolMessage`), plus dedicated sections §3
      (round-trip / id / `ToolMessage`), §4 (tools cost tokens twice over), §5 (three outcomes + why you
      validate → #2). **Gaps (thin):** (a) the four aren't consolidated in the coda's *action-pitfall +
      one-line-cure + demo-point-back* shape (§6.1 is belief-correction framed, no cure column); (b)
      gotcha **#1 "schema sent once"** is covered in §4 but is **not** a row in the §6.1 recap. **Action:**
      accept as covered, or (low priority) extend §6.1 with a cure column + a "schema rides in every
      request" row to fully match the coda. Belongs at the *already-covered* end of the carry-over order.
      No new fixture needed.
- [x] **L08 — designing tools** (FULL Demo 5, incl. new live "tool-soup"). Assets:
      `L0802_lecture.md` (already mentions anti-patterns), `L0803/L0805/L0807/L0809_lecture.ipynb`,
      `L08*_lab_*`. Highest-value target — the roadmap grew a genuinely new demo, so check
      whether a lecture notebook needs the live tool-soup beat added.
      **Finding: `new-demo` → new `L0811_lecture.ipynb` (Demo 5). Top carry-over priority.** The
      materials stop at Demo 4 — there is **no Demo 5 notebook** (item numbering ends at the `L0810`
      lab). BUT the scope is smaller than "a whole new demo": per the roadmap, only the **tool-soup**
      beat is new live content; the other three anti-patterns are Demos 1–4's failures *named*, and
      those are **already delivered**. Naming recap already present: `L0802_lecture.md` §8.1 "The five
      traps" names over-tooling ("more tools = more capable → the opposite"), vague-description, and
      opaque-errors; §4.4 "two extremes to avoid" covers the god-tool/loose-schema. The **flip-back
      bad-design fixtures** Demo 5 reuses all exist already: sparse/misleading description in `L0805`
      (Demo 2), loose schema + opaque errors in `L0807`/`L0809` (Demos 3–4). **The one true gap = the
      live tool-soup beat:** no ~8-overlapping-tool registry (`lookup_user`/`find_user`/`get_customer`/
      `search_accounts`/`user_info`/`whois` + 2 distractors) exists anywhere, and no live
      selection-degradation run. **Action:** build `L0811_lecture.ipynb` = (1) the **new soup-registry
      fixture** + the live "What's Alex's email?" selection-degradation run on Sonnet 4.6 → Haiku 4.5
      (the only genuinely new asset), (2) flip back the *existing* Demo 2–4 bad-design variants to name
      the other three, (3) close on the payoff — in the L23 Demo 5 shape. **Assumptions to support:**
      Haiku 4.5 client (course cheap-contrast model, available) and a capped/re-runnable live selection
      (variance budget, mirror L07 Demo 4). Soup registry is L08-specific teaching material → keep it in
      the lesson (like L23's `example_skills/`), don't promote to `common/`.
- [x] **L10 — agent loop** (coda, names 3). Assets: `L1002_lecture.md`, `L1003/L1006_lecture.ipynb`,
      `L1004/L1005_lab_*`. Confirm the infinite-loop beat stays capped (never actually hangs).
      **Finding: `add-coda` → new section in `L1002_lecture.md` (after §5.3).** **Infinite-loop-stays-capped:
      CONFIRMED.** `L1003` §4 runs on a **scripted/stub model** (deterministic, no key needed), hits
      `recursion_limit` by design, and both `L1002` §3.3 ("safety net, not a correctness tool") and
      `PROCTOR_NOTES.md` ("a cyclic graph with no cap is a runaway waiting to happen — hitting the cap is
      [expected]") frame it as a demonstrated safety mechanism, never an actual hang. Materials map cleanly
      onto all 4 roadmap demos despite only 2 notebooks: `L1003` bundles Demos 1–3 (wire graph, termination
      +`recursion_limit`, tool-failure-as-message); `L1006` = Demo 4 (real model + prebuilt one-liner).
      **Per-gotcha:** #1 no-termination-guard and #2 tool-failure-escaping are thoroughly *shown*
      (`L1003` §4/§5, `L1002` §3/§4) but only *implied*, matching the roadmap's own honest self-assessment.
      #3 unbounded-context-growth is the thinnest — `L1002` slide 2.2 shows `add_messages` **appends every
      turn** mechanically, but neither notebook ties that to actual token/cost growth (no grep hit for
      context-growth/cumulative-token language) — consistent with the roadmap saying L10 only *implies* #3.
      **Gap:** no consolidated naming — `L1002` §5.3 "Common confusions to leave behind" is a *different*
      table (correctness/black-box/retry misconceptions, not these 3 named gotchas) and doesn't overlap.
      **Action:** add a coda section to `L1002_lecture.md` after §5.3, naming the 3 gotchas + one-line cures
      + point-backs (Demo 2's turn panel, Demo 3's error trace, slide 2.2's `add_messages`); #3's cure can
      stay purely a forward-link (L19) per the roadmap's own "name it, don't build it" instruction — no new
      fixture/token-measurement demo needed.
- [x] **L11 — shallow LangGraph agent** (coda, names 3). Assets: `L1102_lecture.md`,
      `L1103_lecture.ipynb`, `L1105_lecture.md`, `L1104_lab_*`. Note: state-mismanagement gotcha
      moved to L15 — coda here is `create_agent`-first only.
      **Finding: `add-coda` (light — borderline `covered`) → new closing section in `L1105_lecture.md`
      (after §3.4).** Well covered: all three gotchas are individually *addressed and even cautioned* in
      the two lecture markdowns. #1 one-liner-can-still-run-away = `L1102` §4.2 "The step cap did not
      disappear" + `L1105` §2.2 "The step cap is still there, just a default now"; #2 create_agent-as-
      un-debuggable-magic = `L1102` §3.2 "Map every piece back to what you wired in L10" + `L1103` §6–7
      ("Render what it wrapped" / "Name the freebies against their L10 twins"); #3 wrong-altitude/ceiling =
      `L1105` §3 (whole section) + §3.3 "Knowing where the ceiling is *is* the skill". **Scope check:** the
      state-mismanagement gotcha is correctly **absent** — materials are `create_agent`-first (`L1102` §4.1
      "You will not wire this graph by hand today"); that content is L15's, matching the roadmap's reorder
      scope note. **Gap (thin):** the three are spread across §4.2/§2.2/§3 and never *consolidated* into one
      named portable-gotcha recap. **Action:** add a short closing coda to `L1105_lecture.md` after §3.4
      "Where you land" that consolidates the three (the cures already exist verbatim in the sections above —
      this is a pull-together, not new teaching). No new fixture needed. Sits near the *already-covered* end
      of the carry-over order, just above L07.
- [x] **L12 — tracing** (coda, names 4). Assets: `L1202/L1204_lecture.ipynb`, `L1206_lecture.md`,
      `L1203/L1205_lab_*`, `PROCTOR_NOTES.md` (already has a gotcha hit).
      **Finding: `add-coda` → end of `L1204_lecture.ipynb` (instrumentation notebook).** All four
      anti-patterns are *shown* directly: #1 tracing-too-little = `L1202` §2 "From `print()` to a structured
      record"; #2 tracing-too-much = `L1204` §2.2 "the field set, and what is left out" + §3.3 "Signal vs
      noise"; #3 not-tracing-tool-args = `L1202` §4.2 "Wrong arguments — the call succeeded but on the
      wrong input"; #4 reading-the-summary-not-the-trace = `L1202` §3.2 "the `RunResult` summary is
      *derived from* the trace" + §4.4 premature-`natural`-stop. The **"reading spans out of order" →
      "reading the summary, not the trace" reframe lands** (§3.2/§4.4). **The flagged PROCTOR "gotcha
      hit" is a false lead for naming:** PROCTOR's "COMMON GOTCHAS" are *lab-mechanics* gotchas
      (unhashable-`dict`, reading `termination` off the wrong span), **not** the four tracing anti-patterns.
      **Gap:** no student-facing cell *names/consolidates* the four as a portable set. **Action:** add a coda
      to the end of `L1204_lecture.ipynb` (tightest fit — #1/#2 are Demo 4's field-set skill, #3/#4 the
      reading skills just practiced) naming the four + cures + point-backs; **preserve the L13 handoff line**
      (#3/#4 = L13's first eval cases). Note `L1206_lecture.md` §6 ("what does NOT go in the trace:
      extracts") already partially covers #2's boundary. No new fixture needed.
- [x] **L13 — evaluation** (coda, names 5). Assets: `L1302/L1304/L1306_lecture.ipynb`,
      `L1307_lecture.md`, `L1303/L1305_lab_*`. Verify the L12-traces cross-ref lands.
      **Finding: `add-coda` → `L1307_lecture.md` (the closing "carry forward" lecture).**
      **L12-traces cross-ref: CONFIRMED, robustly** — explicit `L12` refs in `L1302`/`L1304`/`L1306`/
      `L1307`/intro/PROCTOR, and `L1302` §3 "From a trace to a regression case" (§3.1 "the runaway
      becomes a trajectory check") grounds cases in L12's real failures (runaway/wrong-args/premature),
      exactly anchoring anti-patterns #1 & #4. All five *shown* across Demos 1–4: #1 happy-path-only =
      `L1302` §3 (cases from traces, not imagination); #2 sample-too-small = `L1304` §2 "One run can be
      luck" + §3 "Measure rates, not verdicts"; #3 over-trusting-judge = `L1306` §3 "scorer cost/judgment
      spectrum"; #4 not-targeting-trace-failures = `L1302` §3; #5 regressions-slip-through = `L1304` §4
      (Langfuse A/B experiments) + `L1307` §1.2 "Why a ratchet, not a one-time test". **Bonus:** the
      cross-cutting **brittle/over-tight-scorer** beat is well covered — `L1302` `reworded_case`
      "brittleness" fixture + "loosest check that still catches the bug", a dedicated `L1303` lab **Problem 4
      "loosen a brittle check"**, and `L1306` §3's exact-match/rewording trade-off. **Gap:** no consolidated
      5-item naming recap (`L1307` closes with the ratchet rule + forward pointers, not an anti-pattern list).
      **Action:** add a "five eval anti-patterns" recap section to `L1307_lecture.md` (name + cure + point-back;
      fold in the brittle-scorer as the cross-cutting one). No new fixture needed. Near the *already-covered*
      end of the carry-over order.
- [x] **L22 — skills** (coda, names 4). Assets: `L2202/L2205_lecture.md`,
      `L2203_lecture.ipynb`, `L2204/L2206_lab_*`. `L2205_lecture.md` already has anti-pattern
      content — check overlap with the promoted beat + the L23 handoff.
      **Finding: `add-coda` (expand existing `L2205 §3`) + FLAG a stale mini-cut handoff.** All four
      anti-patterns are already *named*, but **split across two lectures**: description faults (#1 too-vague
      → never loads, #2 too-broad → loads constantly) = `L2202` §4.2 "The failure modes of just-in-time
      loading"; container faults = `L2205` §3 "The anti-patterns" (a real 3-row table: sys-prompt→skill,
      tool→skill, skill→sys-prompt). **Overlap w/ promoted beat:** strong on container, but (a) not
      consolidated as the coda's "two description / two container" four-item beat (the description faults sit
      in a *different* lecture, `L2202`); (b) `L2205` §3's table lacks the coda's exact #3 direction — "a skill
      that should be a **tool**" (deterministic op wrapped in `SKILL.md`); it only has the inverse tool→skill.
      **L23 handoff: MISSING.** No L22 material references `L23` at all (the "composition" hits are L22's
      *own* skill-orchestrates-tools content); the coda wants an explicit hand-off to L23 Demo 5's collision
      beat. **⚠️ FLAG (drift beyond the coda):** `L2205` §5.2 says **"the mini cut ends here"** and forward-
      points only to full-course L24/L19/L09 — but `tracks.toml` (l.55) has the mini cut as `… L22, L23, L50`,
      so **L23 (composition capstone) and L50 follow L22 in the mini**. That line is stale (predates L23
      joining the mini) and must be corrected. **Actions:** (a) expand `L2205` §3 into the four-item beat —
      pull #1/#2 up from `L2202` §4.2, add the skill→tool direction — and add the L23 Demo 5 handoff; (b)
      fix `L2205` §5.2's "mini cut ends here" to point to L23 then L50. No new fixture needed.
- [x] **L23 — skill patterns (REFERENCE/CONTROL)** — Demo 5 already in `L2304/L2305_lecture.ipynb`.
      No action expected; use as the "what good looks like" bar for the others.
      **Finding: `covered` — CONFIRMED as the bar, no action.** `L2305_lecture.ipynb` is literally titled
      "Three composition anti-patterns" and delivers all three in the Demo-5 template shape (name → show
      it break → cure → tie to payoff): §2 over-chaining (5-skill toy chain vs collapsed 2-step seam), §3 a
      shared "skill" that's really a tool (proves they're identical → loading as a skill buys nothing), §4
      description collisions (run it: colliding pair loads the wrong skill → rewritten mutually-discriminating →
      right, with an offline-default + optional-live path). `L2304` builds the dependency graph + "depth costs
      loads" as the setup, and `example_skills/` ships the real `get_order` / `check_lesson_links` fixtures.
      This is the template every other lesson's coda is measured against.

## Output

Per lesson, a one-line finding + action tag (`covered` / `add-coda` / `new-demo` / `lab-tweak`).
When the audit is complete, roll the per-lesson actions into the parent todo's "stage-2
carry-over" line (or a fresh carry-over todo) so the actual edits can be scheduled. Order the
carry-over work by gap size — L08 (new demo) likely first, the already-partially-covered coda
lessons last.

### Carry-over roll-up (gap-ordered — do top-to-bottom)

> **Progress (2026-07-04, batch 2).** Landed the 6 naming-recap codas (**L01, L02, L10, L11, L12,
> L13**) and both reconciliations (**L04** pre-split demos file, **L22** stale mini-cut line — the
> latter already fixed by commit `8e29a5a`). Full pre-commit gate green. Still open (out of this
> batch's scope): the **L04 coda** (waits on L04 stage-2 sequential-only regen), the **L22 §3 coda
> expansion**, and the spun-off **L05 coda** (`task_b39acfac`). See per-item DONE tags below.
>
> **Progress (2026-07-04, batch 3).** Landed the **L04 coda** (item 2). The "waits on L04 stage-2
> sequential-only regen" blocker was **stale** — that regen already shipped in commit `9ce7227` (#18),
> so the built L04 materials were sequential-only already and the coda was added manually like its 6
> batch-2 siblings. Still open: **L22 §3 coda expansion** and the spun-off **L05 coda**
> (`task_b39acfac`).

Tags: `new-demo` (new material) > `add-coda`+flag (coda **and** a drift to reconcile) >
`add-coda` (naming recap, no new fixture) > `add-coda (light)` / `covered` (near/already done).
None of the codas need a new fixture — L08 is the only lesson requiring genuinely new assets.

**A. New material (do first)**
1. **L08 — `new-demo` — DONE (2026-07-04).** Built `L0811_lecture.ipynb` (Demo 5): the ~8-tool
   **soup-registry fixture** (six overlapping user-lookup tools + two distractors, lesson-local) +
   the "What's Alex's email?" selection-degradation beat — offline-by-default on the scripted
   `FakeModel` (unstable picks across runs + a chained-two), with an optional `if LIVE:` cell on real
   Sonnet 4.6 → Haiku 4.5. Beats 2–4 are the existing Demo 2–4 bad-design variants *named* (recap);
   the 4-name recap in `L0802` §8.1/§4.4 was cross-referenced (not duplicated). Added a `PROCTOR_NOTES.md`
   L0811 section and updated the L0802 demo list. Restart-run-all passes keyless; full gate green.

**B. Coda + a drift to reconcile (decide the drift as you go)**
2. **L04 — `add-coda` (2 of 4) + flag — reconciliation DONE (2026-07-04); coda DONE (2026-07-04, batch 3).**
   Reconciliation: added a split-note header to `L04/demos_or_activities.md` mirroring `objectives.md`'s —
   it flags Demos 2–3 (routing / user-input branching) as transitional L05 material and notes the built L04
   materials (`L0401`–`L0404`) are already sequential-only. **Non-destructive on purpose:** `objectives.md`
   also keeps its routing objectives (flagged, not deleted), so deletion is the stage-2 regen's job for both
   files together.
   **Coda: the "waits on L04 stage-2 sequential-only regen" premise was stale** — that regen already landed
   in commit `9ce7227` ("split routing out of L04", #18); the built materials (`L0402`/`L0403`) are
   sequential-chaining-only with **zero** routing content, so the coda went into already-final materials
   exactly like its 6 siblings (added manually, not via a future regen). Added **`## section 6. Two DAG
   gotchas, named`** to `L0402_lecture.md` before the bridge (renumbered Bridge → §7), naming #2
   (deterministic-DAG / accidental back-edge) + #3 (per-node model) with cures and point-backs **rewritten
   to the built sections** (§5.3 / §2.5 / slide 1.2 / §4 / `L0403`) — *not* the roadmap coda's stale
   "Demo 2 / Demo 4" refs, which never existed in the materials. #1/#4 routing gotchas → **L05** (spun off:
   task `task_b39acfac`); the coda points at `L05/objectives.md` in prose (soft link — L05's own material
   coda has not landed yet, so no hard anchor into a nonexistent section).
3. **L22 — mini-cut line DONE (commit `8e29a5a`); §3 coda expansion still pending.** The stale
   `L2205` §5.2 "the mini cut ends here" was already fixed (→ L23 then L50, per `tracks.toml`), along
   with `L2201_intro.md` and `PROCTOR_NOTES.md`. **Still pending (out of batch-2 scope):** expand
   `L2205` §3 into the 4-item beat (pull #1/#2 up from `L2202` §4.2; add the skill→tool direction) +
   add the L23 Demo 5 handoff.

**C. Straight naming coda (no new fixture)**
4. **L01 — `add-coda` — DONE (2026-07-04).** Appended §5 "Common pitfalls: L01's four gotchas" recap
   to `L0110_lecture.ipynb` (name/cure/point-back table, forward-links L13 + L19/L21 in prose, TOC
   synced) + a `PROCTOR_NOTES.md` L0110 pointer.
5. **L10 — `add-coda` — DONE (2026-07-04).** New slide 5.4 "Three agent-loop gotchas, named" in
   `L1002_lecture.md` between §5.3 and the bridge (renumbered bridge → 5.5); #3's cure is a forward-
   link to L19 only.
6. **L12 — `add-coda` — DONE (2026-07-04).** Appended §5 "Common pitfalls: L12's four anti-patterns"
   to `L1204_lecture.ipynb` (TOC synced); preserves the #3/#4 = L13-first-eval-cases handoff line.
7. **L13 — `add-coda` — DONE (2026-07-04).** New section 4 "Five eval anti-patterns, named" in
   `L1307_lecture.md`, folding in the brittle-scorer as the cross-cutting one.

**D. Light / already covered (lowest priority — consolidate existing naming)**
8. **L02 — `add-coda (light)` — DONE (2026-07-04).** New slide 6.2 "Four prompting anti-patterns…" in
   `L0202_lecture.md` §6 (renumbered 6.3/6.4); #4 (bloated always-on system prompt) now explicitly named.
9. **L11 — `add-coda (light)` — DONE (2026-07-04).** New slide 3.5 "Three shallow-agent gotchas,
   named" in `L1105_lecture.md` after §3.4.
10. **L07 — `covered`** → optional light merge into `L0702` §6.1 (add a cure column + a
    "schema rides in every request" row).
11. **L23 — `covered`** → reference/control, the bar. No action.

**Spun-off follow-up:** L05 gotcha coda — task `task_b39acfac` (running); also handles trimming
L04's #1/#4 out so they aren't double-owned.

**Summary:** 1 `new-demo` (L08) · 6 `add-coda` (L01/L04/L10/L12/L13/L22, two with a drift flag) ·
2 `add-coda (light)` (L02/L11) · 2 `covered` (L07/L23) · 1 spun-off L05 coda.
