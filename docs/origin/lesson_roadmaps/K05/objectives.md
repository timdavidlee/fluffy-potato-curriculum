# K05: Async concepts

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (Prework track row K05).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).
> Sibling doc: [demos_or_activities.md](demos_or_activities.md) — the self-paced walkthrough.
> Paired code TODO: [`2026-07-03-2152-prefer-async-methods.md`](../../../todos/2026-07-03-2152-prefer-async-methods.md)
> — the async-first seam migration this unit's explainer is the canonical reference for.

## Format note

Self-paced student walkthrough, not lecture+lab — same shape as K01 (see
[K01/objectives.md](../K01/objectives.md) for the full format rationale). The paired
[demos_or_activities.md](demos_or_activities.md) is the runbook the student executes, in the
"Do → You should see → What just happened / why it matters → If it breaks" shape.

## Where this unit sits

K05 comes after K04 (the Python-you'll-read refresher) and is the **last conceptual unit before
K06 (Docker & the multi-container stack)** closes out prework. K04 taught the student to *read*
strict-typed / pydantic code; K05 teaches the one remaining shape they'll see everywhere in the
agent arc but have almost certainly never met: **`async def` / `await`**.

This unit carries weight beyond its own runtime. **K05 owns the canonical "why async for agents"
explainer** — the single place in the whole course that argues *why* agent code is written
async-first (concurrent tool calls, parallel eval cases, non-blocking traces / streaming). Every
later lesson that meets a sync-vs-async choice — a LangChain/LangGraph object with both
`.invoke()` and `.ainvoke()`, or the Anthropic/OpenAI sync-vs-async clients — carries a **one-line
pointer back here** rather than re-arguing the case. If this explainer doesn't land, those later
pointers are dangling references.

The single outcome: **the student can read an `async def` signature, explain the event loop at a
semi-technical altitude, use `asyncio.gather` to run coroutines concurrently, `await` directly in
a Jupyter cell, and articulate — in their own words — why agents in particular want async.**

## Prerequisites

- K01–K04 complete: a working `uv` env (`uv run`), keys wired through `common/config.py`, comfort
  driving Jupyter (`uv run jupyter lab`, restart-and-run-all), and the ability to *read* Python
  type hints and a pydantic model.
- Specifically from **K03**: the fact that a Jupyter cell supports **top-level `await`** — K05
  cashes that in. From **K04**: reading `def foo(x: int) -> str`; K05 adds the `async` keyword and
  the `-> Awaitable`-shaped return to that same reading skill.
- No prior concurrency, threading, or async experience is assumed. This is a first contact.

## Learning objectives

By the end of K05, a student should be able to:

1. **Read an `async def` signature and say what makes it different.** Concretely: recognize that
   `async def fetch(x: int) -> str` is a **coroutine function** — calling it does *not* run it, it
   returns a **coroutine object** that does nothing until it's `await`-ed (or handed to the event
   loop). Contrast with a plain `def`, which runs immediately when called. The reading skill:
   spot the `async` keyword and know "this must be awaited."

2. **Use `await` and explain what it does at a semi-technical altitude.** Concretely: `await
   some_coroutine()` means "start this, and while it's waiting on I/O (a network call, a model
   response), **hand control back so other work can run**; resume me when the result is ready." The
   mental model to internalize: `await` is a **yield point**, not a blocking wait — the program
   isn't frozen, it's free to make progress elsewhere.

3. **Describe the event loop as a mental model — no internals.** Concretely: picture a single
   **event loop** as a coordinator running one coroutine at a time, but able to **switch** at every
   `await` to whichever coroutine is ready. State the one load-bearing consequence: this is
   **concurrency without threads** — one thread, cooperatively switching at `await` points — which
   is why it's safe and cheap to run thousands of awaits but you must not call a slow *blocking*
   function inside a coroutine (it stalls the whole loop). No talk of selectors, futures internals,
   or C-level detail — this is a picture, not a spec.

4. **Run coroutines concurrently with `asyncio.gather` and measure the win.** Concretely: given two
   coroutines that each "sleep then return," run them **sequentially** (two `await`s back to back,
   ~2× the delay) versus **concurrently** (`await asyncio.gather(a(), b())`, ~1× the delay), and
   read the wall-clock difference off the demo. The concept: `gather` starts all its coroutines and
   lets the event loop **overlap their waiting** — the total time is the *longest* one, not the
   *sum*. This is the demo the pass checkpoint hangs on.

5. **`await` directly in a Jupyter cell (top-level await).** Concretely: in a notebook cell, write
   `result = await some_coro()` with **no** `asyncio.run(...)` wrapper — the notebook already runs
   inside an event loop (the K03 tie-in). Recognize that a plain `.py` script does *not* have this
   luxury: there you need an entry point (`asyncio.run(main())`) to start the loop. Knowing *which
   context you're in* is the skill.

6. **State the `invoke` / `ainvoke` default and where it points.** Concretely: articulate the
   course-wide rule — **wherever a framework object exposes both a sync `.invoke()` and an async
   `.ainvoke()` (LangChain/LangGraph, first met around L03), or a provider SDK offers a sync
   vs. async client (Anthropic/OpenAI), the course defaults to the async variant** — and know that
   the *reason* is the "why async for agents" explainer in this unit. The student won't write this
   code yet; they need to recognize the pattern and the pointer when a later lesson uses it.

7. **Explain, unprompted, why agents in particular want async.** Concretely: reproduce the three
   concrete payoffs from the canonical explainer below — concurrent tool calls, parallel agents /
   eval cases, non-blocking traces / streaming — and say why `await` + `asyncio.gather` is a
   cleaner path to them than threads. This is objective 7 because it's the one the rest of the
   course leans on.

## Concepts to highlight inline (the callouts)

- **`async def` returns a coroutine, not a result.** Calling a coroutine function does nothing on
  its own — the `await` (or the event loop) is what runs it. The classic first-contact surprise:
  "I called it and nothing happened."
- **`await` is a yield point, not a freeze.** At `await`, control goes back to the loop so other
  coroutines can advance. This is the whole reason async buys concurrency.
- **One event loop, one thread, many coroutines.** Concurrency without threads. Cheap to have
  thousands of awaits; fatal to drop a blocking call in the middle of one.
- **`asyncio.gather` overlaps the waiting.** `n` coroutines that each wait `t` finish in ~`t`, not
  `n·t`. This is the number the student watches change in the demo.
- **Top-level `await` works in Jupyter, not in a bare script.** Notebooks run inside a loop
  already (K03); scripts need `asyncio.run(main())` to start one. Same code, different entry.
- **`.invoke()` vs `.ainvoke()` — default to async.** A one-line rule with a pointer to the
  explainer below; the framework lessons cite this, they don't re-explain it.

## Why async for agents (the canonical explainer) — **this unit owns it**

This is K05's signature contribution and the single source of truth the rest of the course
cross-references. State it plainly, then make it concrete. The framing: **for agents, concurrency
isn't a performance tweak bolted on at the end — it's a core shape of the problem, and it's only
reachable if the seams are async.**

Three concrete payoffs, each much cleaner with `await` + `asyncio.gather` than with threads:

1. **Concurrent tool calls.** A single agent turn often decides to call *several* tools at once
   (look up two records, hit two APIs). With async, that's one `await asyncio.gather(tool_a(),
   tool_b(), ...)` — the waits overlap and the turn finishes in the time of the slowest tool, not
   the sum. The thread version needs a pool, a way to collect results, and careful shared-state
   handling; the async version is one line and stays readable.

2. **Running multiple agents / eval cases in parallel.** Evaluation runs the same agent over
   **many** cases; a multi-agent system runs several agents at once. `asyncio.gather` over a list
   of coroutines fans these out on one event loop — dozens or hundreds in flight, each mostly
   *waiting on the model*, which is exactly the situation async is built for. This is why the eval
   harness (L13) and any fan-out want async seams underneath.

3. **Non-blocking traces / streaming.** Emitting a trace span or streaming tokens back shouldn't
   **stall** the agent's real work. With async, a trace export or a token stream is just another
   coroutine the loop interleaves; nothing blocks waiting for the tracer to finish. Streaming
   responses (token-by-token) are natively an async iteration (`async for`).

**The load-bearing conclusion — say it explicitly:** all three are *only reachable if the seams
themselves are async*. A sync `chat()` / `.invoke()` at the bottom forces every layer above it to
choose between blocking or bolting on threads. That's why the course writes the `potato_llm` and
`common/` seams async-first (see the paired TODO
[`2026-07-03-2152-prefer-async-methods.md`](../../../todos/2026-07-03-2152-prefer-async-methods.md))
and defaults every `.invoke()`/`.ainvoke()` choice to the async side — **so this concurrency is on
the table from L01, not a rewrite later.**

> **Seam-state caveat for the material author.** At the time of writing, the `potato_llm` and
> `common/` seams are **still synchronous** — `PotatoLLMClient.chat()`, the Anthropic/OpenAI
> impls, and the LangChain-style `.invoke()` in `common/agent_loop.py` are all `def`, not `async
> def`; there is no `ainvoke`/async client in the repo yet. The async-first migration (TODO 2152)
> has **not** landed. So this explainer teaches the *target* the course is moving toward, and the
> stage-2 materials must **not** show a live `await client.chat(...)` against the real seam as if
> it already exists. Until the migration lands, keep the demos on **stdlib `asyncio`**
> (`asyncio.sleep`-based coroutines) — which is self-contained and correct regardless — and treat
> any seam-specific async snippet as `<need input: exact async seam entry point once TODO 2152
> lands — until then demonstrate the concept with stdlib asyncio, not the live seam>`.

## Verify / pass checkpoint

K05 is "done" when the student can do **both** of the following:

1. **Run the gather-vs-sequential demo and explain the result.** Run the demo script (see
   [demos_or_activities.md](demos_or_activities.md)) that executes two "sleep ~1s then return"
   coroutines first sequentially (~2s wall clock) then via `asyncio.gather` (~1s), and correctly
   explain **why the concurrent version is roughly twice as fast** — the two waits *overlap* on the
   one event loop instead of running back to back.

2. **Read an `async def` signature cold.** Shown an unfamiliar `async def run(cases: list[str]) ->
   list[str]:`, the student can say: it's a coroutine function, calling it returns a coroutine that
   must be `await`-ed (or gathered), and it's expected to do I/O-bound work that yields at `await`
   points.

A student who can time the demo *and* narrate why is ready for K06. If they can produce the
wall-clock difference but can't explain it, re-run the callout for objective 4 — the *explanation*
is the checkpoint, not the timing.

## Bridge to K06

K05 is the last **concept** unit; **K06 (Docker & the multi-container stack)** is the last
**environment** gate. The link is real, not just sequential: the multi-container stack K06 stands
up (Langfuse + Postgres + ClickHouse, plus the DB + agent services) is exactly the kind of
**several-services-talking-over-the-network** world where async pays off — an agent service that
calls a model, writes to Postgres, and emits traces is doing three I/O-bound things that async
lets it overlap. K05 gave the student the mental model; K06 stands up the services that model will
run against, and closes prework with the "does the stack come up?" go/no-go before `L01`.

## Open authoring questions

- `<need input: exact async seam entry point + minimal async call snippet — blocked on TODO 2152
  (`2026-07-03-2152-prefer-async-methods.md`) landing. Until the `potato_llm`/`common/` seams are
  actually `async def`, K05's runnable demos stay on stdlib `asyncio` and any live-seam await is a
  placeholder.>`
- `<need input: does K05 introduce `asyncio.gather`'s error semantics (return_exceptions, one
  failure cancelling siblings) at all, or is that deferred to the eval-harness lesson (L13) where
  a failing case shouldn't kill the batch? Leaning: mention it exists in one sentence here, teach
  it for real in L13.>`
- `<need input: how much of the sync-in-a-coroutine footgun (blocking call stalls the loop) to
  show — a live "here's a blocking sleep freezing gather" counter-demo cements it but adds a cell;
  or keep it to a callout. Leaning: callout only, to respect the ~short-notebook rule.>`
