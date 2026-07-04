# 2026-07-03 — Prefer async methods for all functions and agent-related calls

**Goal:** standardize on `async`/`await` across the curriculum's Python — teach and write
agent code async-first rather than sync-first. Every function that does (or transitively does)
I/O — LLM calls, tool execution, the agent loop, tracing exports, eval harness runs — should be
`async def` and awaited, and the `potato_llm` / `common/` seams should expose async entry points.

## Why

- **It's how real agent code is written.** Production agent frameworks (LangChain/LangGraph,
  the Anthropic/OpenAI SDKs) are async-first; concurrent tool calls, streaming, and fan-out
  parallelism all assume `await`. Teaching sync-first means re-teaching it later.
- **Concurrency is a core agent concept, not an optimization.** Parallel tool calls, running
  multiple agents/eval cases at once, and non-blocking traces are much cleaner with
  `asyncio.gather` than threads — and only reachable if the seams are async.
- **Consistency.** A half-sync/half-async codebase forces awkward `asyncio.run()` bridges and
  color-of-function friction; picking async as the default removes it.

## Where the async *concept* is taught — the `K` prework track

The async mental model is taught in **K05**, part of the new `K<NN>` prework track — see the
dedicated TODO [`2026-07-03-2211-k-prework-track.md`](2026-07-03-2211-k-prework-track.md). K05
owns the canonical **"why async for agents"** explainer (concurrent tool calls, parallel eval
cases, non-blocking traces / streaming); this TODO is only the *code* side — making the seams
and materials async-first so they can lean on that concept. This resolves the "introduce async
from L01 vs. later" question: the concept lands in K05, the seams are async from the first lesson
that uses them.

## Progress (2026-07-04): the code seams are DONE; the notebooks are deferred

Chose "seams now, notebooks later" (the notebook conversion is folded into the active
[LangChain notebook migration](2026-07-03-langchain-notebook-migration.md) so those files are
touched once, when regenerated — the "don't touch twice" call below). The **seams** landed
async-first with the existing sync names kept working, so nothing downstream broke:

- [x] **`potato_llm/`** — `chat`/`achat` on the `PotatoLLMClient` Protocol + both clients (each
      holds a lazily-built sync **and** async SDK client; shared `to_chat_response`).
- [x] **`common/`** — `agent_loop.arun`, `agent_graph.arun`/`atrace_graph` (dual-mode
      `RunnableLambda` node → same compiled graph runs `.stream` **and** `.astream`),
      `evals.aevaluate` (shared `_build_report` rollup), `FakeModel.ainvoke`. Tool dispatch and
      `TraceEvent` stay sync — pure/in-memory, no I/O to await.
- [x] **Test tooling** — `pytest-asyncio` (dev dep) with `asyncio_mode = "auto"`; async sibling
      tests for every new entry point (marker-free `async def test_*`).
- [~] **Lessons** — **started with L01** (2026-07-04). The `potato_llm` intro lessons (L01–L02) are
      *outside* the LangChain migration, so they convert safely now without collision: L01's live
      cells (`L0107`, `L0108` lab pair, `L0109`) + the `L0101` intro snippet + `PROCTOR_NOTES` now
      `await client.achat(...)`. Verified: ruff format/lint clean, every cell compiles as
      top-level-await (a keyed live restart-run-all is the remaining human check). **Next: L02**
      (same `potato_llm` pattern). L03+ stay deferred to the LangChain migration — converted as
      those notebooks regenerate, so they're touched once.
- [~] **`invoke` / `ainvoke` note** — added for L01: the `chat`/`achat` → K05 pointer at the first
      call sites (`L0101` intro, `L0107` §2). Same one-liner to add per lesson as it's converted.

## Scope / where it lands

- **`potato_llm/`** — `PotatoLLMClient` Protocol + Anthropic/OpenAI impls expose `async` call
  methods (keep a thin sync wrapper only if a specific lecture needs it). ✅ done — see above.
- **`common/`** — agent loop, tool dispatch, `TraceEvent` export, eval harness all `async`. ✅ the
  I/O-bearing producers now have async twins; pure helpers (tools, `TraceEvent`) stay sync.
- **Lessons** — notebooks `await` inside cells (Jupyter supports top-level `await`); labs’
  `_empty`/`_solutions` model async signatures. Introduce the async model early enough that the
  agent-arc lessons (L10–L14) can lean on it. ⏳ deferred to the migration.
- **`invoke` / `ainvoke` note** — wherever a framework object's sync call first shows up
  (LangChain/LangGraph `.invoke()`, first met in L03/L04; the Anthropic/OpenAI SDKs' sync vs.
  async clients), add a **short note that both a sync (`.invoke()`) and an async (`.ainvoke()`)
  variant exist, that we default to the async one, → see K05's "why async for agents."** Keep it
  a one-liner pointer at the point of use, not a re-explanation — the reasoning lives in K05.
  ⏳ deferred to the migration.

## Open questions

- **When to introduce async** — resolved: teach the *concept* in **K05** (prework track), keep
  the seams async from the first lesson that uses them.
- **"why async for agents" beat** — resolved: it lives in **K05** as the canonical explainer;
  the framework lessons carry only a short `invoke`/`ainvoke` pointer back to it (see the
  *Scope / where it lands* note above), not a re-explanation.
- Confirm interaction with the pending LangChain migration
  (`2026-07-03-langchain-notebook-migration.md`) — cheapest to bake async in as those notebooks
  are regenerated rather than touching them twice.
- Prework-track concerns (K breakout, gating, Docker stack, renumber) now live in
  [`2026-07-03-2211-k-prework-track.md`](2026-07-03-2211-k-prework-track.md).
