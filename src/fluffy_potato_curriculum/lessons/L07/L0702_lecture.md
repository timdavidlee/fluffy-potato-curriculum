# Tool calling: the protocol, the round-trip, and who runs what

```yaml
title: Tool calling: the protocol, the round-trip, and who runs what
keywords: tool calling, tool call, tool result, tool definition, json schema, round-trip, stateless, token cost, hallucinated tool call, validation, langchain, bind_tools, tool_calls, ToolMessage, anthropic, claude
estimated duration: 75
```

> **Lesson:** L07. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L07/objectives.md).
> This is the written reference lecture — thorough on purpose, so a student who missed the verbal
> delivery can rebuild the lesson from the page. The live demos are split one per beat
> ([L0703](L0703_lecture.ipynb) a tool call is tokens, [L0704](L0704_lecture.ipynb) one wired
> round-trip, [L0706](L0706_lecture.ipynb) trace the round-trip, [L0708](L0708_lecture.ipynb)
> three outcomes); hands-on practice is in the L07 labs (L0705 / L0707 / L0709).
> **Anchor model throughout: Claude Sonnet 4.6** (Haiku 4.5 is the smaller-model contrast in Demo 4).

## section 1. The lesson in one claim

### slide 1.1 From text-out to acting

- L01–L06 only ever asked the model for **text**. Even L06's reasoning, scratchpads, and
  self-critique were text the model produced and your code read. Nothing the model said ever *ran*.
- L07 is the first lesson where the model can **act**: it can request that your application run a
  function and feed the result back. This is the foundation of every agent later in the course.
- But it is not magic, and it is not a new model capability. It is a **protocol** the model was
  trained to participate in.

### slide 1.2 A tool call is just more tokens

- The whole lesson rests on one claim, deliberately parallel to L06's: **a tool call is a block of
  tokens the model emitted in a structured shape — not an action the model took.**
- The model is not running code, opening a network connection, or reaching into your filesystem. It
  generates a token sequence that *has the shape of* a tool-call request. LangChain **parses** those
  tokens into a tidy `AIMessage.tool_calls` list for you — but parsing is all it did; nothing ran.
- This is the [L06](../L06/objectives.md) framing reused exactly: there, *reasoning is tokens*;
  here, *a tool call is tokens*. The parallel is intentional — carry the intuition forward, don't
  relearn it.
- diagram: a model response box containing two things side by side — a greyed-out `text` field and a
  highlighted `tool_calls` list — with a caption: "both came from the same emitted tokens; your code
  decides what to do with each."

### slide 1.3 Three actors, one round-trip

- Every single tool-using exchange has exactly three actors. Naming them keeps "who runs what"
  straight for the rest of the course.
- table: the three actors and the one job each performs.

| Actor | What it does | What it does **not** do |
| --- | --- | --- |
| **Model** | decides to call a tool; emits a tool call (surfaced as an `AIMessage.tool_calls` entry: name + arguments + id) | run the function, validate its own arguments |
| **Application** (your code) | reads the tool call, validates arguments, runs the function, returns a `ToolMessage`, continues the conversation | decide *whether* a tool is needed (the model proposes that) |
| **Tool** (the function) | does the real work and returns a value | talk to the model directly — it only ever sees what your application passes it |

- The model **proposes**; the application **disposes**; the tool **computes**. Say it as a chant.

[↑ Back to top](#tool-calling-the-protocol-the-round-trip-and-who-runs-what)

## section 2. Wiring a single tool

### slide 2.1 A tool is a typed function; the definition is derived from it

- Start with a plain Python function that does some side-effect-free work — for this lesson, a
  `calculator(expression: str) -> str` that evaluates a simple arithmetic expression deterministically.
- To make it available to the model you call `model.bind_tools([calculator])`. LangChain reads the
  function's **type hints and docstring** and derives the **tool definition**: a `name`, a
  natural-language `description`, and a JSON-Schema description of the arguments. You do not
  hand-write that JSON — the typed function *is* the source of it.
- The model never sees your Python function. It sees only the derived *definition* — the name, the
  prose, and the argument schema. That is the entire contract. (Demo 1 prints the derived schema so
  you can see it plainly.)

### slide 2.2 The five mechanical steps

- Wiring a tool is the same five steps every time. This is the whole Objective-1 skill:
- table: the five steps, who performs each, and what crosses the boundary.

| # | Step | Who | What crosses the wire |
| --- | --- | --- | --- |
| 1 | **name** the function | you | the function name becomes the id the model will echo back |
| 2 | **describe** it (a typed signature + docstring) and `bind_tools` it | you | the derived tool definition, sent with the prompt |
| 3 | model **decides + emits** a tool call | model | an `AIMessage.tool_calls` entry: name + arguments + a unique call id |
| 4 | **dispatch**: match the name, validate args, run the function | you | the function's return value |
| 5 | **continue**: hand the result back as a `ToolMessage` (same id) | you | the result, tagged with the same id |

- diagram: the five steps as a horizontal pipeline, with steps 1–2 and 4–5 shaded as "application"
  and step 3 shaded as "model".

### slide 2.3 The tool definition is a contract about shape

- A tool definition tells the model "tools of *this shape* exist." Mirroring L06's `<thinking>`
  tags, it adds **zero capability** and makes **zero guarantees about behavior**.
- Concretely, the definition does **not**:
  - force the model to call the tool (it may answer directly instead),
  - validate the arguments at generation time (the model can pass nonsense),
  - stop the model from inventing a tool name that doesn't exist.
- **The application validates; the model proposes.** This is the single sentence to repeat whenever
  a student expects the schema to *enforce* anything. (Deriving the schema from your function makes
  it easier to *write*; it does nothing to make it *enforced*.)

### slide 2.4 The model decides whether to call — that's a reasoning step

- Handing the model a tool is an *offer*, never a *command*. Whether the model reaches for the tool
  is a sampling decision conditioned on the prompt, the conversation, and the tool's description.
- That decision is itself a **reasoning step** — exactly the kind [L06](../L06/objectives.md) was
  about. A vague tool the model can't tell when to use is a tool it will skip. (Reinforce L06; we do
  not re-teach chain-of-thought here.)
- *Foreshadow [L08](../L08/objectives.md):* "what makes a tool worth adding, well-named, and
  well-described?" is L08's whole job. Because the description now *comes from the docstring*, L08's
  advice lands directly on how you write that docstring. L07 only needs you to see that the
  description visibly moves behavior.

[↑ Back to top](#tool-calling-the-protocol-the-round-trip-and-who-runs-what)

## section 3. Tracing one round-trip

### slide 3.1 A round-trip is at least four messages

- The user "asks once," but a single successful tool-using exchange grows the conversation history
  by **four messages**. This four-message shape *is* the protocol — it is not an implementation
  detail you can optimize away.
- diagram: four labeled boxes left to right —
  `HumanMessage(question) → AIMessage(tool call) → ToolMessage(result) → AIMessage(final)` — with the
  producer written under each.
- table: the four messages of a successful round-trip.

| # | Message type | Produced by | Carries |
| --- | --- | --- | --- |
| 1 | `HumanMessage` | the human | the original question |
| 2 | `AIMessage` (with `tool_calls`) | the model | tool name, parsed arguments, a unique call **id** |
| 3 | `ToolMessage` | the **application** | the function's output, tagged with the same **id** |
| 4 | `AIMessage` (text) | the model | the final natural-language answer |

### slide 3.2 The id is the thread tying request to result

- The tool call in message 2 carries a unique **id** (`ai.tool_calls[0]["id"]`). The `ToolMessage`
  in message 3 sets `tool_call_id` to that *same* id — that is how your application says "this
  result answers *that* request."
- With a single tool and a single call, the id feels redundant. It stops being redundant the moment
  more than one call is in flight (a forward-link to [L10](../L10/objectives.md)'s agent loop). Build
  the habit now.
- diagram: an arrow drawn from message 3's `ToolMessage.tool_call_id` back to the matching id in
  message 2's tool call.

### slide 3.3 The tool result is its own kind of message

- This surprises everyone: the tool result does **not** go in an assistant message, and it is not a
  human turn either. In LangChain it is a **`ToolMessage`** — a message role of its own, carrying the
  output and the `tool_call_id` it answers.
- So the conversation reads `Human → AI → Tool → AI`. The `ToolMessage` role marks **protocol
  position** — "this is a tool's result" — regardless of who typed the original question.
- *Under the hood:* on the raw Anthropic wire the result travels as a `tool_result` block inside a
  *user-role* message; other providers shape it differently. LangChain normalizes all of that into
  one `ToolMessage` so your code is the same on every provider. You write `ToolMessage(...)` and
  never touch the wire form.

### slide 3.4 The model is stateless across calls

- To produce message 4, the model was sent messages 1–3 **and** the full tool definition list,
  *again*. It did not "remember" the tool from message 2.
- This is the most common student misconception: *"I told the model about the tool last turn, so it
  remembers."* It does not. **The schema is in the prompt every single time** — `bind_tools` re-sends
  the derived definitions on every `.invoke`.
- Statelessness is why the next section is about cost — re-sending everything on every call is not
  free.

[↑ Back to top](#tool-calling-the-protocol-the-round-trip-and-who-runs-what)

## section 4. What tools cost

### slide 4.1 Tools cost tokens twice over

- Because the model is stateless, a tool is paid for in **two** places on every turn:
  - the tool **definition** is re-sent in the prompt of *every* request, and
  - the tool **result** lives in the message history for *every* subsequent turn.
- This is L01's per-token cost shadow, now attached to tools. Nothing here is hypothetical — the
  demos print the token counts (`ai.usage_metadata`).

### slide 4.2 A worked cost example

- table: a 500-token tool definition across a 10-turn conversation, before any tool is even called.

| Quantity | Value |
| --- | --- |
| Tool definition size | ~500 tokens |
| Conversation length | 10 turns |
| Input tokens spent on the definition alone | ~5,000 tokens |
| Tool calls required for that cost | **zero** — it's the definition, re-sent every turn |

- The lesson: every tool you add is a standing tax on every request, paid whether or not the model
  uses it. This is why [L08](../L08/objectives.md) asks "should this be a tool at all?" and why
  L16 (context management) comes back to it.

### slide 4.3 Where this cost reasoning returns

- **[L08](../L08/objectives.md)** — "more tools = more schema text in every prompt, more chances to
  mis-pick." The cost is one reason *not* to add a tool.
- **[L12](../L12/objectives.md)** (model power) and **L16** (context management) revisit tool cost as
  a budget you actively manage. Carry the "twice over" framing forward.

[↑ Back to top](#tool-calling-the-protocol-the-round-trip-and-who-runs-what)

## section 5. Three outcomes, and why you validate

### slide 5.1 Handing the model a tool has three observable outcomes

- Give the model a tool and a prompt, and exactly one of three things happens. Being able to look at
  a response and say *which* happened is Objective 2.
- table: the three outcomes and what your application sees.

| Outcome | Response contains | What it means |
| --- | --- | --- |
| **Calls the tool** | `ai.tool_calls` is non-empty, with valid arguments | the model judged the tool useful and proposed a well-formed call |
| **Answers without it** | `ai.tool_calls` is empty; only `ai.text` | the model judged the tool unnecessary — a registered tool is an *option*, never an obligation |
| **Calls it with bad arguments** | `ai.tool_calls` has an entry with malformed / missing / invented arguments | the model hallucinated; **your application must catch this** |

### slide 5.2 The model can hallucinate a tool call

- The schema did not stop any of this at generation time: wrong argument *types*, a *missing*
  required argument, an *extra* invented argument, even a tool *name that doesn't exist*.
- This is the L07 analogue of [L06](../L06/objectives.md)'s tag-violation moment: **showing one
  hallucination teaches more than ten clean runs**, because it proves the contract is best-effort.
- The remedy is not a better schema (that's an L08 conversation) — it is that **the application
  validates; the model proposes.** Validation is not optional. (LangChain hands you a clean
  `tool_calls` dict, but a clean *shape* is not a valid *value* — the arguments inside can still be
  nonsense.)

### slide 5.3 Tool calls are not deterministic

- The same prompt and the same schema can produce a call on one run and a skip on the next, with
  slightly different arguments each time.
- This is *why* you validate every call rather than trusting a clean dry-run. A round-trip that
  worked at your desk can fumble in class — that variance is the point, not a bug.

### slide 5.4 A brief word on forcing a call

- Most chat models expose a `tool_choice` control (auto / any / none / a specific tool) — in
  LangChain, `model.bind_tools([...], tool_choice=...)` — that *biases* the decision toward or away
  from a tool call.
- But even *forcing* a call does not guarantee **well-formed arguments** — it only guarantees that
  *some* tool call is attempted. Forcing changes whether the model calls, not whether it calls
  *correctly*.
- We mention it and move on: the deeper `tool_choice` design conversation belongs to
  [L08](../L08/objectives.md).

[↑ Back to top](#tool-calling-the-protocol-the-round-trip-and-who-runs-what)

## section 6. Common confusions to retire

### slide 6.1 The misconceptions, named

- table: the confusion, and the one-line correction to give every time it surfaces.

| Confusion | Correction |
| --- | --- |
| "The model runs the tool." | It does not. The **application** runs the tool; the model only emits a request, which LangChain surfaces as `ai.tool_calls`. |
| "If I define a tool, the model will use it." | Not necessarily. Tool selection is a sampling decision conditioned on the prompt and the tool's *description* (its docstring). |
| "Tool calls are deterministic." | They are not. Same prompt + schema can call, skip, or pass different arguments across runs. |
| "The tool result is part of the assistant message." | It is not. In LangChain it is its own `ToolMessage` (role `tool`), tagged with the `tool_call_id` it answers. |
| "More tools = better agent." | More tools means more schema in every prompt, more mis-picks, more edge cases. (Forward-link to [L08](../L08/objectives.md).) |
| "I can force the model to always call this tool." | `tool_choice` biases the decision, but forced choice still does not guarantee well-formed arguments. |

[↑ Back to top](#tool-calling-the-protocol-the-round-trip-and-who-runs-what)

## section 7. Bridge to L08

### slide 7.1 From "it works" to "is it good?"

- By the end of L07 you can **build a tool-using exchange that works** — wire one tool, trace one
  round-trip, and validate a hallucinated call. That is the mechanics.
- [L08](../L08/objectives.md) ("Designing good tools") takes those mechanics and asks the **design**
  questions: *should* this be a tool, what should we name it, what should the schema look like, how
  should it report failure?
- A useful handoff: by the end of L07 you can make a tool call *work*; by the end of L08 you can argue
  about whether the tool should exist at all and whether the schema is good.

### slide 7.2 What to carry forward

- **Vocabulary** — `tool`, `tool definition`, `tool call`, `tool result`, `round-trip`. L08 reuses
  every term; you should not have to relearn one.
- **The validation reflex** — "the application validates; the model proposes" becomes L08's launchpad
  for tool-error *design*.
- One sentence to L08: *you can now wire a tool that works; next you'll decide whether it should
  exist and how to shape it well.*

[↑ Back to top](#tool-calling-the-protocol-the-round-trip-and-who-runs-what)
