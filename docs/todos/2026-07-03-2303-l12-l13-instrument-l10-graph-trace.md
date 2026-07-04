# TODO — L12/L13: re-point tracing + eval onto the L10 *graph* (the "deeper" option)

**Date:** 2026-07-03
**Status:** open — proposed, not started. This is the **deeper** of the two paths flagged when L10
was regenerated as a cyclic `StateGraph` (see the completed
[L11/L10 reframe todo](2026-07-03-2151-l11-create-agent-mapping-and-l10-graph-reframe.md), "Related
(broader ripple)"). The **light** alternative — leave `common/agent_loop.py` as L12's subject and
only fix prose so it stops claiming students *built* that plain loop in L10 — is cheaper and is the
recommended stopgap. This doc specifies the deeper rework for when it's worth doing.

## Why this exists

L10 no longer teaches a plain-Python `while` loop; it teaches a ReAct **`StateGraph`** (agent node →
`route` conditional edge → `ToolNode` → `tools → agent` back-edge), inspected live with
`graph.stream(stream_mode="updates")`. But L12 (tracing) and L13 (eval) still instrument and import
the **hand-rolled loop** in `common/agent_loop.py`:

- [L1201_intro.md:16](../../src/fluffy_potato_curriculum/lessons/L12/L1201_intro.md) — *"In L10 you
  built a model→tool→model loop in plain Python… `run(...)` returning a `RunResult`."* Students never
  built that; they built a graph and never saw `run()` / `RunResult`.
- [L1202_lecture.ipynb](../../src/fluffy_potato_curriculum/lessons/L12/L1202_lecture.ipynb) — builds
  five traces by running `agent_loop.run` against a scripted `FakeModel`.

So L12/L13's "the loop you built in L10" framing is now false. The deeper fix makes the **graph** the
traced subject, so tracing and eval read the artifact students actually built.

## Current dependency web (why this pulls in L13)

The tracing/eval harness is shared `common/` code, imported across L12 **and** L13:

- `common/tracing.py` — `TraceEvent` (OTel-shaped span model), `SpanUsage`, `RunType =
  Literal["llm","tool","chain"]`. The L12 teaching artifact.
- `common/agent_loop.py` — `run(...) -> RunResult`; `RunResult.trace: list[TraceEvent]`. Emits an
  `llm`/`tool`/`chain` span at each loop boundary. **This is the plain loop L10 no longer teaches.**
- `common/evals.py` — L13's harness. `from .agent_loop import RunResult`; `Scorer.__call__(*, run:
  RunResult, example) -> EvalResult`; `tool_trajectory(run) = [span.name for span in run.trace if
  span.run_type == "tool"]`. **L13 scorers read `run.trace` directly.**

**Consequence:** you cannot change how the trace is *produced* without deciding what happens to
`RunResult` / `TraceEvent` / `run.trace`, because L13's scorers and `tool_trajectory` are written
against exactly that shape. That is the pull-in.

## Goal

L12 instruments **the L10 graph** (each node → a span) and L13 evaluates runs of **the L10 graph** —
with the by-hand→prebuilt story intact (L10 graph → L12 traces it → L13 judges it), and without
re-teaching the plain loop students never wrote.

## Recommended approach — keep the trace *schema* as the seam, swap the *producer*

Treat `TraceEvent` / `RunResult.trace` as a **stable contract** and replace only what produces it.
This keeps L13 (and the Langfuse export story) working with minimal churn:

1. **Add a graph-tracing producer in `common/`** — a function that runs the compiled L10 graph and
   returns a `RunResult`-shaped object whose `.trace` is the same ordered `list[TraceEvent]` (one
   `chain` span for the run, one `llm` span per `agent`-node visit, one `tool` span per `ToolNode`
   call). Two viable implementations:
   - **Adapt `graph.stream(stream_mode="updates")`** — map each `{node: update}` chunk to a
     `TraceEvent` (the same stream students learn from L03/L10). Pedagogically tight: "the stream you
     already watched, captured." Preferred.
   - **A LangGraph callback / `RunnableConfig` callbacks handler** — closer to how Langfuse's real
     `langchain`/`langgraph` integration hooks in; more moving parts.
2. **Keep `RunResult` and `TraceEvent` field-compatible** so `evals.py`, `tool_trajectory`, and every
   L13 scorer keep working unchanged. If a graph run can't fill a field (e.g. `iterations` → count
   `agent` spans; `termination` → `"natural"` vs `GraphRecursionError`), map it explicitly.
3. **Decide the fate of `common/agent_loop.py`.** Either (a) keep it as a secondary reference and add
   the graph producer alongside, or (b) demote it and make the graph producer canonical. Prefer (a)
   first to limit blast radius; revisit (b) once L12/L13 are green on the graph.

Rejected sub-option: reshaping `TraceEvent` to LangGraph-native event types. It ripples into every
L13 scorer and the Langfuse-export framing for little teaching gain — the OTel-shaped `TraceEvent` is
already the point of L12.

## Scope — files that will move

- **`common/`** — new graph-tracing producer (new function/module); possibly light edits to
  `tracing.py` / `agent_loop.py` docstrings; **do not** break `evals.py`'s imports.
- **L12 (~9 files)** — `L1201_intro.md`, `L1202_lecture.ipynb`, `L1203_lab_{empty,solutions}.ipynb`,
  `L1204_lecture.ipynb`, `L1205_lab_{empty,solutions}.ipynb`, `L1206_lecture.md`, `PROCTOR_NOTES.md`.
  Re-point from `agent_loop.run` to the graph producer; fix all "the loop you built in L10" prose to
  "the graph you built in L10"; refresh notebook outputs.
- **L13 (~4 files)** — `L1301_intro.md`, `L1303_lab_{empty,solutions}.ipynb`,
  `L1305_lab_{empty,solutions}.ipynb`, `PROCTOR_NOTES.md`. If the `RunResult`/`trace` contract holds,
  these are mostly prose ("the L10 loop" → "the L10 graph") + a swapped import for how a run is
  produced; scorers and `tool_trajectory` should not need logic changes.
- **Roadmaps** — check `docs/origin/lesson_roadmaps/L12/` and `L13/` still describe the subject
  correctly (L12's roadmap already says "instrument the L10 graph" in places from the earlier
  reframe; L13's was just re-spined to Langfuse-forward — reconcile, don't clobber).

## Open questions / decisions before starting

- **Stream-adapter vs. callbacks handler** for the producer (recommend the `stream_mode="updates"`
  adapter for pedagogical continuity with L03/L10).
- **Keep or demote `common/agent_loop.py`?** L13's roadmap was just re-spined to a Langfuse-forward
  hybrid; confirm whether that direction still wants a plain-loop reference at all.
- **`FakeModel` determinism holds** through the graph producer (it does for L10 — but the
  `add_messages` id-dedup gotcha means runaway/`max_steps` fixtures must script *distinct* replies;
  L12/L13's saved failure fixtures may need regenerating for the graph).
- **Interaction with the pending Langfuse-forward L13 re-spine** (commit `34ed9e5`) and the
  [LangChain notebook migration](2026-07-03-langchain-notebook-migration.md) — cheapest to fold this
  in as those land, not twice.

## Verify when done

- `grep -rin "hand-rolled\|loop in plain Python\|the loop you built" lessons/L12/ lessons/L13/`
  returns nothing that miscredits L10.
- L12 notebooks trace the **compiled graph** (spans per node), run top-to-bottom offline on
  `FakeModel`, and render clean.
- L13 eval harness runs unchanged against graph-produced `RunResult`s: `evaluate(...)` returns a pass
  rate, `tool_trajectory` still reads `run.trace`, scorers unmodified (or minimally so).
- Full gate green: `uv run ruff format && uv run ruff check && uv run pyright && uv run pytest`
  (including `tests/lessons/test_toc_anchors.py`).
- Hand-off reads cleanly: L10 (build the graph) → L12 (trace *that* graph, node = span) → L13 (judge
  runs of *that* graph).

## Out of scope

- The **light-touch** prose-only fix (that's the alternative, not this).
- Token-level streaming, Langfuse's native LangChain callback as the *only* tracer (name as "the real
  tool," keep the hand-built `TraceEvent` as the teaching artifact), and any L10 material changes.
