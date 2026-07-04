# The ReAct agent: a graph with a cycle

```yaml
title: "The ReAct agent: a graph with a cycle"
keywords: ReAct agent, cyclic graph, StateGraph, back-edge, add_messages, ToolNode, conditional edge, route, tools_condition, recursion_limit, handle_tool_errors, termination, langgraph, langchain, claude
estimated duration: 10
```

> **Lesson:** L10 — Cyclic graphs: the ReAct agent loop.
> **Roadmap:** see this lesson's [objectives.md](../../../../docs/origin/lesson_roadmaps/L10/objectives.md).
> This is a short framing piece. Read it before the reference lecture
> ([L1002_lecture.md](L1002_lecture.md)), the stub-model demo notebook that wires the graph
> ([L1003_lecture.ipynb](L1003_lecture.ipynb)), the two hands-on labs
> ([L1004](L1004_lab_empty.ipynb), [L1005](L1005_lab_empty.ipynb)), and the one live multi-step demo
> ([L1006_lecture.ipynb](L1006_lecture.ipynb)).
> **Anchor model for the live demo: Claude Sonnet 4.6.**

## Where this lesson sits

By L10 you have built graphs that flow **forward and stop**. [L04](../L04/objectives.md) wired a
directed `StateGraph` — typed state, `add_node`, `add_edge`, `compile`, `invoke` — and
[L05](../L05/objectives.md) added a **conditional edge** (`add_conditional_edges` + a routing
function) so a graph can branch. You have also seen the *mechanics* of tool calling
([L07](../L07/L0701_intro.md): `bind_tools`, `.tool_calls`, `ToolMessage`), the *design* of good
tools ([L08](../L08/objectives.md)), and tools *packaged* as a portable contract over MCP
([L09](../L09/objectives.md)). What every graph so far has in common is that it is a **DAG** — it
runs forward and no node ever runs twice.

L10 adds the one primitive those graphs lacked: a **back-edge**. That single edge — from the tool
node back to the model node — is the entire difference between a pipeline and an agent. This is the
first lesson where your graph **calls the model on its own, repeatedly**, chaining tool calls toward
a goal until the model stops asking.

## The one idea, said three ways

If you remember nothing else from L10, remember this: **an agent is a graph with a cycle.**

1. The **model** node is a stateless function call. You send it the whole conversation plus the tool
   definitions; it emits one reply, possibly carrying `.tool_calls`. It does not remember the last
   turn and it does not run your tools — that framing is straight from [L07](../L07/L0701_intro.md).
2. The **cycle** is what makes it an agent. A conditional edge asks *"did the model ask for tools?"*;
   if yes, a tool node runs them and a **back-edge** loops to the model so it can react to what it
   just saw — over and over — until the model returns plain text or a safety cap fires. That
   loop-shaped graph is the **ReAct** pattern (reason, act, repeat).
3. **The graph *is* the loop.** Drawn as boxes and arrows, the model→tool→model loop is exactly:
   an `agent` node, a `tools` node, a conditional exit, and a back-edge. The next lesson
   ([L11](../L11/L1101_intro.md)) reveals that `create_agent` builds *this exact graph* in one line;
   [L18](../../CURRICULUM_PRD.md)'s deep agents nest it. Wiring it by hand once is what makes every
   framework legible.

## The three rules this lesson lands

These three rules are the spine of the lesson — the lecture, the demo, and both labs return to them:

- **The message-history invariant is load-bearing — and the graph maintains it for you.** After an
  `AIMessage` with `.tool_calls`, every call must be answered by a matching `ToolMessage` (same
  `tool_call_id`) before the next model call. Two prebuilt pieces own this: the **`add_messages`
  reducer** on the state (each node *appends* to the conversation instead of overwriting it) and the
  prebuilt **`ToolNode`** (it runs each requested tool and appends one `ToolMessage` per call). In a
  hand loop the pairing is the #1 bug; here it is a graph invariant. Know *what* the invariant is so
  you can debug it — even though `ToolNode` enforces it.
- **Termination is a design decision — and it is just a branch of `route`.** Left alone, the model
  will call tools forever. **Natural termination** is the `route` function returning `END` because
  the last reply had no `.tool_calls`; the graph's built-in **`recursion_limit`** is the safety cap
  that halts a runaway (a `GraphRecursionError`) even when the model still wants tools. Framing
  termination as the `END` branch of an L05 conditional edge — not a special mechanism — is the
  payoff of teaching L05 first.
- **Tool failures are messages, not exceptions.** When a tool *raises*,
  `ToolNode(handle_tool_errors=True)` catches it and appends a `ToolMessage(status="error")`, so the
  back-edge hands the model a message, not a crash. This builds on L08: L08 taught the *tool author*
  what to **return** on failure; L10 teaches the *graph* what to do when the tool **can't even
  return**. The graph's job is to translate exceptions into well-formed messages — not to make the
  recovery decision. That is the model's call.

## How we teach it: a stub model, then one live run

The hard part of an agent is the **control flow** — the cycle, the stop condition, the failure
path — not the live model. So most of L10 runs on a tiny **stub model** (the course's `FakeModel`):
a fake whose `.invoke(...)` returns the next *scripted* `AIMessage` off a list (a tool-call turn,
then another, then a final text turn). Because `ToolNode` drives the *real* tools against those
scripted calls, a scripted model makes the whole graph **deterministic**:

- the graph runs the same way every time — no API key, no cost, no network;
- you can script a runaway (the model "never stops") and watch the `recursion_limit` *catch* it;
- you can script a tool that raises and watch `ToolNode` turn the exception into a `ToolMessage`.

That is how the demo ([L1003](L1003_lecture.ipynb)) and both labs ([L1004](L1004_lab_empty.ipynb),
[L1005](L1005_lab_empty.ipynb)) work — **offline and verifiable**. Exactly **one** notebook
([L1006](L1006_lecture.ipynb)) swaps the stub for a real model and runs a genuine multi-step agent,
so you see the same graph drive live Claude.

## A note on the code you'll see

From here the course wires graphs with **LangGraph** and drives the model node through a **LangChain
chat model**, not the raw Anthropic SDK — that is what keeps the agent provider-agnostic. The model
node only ever touches a tiny slice of the interface: `model.bind_tools(tools)`, then
`.invoke(messages)` → an `AIMessage` whose `.tool_calls` say which tools to run. Because that slice
is all the graph needs, the **live** demo (a real `ChatAnthropic` via `init_chat_model("anthropic:…")`,
key through the config seam — never hard-coded) and the stub-model notebooks (the course's
`FakeModel`, which implements the same `.bind_tools()` / `.invoke()`) run the **identical** graph
code. Swap the model object, keep the graph.

One more vocabulary note: LangGraph labels the model-call node **`model`** in the rendered diagram;
this lesson names it the **`agent`** node when we wire it by hand. Same node — `agent` and `model`
are used interchangeably for it throughout L10 and L11.

The one sentence to leave L10 with:

> *An agent is a cyclic graph around a stateless model: an `agent` node calls the model, a `route`
> edge asks "any tool calls?", a `tools` node runs them, and a **back-edge** loops to the model —
> until `route` returns `END` or `recursion_limit` fires; and when a tool breaks, `ToolNode` turns
> the break into a message, not a crash.*

Next: the reference lecture in [L1002_lecture.md](L1002_lecture.md), then the graph-wiring demo
([L1003](L1003_lecture.ipynb)), the labs ([L1004](L1004_lab_empty.ipynb),
[L1005](L1005_lab_empty.ipynb)), and the live multi-step run ([L1006](L1006_lecture.ipynb)).
