# L04: Teacher-led demos — Tool calling: how it works

> Sibling docs: [objectives.md](objectives.md) (what the lesson aims for), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md).
>
> **Audience for this file:** the teacher running L04. Every demo below is *teacher-driven, no student participation*. Student-driven exercises live in the L04 labs (separate file).

## How to read this file

Each demo is a self-contained block with:

- **Goal** — the single insight the demo should land. Tied to a learning objective from [objectives.md](objectives.md).
- **Pre-flight** — what the teacher needs loaded before class.
- **Live script** — the order of operations during the demo. Treat it as a checklist, not a teleprompter.
- **What to highlight** — the moment(s) where the teacher should slow down and call out the takeaway out loud.
- **If the demo misbehaves** — graceful fallback for when the model surprises you (because it will).

The demos are ordered to build the protocol from the inside out: Demo 1 shows what a tool call *is* (a block of tokens), Demo 2 wires a full round-trip end-to-end, Demo 3 slows down and traces that round-trip message by message, and Demo 4 breaks it on purpose to show the three observable outcomes. Run them in order on the first delivery — Demo 3 dissects the exact exchange Demo 2 produced, and Demo 4's failures only read as failures once Demos 2–3 have established what success looks like.

This lesson is the first time the model is given the ability to *act*. The single most important thing every demo must reinforce — stated four different ways across the four demos — is that **the model never runs anything; it emits structured tokens and the application does the work.** If students leave with only one sentence, it should be that one.

## Pre-flight (once, at the top of the lesson)

The teacher should have, before the first demo starts:

- A working REPL or notebook with the project's Claude SDK setup (per the project's `uv` env).
- A **demo harness** that wraps every model call and prints, for each turn: the full list of content blocks in the response (so a `text` block and a `tool_use` block are both visible side by side), the tool-use request (name + parsed arguments + the call/use id), the tool result handed back (with the id it answers), and per-call `input_tokens` / `output_tokens` / wall-clock time. This is the same wrapper described in [L03's demos](../L03/demos_or_activities.md) and extended again in [L05's demos](../L05/demos_or_activities.md) — here it must surface the *raw block structure* of a response, because the whole lesson is about seeing the tool-call block as tokens, not as a magic event.
- One pre-built tool: a `calculator(expression: str) -> str` function that evaluates a simple arithmetic expression deterministically, plus its tool definition (name, description, JSON-Schema for the single `expression` argument). This one tool carries Demos 1–4 — resist adding more; L04 is deliberately a *single-tool* lesson (multi-tool selection is [L05](../L05/objectives.md), the agent loop over many calls is L07).
- A way to display the tool definition (name, description, input schema) on screen next to the model's output, so the audience sees exactly what the model was handed.
- A second model client for Demo 4's hallucination beat. **Primary model: Claude Sonnet 4.6** (the course anchor). **Cheap contrast: Claude Haiku 4.5** — a smaller model is more likely to fumble tool selection or arguments, which makes the "the application must validate" point land harder.

> Why pre-built and pre-loaded: L04 lives or dies on the audience seeing the *same* exchange slowly. If the teacher live-types a tool definition or a prompt mid-demo, the round-trip pacing breaks and the protocol reads as "some plumbing happened" instead of "here is each message, in order, and who produced it."

<!-- *NEED INPUT*: which API/SDK anchors the demos — this is the same open question raised in objectives.md (Anthropic Python SDK vs. OpenAI-style vs. generic-pseudocode-with-pinned-SDK). It propagates to the exact block names the harness prints (tool_use vs. function_call) and to how the round-trip is displayed. Pin once, course-wide, and reuse here. -->

## Demo 1 — A tool call is just more tokens (Objective 3)

**Goal:** show that a tool call is a *block of tokens the model emitted*, not an action the model took. Land the framing from [objectives.md](objectives.md): *tool calling is a protocol the model was trained to participate in, not a runtime capability.* This is the conceptual anchor for the whole lesson — run it first, before any working round-trip.

**Pre-flight:**

- The `calculator` tool definition loaded, but **no dispatch code wired up yet** — for this demo the teacher deliberately does *not* run the function. The point is to stop the moment the model emits the tool-call block and inspect it.
- A prompt that should plausibly trigger the tool: *"What is 18,374 × 92,431?"* — arithmetic the model is unreliable at, so it has a real reason to reach for the calculator.

**Live script:**

1. First, run the prompt **with no tools registered at all.** The model answers directly — often with a confident, wrong number. Note it: this is the model doing what it has done in L01–L03, text in, text out.
2. Now register the `calculator` tool definition and run the *exact same prompt*. Stop as soon as the response comes back — do **not** run the calculator.
3. Print the raw response structure with the harness. Point at the `tool_use` block: it has a tool name (`calculator`), an arguments object (`{"expression": "18374 * 92431"}`), and a unique call/use id. Read each field aloud.
4. Emphasize what just happened: nothing was computed. The model did not multiply anything. It emitted a block of tokens that *says* "I would like the calculator run with this expression." The number in the arguments came from the model's tokens, not from arithmetic.

**What to highlight:**

- The tool-call block is just more structured tokens — the same kind of shape-contract as the `<thinking>` / `<answer>` tags from [L03](../L03/objectives.md), except this time the surrounding application is expected to *act* on the shape. Reinforce that L03 framing explicitly; do not re-teach it.
- Three actors exist, and only one of them has done anything so far: the **model** proposed a call, the **application** (us) has the block in hand and has not acted, the **tool** (the calculator function) has not run. Name all three now — the rest of the lesson fills in the remaining steps.
- The decision to emit the tool call *instead of* answering directly is itself a reasoning step — the same kind of judgment from L03. Reinforce, don't re-teach: a vague tool the model can't tell when to use is a tool it will skip (forward-link to [L05](../L05/objectives.md)).

**If the demo misbehaves:**

- If the model answers the arithmetic directly *even with the tool registered* (skips the tool), that is a teaching gift, not a failure: it proves the schema is an *offer*, not a *command*. Show the response has only a `text` block and no `tool_use` block. Then make the prompt more obviously tool-shaped (*"Use the calculator to compute 18,374 × 92,431."*) and re-run to get the tool-call block. Name the contrast: the model chose.
- If the model both answers in text *and* emits a tool call in the same response (a `text` block plus a `tool_use` block), lean in — that previews Demo 3's point that a single response can carry more than one block.

## Demo 2 — One wired round-trip, end to end (Objective 1)

**Goal:** complete the loop Demo 1 stopped halfway through: dispatch the tool call, run the real function, hand the result back, and get the model's final answer. Land the framing from [objectives.md](objectives.md): *wiring a tool is name → description → schema → dispatch → result → continue.*

**Pre-flight:**

- The `calculator` tool from Demo 1, now with the dispatch code wired: read the `tool_use` block, check the tool name, pull the `expression` argument, call `calculator(...)`, capture the string result.
- Reuse Demo 1's prompt (*"What is 18,374 × 92,431?"*) so students see the technique complete on something familiar.

**Live script:**

1. Recap Demo 1 in one line: the model emitted a `tool_use` block; last time we stopped here.
2. Now run the dispatch: print the tool name the application matched on, the arguments it extracted, and the value `calculator(...)` returned. Show that *this* number is real — the function computed it.
3. Build the next message: a user-role message carrying a `tool_result` block that references the same call/use id from the `tool_use` block and contains the function's output.
4. Send the full conversation back to the model (original user message + the assistant's tool-use turn + the new tool-result turn). The model returns a final, natural-language answer that uses the real number.
5. Put the wrong number from Demo 1, step 1 (model answering with no tool) next to the right number from the calculator. Same model, same question — the tool closed the accuracy gap.

**What to highlight:**

- Walk the five mechanical steps out loud as they happen: **name** the function, **describe** it, give it a **schema**, **dispatch** on the returned call, run the **result**, **continue** the conversation. This is the entire Objective-1 skill in one pass.
- The application is the one that validated the arguments and ran the function. The model proposed; the application disposed. (Reinforce the Demo 1 framing — say it again, in these new words.)
- The `tool_result` goes in a **user-role** message, not an assistant message. The application is speaking on the user's behalf. This surprises students and is worth pausing on — it sets up Demo 3's message-by-message trace.

**If the demo misbehaves:**

- If the model, after receiving the tool result, calls the tool *again* instead of answering, don't fight it — name it: the model decided it needed another round-trip. L04 only promises a *single* round-trip; multi-step loops are [L07](../L07/objectives.md). Send the second result back manually to reach a final answer and move on.
- If the calculator raises on a malformed expression, that is Demo 4's territory arriving early — note it, hand back a clean result for now, and promise the failure case is coming.

## Demo 3 — Trace the round-trip, message by message (Objective 2)

**Goal:** show that a single tool-using exchange is *at minimum four messages* in the conversation history, and that the call/use id is the thread tying request to result. Land the framing from [objectives.md](objectives.md): *every tool call grows the message history — that is the protocol, not a side effect.*

**Pre-flight:**

- The completed exchange from Demo 2, captured so the full message list can be printed and walked slowly. No new model calls are required for this demo — it dissects the transcript Demo 2 already produced.
- A simple on-screen diagram or four labeled boxes: `user → assistant(tool_use) → user(tool_result) → assistant(final)`.

**Live script:**

1. Print the full conversation history from Demo 2 as an ordered list of messages, with each message's role and the *types* of blocks it contains.
2. Walk the four messages in order, naming the role and the producer of each:
   - **Message 1 — user:** the original question. Produced by the human.
   - **Message 2 — assistant, `tool_use` block:** the model's request to call `calculator`. Produced by the model. Read off its call/use id.
   - **Message 3 — user, `tool_result` block:** the calculator's output. Produced by the *application*, wearing the user role. Point at the call/use id — it matches Message 2.
   - **Message 4 — assistant, `text` block:** the final answer. Produced by the model.
3. Draw the id-matching arrow explicitly: the `tool_result` in Message 3 names the same id as the `tool_use` in Message 2. That id is how the application says "this result answers *that* request" — essential once there is more than one call in flight (forward-link to L07).
4. Count it out: the user "asked once," but the history grew by four messages. Underline that every future tool call repeats this growth.

**What to highlight:**

- The conversation alternates assistant ↔ user even though one of those "users" is the application speaking for itself. The role labels are about *protocol position*, not about who is human.
- The model is **stateless across calls** — Message 4's request had to include Messages 1–3 *and* the tool definition again. The model did not "remember" the tool from Message 2; the schema rode along in the prompt every time. This is the single most common student misconception; name it here.
- Tools cost tokens **twice over**: the tool *definition* is re-sent on every request, and the tool *result* lives in the history for every subsequent turn. A 500-token tool definition across a 10-turn chat is ~5,000 input tokens before the tool is even called. Forward-link to [L09](../L09/objectives.md) (model power) and L14 (context management), which return to this cost.

**If the demo misbehaves:**

- This demo replays a captured transcript, so it should not vary. If the teacher prefers a live re-run and the model produces a *different* number of messages (e.g. an extra round-trip), use the actual transcript — count whatever messages are really there and note that four is the *minimum*, not a fixed number.

## Demo 4 — Three outcomes, including a hallucinated call (Objective 2 + 3)

**Goal:** show the three observable outcomes of handing a model a tool — it calls the tool, it answers without the tool, or it calls the tool with malformed/hallucinated arguments — and show that the **application**, not the model, is responsible for catching the bad case. Land the framing from [objectives.md](objectives.md): *the schema is a contract about shape, not a guarantee about behavior.*

**Pre-flight:**

- The same `calculator` tool. Three prompts prepared to elicit the three outcomes:
  - **P1 — clean tool call:** *"What is 47,219 × 8,803?"* (arithmetic the model should defer to the tool).
  - **P2 — answers without the tool:** *"What is 2 + 2?"* (trivial; the model answers directly and usually skips the tool — adding a tool to a task the model already owns is wasted overhead, a forward-link to [L05](../L05/objectives.md)'s "tool or no tool?" demo).
  - **P3 — provoke a malformed call:** a prompt that nudges the model toward a bad argument — e.g. *"Use the calculator to work out the average of these: 12, 19, and 'twenty'."* The non-numeric token tends to produce a malformed `expression`. Have a backup prompt warmed up in case the model sanitizes the input cleanly.
- The dispatch code from Demo 2, but with its validation step made **visible**: when the arguments fail to validate (or the function raises), the harness prints the rejection rather than crashing.
- The Haiku 4.5 client ready, in case the primary model is too well-behaved to fumble P3.

**Live script:**

1. Run **P1**. Outcome one: a clean `tool_use` block, valid arguments, a real result, a correct final answer. (A fast recap of Demos 1–2.)
2. Run **P2**. Outcome two: the response has only a `text` block, no `tool_use`. The model judged the tool unnecessary. Note that a registered tool is an *option*, never an obligation.
3. Run **P3**. Outcome three: the model emits a `tool_use` block whose arguments are malformed (a non-numeric expression, a missing field, or an invented argument name). Let the application's validation **catch and reject** it — show the rejection message the harness prints.
4. If the primary model handles P3 cleanly, re-run P3 on **Haiku 4.5** to surface the fumble. Make the model-class contrast explicit: smaller models stress your validation harder.
5. Optionally, hand the structured rejection back to the model as a tool-result-style error and show it can sometimes correct itself on the next turn — but keep this light; error-handling *design* is [L05](../L05/objectives.md), not L04.

**What to highlight:**

- The model can hallucinate a tool call: wrong argument types, missing required arguments, extra invented arguments, even a tool name that doesn't exist. The schema did *not* stop any of this at generation time — **the application validates; the model proposes.** Say it in exactly those terms.
- Showing one hallucination is worth ten clean runs — it is the L04 analogue of L03's tag-violation moment, where a single contract failure taught that the contract is best-effort.
- Tool calls are **not deterministic**: the same prompt and schema can produce a call on one run and a skip on the next, with slightly different arguments each time. This is why validation is not optional.
- Resist going deep on *how* to design the error response or *how* to recover — name that as [L05](../L05/objectives.md)'s job (errors as part of the tool's interface) and move on.

**If the demo misbehaves:**

- If neither the primary nor the Haiku model produces a malformed call on the day, fall back to **hand-editing** the model's `tool_use` arguments before dispatch (e.g. replace the expression with `"twenty + 1"`) to force the validation path. The teaching point is the application's *response* to a bad call, which you can demonstrate regardless of whether the model cooperated in producing one.
- If the model invents a tool name that doesn't exist, that is the best possible version of this demo — slow down and show the dispatch step finding no matching tool.

## Optional bridge demo — toward designing good tools (L05)

If time allows, run one final demo that previews [L05](../L05/objectives.md): take the `calculator` tool and swap its rich description for a deliberately vague one (e.g. `"Does math."`), changing nothing else. Re-run Demo 4's P1 prompt and show the model now hesitates, skips the tool, or calls it with worse arguments. Don't teach *how* to write a good description here — just show that the description visibly moved the model's behavior, and name the question L05 will answer: *what makes a tool worth adding, well-named, and well-described?* This mirrors the bridge demo L03 used to set up L04, and the one [L05](../L05/demos_or_activities.md) uses to set up L06.

<!-- *NEED INPUT*: include this bridge demo, or save it as the opener for L05? Mirrors the same open question on the L03→L04 and L05→L06 bridges. -->

## Pacing notes for the teacher

- **Per-demo time:** 8–12 minutes including post-demo discussion. Four demos plus the optional bridge fits in a 50–70 minute block. <!-- *NEED INPUT*: confirm against the lesson-time budget once duration is pinned in objectives.md's open questions (best guess there is 60–90 minutes, possibly split into two lectures). -->
- **Variance budget:** model behavior varies run-to-run — especially Demo 4, where the whole point is that the same prompt can produce different outcomes. Budget at least one re-run per demo. Demo 3 replays a captured transcript and should not vary.
- **The audience watches, doesn't participate.** Resist asking "what arguments do you think it'll pass?" — that is a lab pattern, not a demo pattern. Hands-on wiring is for the L04 labs.
- **Keep the same `calculator` tool across all four demos.** One tool, seen four times under different conditions, is what makes the protocol legible. Don't introduce a second tool for variety — that dilutes the single-round-trip focus and strays into L05/L07 territory.

## Open authoring questions

- <!-- *NEED INPUT*: which API/SDK anchors the demos and labs (Anthropic Python SDK, OpenAI-style, or generic-pseudocode-with-pinned-SDK)? Mirrors objectives.md's open question — this drives the exact block names the harness prints (tool_use vs. function_call) and must be pinned once, course-wide. -->
- <!-- *NEED INPUT*: which model class anchors the labs and demos — Sonnet 4.6 is the assumed primary with Haiku 4.5 as the Demo 4 contrast, mirroring objectives.md. Smaller models fumble tool selection and arguments more, which sharpens Demos 1 and 4; confirm once the course-wide model choice is settled. -->
- <!-- *NEED INPUT*: should the demo tool be a pure-Python calculator (current choice — keeps the focus on the protocol) or a real external service (weather, time-of-day) that teaches failure modes earlier at the cost of flakiness? Mirrors objectives.md's open question. -->
- <!-- *NEED INPUT*: include tool_choice / forced-tool-call mechanics in a Demo 4 sub-step, or defer entirely to L05? objectives.md leans "brief mention here, deeper in L05" — if mentioned, the natural spot is right after P2 (the model skipping the tool), showing that forcing a call still does not guarantee well-formed arguments. -->
- <!-- *NEED INPUT*: are the demos run in a Jupyter notebook the teacher projects, or a slide-embedded REPL, or a custom demo runner? Affects how the harness and the single tool are pre-loaded. Mirrors the same question in the L03 and L05 demo docs. -->
- <!-- *NEED INPUT*: a pointer/link to where the demo tool and harness live as code (a demos/ subdir? inline in a notebook?) — not yet decided in non-draft docs. -->
