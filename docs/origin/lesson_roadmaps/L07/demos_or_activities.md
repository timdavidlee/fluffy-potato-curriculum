# L07: Teacher-led demos — Hand-rolled agent loop

> Sibling docs: [objectives.md](objectives.md) (what the lesson aims for), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md).
>
> **Audience for this file:** the teacher running L07. Every demo below is *teacher-driven, no student participation*. Student-driven exercises live in the L07 labs (separate file).

## How to read this file

Each demo is a self-contained block with:

- **Goal** — the single insight the demo should land. Tied to a learning objective from [objectives.md](objectives.md).
- **Pre-flight** — what the teacher needs loaded before class.
- **Live script** — the order of operations during the demo. Treat it as a checklist, not a teleprompter.
- **What to highlight** — the moment(s) where the teacher should slow down and call out the takeaway out loud.
- **If the demo misbehaves** — graceful fallback for when the model surprises you (because it will).

The demos are ordered to match the four learning objectives from [objectives.md](objectives.md). Demo 1 builds the loop; Demo 2 stresses termination; Demo 3 stresses failure handling; Demo 4 contrasts hand-rolled vs. framework. They build on each other — Demos 2 and 3 deliberately reuse Demo 1's loop so students see it stretched and broken, not replaced. Run them in order on first delivery.

## Pre-flight (once, at the top of the lesson)

The teacher should have, before the first demo starts:

- A working REPL or notebook with the project's Claude SDK setup (per the project's `uv` env), and a known-good single-tool round-trip from L04 in scrollback as a warm-up reference.
- Two pre-defined inline Python tools that will be reused across all demos:
  - `calculator(expression: str) -> str` — evaluates a small arithmetic expression. Cheap, deterministic, easy to reason about.
  - `lookup(key: str) -> str` — returns a value from a tiny in-memory dict (e.g. mapping product names to prices, or city names to populations). Has a couple of keys present and a couple deliberately missing, so "key not found" is reachable.
- A third tool that will *fail on demand*, used only in Demo 3:
  - `flaky_fetch(url: str) -> str` — has a flag the teacher flips to make it raise an exception, return a structured error, or return malformed output. <!-- *NEED INPUT*: confirm whether this is implemented as a single tool with a global flag, three distinct tools, or a tool whose behavior depends on the `url` argument. Recommendation: one tool keyed on the URL — `https://ok` returns a value, `https://error` returns a structured error, `https://crash` raises, `https://garbage` returns malformed JSON. Keeps the demo prompt natural. -->
- A loop function `agent_loop.run(...)` that the teacher will *write live* in Demo 1 and *reuse unchanged* through Demos 2 and 3. Keep a "completed" version in a sibling file the teacher can paste in if live-coding falls behind. <!-- *NEED INPUT*: confirm naming with [objectives.md](objectives.md) open question on `agent_loop.run` API shape. Same name should be used in lectures, labs, and L08. -->
- A small wrapper that prints, after each model call: iteration number, tool calls requested, tool results returned, cumulative input/output tokens, and wall-clock latency. This is the closest thing to a "trace" the lesson exposes; L08 replaces it with something structured. Foreshadow that.
- A second model client configured for Demo 4's framework comparison. <!-- *NEED INPUT*: confirm which Claude model anchors L07's demos — the loop is model-agnostic but chaining depth varies. Mirrors the open question in [objectives.md](objectives.md). -->

> Why pre-defined tools: the lesson is about the *loop*, not about tool design. L05 already covered tool design. Re-litigating tool schemas mid-demo eats time and dilutes the message. Spend tool-design time only on `flaky_fetch` (Demo 3), where the failure modes *are* the point.

## Demo 1 — The loop made visible (Objective 1)

**Goal:** build a model→tool→model loop from scratch in front of the class. Land the framing from [objectives.md](objectives.md): *"an agent is a loop, not a model."* Show the message-history invariant in practice.

**Pre-flight:**

- An empty `agent_loop.py` (or notebook cell) the teacher will fill in live.
- The `calculator` and `lookup` tools defined and importable.
- A starter task on the slide: *"What is the population of the city whose name is the answer to 17 squared minus 1?"* — chosen because it forces (1) a calculator call, then (2) a lookup using the calculator's result, then (3) a final assistant answer. <!-- *NEED INPUT*: confirm the lookup table contains a "288"-keyed entry that produces a sensible city, or swap the puzzle. The point is two sequential tool calls plus a natural-termination model message — pick any task that produces that shape. -->

**Live script:**

1. Sketch the loop on the whiteboard before typing: *call model → got `tool_use`? execute, append `tool_result`, loop. Got plain text? return it.* Three lines of pseudocode.
2. Live-code the loop in Python. Write the message list, the call, the `tool_use` detection, the tool dispatch, and the append-`tool_result` step. **Do not add an iteration cap yet.** That's Demo 2's punchline.
3. Run the loop on the starter task. Walk through the printed iterations: model emits `tool_use` for `calculator`, tool runs, result appended, next call, model emits `tool_use` for `lookup`, tool runs, result appended, next call, model emits a final assistant message — natural termination.
4. Re-run with a task that produces *two `tool_use` blocks in a single response*. <!-- *NEED INPUT*: confirm a task that reliably produces parallel tool calls on the target model — e.g. *"Look up the populations of Tokyo and Lagos and tell me which is larger."* If the chosen model splits these into sequential calls, swap to a task where the calls are clearly independent. --> Show the loop executing both tools and packaging both `tool_result`s into a single user-role message.

**What to highlight:**

- The message-history invariant. After every assistant response with `tool_use`, the *next* user message must contain a `tool_result` for *every* `tool_use` block, in order. Show what happens if you skip one (the API rejects the request). This is the lesson's most-bug-prone moment in real code — call it out by name.
- The model is *not* aware of the loop. From its perspective, every call is one round-trip. The loop lives entirely in the surrounding Python.
- The same loop will run MCP-exposed tools from L06 unchanged — the dispatch function is the only thing that differs.

**If the demo misbehaves:**

- If live-coding falls behind, paste the prepared completed version and walk through it line by line. Don't sacrifice the runs — the runs are where the loop becomes concrete.
- If the model answers from prior knowledge without calling the tools, tighten the system prompt (*"You may only answer using the tools provided"*) and rerun.
- If the model emits `tool_use` and a final-answer text in the same response, that's a real protocol nuance worth a brief aside — the loop should still execute the tool *and* keep going; the text is interim narration.

## Demo 2 — Termination conditions, three ways (Objective 2)

**Goal:** show natural termination, an iteration-cap rescue, and a runaway loop in the same demo. Land that *termination is a design decision* from [objectives.md](objectives.md), not a default.

**Pre-flight:**

- The Demo 1 loop, plus a one-line addition of an `iteration_cap` parameter that defaults to a sensibly low number for the demo (e.g. 6).
- A "looping" task designed to provoke the model into calling the same tool repeatedly. <!-- *NEED INPUT*: confirm a task that reliably produces a runaway — e.g. asking the model to "keep checking" a value via the lookup tool, or giving it a tool whose result is ambiguous so the model retries with variations. The exact prompt depends on the chosen model's behavior; dry-run before class. -->
- A side-by-side panel ready: iteration number on the left, tool call args on the right. Helps the audience see "same call, again" land visually.

**Live script:**

1. Re-run Demo 1's starter task with `iteration_cap=20`. It naturally terminates in 3–4 iterations. Read out the termination cause: *"natural — model emitted no `tool_use`."*
2. Run the looping task with `iteration_cap=20`. Watch the model call the same tool 8+ times. Cap fires. Read out the termination cause: *"iteration cap hit — non-natural termination."*
3. Show the *same* looping task with `iteration_cap=3`. Cap fires faster. Discuss: the cap caught the bug, but smaller caps cost less when things go wrong.
4. Sketch (don't implement live) two more termination conditions:
   - **Token budget:** sum input+output tokens across iterations; halt if over budget. Show the printed token counts from pre-flight that already make this trivial to add.
   - **Loop detection:** keep a small history of `(tool_name, json.dumps(args))` tuples; halt if the last 3 are identical.

**What to highlight:**

- The iteration cap *is* the safety net. Hitting it is always a signal worth investigating — either the task is genuinely too hard (need a higher cap) or the agent is misbehaving (need to fix the prompt, the tools, or the model). Either way, treat cap-hits as alerts, not noise.
- "Natural termination" is one specific signal — the model returned plain text. Make sure students hear that phrase tied to *no `tool_use` block in the response.* That's the only condition that means "the model thinks it's done."
- A loop with no cap is not "minimal" — it's broken. Even a hand-rolled toy needs a cap.

**If the demo misbehaves:**

- If the chosen model refuses to loop on the looping task (e.g. it correctly gives up after one or two retries), force the issue with a tool whose result is deliberately unhelpful (`lookup` returning `"unknown — try again"`). The point is to show the cap *catching* something, not to make the model look bad.
- If the natural-termination run actually hits the cap on the day (model keeps wanting to call tools), raise the cap and re-run. Don't let the demo accidentally teach "natural termination is rare."

## Demo 3 — Tool failure as a message, not an exception (Objective 3)

**Goal:** show all three failure modes from [objectives.md](objectives.md) flowing back through the loop as `tool_result`s, and watch the model recover. Land that *the loop's job is mostly translating exceptions into well-formed messages.*

**Pre-flight:**

- The Demo 1 loop with one addition: a `try/except` wrapper around the tool dispatch that converts any uncaught exception to a `tool_result` with `is_error: true` and the exception's `repr()` as content. **Do not write this addition yet** — it's the live-code beat.
- The `flaky_fetch` tool with the four URL behaviors from pre-flight.
- A small task on the slide: *"Fetch the value at https://ok and tell me what it is. If that fails, try https://crash, then https://error, then give up gracefully."* — chosen so the model walks through every failure mode in one run, with explicit recovery instructions in the prompt so the demo doesn't depend on the model improvising. <!-- *NEED INPUT*: confirm the prompt is explicit enough that the model will walk all four URLs without deciding to abort early. Adjust the system prompt if the model gives up after the first failure. -->

**Live script:**

1. Run the loop on the failure task *without* the `try/except` wrapper. The first call to `https://crash` raises; the loop crashes. Walk through the traceback. Punchline: *the agent died because one tool had a bug.*
2. Live-add the `try/except` → `tool_result(is_error=True, content=repr(exc))` conversion. Five lines.
3. Re-run the same task. Watch the model:
   - call `https://ok` → success → continue.
   - call `https://crash` → exception → loop converts to `is_error: true` → model receives the error, sees it can't recover that URL, tries the next.
   - call `https://error` → tool returns a structured error result (`{"error": "..."}`) — show that this case needs *no* loop changes, because the tool followed the L05 pattern of returning errors as data.
   - call `https://garbage` → tool returns malformed output — show what the model does with it. <!-- *NEED INPUT*: depending on the model's behavior, this may be the place to introduce a *minimum* output-shape check in the loop (e.g. ensure the result is a string), or to leave it for the lab. Pick one based on time budget. -->
   - emit a final assistant message acknowledging the failures and giving up gracefully — natural termination.
4. Quick aside: show what *not* to do. Re-run with the exception's full traceback as the `tool_result` content (instead of a short message). Note token cost, irrelevance to the model, and the stack-trace leak concern.

**What to highlight:**

- The default move when a tool fails is to convert the failure into a `tool_result` and hand it back to the model. The model is often the best component to decide whether to retry, swap tools, or give up.
- Loop-level failure handling and tool-level failure handling are *different layers*. L05 taught the tool author what to *return* when something goes wrong; L07 teaches the loop what to do when the tool *can't even return* (raise, malformed, etc.).
- Don't dump tracebacks at the model. A short, descriptive error string is better signal and cheaper.
- Retries are a model-side decision in this design. The loop doesn't auto-retry. If you wanted auto-retry, you'd add it deliberately, with a budget, and you'd probably regret it on the first idempotency-violating tool.

**If the demo misbehaves:**

- If the model immediately gives up after the first failure instead of trying the next URL, strengthen the prompt's recovery instructions and re-run. The point is to show the loop *enabling* recovery, even if today's model is being conservative.
- If `https://garbage` produces an output the model handles gracefully, mention that and skip the malformed-output beat. Don't manufacture a failure that doesn't naturally occur.

## Demo 4 — Hand-rolled vs. framework: a one-screen contrast (Objective 4)

**Goal:** show the same task running on the hand-rolled loop and on a minimal framework loop side by side. Land that *every framework students will see (L12, L16) is a fancier version of this loop.*

**Pre-flight:**

- The Demo 1+2+3 loop, now with iteration cap and exception-to-`tool_result` conversion built in (~50 lines of Python).
- A LangGraph "minimum viable" agent doing the same thing, pre-written. <!-- *NEED INPUT*: confirm whether L07 should preview LangGraph here at all, or stay strictly framework-free and defer the comparison to L10's opening. Recommendation: a 60-second preview here is high-value because it makes "hand-rolled" feel like a real choice, not a default. But the *lecture* should not teach LangGraph mechanics — that's L10's job. -->
- The starter task from Demo 1, runnable against both implementations.

**Live script:**

1. Show the hand-rolled loop side by side with the framework version. ~50 lines vs. however-many. Don't read the framework code line by line — just point out the abstractions (graph, nodes, state object).
2. Run the *same task* on both. Identical final answer (or close enough). Identical tool-call sequence. Different code shape.
3. Discuss: when does the framework's overhead pay off? Three specific cases — graph-shaped control flow (parallel branches, conditional routing), built-in observability/tracing, persistent state across runs.
4. Discuss: when does it *not* pay off? Three specific cases — small surface area (this lesson's loop), one-off scripts, debugging a behavior the framework abstracts.
5. Foreshadow: L08 will instrument *this exact hand-rolled loop* with structured tracing. L10 will reframe *this exact loop* as a LangGraph graph. The loop itself doesn't change — the wrapper around it does.

**What to highlight:**

- The framework decision is a real engineering choice with real trade-offs. Students who only ever see frameworks tend to over-reach for them; students who only ever hand-roll tend to under-reach. Both extremes are bugs.
- Tracing (L08) is the most common reason teams *do* reach for a framework — and it's exactly what the next lesson will start adding to the hand-rolled version. Set the expectation now.

**If the demo misbehaves:**

- If the LangGraph install or the framework demo flakes on the day, skip the live run and walk through the *code shape* on the slide. The point is the contrast in shape, not a live race.

## Optional bridge demo — toward tracing (L08)

If time allows, run one final beat that previews L08: take the print-wrapper from pre-flight and replace one `print()` with a structured dict (`{"event": "tool_call", "iteration": i, "tool": name, "args": args}`) appended to a list. Show the list at the end of a run. That's the simplest possible trace.

Don't teach trace analysis here — that's L08. Just show the *shape* of what's about to come, so students see the next lesson as a natural extension of this one rather than a new topic.

<!-- *NEED INPUT*: include this bridge demo, or save it as the opener for L08? -->

## Pacing notes for the teacher

- **Per-demo time:** Demo 1 is the long one (15–25 minutes including the live-code build). Demos 2 and 3 are 10–15 minutes each. Demo 4 is 8–12 minutes. Total: 45–75 minutes for the four demos plus the optional bridge. Fits a 90-minute block with discussion. <!-- *NEED INPUT*: confirm against the lesson-time budget once duration is pinned in [objectives.md](objectives.md)'s open questions. -->
- **Live-coding budget:** Demo 1's loop is the only place to live-code. Demos 2–4 should reuse Demo 1's code with small additions; do *not* re-derive the loop in each demo.
- **Variance budget:** the model's tool-call patterns are not deterministic. Budget at least one re-run per demo for tasks that depend on the model issuing specific tool calls.
- **The audience watches, doesn't participate.** Resist the temptation to ask "what should the loop do here?" — that's a lab pattern, not a demo pattern. Hands-on practice is for the L07 labs.

## Open authoring questions

- <!-- *NEED INPUT*: which model class anchors the demos — see pre-flight. Mirrors the open question in [objectives.md](objectives.md). -->
- <!-- *NEED INPUT*: are demos run in a Jupyter notebook the teacher projects, or a slide-embedded REPL, or a custom demo runner script? Affects how `agent_loop.run` is structured for live-code in Demo 1. -->
- <!-- *NEED INPUT*: should Demo 4's LangGraph preview happen here, or be deferred entirely to L10? Recommendation in the demo above; final call is the author's. -->
- <!-- *NEED INPUT*: should Demo 3 use one of L06's MCP-exposed tools as the failing tool, to reinforce "the loop runs both kinds"? Adds setup overhead; reinforces the L06 framing. Trade-off worth deciding. -->
- <!-- *NEED INPUT*: a pointer/link to where the demo prompts and the `flaky_fetch` tool live as code (a `demos/` subdir? inline in a notebook?) — not yet decided. -->
- <!-- *NEED INPUT*: are *parallel tool calls* (multiple `tool_use` blocks in one assistant response) shown in Demo 1 as planned, or deferred to the lab? Mirrors the same open question in [objectives.md](objectives.md). -->
