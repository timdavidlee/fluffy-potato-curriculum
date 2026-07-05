# What an agent generates — state, logs, traces & extracts

```yaml
title: "What an agent generates — state, logs, traces & extracts"
keywords: tracing, trace, span, state, logs, extracts, observability, data plane, agent graph, Langfuse, debugging
estimated duration: 10
```

> **Lesson:** L12 — What an agent generates: state, logs, traces & extracts.
> **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L12/objectives.md) · [demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L12/demos_or_activities.md)
> **Read in order:** this intro (the map) → `L1202_lecture` (read a trace, locate a failure) → `L1203_lab` → `L1204_lecture` (instrument the graph, compare two runs) → `L1205_lab` → `L1206_lecture` (see it in Langfuse; where extracts go instead).
> **Anchor model for the live demo: Claude Sonnet 4.6.** The reading demos and both labs run **offline with no API key** (a scripted `FakeModel`); only the live instrument/export steps call a real model.

## Where this lesson sits

In [L10](../L10/L1001_intro.md) you built an agent from nothing: a **cyclic `StateGraph`** — an `agent` node that calls the model, a `route` conditional edge, a prebuilt `ToolNode` that runs any tool the model asks for, and a `tools → agent` back-edge that feeds the result back and cycles until the model stops — `run(...)` returning a `RunResult` with the `final_text`, the number of `iterations` (its `agent`-node visits), and *why* it stopped (`termination`: `"natural"` or `"max_steps"`). That graph already *did* something on every run. But unless you were watching the streamed chunks live, that "something" vanished the moment the run ended.

L12 is the turning point where the agent stops being only something you *build* and becomes something you *observe*. This lesson is titled for the whole inventory of what a run leaves behind — but its **center of gravity is tracing**, because the trace is the artifact next lesson (evaluation) consumes.

## The map: what a run generates, on two planes

Every agent run produces byproducts, and the first skill is knowing **which plane each belongs on** — because they have different homes, lifetimes, and readers.

- **Observability plane — *what the agent did*** (for *you* and the eval harness to read):
  - **State** — the agent's live working memory: the message history the graph grows turn by turn (via `add_messages`) and feeds back to the model. In-memory, mutating, gone when the process exits. It's the model's actual input on every `agent`-node visit.
  - **Logs** — the human-readable play-by-play, one line per event (L10's `print()` stream). Streamed, unstructured; fine for one live run, useless the moment you have two to compare.
  - **Traces** — the durable, structured, run-scoped record: every model call, tool call, and result, ordered and keyed by a shared `trace_id`. Filterable, diffable, feedable to evaluation.

  These three sit on one **axis of increasing permanence**: live state → streamed logs → durable trace. A trace is largely *state captured over time* — which is why reading a trace (most of this lesson) **is** reading what the model saw.

- **Data plane — *what the agent made*** (the deliverable, for downstream systems and users):
  - **Extracts / new records** — the hard data a run produces as its actual output: extracted fields, generated records, files. This does **not** go in the trace. It's persisted to its proper home — a **database** (rows/documents) or an **object store like S3** (files/blobs) — with its own schema, retention, and consumers.

**The one boundary to hold onto:** don't cross the streams. Your trace is not your database (wrong retention, wrong query model), and your database is not your trace (a trace is sampled, TTL'd observability, not durable business data). Observe the run in the trace; persist the product to the datastore. You'll get this boundary **conceptually** here and spend the hands-on time on the trace.

## The one idea, said three ways

- **You debug agents by reading, not by re-running.** A normal program is deterministic: re-run it and the bug reproduces. An agent is **not** — re-running can hide the bug or produce a *different* one. The trace of the failing run *is* the reproduction. Reading it is the first move when an agent misbehaves.
- **A trace is the durable memory of an ephemeral run.** The graph runs and exits; without a record, all you keep is the final answer and whatever scrolled past. The trace is what lets you answer *"what did it actually do?"* an hour, a day, or a hundred runs later.
- **Arguments are where the truth is.** Call counts tell you *how much*; the **arguments** the model chose tell you *what it was thinking*. "Called `lookup` three times" is ambiguous; "called `lookup('288')`, `lookup('289')`, `lookup('290')`" is obviously a fumbling search. Trace the arguments, and read them first.

## What you'll be able to do

By the end of L12 you can:

1. **Read a trace** of a multi-step run and narrate what the agent did, event by event — including the **state** (the message history) the trace carries.
2. **Locate a failure** from the trace alone — and name its signature: a **tool error**, **wrong arguments**, a **runaway loop**, or **premature termination**.
3. **Instrument** the L10 graph to emit a structured trace (`RunResult.trace`) — a wrapper around the compiled graph, never a rewrite of it.
4. **Compare two traces** of the same task and separate a real change (**signal**) from run-to-run variance (**noise**).
5. **Export the same run to a real observability tool** — the cohort's self-hosted **Langfuse** — and recognize your hand-built spans rendered in a dashboard.
6. **Sort what a run generates onto the right plane** — state, logs, traces (observability) vs extracts / new records (data) — and keep hard data out of the trace, in a database or S3 where it belongs.

## The vocabulary this lesson fixes

- **State** — the agent's live, in-memory working set (the growing message history the graph feeds back to the model each turn, via `add_messages`). Mutating and consumed by the graph; a trace is this state *serialized over time* so you can read it later.
- **Trace** — the complete, ordered record of one run: every model call, tool call, and the `chain` framing of the whole run, with enough detail to reconstruct the run without re-executing it.
- **Span** — one entry in a trace (one model call — an `agent`-node visit; one tool call — a `ToolNode` dispatch; or the `chain` framing span). We say **span** in prose; OpenTelemetry says "span," Langfuse says "observation," LangSmith says "run" — so you'll recognize the structure when you meet a real tool.
- **`trace_id`** — the id shared by every span of one run, so multiple runs' traces can be stored together and still be told apart. It's what makes the two-run comparison (and the Langfuse view) possible.
- **Structured trace vs. `print()`** — machine-readable records you can filter, count, and diff, versus human-readable text that collapses the moment you have more than one run to compare.
- **Extracts / new records (the data plane)** — the hard data a run produces as its deliverable. Distinct from state/logs/traces: it's the *product*, not a lens on the run, and it belongs in a **database or object store (S3)**, never in the trace.
- **`RunResult` vs. trace** — `RunResult` (from L10) is the *summary*; the trace is the *full record* the summary was derived from. You should be able to point at where each `RunResult` field came from in the trace.

## How we teach it: concept first, then tooled

You build the trace **by hand first** — instrument the L10 graph, read the spans, diff two runs — and only *then* meet the real tool (Langfuse), where you discover the structure you built by hand is exactly what the industry uses. That ordering is deliberate: when you open the dashboard, the timeline, token counts, and errors are the very `TraceEvent` fields you emitted, so the tool reads as obvious instead of magic.

## A note on the code you'll see

The L10 graph and tools now live as a shared, reusable reference in `fluffy_potato_curriculum.common` — `common/agent_graph.py` (`build_agent()` compiles the L10 ReAct graph; `run()`/`trace_graph()` stream it into a `RunResult`), `common/tools.py` (`calculator`, `lookup`, `flaky_fetch`), and `common/tracing.py` (`TraceEvent`). (`common/agent_loop.py` — the same `RunResult`/`TraceEvent` contract produced by a plain `while` loop — is kept alongside as a by-hand reference, but the graph is what L10 teaches and what L12 traces.) L12 is the first lesson that *imports* them instead of hand-building them, because this lesson is about *observing* the graph, not re-deriving it. The labs drive that graph with a scripted `FakeModel` so they run deterministically with no API key.

## The takeaway

L12 produces the record; **L13 (evaluation) judges it.** Tracing without evaluation tells you *what happened*; evaluation without tracing tells you *that something is wrong but not where*. They are a pair, and tracing comes first — because you cannot evaluate a run you cannot read. Keep the failures you find in this lesson's traces: they become your first eval cases next lesson. And keep the boundary straight: the trace is for *reading what the run did*; the hard data the run *made* goes to a database or S3, not into the trace.
