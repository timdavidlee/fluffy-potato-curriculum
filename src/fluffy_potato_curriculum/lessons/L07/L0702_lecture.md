# The agent loop: termination and tool-failure handling

```yaml
title: "The agent loop: termination and tool-failure handling"
keywords: agent loop, model tool model, message history invariant, termination, iteration cap, max steps, token budget, loop detection, tool failure, is_error, hand-rolled vs framework, anthropic, claude
estimated duration: 75
```

> **Lesson:** L07. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L07/objectives.md).
> This is the written reference lecture — thorough on purpose, so a student who missed the verbal
> delivery can rebuild the lesson from the page. The runnable companion is the stub-model demo
> ([L0703_lecture.ipynb](L0703_lecture.ipynb)); the live multi-step run is
> ([L0706_lecture.ipynb](L0706_lecture.ipynb)); hands-on practice is the two L07 labs
> ([L0704](L0704_lab_empty.ipynb) loop + termination, [L0705](L0705_lab_empty.ipynb) tool failures).
> **Anchor model for the live demo: Claude Sonnet 4.6.**

## section 1. The lesson in one claim

### slide 1.1 An agent is a loop, not a model

- The model is a **stateless function call**: send it the conversation plus the tool definitions, get
  back one response, done. It does not remember the last turn ([L04](L0701_intro.md) called this out).
- An **agent** is the *loop* wrapped around that function call. The loop is the only thing that turns
  a single round-trip into multi-step behaviour.
- Said as a chant: **the model proposes; the loop drives.** Everything in this lecture is about how
  the loop drives — and, crucially, when it *stops* driving.

### slide 1.2 Where L07 sits in the arc

- table: what each neighbouring lesson contributed, and what L07 adds on top.

| Lesson | What it built | What L07 reuses |
| --- | --- | --- |
| [L04](L0701_intro.md) | one tool-call round-trip; the `tool_use` / `tool_result` protocol | the exact protocol, now repeated in a loop |
| [L05](../L05/objectives.md) | tool design; what a tool *returns* on failure | the error-as-data idea, now propagated by the loop |
| **L07** | the model→tool→model **loop**: termination + loop-level failure handling | — |
| L08 (next) | tracing what the loop did | the loop becomes the thing you instrument |
| L11 (later) | the same loop, reframed as a LangGraph graph | the skeleton is identical; the wrapper changes |

- The loop you write here is **reused, not replaced**, by every later lesson. That is why it is worth
  building by hand once.

### slide 1.3 The three rules, up front

- This whole lecture lands three rules. Read them now; every section returns to one of them.
- **Rule 1 — the message-history invariant.** Every `tool_use` block must be answered by a matching
  `tool_result` (same id) in the next user-role message before the next model call. (section 2)
- **Rule 2 — termination is a design decision.** The model will call tools forever if you let it; a
  loop with no cap is broken, not minimal. (section 3)
- **Rule 3 — tool failures are messages, not exceptions.** The loop converts a raised exception into a
  `tool_result` with `is_error: true` and hands it back to the model. (section 4)

[↑ Back to top](#the-agent-loop-termination-and-tool-failure-handling)

## section 2. Building the loop

### slide 2.1 The loop in three lines of pseudocode

- Before any Python, the whole loop fits in three lines:
- text: *call the model → got a `tool_use`? run the tool, append the `tool_result`, loop again. Got
  plain text and no `tool_use`? return it — that's the answer.*
- diagram: a cycle — `call model` → diamond `tool_use?` → (yes) `run tool` → `append tool_result` →
  back to `call model`; (no) → `return final text`. A second arrow from the cycle labelled
  `max_steps reached` exits to `stop: cap hit`.

### slide 2.2 The function shape we standardize on

- We give the loop one fixed shape so the labs, the demo, and L08 all reference it the same way.
- text: `run_loop(model, tools, user_msg, max_steps)` returns a small result bundle with the final
  text, the number of iterations, and **why** it stopped.
- table: the four parameters and what each is.

| Parameter | Type | What it is |
| --- | --- | --- |
| `model` | a client object | anything with a `.create(messages, tools, ...)` method — the **real SDK or a stub** |
| `tools` | `dict[str, Callable]` | maps a tool name to the Python function that runs it (the *dispatch table*) |
| `user_msg` | `str` | the user's request that seeds the conversation |
| `max_steps` | `int` | the iteration cap — the safety net of section 3 |

- The return is a `RunResult` carrying `final_text`, `iterations`, and `termination` (a string like
  `"natural"` or `"max_steps"`). Naming the *termination cause* is what makes the loop debuggable —
  and is exactly what L08's traces will build on.

### slide 2.3 Rule 1 — the message-history invariant

- This is the single most common bug in hand-rolled loops, so we teach it as a rule, not a footnote.
- text: after the model emits an assistant message containing `tool_use` blocks, the **next**
  message you send must be a **user-role** message whose content contains a `tool_result` block for
  **every** `tool_use` — each referencing the same `tool_use_id`, in order — *before* you call the
  model again.
- text: skip one, mismatch an id, or put the result in an `assistant` message instead of a `user`
  message, and the API rejects the request (or, worse, accepts it and the model produces garbage).
- diagram: two columns. Left "correct": `assistant[tool_use #a, tool_use #b]` → `user[tool_result
  #a, tool_result #b]`. Right "broken": `assistant[tool_use #a, tool_use #b]` → `user[tool_result
  #a]` with a red X and the caption "missing #b → API error".

### slide 2.4 Multiple tool calls in one response

- A single assistant response can contain **more than one** `tool_use` block (the model asks for two
  lookups at once, say).
- text: the loop must run **all** of them and package **all** their `tool_result`s into a **single**
  user-role message before the next model call. One assistant turn with N tool calls is answered by
  one user turn with N tool results.
- text: *executing* them one after another in a Python `for` loop is fine for L07. True *parallel*
  execution (threads / asyncio) and streaming are explicitly **out of scope** here — the control flow
  is identical; we get the simple case right first.

### slide 2.5 The dispatch table

- The loop does not hard-code tool names. It looks each requested name up in the `tools` dict and
  calls the function it finds.
- text: this is why "the same loop runs MCP tools and inline tools" ([L06](../../CURRICULUM_PRD.md)
  framing): from the loop's view a tool is just *a name → a function that takes JSON in and returns
  a string out*. Whether that function dispatches over an MCP transport or runs in-process is
  invisible to the loop.
- text: an unknown name (the model invented a tool) is itself a failure the loop handles — see
  section 4.

[↑ Back to top](#the-agent-loop-termination-and-tool-failure-handling)

## section 3. Termination: when does the loop stop?

### slide 3.1 Termination is a design decision

- The model has no idea a loop exists. It will keep emitting `tool_use` blocks as long as it thinks
  more tool calls help. **Nothing stops the loop unless you write the stop.**
- text: a loop with no cap is not "minimal" — it is **broken**. Even a hand-rolled toy needs a cap.
- text: there are four termination conditions worth naming. You will *implement* the first two and
  *sketch* the other two.

### slide 3.2 Four termination conditions

- table: the four conditions, when each fires, and whether L07 implements it.

| Condition | Fires when | In L07 |
| --- | --- | --- |
| **Natural termination** | the model returns a response with **no `tool_use` block** — plain text. This is the happy path: "the model thinks it's done." | implement |
| **Step / iteration cap** (`max_steps`) | the loop has run more model→tool→model cycles than the budget allows. Forces a halt even if the model still wants tools. | implement |
| **Token budget** | cumulative input+output tokens (or cost) crosses a threshold. | sketch |
| **Loop detection** | the model calls the *same tool with the same arguments* repeatedly without progress. Needs the call *history*, not just a counter. | sketch |

- text: **natural** is the only condition that means "the answer is ready." Every other condition
  means "we stopped it" — a halt, not a completion.

### slide 3.3 The iteration cap is a safety net, not a correctness tool

- text: the cap exists to bound the damage when something goes wrong — a runaway model, a tool that
  always looks unfinished, a prompt that never converges. It does **not** make answers correct.
- text: **hitting the cap is always a signal worth investigating.** Either the task genuinely needs a
  higher cap, or the agent is misbehaving (fix the prompt, the tools, or the model). Treat a cap-hit
  as an alert, not as noise.
- diagram: a runaway trace — iterations 1..6 each showing `tool_use lookup(args=...)` with identical
  args, then iteration 6 boxed in red with "max_steps=6 hit — STOP".

### slide 3.4 What the loop returns on a non-natural stop

- When the loop stops because a cap fired (not because the model finished), you must decide what to
  hand back. Three reasonable choices:
- text: **(a) raise an exception** — loudest; good when a cap-hit is a true error your caller must
  handle. **(b) return a partial result with a status flag** — our default; the caller inspects
  `termination` and decides. **(c) give the model one last turn to summarize** — friendliest output,
  costs one more call.
- text: we use **(b)** in L07: `RunResult.termination` is `"natural"` or `"max_steps"`, and the
  caller (or L08's trace) reads it. Defend your choice against *who consumes the result* — a batch
  job wants (a); a chat UI may want (c).

### slide 3.5 Sketching the other two caps

- text: **token budget** — keep a running sum of `response.usage` input+output tokens across
  iterations; halt when it crosses a threshold. Trivial to add once you print per-iteration tokens
  (the demo does).
- text: **loop detection** — keep a short history of `(tool_name, json.dumps(args))` tuples; halt if
  the last *k* are identical. This catches "same call, again" that the iteration counter alone
  misses. Note this needs *arguments and progress*, not just call counts — a model calling the same
  tool three times with *different* args may be correctly exploring.

[↑ Back to top](#the-agent-loop-termination-and-tool-failure-handling)

## section 4. Tool failures: messages, not exceptions

### slide 4.1 Two layers of failure handling

- text: L05 taught the **tool author** what to *return* when something goes wrong — the
  error-as-data pattern, e.g. returning `{"error": "row not found"}` from the tool itself.
- text: L07 teaches the **loop** what to do when the tool *can't even return* — it raised, or it
  returned the wrong shape. These are **different layers**, and the loop owns the second one.
- diagram: a stack — top box "tool author (L05): return errors as data" over a bottom box "loop
  (L07): catch raises, normalize shape, attach is_error" — with the model sitting above both.

### slide 4.2 Three failure modes at the loop level

- table: the three failure modes the loop must distinguish, and the default loop response to each.

| Failure mode | What it looks like | Default loop response |
| --- | --- | --- |
| **Tool raises an exception** | `network error`, `ZeroDivisionError`, an edge case the author missed — a Python traceback | catch it; build a `tool_result` with `is_error: true` and a short message; feed it back |
| **Tool returns a structured error** | a well-formed `tool_result` whose content says `{"error": "..."}` (the L05 pattern) | **no loop change** — propagate it as-is; the tool already did the right thing |
| **Tool output is malformed** | wrong type, unparseable, missing a field the model expected | normalize to a string / minimal shape check; surface as a (possibly `is_error`) `tool_result` |

- text: the unifying move across all three: **turn the failure into a `tool_result` and hand it back
  to the model.** The loop translates; it does not (by default) decide the recovery.

### slide 4.3 Exception-to-`tool_result`, in five lines

- text: the core of loop-level failure handling is a `try/except` around the dispatch that converts
  any uncaught exception into a `tool_result(is_error=True, content=<short message>)`. Five lines.
- diagram: pseudocode block —
  `try: out = tools[name](**args)` /
  `except Exception as exc: out = repr(exc); is_error = True` /
  `append tool_result(tool_use_id, out, is_error)`.
- text: a buggy tool now **degrades into a message** instead of crashing the agent. The model
  receives the error and can retry with corrected arguments, try a different tool, or apologize to
  the user — its call, not the loop's.

### slide 4.4 Don't dump tracebacks at the model

- text: feed the model a **short, descriptive** error string — `"division by zero"`, not a 40-line
  Python traceback.
- text: three reasons: tracebacks are **token-expensive**, they are **noise** the model can't act on,
  and they **leak** stack details (file paths, internals) you'd rather not expose.
- text: `repr(exc)` (e.g. `ZeroDivisionError('division by zero')`) is usually the right amount of
  signal — a class name plus a one-line message.

### slide 4.5 Retries are a decision, not a default

- text: the L07 loop does **not** auto-retry. Surfacing the error to the model and letting it decide
  is the default — the model often knows whether a retry could possibly help.
- text: not all failures are alike. A `404 row not found` will *never* succeed on retry; a `503
  service unavailable` *might*. Blind retries waste tokens and can mask bugs — and an idempotency-
  violating tool (one that charges a card, sends an email) makes auto-retry actively dangerous.
- text: if you *do* want auto-retry, add it **deliberately**, with its own budget — never as a
  reflex. For L07, surface-and-let-the-model-decide is the stance.

[↑ Back to top](#the-agent-loop-termination-and-tool-failure-handling)

## section 5. When to hand-roll vs. reach for a framework

### slide 5.1 The hand-rolled loop is a real choice

- text: students who only ever see frameworks over-reach for them; students who only ever hand-roll
  under-reach. Both extremes are bugs. The framework decision is a genuine engineering trade-off.
- table: when each side wins.

| Hand-roll your own loop when... | Reach for a framework when... |
| --- | --- |
| small surface area — a 50-line problem | graph-shaped control flow (parallel branches, conditional routing) |
| you want full control over termination / failure semantics | you want built-in tracing / observability |
| it must be trivial to debug — no abstraction in the way | you need persistent state across runs |
| you don't want framework lock-in | your team already standardizes on one framework |

### slide 5.2 The loop is the foundation; the framework is the convenience

- text: hand-rolled loops show up constantly in production — for tightly-scoped jobs, for tests, for
  places where a framework is too heavy. "I'll never write this in real life" is false.
- text: **tracing (L08) is the most common reason teams reach for a framework** — and it is exactly
  what the next lesson starts adding to *this* hand-rolled loop.
- text: foreshadow — L08 instruments *this exact loop* with structured traces; L11 reframes *this
  exact loop* as a LangGraph graph. The loop itself doesn't change; the wrapper around it does. We
  keep L07 plain Python **on purpose**, so you see the skeleton before a framework hides it.

### slide 5.3 Common confusions to leave behind

- table: the misconception and the correction (each recurs in the labs).

| "I think..." | Actually |
| --- | --- |
| "the loop ends when the answer is right" | the loop ends when the model stops calling tools or a cap fires; *correctness* is a downstream concern (L08 traces, L09 eval) |
| "I should retry every failed tool call" | usually not — a `404` is not a `503`; default to surfacing the error and letting the model decide |
| "the model needs my Python traceback" | it doesn't and shouldn't — a short `is_error` string is better signal and cheaper |
| "if I skip the `tool_result` the model will figure it out" | it won't — the API rejects the next request; the pairing is protocol, not a suggestion |
| "the model called the same tool 3× so my loop is broken" | maybe — or it's correctly exploring; loop-detection needs *args + progress*, not just counts |

### slide 5.4 The minimum-viable trace (bridge to L08)

- text: by the end of L07 your loop prints, per iteration: the iteration number, the tool calls it
  made, and the termination cause. That is a **minimum-viable trace**.
- text: L08 replaces that `print()` with a structured record (`{"event": "tool_call", "iteration": i,
  "tool": name, "args": args}` appended to a list) and teaches you to *read* it. Keep your L07 code
  accessible — you extend it in L08.
- text: one sentence to leave L07 with: *an agent is a loop around a stateless model — call, run the
  tool, feed the result back, repeat, until the model stops or a cap you chose fires; and when a tool
  breaks, the loop turns the break into a message, not a crash.*

[↑ Back to top](#the-agent-loop-termination-and-tool-failure-handling)
