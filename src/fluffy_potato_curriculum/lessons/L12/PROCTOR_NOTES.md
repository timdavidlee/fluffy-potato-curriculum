# L12 Proctor Notes — What an agent generates (state · logs · traces · extracts)

Covers both labs in this lesson: **L1203** (read traces, locate failures) and **L1205**
(instrument and compare traces). Both labs are **pure Python, offline — no API key needed**;
they drive the shared `agent_graph.arun` (awaited in the setup cell) with a scripted `FakeModel`, so every trace is
deterministic. If a student's trace looks different from the solution, suspect an edited setup
cell, not "the model did something else" — there is no live model here.

**The lesson is framed by a taxonomy but its labs are all tracing.** The intro and lectures open
with the **map** (objective 6 / Demo 0): a run generates *state, logs, traces* (observability)
and *extracts / new records* (data). The two conceptual beats — the opening map (in the intro and
`L1202`) and the closing "extracts go to a store, not the trace" (in `L1206`, section 6) — are
**lecture content, deliberately not lab problems**; objective 6 is taught, not exercised (a real
persistence exercise is out of scope for the mini budget). Deliver them, but don't expect a TODO
for them. The confusion to watch for during those beats: *"just save the agent's output in the
trace."* The answer: a trace is observability (sampled, TTL'd, for debugging); the hard data a run
produces is a deliverable and belongs in a **database or S3**. One line to leave them with:
**observe the run in the trace; persist the product to the datastore.**

General unblockers that apply across the lesson:

- The shared code lives in `fluffy_potato_curriculum.common` (`agent_graph`, `tools`, `tracing`,
  `fake_model`). If imports fail, the student is likely running a stale kernel or the wrong venv —
  `Restart Kernel` and confirm they launched with `uv run jupyter lab`.
- Remind students of the span vocabulary: `trace[0]` is the `chain` (run summary) span; each model
  call is an `llm` span; each tool dispatch is a `tool` span. `.one_line()` is the quickest way to
  eyeball any span.
- The through-line of the whole lesson: **read the arguments** (`span.inputs`), not just the call
  names. Most "I can't find the bug" moments end the second a student actually reads `inputs`.

---

## L1203_lab problem 1

**Narrate the good run** — loop over the trace printing `span.one_line()`, then answer which span
is the natural-termination point.

- COMMON GOTCHAS: Students point at the `chain` summary span (`trace[0]`) as "where it stopped."
  The termination *decision* is the last **`llm`** span — the one whose `outputs["tool_calls"]` is
  empty (the model emitted text, no tool). The `chain` span only *records* the outcome.
- UNBLOCKERS: Have them print `run_type` next to each `one_line()` and find the last `llm` span.
  Ask: "which span shows the model choosing *not* to call a tool?"
- APPROX TIME: 5 minutes.
- STRETCH: Reconstruct the `RunResult` summary (`final_text`, `iterations`, `termination`) from the
  trace alone, then assert it matches the real `RunResult` — proving the summary is derivable.

## L1203_lab problem 2

**Find the runaway** — detect the repeated tool call and assert `termination == "max_steps"`.

- COMMON GOTCHAS: `span.inputs` is a `dict` and therefore unhashable — counting it directly raises
  `TypeError`. They must key on `tuple(sorted(span.inputs.items()))`. Second gotcha: forgetting to
  filter to `run_type == "tool"` first, so `llm`/`chain` spans pollute the count.
- UNBLOCKERS: Suggest `collections.Counter` over the normalized `(name, tuple(sorted(items)))` key,
  built only from tool spans. The repeated key with count 4 is the runaway.
- APPROX TIME: 8–10 minutes (the unhashable-dict snag is the time sink).
- STRETCH: Generalize to "flag any tool call that repeats with identical args ≥ 3 times" — the seed
  of a loop-detection check, and a natural L13 eval case.

## L1203_lab problem 3

**Spot the wrong argument** — read the `lookup` span's `inputs["city"]` and assert the looked-up
city was not `"Tokyo"`; explain why a success flag wouldn't catch it.

- COMMON GOTCHAS: Students look for an `error` or `is_error` and find none — the run is `natural`,
  `error=None`, and *looks green*. The whole point: the call **succeeded** at answering the **wrong
  question** (`{"city": "Paris"}`). The bug is visible only in the arguments.
- UNBLOCKERS: "The tool returned successfully — so why is the answer wrong? Read what we asked it to
  look up." Point them at the single `tool` span's `inputs`.
- APPROX TIME: 5–7 minutes.
- STRETCH: Write the assertion as a reusable check ("the answer about city X must have looked up
  city X") and note it's an outcome-vs-trajectory check — foreshadowing L13.

## L1203_lab problem 4

**Classify the signatures** — fill a markdown table mapping each failure trace to its signature name
and the field that reveals it.

- COMMON GOTCHAS: `tool_error` and `runaway` both surface an `[is_error]` tool span, so students
  conflate them. The distinguisher is `termination` (`natural` vs `max_steps`) plus the repetition,
  not the error flag alone. `premature` has **zero** tool spans — students expect a tool error and
  don't find one.
- UNBLOCKERS: Build a tiny table together for one trace (signature, the field that proves it), then
  let them fill the rest. The four tells: error field set (tool_error), wrong `inputs` on a green
  run (wrong_args), repeated call + `max_steps` (runaway), `natural` with no tool span (premature).
- APPROX TIME: 8 minutes.
- STRETCH: For each signature, name the L13 eval case it would become ("a check that fails when the
  bug is present") — these are literally next lesson's first cases.

---

## L1205_lab problem 1

**Trajectory from a trace** — write `tool_trajectory(trace) -> list[tuple[str, dict]]` returning
each tool span's `(name, inputs)`; assert it equals the expected sequence for the good run.

- COMMON GOTCHAS: Forgetting to filter to `run_type == "tool"` — including the `chain` and `llm`
  spans makes the trajectory wrong and the assert fail. Type-hint drift (`list[tuple[str, dict]]`)
  if they model it strictly.
- UNBLOCKERS: "What's the *path* through the tools — just the tool spans, in order?" One list
  comprehension filtered on `run_type == "tool"`.
- APPROX TIME: 5 minutes.
- STRETCH: Return inputs as a hashable, comparable form so two trajectories can be `==`-compared
  directly (sets/tuples) — useful for Problem 2's diff.

## L1205_lab problem 2

**Write `diff_traces(a, b)`** — compare two traces' tool trajectory, termination, and total tokens,
and report the differences.

- COMMON GOTCHAS: Reading `termination` off the wrong span — it lives on the **`chain`** span's
  `outputs["termination"]`, not the last `llm` span. Summing tokens without guarding `usage is None`
  — `tool` and `chain` spans carry no `usage`, so `span.usage.total_tokens` raises `AttributeError`
  on them; only sum over `llm` spans (or `if span.usage is not None`).
- UNBLOCKERS: Give the three things to compare as a checklist: trajectory (Problem 1), termination
  (chain span), total tokens (sum over llm spans). Build the return dict field by field.
- APPROX TIME: 12–15 minutes (this is the core problem).
- STRETCH: Add a per-span latency delta (`end_time - start_time`) and discuss why it's almost always
  noise on this offline model — real latency only shows up against a live model.

## L1205_lab problem 3

**Signal vs noise (written)** — apply `diff_traces` to the A/B pair and explain which difference is
signal and which would be noise, and why one run can't prove a fix.

- COMMON GOTCHAS: Students label the **token delta** as "signal." On its own it's noise — the
  meaningful change is `termination: max_steps → natural` (the runaway was fixed). The deeper point
  they often miss: because the graph is non-deterministic, a *single* A-vs-B pair can't prove the
  prompt edit caused the fix — you'd need several runs (the seed of L13's eval set).
- UNBLOCKERS: Ask two questions: "Which difference would a user actually feel?" (the runaway) and
  "If you re-ran B five times, are you sure it always terminates naturally?" (you're not — hence
  eval).
- APPROX TIME: 6–8 minutes.
- STRETCH: Have them sketch how they'd turn this one comparison into a repeatable check run many
  times — they're describing L13's eval harness before it's taught.

## L1205_lab problem 4

**A trace is data** — round-trip the good trace through `to_jsonl`/`from_jsonl` (or
`write_jsonl`/`read_jsonl` to a `tmp` path) and assert equality.

- COMMON GOTCHAS: Comparing object identity instead of value, or forgetting to actually pass through
  the string/file. `TraceEvent` is a Pydantic model, so `from_jsonl(to_jsonl(trace)) == trace` is
  value-equal — but only if they round-trip, not just `trace == trace`. Path handling: use the
  provided `tmp` path / `pathlib.Path`, not a hard-coded filename.
- UNBLOCKERS: "Serialize to text, parse it back, compare the two lists." Point at `to_jsonl` →
  `from_jsonl`. If using files, remind them `write_jsonl`/`read_jsonl` take a `Path`.
- APPROX TIME: 5 minutes.
- STRETCH: Open the `.jsonl` and read one line — it's one span as JSON. Connect to L1206: this is
  exactly the shape Langfuse ingests (one observation per span).
