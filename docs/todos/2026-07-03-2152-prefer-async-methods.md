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

## Progress (2026-07-06): DONE — seams *and* notebooks converted

The seams landed async-first on 2026-07-04 (below). On **2026-07-06** the remaining notebook
conversion — which the closed LangChain migration never picked up — was done directly as its own
pass, so every lesson that makes a model/agent/eval call is now async-first end to end:

- [x] **`potato_llm/`** — `chat`/`achat` on the `PotatoLLMClient` Protocol + both clients (each
      holds a lazily-built sync **and** async SDK client; shared `to_chat_response`).
- [x] **`common/`** — `agent_loop.arun`, `agent_graph.arun`/`atrace_graph` (dual-mode
      `RunnableLambda` node → same compiled graph runs `.stream` **and** `.astream`),
      `evals.aevaluate` (shared `_build_report` rollup), `FakeModel.ainvoke`. Tool dispatch and
      `TraceEvent` stay sync — pure/in-memory, no I/O to await.
- [x] **Test tooling** — `pytest-asyncio` (dev dep) with `asyncio_mode = "auto"`; async sibling
      tests for every new entry point (marker-free `async def test_*`).
- [x] **Lessons** — **all lessons converted**. L01/L02 (2026-07-04) `await client.achat(...)`.
      L03–L08, L10–L13, L22–L23 (2026-07-06) now `await` their async twins: LangChain/agent
      `.invoke`/`.stream` → `.ainvoke`/`.astream`; the shared graph's `run`/`trace_graph` →
      `arun`/`atrace_graph` (L10/L12); the eval harness `evaluate` → `aevaluate` (L13). Lecture
      notebooks, `_empty`/`_solutions` lab pairs, intro/outline markdown, `PROCTOR_NOTES`, and the
      built `_lecture_deck.html` snippets were all updated together. Deliberately kept sync: tool
      dispatch/execution, `TraceEvent`, pure in-memory helpers, and Langfuse v4
      `dataset.run_experiment` (no async twin — its *task* callable went `async def` instead, which
      the SDK supports). Verified: ruff format/lint clean, `pyright` 0 errors, `pytest` 360 pass,
      every touched cell compiles as top-level-await, `_empty` outputs cleared. **Remaining human
      check:** a keyed live restart-run-all of the gated live cells (same open item as L01/L02).
- [x] **`invoke` / `ainvoke` note** — the short K05 pointer now lands once per lesson at its first
      framework call site (L01–L08, L10–L13, L22–L23).

## Scope / where it lands

- **`potato_llm/`** — `PotatoLLMClient` Protocol + Anthropic/OpenAI impls expose `async` call
  methods (keep a thin sync wrapper only if a specific lecture needs it). ✅ done — see above.
- **`common/`** — agent loop, tool dispatch, `TraceEvent` export, eval harness all `async`. ✅ the
  I/O-bearing producers now have async twins; pure helpers (tools, `TraceEvent`) stay sync.
- **Lessons** — notebooks `await` inside cells (Jupyter supports top-level `await`); labs’
  `_empty`/`_solutions` model async signatures. Introduce the async model early enough that the
  agent-arc lessons (L10–L14) can lean on it. ✅ done (2026-07-06) — all lessons converted.
- **`invoke` / `ainvoke` note** — wherever a framework object's sync call first shows up
  (LangChain/LangGraph `.invoke()`, first met in L03/L04; the Anthropic/OpenAI SDKs' sync vs.
  async clients), add a **short note that both a sync (`.invoke()`) and an async (`.ainvoke()`)
  variant exist, that we default to the async one, → see K05's "why async for agents."** Keep it
  a one-liner pointer at the point of use, not a re-explanation — the reasoning lives in K05.
  ✅ done — one pointer per lesson at its first framework call site.

## Open questions

- **When to introduce async** — resolved: teach the *concept* in **K05** (prework track), keep
  the seams async from the first lesson that uses them.
- **"why async for agents" beat** — resolved: it lives in **K05** as the canonical explainer;
  the framework lessons carry only a short `invoke`/`ainvoke` pointer back to it (see the
  *Scope / where it lands* note above), not a re-explanation.
- ~~Confirm interaction with the pending LangChain migration~~ — resolved: that migration closed
  2026-07-04 *without* the async conversion, so L03+ was done as its own direct pass on
  2026-07-06 rather than folded into a regeneration. No double-touch materialized.
- Prework-track concerns (K breakout, gating, Docker stack, renumber) now live in
  [`2026-07-03-2211-k-prework-track.md`](2026-07-03-2211-k-prework-track.md).
