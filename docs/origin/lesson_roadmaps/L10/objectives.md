# L10: Hand-rolled agent loop

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (lesson-plan row L10).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).

## Where this lesson sits

By L10, students have seen the *mechanics* of tool calling (L07), the *design* of good tools (L08), and the *packaging* of tools as a portable contract via MCP (L09). What they have not yet built is the *outer loop* that turns a single tool-call round-trip into something that resembles an agent. L10 closes that gap: students assemble a minimal model→tool→model loop in plain Python and learn to reason about the two non-obvious questions that loop raises — *when does it stop?* and *what happens when a tool fails?*

This is the first lesson where the student writes code that *keeps calling the model on its own*. Everything before this was a single API call (L01–L08) or a single tool round-trip (L07). After this lesson, the student has a working agent — small, hand-built, no framework — that can chain multiple tool calls toward a goal. L11 immediately follows by teaching how to *read* what that loop did via tracing; L13 later reframes the same loop as a LangGraph graph.

## Prerequisites

Students arriving at L10 should already be able to:

- Send a chat completion with system/user/assistant roles and parse structured output (L02).
- Wire a single tool to a model call and trace one tool-call round-trip end-to-end (L07). Concretely: bind a typed tool to the model, send the request, detect that the reply's `.tool_calls` is non-empty, execute the tool, and append a matching `ToolMessage` back to the message list.
- Decide when a tool is needed vs. model-alone, name and schema-design a tool, and decide what to return on tool errors at the *tool* level — i.e. what message body the tool produces when it can't do its job (L08).
- Recognize that an MCP-exposed tool and an inline Python tool present the same `.tool_calls`/`ToolMessage` shape to the loop, even though their packaging differs (L09).

If a student is shaky on the L07 single round-trip in particular, redirect to the L07 lab before continuing — L10 assumes that round-trip is muscle memory.

## Learning objectives

By the end of L10, a student should be able to:

1. **Build a model→tool→model loop in plain Python.** Concretely:
   - Implement a function that takes a user request, a system prompt, and a list of tool definitions, binds the tools to the model (`model.bind_tools(...)`), and runs a loop of: `.invoke(messages)` → if the reply's `.tool_calls` is non-empty, execute the tool(s) and append a matching `ToolMessage` per call → otherwise return the final assistant `AIMessage`.
   - Maintain the message history correctly across iterations: after appending the assistant `AIMessage`, every entry in its `.tool_calls` must be answered by a matching `ToolMessage` (paired by `tool_call_id`) before the next `.invoke`. Mismatches here are the single most common cause of an agent that "just won't work" — call it out by name.
   - Handle the case where the model emits *multiple* entries in `.tool_calls` in one reply. The loop must execute all of them and append one `ToolMessage` per call before the next `.invoke`.
   - Run the loop against a small concrete task (e.g. "use the calculator and the lookup tool to answer X") and observe the model issuing two-or-more tool calls in sequence.

2. **Reason about termination.** Concretely:
   - Name at least four termination conditions and explain when each fires:
     - **Natural termination** — the reply is an `AIMessage` with empty `.tool_calls` (text only). This is the "happy path."
     - **Step / iteration cap** — the loop has run more model→tool→model cycles than the budget allows. Forces a halt even if the model still wants to call tools.
     - **Token budget** — cumulative input+output tokens (or cost) exceed a threshold.
     - **Loop detection** — the model is calling the same tool with the same arguments repeatedly without making progress. Catching this requires inspecting the tool-call history, not just counting iterations.
   - Implement at least the iteration-cap and natural-termination conditions in code; sketch how token-budget and loop-detection would be added.
   - Decide what the loop returns when it terminates *non-naturally* (raise an exception, return a partial result with a status flag, give the model one last chance to summarize). Defend the choice against a downstream consumer's needs.

3. **Handle tool failures.** Concretely:
   - Distinguish three failure modes at the *loop* level (not the tool-design level from L08):
     - **The tool raises a Python exception** during execution (network error, division by zero, an unhandled edge case the tool author missed).
     - **The tool returns a structured error result** — a `ToolMessage` whose content describes a failure (e.g. `{"error": "row not found"}`). This is the L08-recommended pattern; the loop must still propagate it.
     - **The tool's output is malformed** — the wrong shape, an unparseable string, missing fields the model expected.
   - For each, decide: does the loop swallow it and feed the model an error `ToolMessage` (so the model can recover), abort the loop, or retry? Defend the choice on a per-tool basis. The default for a hand-rolled loop is *surface to the model as a `ToolMessage(..., status="error")`* and let the model decide whether to retry — but that default has limits (infinite-retry risk, cost).
   - Implement exception-to-`ToolMessage` conversion so a buggy tool doesn't crash the agent — `ToolMessage(content=repr(exc), tool_call_id=..., status="error")`. Show the model receiving the error and either retrying with corrected arguments or apologizing to the user.

4. **Decide when a hand-rolled loop is the right tool.** Concretely:
   - Name at least three reasons to write your own loop instead of reaching for a framework: small surface area, full control over termination/failure semantics, easier to debug, no framework lock-in for a 50-line problem.
   - Name at least three reasons to *not* write your own loop: graph-shaped control flow (parallel branches, conditional routing), built-in tracing/observability, persistent state across runs, team familiarity with a specific framework.
   - Recognize that L14 (LangGraph shallow agents) and L18 (deep agents) both build on this same model→tool→model skeleton — the framework changes, the loop does not.

## Main points the lecture should land

- **An agent is a loop, not a model.** The model is a stateless function call; the *loop* is what makes it an agent. Every framework students will see later — LangGraph, deep agents, supervisor patterns — is a fancier version of the loop they wrote in this lesson. Hand-rolling it once demystifies the abstraction.
- **The message-history invariant is load-bearing.** After you append the assistant `AIMessage`, every entry in its `.tool_calls` must be answered by a matching `ToolMessage` (paired by `tool_call_id`), in order, before the next `.invoke`. Get this wrong and the model/runtime expects every tool call answered — an unanswered `tool_call` leaves the conversation malformed and you get a rejected request or, worse, garbage. This is the single most common bug in hand-rolled loops; teach it as a rule, not a footnote.
- **Termination is a design decision, not a default.** The model will happily call tools forever if you let it. Every production loop has at least one cap (iterations, tokens, time) — usually all three. The cap is a *safety* mechanism, not a correctness one; hitting it always means something went wrong worth investigating.
- **Tool failures are messages, not exceptions.** The default move when a tool fails is to convert the failure into a `ToolMessage` (`status="error"`) and hand it back to the model. The model is often the *best* component to decide whether to retry, give up, or try a different tool. The loop's job is mostly to translate exceptions into well-formed messages — not to make the recovery decision itself.
- **The same loop runs MCP tools and inline tools.** From the loop's perspective, a tool is a name + a schema + a function that takes JSON in and returns JSON out. Whether that function dispatches over an MCP transport (L09) or runs in-process is invisible — the loop only ever sees a `.tool_calls` entry to run and a `ToolMessage` to append. This is the payoff of the L09 framing: the loop you write here is reusable across both.
- **Streaming and parallelism are out of scope.** The loop in L10 is sequential and non-streaming. Modern Claude APIs support both — students will see them later — but the *control flow* is identical. Get the simple case right first.

## Common student confusions to watch for

- *"The loop ends when the answer is right."* No — the loop ends when the model stops calling tools or a budget cap fires. Whether the answer is "right" is a downstream concern (eval, L11 traces, human review).
- *"I should retry every failed tool call."* Sometimes; often not. A `404 row not found` is not the same kind of failure as a `503 service unavailable`. Blind retries waste tokens and can mask bugs. Default to surfacing the error to the model and letting it decide.
- *"The model needs to see my Python exception traceback."* It doesn't, and shouldn't. Convert the exception to a short, descriptive `ToolMessage(content=repr(exc), status="error")`. Tracebacks are noise for the model and a leak risk for stack details.
- *"If I don't append a `ToolMessage`, the model will figure it out."* It won't — an unanswered `tool_call` leaves the conversation malformed and the next request is rejected. The `.tool_calls` → `ToolMessage` pairing (by `tool_call_id`) is part of the protocol, not a suggestion.
- *"My loop is broken because the model called the same tool three times."* Maybe — or maybe the model is correctly exploring. Loop-detection has to look at *arguments and progress*, not just call counts.
- *"This is what an agent framework does, so I'll never write this code in real life."* Hand-rolled loops show up constantly in production — for tightly-scoped jobs, for testing, for places where a framework is too heavy. The loop is foundational; the framework is the convenience.

## Bridge to L11

L11 introduces tracing: reading what an agent did, locating failures from a trace alone, comparing traces across runs. The hand-rolled loop built in L10 is the natural subject — it has obvious places to instrument (every model call, every tool call, every termination decision) and no built-in observability. L11 starts by adding structured logging to *this exact loop* and grows from there. Encourage students to keep their L10 code accessible; they'll extend it in L11.

A small concrete handoff: at the end of L10, students should have at least one `print()` or `logging.info()` per loop iteration showing iteration number, tool calls made, and termination cause. That's a minimum-viable trace and exactly what L11 will replace with something structured.

## Open authoring questions

- <!-- *NEED INPUT*: estimated lecture duration — best guess 90–120 minutes including a code-along, possibly split into two lectures (loop mechanics + termination, then failure handling). -->
- <!-- *NEED INPUT*: which Claude model anchors the labs — the loop code is identical across models, but the *demos* of natural termination behavior differ. Sonnet 4.6 vs. Haiku 4.5 produce visibly different chaining depth on the same task. -->
- > **Resolved:** L10 drives a LangChain chat model (`model.bind_tools(...)` → `.invoke(messages)` → `AIMessage.tool_calls` → `ToolMessage`); the canonical instrumented copy is `common/agent_loop.py`. The loop bookkeeping (pairing each tool call with a `ToolMessage`) is exactly what the lesson teaches, so it stays visible — not hidden behind a wrapper.
- <!-- *NEED INPUT*: are *parallel tool calls within a single model response* in scope here, or deferred? Modern Claude responses can include multiple `.tool_calls` entries in one `AIMessage`; the loop has to execute them all before replying. Recommendation: in scope at the "execute all of them" level (objective 1), but parallel *execution* (asyncio / threading) deferred to a later lesson. -->
- <!-- *NEED INPUT*: is *streaming* in scope? Recommendation: explicitly out of scope for L10; the loop is non-streaming. Mention streaming exists, defer the mechanics. -->
- <!-- *NEED INPUT*: should the lab use one of the MCP servers from L09 as the tool source, or define inline Python tools, or both? Using L09's MCP server is a strong reinforcement of the "same loop runs both" framing but adds setup overhead. -->
- <!-- *NEED INPUT*: where does *cost/latency observability* land — a print of input/output tokens per iteration in L10, or wait for L11's structured traces? L13 (models & providers) needs this signal too. -->
- <!-- *NEED INPUT*: any fixed naming for the loop function/module so labs and later lessons (L11, L13) can reference it consistently? Suggest `agent_loop.run(...)` returning a `RunResult` with `final_message`, `iterations`, `termination_cause`, and `tool_calls`. -->
