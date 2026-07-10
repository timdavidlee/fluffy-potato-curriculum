# Shallow agents in LangGraph: your L10 loop, in one line

```yaml
title: "Shallow agents in LangGraph: your L10 loop, in one line"
keywords: shallow agent, create_agent, langchain, langgraph, ChatAnthropic, model tool model loop, back-edge, cycle, agent node, tools node, recursion limit, system prompt, sonnet, claude, framework
estimated duration: 10
```

> **Lesson:** L11 — Shallow agents in LangGraph.
> **Roadmap:** see this lesson's [objectives.md](../../../../docs/origin/lesson_roadmaps/L11/objectives.md).
> This is a short framing piece. Read it before the "what `create_agent` wraps" slide
> outline ([L1102_lecture.md](L1102_lecture.md)), the build-and-run demo notebook
> ([L1103_lecture.ipynb](L1103_lecture.ipynb)), the hands-on lab
> ([L1104](L1104_lab_empty.ipynb)), and the config-surface slide outline
> ([L1105_lecture.md](L1105_lecture.md)).
> **Anchor model for the live path: Claude Sonnet 4.6.**

## Where this lesson sits

In [L10](../L10/L1001_intro.md) you built an agent from nothing: a **model → tool → model** loop,
wired by hand as a cyclic **`StateGraph`**. You wrote the `agent` node, the `route` conditional
edge, the `ToolNode`, the `add_messages` reducer, and the `tools → agent` **back-edge** — every
piece by hand. The one sentence you left L10 with was:

> *An agent is a cyclic graph around a stateless model: an `agent` node calls the model, a `route`
> edge asks "any tool calls?", a `tools` node runs them, and a back-edge loops around — until
> `route` returns `END` or `recursion_limit` fires.*

L11 cashes in the punchline L10's last demo previewed: **"every framework you'll meet is a
fancier version of the loop you wrote."** Here is that fancier version. LangChain's
**`create_agent`** takes a model and a list of tools and hands you back *the same loop* — running,
tested, production-shaped — in **one function call**:

```python
from langchain.agents import create_agent

agent = create_agent(model, [calculator, lookup, flaky_fetch], system_prompt=...)
```

That single line is the whole lesson. The control flow does not change — it is still model → tool
→ model until termination. What changes is **who wires the graph**: the nodes and back-edge, the
tool-call routing, the message-history bookkeeping, and the step cap are now the framework's job,
not yours.

## What "shallow" means

The title word **shallow** is load-bearing, so define it up front:

> A **shallow agent** is a *single tool-calling loop* — one model, one set of tools, one decision
> point that either calls a tool or finishes.

That is *exactly* the L10 loop. Shallow is contrasted with **deep** agents (planning, persistent
memory, sub-todos, reflection), which are a later, heavier choice (L18) — named here only as *what
we are not building yet*. **Shallow does not mean lesser:** most production agents are shallow. A
single well-designed tool-calling loop is a complete, useful agent.

## The one idea, said three ways

If you remember nothing else from L11, remember this: **`create_agent` is not magic — it is your
L10 loop, packaged.**

1. **It's the same loop.** `create_agent` introduces no new *control flow*. Model → tool → model
   until termination is the L10 skeleton, unchanged. You will run the rebuilt agent on the two
   L10 tasks and watch it issue the *same tool sequence* and stop the *same way*.
2. **It draws as a small graph.** The loop `create_agent` wraps is a two-node graph: an **`agent`**
   node (call the model), a **`tools`** node (run what it asked for), a **back-edge** from `tools`
   back to `agent`, and a conditional exit out of `agent` (tool call → run tools; plain text →
   finish). That **back-edge is the cycle**, and *the cycle is the agent* — it is the one thing
   that turned the acyclic workflows of [L03](../L03/objectives.md)/[L05](../L05/objectives.md)
   into an agent.
3. **The framework gives you the boring parts for free.** The graph wiring (L10's `StateGraph` +
   `tools → agent` back-edge), the routing (L10's hand-written `route`, now the prebuilt
   `tools_condition`), the message accumulation (L10's `add_messages` reducer), a recursion/step
   limit (L10's `recursion_limit`), and tool execution (L10's `ToolNode`) — all supplied. That
   convenience *is* the value proposition.

## A note on the client you'll see

L10 drove the model through a LangChain chat model already. L11 keeps going in that direction but
takes one deliberate step: it uses the **native LangChain `ChatAnthropic` client directly**, *not*
the repo's `PotatoLLMClient` seam you saw earlier in the course. This is on purpose and worth
saying out loud — **frameworks bring their own client abstraction**. When you adopt LangChain, you
adopt its model object. The API key still loads through the same `common/config.py` config seam
(`ChatAnthropic` reads `ANTHROPIC_API_KEY` from the environment the seam populates); only the
*client object* is the framework's now.

Because the demo and lab are built the LangChain way, they run two ways with the *same* code:
offline against the course's scripted `FakeModel` (deterministic, no key, no cost — this is how a
restart-and-run-all stays green), and live against `ChatAnthropic` (Sonnet 4.6) when a key is
present. Swap the model object, keep the agent — the same interchangeability you relied on in L10.

## Where the one-liner ends

`create_agent`'s config surface for a shallow agent is small and worth memorizing: the **model**,
the **tools**, and the **system prompt**. That's it — the message-history state and the graph are
managed for you (no `add_messages` reducer to declare, no nodes or edges to wire). The last thing L11 teaches is *when the
one-liner stops being enough*: the moment your control flow stops being a single loop and you need a
second model for one step, a branch that isn't just tool-or-finish, a custom node, or state beyond
the message list. That is exactly when you drop below `create_agent` to an explicit `StateGraph` —
and building that graph by hand, plus the named patterns on top of it (ReAct, plan-and-execute,
supervisor), is **[L15](../../CURRICULUM_PRD.md)'s** job. L11 points at that door without walking
through it.

The one sentence to leave L11 with:

> *A shallow agent is the L10 loop; `create_agent` is the one line that gives it to you — model +
> tools + prompt in, a running agent out — and the loop, routing, message bookkeeping, and step cap
> are now the framework's to keep.*

Next: the "what `create_agent` wraps" slide outline in
[L1102_lecture.md](L1102_lecture.md), then the build-and-run demo
([L1103](L1103_lecture.ipynb)), the lab ([L1104](L1104_lab_empty.ipynb)), and the config-surface
outline ([L1105](L1105_lecture.md)).
