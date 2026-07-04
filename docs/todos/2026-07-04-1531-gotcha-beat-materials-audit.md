# 2026-07-04 — Audit: gotcha/anti-pattern roadmap beats vs. existing materials

**Status: OPEN.** Follow-on to
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
- [ ] **L08 — designing tools** (FULL Demo 5, incl. new live "tool-soup"). Assets:
      `L0802_lecture.md` (already mentions anti-patterns), `L0803/L0805/L0807/L0809_lecture.ipynb`,
      `L08*_lab_*`. Highest-value target — the roadmap grew a genuinely new demo, so check
      whether a lecture notebook needs the live tool-soup beat added. **Finding:**
- [ ] **L10 — agent loop** (coda, names 3). Assets: `L1002_lecture.md`, `L1003/L1006_lecture.ipynb`,
      `L1004/L1005_lab_*`. Confirm the infinite-loop beat stays capped (never actually hangs).
      **Finding:**
- [ ] **L11 — shallow LangGraph agent** (coda, names 3). Assets: `L1102_lecture.md`,
      `L1103_lecture.ipynb`, `L1105_lecture.md`, `L1104_lab_*`. Note: state-mismanagement gotcha
      moved to L15 — coda here is `create_agent`-first only. **Finding:**
- [ ] **L12 — tracing** (coda, names 4). Assets: `L1202/L1204_lecture.ipynb`, `L1206_lecture.md`,
      `L1203/L1205_lab_*`, `PROCTOR_NOTES.md` (already has a gotcha hit). **Finding:**
- [ ] **L13 — evaluation** (coda, names 5). Assets: `L1302/L1304/L1306_lecture.ipynb`,
      `L1307_lecture.md`, `L1303/L1305_lab_*`. Verify the L12-traces cross-ref lands. **Finding:**
- [ ] **L22 — skills** (coda, names 4). Assets: `L2202/L2205_lecture.md`,
      `L2203_lecture.ipynb`, `L2204/L2206_lab_*`. `L2205_lecture.md` already has anti-pattern
      content — check overlap with the promoted beat + the L23 handoff. **Finding:**
- [ ] **L23 — skill patterns (REFERENCE/CONTROL)** — Demo 5 already in `L2304/L2305_lecture.ipynb`.
      No action expected; use as the "what good looks like" bar for the others. **Finding:**

## Output

Per lesson, a one-line finding + action tag (`covered` / `add-coda` / `new-demo` / `lab-tweak`).
When the audit is complete, roll the per-lesson actions into the parent todo's "stage-2
carry-over" line (or a fresh carry-over todo) so the actual edits can be scheduled. Order the
carry-over work by gap size — L08 (new demo) likely first, the already-partially-covered coda
lessons last.
