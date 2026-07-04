# L12: What an agent generates — state, logs, traces & extracts

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (lesson-plan row L12).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).
> Preceding lesson: [L11 Shallow agents in LangGraph](../L11/objectives.md). Following lesson: L13 Evaluation: first pass (roadmap not yet written). (Its subject is still the hand-rolled loop from [L10](../L10/objectives.md), which L11 rebuilt as a one-liner — L12 instruments that same loop.)

> **Framing (read first).** This lesson is titled for the whole inventory of what an
> agent run produces, but its **center of gravity is tracing** (objectives 1–5) —
> because the trace is the durable artifact L13 (evaluation) consumes. The opening
> taxonomy (objective 6, taught *first* in delivery order) exists to place tracing among
> the other things a run generates and to draw one hard boundary: the **observability
> plane** (state · logs · traces — *what the agent did*, for you to debug and evaluate)
> is separate from the **data plane** (extracts / new records — *what the agent made*,
> persisted to a database or object store). Don't cross the streams: a trace is not a
> datastore, and a datastore is not a trace.

## Where this lesson sits

By L10, students have built a working **model → tool → model** loop in plain Python — `agent_loop.run(...)` returning a `RunResult` carrying `final_text`, `iterations`, and a `termination` cause (`"natural"`, `"max_steps"`, …). They have also already seen the *seed* of this lesson: L10's loop printed one line per iteration (iteration number, tool calls requested, tool results, cumulative tokens, latency), and L10 explicitly named that print-wrapper a **"minimum-viable trace."** L10's optional bridge demo went one step further and replaced a `print()` with a structured event dict appended to a list.

L12 picks up exactly there. The hand-rolled loop *did* something on every run — called the model, dispatched tools, hit a termination condition — but unless you were watching the console live, that "something" vanished the moment the run ended. **A trace is the durable, structured record of what happened, so you can read the run after the fact instead of guessing.** This lesson teaches students to (1) *read* a trace and reconstruct what the agent did, (2) *locate a failure* from the trace alone, (3) *instrument* their own L10 loop to emit a useful trace, and (4) *compare two traces* of the same task to see what changed between runs.

This is a turning point in the course's arc. Up to here, the agent has been something you *build*; from here on it is also something you *observe and judge*. L12 produces the raw material — the trace — that L13 (evaluation) turns into a graded judgment. Tracing without evaluation tells you *what happened*; evaluation without tracing tells you *that something is wrong but not where*. The two are a pair, and L12 comes first because you cannot evaluate a run you cannot read.

L12 is **concept-first, then tooled.** Students *first* instrument the same hand-rolled loop from L10 and read the trace themselves — so the *concept* of a trace is never hidden behind a product — and *then* graduate to a **real observability tool, self-hosted Langfuse**, where they see the very same spans rendered in a dashboard (objective 5). The hand-rolled trace is the teaching artifact; Langfuse is where students learn that the structure they built by hand is exactly what the industry uses. **Decided:** the hosted tracer for this course is **self-hosted Langfuse** — open-source (MIT), run as one shared instructor instance the whole cohort points at, so there are no per-student signups or seat costs (see [docs/classroom-llm-management.md](../../../classroom-llm-management.md) for the infra). Students never depend on a paid SaaS account, and a keyless/offline run still works on the hand-rolled trace alone.

## What a run generates: the two planes (the lesson's organizing map)

Before any tracing mechanics, the lecture opens by inventorying **everything a single agent
run produces** and sorting it onto two planes. This map is the reason the lesson is titled the
way it is, and it makes the tracing objectives (1–5) land as *one corner of a bigger picture*
rather than an isolated topic.

**Observability plane — *what the agent did* (for you, the developer, to read):**

- **State** — the agent's **live working memory**: the message history the loop grows turn by
  turn, plus any scratchpad the model reads back. It is **in-memory, mutating, and consumed by
  the next step** — the model's actual input on every iteration. It is ephemeral by default
  (gone when the process exits) unless you deliberately snapshot it. A trace is, in large part,
  *state captured over time*.
- **Logs** — the **human-readable play-by-play**, one line per event (L10's `print()` stream).
  Streamed, unstructured, fine for one live run — collapses the moment you have two runs to
  compare. Medium permanence at best.
- **Traces** — the **durable, structured, run-scoped record**: every model call, tool call, and
  result, ordered and keyed by a shared `trace_id`, built to be filtered, diffed, and fed to
  evaluation. This is the artifact the lesson spends most of its time on and the one L13 grades.

  These three sit on a single **axis of increasing permanence**: live state → streamed logs →
  durable trace. All three answer *"what did the run do?"* and are consumed by **developers and
  the eval harness** — never by the product's end users.

**Data plane — *what the agent made* (the deliverable, for downstream consumers):**

- **Extracts / new records** — the **hard data an agent produces as its actual output**:
  extracted fields, generated records, files, computed results — the business artifact the run
  exists to create. This does **not** belong in the trace. When a run produces hard data, that
  data is **persisted to its proper home — a database (rows/documents) or an object store like
  S3 (files/blobs)** — with its own schema, retention, and downstream consumers. It is durable,
  business-owned, and read by systems and people who never look at a trace.

**The one boundary to teach (and the common mistake):** keep the two planes separate. Do **not**
stuff extracted business records into trace spans (your tracer is not your database — wrong
retention, wrong query model, wrong access controls), and do **not** treat your trace store as
the system of record for the data your agent produces (a trace is sampled, TTL'd observability,
not durable business data). This lesson teaches the boundary **conceptually** — where each
artifact goes and why — and does the hands-on work on the trace; a real persistence exercise
(writing extracts to a DB/S3) is out of scope for the mini budget and is flagged as such.

## Prerequisites

Students arriving at L12 should already be able to:

- Build and run a model→tool→model loop in plain Python: call the model, detect a `tool_use` block, dispatch the tool, append a matching `tool_result`, and loop until termination (L10, objective 1). L12 instruments *this* loop — a student who cannot run it cannot trace it.
- Name the termination conditions and read a `RunResult`'s `termination` cause — `natural` vs. `max_steps`, with token-budget and loop-detection as sketched extensions (L10, objective 2). The termination cause is one of the most important fields a trace records.
- Recognize the three loop-level tool-failure modes — a tool raises, a tool returns a structured error result, a tool returns malformed output — and that the loop's default is to convert a failure into a `tool_result` with `is_error: true` (L10, objective 3). These are exactly the failure signatures students will hunt for in a trace.
- Read the per-iteration print output from L10's loop (iteration number, tool calls, tool results, tokens, latency). L12 turns that ephemeral print stream into a durable, structured trace.

If a student is shaky on the L10 loop itself, redirect to the L10 labs before continuing — L12 assumes a running loop as its subject and adds *observation*, not new control flow.

## Learning objectives

By the end of L12, a student should be able to:

1. **Read a trace of an agent run and reconstruct what the agent did.** Concretely:
   - Given a trace of a multi-step run (an ordered list of events — see "What a trace is" below), narrate the run out loud: "iteration 1, the model called `calculator(expression='17**2 - 1')`, got `288`; iteration 2, it called `lookup(key='288')`, got a city; iteration 3, it returned a final answer; terminated `natural`."
   - Identify, for each event, *which kind* it is — a model call, a tool call, a tool result, or a termination event — and where one iteration ends and the next begins.
   - Read the **intermediate state** the trace carries — and name it as *state*, the first artifact from the taxonomy: the **running message history** (the model's actual input each turn, grown turn by turn), cumulative token usage, per-call latency, and the arguments the model chose for each tool. Make the connection explicit: the trace is largely *the live state captured over time*, so reading a trace **is** reading the state the loop built up. Emphasize that the *arguments* and the *evolving message history* are where the interesting information is — the model's choices and what it was looking at, not just the call counts.
   - Distinguish a **trace** (the ordered record of *what happened* in one run) from a **log line** (one event) and from the `RunResult` (the loop's *summary* of the run). A trace sits between raw prints and the summary: structured, complete, and replayable on the page.

2. **Locate where a failure occurred from the trace alone — without re-running the agent.** Concretely:
   - Given a trace of a *failed or wrong* run, point to the exact event where things went off the rails, and classify the failure by its trace signature:
     - **Tool error** — a `tool_result` with `is_error: true` (the L10 exception-to-`tool_result` conversion, or a structured error the tool returned). The trace shows the model's *next* move: did it recover, retry, or give up?
     - **Wrong tool arguments** — the call succeeded but the model passed bad args (wrong key, malformed expression). The tool result looks "fine" but is answering the wrong question. This is the hardest to spot and the best argument for tracing *arguments*, not just call names.
     - **Runaway loop** — the same `(tool_name, args)` pair repeating across iterations, ending in `max_steps`. The trace makes the repetition visible at a glance.
     - **Premature termination** — `natural` termination with a final answer that's wrong or incomplete, because the model thought it was done when it wasn't.
   - State the headline skill plainly: **a good trace lets you find the failure by reading, not by re-running.** Re-running a nondeterministic agent to "reproduce" a bug is slow and unreliable; the trace is the reproduction.

3. **Instrument a hand-rolled agent loop to emit a useful trace.** Concretely:
   - Add structured event emission to the L10 loop at the natural boundaries: before/after each model call, before/after each tool call, and at termination. Each event is a small typed record (a dict or — preferred for teaching the project's typed style — a Pydantic model / `TypedDict`), not a free-text string.
   - Decide *which fields make a trace useful* and defend the list: an ordering key (sequence index and/or timestamp), an event type, the iteration number, the tool name and arguments, the result (or `is_error` + error content), token usage, and latency. Tie each field back to a question it answers ("why is this slow?" → latency; "why did it loop?" → repeated args; "why did it cost that much?" → per-call tokens).
   - Include a **run identifier** so events from one run can be told apart from another's when traces are collected together — the minimum needed to make objective 4's two-trace comparison possible.
   - Contrast **structured** tracing (machine-readable records you can filter, diff, and later feed to eval) with the **`print()` debugging** from L10 (human-readable, ephemeral, un-greppable at scale). Land *why* structured wins the moment you have more than one run to look at.
   - Keep the instrumentation a thin wrapper around the loop, not a rewrite of it — the L10 control flow does not change; L12 only adds observation. **Decided:** the `TraceEvent` type lives in the shared `common/tracing.py` module, with an approximate, OpenTelemetry/Langfuse-shaped schema and a `RunResult.trace: list[TraceEvent]` return shape (see *Decided trace schema* below), so L13 and the later LangGraph lessons import it rather than redefine it.

4. **Compare two traces of the same task to spot what changed.** Concretely:
   - Run the *same task twice* (or run it once on each of two models, or before/after a prompt tweak) and diff the two traces: did the tool-call sequence change, did the arguments change, did an extra iteration appear, did a new error show up, did token/latency move?
   - Explain *why this matters for agents specifically*: the loop is **non-deterministic** — the same task can take a different path on each run (L10 flagged this as a "variance budget"). A diff separates the *signal* (a real behavior change, e.g. a regression introduced by a prompt edit) from the *noise* (run-to-run variation that means nothing).
   - Use a trace diff to answer a concrete before/after question — e.g. "did tightening the system prompt actually stop the runaway loop, or did I just get a lucky run?" — and articulate why a single run can't answer it but a comparison across runs (ideally several) can.
   - Recognize this as the seed of evaluation: comparing runs to flag regressions is exactly the discipline L13 formalizes into an eval set. **Decided:** do the two-trace comparison **by eye first** on two printed traces (cheap, fits the time budget), then introduce a **~10-line diff helper** over the two event lists to reinforce "trace is data" — the helper is the upgrade once students have felt the eyeball version.

5. **Send a trace to a real observability tool (self-hosted Langfuse) and read it there.** Concretely:
   - Point the loop at the cohort's shared **self-hosted Langfuse** instance (a base URL + project keys read through `common/config.py`, never hard-coded) and emit the *same* run as a Langfuse trace — so students see the hand-rolled `TraceEvent` spans they just built rendered in a real dashboard: a timeline of spans, per-call token usage and cost, latency, inputs/outputs, and errors.
   - Map the hand-rolled vocabulary onto Langfuse's so the structures line up explicitly: a Langfuse **trace** = one run (shares the `trace_id`); a Langfuse **observation** = one span, typed **GENERATION** for a model call (carries model, token `usage`, cost) and **SPAN** for a tool call or loop step. This is the same `run_type: llm | tool | chain` distinction, in the tool's own words.
   - Do the objective-2 (locate-a-failure) and objective-4 (compare-two-runs) tasks *again* in the Langfuse UI — filter to the failing run, expand the offending span, diff two runs side by side — and feel how a real tool makes the same reading faster at scale, while understanding exactly what it's showing because they built the minimal version first.
   - Keep this graceful: the export is an *additive* step. A student without the Langfuse instance configured still completes objectives 1–4 on the in-memory/`.to_jsonl()` trace; Langfuse is the "now see it in the real tool" payoff, not a hard dependency. **Decided:** the cohort uses **one shared instructor-run Langfuse instance** (zero per-student setup — students get a URL + project key through `common/config.py`), with a **local-Docker instance documented as the fallback** for solo/self-paced learners. Infra in [docs/classroom-llm-management.md](../../../classroom-llm-management.md).
   - Mechanics: instrument via the `langfuse` SDK (added as a project dep) or by exporting the OTel-shaped spans over OTLP, since Langfuse ingests OpenTelemetry — the approximate-OTel trace schema (below) was chosen partly to make this export natural.

6. **Sort what an agent generates onto the right plane, and keep hard data out of the trace.** Taught **first** in delivery order (it is the lesson's opening map) but numbered last so objectives 1–5 — the tracing core — keep their identifiers stable for the labs and demos. Concretely:
   - Name the four artifacts a run produces and which plane each lives on: **state** (live, in-memory), **logs** (streamed, human-readable), **traces** (durable, structured, run-scoped) — all *observability*, all answering "what did the run do?" — versus **extracts / new records** (the hard data the run produces), which are *data*, answering "what did the run make?".
   - Place the three observability artifacts on the **increasing-permanence axis** (state → logs → trace) and articulate that a trace is largely *state captured durably over time*, which is why reading a trace (objective 1) is reading the state the loop built.
   - State the **plane boundary** as a rule with a reason on each side: extracted business data goes to a **database or object store (S3)** — its own schema, retention, and consumers — **not** into trace spans (a tracer has the wrong retention, query model, and access controls to be a datastore); and the **trace store is not the system of record** for that data (traces are sampled and TTL'd observability, not durable business data). Give the concrete failure of crossing the streams: an agent that writes its extracted records *only* into its trace has no queryable datastore and will lose the data when traces expire; an agent that treats Langfuse as its database can't serve, join, or back up that data.
   - Keep this **conceptual** — a diagram/whiteboard beat plus a tiny illustrative sketch (e.g. one line that appends a `TraceEvent` for observability *next to* a separate `save_record(...)` call that would write to a DB/S3), **not** a real persistence lab. Wiring an actual database or S3 client is out of scope for the mini time budget; name that omission explicitly so students read it as a deliberate boundary, not a gap. **Decided:** conceptual-only for this lesson; a hands-on "persist the extract" exercise is a candidate for a later data/RAG lesson (L20/L21) or a project brief, not L12.

## What a trace is (vocabulary the lecture must establish)

Define these terms explicitly and reuse them verbatim through the labs and into L13:

- **Trace** — the complete, ordered record of one agent run: every model call, tool call, tool result, and termination event, with enough detail attached to reconstruct the run without re-executing it. The unit of "what the agent did."
- **Span** — one entry in a trace: a single model call, a single tool call, the loop step itself. Carries a type, an order key, and type-specific fields (tool name + args for a tool call; token usage for a model call). Use **span** consistently in prose, with a one-line note that OpenTelemetry calls these "spans", Langfuse calls them "observations" (a model-call span is a Langfuse **GENERATION**; a tool/loop span is a Langfuse **SPAN**), and LangSmith calls them "runs" — so students recognize the structure when they meet a real tracing tool (they meet Langfuse in objective 5).
- **Run identifier (`trace_id`)** — a value shared by all spans of one run, so multiple runs' traces can be stored together and still be separable. Needed for the two-trace comparison.
- **Structured trace** — spans as machine-readable records (Pydantic models / JSON-lines), as opposed to free-text `print()` output. Structured traces can be filtered, diffed, counted, and fed to evaluation; print output can't, at scale.
- **`RunResult` vs. trace** — `RunResult` (from L10) is the *summary*: final text, iteration count, termination cause. The trace is the *full record* the summary was derived from. A student should be able to point at where in the trace each `RunResult` field came from.
- **State** — the agent's live, in-memory working set (the growing message history the loop feeds back to the model each turn). Distinct from a trace: state is *mutating and consumed by the loop*; a trace is *append-only and read by you*. The trace is state serialized over time — reading one is reading the other.
- **Extracts / new records (data plane)** — the hard data the run produces as its deliverable (extracted fields, generated records, files). Distinct from all three observability artifacts: it is the *product*, not a lens on the run, and it belongs in a **database or object store (S3)**, not in the trace. Named here so students hold the boundary — trace ≠ datastore — verbatim through the lesson.

### Decided trace schema (approximate, OpenTelemetry / Langfuse-shaped)

**Decision:** the trace format is a deliberately *approximate* match to the OpenTelemetry span model that Langfuse (objective 5's tool) ingests — not an exact SDK schema, just close enough that a student who opens Langfuse (or any OTel-based tracer) finds the same structure, and close enough that exporting over OTLP is a natural step. It is authored in `common/tracing.py` (the shared `common/` layer) and imported by L13/L11.

- **`TraceEvent`** (a Pydantic model; "span" in prose) carries, roughly:
  - `run_id` — this span's id; `trace_id` — shared by all spans of one run; `parent_run_id: str | None` — nesting (mostly flat for a shallow loop).
  - `run_type: Literal["llm", "tool", "chain"]` — the categorical field; maps to Langfuse observation types (`llm` → **GENERATION**, `tool`/`chain` → **SPAN**) and to OTel span kinds.
  - `name` — e.g. `"anthropic.messages"`, `"calculator"`, `"agent_loop"`.
  - `inputs` / `outputs` — dicts; `error: str | None` for a failed span.
  - `start_time` / `end_time`; `usage` — token counts on `llm` spans (`input_tokens` / `output_tokens` / `total_tokens`), which Langfuse renders as token usage + cost on a GENERATION.
- **Return shape:** `RunResult` gains a **`trace: list[TraceEvent]`** field — one return object, flat ordered list sharing a `trace_id`. (Chosen over a `(RunResult, trace)` pair for simplicity; the trace is right there for L13 to consume.)
- **On-disk / export:** a `.to_jsonl()` helper (one span per line) for the compare-two-runs lab, and the same spans export to the cohort's self-hosted Langfuse via the `langfuse` SDK / OTLP (objective 5).
- These names (`run_type` `llm`/`tool`/`chain`, token `usage`) reappear natively in L11's LangChain/LangGraph trace *and* in the Langfuse UI — that recognition *is* the payoff. Exact field-name fidelity to any one vendor is explicitly **not** required; approximate OTel-ish structure is.

## Main points the lecture should land

- **A run generates two kinds of thing, on two planes — say this first of all.** *Observability* (state · logs · traces — what the agent *did*, read by you and the eval harness) is separate from *data* (extracts / new records — what the agent *made*, persisted to a database or S3 for downstream consumers). The whole lesson lives in the trace corner of the observability plane; open with the map so students know where they are, and close (objective 6 / Demo 7) by drawing the boundary: **a trace is not a datastore, and a datastore is not a trace.**
- **A trace is the durable memory of an ephemeral run.** The agent loop runs and exits; without a trace, all you keep is the final answer and whatever scrolled past in the console. The trace is what lets you answer "what did it *do*?" an hour, a day, or a hundred runs later. This is the whole reason the lesson exists — say it first and say it plainly. (And a trace is largely the agent's **state** — its message history — captured durably over time.)
- **You debug agents by reading, not by re-running.** A normal program is deterministic: re-run it and the bug reproduces. An agent is not — re-running can hide the bug or produce a *different* bug. The trace is the reproduction. Teach "read the trace" as the first move when an agent misbehaves, before "run it again."
- **Arguments are where the truth is.** Call counts tell you *how much*; arguments tell you *what the model was thinking*. A run that "called the lookup tool 3 times" is ambiguous; a run that "called `lookup('288')`, `lookup('289')`, `lookup('290')`" is obviously a fumbling search. Instrument arguments, and read them first.
- **Structured beats printed the moment you have two runs.** One run, a `print()` is fine. Two runs you need to compare — or a hundred runs you need to filter — and free text collapses. The jump from print to structured event is the single most important instrumentation move in the lesson; motivate it with a concrete "now compare these two runs" moment, not as a style preference.
- **The trace is L13's input.** Tracing is not a standalone nicety; it is the data layer evaluation runs on. Every field worth tracing is a field eval might score. Frame L12 as "produce the record" and L13 as "judge the record" so students see the pair.
- **Instrumentation is a wrapper, not a rewrite.** The L10 loop's control flow is correct and untouched. Tracing observes it from the outside — emit an event at each boundary. If students find themselves changing *how the loop decides things* to add tracing, they've conflated observation with control; pull them back.
- **You build the trace by hand, then meet the real tool.** Real teams use a managed tracing backend; in this course that's **self-hosted Langfuse** (objective 5). Learning to emit and read a trace by hand *first* means students understand what Langfuse shows them instead of treating the dashboard as magic — when they open it, the spans, token usage, and errors are the exact structure they just built. "Concept first, then tooled" is the spine of the lesson, and it's also why the L11 LangGraph traces (which land in the *same* Langfuse) feel familiar rather than new.

## Common student confusions to watch for

- *"Tracing is just logging."* Related, but not the same. Logging is unstructured, human-oriented, and per-line. A trace is structured, ordered, run-scoped, and built to be read *as a whole* and diffed against another run. A pile of log lines is not a trace until it has order, structure, and a run identifier.
- *"I'll just re-run it to see what went wrong."* The agent is non-deterministic — re-running may not reproduce the failure, and may introduce a new one. The trace of the failing run is the evidence; capture it, don't chase it.
- *"More fields is always better."* No — a trace bloated with every internal variable is as unreadable as no trace. Trace the fields that answer a question (objective 3). Everything else is noise that costs storage and attention. **Decided:** bias toward a **small, defensible field set** (the schema in "What a trace is") and **name what to leave out explicitly** — e.g. full prompt bodies, raw tracebacks, every intermediate variable — so students learn minimalism as a deliberate choice, not an omission.
- *"The two traces are different, so I broke something."* Maybe — or maybe that's just run-to-run variance on a non-deterministic loop. A single differing run proves nothing; you need to know what variation is normal before you call a difference a regression. This is precisely why L13 moves from one comparison to a *set* of cases.
- *"The trace shows the tool returned successfully, so that step was fine."* Not necessarily — the call can succeed with *wrong arguments* and return a perfectly valid-looking result to the wrong question. Reading the arguments, not just the success flag, is the skill.
- *"Tracing changes what my agent does."* It shouldn't. If adding a trace changed the run's behavior, the instrumentation leaked into the control flow. Observation is read-only with respect to the loop's decisions.
- *"I'll just save the agent's output in the trace."* No — that crosses the plane boundary. A trace is observability: sampled, TTL'd, keyed for debugging. The hard data your agent produces is a *deliverable* — it belongs in a database or object store with its own schema and retention. Put extracted records in the trace and you have no queryable datastore and lose the data when traces expire; treat the trace store as your database and you can't serve, join, or back up the data. Observe the run in the trace; persist the product to the datastore.

## Bridge to L13

L13 (Evaluation: first pass) builds *directly* on the artifacts L12 produces. Its subgoals name L12 explicitly: "design eval cases that target failure modes already seen in **traces from L12**," and "compare two runs of the same task to flag regressions" — the same two-trace comparison students practice in L12 objective 4, scaled up from an eyeball diff to a repeatable eval set.

The concrete handoff: at the end of L12, students have (1) a hand-rolled loop that emits a structured trace, (2) the skill of reading a trace to locate a failure, and (3) a first taste of comparing two runs. L13 turns the *ad-hoc* failure-spotting into a *deliberate* practice — collect the failure modes seen in traces, write cases that target them, run them across versions, and flag regressions automatically. Tracing is the observation; evaluation is the judgment built on top of it. Encourage students to keep the failure modes they find in L12 traces — those become the first eval cases in L13. **Decision:** the `TraceEvent` type is authored in `common/tracing.py` (promoted to the shared `common/` layer, not the lesson directory), so L13 imports it directly rather than re-specifying it.

## Open authoring questions

- **Decided (lecture duration):** **~75–100 minutes**, one lecture, including a code-along that instruments the L10 loop and a two-trace comparison. If it runs long, split into "read a trace / locate a failure" and "instrument / compare (+ Langfuse export)". The objective-5 Langfuse step adds ~10–15 minutes and can be trimmed to a demo if time is tight.
- **Decided (anchor model):** Claude **Sonnet 4.6**, inheriting the L01–L10 precedent so the traced loop behaves identically to the one students built in L10. The trace *shape* is model-agnostic regardless.
- **Decided (trace representation):** in-memory `RunResult.trace: list[TraceEvent]`, plus a `.to_jsonl()` helper for the compare-two-runs lab. Approximate OpenTelemetry/Langfuse-shaped schema (see *Decided trace schema* in "What a trace is"). L13 reuses this.
- **Decided (terminology):** call a single trace entry a **span** in prose (class `TraceEvent`, field `run_type`); note that OpenTelemetry says "spans", Langfuse says "observations" (GENERATION/SPAN), LangSmith says "runs" — so the structure is recognizable later.
- **Decided (hosted tracer = self-hosted Langfuse, hands-on):** L12 includes a real hands-on observability step on **self-hosted Langfuse** (objective 5), not just a name-drop — students export their hand-rolled trace and read it in the dashboard. It's an *additive* step gated on the cohort instance being configured; objectives 1–4 still stand alone on the in-memory trace. Requires the `langfuse` dependency (added via `uv add`) and a running Langfuse instance (infra in [docs/classroom-llm-management.md](../../../classroom-llm-management.md)).
- **Decided (promote to `common/`):** the trace types live in the shared `common/` layer, not the lesson directory. `TraceEvent` (and any emit helpers) go in `common/tracing.py`, so L13 and the later LangGraph lessons import the same type instead of redefining it. Stage 2 authors the module there.
- **Decided (shared tools):** L12 reuses L10's tools (`calculator`, `lookup`, `flaky_fetch` with its four URL behaviors), available from `common/tools.py` so every lesson imports the same tools. `flaky_fetch`'s built-in failure modes give objective 2 (locate-the-failure) a ready-made set of trace signatures to read.
- **Decided (inline-build vs. reference, important pedagogy):** L10 *keeps* the loop and tools built **inline** in its notebooks/labs — students hand-build the loop, and hiding it behind an import would defeat L10's entire point. The `common/` modules (`common/agent_loop.py` as `run()` → `RunResult`, `common/tools.py`) are the **canonical reference version** of the *same* code, which L12 and later lessons import so they don't re-derive it. This mirrors L10's existing demo pattern of keeping a "completed version in a sibling file." So the work is **not** "lift the code out of L10" — it's "*also* provide a reference copy in `common/`," kept in sync with what L10 teaches. **Decided:** the **L12 stage-2 pass owns** authoring `common/agent_loop.py` + `common/tools.py` (L12 is the first lesson that *imports* them) and verifying they stay behaviorally consistent with L10's inline build.
  - Verify before stage 2 that L12's imported loop is behaviorally identical to L10's inline one, so a trace of the `common/` loop matches what students saw in L10.
- **Decided (L10 overlap):** L12 opens by **reinforcing and extending** L10's optional bridge demo (the `print()` → structured-event-dict beat), **not re-teaching the loop**. L10's bridge demo stays a *teaser*; L12 delivers the full instrumentation (the `common/tracing.py` `TraceEvent`, all boundaries, plus the Langfuse export). The L10 loop itself is assumed, not re-derived.
