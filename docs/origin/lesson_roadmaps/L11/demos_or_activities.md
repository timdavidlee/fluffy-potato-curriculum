# L11: Teacher-led demos — What an agent generates: state, logs, traces & extracts

> Sibling doc: [objectives.md](objectives.md) (what the lesson aims for), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (lesson-plan row L11).
> Preceding lesson demos: [L10 demos_or_activities.md](../L10/demos_or_activities.md) (the loop these demos instrument). Following lesson: [L12 Evaluation: first pass](../L12/objectives.md) (consumes the trace this lesson produces).
>
> **Audience for this file:** the teacher running L11. Every demo below is *teacher-driven, no student participation*. Student-driven exercises live in the L11 labs (separate file, produced by stage 2).

## How to read this file

Each demo is a self-contained block with:

- **Goal** — the single insight the demo should land. Tied to a learning objective from [objectives.md](objectives.md).
- **Pre-flight** — what the teacher needs loaded before class.
- **Live script** — the order of operations during the demo. Treat it as a checklist, not a teleprompter.
- **What to highlight** — the moment(s) where the teacher should slow down and call out the takeaway out loud.
- **If the demo misbehaves** — graceful fallback for when the model surprises you (because it will; the loop is non-deterministic and that non-determinism is itself part of objective 4).

The demos are ordered to follow the learning objectives and the lesson's **concept-first, then tooled** spine, bracketed by the objective-6 taxonomy: **Demo 0** draws the opening map — *what a run generates, across two planes* (objective 6, the frame); Demo 1 motivates *why* a structured trace beats a `print()` (the L10 bridge, now this lesson's opener) and produces the first tiny trace; Demo 2 *reads* a full trace and reconstructs the run — including the **state** the trace carries (objective 1); Demo 3 *locates a failure* from the trace alone (objective 2); Demo 4 *instruments* the loop live to emit the full `TraceEvent` trace (objective 3); Demo 5 *compares two traces* of the same task (objective 4); Demo 6 *exports the same run to self-hosted Langfuse* and re-does objectives 2 and 4 in a real dashboard (objective 5); **Demo 7** closes the frame — *extracts go to a store, not the trace* (objective 6, conceptual). They build on each other — Demos 2, 3, and 5 read traces of the same loop Demo 4 instruments, so students see the artifact before they see how it is produced (concept first), then meet the real tool last (then tooled); Demos 0 and 7 are the conceptual bookends that place all this tracing work on the wider map. Run them in order on first delivery.

> **A note on what L11 reuses from L10, and what is new.** L11 does **not** re-teach or re-derive the L10 loop — the model→tool→model control flow is assumed (see the L10 "Bridge to L11" and this lesson's objectives "L10 overlap" decision). What L11 adds is *observation*: a structured trace emitted at the loop's boundaries, read after the fact. Per the objectives' "inline-build vs. reference" decision, the **canonical reference copy** of the loop and tools is authored in the shared `common/` layer during L11's stage-2 pass — `common/agent_loop.py`, `common/tools.py`, and the new `common/tracing.py` (`TraceEvent`) — and L11 is the first lesson that *imports* them rather than hand-building them. The demos below therefore reference the loop and tools by name as a stable import, not as live-coded scratch (the one live-code beat is Demo 4's instrumentation wrapper).

## Naming and tooling reconciliation (read before building any demo)

The L11 [objectives.md](objectives.md) describe the loop and tools as they should exist in `common/` *after* stage 2 authors them. The **already-built L10 materials** (under `src/fluffy_potato_curriculum/lessons/L10/`) use slightly different names, and one planned tool does not exist yet. Stage 2 must reconcile these before these demos are runnable; flagging them here so the demo scripts and the eventual `common/` modules agree.

- **Loop function name.** L10's built lecture/labs name the loop `run_loop(model, tools, user_msg, max_steps) -> RunResult`. The objectives refer to it as `agent_loop.run(...)` / `common/agent_loop.py`'s `run()`. The demos below use **`agent_loop.run(...)`** to match the objectives and L12, on the assumption stage 2 names the `common/` reference copy that way. <!-- *NEED INPUT*: confirm the canonical name for the reference loop in common/agent_loop.py — keep the objectives' `run()` (and update any L10 cross-refs that still say `run_loop`), or rename to `run_loop` everywhere for continuity with what students built in L10. The name must be identical in L10's lecture/labs, this lesson, common/agent_loop.py, and L12, or the import story breaks. -->
- **`RunResult` gains a `trace` field.** L10's built `RunResult` is a dataclass with exactly `final_text: str`, `iterations: int`, `termination: str` (`"natural"` | `"max_steps"`) — and **no trace field**. Objective 3's decided schema adds **`trace: list[TraceEvent]`**. Demo 4 is where that field first appears; stage 2 adds it to `common/agent_loop.py`'s `RunResult`. Demo 2's narration of "where each `RunResult` field came from in the trace" relies on this addition.
- **`flaky_fetch` does not exist in L10 yet.** The L10 demos roadmap *planned* a `flaky_fetch(url)` tool with four URL behaviors, but the built L10 materials implement tool failure differently: `calculator(expression)` raises `ValueError` on non-arithmetic input, `lookup(city)` raises `KeyError` for a city not in its small `POPULATIONS` table, and `dispatch(...)` converts any raised exception into a `tool_result` with `is_error: True` and `repr(exc)` as content. The objectives nonetheless say L11 reuses `flaky_fetch` from `common/tools.py`. **Either path gives objective 2 its failure signatures**, so the demos below are written to work with whichever stage 2 ships, and call out where the choice matters. <!-- *NEED INPUT*: decide what backs objective 2's "locate a failure" signatures in common/tools.py — (a) author the planned flaky_fetch(url) with the four URL behaviors fresh in common/tools.py (matches the objectives' wording, gives a clean tool-error signature), or (b) reuse the already-built calculator ValueError / lookup KeyError failures plus a wrong-arguments task (no new tool, matches what students saw in L10). Recommendation: (a) flaky_fetch, because a dedicated failing tool makes the tool-error and runaway signatures far easier to provoke reliably than coaxing the model into a bad calculator expression. Whichever is chosen must match L12's reuse of the same tools. -->
- **Anchor model.** Decided in the objectives: Claude **Sonnet 4.6**, inheriting the L01–L10 precedent so a trace of the `common/` loop matches the behavior students saw in L10. Used live in Demos 4–6; Demos 1–3 read pre-captured traces and need no live call.

## Pre-flight (once, at the top of the lesson)

The teacher should have, before the first demo starts:

- A working notebook/REPL with the project `uv` env, able to `from fluffy_potato_curriculum.common import agent_loop, tools, tracing` (the stage-2 reference modules). Keys load through `common/config.py` (the pydantic-settings seam), never hard-coded — consistent with the project's live-by-default notebook stance.
- **A set of pre-captured traces, saved to disk as `.jsonl`** (one `TraceEvent` span per line, via the decided `.to_jsonl()` helper), captured *before class* on Sonnet 4.6 so the reading demos (2, 3, 5) are deterministic and don't depend on a live model behaving on the day:
  - `trace_good.jsonl` — one clean multi-step run of the L10 chaining task that terminates `natural` (Demo 2).
  - Four short *failing* traces, one per failure signature from objective 2 (Demo 3): `trace_tool_error.jsonl`, `trace_wrong_args.jsonl`, `trace_runaway.jsonl` (ends in `max_steps`), `trace_premature.jsonl` (terminates `natural` on a wrong/incomplete answer).
  - Two traces of the *same task* for the comparison demo (Demo 5): `trace_run_a.jsonl` and `trace_run_b.jsonl` — ideally one where a behavior actually changed (e.g. a runaway in A that a tightened prompt fixed in B) and the run-to-run noise is visible alongside it.
  - <!-- *NEED INPUT*: confirm where these captured traces live in the repo (a demos/ subdir under the L11 lesson folder? a fixtures file?) and that they are committed so the teacher isn't re-capturing live before every class. The compare demo (5) especially benefits from a saved A/B pair with a known, explainable difference. -->
- **The exact chaining task** used to produce `trace_good.jsonl`. It must force a *multi-step* run (at least two tool calls in sequence plus a natural-termination text turn) so there is something to narrate. L10's built tools are `calculator` (number in, number out) and `lookup` (city in, population out), which do not chain cleanly on their own. <!-- *NEED INPUT*: confirm the concrete multi-step task and that common/tools.py supports it. Options: (a) a task that calls calculator then lookup independently and combines them in the final answer (e.g. "What is 17*23, and what is the population of Tokyo?" — two tool calls, one text turn); (b) if flaky_fetch is added, a fetch-then-summarize task; (c) restore the L10 demos-roadmap puzzle ("population of the city whose name is the answer to 17 squared minus 1") only if common/tools.py's lookup table actually contains a matching keyed entry — the current L10 table is keyed by city name (tokyo/lagos/paris), not by number, so that puzzle does not run as-is. -->
- A slide (or printed handout) with the **`TraceEvent` field list** from the objectives' decided schema, so the teacher can point at it while narrating: `run_id`, `trace_id`, `parent_run_id`, `run_type` (`llm` | `tool` | `chain`), `name`, `inputs`, `outputs`, `error`, `start_time`, `end_time`, `usage` (`input_tokens` / `output_tokens` / `total_tokens` on `llm` spans).
- For Demos 4–6 only: a live Sonnet 4.6 client (through `common/config.py`) and, for Demo 6, the cohort's **self-hosted Langfuse** base URL + project keys (also through `common/config.py`). Infra and fallback in [docs/classroom-llm-management.md](../../../classroom-llm-management.md). If Langfuse isn't reachable on the day, Demo 6 degrades to a screenshot walk-through (see that demo's misbehave note) — objectives 1–4 stand alone without it.

> Why pre-capture the reading traces: objectives 1, 2, and 4 are *reading* skills. Reading is clearest on a fixed, known artifact the teacher has already studied — not on a live run that might take a different path mid-demo. Capture once before class, read live in class. The live model only appears in Demos 4–6, where *producing* and *exporting* a trace is the point.

## Demo 0 — The map: what a run generates (Objective 6, the opening frame)

**Goal:** in ~4 minutes, before any code, give the class the map the whole lesson hangs on: a single agent run generates several kinds of byproduct, and they belong on **two different planes**. Land the one boundary — *observability ≠ data* — so that when the lesson then spends most of its time on traces, students know exactly which corner of the map they're in.

**Pre-flight:**

- A whiteboard or one slide with two columns: **Observability plane** (State · Logs · Traces) and **Data plane** (Extracts / new records → DB / S3). No code needed.

**Live script:**

1. Ask: *"Your agent just finished a run. What did it leave behind?"* Collect answers, then sort them live into the two columns.
2. Walk the **observability plane** as an increasing-permanence axis: **state** (the live message history the loop feeds the model — mutating, in-memory, gone at exit), **logs** (the `print()` play-by-play — streamed, human-readable), **traces** (the durable, structured, run-scoped record). Say the through-line: *"a trace is mostly state, captured durably over time — that's why reading a trace is reading what the model saw."* All three answer **"what did the run do?"** and are read by *you and the eval harness*.
3. Walk the **data plane**: **extracts / new records** — the hard data the run produces as its deliverable (extracted fields, generated files, computed rows). This answers **"what did the run make?"** and is read by *downstream systems and users*.
4. Draw the boundary and name the mistake: *"Don't cross the streams. Extracted business data goes to a database or S3 — not into your trace spans. And your trace store is not your system of record."* Preview that Demo 7 returns to this at the end; everything between here and there is the **traces** column.

**What to highlight:**

- The lesson's title lists four things, but its *weight* is on one column: **traces**. This map exists so tracing reads as one corner of a bigger picture, not an isolated topic.
- The single boundary to remember: **observability (state/logs/traces) is for reading the run; data (extracts) is the product.** Different homes, retention, and consumers.

**If the demo misbehaves:**

- Purely conceptual — no model, no code. If the class fills the columns fast, move straight to Demo 1; if they conflate "the answer the agent returned" with "a trace," that confusion *is* the Demo 7 payoff — flag it and move on.

## Demo 1 — From `print()` to a structured event (Objective 3, opener; reinforces the L10 bridge)

**Goal:** motivate the whole lesson in two minutes. Land the main point *"structured beats printed the moment you have two runs"* by turning one of L10's `print()` lines into a structured event appended to a list — the simplest possible trace. This is the L10 optional bridge demo, promoted to L11's opener per the objectives' "L10 overlap" decision (the L10 demos file left "include the bridge here or save it as L11's opener?" open; L11 claims it).

**Pre-flight:**

- L10's per-iteration print wrapper visible in scrollback or on a slide: the line that prints iteration number, tool calls, tool results, cumulative tokens, latency. Recall it by name as the *"minimum-viable trace"* L10 already called it.
- An empty `events: list[dict] = []` ready to append to.

**Live script:**

1. Recall L10's print-per-iteration wrapper out loud: *"L10 ended with this — one printed line per loop step. We called it a minimum-viable trace. Watch what's wrong with it the moment we have more than one run."*
2. Run a single loop iteration with the print wrapper. Read the printed line. Then ask the rhetorical question: *"Now compare this run to yesterday's run. How? Scroll up and eyeball two walls of text?"*
3. Replace **one** `print(...)` with a structured dict appended to a list — exactly the L10 bridge shape, e.g. `events.append({"run_type": "tool", "name": call.name, "inputs": call.input})`. Run again. Show `events` at the end: a list of records, not a wall of text.
4. Land the contrast explicitly: a printed line is human-readable and ephemeral; a record can be **filtered, counted, diffed, and fed to evaluation** (forward-point to L12). That jump — print → structured record — is the single most important instrumentation move in the lesson.

**What to highlight:**

- A trace is the **durable memory of an ephemeral run.** The loop runs and exits; without a record, all you keep is the final answer and whatever scrolled past. Say this first and say it plainly — it's the reason the lesson exists.
- *"Tracing is just logging"* is the confusion to pre-empt right here. A pile of `print()` lines is not a trace until it has **order, structure, and a run identifier**. This demo shows structure; Demo 4 adds the run identifier.
- This dict is a hand-rolled stand-in; Demo 4 replaces it with the real `TraceEvent` Pydantic model from `common/tracing.py`. Don't polish the dict — it's a teaser.

**If the demo misbehaves:**

- Nothing model-dependent here; a single iteration is enough. If a live call is slow, run it against one of the pre-captured traces instead and just show the difference between the printed line and the structured record.

## Demo 2 — Read a trace and narrate the run (Objective 1)

**Goal:** reconstruct a multi-step run *by reading the trace alone*, out loud, event by event. Land that a trace is structured, complete, and **replayable on the page** — no re-execution needed.

**Pre-flight:**

- `trace_good.jsonl` loaded into a list of `TraceEvent` and pretty-printed (a compact one-line-per-span rendering the class can read top to bottom).
- The `TraceEvent` field-list slide from pre-flight visible alongside.
- The `RunResult` for the same run on hand (its `final_text`, `iterations`, `termination`), so the teacher can point from summary back into the trace.

**Live script:**

1. Narrate the run from the trace, in order, the way the objective phrases it: *"span 1 is an `llm` call — the model asked for `calculator(expression=...)`; span 2 is a `tool` call running it, output `…`; span 3, another `llm` call; …; the last `llm` span emitted text and no tool call — terminated `natural`."* Read it like a story.
2. For each span, name **which kind** it is from `run_type` (`llm` / `tool` / `chain`) and show where one loop iteration ends and the next begins.
3. Stop on a tool-call span and read the **arguments** out loud. Make the point that the arguments — `calculator(expression="17*23")`, not just "called calculator" — are where the model's *thinking* shows. Read arguments first, always.
4. Point at the **intermediate state** the trace carries: cumulative token `usage` on the `llm` spans, per-span latency from `start_time`/`end_time`, the growing message history. Tie each field to a question it answers: *"why slow?" → latency; "why expensive?" → per-call tokens.*
5. Close by distinguishing the three things students now have in front of them: a **log line** (one event), a **trace** (the ordered record of the whole run), and the **`RunResult`** (the loop's summary). Point at where each `RunResult` field — `final_text`, `iterations`, `termination` — *came from* in the trace.

**What to highlight:**

- **Arguments are where the truth is.** Call counts say *how much*; arguments say *what the model was thinking*. This is the through-line of the entire lesson — set it here so Demo 3's "wrong arguments" signature lands.
- A trace sits **between** raw prints and the summary: more structured than a print, more complete than a `RunResult`. Students should be able to derive the `RunResult` from the trace by hand.
- Use the word **span** consistently for one trace entry, with the one-line note that OpenTelemetry says "spans," Langfuse says "observations," LangSmith says "runs" — so the structure is recognizable when they meet Langfuse in Demo 6.

**If the demo misbehaves:**

- This reads a fixed file, so it can't "misbehave" — but if the trace is too long to narrate in full, pre-trim it to ~6–8 spans. A trace you can't read top-to-bottom in ninety seconds is too long for a first narration.

## Demo 3 — Locate a failure from the trace alone (Objective 2)

**Goal:** find *where a run went wrong by reading*, not by re-running, and classify the failure by its **trace signature**. Land the headline skill: *a good trace lets you find the failure by reading; re-running a non-deterministic agent to "reproduce" a bug is slow and unreliable — the trace is the reproduction.*

**Pre-flight:**

- The four failing traces from pre-flight loaded and ready to show one at a time: `trace_tool_error.jsonl`, `trace_wrong_args.jsonl`, `trace_runaway.jsonl`, `trace_premature.jsonl`.
- A side panel showing, per iteration, the `(run_type, name, inputs)` triple — so a repeated call lands visually for the runaway case.

**Live script:** walk the four signatures, one trace each. For each, ask the class to watch, then point to the **exact span** where it went off the rails and name the signature:

1. **Tool error** — find the `tool` span (or its result) carrying `error` set / `is_error: true`. Then read the model's *next* span: did it recover, retry with different arguments, or give up? The trace shows the recovery decision, not just the failure. (If stage 2 ships `flaky_fetch`, this is the `https://crash`/`https://error` span; if it reuses L10's tools, this is a `calculator` `ValueError` or `lookup` `KeyError` surfaced as `is_error` by `dispatch`.)
2. **Wrong tool arguments** — the hardest and most important. The call **succeeded**, `error` is unset, the result looks fine — but the model passed a bad argument (wrong city, malformed expression), so it answered the *wrong question*. Show that the success flag tells you nothing here; only reading the `inputs` reveals it. This is the payoff of "trace arguments, not just call names."
3. **Runaway loop** — the same `(name, inputs)` pair repeating across iterations, ending in `max_steps`. Point at the side panel: same call, again, again. The trace makes the repetition obvious at a glance; the `termination: max_steps` confirms it.
4. **Premature termination** — terminated `natural` (the model emitted no tool call) but the `final_text` is wrong or incomplete: the model *thought* it was done when it wasn't. Show that `natural` is not a synonym for "correct" — it only means "the model stopped asking for tools."

**What to highlight:**

- **You debug agents by reading, not by re-running.** A normal program is deterministic — re-run it and the bug reproduces. An agent is not: re-running can hide the bug or produce a *different* one. Teach "read the trace" as the first move when an agent misbehaves.
- Pre-empt *"the tool returned successfully, so that step was fine"* directly on the wrong-arguments case — a successful call to the wrong question is the bug a success flag will never show you.
- Pre-empt *"I'll just re-run it to see what went wrong"* on the runaway case — the trace of the failing run *is* the evidence; capture it, don't chase it.
- These four signatures are exactly L12's first eval cases (objective 2 of L12: "design eval cases that target failure modes already seen in traces from L11"). Tell students to keep the failures they find — they become regression cases next lesson.

**If the demo misbehaves:**

- All four traces are pre-captured, so behavior is fixed. If time is short, cut to the two highest-value signatures — **wrong arguments** and **runaway** — which are the ones a `print()` log makes hardest to see and a structured trace makes easy.

## Demo 4 — Instrument the loop to emit a real trace (Objective 3)

**Goal:** turn the toy dict from Demo 1 into the real thing — add `TraceEvent` emission at the loop's boundaries so `agent_loop.run(...)` returns a populated `RunResult.trace`. Land that **instrumentation is a wrapper, not a rewrite**: the L10 control flow is untouched; tracing only *observes* it.

**Pre-flight:**

- The `common/agent_loop.py` reference loop open, *without* trace emission yet (or with it folded behind a flag the teacher toggles). This is the one live-code beat of the lesson.
- The `TraceEvent` model from `common/tracing.py` importable.
- A live Sonnet 4.6 client through `common/config.py`, and the chaining task from pre-flight.

**Live script:**

1. State the rule before typing: *"I am not changing how the loop decides anything. I'm adding an emit at each boundary — that's it."* Point at the boundaries on the loop: before/after each model call, before/after each tool call, and at termination.
2. Live-add the emission. At each boundary, append a `TraceEvent`: an `llm` span around the model call (carrying `usage` token counts, `start_time`/`end_time`); a `tool` span around each dispatch (carrying `name` and `inputs`, and `error` on failure); and the loop/`chain` framing span. Give every span the **same `trace_id`** so they belong to one run — call out that this `trace_id` is the field that makes Demo 5's comparison and Demo 6's Langfuse view possible.
3. Run it live on the chaining task. Show the returned `RunResult.trace` — the same shape students read in Demo 2, now produced in front of them.
4. **Defend the field set out loud, and name what's left out.** Each field answers a question (latency → "why slow?"; repeated args → "why loop?"; per-call tokens → "why so expensive?"). Then name what is *deliberately omitted* — full prompt bodies, raw tracebacks, every intermediate variable — and why: a trace bloated with everything is as unreadable as no trace. Minimalism is a deliberate choice (objective 3; the "more fields is always better" confusion).
5. Call `.to_jsonl()` and show one span per line — the on-disk form that fed Demos 2–3 and will feed Demo 5.

**What to highlight:**

- **Instrumentation is a wrapper, not a rewrite.** If adding a trace ever changes *how the loop decides things*, observation has leaked into control flow — pull it back. Pre-empt *"tracing changes what my agent does"*: it shouldn't; it's read-only with respect to the loop's decisions.
- The `run_type` values (`llm` / `tool` / `chain`) and token `usage` are chosen to match OpenTelemetry/Langfuse shape on purpose — Demo 6 shows the same spans rendered in the real tool, and L14's LangGraph traces land in the same Langfuse with the same vocabulary. The recognition *is* the payoff.
- The `trace` field is what L12 consumes. Frame L11 as "produce the record," L12 as "judge the record" — say the pair out loud.

**If the demo misbehaves:**

- If live-coding the emission falls behind, toggle the prepared flagged version and walk it line by line — don't sacrifice the live run that produces the trace.
- If the live model takes a different path than expected, that's fine — *any* successful multi-step run produces a readable trace. Only Demo 5 needs a *specific* behavior, and that one reads pre-captured traces.

## Demo 5 — Compare two traces of the same task (Objective 4)

**Goal:** diff two runs of the *same* task and separate **signal** (a real behavior change) from **noise** (run-to-run variance on a non-deterministic loop). Land that a single differing run proves nothing — you compare to know whether a change is real.

**Pre-flight:**

- `trace_run_a.jsonl` and `trace_run_b.jsonl` from pre-flight — two runs of the same task, ideally with one explainable real difference (e.g. A runs away and hits `max_steps`; B, after a tightened system prompt, terminates `natural`) plus some benign variation.
- A ~10-line trace-diff helper ready but **not shown yet** — it's the upgrade beat. It walks the two ordered span lists and reports: did the tool-call sequence change, did any `inputs` change, did an extra iteration appear, did a new `error` show up, did `usage`/latency move.

**Live script:**

1. **Eyeball first.** Put the two printed traces side by side. Walk them together: same first tool call? same arguments? does B have an extra iteration? a new error? Find the differences by eye. This is cheap and fits the time budget — do it before reaching for code.
2. Ask the load-bearing question: *"B fixed the runaway — but is that because the prompt edit worked, or did I just get a lucky run?"* State plainly that a single A-vs-B difference **cannot** answer this; only comparing across runs (ideally several) can.
3. **Now introduce the diff helper** — the ~10-line walk over the two event lists. Run it; it prints the same differences students just found by eye, plus the token/latency deltas. The point of showing code *after* the eyeball pass: reinforce "a trace is data" — once it's structured, diffing is trivial.
4. Separate signal from noise explicitly on the output: *"this difference — runaway vs. natural — is signal; this one — 3 extra output tokens, 80ms slower — is noise."* Naming which is which is the skill.

**What to highlight:**

- The loop is **non-deterministic** (L10's "variance budget"). The same task can take a different path each run. A diff is how you tell a real regression from normal variation — but you must know what variation is *normal* before you call a difference a regression. Pre-empt *"the two traces are different, so I broke something"* head-on.
- This is the **seed of evaluation.** Comparing runs by eye to flag a regression is exactly the discipline L12 formalizes into a repeatable eval set — *same comparison, scaled from one eyeball diff to a fixed set of cases run many times*. Forward-point to L12 by name.
- The diff is only possible because every span carries a shared `trace_id` and structured fields (Demo 4). You cannot diff two walls of `print()` output — this is "structured beats printed," paid off.

**If the demo misbehaves:**

- Reads pre-captured traces, so it's stable. If you *also* want to show a live A/B (e.g. run the same task twice live to show the path genuinely varies), budget a re-run or two and accept that the live pair may not show as clean a difference as the curated one — that messiness is itself the lesson about variance. <!-- *NEED INPUT*: confirm the A/B framing for the curated pair — same-task-twice (pure variance), before/after a prompt edit (regression framing), or model A vs model B. The objectives leave all three open as valid; the before/after-a-prompt-edit pair makes the "signal vs noise" point most cleanly and previews L12's regression framing. (Note: the *model* A/B — Sonnet vs Haiku — is L12's headline contrast, so consider leaving model-vs-model to L12 and using a prompt before/after here to avoid stealing L12's beat.) -->

## Demo 6 — See the same trace in a real tool: self-hosted Langfuse (Objective 5)

**Goal:** export the hand-rolled `TraceEvent` spans from Demo 4 to the cohort's **self-hosted Langfuse** and read the *same run* in a real dashboard. Land that the structure students built by hand is exactly what the industry uses — the dashboard is not magic, it's their trace rendered. This is an **additive** step: objectives 1–4 already stand without it.

**Pre-flight:**

- The cohort's shared self-hosted Langfuse instance reachable; base URL + project keys loaded through `common/config.py` (never hard-coded). Fallback (local Docker, or a screenshot walk-through) per [docs/classroom-llm-management.md](../../../classroom-llm-management.md).
- The export path wired: either the `langfuse` SDK (a project dep added via `uv add`) or OTLP export of the OTel-shaped spans, since Langfuse ingests OpenTelemetry. <!-- *NEED INPUT*: confirm the export mechanism for the demo — the langfuse SDK (simplest, most legible mapping to GENERATION/SPAN) or raw OTLP export of the TraceEvent spans (reinforces the "approximate-OTel schema" decision but more moving parts). Requires `uv add langfuse` either way; surface the dependency to the user rather than installing it from this stage. -->
- The Langfuse project pre-opened in a browser tab the teacher can project.

**Live script:**

1. Re-run the Demo 4 task (or replay the captured run) with the Langfuse export enabled. Switch to the Langfuse tab and find the new trace.
2. **Map the vocabulary explicitly**, pointing at the UI: a Langfuse **trace** = one run (shares the `trace_id`); a Langfuse **observation** = one span; an `llm` span renders as a **GENERATION** (carrying model, token `usage`, cost); a `tool`/`chain` span renders as a **SPAN**. Say it as a translation: *"the `run_type` field you set in Demo 4 is the thing that decides GENERATION vs SPAN here."*
3. **Re-do objective 2** in the UI: filter to a failing run, expand the offending observation, read its `inputs`/`error`. Same reading as Demo 3, now point-and-click.
4. **Re-do objective 4** in the UI: open two runs of the same task side by side and compare token usage, latency, and the span timeline. Same comparison as Demo 5, now visual.
5. Close the arc: *"You built the minimal version by hand first, so none of this is mysterious — the timeline, the token counts, the errors are the exact `TraceEvent` fields you emitted. And when L14's LangGraph agent lands its traces in this same Langfuse, they'll look familiar, not new."*

**What to highlight:**

- **You build the trace by hand, then meet the real tool.** Learning to emit and read a trace by hand first is *why* the dashboard reads as obvious instead of magic. Concept-first, then tooled — the spine of the whole lesson, paid off in the last demo.
- The export is *additive*. A student without the Langfuse instance configured still completed objectives 1–4 on the in-memory / `.to_jsonl()` trace. Langfuse is the "now see it in the real tool" payoff, not a hard dependency — say this so the keyless/offline path doesn't feel second-class.
- The same Langfuse instance returns in L14 (LangGraph traces) and has a datasets/experiments feature L12 name-drops for eval. This is the cohort's one shared observability home.

**If the demo misbehaves:**

- If Langfuse is unreachable on the day, fall back to **pre-captured screenshots** of the trace timeline, a GENERATION observation, and a two-run comparison — narrate them against the live `TraceEvent` list students just produced. The mapping (trace=run, observation=span, GENERATION=llm) is the teachable content; the live click-through is a bonus, not the lesson.
- If the export produces spans that don't render as expected (wrong observation type, missing usage), that's a real and useful aside about the *approximate* OTel mapping — show the mismatch, explain that exact field-name fidelity to one vendor is explicitly *not* required, only approximate OTel-ish structure.

## Demo 7 — Extracts go to a store, not the trace (Objective 6, the closing boundary)

**Goal:** close the loop opened in Demo 0. Now that students have *built* a trace, show — conceptually, in ~5 minutes — that the hard data an agent produces is a **different artifact on a different plane**, and belongs in a database or object store, **not** in the trace they just built. Land the rule: *observe the run in the trace; persist the product to the datastore.*

**Pre-flight:**

- The `RunResult.trace` from Demo 4 still on screen (the observability artifact).
- One slide/snippet contrasting two side-by-side calls at a tool boundary — **no real DB/S3 client, no live persistence** (out of scope for the mini budget; say so):

  ```python
  # observability plane — what the agent DID (goes to the trace)
  trace.append(TraceEvent(run_type="tool", name="extract_invoice", inputs=args, outputs=result))

  # data plane — what the agent MADE (goes to a real store, NOT the trace)
  save_record(result)   # -> a database row / document, or a file in S3
  ```

**Live script:**

1. Point back at the Demo 4 trace: *"This is observability — sampled, TTL'd, keyed by `trace_id`, read by me and the eval harness. Useful for debugging; it is **not** where the invoice we just extracted should live."*
2. Show the two-call sketch. Make the split explicit: the **same** extracted `result` is *referenced* in the trace (so you can debug how it was produced) and *persisted* via `save_record(...)` to its real home (so downstream systems can query it). The trace holds a pointer/summary; the datastore holds the record.
3. Name the two failure modes of crossing the streams: (a) extracts written *only* into the trace → no queryable datastore, and the data vanishes when traces expire; (b) the trace store used *as* the database → can't serve, join, back up, or access-control the data. Neither tool is wrong; each is being used for the other's job.
4. State the scope boundary out loud: *"Wiring an actual Postgres or S3 client is a data-engineering exercise — that's L20/L21 or a project, not today. Today's takeaway is the boundary itself."*

**What to highlight:**

- **Two planes, two homes.** Observability (state/logs/traces) answers *what did the run do?*; data (extracts) is *what the run made*. Don't put the product in the observability layer.
- This is why the lesson is titled for all four artifacts but spends its hands-on time on the trace: the extract is real and important, but its *persistence* is a different lesson — here we only draw the line.

**If the demo misbehaves:**

- Purely conceptual — nothing to run. If time is tight, this compresses to a single sentence over the Demo 0 slide: *"extracts go to a DB or S3, never the trace."* Don't skip it entirely — it's the payoff of the Demo 0 frame and objective 6.

## Pacing notes for the teacher

- **Per-demo time (targets the objectives' decided ~75–100 minute, one-lecture budget):** Demo 0 is a ~4-min whiteboard frame (no code). Demo 1 is short (3–5 min, it's a recap + one edit). Demo 2 is 10–15 min (the core reading skill — don't rush it). Demo 3 is 12–18 min (four signatures; the wrong-arguments one deserves the most time). Demo 4 is the long live-code beat, 15–20 min. Demo 5 is 10–15 min. Demo 6 is 10–15 min and is the trimmable one — drop to a 5-minute screenshot tour or cut entirely if time is tight, since objectives 1–4 stand alone. Demo 7 is a ~5-min conceptual close (no code), compressible to one sentence but not skippable — it's the objective-6 payoff. Total: ~70–100 min for all eight, fitting the lecture block with discussion; the two conceptual bookends (Demos 0 and 7) add ~9 min and are the cheapest to compress under time pressure.
- **If the lecture must split** (per the objectives' open question): break after Demo 3 — part one is "read a trace / locate a failure" (Demos 1–3, all reading pre-captured traces, no live model), part two is "instrument / compare / export" (Demos 4–6, the live + tooled half).
- **Live-coding budget:** Demo 4's instrumentation wrapper is the *only* place to live-code. Demo 1 is a one-line edit; Demos 2, 3, 5 read fixed files; Demo 6 runs an export, not new logic. Do not re-derive the L10 loop anywhere — it's imported.
- **Variance budget:** only Demos 4 and 6 touch a live model. Budget one re-run each. The reading demos (2, 3, 5) are deterministic by construction because they read pre-captured traces — that determinism is a deliberate teaching choice, not an accident.
- **The audience watches, doesn't participate.** Resist *"where's the bug in this trace?"* as a class question — that's the L11 lab pattern, not a demo pattern. Hands-on trace-reading is for the labs (stage 2).

## Open authoring questions

- <!-- *NEED INPUT*: loop/tool naming reconciliation between L10's built `run_loop` + exception-based failures and the objectives' `agent_loop.run()` + `flaky_fetch`. See "Naming and tooling reconciliation" above — this must be settled before any demo is runnable, and the resolution must be identical in L10, common/agent_loop.py, common/tools.py, this lesson, and L12. -->
- <!-- *NEED INPUT*: where the pre-captured demo traces (trace_good, the four failure traces, the A/B pair) and the chaining task live in the repo, and that they're committed so the teacher isn't re-capturing live each delivery. -->
- <!-- *NEED INPUT*: the concrete multi-step chaining task for Demo 2, confirmed runnable against common/tools.py (the current L10 calculator+lookup don't chain cleanly, and the old "288-city" puzzle needs a number-keyed lookup entry that doesn't exist). -->
- <!-- *NEED INPUT*: the A/B framing for Demo 5's curated trace pair — prompt before/after vs. same-task-twice vs. model-vs-model — bearing in mind model-vs-model (Sonnet vs Haiku) is L12's headline contrast and may be best left to L12. -->
- <!-- *NEED INPUT*: the Langfuse export mechanism for Demo 6 (langfuse SDK vs OTLP), and confirmation that `uv add langfuse` (or the OTLP exporter dep) is run during stage 2 — this stage does not install deps, only surfaces them. -->
- <!-- *NEED INPUT*: whether Demo 6 runs live against the shared cohort Langfuse on first delivery or ships as a screenshot walk-through by default, gated on the shared instance being stood up (infra in docs/classroom-llm-management.md). -->
