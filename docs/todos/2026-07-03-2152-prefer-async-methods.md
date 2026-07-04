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

## Scope / where it lands

- **`potato_llm/`** — `PotatoLLMClient` Protocol + Anthropic/OpenAI impls expose `async` call
  methods (keep a thin sync wrapper only if a specific lecture needs it).
- **`common/`** — agent loop, tool dispatch, `TraceEvent` export, eval harness all `async`.
- **Lessons** — notebooks `await` inside cells (Jupyter supports top-level `await`); labs’
  `_empty`/`_solutions` model async signatures. Introduce the async model early enough that the
  agent-arc lessons (L10–L14) can lean on it.
- **`invoke` / `ainvoke` note** — wherever a framework object's sync call first shows up
  (LangChain/LangGraph `.invoke()`, first met in L03/L04; the Anthropic/OpenAI SDKs' sync vs.
  async clients), add a **short note that both a sync (`.invoke()`) and an async (`.ainvoke()`)
  variant exist, that we default to the async one, → see K05's "why async for agents."** Keep it
  a one-liner pointer at the point of use, not a re-explanation — the reasoning lives in K05.

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
