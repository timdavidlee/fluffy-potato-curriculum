# K05: Self-paced walkthrough — Async concepts

> Sibling docs: [objectives.md](objectives.md), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md).
>
> **Audience:** the *student*, alone at a keyboard. Every step is something you run yourself. Same
> "Do → You should see → What just happened / why it matters → If it breaks" shape as
> [K01](../K01/demos_or_activities.md) and [K02](../K02/demos_or_activities.md).

## How to read this file

Work top to bottom; budget ~20–25 minutes. The finish line is the **gather-vs-sequential timing
demo** (Step 4) plus being able to *explain* why the concurrent version is faster — that
explanation, not the timing, is the pass checkpoint.

**Reminder:** every command is `uv run …` (K01, Step 4). The runnable demos here use only Python's
**standard library** (`asyncio`) — no keys, no network, nothing to install — so they're safe,
free, and deterministic. We deliberately do **not** call a live model in K05; the async *concept*
is the whole point, and the model calls come later.

> **One-sentence orientation:** async is how you get **concurrency without threads** — one program,
> one thread, cooperatively switching between tasks whenever one of them is *waiting*. That's the
> whole idea; the steps below make it concrete.

## Step 0 — Where you'll run these

You can run every demo two ways, and K05 uses both on purpose:

- A **`.py` script** via `uv run python path/to/script.py` — a script has *no* event loop of its
  own, so it needs an `asyncio.run(main())` entry point.
- A **Jupyter cell** via `uv run jupyter lab` — a notebook is *already* inside an event loop, so
  you can write `await ...` at the top of a cell with no wrapper (the K03 tie-in, Step 5).

Knowing *which context you're in* is a real skill — the same coroutine is started differently in
each. We'll see both.

## Step 1 — A first coroutine: `async def` returns something that doesn't run yet

**Do:** create a scratch file (anywhere; delete it after) — say `~/k05_first.py`:

```python
import asyncio


async def greet(name: str) -> str:
    await asyncio.sleep(0.1)  # pretend this is a slow network / model call
    return f"hello, {name}"


# Calling a coroutine function does NOT run it — it makes a coroutine object:
coro = greet("world")
print("before await:", coro)          # <coroutine object greet at 0x...>

# To actually run it from a script, hand it to the event loop:
result = asyncio.run(greet("world"))
print("after run:  ", result)
```

Run it:

```sh
uv run python ~/k05_first.py
```

**You should see:** the first line prints a `<coroutine object greet ...>` — **not** the greeting.
The second prints `after run:   hello, world`.

**What just happened / why it matters:** an `async def` is a **coroutine function**. Calling it
(`greet("world")`) doesn't execute the body — it hands you back a **coroutine object** that does
nothing until something *runs* it. In a script, `asyncio.run(...)` starts the event loop, runs the
coroutine to completion, and gives you the return value. This is the first-contact surprise worth
feeling in your hands: **"I called it and nothing happened" is correct** — you have to `await` it
(next step) or `asyncio.run` it.

**If it breaks:** `RuntimeWarning: coroutine 'greet' was never awaited` means you *called* a
coroutine and then threw it away without running it — exactly the mistake this step is about. Wrap
it in `asyncio.run(...)` (script) or `await` it (notebook).

## Step 2 — `await` inside a coroutine: the yield point

**Do:** extend the idea — one coroutine awaiting another. New file `~/k05_await.py`:

```python
import asyncio
import time


async def slow_double(x: int) -> int:
    await asyncio.sleep(1)  # a 1-second "I'm waiting on I/O" pause
    return x * 2


async def main() -> None:
    start = time.perf_counter()
    a = await slow_double(10)   # start it, wait for it, get 20
    b = await slow_double(21)   # THEN start the next one, wait, get 42
    elapsed = time.perf_counter() - start
    print(f"results: {a}, {b}  |  took {elapsed:.1f}s")


asyncio.run(main())
```

Run it:

```sh
uv run python ~/k05_await.py
```

**You should see:** `results: 20, 42  |  took 2.0s` (about two seconds).

**What just happened / why it matters:** each `await` **starts a coroutine and waits for it to
finish before the next line runs**. Because we awaited them *one after another*, the two
1-second waits happened **back to back** — ~2 seconds total. The key mental note: `await` is a
**yield point** — while `slow_double` is sleeping, the program *could* be doing other work — but
here we gave it nothing else to do, so it just waited. Step 4 gives it something else to do, and
that's where the magic shows up.

**If it breaks:** `SyntaxError: 'await' outside function` means you put `await` at the top level of
a **script** — that only works inside an `async def` (or a notebook cell, Step 5). Keep the awaits
inside `main` and call `asyncio.run(main())`.

## Step 3 — The event loop, in one picture

There's no command for this step — read it, then Step 4 makes it real.

Picture a single **event loop**: a coordinator that runs **one** coroutine at a time, on **one**
thread. Whenever the running coroutine hits an `await` on something slow (a sleep, a network call,
a model response), it **yields control back to the loop**, which immediately switches to any *other*
coroutine that's ready to make progress. When the slow thing finishes, the loop resumes the first
one where it left off.

Two consequences worth holding onto:

- **This is concurrency without threads.** One thread, cooperatively switching at `await` points.
  It's cheap to have hundreds or thousands of coroutines in flight, because most of them are just
  *waiting* — and waiting is free.
- **Never drop a *blocking* call inside a coroutine.** If you call a slow **synchronous** function
  (e.g. plain `time.sleep(5)` instead of `await asyncio.sleep(5)`) inside a coroutine, it doesn't
  yield — it **freezes the entire loop**, and every other coroutine stalls with it. The rule of
  thumb: inside `async def`, wait on things with `await`, not with blocking calls.

## Step 4 — The payoff: `asyncio.gather` (pass-checkpoint demo)

This is the demo the whole unit is built around. New file `~/k05_gather.py`:

```python
import asyncio
import time


async def slow_double(x: int) -> int:
    await asyncio.sleep(1)  # same 1-second "waiting on I/O" as before
    return x * 2


async def sequential() -> None:
    start = time.perf_counter()
    a = await slow_double(10)
    b = await slow_double(21)
    print(f"sequential: {a}, {b}  |  {time.perf_counter() - start:.1f}s")


async def concurrent() -> None:
    start = time.perf_counter()
    # Start BOTH coroutines and let the loop overlap their waiting:
    a, b = await asyncio.gather(slow_double(10), slow_double(21))
    print(f"concurrent: {a}, {b}  |  {time.perf_counter() - start:.1f}s")


async def main() -> None:
    await sequential()
    await concurrent()


asyncio.run(main())
```

Run it:

```sh
uv run python ~/k05_gather.py
```

**You should see:** two lines, and the second is about **twice as fast**:

```
sequential: 20, 42  |  2.0s
concurrent: 20, 42  |  1.0s
```

**What just happened / why it matters — the load-bearing concept of this unit:**
`asyncio.gather(...)` **starts all the coroutines you pass it at once** and waits for them together.
Because both `slow_double` calls spend their second *waiting*, the event loop **overlaps** those
waits on its one thread — so the total time is the **longest** coroutine (~1s), not the **sum**
(~2s). Same coroutines, same work, half the wall clock, no threads.

**Say the explanation out loud** (this is your pass checkpoint, per
[objectives.md](objectives.md)): *"The concurrent version is faster because `gather` runs both
waits at the same time on one event loop instead of one after the other — the total is the longest
wait, not the sum."* If you can produce the timing **and** that sentence, you've cleared K05's main
gate.

**If it breaks:** if both lines show ~2s, check that `concurrent()` uses `asyncio.gather(a(), b())`
and not two separate `await`s (that's just `sequential` again). If you get a `RuntimeWarning` about
a coroutine never awaited, you probably passed `gather` the coroutine *functions* (`slow_double`)
instead of *called* coroutines (`slow_double(10)`).

## Step 5 — Top-level `await` in a Jupyter cell (the K03 tie-in)

**Do:** start Jupyter (from K03) and open a scratch notebook:

```sh
uv run jupyter lab
```

In a cell, paste **and run**:

```python
import asyncio


async def slow_double(x: int) -> int:
    await asyncio.sleep(1)
    return x * 2


# No asyncio.run(...) here — a notebook is ALREADY inside an event loop:
results = await asyncio.gather(slow_double(10), slow_double(21))
results
```

**You should see:** `[20, 42]` after about one second — and notice you wrote `await` **directly at
the top of the cell**, with no `asyncio.run(...)` wrapper.

**What just happened / why it matters:** a Jupyter notebook runs your code **inside an event loop
already**, so it supports **top-level `await`** — you can `await` a coroutine straight from a cell.
A plain `.py` script does **not** have a loop running, which is why the scripts above needed
`asyncio.run(main())` to start one. Same coroutine, two different entry points depending on where
you are. This is why so many of the course's live demos live in notebooks: `await
some_agent_call(...)` just works in a cell.

**If it breaks:** `SyntaxError: 'await' outside function` in a notebook usually means an *older*
IPython/Jupyter without top-level-await support — but the pinned `.venv` (K01) ships a current one,
so if you see this, confirm you launched with `uv run jupyter lab` and not a system Jupyter.

## Step 6 — Read an `async def` signature cold (the other half of the checkpoint)

**Do:** no code — a reading drill. Look at this signature and answer three questions to yourself:

```python
async def run_cases(cases: list[str]) -> list[str]:
    ...
```

1. What kind of function is it? *(A coroutine function — the `async` keyword.)*
2. What does calling `run_cases([...])` give you? *(A coroutine object — it doesn't run yet; you
   must `await` it, or hand it to `asyncio.gather` / `asyncio.run`.)*
3. What's it probably doing? *(I/O-bound work — likely awaiting a model or a tool per case — that
   yields at each `await`, which is exactly why it's async.)*

**Why it matters:** every agent-arc lesson from L03 onward is full of `async def` signatures
like this. You don't need to *write* them yet — you need to **read** them without flinching, which
you now can.

## The one rule to carry forward: `.invoke()` vs `.ainvoke()`

You'll soon meet framework objects (LangChain / LangGraph, around L03) that expose **two** ways
to call them: a **sync** `.invoke()` and an **async** `.ainvoke()`. The provider SDKs
(Anthropic / OpenAI) similarly offer a sync client and an async client. **This course defaults to
the async variant** — `.ainvoke()`, the async client — everywhere it has the choice.

*Why?* Exactly the "why async for agents" reasoning from
[objectives.md](objectives.md): concurrent tool calls, running many agents / eval cases in
parallel, and non-blocking traces / streaming are all one clean `await asyncio.gather(...)` away —
but **only if the whole stack is async down to the seam.** When a later lesson writes `.ainvoke()`
and drops a one-line "we default to async — see K05," *this* is what it's pointing at.

> **Heads-up on the current code.** As of this writing the project's own LLM seam
> (`potato_llm` / `common/`) is **still synchronous** — the async-first migration is in progress
> (see [`2026-07-03-2152-prefer-async-methods.md`](../../../todos/2026-07-03-2152-prefer-async-methods.md)).
> So the concept you learned here is the direction the course is moving; the stdlib `asyncio` demos
> above teach it correctly and independently of that migration.
> `<need input: replace this heads-up with a real `await client.chat(...)` seam example once
> TODO 2152 lands and the seams are actually async.>`

## Done — and the hook into K06

You can now read `async def`, explain the event loop, run coroutines concurrently with
`asyncio.gather`, `await` at the top of a Jupyter cell, and say **why** agents want async. That's
the last **concept** of prework.

The last **environment** step remains: **K06 (Docker & the multi-container stack)** stands up the
several services your agents will actually run against — Langfuse (tracing), Postgres (data), and
the agent service — the exact multi-service, network-bound world where the async concurrency you
just learned earns its keep. K06 is also prework's final go/no-go: "does the stack come up?" before
`L01`.
