# L10 Proctor Notes

Notes for whoever runs the L10 labs. One section per problem, keyed by lab id and problem number.
Times are rough and assume a semi-technical student with basic Python who completed L01–L08.

> **Both L10 labs are OFFLINE — no API key needed.** They drive a *scripted stub model* (`FakeModel`),
> so termination, the `max_steps` cap, and tool-failure handling are fully deterministic and run the
> same way every time. The only **live** notebook in L10 is the [L1006](L1006_lecture.ipynb) demo
> (a real LangChain chat model, `ANTHROPIC_API_KEY` required) — that's a teacher demo, not a lab.
>
> **Why a stub model?** L10 is about LOOP CONTROL FLOW (iterate model→tool→model until done;
> termination; the cap; failure handling). Scripting the model is the cleanest way to exercise that
> offline and reproducibly — the same mocking stance as the project's tests. The `FakeModel` mimics a
> LangChain chat model (`.bind_tools()` then `.invoke()` → a scripted `AIMessage`), so the loop code
> students write is identical to the live version in L1006.
>
> **Model-agnostic through LangChain.** From L03 on, the course drives every model through a LangChain
> chat model, not the raw Anthropic SDK — the loop only touches `.bind_tools()` / `.invoke()` /
> `AIMessage.tool_calls` / `ToolMessage`, so the same code runs against `ChatAnthropic`, `ChatOpenAI`,
> or the offline `FakeModel`. L1006 builds a real model with `init_chat_model("anthropic:…")`; the key
> loads through `common.config` (`get_settings().anthropic_api_key`), never hard-coded.
>
> The labs map to the L10 subgoals: **L1004** → build the model→tool→model loop + reason about
> termination; **L1005** → handle tool failures at the loop level.

## L1004_lab problem 1 — Detect natural termination

- **Common gotchas:** checking a `stop_reason`/`response_metadata` string instead of the tool calls
  (the lesson wants students to see that *no tool call* is the real signal); a reply can carry text
  **and** tool calls at once — any tool call means "not done," regardless of the text.
- **Unblockers:** "Return `not reply.tool_calls`." Natural termination means the reply carried no
  tool call at all.
- **Time:** ~5 min.
- **Key point:** natural termination is the *only* condition that means "the model thinks it's done."
  Every other stop is something *you* imposed.

## L1004_lab problem 2 — Write run_loop

- **Common gotchas:** **(the big one)** breaking the message-history invariant — appending the
  `ToolMessage`s without first appending the assistant `AIMessage` reply, or dropping one. Stress the
  order: append the `reply` (the `AIMessage`), then one `ToolMessage` per `reply.tool_calls`, then
  loop. Other gotchas: returning after the *first* tool call instead of running *all* of them;
  forgetting the `max_steps` fall-through `return`; off-by-one on the cap (`range(1, max_steps + 1)`
  gives exactly `max_steps` iterations).
- **Unblockers:** walk the four bullets in the prompt in order. If stuck, point them at the L1003 demo
  cell — the structure is identical. The loop is ~15 lines; if theirs is much longer they're probably
  re-deriving `dispatch` (it's given).
- **Time:** ~15 min. This is the heart of the lab.
- **Key point:** the loop is the agent. The model is a stateless function call; the loop is the part
  that makes it iterate.

## L1004_lab problem 3 — Drive it: natural termination

- **Common gotchas:** passing `happy_script` directly to `run_loop` instead of wrapping it in
  `FakeModel(...)`; expecting a different iteration count (it's exactly 3 — two tool turns + one text
  turn).
- **Unblockers:** "`model = FakeModel(happy_script)`, then `run_loop(model, TOOLS, '...', max_steps=10)`."
  The `assert` at the end pins `termination == 'natural'` and `iterations == 3`.
- **Time:** ~4 min.

## L1004_lab problem 4 — The max_steps cap catches a runaway

- **Common gotchas:** confusion about *why* the stub loops forever — explain that `FakeModel` reuses
  its last script line when it runs out, simulating a model that won't stop. Some students expect the
  cap value and the iteration count to differ; they're equal here (cap fires *after* `max_steps`
  iterations).
- **Unblockers:** "One-line script of a single `lookup` tool call (`tool_reply(tool_call(...))`);
  `FakeModel` repeats it; the cap at 5 stops the loop." Expect `termination == 'max_steps'`,
  `iterations == 5`.
- **Time:** ~4 min.
- **Key point:** a loop with no cap is broken, not minimal. Hitting the cap is an **alert** worth
  investigating, not normal operation.

## L1004_lab problem 5 — Multiple tool calls in one reply (written)

- **Common gotchas:** answering "run the first one" — no, run **all** of them; or forgetting that
  each tool call needs its own `ToolMessage`.
- **Unblockers:** expected: when a reply carries multiple tool calls, the loop must execute *every*
  one and append *one `ToolMessage` per call* (all before the next model call) — otherwise the
  message-history invariant is violated and the next request is rejected.
- **Time:** ~3 min.

## L1005_lab problem 1 — Write dispatch: turn a raise into a ToolMessage

- **Common gotchas:** letting the exception propagate (the whole point is to *catch* it); catching
  only one exception type — use a broad `except Exception` here on purpose, because the loop must
  survive *any* tool bug; putting a full traceback in `content` instead of `repr(exc)`; forgetting
  `status="error"` on the failure branches; checking the tool name against the dict's *values*
  instead of `tools.get(call["name"])`.
- **Unblockers:** "Three branches: `fn is None` → error `ToolMessage`; `try: fn(**call["args"])` →
  success `ToolMessage`; `except Exception as exc` → error `ToolMessage` with `repr(exc)`." The good
  `lookup('Paris')` call returns a `status="success"` `ToolMessage` with content `'11000000'`.
- **Time:** ~10 min.
- **Key point:** this is the loop's safety layer. L08 taught the tool author what to *return*; this is
  what the loop does when the tool can't even return.

## L1005_lab problem 2 — The three failure modes, one by one

- **Common gotchas:** the loop crashing here means Problem 1's `dispatch` is letting an exception
  escape — send them back. Expecting the unknown-tool case to raise (it shouldn't; `tools.get` returns
  `None` and `dispatch` handles it).
- **Unblockers:** "Loop over `bad_calls`, print `dispatch(TOOLS, call)`, assert each has
  `status == 'error'`." All three are errors: `KeyError` (missing city), `ValueError` (bad
  expression), unknown tool name.
- **Time:** ~5 min.

## L1005_lab problem 3 — Watch the model recover (no crash)

- **Common gotchas:** expecting the run to crash on the first (failing) `lookup` — it doesn't, because
  `dispatch` converted the `KeyError` into a `status="error"` `ToolMessage`; the scripted model then
  "recovers." Some students forget to wrap the script in `FakeModel`.
- **Unblockers:** "`FakeModel(recover_script)`, then `run_loop(..., max_steps=10)`; assert
  `termination == 'natural'`." The loop reaches the final text turn because the failure became a
  message, not a crash.
- **Time:** ~5 min.
- **Key point:** the loop *enabled* recovery by handing the error back; the model decided what to do
  with it.

## L1005_lab problem 4 — Why not dump the traceback? (written)

- **Common gotchas:** "the model needs the full traceback to debug" — backwards; the traceback is
  noise for the model.
- **Unblockers:** expected (any two): tracebacks are **token-expensive**; they are **noise** the model
  can't act on (it can't read your stack frames); they **leak** internal details (file paths, library
  internals). `repr(exc)` — a class name plus a one-line message — is the right amount of signal.
- **Time:** ~3 min.

## L1005_lab problem 5 — Should the loop auto-retry? (written)

- **Common gotchas:** "always retry, retries are free" — wrong on both counts.
- **Unblockers:** expected: not all failures are alike — a `404 not found` will never succeed on
  retry, a `503` might; blind retries waste tokens and can mask bugs; and an idempotency-violating tool
  (charges a card, sends an email) makes auto-retry actively dangerous. Default: surface the error to
  the model and let *it* decide; add auto-retry only deliberately, with its own budget.
- **Time:** ~3 min.
