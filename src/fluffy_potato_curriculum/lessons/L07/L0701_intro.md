# Tool calling: a tool call is also just tokens

```yaml
title: Tool calling: a tool call is also just tokens
keywords: tool calling, tool use, tool call, tool result, tool definition, schema, round-trip, protocol, langchain, bind_tools, tool_calls, ToolMessage, anthropic, claude
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
3. A single tool-using exchange is **at minimum four messages**:
   `HumanMessage → AIMessage(tool call) → ToolMessage(result) → AIMessage(final)`. Every tool call
   grows the history — that *is* the protocol, not a side effect.
4. The model is **stateless across calls**. The tool definitions and the full history ride along
   in *every* request; the model does not "remember" the tool from last turn.
5. Tools cost tokens **twice over**: the definition is re-sent on every request, and the result
   lives in the history forever after.

## Vocabulary this lesson lands

These five terms recur all the way through L08–L20, so we pin them now:

- **Tool** — a callable in your application (here, a plain typed Python function) that the model
  can *request*. You hand it to the model with `model.bind_tools([...])`.
- **Tool definition / schema** — a structured description (name, natural-language description,
  JSON-Schema input shape) the model sees alongside the prompt. With LangChain you don't hand-write
  it: it is **derived from your function's type hints and docstring** when you bind the tool.
- **Tool call** — the model's request to run tool X with arguments Y. LangChain surfaces it as an
  entry in `AIMessage.tool_calls`, each a `{"name", "args", "id"}` dict. A request, not an execution.
- **Tool result** — the output of running the requested tool, handed back as a `ToolMessage` that
  references the call's **id**. It closes the loop.
- **Round-trip** — one full `model → tool call → application runs tool → tool result → model`
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

From L03 on, the course drives every model call through a **LangChain chat model**
(`ChatAnthropic`, and its siblings `ChatOpenAI`, `init_chat_model("provider:model")`, …) rather
than a raw provider SDK. The payoff is that the tool code is **model-agnostic**: swap
`ChatAnthropic` for `ChatOpenAI` and the *same* tool-calling code runs unchanged. That
interchangeability is the whole reason we don't reach for a single vendor's wire format.

Concretely, an L07 demo looks like this:

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, ToolMessage
from fluffy_potato_curriculum.common.config import require_anthropic_key


def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression and return the exact result."""
    ...


model = ChatAnthropic(model="claude-sonnet-4-6", api_key=require_anthropic_key())
bound = model.bind_tools([calculator])          # LangChain derives the schema from the function
ai = bound.invoke([HumanMessage("What is 18374 * 92431?")])
for call in ai.tool_calls:                       # each: {"name", "args", "id"}
    ...
```

The tool is a **plain typed function** — you do not hand-write a JSON schema; `bind_tools` derives
it from the signature and docstring. The tool call comes back as `AIMessage.tool_calls` (a
normalized list of dicts), and you return the result as a `ToolMessage`. *Under the hood* the
Anthropic wire carries these as `tool_use` / `tool_result` blocks; LangChain normalizes them so the
same code runs on any provider — you never touch the raw blocks.

The key still loads through the config seam (`require_anthropic_key`) — we never hard-code it. Two
of the labs are **offline** (no key needed): they script a deterministic model with the course's
`FakeModel` so you can practice the mechanics — inspect a tool call, dispatch it, validate it —
with the same interface and no network.

The one sentence to leave L07 with:

> *A tool call is a block of tokens the model emitted; your application is the one that reads it,
> runs the function, and hands the result back — and that exchange is always at least four messages.*

Next: the written reference lecture in [L0702_lecture.md](L0702_lecture.md), then the live demos
(L0703 / L0704 / L0708) and the hands-on labs (L0705 / L0707 / L0709).
