# L08 lecture: Seeing your trace in Langfuse

```yaml
title: "L08 lecture: Seeing your trace in Langfuse"
keywords: langfuse, observability, trace, span, generation, observation, OpenTelemetry, export
estimated duration: 20
```

> **Lesson:** L08 — Tracing: reading what your agent did.
> **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L08/objectives.md) (objective 5) · [demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L08/demos_or_activities.md) (Demo 6)
> **Comes after:** `L0804_lecture` (you instrumented the loop and produced `RunResult.trace`). This lecture sends *that* trace to a real tool.
> **Anchor model for the live demo: Claude Sonnet 4.6.** This step is **additive** — objectives 1–4 stand alone on the in-memory / `.to_jsonl()` trace. Langfuse is the "now see it in the real tool" payoff, not a hard dependency.

## section 1. Why a real tool at all

### slide 1.1 You already built the minimal version

- text: in `L0804_lecture` you emitted a structured trace by hand — `TraceEvent` spans with `run_type`, `name`, `inputs`, `usage`, timings, all sharing one `trace_id`.
- text: real teams don't read `.jsonl` by eye at scale. They send traces to a **managed observability backend** and read them in a dashboard: a timeline of spans, token usage and cost, latency, inputs/outputs, errors.
- text: the point of building it by hand *first*: when you open the dashboard, none of it is magic — the timeline, the token counts, the errors are the **exact fields you emitted**.

### slide 1.2 The tool for this course: self-hosted Langfuse

- text: **Langfuse** is an open-source (MIT) LLM observability platform. The cohort runs **one shared instructor instance** — you get a base URL + project keys, no per-student signup, no seat cost.
- text: it ingests **OpenTelemetry** spans. That is *why* `TraceEvent` was shaped the way it was in `common/tracing.py` — an approximate OTel/Langfuse shape — so exporting is a natural step, not a rewrite.
- text: keys load through `common/config.py` (the pydantic-settings seam), **never hard-coded** — the same stance as every other live call in the course.
- diagram: a box "your instrumented `agent_loop.run(...)`" with an arrow labeled "export (langfuse SDK / OTLP)" pointing to a box "shared Langfuse dashboard"; a second arrow from "L12 LangGraph agent" pointing at the *same* dashboard, to foreshadow that later traces land here too.

[↑ Back to top](#l08-lecture-seeing-your-trace-in-langfuse)

## section 2. The vocabulary mapping (the whole lecture in one table)

### slide 2.1 Your hand-built words, in Langfuse's words

- text: nothing new is happening — the same run, relabeled. Learn this table and the dashboard reads itself.
- table: maps each hand-built concept to its Langfuse name.

| You built (L0804) | Langfuse calls it | Notes |
| --- | --- | --- |
| one run (all spans share a `trace_id`) | a **trace** | the `trace_id` is the grouping key |
| one span (`TraceEvent`) | an **observation** | one row in the trace's timeline |
| an `llm` span (`run_type="llm"`) | a **GENERATION** | carries model, token `usage`, and cost |
| a `tool` / `chain` span | a **SPAN** | a tool call or the loop step |
| `usage.input_tokens` / `output_tokens` | token usage + **cost** | Langfuse multiplies tokens by model price |
| `start_time` / `end_time` | latency on the timeline | the span's width in the waterfall |
| `error` | the observation's error badge | red, expandable |

### slide 2.2 Say it as a translation

- text: the one sentence to land out loud: *"the `run_type` field you set when instrumenting is the thing that decides GENERATION vs SPAN here."*
- text: OpenTelemetry says "span," Langfuse says "observation," LangSmith says "run" — three names, one structure. You learned the structure; the names are just vocabulary.
- text: exact field-name fidelity to one vendor is **not** the goal — approximate OTel-ish structure is. If a field doesn't map perfectly, that mismatch is a useful aside, not a bug.

[↑ Back to top](#l08-lecture-seeing-your-trace-in-langfuse)

## section 3. Exporting a run

### slide 3.1 The shape of the export (don't memorize the SDK)

- text: the export is a thin wrapper — you hand Langfuse the spans you already have. The exact call surface evolves; the *shape* is what matters.
- text: read the keys through the config seam, open a trace, add one observation per `TraceEvent`, mapping `run_type` to the observation type, and flush.
- diagram: pseudocode, not runnable verbatim — `for span in result.trace: langfuse.<generation|span>(name=span.name, input=span.inputs, output=span.outputs, usage=span.usage, ...)` then `langfuse.flush()`. Emphasize the one-to-one: one `TraceEvent` → one observation.

### slide 3.2 Two ways in, same destination

- text: **langfuse SDK** — the most legible mapping to GENERATION / SPAN; you call a method per span. Simplest to read.
- text: **OTLP export** — emit the OTel-shaped spans over the OpenTelemetry protocol; Langfuse ingests them. More moving parts, but reinforces "this was OTel-shaped all along."
- text: either way the `langfuse` dependency is already in the project (`uv add` was run when the course infra was set up) — there is no install step in class.

[↑ Back to top](#l08-lecture-seeing-your-trace-in-langfuse)

## section 4. Re-doing L08's reading skills in the dashboard

### slide 4.1 Locate a failure (objective 2), now point-and-click

- text: filter the project to the failing run, expand the offending observation, read its `inputs` and `error`.
- text: it's the *same reading* you did on the `.jsonl` in `L0803_lab` — wrong arguments, a runaway's repeated calls, a tool error — only faster to find at scale.
- text: the dashboard does not replace the skill; it accelerates a skill you already have. A student who never read a raw trace would treat the dashboard as a mystery.

### slide 4.2 Compare two runs (objective 4), now visual

- text: open two runs of the same task side by side; compare token usage, latency, and the span timeline.
- text: same comparison as `L0805_lab`'s diff helper — signal (a real behavior change) vs. noise (a few tokens, a few milliseconds) — now read off a waterfall instead of two printed lists.

[↑ Back to top](#l08-lecture-seeing-your-trace-in-langfuse)

## section 5. Graceful degradation and what's next

### slide 5.1 It's additive, never a gate

- text: a student without the Langfuse instance configured **already finished** objectives 1–4 on the in-memory / `.to_jsonl()` trace. This step is the payoff, not a prerequisite.
- text: if the instance is unreachable on the day, a screenshot walk-through of the timeline, a GENERATION, and a two-run comparison teaches the same mapping. The live click-through is a bonus.

### slide 5.2 This is the cohort's one observability home

- text: the same Langfuse instance returns in **L12**, where your LangGraph agent's auto-emitted trace lands in the *same dashboard* — and looks familiar, because it's the same spans (GENERATION/SPAN) you learned here.
- text: it also has a datasets/experiments feature that **L09** name-drops for evaluation — the platform version of the eval harness you'll hand-build next lesson.
- text: closing line: *"you built the minimal version by hand, so the real tool is just your trace, rendered."*

[↑ Back to top](#l08-lecture-seeing-your-trace-in-langfuse)
