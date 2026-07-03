# Tool calling: the protocol, the round-trip, and who runs what

```yaml
title: Tool calling: the protocol, the round-trip, and who runs what
keywords: tool calling, tool_use, tool_result, tool definition, json schema, round-trip, stateless, token cost, hallucinated tool call, validation, anthropic, claude
estimated duration: 75
```

> **Lesson:** L07. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L07/objectives.md).
> This is the written reference lecture — thorough on purpose, so a student who missed the verbal
> delivery can rebuild the lesson from the page. The live demos are split one per beat
> ([L0703](L0403_lecture.ipynb) a tool call is tokens, [L0704](L0404_lecture.ipynb) one wired
> round-trip, [L0706](L0406_lecture.ipynb) trace the round-trip, [L0708](L0408_lecture.ipynb)
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
  generates a token sequence that *has the shape of* a tool-call request. Your application reads
  those tokens and does the work.
- This is the [L06](../L06/objectives.md) framing reused exactly: there, *reasoning is tokens*;
  here, *a tool call is tokens*. The parallel is intentional — carry the intuition forward, don't
  relearn it.
- diagram: a model response box containing two blocks side by side — a greyed-out `text` block and a
  highlighted `tool_use` block — with a caption: "both are just tokens; your code decides what to do
  with each."

### slide 1.3 Three actors, one round-trip

- Every single tool-using exchange has exactly three actors. Naming them keeps "who runs what"
  straight for the rest of the course.
- table: the three actors and the one job each performs.

| Actor | What it does | What it does **not** do |
| --- | --- | --- |
| **Model** | decides to call a tool; emits a `tool_use` block (name + arguments + id) | run the function, validate its own arguments |
| **Application** (your code) | reads the block, validates arguments, runs the function, formats the result, continues the conversation | decide *whether* a tool is needed (the model proposes that) |
| **Tool** (the function) | does the real work and returns a value | talk to the model directly — it only ever sees what your application passes it |

- The model **proposes**; the application **disposes**; the tool **computes**. Say it as a chant.

[↑ Back to top](#tool-calling-the-protocol-the-round-trip-and-who-runs-what)

## section 2. Wiring a single tool

### slide 2.1 A tool is a function plus a description of it

- Start with a plain Python function that does some side-effect-free work — for this lesson, a
  `calculator(expression: str) -> str` that evaluates a simple arithmetic expression deterministically.
- To make it available to the model you wrap it in a **tool definition**: a `name`, a
  natural-language `description` of what it does and when to use it, and a JSON-Schema `input_schema`
  describing the arguments.
- The model never sees your Python function. It sees only the *definition* — the name, the prose, and
  the argument schema. That is the entire contract.

### slide 2.2 The five mechanical steps

- Wiring a tool is the same five steps every time. This is the whole Objective-1 skill:
- table: the five steps, who performs each, and what crosses the boundary.

| # | Step | Who | What crosses the wire |
| --- | --- | --- | --- |
| 1 | **name** the function | you | a string id the model will echo back |
| 2 | **describe** it (prose + JSON-Schema) | you | the tool definition, sent with the prompt |
| 3 | model **decides + emits** a `tool_use` block | model | name + arguments + a unique call id |
| 4 | **dispatch**: match the name, validate args, run the function | you | the function's return value |
| 5 | **continue**: send the result back as a `tool_result` block | you | the result, tagged with the same id |

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
  a student expects the schema to *enforce* anything.

### slide 2.4 The model decides whether to call — that's a reasoning step

- Handing the model a tool is an *offer*, never a *command*. Whether the model reaches for the tool
  is a sampling decision conditioned on the prompt, the conversation, and the tool's description.
- That decision is itself a **reasoning step** — exactly the kind [L06](../L06/objectives.md) was
  about. A vague tool the model can't tell when to use is a tool it will skip. (Reinforce L06; we do
  not re-teach chain-of-thought here.)
- *Foreshadow [L08](../L08/objectives.md):* "what makes a tool worth adding, well-named, and
  well-described?" is L08's whole job. L07 only needs you to see that the description visibly moves
  behavior.

[↑ Back to top](#tool-calling-the-protocol-the-round-trip-and-who-runs-what)

## section 3. Tracing one round-trip

### slide 3.1 A round-trip is at least four messages

- The user "asks once," but a single successful tool-using exchange grows the conversation history
  by **four messages**. This four-message shape *is* the protocol — it is not an implementation
  detail you can optimize away.
- diagram: four labeled boxes left to right —
  `user(question) → assistant(tool_use) → user(tool_result) → assistant(final)` — with the producer
  written under each.
- table: the four messages of a successful round-trip.

| # | Role | Block type | Produced by | Carries |
| --- | --- | --- | --- | --- |
| 1 | `user` | `text` | the human | the original question |
| 2 | `assistant` | `tool_use` | the model | tool name, parsed arguments, a unique call **id** |
| 3 | `user` | `tool_result` | the **application** (wearing the user role) | the function's output, tagged with the same **id** |
| 4 | `assistant` | `text` | the model | the final natural-language answer |

### slide 3.2 The id is the thread tying request to result

- The `tool_use` block in message 2 carries a unique **call id**. The `tool_result` block in message
  3 names that *same* id — that is how your application says "this result answers *that* request."
- With a single tool and a single call, the id feels redundant. It stops being redundant the moment
  more than one call is in flight (a forward-link to [L10](../L10/objectives.md)'s agent loop). Build
  the habit now.
- diagram: an arrow drawn from the id in message 3's `tool_result` back to the matching id in message
  2's `tool_use`.

### slide 3.3 The tool result rides in a *user-role* message

- This surprises everyone: the tool result does **not** go in an assistant message. By convention the
  application puts it in a **user-role** message — your code is speaking on the user's behalf.
- So the conversation still alternates `assistant ↔ user` even though one of those "users" is your
  program. The role labels mark **protocol position**, not who is human.

### slide 3.4 The model is stateless across calls

- To produce message 4, the model was sent messages 1–3 **and** the full tool definition list,
  *again*. It did not "remember" the tool from message 2.
- This is the most common student misconception: *"I told the model about the tool last turn, so it
  remembers."* It does not. **The schema is in the prompt every single time.**
- Statelessness is why the next section is about cost — re-sending everything on every call is not
  free.

[↑ Back to top](#tool-calling-the-protocol-the-round-trip-and-who-runs-what)

## section 4. What tools cost

### slide 4.1 Tools cost tokens twice over

- Because the model is stateless, a tool is paid for in **two** places on every turn:
  - the tool **definition** is re-sent in the prompt of *every* request, and
  - the tool **result** lives in the message history for *every* subsequent turn.
- This is L01's per-token cost shadow, now attached to tools. Nothing here is hypothetical — the
  demos print the token counts.

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
  a transcript and say *which* happened is Objective 2.
- table: the three outcomes and what your application sees.

| Outcome | Response contains | What it means |
| --- | --- | --- |
| **Calls the tool** | a `tool_use` block with valid arguments | the model judged the tool useful and proposed a well-formed call |
| **Answers without it** | only a `text` block, no `tool_use` | the model judged the tool unnecessary — a registered tool is an *option*, never an obligation |
| **Calls it with bad arguments** | a `tool_use` block with malformed / missing / invented arguments | the model hallucinated; **your application must catch this** |

### slide 5.2 The model can hallucinate a tool call

- The schema did not stop any of this at generation time: wrong argument *types*, a *missing*
  required argument, an *extra* invented argument, even a tool *name that doesn't exist*.
- This is the L07 analogue of [L06](../L06/objectives.md)'s tag-violation moment: **showing one
  hallucination teaches more than ten clean runs**, because it proves the contract is best-effort.
- The remedy is not a better schema (that's an L08 conversation) — it is that **the application
  validates; the model proposes.** Validation is not optional.

### slide 5.3 Tool calls are not deterministic

- The same prompt and the same schema can produce a call on one run and a skip on the next, with
  slightly different arguments each time.
- This is *why* you validate every call rather than trusting a clean dry-run. A round-trip that
  worked at your desk can fumble in class — that variance is the point, not a bug.

### slide 5.4 A brief word on forcing a call

- Most APIs offer a `tool_choice` control (auto / any / none / a specific tool) that *biases* the
  decision toward or away from a tool call.
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
| "The model runs the tool." | It does not. The **application** runs the tool; the model only emits a request shaped like a tool call. |
| "If I define a tool, the model will use it." | Not necessarily. Tool selection is a sampling decision conditioned on the prompt and the tool's *description*. |
| "Tool calls are deterministic." | They are not. Same prompt + schema can call, skip, or pass different arguments across runs. |
| "Tool results are part of the assistant message." | They are not. By convention the result goes in a **user-role** message — your app speaking for itself. |
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
