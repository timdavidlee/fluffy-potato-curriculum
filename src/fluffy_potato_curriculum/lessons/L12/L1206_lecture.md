# Seeing your trace in Langfuse

```yaml
title: "Seeing your trace in Langfuse"
keywords: Langfuse, observability, trace, span, generation, observation, OpenTelemetry, export
estimated duration: 20
```

> **Lesson:** L12 — What an agent generates: state, logs, traces & extracts.
> **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L12/objectives.md) (objectives 5–6) · [demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L12/demos_or_activities.md) (Demos 6–7)
> **Comes after:** `L1204_lecture` (you instrumented the graph and produced `RunResult.trace`). This lecture sends *that* trace to a real tool — then closes the lesson by drawing the line between observability and the data your agent produces.
> **Anchor model for the live demo: Claude Sonnet 4.6.** This step is **additive** — objectives 1–4 stand alone on the in-memory / `.to_jsonl()` trace. Langfuse is the "now see it in the real tool" payoff, not a hard dependency.

## section 1. Why a real tool at all

### slide 1.1 You already built the minimal version

- text: in `L1204_lecture` you emitted a structured trace by hand — `TraceEvent` spans with `run_type`, `name`, `inputs`, `usage`, timings, all sharing one `trace_id`.
- text: real teams don't read `.jsonl` by eye at scale. They send traces to a **managed observability backend** and read them in a dashboard: a timeline of spans, token usage and cost, latency, inputs/outputs, errors.
- text: the point of building it by hand *first*: when you open the dashboard, none of it is magic — the timeline, the token counts, the errors are the **exact fields you emitted**.
- diagram: re-draw L1204's artifact — a stack of `TraceEvent` pills (chain frame · llm · tool · llm …) with the shared `trace_id` drawn as one **cyan** thread tying every pill together; an `--ink-faint` `.jsonl` file chip beside the stack tagged "readable — but by eye". No coral: nothing is failing, this is the raw material the whole lecture exports. Debuts the pill-stack this deck re-shows in 3.1.

### slide 1.2 The tool for this course: self-hosted Langfuse

- text: **Langfuse** is an open-source (MIT) LLM observability platform. The cohort runs **one shared instructor instance** — you get a base URL + project keys, no signup, no seat cost.
- text: it ingests **OpenTelemetry** spans. That is *why* `TraceEvent` was shaped the way it was in `common/tracing.py` — an approximate OTel/Langfuse shape — so exporting is a natural step, not a rewrite.
- text: keys load through `common/config.py` (the pydantic-settings seam), **never hard-coded** — the same stance as every other live call in the course.
- diagram: a **cyan** box "your instrumented `agent_graph.arun(...)`" with a **cyan** arrow labeled "export (langfuse SDK / OTLP)" — the lesson's own contribution — pointing to a cyan-bordered box "shared Langfuse dashboard"; a second arrow from an `--ink-faint` **dashed** box "L11 LangGraph agent" pointing at the *same* dashboard (another lesson's trace, not today's work). Explicitly no coral anywhere. **This source→pipe→dashboard picture is the lesson's motif**: 3.2 splits the pipe in two, 5.1 dashes the export leg, 5.2 re-draws the fan as the bookend.

[↑ Back to top](#seeing-your-trace-in-langfuse)

## section 2. The vocabulary mapping (the whole lecture in one table)

### slide 2.1 Your hand-built words, in Langfuse's words

- text: nothing new is happening — the same run, relabeled. Learn this table and the dashboard reads itself.
- table: maps each hand-built concept to its Langfuse name.

| You built (L1204) | Langfuse calls it | Notes |
| --- | --- | --- |
| one run (all spans share a `trace_id`) | a **trace** | the `trace_id` is the grouping key |
| one span (`TraceEvent`) | an **observation** | one row in the trace's timeline |
| an `llm` span (`run_type="llm"`) | a **GENERATION** | carries model, token `usage`, and cost |
| a `tool` / `chain` span | a **SPAN** | a tool call or the run's framing |
| `usage.input_tokens` / `output_tokens` | token usage + **cost** | Langfuse multiplies tokens by model price |
| `start_time` / `end_time` | latency on the timeline | the span's width in the waterfall |
| `error` | the observation's error badge | red, expandable |

### slide 2.2 Say it as a translation

- text: the one sentence to land out loud: *"the `run_type` field you set when instrumenting is the thing that decides GENERATION vs SPAN here."*
- text: OpenTelemetry says "span," Langfuse says "observation," LangSmith says "run" — three names, one structure. You learned the structure; the names are just vocabulary.
- text: exact field-name fidelity to one vendor is **not** the goal — approximate OTel-ish structure is. If a field doesn't map perfectly, that mismatch is a useful aside, not a bug.
- diagram: one `TraceEvent` card with the `run_type` row lit **cyan** — the field that decides — forking to two chips: **GENERATION** (`run_type="llm"`, with a token-`usage` badge) and **SPAN** (`tool` / `chain`); beneath, three `--ink-faint` name-tags pointing at the *same* card — "span (OTel)" · "observation (Langfuse)" · "run (LangSmith)" — three vocabularies, one shape. No coral: nothing here is a failure.

[↑ Back to top](#seeing-your-trace-in-langfuse)

## section 3. Exporting a run

### slide 3.1 The shape of the export (don't memorize the SDK)

- text: the export is a thin wrapper — you hand Langfuse the spans you already have. The exact call surface evolves; the *shape* is what matters.
- text: read the keys through the config seam, open a trace, add one observation per `TraceEvent`, mapping `run_type` to the observation type, and flush.
- diagram: not a code-print — draw the one-to-one mapping: left, 1.1's `TraceEvent` pill-stack re-shown; right, a column of Langfuse observation rows (**GENERATION** for the `llm` pills, `usage` badge attached; **SPAN** for `tool`/`chain`); one **cyan** arrow per pill, strictly one-to-one — the export is the lesson's contribution, so the arrows carry the cyan. Row chrome `--ink-faint`, no coral. The pseudocode sits beneath as a small supporting code chip, not the visual: `for span in result.trace: langfuse.<generation|span>(name=span.name, input=span.inputs, output=span.outputs, usage=span.usage, ...)` then `langfuse.flush()`.

### slide 3.2 Two ways in, same destination

- text: **langfuse SDK** — the most legible mapping to GENERATION / SPAN; you call a method per span. Simplest to read.
- text: **OTLP export** — emit the OTel-shaped spans over the OpenTelemetry protocol; Langfuse ingests them. More moving parts, but reinforces "this was OTel-shaped all along."
- text: either way the `langfuse` dependency is already in the project (`uv add` was run when the course infra was set up) — there is no install step in class.
- diagram: the 1.2 pipe re-drawn with its middle split into two lanes that reconverge on the *same* Langfuse dashboard box: "langfuse SDK — a method per span" in solid **cyan** (the lane the demo drives) and "OTLP export — OTel protocol" in solid `--ink-faint` (real and available, just not our route today). Explicitly no coral — neither lane is a failure — and not dashed either: OTLP isn't deferred, just dimmer. Second beat of the pipe motif.

[↑ Back to top](#seeing-your-trace-in-langfuse)

## section 4. Re-doing L12's reading skills in the dashboard

### slide 4.1 Locate a failure (objective 2), now point-and-click

- text: filter the project to the failing run, expand the offending observation, read its `inputs` and `error`.
- text: it's the *same reading* you did on the `.jsonl` in `L1203_lab` — wrong arguments, a runaway's repeated calls, a tool error — only faster to find at scale.
- text: the dashboard does not replace the skill; it accelerates a skill you already have. Without that reading practice, the dashboard would just look like a mystery — you've already put in the work that makes it legible.
- diagram: a mock dashboard waterfall — six observation rows as horizontal `--ink-faint` timeline bars (width = latency), one row carrying a **coral** error badge; a **cyan** filter→expand path landing on that row's `inputs` + `error` detail. Coral appears here for the first time in the deck and only on the actual failure being located — everything about the *finding* is cyan. **Section-4 motif**: 4.2 re-draws this waterfall twice.

### slide 4.2 Compare two runs (objective 4), now visual

- text: open two runs of the same task side by side; compare token usage, latency, and the span timeline.
- text: same comparison as `L1205_lab`'s diff helper — signal (a real behavior change) vs. noise (a few tokens, a few milliseconds) — now read off a waterfall instead of two printed lists.
- diagram: two of 4.1's waterfalls side by side (run A / run B) with a paired token-usage bar chart beneath; the one real behavior change — an extra tool-call row and its visibly taller bar — highlighted **cyan** (the signal), while the few-token / few-millisecond deltas stay `--ink-faint` (the noise). No coral: a difference is not a failure. Second waterfall beat; mirrors `L1205_lab`'s diff helper.

[↑ Back to top](#seeing-your-trace-in-langfuse)

## section 5. Graceful degradation and what's next

### slide 5.1 It's additive, never a gate

- text: without the Langfuse instance configured, you've **already finished** objectives 1–4 on the in-memory / `.to_jsonl()` trace. This step is the payoff, not a prerequisite.
- text: if the instance is unreachable on the day, a screenshot walk-through of the timeline, a GENERATION, and a two-run comparison teaches the same mapping. The live click-through is a bonus.
- diagram: the 1.2 pipe one more time, split at the source: the in-memory / `.to_jsonl()` leg solid **cyan** and stamped "objectives 1–4 — already done"; the export leg to the dashboard **dashed** `--ink-faint`, labeled "additive payoff — when the instance is up". Dashed here means optional-today, not failure — explicitly no coral, even for the instance-unreachable case. Third pipe beat.

### slide 5.2 This is the cohort's one observability home

- text: this is also where the LangGraph agent you built in **L11** can land its auto-emitted trace — the *same dashboard*, and it looks familiar, because it's the same spans (GENERATION/SPAN) you learned here.
- text: it also has a datasets/experiments feature that **L13** name-drops for evaluation — the platform version of the eval harness you'll hand-build next lesson.
- text: closing line: *"you built the minimal version by hand, so the real tool is just your trace, rendered."*
- diagram: the 1.2 fan as the motif bookend, extended: the shared Langfuse dashboard box in the middle with three tenants — today's hand-built trace arriving on a solid **cyan** arrow, the L11 LangGraph agent's auto-emitted trace on a **dashed** `--ink-faint` arrow (same spans, different lesson), and a dashed `--ink-faint` "datasets / experiments → L13" chip hanging off the dashboard. One observability home; no coral.

[↑ Back to top](#seeing-your-trace-in-langfuse)

## section 6. What does *not* go in here: extracts (the data plane)

### slide 6.1 Langfuse is observability — not your database

- text: you just sent your trace to Langfuse. That is the **observability plane** — sampled, TTL'd, keyed by `trace_id`, read by you and the eval harness to answer *"what did the run do?"*
- text: it is **not** where the data your agent *produces* should live. If a run extracts an invoice, scrapes a table, or generates a record, that hard data is a **deliverable** — the **data plane** — and it answers a different question: *"what did the run make?"*
- text: this is the last artifact from the intro's map — **extracts / new records** — and the one place it's easiest to get the architecture wrong.
- diagram: one **cyan** tool-call box fanning out to two destinations — a **cyan** arrow "observe" to a box "trace → Langfuse (TTL'd, for debugging)" captioned *"what did it DO?"*, and a *separate* **cyan** arrow "persist" to a box "database or S3 (durable, for downstream)" captioned *"what did it MAKE?"*. Both arrows cyan on purpose — doing *both* is the happy path, so explicitly no coral; the TTL'd/durable tags in `--ink-faint`. **The two-destination fan is the section-6 motif**: 6.2 pins the code to it, 6.3 breaks it.

### slide 6.2 Two calls at the boundary, two homes

- text: at the point your agent produces hard data you do **two independent things**: record *that it happened* in the trace, and *save the data itself* to its real store. The trace holds a pointer/summary; the datastore holds the record.
- diagram: 6.1's fan re-drawn with the two lines of the snippet below pinned as code chips on their arrows — `trace.append(TraceEvent(...))` riding the **cyan** observe arrow, `save_record(result)` riding the **cyan** persist arrow; the datastore's internals **dashed** `--ink-faint` ("wiring → L20/L21 / project brief" — deferred, not failed). Second fan beat. Conceptual snippet, not runnable — **no DB/S3 client is wired here** (that's out of scope):

  ```python
  # observability plane -- what the agent DID (goes to the trace)
  trace.append(TraceEvent(run_type="tool", name="extract_invoice", inputs=args, outputs=result))

  # data plane -- what the agent MADE (goes to a real store, NOT the trace)
  save_record(result)   # -> a database row / document, or a file in S3
  ```

- text: wiring an actual Postgres or S3 client is a data-engineering exercise — that's **L20/L21** or a project brief. Today's takeaway is the **boundary**, not the plumbing.

### slide 6.3 Cross the streams and you lose

- text: put extracts **only** in the trace → you have no queryable datastore, and the data vanishes when traces expire.
- text: treat the trace store **as** your database → you can't serve, join, back up, or access-control the data.
- text: neither tool is wrong; each is being used for the other's job. The rule, one line to carry out of L12: **observe the run in the trace; persist the product to the datastore.**
- diagram: 6.1's fan broken twice, two-up: left panel, the persist arrow missing — extracts ride only in the trace — with a **coral** "TTL expired — data gone" strike over the record; right panel, the persist arrow bent *into* the Langfuse box — trace store used as the database — with **coral** struck-through "serve / join / back up / access-control" chips. Coral is earned in both panels: these are the failures. The intact fan from 6.1 repeated small in cyan beneath as the fix. Third and final fan beat.

[↑ Back to top](#seeing-your-trace-in-langfuse)
