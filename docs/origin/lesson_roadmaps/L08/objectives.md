# L08: Tracing — reading what your agent did

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (lesson-plan row L08).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).
> Preceding lesson: [L07 Hand-rolled agent loop](../L07/objectives.md). Following lesson: L09 Evaluation: first pass (roadmap not yet written).

## Where this lesson sits

By L07, students have built a working **model → tool → model** loop in plain Python — `agent_loop.run(...)` returning a `RunResult` carrying `final_text`, `iterations`, and a `termination` cause (`"natural"`, `"max_steps"`, …). They have also already seen the *seed* of this lesson: L07's loop printed one line per iteration (iteration number, tool calls requested, tool results, cumulative tokens, latency), and L07 explicitly named that print-wrapper a **"minimum-viable trace."** L07's optional bridge demo went one step further and replaced a `print()` with a structured event dict appended to a list.

L08 picks up exactly there. The hand-rolled loop *did* something on every run — called the model, dispatched tools, hit a termination condition — but unless you were watching the console live, that "something" vanished the moment the run ended. **A trace is the durable, structured record of what happened, so you can read the run after the fact instead of guessing.** This lesson teaches students to (1) *read* a trace and reconstruct what the agent did, (2) *locate a failure* from the trace alone, (3) *instrument* their own L07 loop to emit a useful trace, and (4) *compare two traces* of the same task to see what changed between runs.

This is a turning point in the course's arc. Up to here, the agent has been something you *build*; from here on it is also something you *observe and judge*. L08 produces the raw material — the trace — that L09 (evaluation) turns into a graded judgment. Tracing without evaluation tells you *what happened*; evaluation without tracing tells you *that something is wrong but not where*. The two are a pair, and L08 comes first because you cannot evaluate a run you cannot read.

This lesson is deliberately **framework-free**. Students instrument the *same hand-rolled loop from L07*, not a hosted tracing platform. Hosted/managed tracers (LangSmith, OpenTelemetry-based backends, vendor dashboards) are mentioned as a forward pointer — students should know the category exists — but the teaching is built on a trace they emit and read themselves, so the *concept* is never hidden behind a product. <!-- *NEED INPUT*: confirm we want zero hosted-tracer hands-on in L08 and only a named-drop forward pointer. Recommendation: yes — keep L08 on the hand-rolled trace; revisit managed tracing once LangGraph lands (its built-in observability is one of the reasons to reach for a framework, per L07 objective 4). -->

## Prerequisites

Students arriving at L08 should already be able to:

- Build and run a model→tool→model loop in plain Python: call the model, detect a `tool_use` block, dispatch the tool, append a matching `tool_result`, and loop until termination (L07, objective 1). L08 instruments *this* loop — a student who cannot run it cannot trace it.
- Name the termination conditions and read a `RunResult`'s `termination` cause — `natural` vs. `max_steps`, with token-budget and loop-detection as sketched extensions (L07, objective 2). The termination cause is one of the most important fields a trace records.
- Recognize the three loop-level tool-failure modes — a tool raises, a tool returns a structured error result, a tool returns malformed output — and that the loop's default is to convert a failure into a `tool_result` with `is_error: true` (L07, objective 3). These are exactly the failure signatures students will hunt for in a trace.
- Read the per-iteration print output from L07's loop (iteration number, tool calls, tool results, tokens, latency). L08 turns that ephemeral print stream into a durable, structured trace.

If a student is shaky on the L07 loop itself, redirect to the L07 labs before continuing — L08 assumes a running loop as its subject and adds *observation*, not new control flow.

## Learning objectives

By the end of L08, a student should be able to:

1. **Read a trace of an agent run and reconstruct what the agent did.** Concretely:
   - Given a trace of a multi-step run (an ordered list of events — see "What a trace is" below), narrate the run out loud: "iteration 1, the model called `calculator(expression='17**2 - 1')`, got `288`; iteration 2, it called `lookup(key='288')`, got a city; iteration 3, it returned a final answer; terminated `natural`."
   - Identify, for each event, *which kind* it is — a model call, a tool call, a tool result, or a termination event — and where one iteration ends and the next begins.
   - Read the **intermediate state** the trace carries: the running message history, cumulative token usage, per-call latency, and the arguments the model chose for each tool. Emphasize that the *arguments* are often where the interesting information is — the model's choices, not just the call counts.
   - Distinguish a **trace** (the ordered record of *what happened* in one run) from a **log line** (one event) and from the `RunResult` (the loop's *summary* of the run). A trace sits between raw prints and the summary: structured, complete, and replayable on the page.

2. **Locate where a failure occurred from the trace alone — without re-running the agent.** Concretely:
   - Given a trace of a *failed or wrong* run, point to the exact event where things went off the rails, and classify the failure by its trace signature:
     - **Tool error** — a `tool_result` with `is_error: true` (the L07 exception-to-`tool_result` conversion, or a structured error the tool returned). The trace shows the model's *next* move: did it recover, retry, or give up?
     - **Wrong tool arguments** — the call succeeded but the model passed bad args (wrong key, malformed expression). The tool result looks "fine" but is answering the wrong question. This is the hardest to spot and the best argument for tracing *arguments*, not just call names.
     - **Runaway loop** — the same `(tool_name, args)` pair repeating across iterations, ending in `max_steps`. The trace makes the repetition visible at a glance.
     - **Premature termination** — `natural` termination with a final answer that's wrong or incomplete, because the model thought it was done when it wasn't.
   - State the headline skill plainly: **a good trace lets you find the failure by reading, not by re-running.** Re-running a nondeterministic agent to "reproduce" a bug is slow and unreliable; the trace is the reproduction.

3. **Instrument a hand-rolled agent loop to emit a useful trace.** Concretely:
   - Add structured event emission to the L07 loop at the natural boundaries: before/after each model call, before/after each tool call, and at termination. Each event is a small typed record (a dict or — preferred for teaching the project's typed style — a Pydantic model / `TypedDict`), not a free-text string.
   - Decide *which fields make a trace useful* and defend the list: an ordering key (sequence index and/or timestamp), an event type, the iteration number, the tool name and arguments, the result (or `is_error` + error content), token usage, and latency. Tie each field back to a question it answers ("why is this slow?" → latency; "why did it loop?" → repeated args; "why did it cost that much?" → per-call tokens).
   - Include a **run identifier** so events from one run can be told apart from another's when traces are collected together — the minimum needed to make objective 4's two-trace comparison possible.
   - Contrast **structured** tracing (machine-readable records you can filter, diff, and later feed to eval) with the **`print()` debugging** from L07 (human-readable, ephemeral, un-greppable at scale). Land *why* structured wins the moment you have more than one run to look at.
   - Keep the instrumentation a thin wrapper around the loop, not a rewrite of it — the L07 control flow does not change; L08 only adds observation. **Decided:** the `TraceEvent` type lives in the shared `common/tracing.py` module, with an approximate, LangSmith-shaped schema and a `RunResult.trace: list[TraceEvent]` return shape (see *Decided trace schema* below), so L09 and the later LangGraph lessons import it rather than redefine it.

4. **Compare two traces of the same task to spot what changed.** Concretely:
   - Run the *same task twice* (or run it once on each of two models, or before/after a prompt tweak) and diff the two traces: did the tool-call sequence change, did the arguments change, did an extra iteration appear, did a new error show up, did token/latency move?
   - Explain *why this matters for agents specifically*: the loop is **non-deterministic** — the same task can take a different path on each run (L07 flagged this as a "variance budget"). A diff separates the *signal* (a real behavior change, e.g. a regression introduced by a prompt edit) from the *noise* (run-to-run variation that means nothing).
   - Use a trace diff to answer a concrete before/after question — e.g. "did tightening the system prompt actually stop the runaway loop, or did I just get a lucky run?" — and articulate why a single run can't answer it but a comparison across runs (ideally several) can.
   - Recognize this as the seed of evaluation: comparing runs to flag regressions is exactly the discipline L09 formalizes into an eval set. <!-- *NEED INPUT*: confirm whether the two-trace comparison is done by eye on two printed traces (cheaper, fits the time budget) or with a tiny helper that diffs two event lists (reinforces "trace is data"). Recommendation: show it by eye first, then a ~10-line diff helper if time allows. -->

## What a trace is (vocabulary the lecture must establish)

Define these terms explicitly and reuse them verbatim through the labs and into L09:

- **Trace** — the complete, ordered record of one agent run: every model call, tool call, tool result, and termination event, with enough detail attached to reconstruct the run without re-executing it. The unit of "what the agent did."
- **Span** — one entry in a trace: a single model call, a single tool call, the loop step itself. Carries a type, an order key, and type-specific fields (tool name + args for a tool call; token usage for a model call). Use **span** consistently in prose, with a one-line note that LangSmith calls these "runs" and OpenTelemetry calls them "spans" — so students recognize the structure when they meet a real tracing tool.
- **Run identifier (`trace_id`)** — a value shared by all spans of one run, so multiple runs' traces can be stored together and still be separable. Needed for the two-trace comparison.
- **Structured trace** — spans as machine-readable records (Pydantic models / JSON-lines), as opposed to free-text `print()` output. Structured traces can be filtered, diffed, counted, and fed to evaluation; print output can't, at scale.
- **`RunResult` vs. trace** — `RunResult` (from L07) is the *summary*: final text, iteration count, termination cause. The trace is the *full record* the summary was derived from. A student should be able to point at where in the trace each `RunResult` field came from.

### Decided trace schema (approximate, LangSmith-shaped)

**Decision:** the trace format is a deliberately *approximate* match to LangSmith/LangGraph's run model — not the exact SDK, just close enough that a student who later opens a real tracing tool finds the same structure. It is authored in `common/tracing.py` (the shared `common/` layer) and imported by L09/L11.

- **`TraceEvent`** (a Pydantic model; "span" in prose) carries, roughly:
  - `run_id` — this span's id; `trace_id` — shared by all spans of one run; `parent_run_id: str | None` — nesting (mostly flat for a shallow loop).
  - `run_type: Literal["llm", "tool", "chain"]` — the categorical field, mirroring LangSmith's run types (model call / tool call / loop step).
  - `name` — e.g. `"anthropic.messages"`, `"calculator"`, `"agent_loop"`.
  - `inputs` / `outputs` — dicts; `error: str | None` for a failed span.
  - `start_time` / `end_time`; `usage` — token counts on `llm` spans (`input_tokens` / `output_tokens` / `total_tokens`).
- **Return shape:** `RunResult` gains a **`trace: list[TraceEvent]`** field — one return object, flat ordered list sharing a `trace_id`. (Chosen over a `(RunResult, trace)` pair for simplicity; the trace is right there for L09 to consume.)
- **On-disk:** a `.to_jsonl()` helper (one span per line) gives the compare-two-runs lab a file format that also resembles a real trace export.
- These names (`run_type` `llm`/`tool`/`chain`, token `usage`) reappear natively in L11's LangChain messages and graph trace — that recognition *is* the payoff. Exact field-name fidelity to the current LangSmith version is explicitly **not** required; approximate structure is.

## Main points the lecture should land

- **A trace is the durable memory of an ephemeral run.** The agent loop runs and exits; without a trace, all you keep is the final answer and whatever scrolled past in the console. The trace is what lets you answer "what did it *do*?" an hour, a day, or a hundred runs later. This is the whole reason the lesson exists — say it first and say it plainly.
- **You debug agents by reading, not by re-running.** A normal program is deterministic: re-run it and the bug reproduces. An agent is not — re-running can hide the bug or produce a *different* bug. The trace is the reproduction. Teach "read the trace" as the first move when an agent misbehaves, before "run it again."
- **Arguments are where the truth is.** Call counts tell you *how much*; arguments tell you *what the model was thinking*. A run that "called the lookup tool 3 times" is ambiguous; a run that "called `lookup('288')`, `lookup('289')`, `lookup('290')`" is obviously a fumbling search. Instrument arguments, and read them first.
- **Structured beats printed the moment you have two runs.** One run, a `print()` is fine. Two runs you need to compare — or a hundred runs you need to filter — and free text collapses. The jump from print to structured event is the single most important instrumentation move in the lesson; motivate it with a concrete "now compare these two runs" moment, not as a style preference.
- **The trace is L09's input.** Tracing is not a standalone nicety; it is the data layer evaluation runs on. Every field worth tracing is a field eval might score. Frame L08 as "produce the record" and L09 as "judge the record" so students see the pair.
- **Instrumentation is a wrapper, not a rewrite.** The L07 loop's control flow is correct and untouched. Tracing observes it from the outside — emit an event at each boundary. If students find themselves changing *how the loop decides things* to add tracing, they've conflated observation with control; pull them back.
- **Hosted tracers exist; you're learning the concept first.** Real teams often use a managed tracing backend (named as a forward pointer, not taught here). Learning to emit and read a trace by hand means students will understand what those tools show them, instead of treating the dashboard as magic. The framework's built-in tracing (a reason to adopt one, per L07 objective 4) becomes legible because they built the hand-rolled version once.

## Common student confusions to watch for

- *"Tracing is just logging."* Related, but not the same. Logging is unstructured, human-oriented, and per-line. A trace is structured, ordered, run-scoped, and built to be read *as a whole* and diffed against another run. A pile of log lines is not a trace until it has order, structure, and a run identifier.
- *"I'll just re-run it to see what went wrong."* The agent is non-deterministic — re-running may not reproduce the failure, and may introduce a new one. The trace of the failing run is the evidence; capture it, don't chase it.
- *"More fields is always better."* No — a trace bloated with every internal variable is as unreadable as no trace. Trace the fields that answer a question (objective 3). Everything else is noise that costs storage and attention. <!-- *NEED INPUT*: decide how hard to push trace minimalism vs. completeness for a first lesson. Recommendation: bias toward a small, defensible field set and name "what to leave out" explicitly. -->
- *"The two traces are different, so I broke something."* Maybe — or maybe that's just run-to-run variance on a non-deterministic loop. A single differing run proves nothing; you need to know what variation is normal before you call a difference a regression. This is precisely why L09 moves from one comparison to a *set* of cases.
- *"The trace shows the tool returned successfully, so that step was fine."* Not necessarily — the call can succeed with *wrong arguments* and return a perfectly valid-looking result to the wrong question. Reading the arguments, not just the success flag, is the skill.
- *"Tracing changes what my agent does."* It shouldn't. If adding a trace changed the run's behavior, the instrumentation leaked into the control flow. Observation is read-only with respect to the loop's decisions.

## Bridge to L09

L09 (Evaluation: first pass) builds *directly* on the artifacts L08 produces. Its subgoals name L08 explicitly: "design eval cases that target failure modes already seen in **traces from L08**," and "compare two runs of the same task to flag regressions" — the same two-trace comparison students practice in L08 objective 4, scaled up from an eyeball diff to a repeatable eval set.

The concrete handoff: at the end of L08, students have (1) a hand-rolled loop that emits a structured trace, (2) the skill of reading a trace to locate a failure, and (3) a first taste of comparing two runs. L09 turns the *ad-hoc* failure-spotting into a *deliberate* practice — collect the failure modes seen in traces, write cases that target them, run them across versions, and flag regressions automatically. Tracing is the observation; evaluation is the judgment built on top of it. Encourage students to keep the failure modes they find in L08 traces — those become the first eval cases in L09. **Decision:** the `TraceEvent` type is authored in `common/tracing.py` (promoted to the shared `common/` layer, not the lesson directory), so L09 imports it directly rather than re-specifying it.

## Open authoring questions

- <!-- *NEED INPUT*: estimated lecture duration — best guess 75–100 minutes including a code-along that instruments the L07 loop and a two-trace comparison. Likely one lecture; split into "read a trace / locate a failure" and "instrument / compare" if it runs long. -->
- <!-- *NEED INPUT*: which Claude model anchors the demos/labs — mirrors the L07 open question. The *trace shape* is model-agnostic, but the trace *contents* (chaining depth, runaway behavior) differ visibly between Sonnet 4.6 and Haiku 4.5. A model contrast could double as the objective-4 two-trace comparison. -->
- **Decided (trace representation):** in-memory `RunResult.trace: list[TraceEvent]`, plus a `.to_jsonl()` helper for the compare-two-runs lab. Approximate LangSmith-shaped schema (see *Decided trace schema* in "What a trace is"). L09 reuses this.
- **Decided (terminology):** call a single trace entry a **span** in prose (class `TraceEvent`, field `run_type`); note that LangSmith calls them "runs" / OpenTelemetry "spans" so the structure is recognizable later.
- <!-- *NEED INPUT*: how far to go toward industry tracing standards — name-drop OpenTelemetry / LangSmith as a forward pointer only, or show one screenshot of a hosted trace for motivation? Recommendation: name-drop plus at most one annotated screenshot; no hands-on hosted tracer in L08. -->
- **Decided (promote to `common/`):** the trace types live in the shared `common/` layer, not the lesson directory. `TraceEvent` (and any emit helpers) go in `common/tracing.py`, so L09 and the later LangGraph lessons import the same type instead of redefining it. Stage 2 authors the module there.
- **Decided (shared tools):** L08 reuses L07's tools (`calculator`, `lookup`, `flaky_fetch` with its four URL behaviors), available from `common/tools.py` so every lesson imports the same tools. `flaky_fetch`'s built-in failure modes give objective 2 (locate-the-failure) a ready-made set of trace signatures to read.
- **Decided (inline-build vs. reference, important pedagogy):** L07 *keeps* the loop and tools built **inline** in its notebooks/labs — students hand-build the loop, and hiding it behind an import would defeat L07's entire point. The `common/` modules (`common/agent_loop.py` as `run()` → `RunResult`, `common/tools.py`) are the **canonical reference version** of the *same* code, which L08 and later lessons import so they don't re-derive it. This mirrors L07's existing demo pattern of keeping a "completed version in a sibling file." So the work is **not** "lift the code out of L07" — it's "*also* provide a reference copy in `common/`," kept in sync with what L07 teaches. <!-- *NEED INPUT*: confirm who owns authoring the `common/agent_loop.py` + `common/tools.py` reference modules and keeping them consistent with L07's inline build — most likely the stage-2 pass for L08, since L08 is the first lesson that needs to *import* them. -->
  - Verify before stage 2 that L08's imported loop is behaviorally identical to L07's inline one, so a trace of the `common/` loop matches what students saw in L07.
- <!-- *NEED INPUT*: overlap check with L07 — L07's optional bridge demo already converts one `print()` into a structured event dict. Confirm L08 opens by *reinforcing and extending* that beat (not re-teaching the loop), and that L07's bridge demo stays a teaser rather than the full instrumentation. -->
