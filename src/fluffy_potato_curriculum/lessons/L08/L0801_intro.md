# L08 intro: Tracing — reading what your agent did

```yaml
title: "L08 intro: Tracing — reading what your agent did"
keywords: tracing, trace, span, observability, agent loop, langfuse, debugging
estimated duration: 10
```

> **Lesson:** L08 — Tracing: reading what your agent did.
> **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L08/objectives.md) · [demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L08/demos_or_activities.md)
> **Read in order:** this intro → `L0802_lecture` (read a trace, locate a failure) → `L0803_lab` → `L0804_lecture` (instrument the loop, compare two runs) → `L0805_lab` → `L0806_lecture` (see it in Langfuse).
> **Anchor model for the live demo: Claude Sonnet 4.6.** The reading demos and both labs run **offline with no API key** (a scripted `FakeModel`); only the live instrument/export steps call a real model.

## Where this lesson sits

In [L07](../L07/L0701_intro.md) you built an agent from nothing: a **model → tool → model loop** in plain Python that calls the model, runs any tool the model asks for, hands the result back, and repeats until the model stops — `run(...)` returning a `RunResult` with the `final_text`, the number of `iterations`, and *why* it stopped (`termination`: `"natural"` or `"max_steps"`). That loop already *did* something on every run. But unless you were watching the console live, that "something" vanished the moment the run ended.

L08 is the turning point where the agent stops being only something you *build* and becomes something you *observe*. The whole lesson rests on one sentence:

> **A trace is the durable, structured record of what happened, so you can read the run after the fact instead of guessing.**

L07 already showed you the seed of this: its loop *printed* one line per iteration, and we called that print-wrapper a **"minimum-viable trace."** L08 takes that idea seriously — it replaces the ephemeral `print()` with a structured record you can filter, diff, and feed to the next lesson.

## The one idea, said three ways

- **You debug agents by reading, not by re-running.** A normal program is deterministic: re-run it and the bug reproduces. An agent is **not** — re-running can hide the bug or produce a *different* one. The trace of the failing run *is* the reproduction. Reading it is the first move when an agent misbehaves.
- **A trace is the durable memory of an ephemeral run.** The loop runs and exits; without a record, all you keep is the final answer and whatever scrolled past. The trace is what lets you answer *"what did it actually do?"* an hour, a day, or a hundred runs later.
- **Arguments are where the truth is.** Call counts tell you *how much*; the **arguments** the model chose tell you *what it was thinking*. "Called `lookup` three times" is ambiguous; "called `lookup('288')`, `lookup('289')`, `lookup('290')`" is obviously a fumbling search. Trace the arguments, and read them first.

## What you'll be able to do

By the end of L08 you can:

1. **Read a trace** of a multi-step run and narrate what the agent did, event by event.
2. **Locate a failure** from the trace alone — and name its signature: a **tool error**, **wrong arguments**, a **runaway loop**, or **premature termination**.
3. **Instrument** the L07 loop to emit a structured trace (`RunResult.trace`) — a wrapper around the loop, never a rewrite of it.
4. **Compare two traces** of the same task and separate a real change (**signal**) from run-to-run variance (**noise**).
5. **Export the same run to a real observability tool** — the cohort's self-hosted **Langfuse** — and recognize your hand-built spans rendered in a dashboard.

## The vocabulary this lesson fixes

- **Trace** — the complete, ordered record of one run: every model call, tool call, and the loop step, with enough detail to reconstruct the run without re-executing it.
- **Span** — one entry in a trace (one model call, one tool call, the loop step). We say **span** in prose; OpenTelemetry says "span," Langfuse says "observation," LangSmith says "run" — so you'll recognize the structure when you meet a real tool.
- **`trace_id`** — the id shared by every span of one run, so multiple runs' traces can be stored together and still be told apart. It's what makes the two-run comparison (and the Langfuse view) possible.
- **Structured trace vs. `print()`** — machine-readable records you can filter, count, and diff, versus human-readable text that collapses the moment you have more than one run to compare.
- **`RunResult` vs. trace** — `RunResult` (from L07) is the *summary*; the trace is the *full record* the summary was derived from. You should be able to point at where each `RunResult` field came from in the trace.

## How we teach it: concept first, then tooled

You build the trace **by hand first** — instrument the L07 loop, read the spans, diff two runs — and only *then* meet the real tool (Langfuse), where you discover the structure you built by hand is exactly what the industry uses. That ordering is deliberate: when you open the dashboard, the timeline, token counts, and errors are the very `TraceEvent` fields you emitted, so the tool reads as obvious instead of magic.

## A note on the code you'll see

The L07 loop and tools now live as a shared, reusable reference in `fluffy_potato_curriculum.common` — `common/agent_loop.py` (`run()` → `RunResult`), `common/tools.py` (`calculator`, `lookup`, `flaky_fetch`), and the new `common/tracing.py` (`TraceEvent`). L08 is the first lesson that *imports* them instead of hand-building them, because this lesson is about *observing* the loop, not re-deriving it. The labs drive that loop with a scripted `FakeModel` so they run deterministically with no API key.

## The takeaway

L08 produces the record; **L09 (evaluation) judges it.** Tracing without evaluation tells you *what happened*; evaluation without tracing tells you *that something is wrong but not where*. They are a pair, and tracing comes first — because you cannot evaluate a run you cannot read. Keep the failures you find in this lesson's traces: they become your first eval cases next lesson.
