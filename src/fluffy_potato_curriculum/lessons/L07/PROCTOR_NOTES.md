# L07 Proctor Notes

Notes for whoever runs the L07 labs. One section per problem, keyed by lab id and problem number.
Times are rough and assume a semi-technical student with basic Python who completed L01–L05.

> **Both L07 labs are OFFLINE — no API key needed.** They drive a *scripted stub model* (`FakeModel`),
> so termination, the `max_steps` cap, and tool-failure handling are fully deterministic and run the
> same way every time. The only **live** notebook in L07 is the [L0706](L0706_lecture.ipynb) demo
> (raw Anthropic SDK, `ANTHROPIC_API_KEY` required) — that's a teacher demo, not a lab.
>
> **Why a stub model?** L07 is about LOOP CONTROL FLOW (iterate model→tool→model until done;
> termination; the cap; failure handling). Scripting the model is the cleanest way to exercise that
> offline and reproducibly — the same mocking stance as the project's tests. The stub mimics the
> SDK's `.content` blocks with `SimpleNamespace`, so the loop code students write is identical to the
> live version in L0706.
>
> **Why the raw Anthropic SDK in L0706 (not `potato_llm`)?** The course's `potato_llm` seam is
> text-only — its `Message` cannot carry `tool_use`/`tool_result` blocks, which are exactly what the
> agent loop is built on. So L0706 calls the raw SDK directly; the key still loads through
> `common.config` (`require_anthropic_key`), never hard-coded. This is the same seam exception L04
> made. (Open design question for the course: extend `potato_llm` to model tool blocks, or keep the
> loop on the raw SDK — flagged for the curriculum author.)
>
> The labs map to the L07 subgoals: **L0704** → build the model→tool→model loop + reason about
> termination; **L0705** → handle tool failures at the loop level.

## L0704_lab problem 1 — Detect natural termination

- **Common gotchas:** checking `stop_reason` instead of the blocks (works, but the lesson wants
  students to see that *no `tool_use` block* is the real signal); using `all(...)` instead of
  `not any(...)`; assuming a response is either all-text or all-tool_use (it can mix — a `text` block
  *and* a `tool_use` block coexist, and that still counts as "not done").
- **Unblockers:** "Return `not any(b.type == 'tool_use' for b in resp.content)`." Natural termination
  means the model emitted no tool call at all.
- **Time:** ~5 min.
- **Key point:** natural termination is the *only* condition that means "the model thinks it's done."
  Every other stop is something *you* imposed.

## L0704_lab problem 2 — Write run_loop

- **Common gotchas:** **(the big one)** breaking the message-history invariant — appending the
  `tool_result`s without first appending the assistant's `tool_use` turn, or putting the results in an
  `assistant` message instead of a `user` message. Stress that the order is always
  `assistant(tool_use…)` then `user(tool_result…)`. Other gotchas: returning after the *first*
  `tool_use` instead of running *all* of them; forgetting the `max_steps` fall-through `return`;
  off-by-one on the cap (`range(1, max_steps + 1)` gives exactly `max_steps` iterations).
- **Unblockers:** walk the four bullets in the prompt in order. If stuck, point them at the L0703 demo
  cell — the structure is identical. The loop is ~15 lines; if theirs is much longer they're probably
  re-deriving `dispatch` (it's given).
- **Time:** ~15 min. This is the heart of the lab.
- **Key point:** the loop is the agent. The model is a stateless function call; the loop is the part
  that makes it iterate.

## L0704_lab problem 3 — Drive it: natural termination

- **Common gotchas:** passing `happy_script` directly to `run_loop` instead of wrapping it in
  `FakeModel(...)`; expecting a different iteration count (it's exactly 3 — two tool turns + one text
  turn).
- **Unblockers:** "`model = FakeModel(happy_script)`, then `run_loop(model, TOOLS, '...', max_steps=10)`."
  The `assert` at the end pins `termination == 'natural'` and `iterations == 3`.
- **Time:** ~4 min.

## L0704_lab problem 4 — The max_steps cap catches a runaway

- **Common gotchas:** confusion about *why* the stub loops forever — explain that `FakeModel` reuses
  its last script line when it runs out, simulating a model that won't stop. Some students expect the
  cap value and the iteration count to differ; they're equal here (cap fires *after* `max_steps`
  iterations).
- **Unblockers:** "One-line script of a single `lookup` `tool_use`; `FakeModel` repeats it; the cap at
  5 stops the loop." Expect `termination == 'max_steps'`, `iterations == 5`.
- **Time:** ~4 min.
- **Key point:** a loop with no cap is broken, not minimal. Hitting the cap is an **alert** worth
  investigating, not normal operation.

## L0704_lab problem 5 — Two tool calls in one response (written)

- **Common gotchas:** answering "run the first one" — no, run **all** of them; or forgetting that all
  the `tool_result`s go in **one** user message.
- **Unblockers:** expected: when a response has multiple `tool_use` blocks, the loop must execute
  *every* one and return *all* their `tool_result`s in a **single** user-role message before the next
  model call — otherwise the message-history invariant is violated and the API rejects the request.
- **Time:** ~3 min.

## L0705_lab problem 1 — Write dispatch: turn a raise into a tool_result

- **Common gotchas:** letting the exception propagate (the whole point is to *catch* it); catching
  only one exception type — use a broad `except Exception` here on purpose, because the loop must
  survive *any* tool bug (note the `# noqa: BLE001`); putting a full traceback in `content` instead of
  `repr(exc)`; forgetting `is_error: True` on the failure branches; checking the tool name with `in`
  against the dict's *values* instead of `tools.get(name)`.
- **Unblockers:** "Three branches: `fn is None` → error result; `try: fn(**call.input)` → success
  result; `except Exception as exc` → error result with `repr(exc)`." The good `lookup('Paris')` call
  returns content `'11000000'` with no `is_error` key.
- **Time:** ~10 min.
- **Key point:** this is the loop's safety layer. L05 taught the tool author what to *return*; this is
  what the loop does when the tool can't even return.

## L0705_lab problem 2 — The three failure modes, one by one

- **Common gotchas:** the loop crashing here means Problem 1's `dispatch` is letting an exception
  escape — send them back. Expecting the unknown-tool case to raise (it shouldn't; `tools.get` returns
  `None` and `dispatch` handles it).
- **Unblockers:** "Loop over `bad_calls`, print `dispatch(TOOLS, call)`, assert each has
  `is_error is True`." All three are errors: `KeyError` (missing city), `ValueError` (bad expression),
  unknown tool name.
- **Time:** ~5 min.

## L0705_lab problem 3 — Watch the model recover (no crash)

- **Common gotchas:** expecting the run to crash on the first (failing) `lookup` — it doesn't, because
  `dispatch` converted the `KeyError` into a `tool_result`; the scripted model then "recovers." Some
  students forget to wrap the script in `FakeModel`.
- **Unblockers:** "`FakeModel(recover_script)`, then `run_loop(..., max_steps=10)`; assert
  `termination == 'natural'`." The loop reaches the final text turn because the failure became a
  message, not a crash.
- **Time:** ~5 min.
- **Key point:** the loop *enabled* recovery by handing the error back; the model decided what to do
  with it.

## L0705_lab problem 4 — Why not dump the traceback? (written)

- **Common gotchas:** "the model needs the full traceback to debug" — backwards; the traceback is
  noise for the model.
- **Unblockers:** expected (any two): tracebacks are **token-expensive**; they are **noise** the model
  can't act on (it can't read your stack frames); they **leak** internal details (file paths, library
  internals). `repr(exc)` — a class name plus a one-line message — is the right amount of signal.
- **Time:** ~3 min.

## L0705_lab problem 5 — Should the loop auto-retry? (written)

- **Common gotchas:** "always retry, retries are free" — wrong on both counts.
- **Unblockers:** expected: not all failures are alike — a `404 not found` will never succeed on
  retry, a `503` might; blind retries waste tokens and can mask bugs; and an idempotency-violating tool
  (charges a card, sends an email) makes auto-retry actively dangerous. Default: surface the error to
  the model and let *it* decide; add auto-retry only deliberately, with its own budget.
- **Time:** ~3 min.
