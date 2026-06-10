# L07: Hand-rolled agent loop

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (lesson-plan row L07).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).

## Where this lesson sits

By L07, students have seen the *mechanics* of tool calling (L04), the *design* of good tools (L05), and the *packaging* of tools as a portable contract via MCP (L06). What they have not yet built is the *outer loop* that turns a single tool-call round-trip into something that resembles an agent. L07 closes that gap: students assemble a minimal model→tool→model loop in plain Python and learn to reason about the two non-obvious questions that loop raises — *when does it stop?* and *what happens when a tool fails?*

This is the first lesson where the student writes code that *keeps calling the model on its own*. Everything before this was a single API call (L01–L05) or a single tool round-trip (L04). After this lesson, the student has a working agent — small, hand-built, no framework — that can chain multiple tool calls toward a goal. L08 immediately follows by teaching how to *read* what that loop did via tracing; L10 later reframes the same loop as a LangGraph graph.

## Prerequisites

Students arriving at L07 should already be able to:

- Send a chat completion with system/user/assistant roles and parse structured output (L02).
- Wire a single tool to a model call and trace one tool-call round-trip end-to-end (L04). Concretely: format a tool schema, send it with the request, detect a `tool_use` response, execute the tool, and return a `tool_result` message back to the model.
- Decide when a tool is needed vs. model-alone, name and schema-design a tool, and decide what to return on tool errors at the *tool* level — i.e. what message body the tool produces when it can't do its job (L05).
- Recognize that an MCP-exposed tool and an inline Python tool present the same `tool_use`/`tool_result` shape to the loop, even though their packaging differs (L06).

If a student is shaky on the L04 single round-trip in particular, redirect to the L04 lab before continuing — L07 assumes that round-trip is muscle memory.

## Learning objectives

By the end of L07, a student should be able to:

1. **Build a model→tool→model loop in plain Python.** Concretely:
   - Implement a function that takes a user request, a system prompt, and a list of tool definitions, and runs a loop of: call model → if the response contains a `tool_use`, execute the tool and append a `tool_result` message → otherwise return the final assistant message.
   - Maintain the message history correctly across iterations: every `tool_use` block from the assistant must be answered by a matching `tool_result` block in the next user-role message before the model is called again. Mismatches here are the single most common cause of an agent that "just won't work" — call it out by name.
   - Handle the case where the model emits *multiple* `tool_use` blocks in one response. The loop must execute all of them and return all `tool_result`s in a single user-role message before the next model call.
   - Run the loop against a small concrete task (e.g. "use the calculator and the lookup tool to answer X") and observe the model issuing two-or-more tool calls in sequence.

2. **Reason about termination.** Concretely:
   - Name at least four termination conditions and explain when each fires:
     - **Natural termination** — the model emits a final assistant message with no `tool_use` blocks. This is the "happy path."
     - **Step / iteration cap** — the loop has run more model→tool→model cycles than the budget allows. Forces a halt even if the model still wants to call tools.
     - **Token budget** — cumulative input+output tokens (or cost) exceed a threshold.
     - **Loop detection** — the model is calling the same tool with the same arguments repeatedly without making progress. Catching this requires inspecting the tool-call history, not just counting iterations.
   - Implement at least the iteration-cap and natural-termination conditions in code; sketch how token-budget and loop-detection would be added.
   - Decide what the loop returns when it terminates *non-naturally* (raise an exception, return a partial result with a status flag, give the model one last chance to summarize). Defend the choice against a downstream consumer's needs.

3. **Handle tool failures.** Concretely:
   - Distinguish three failure modes at the *loop* level (not the tool-design level from L05):
     - **The tool raises a Python exception** during execution (network error, division by zero, an unhandled edge case the tool author missed).
     - **The tool returns a structured error result** — a well-formed `tool_result` whose content describes a failure (e.g. `{"error": "row not found"}`). This is the L05-recommended pattern; the loop must still propagate it.
     - **The tool's output is malformed** — the wrong shape, an unparseable string, missing fields the model expected.
   - For each, decide: does the loop swallow it and feed the model an error `tool_result` (so the model can recover), abort the loop, or retry? Defend the choice on a per-tool basis. The default for a hand-rolled loop is *surface to the model as a `tool_result` with `is_error: true`* and let the model decide whether to retry — but that default has limits (infinite-retry risk, cost).
   - Implement exception-to-`tool_result` conversion so a buggy tool doesn't crash the agent. Show the model receiving the error and either retrying with corrected arguments or apologizing to the user.

4. **Decide when a hand-rolled loop is the right tool.** Concretely:
   - Name at least three reasons to write your own loop instead of reaching for a framework: small surface area, full control over termination/failure semantics, easier to debug, no framework lock-in for a 50-line problem.
   - Name at least three reasons to *not* write your own loop: graph-shaped control flow (parallel branches, conditional routing), built-in tracing/observability, persistent state across runs, team familiarity with a specific framework.
   - Recognize that L12 (LangGraph shallow agents) and L16 (deep agents) both build on this same model→tool→model skeleton — the framework changes, the loop does not.

## Main points the lecture should land

- **An agent is a loop, not a model.** The model is a stateless function call; the *loop* is what makes it an agent. Every framework students will see later — LangGraph, deep agents, supervisor patterns — is a fancier version of the loop they wrote in this lesson. Hand-rolling it once demystifies the abstraction.
- **The message-history invariant is load-bearing.** Every `tool_use` block must be followed by a matching `tool_result` block, in order, before the next model call. Get this wrong and the API will reject the request or — worse — accept it and produce garbage. This is the single most common bug in hand-rolled loops; teach it as a rule, not a footnote.
- **Termination is a design decision, not a default.** The model will happily call tools forever if you let it. Every production loop has at least one cap (iterations, tokens, time) — usually all three. The cap is a *safety* mechanism, not a correctness one; hitting it always means something went wrong worth investigating.
- **Tool failures are messages, not exceptions.** The default move when a tool fails is to convert the failure into a `tool_result` and hand it back to the model. The model is often the *best* component to decide whether to retry, give up, or try a different tool. The loop's job is mostly to translate exceptions into well-formed messages — not to make the recovery decision itself.
- **The same loop runs MCP tools and inline tools.** From the loop's perspective, a tool is a name + a schema + a function that takes JSON in and returns JSON out. Whether that function dispatches over an MCP transport (L06) or runs in-process is invisible. This is the payoff of the L06 framing: the loop you write here is reusable across both.
- **Streaming and parallelism are out of scope.** The loop in L07 is sequential and non-streaming. Modern Claude APIs support both — students will see them later — but the *control flow* is identical. Get the simple case right first.

## Common student confusions to watch for

- *"The loop ends when the answer is right."* No — the loop ends when the model stops calling tools or a budget cap fires. Whether the answer is "right" is a downstream concern (eval, L08 traces, human review).
- *"I should retry every failed tool call."* Sometimes; often not. A `404 row not found` is not the same kind of failure as a `503 service unavailable`. Blind retries waste tokens and can mask bugs. Default to surfacing the error to the model and letting it decide.
- *"The model needs to see my Python exception traceback."* It doesn't, and shouldn't. Convert the exception to a short, descriptive `tool_result` with `is_error: true`. Tracebacks are noise for the model and a leak risk for stack details.
- *"If I don't return a `tool_result`, the model will figure it out."* It won't — the API will reject the next request. The `tool_use` → `tool_result` pairing is part of the protocol, not a suggestion.
- *"My loop is broken because the model called the same tool three times."* Maybe — or maybe the model is correctly exploring. Loop-detection has to look at *arguments and progress*, not just call counts.
- *"This is what an agent framework does, so I'll never write this code in real life."* Hand-rolled loops show up constantly in production — for tightly-scoped jobs, for testing, for places where a framework is too heavy. The loop is foundational; the framework is the convenience.

## Bridge to L08

L08 introduces tracing: reading what an agent did, locating failures from a trace alone, comparing traces across runs. The hand-rolled loop built in L07 is the natural subject — it has obvious places to instrument (every model call, every tool call, every termination decision) and no built-in observability. L08 starts by adding structured logging to *this exact loop* and grows from there. Encourage students to keep their L07 code accessible; they'll extend it in L08.

A small concrete handoff: at the end of L07, students should have at least one `print()` or `logging.info()` per loop iteration showing iteration number, tool calls made, and termination cause. That's a minimum-viable trace and exactly what L08 will replace with something structured.

## Open authoring questions

- <!-- *NEED INPUT*: estimated lecture duration — best guess 90–120 minutes including a code-along, possibly split into two lectures (loop mechanics + termination, then failure handling). -->
- <!-- *NEED INPUT*: which Claude model anchors the labs — the loop code is identical across models, but the *demos* of natural termination behavior differ. Sonnet 4.6 vs. Haiku 4.5 produce visibly different chaining depth on the same task. -->
- <!-- *NEED INPUT*: should this lesson use the Anthropic SDK directly, or a thin project-internal wrapper that hides the message-array bookkeeping? The pedagogy argument cuts both ways — the wrapper hides the very thing we want to teach, but also lets the lab focus on loop semantics rather than SDK ergonomics. -->
- <!-- *NEED INPUT*: are *parallel tool calls within a single model response* in scope here, or deferred? Modern Claude responses can include multiple `tool_use` blocks in one assistant message; the loop has to execute them all before replying. Recommendation: in scope at the "execute all of them" level (objective 1), but parallel *execution* (asyncio / threading) deferred to a later lesson. -->
- <!-- *NEED INPUT*: is *streaming* in scope? Recommendation: explicitly out of scope for L07; the loop is non-streaming. Mention streaming exists, defer the mechanics. -->
- <!-- *NEED INPUT*: should the lab use one of the MCP servers from L06 as the tool source, or define inline Python tools, or both? Using L06's MCP server is a strong reinforcement of the "same loop runs both" framing but adds setup overhead. -->
- <!-- *NEED INPUT*: where does *cost/latency observability* land — a print of input/output tokens per iteration in L07, or wait for L08's structured traces? L10 (model power) needs this signal too. -->
- <!-- *NEED INPUT*: any fixed naming for the loop function/module so labs and later lessons (L08, L10) can reference it consistently? Suggest `agent_loop.run(...)` returning a `RunResult` with `final_message`, `iterations`, `termination_cause`, and `tool_calls`. -->
