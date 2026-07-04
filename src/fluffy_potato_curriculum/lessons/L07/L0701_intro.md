# Tool calling: a tool call is also just tokens

```yaml
title: Tool calling: a tool call is also just tokens
keywords: tool calling, tool call, bind_tools, tool_calls, ToolMessage, tool definition, schema, round-trip, protocol, anthropic, claude
estimated duration: 10
```

> **Lesson:** L07 — Tool calling: how it works.
> **Roadmap:** see this lesson's [objectives.md](../../../../docs/origin/lesson_roadmaps/L07/objectives.md).
> This is a short framing piece. Read it before the written reference lecture
> ([L0702_lecture.md](L0702_lecture.md)) and the four teacher demo notebooks
> (a-tool-call-is-tokens [L0703_lecture.ipynb](L0703_lecture.ipynb), one-wired-round-trip
> [L0704_lecture.ipynb](L0704_lecture.ipynb), trace-the-round-trip [L0706_lecture.ipynb](L0706_lecture.ipynb),
> three-outcomes [L0708_lecture.ipynb](L0708_lecture.ipynb)).
> **Anchor model throughout: Claude Sonnet 4.6** (Claude Haiku 4.5 is the smaller-model contrast in the last demo).

## Where this lesson sits

L01–L06 covered everything a model can do that is purely *text-in, text-out*: tokenization and
cost (L01), prompting roles and structured output (L02), and getting the model to reason better
by changing the *content* of the prompt (L06). In every one of those lessons the model only ever
produced text, and your program read that text. Nothing the model said ever *ran*.

L07 is the first lesson where the model is given the ability to **act** — to request that your
application run a function and feed the result back. This is the bedrock of every agent in the
rest of the course. But the framing from L06 carries over almost word for word:

> *Reasoning is just more tokens. A `<thinking>` block is a contract about **shape**, not a new
> capability.*

becomes, in L07:

> *A tool call is also just more tokens. A tool definition is a contract about **shape**, not a new
> capability — and the model never runs anything; your application does.*

That last clause is the single most important sentence in the lesson. Keep it in mind through
every demo and lab.

## The one idea, said five ways

If you remember nothing else from L07, remember this: **the model does not run your tool.** It
emits a block of tokens that — by training — has the *shape* of a tool-call request. Your
application reads those tokens, decides what to do, runs the real function, and hands the result
back. Said five ways, because it reshapes how you debug, secure, and scale every agent later:

1. The model **proposes**; the application **disposes**. A tool call is a request, not an
   execution.
2. The tool **definition** is a contract about shape (like L06's `<thinking>` tags), not a
   guarantee about behavior. It does not force a call, validate arguments, or stop the model from
   inventing a tool that doesn't exist.
3. A single tool-using exchange is **at minimum four messages**: `HumanMessage →
   AIMessage(tool_calls) → ToolMessage → AIMessage(final)`. Every tool call grows the history —
   that *is* the protocol, not a side effect.
4. The model is **stateless across calls**. The tool definitions and the full history ride along
   in *every* request; the model does not "remember" the tool from last turn.
5. Tools cost tokens **twice over**: the definition is re-sent on every request, and the result
   lives in the history forever after.

## Vocabulary this lesson lands

These five terms recur all the way through L08–L20, so we pin them now:

- **Tool** — a callable in your application (here, a plain Python function) that the model can
  *request* via the tool-call protocol.
- **Tool definition / schema** — a structured description (name, natural-language description,
  JSON-Schema input shape) the model is given alongside the prompt. It tells the model what tools
  exist and how to invoke them. You don't hand-write it in this course: `model.bind_tools([fn])`
  **infers** the definition from a plain typed function — its name, its docstring, and its type
  hints. A typed function *is* the schema.
- **Tool call** — an entry in the model response's `.tool_calls` list saying "I want to call tool
  X with arguments Y" (a `{name, args, id}` record). A request, not an execution.
- **Tool result** — a `ToolMessage` carrying the output of running the requested tool. It closes
  the loop and names the call's id (`tool_call_id`).
- **Round-trip** — one full `model → tool-call → application runs tool → tool-result → model`
  exchange. L07 deals only with *single* round-trips; multi-step loops arrive in L10.

## What L07 deliberately does *not* do

L07 is scoped tight on purpose, the same way L06 stayed prompt-only:

- **One tool, one round-trip.** Every demo and lab uses a single `calculator` tool and a single
  model→tool→model exchange. Multi-tool *selection* and tool-error *design* are **L08**; an agent
  loop over many calls is **L10**. Resisting "just one more tool" is what keeps the protocol legible.
- **Mechanics, not judgment.** L07's job is to make the protocol mechanically obvious — to let you
  *build* a tool-using exchange that works. **L08 ("Designing good tools")** asks the design
  questions: should this be a tool at all, what should it be named, what should the schema look
  like, how should it report failure? We share vocabulary with L08 exactly so you don't relearn
  terms.

## A note on the code you'll see

L07 continues on the same framework client you met in **L03**: LangChain's `ChatAnthropic`. Unlike
the text-only `potato_llm` seam from L01–L02, a LangChain chat model carries tool calls natively —
so there is nothing to reach "under." You bind a plain Python function to the model and invoke it:

```python
from langchain_anthropic import ChatAnthropic
from fluffy_potato_curriculum.common.config import require_anthropic_key

def calculator(expression: str) -> str:
    """Evaluate a simple arithmetic expression."""
    ...

model = ChatAnthropic(model="claude-sonnet-4-6", api_key=require_anthropic_key(), max_tokens=512)
model_with_tools = model.bind_tools([calculator])   # the definition is inferred from the function
reply = model_with_tools.invoke([...])               # reply.tool_calls holds any requested calls
```

The key still loads through the config seam (`require_anthropic_key`) — we never hard-code it. Two
of the labs are **offline pure Python** (no key needed): they hand you a *crafted* tool call (the
`{name, args, id}` shape) to dispatch on and validate, so you can practice the mechanics
deterministically.

The one sentence to leave L07 with:

> *A tool call is a block of tokens the model emitted; your application is the one that reads it,
> runs the function, and hands the result back — and that exchange is always at least four messages.*

Next: the written reference lecture in [L0702_lecture.md](L0702_lecture.md), then the live demos
(L0703 / L0704 / L0708) and the hands-on labs (L0705 / L0707 / L0709).
