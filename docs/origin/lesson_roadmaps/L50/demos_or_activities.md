# L50: Teacher-led walkthrough — Agent mini-project, end-to-end (mini-track capstone)

> Sibling docs: [objectives.md](objectives.md) (what the capstone aims for), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md).
>
> **Audience for this file:** the proctor running L50. This lesson is a **continuous guided build**, not a set of independent demos. The proctor drives from a blank file to a traced, evaluated shallow agent, narrating each decision; **students rebuild it alongside, cell by cell.** That "everyone builds the same thing, guided" shape is the walkthrough format — it sits between L13's teacher-only demos and a student-invented lab. The *independent* build is the separate [end-of-week project](../../PROJECT_BRIEF_DESIGN.md), not this lesson.
>
> **Anchor model: Claude Sonnet 4.6** (inherits the whole mini-arc precedent). **Contrast model: Claude Haiku 4.5**, used only in the optional Segment 5 A/B so students see their *own* agent's pass rate move between models — the same stance as [L13](../L13/objectives.md).
>
> **Platform: the cohort's self-hosted Langfuse instance** (the one they've traced to since [L12](../L12/objectives.md)). L50 makes **live** model calls and **live** Langfuse writes — keys via `common/config.py`, stack from [K06](../K06/objectives.md). Assume it is up; the notebook raises a clear error if not (**recommended:** require the live stack, no offline fallback — consistent with L13; see [objectives.md](objectives.md) open questions).

## How to read this file

The build is broken into six **segments** that map one-to-one onto the six learning objectives in [objectives.md](objectives.md). Unlike L13's demos, the segments are **not** independent — each one continues the *same* file the previous one left, so the artifact grows on screen from a goal to an evaluated agent. Run them strictly in order. Each segment carries:

- **Goal** — the single beat the segment lands, tied to an objective.
- **Pre-flight** — what must already be loaded/true before the segment starts.
- **Live script** — the order of operations; a checklist, not a teleprompter.
- **What to say out loud** — the capstone framing to voice at that moment (the "you already know this — watch it connect" narration that *is* this lesson's value).
- **If it misbehaves** — graceful fallback for a live model/platform surprise.

> **The spine of L50: assemble, don't teach.** Every primitive here was taught in an earlier lesson and lives in the shared [`common/`](../../../../src/fluffy_potato_curriculum/common/CLAUDE.md) layer. When a segment reaches for a tool, `create_agent`, a `TraceEvent`, or an `EvalCase`, **recall the owning lesson in one line and move on** — do not re-derive it. The new thing L50 offers is the *connection*: five skills becoming one build on a task the student chose. If you find yourself re-teaching how tracing works, you've left L50's lane.

## Pre-flight (once, at the top of the lesson)

Before Segment 1 starts, the proctor should have:

- **A live, reachable Langfuse instance** (host + keys through `common/config.py`; the K06 stack healthy). Dry-run the connection and a **trace write** *before class* — this is a hard dependency for **Segment 4** (the trace push), same as L12. The core walkthrough does **not** upload a dataset or run an experiment (that's the S5 student bonus), so no dataset/experiment dry-run is needed for the timed session. <!-- *NEED INPUT (stage-2 infra)*: confirm the config surface (host + public/secret key env vars) and the `require_langfuse()`-style guard the notebook calls at the top. -->
- **The shared `common/` layer importable, not rebuilt** — the shallow-agent constructor **`create_agent`** ([L11](../L11/objectives.md)), the shared tools in `common/tools.py`, the `TraceEvent` tracing bridge (`common/tracing.py`, L12), and the eval seam `common/evals.py` (`EvalCase` / `Scorer` / `EvalResult` + the Langfuse bridge `upload_dataset` / `emit_score`, L13). Use these names verbatim so students recognize them from the lessons that introduced them. <!-- *NEED INPUT (stage-2)*: confirm the exact import symbol for "run this shallow agent and get a traced RunResult" in the mini-track `create_agent` path (L11/L12 wiring), and pin it here so the walkthrough calls one stable API. -->
- **The receipt-reconciliation domain bundle ready** (decided — see the domain note below): the offline receipts (varied source formats) + records ledger + bank-transactions JSON/CSV in the lesson dir, and the one new tool `find_matching_record` **written and tested in a sibling file** so the walkthrough *writes* it live but doesn't *debug* it live.
- **A known, reproducible failure on that task** — a **malformed / unknown-format receipt** that must resolve to a graceful "no confident match"; captured ahead of class as a saved trace fixture (the L12 `.to_jsonl()` helper), so Segment 4's "find a real failure" never depends on reproducing a non-deterministic bug on the projector.
- **The Sonnet 4.6 client configured** — read through `common/config.py`. (Haiku 4.5 is only needed for the S5 *student bonus* A/B, not the walkthrough, so don't set it up for the timed session.)
- **The Langfuse project open on the projector** — you'll switch to it in **Segment 4** to show the trace (the dataset/experiment views belong to the S5 bonus, not the walkthrough).

> Why reuse `common/` wholesale: L50 is about *assembly and finishing*, not new agent code. Every minute spent re-implementing a loop or a trace emitter is a minute not spent on the capstone skill — taking a fuzzy goal all the way to an evaluated agent.

## Segment 1 — Scope the vertical slice (Objective 1)

**Goal:** turn a one-line goal into a buildable spec — one task, one tool, a "done" definition, and an explicit non-goal list. Land **build the thinnest thing that exercises all five objectives, then stop.**

**Pre-flight:** the chosen domain on a slide as a single sentence ("an agent that helps a user do X").

**Live script:**

1. Write the goal sentence at the top of the blank notebook. Out loud, cut it down: what is the *one* task, the *one* tool, and what will this mini-agent deliberately *not* do? Write the non-goal list into a markdown cell — visible restraint.
2. Apply the [L08](../L08/objectives.md) *is-a-tool-warranted?* test to the task on screen: could the model do this reliably in its head? If yes, the task is too trivial to trace/eval — pick a harder one. If the tool is clearly justified, say why.
3. State the "done" condition concretely: *the agent answers the task, the run is traced in Langfuse, and one eval case would catch its regression.* That sentence is the whole rest of the lesson.

**What to say out loud:**

- **A capstone is a vertical slice, not a product** — thin and all the way through beats wide and half-wired. Scope creep is the failure mode of this exact lesson.
- Naming the non-goals *is* the skill — the mini-project is defined as much by what it refuses to do as by what it does.

**If it misbehaves:** if the room pushes for a bigger scope, write the bigger idea into the non-goal list as "v2 / your own project" — it becomes the Segment 6 hand-off, not today's build.

## Segment 2 — Design and write the one new tool (Objective 2)

**Goal:** author a single small deterministic domain tool with the [L07](../L07/objectives.md)/[L08](../L08/objectives.md) checklist, registered next to the shared `common/tools.py` tools — the *only* genuinely new code in the lesson.

**Pre-flight:** the tool already written and tested in a sibling file (so class *writes* it fresh but the proctor knows it works).

**Live script:**

1. Write `find_matching_record(receipt)` as a plain Python function: clear name, typed signature, a docstring that reads as the tool's contract, and explicit error handling for a malformed/unknown-format receipt (return a "no confident match" signal, don't raise into a loop). Narrate each L08 choice as you make it — normalizing the varied receipt formats to a common shape is the one place the course's tool-design lesson gets a fresh workout.
2. Keep it **deterministic and offline** — it reads only the bundled records/receipts JSON/CSV; say why: a reproducible tool keeps the eval reproducible (the whole `common/` design stance).
3. Register it alongside the reused `calculator` (to total the receipt's line items and compute the reconciliation variance against the matched record) so the agent has a *real tool-selection decision* to make — which makes the Segment 4 trace worth reading.

**What to say out loud:**

- This is the L08 checklist, once more, on *your* task — name, schema, docstring-as-contract, error handling. Everything else today is imported; this you design.
- One new tool is the budget. If you're writing a second, that's your own project (Segment 6), not this slice.

**If it misbehaves:** if the tool's schema confuses the model into never calling it, that's a live L08 teachable moment — tighten the name/description and rerun; don't paper over it.

## Segment 3 — Assemble the shallow agent with `create_agent` (Objective 3)

**Goal:** wire the new tool (+ the reused shared tool) into a **`create_agent`** shallow agent, run it on the task, read the `RunResult`, and confirm natural termination — the [L11](../L11/objectives.md) one-liner doing a job the student defined.

**Pre-flight:** Segment 2's tool in hand; the `create_agent` import ready.

**Live script:**

1. One line: `agent = create_agent(model, tools=[new_tool, reused_tool])` (recall L11: "this is the L10 loop, packaged"). Run it on the task.
2. Read the `RunResult` on screen — final text, iteration count, termination cause. Confirm it terminated `natural`, not at the step cap.
3. Pick a `max_steps` deliberately *for this task* and say why — termination as a design choice ([L10](../L10/objectives.md), objective 2), not a magic default.

**What to say out loud:**

- **This is the same model → tool → model loop you hand-rolled in L10** — you're just not typing the loop anymore. The agent is now doing work *you* scoped.
- A shallow agent is enough. We are deliberately *not* adding planning/memory/subagents — that's the full course; the mini-project's whole point is that shallow is plenty.

**If it misbehaves:** if it loops or terminates early, don't fix it yet — **that's the raw material for Segment 4.** Note it and move on; the trace is where you'll diagnose it.

## Segment 4 — Trace it and find a real failure (Objective 4)

**Goal:** emit a `TraceEvent` trace, push the run to Langfuse, read it to narrate what the agent did, and **locate one real failure from the trace alone** — the [L12](../L12/objectives.md) skill, now on the student's *own* agent and an un-planted failure.

**Pre-flight:** the tracing bridge wired; the saved failure-trace fixture ready as a fallback.

**Live script:**

1. Run the agent with tracing on; push the run to Langfuse. Switch to the UI and narrate the run from the trace — model calls, the tool call and its arguments, the tool result, termination. Recall the L12 move in one line; don't re-teach trace reading.
2. Surface **the failure** — feed a **malformed / unknown-format receipt** and watch what the agent does: ideally it should return "no confident match," but a naive first cut may fabricate a wrong match or loop retrying `find_matching_record` on the same bad input. **Locate it from the trace**, not by guessing. Name its failure signature with the L12 vocabulary (tool error / wrong args / runaway / premature termination).
3. If the live run won't misbehave on cue, open the **saved failure fixture** and read *that* trace — modeling L12's "don't chase a non-deterministic failure by re-running; read the captured trace."

**What to say out loud:**

- **Now the failure is yours** — the course isn't handing you a planted bug. Spotting it in your own trace is the capstone version of L12.
- **Trace before you guess.** The trace says what actually happened; without it you'd be theorizing about a non-deterministic run.

**If it misbehaves:** the platform being down mid-segment is the hard dependency biting — fall back to reading the returned trace object inline, reconnect, and re-push after.

## Segment 5 — Turn the failure into one eval case (minimal — the walkthrough ends here) (Objective 5)

**Goal:** convert the Segment 4 failure into **one regression case** (`EvalCase` + `Scorer` that fails-when-broken / passes-when-fixed) and run it **once** against the agent — the [L13](../L13/objectives.md) loop **trace a failure → write a case that catches it → keep it forever**, on the student's own agent. This is the *minimal* close: **one case, one scorer, one run.** The Langfuse Dataset/Experiment/pass-rate/A-B machinery is deliberately **out of the walkthrough** — it becomes a student bonus (below).

**Pre-flight:** the failure from Segment 4 (live or fixture); `common/evals.py` types imported. **No Langfuse write needed for the core** (recommended: keep S5 a pure-Python single run). <!-- *NEED INPUT (stage-2)*: confirm the core S5 does a pure-Python `EvalResult` print (no `emit_score`/`upload_dataset`), with all platform writes in the bonus — see objectives.md objective 5. -->

**Live script:**

1. Write one `EvalCase` reproducing the malformed-receipt task, and a **trajectory** `Scorer` that reads `run.trace` and fails on the bug (e.g. "did not call `find_matching_record` twice on the same input" / "did not terminate `max_steps`"). Run it once; show it returning **False** against the bad run and **True** once the tool handles the malformed receipt gracefully.
2. Optionally add one **outcome** `Scorer` that reads `final_text` — checks the agent reported "no confident match" rather than a fabricated record id; the loosest check that still catches the bug (recall L13's brittleness beat in one line). Keep it to a single extra scorer; do not build out a dataset.
3. State the ratchet in one sentence and **stop**: *this case now catches this regression forever — that's what "done" means.* Point at the bonus for scaling it (dataset, experiment, pass rate, model A/B) — do **not** demo the platform here.

**What to say out loud:**

- **A good eval case comes from a real failure, not imagination** — you just watched yours happen in the trace. That's why L12 came before L13, and why both come before this capstone.
- **The slice isn't done when it runs — it's done when it's traced and has one case that would catch its regression.** That's the habit the whole mini course was building toward — and it's *one case*, not a platform.
- **Scaling this is your bonus.** You already learned Datasets, Experiments, and pass rates in L13; taking this one case there on your own agent is the "try it yourself" exercise, not something we spend the last of our 90 minutes on.

**If it misbehaves:** if the scorer passes against the *bad* run, it's not catching the bug — tighten it live (a regression case is *defined* by failing when broken). No platform dependency here, so nothing external to fail.

### Student bonus (not demoed) — take the case to the platform

Left for students to do after class, on their own agent (the platform-heavy half of [L13](../L13/objectives.md)): add both an outcome and a trajectory score, `upload_dataset` the small set as a Langfuse **Dataset**, run it as an **Experiment** with K samples to read a pass *rate*, and re-run against **Haiku 4.5** to compare Sonnet-vs-Haiku pass rates in Langfuse's run comparison. Flag it as the natural on-ramp to the [end-of-week project](../../PROJECT_BRIEF_DESIGN.md); keep it out of the timed walkthrough.

## Segment 6 — Reflect and hand off to your own project (Objective 6)

**Goal:** narrate the finished artifact as one connected story and point every student at their own next build.

**Live script:**

1. Scroll the notebook top to bottom — *goal → tool → agent → trace → eval* — and name, on this concrete agent, where each of the five mini-cut objectives showed up. This is the "you built the real thing, end to end" moment.
2. Ask each student (rhetorically — this is still proctor-led) for the **first thing they'd add next** — the canonical example being **reimbursement detection** (`check_reimbursement`: offset a matched expense against a bank credit that already hit the account), the stretch tool deliberately left out of the core slice. Other candidates: a harder receipt format, a tighter scorer. Name that as the seam into the independent [end-of-week project](../../PROJECT_BRIEF_DESIGN.md).
3. Point at [`MINI_WRAPUP.md`](../../../../src/fluffy_potato_curriculum/lessons/MINI_WRAPUP.md) as the next read — the course-level retrospective L50 deliberately does *not* try to be.

**What to say out loud:**

- **This is the shape of your project.** You've now watched one agent go blank-file-to-evaluated; the team build is the same shape, wider and yours.
- Everything you used today is in `common/` — you leave here knowing how little new code a real shallow agent actually needs.

**If it misbehaves:** n/a — if you're short on time, this segment compresses to two minutes of scrolling-and-naming without losing its point.

## Pacing notes for the teacher

- **Per-segment time (decided — ~90 min cap):** S1 scope ~10, S2 tool ~15, S3 assemble ~10, S4 trace+failure ~15, **S5 minimal eval case ~10**, S6 reflect ~10. **Total ~70 minutes**, comfortably inside the 90-minute ceiling pinned in [objectives.md](objectives.md) with room for discussion. **Out of the base budget entirely (student bonus / stretch, not demoed):** the Langfuse Dataset/Experiment/pass-rate work and the **Haiku 4.5 A/B** (S5 bonus), and the **reimbursement-detection** tool (S6 stretch) — run the reimbursement tool only if the room is ahead; the eval-platform work is always left for students. If you somehow overrun, the clean split point is the **S3/S4 boundary** ("scope → tool → agent" | "trace → minimal eval → hand-off"), but at ~70 minutes of content the whole slice is meant to land in one session.
- **Live-coding budget:** only S2's tool and S5's one-or-two scorers are genuinely *new* code written live. S3 is one `create_agent` line; S4 is a trace push + reading the Langfuse UI; S5 is a pure-Python single run. Keep everything in `common/` pre-imported — do not re-derive a loop, a trace emitter, or the eval types on screen.
- **Platform dependency:** Langfuse up is a *hard* pre-flight for **S4 only** (the trace push) — dry-run a trace write before class. The core walkthrough needs **no** dataset upload or experiment run (that's the S5 student bonus), so a flaky experiment path won't sink the timed session.
- **Variance budget:** the agent is non-deterministic. **Capture the S4 failure trace ahead of class** so "find a real failure" never depends on reproducing a bug live; keep the saved fixture one keystroke away.
- **Format reminder:** this is a *walkthrough* — students rebuild the same agent alongside the proctor. Resist turning it into an open "everyone invent your own agent now" session; that divergence is the end-of-week project, and doing it here will overrun the clock and fragment the room. **Decided:** stage 2 realizes these six segments as **ONE guided build notebook + `PROCTOR_NOTES.md`** (K-prework "runbook" spirit), **not** a lecture + separate `_empty`/`_solutions` lab pair — see the *Decided (format)* note in [objectives.md](objectives.md).

## Open authoring questions

Most of L50's framing is pinned in [objectives.md](objectives.md) (integrative-not-additive; reuse `common/` wholesale; one new tool only; find-your-own-failure; **core walkthrough = S1–S4 + a minimal S5, ~90 min, Sonnet-only; the Langfuse experiment/pass-rate/Haiku-A/B is a student bonus**; walkthrough format; hand off to the end-of-week project and `MINI_WRAPUP.md`). The remaining open items are shared with the sibling and are stage-2 mechanics:

- **Decided (format, 2026-07-04):** a **single guided build notebook + `PROCTOR_NOTES.md`** (K-prework runbook spirit), **not** the default lecture + `_empty`/`_solutions` lab pair — the whole lesson is one continuous proctor-led build, and the independent lab is the separate [end-of-week project](../../PROJECT_BRIEF_DESIGN.md). Stage 2 follows the runbook shape here, not the default material set. (Full rationale in the [objectives.md](objectives.md) *Decided (format)* note.)
- **Decided (mini-project domain, 2026-07-04):** a **receipt / expense-reconciliation helper** — normalize a receipt (varied source formats) and match it against an **offline records bundle** (JSON/CSV, no SQL). New tool `find_matching_record` + reused `calculator`; natural failure = a malformed/unknown-format receipt that must resolve to a graceful "no confident match"; **reimbursement detection** (`check_reimbursement`, offset an expense against a bank credit) is the Segment 6 stretch. Full spec — data bundle, tool signatures, failure, stretch — in the *Decided (mini-project domain)* note in [objectives.md](objectives.md); stage 2 builds to that.
- <!-- *NEED INPUT (stage-2 infra)*: the Langfuse config surface in `common/config.py` and the `require_langfuse()`-style guard — same item L12/L13 carry. -->
- <!-- *NEED INPUT (stage-2)*: the exact import/API for "run the mini-track `create_agent` shallow agent and get a traced `RunResult`" so the walkthrough calls one stable symbol (pin the L11/L12 wiring). -->
- <!-- *NEED INPUT (stage-2)*: whether the Segment 5 experiment is launched from the notebook via the Langfuse SDK or partly clicked in the UI on the projector — affects how the runner is shown live (same question L13 carries). -->
- <!-- *NEED INPUT (offline fallback)*: whether to provide a FakeModel-backed offline path for a student without a live key on the day, or hard-require the live stack (recommended: hard-require, consistent with L13 — a real traced/evaluated run is the point). -->
