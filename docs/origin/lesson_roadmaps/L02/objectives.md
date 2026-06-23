# L02: Prompting fundamentals

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (lesson-plan row L02).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).

## Where this lesson sits

L01 ([objectives](../L01/objectives.md), [demos](../L01/demos_or_activities.md)) installed the four primitives — tokens, context windows, sampling, cost — that describe *what an API call costs and how the model's output is produced*. L02 is the first lesson about *what to put in the call*. It moves up one level of abstraction: from "a prompt is N tokens you pay for" to "a prompt has structure, and the structure changes the answer."

L02's three subgoals — roles, structured output, few-shot examples — are the minimum prompting toolkit a student needs before L03 can teach reasoning techniques on top of them. L03 ([objectives](../L03/objectives.md), [demos](../L03/demos_or_activities.md)) explicitly assumes the student arrives able to send multi-turn role-segmented chats, request structured output, and read its own few-shot examples. Everything from L04 onward (tool calling, agents) presumes the same toolkit.

This lesson is foundational and *narrow on purpose*. It does not teach chain-of-thought, scratchpad reasoning, or self-critique — those are L03. It does not teach tool calling or function-calling protocols — that is L04. The temptation to broaden scope here should be resisted; L02's job is to hand L03 a competent multi-turn chat user, nothing more, nothing less.

## Prerequisites

Students arriving at L02 should already be able to:

- Tokenize a string and predict roughly how many tokens a given prompt will consume (L01).
- Reason about the context window as a shared budget across system message, prior turns, current input, and output (L01).
- Pick a temperature appropriate to a task and explain the trade-off (L01).
- Estimate the per-call and per-conversation cost of an API call, including the staircase effect of re-sending conversation history (L01).
- Make a basic Anthropic SDK call from Python (L01 lab outcome).

If a student is shaky on any of these, redirect to the corresponding L01 lab before continuing — every L02 objective compounds on L01's primitives.

## Learning objectives

By the end of L02, a student should be able to:

1. **Use system, user, and assistant roles deliberately.** Concretely:
   - Explain what each role *is* in the API protocol: the system message as out-of-band steering, user messages as inputs from the caller, assistant messages as the model's prior responses (or as in-context examples — see Subgoal 3).
   - Construct a multi-turn conversation by appending alternating user/assistant messages and resending the full history (recall from L01: there is no server-side memory).
   - Decide what content belongs in the system message vs. the user message: durable, identity-and-policy content goes in `system`; per-call task content goes in `user`. Articulate why this matters for both reusability and (foreshadowing prompt caching) cost.
   - Recognize the consequences of mis-attributing content: instructions buried in user messages get re-sent every turn (cost and confusion); per-call data crammed into the system message poisons reuse.
   - Identify when to start a *new* conversation vs. continue an existing one — and reason about the cost-vs-context trade-off (recall L01: every continued turn re-bills history).

2. **Request structured output and parse it reliably.** Concretely:
   - Ask the model for output in a specified shape — JSON, a fixed list of fields, XML-ish tags — using prompt instructions alone.
   - **Anchor the lesson on prompt-instruction-only structured output** — i.e. asking for JSON via the prompt and parsing defensively in client code. *The Anthropic SDK's stricter mechanism (tool-use-as-schema, where you hijack the tool-call protocol to force schema-conformant arguments) is deliberately deferred to L04*, so that L04 can introduce the tool-use protocol once and then immediately apply it to the structured-output problem the student already understands. End the structured-output beat with a one-line foreshadow: *"In production, tool-use-as-schema is the stricter pattern — you'll see it in L04."* No need to teach the protocol here.
   - Write a parser that accepts the model's structured output and *also* gracefully handles the common failure modes: extra prose around the JSON, mismatched field names, missing required fields, and the occasional fully-malformed response. The lesson should land that "the model agreed to a contract" is not the same as "the model honored the contract."
   - Pick a temperature and a verbosity setting appropriate to structured output (recall L01: low temperature is the right default for extraction and classification).
   - Explain why structured output matters before agents exist: it makes the model's response *programmatic* rather than *conversational*, which is the precondition for everything from evals (L09) to tool calling (L04) to multi-step pipelines.

3. **Use few-shot examples deliberately — including knowing when not to.** Concretely:
   - Construct an in-context few-shot prompt: a small number of input/output example pairs followed by the real input. Place the examples either as alternating fake user/assistant turns or as a structured block in the user message — and articulate the trade-off between the two placements.
   - Choose example diversity over example volume: a few well-chosen contrasting examples will outperform many similar ones. Recognize the "all examples look like the easy case" failure mode where the model overfits to a surface pattern and misses harder inputs.
   - Reason about the cost of few-shot examples explicitly (L01 callback): each example consumes input tokens on every call. Few-shot is a real cost-vs-quality dial, not a free improvement.
   - Recognize when few-shot is the wrong tool: if a single clear instruction works, use it; if the task needs *reasoning* steps rather than *pattern-matching* steps, defer to L03's chain-of-thought techniques; if the schema is large or the example set would dominate the context window, structured output (Subgoal 2) or fine-tuning (out of scope for this course) may be better.
   - Distinguish "few-shot for format" (showing the model the desired output shape) from "few-shot for behavior" (showing the model the desired reasoning or judgment). Both work; they fail in different ways.

## Main points the lecture should land

- **Roles are an API-level contract about *who said what*, not a magical trust hierarchy.** The model treats the system message as conversational context with a privileged label — it tends to follow it, but it is not invulnerable to instructions in user messages. Frame the system message as "the always-true context that doesn't change between turns" rather than "the inviolable rules." This framing also explains why pushing per-call content into the system message is wrong: it stops being always-true.
- **Conversation history is a list, and you own it.** The "conversation" is a Python list of `{role, content}` dicts that the caller assembles and re-sends. There is no hidden server state. This explains both the cost staircase (recall L01) and the freedom: students can edit, summarize, or drop prior turns at any time. Foreshadow that L17 (context management) is largely about *how* to edit that list intelligently.
- **Structured output is a *negotiation*, not a guarantee.** Even with JSON mode or schema enforcement, the model can produce subtly-wrong structures (missing fields, wrong types, hallucinated values). The right mental model is: ask for structure, parse defensively, fail loudly when the parse fails. This pattern returns in L04 (tool calling, where the model's tool-call arguments must be parseable) and L08 (tracing, where structured intermediate outputs make traces readable).
- **Few-shot examples are a context-window-priced behavior nudge.** They are powerful — sometimes a 3-example block fixes a problem that no amount of instruction-writing can — but they are *expensive* in tokens (every call) and *brittle* (the model overfits to surface features of the examples). Treat them as a precision tool, not a default.
- **Prompt design has a *first-call vs. Nth-call* axis.** A prompt that works on call 1 of a conversation may degrade by call 5 as the model accumulates its own (potentially flawed) prior turns in the history. This is one of the first places students will feel "the model got worse" without anything obvious changing. Naming the phenomenon here makes it diagnosable later in agent loops (L07) and in long-running conversations (L17).
- **The shape of a prompt and the shape of an output are linked.** Asking the model to "give me a JSON list of names" while phrasing the request in flowing English produces a different result than asking it in a structured, labeled way. Consistency between input shape and output shape reduces the model's degrees of freedom — and therefore reduces the parse failures from Subgoal 2.

## Common student confusions to watch for

- *"The system message is enforced; the user can't override it."* No. The system message is *strongly weighted* but not inviolable. Anything close to a security or policy guarantee belongs outside the model, not inside the system prompt.
- *"Once I say 'output JSON', the model will always output valid JSON."* No. Even with JSON mode, the model can produce malformed output, especially under unusual inputs or low capacity. Always parse defensively.
- *"More examples is always better."* No — examples cost tokens every call (recall L01), and the model often overfits to surface features of a uniform example set.
- *"Few-shot teaches the model new things."* No — it conditions in-context behavior. The model's underlying capabilities don't change. Frame few-shot as "showing", not "teaching."
- *"The assistant role is only for what the model said."* No — the assistant role is the right place to put fake "model said this" content for in-context examples (Subgoal 3). This often surprises students.
- *"Structured output and chain-of-thought are competing techniques."* No — they compose. Many real prompts ask for `<thinking>...</thinking>` (L03) followed by a structured `<answer>{...}</answer>` (L02). L02 teaches the structured-answer half; L03 teaches the thinking half; later lessons combine them.

## Bridge to L03

L03 (teaching an LLM to think via prompting) builds directly on the L02 toolkit:

- The chain-of-thought prompts in L03 are sent through the same role structure L02 just taught — typically a system message that licenses reasoning, plus a user message containing the problem.
- L03's `<thinking>` and `<answer>` scratchpad pattern is *a specific use of structured output* (L02 Subgoal 2), with the parser pulling the answer out and (optionally) logging the thinking for debugging. L03 extends, rather than re-teaches, the parsing discipline introduced here.
- L03's worked-example few-shot for chain-of-thought is *a specific use of few-shot examples* (L02 Subgoal 3), where each example pair includes the reasoning trace as well as the final answer. Students who saw few-shot as a generic technique in L02 will see L03's worked-example CoT as one application, not as a new concept.
- L03 will explicitly call back to "every CoT token costs money" (L01 callback via L02's cost-of-few-shot framing). The cost mindset L01 installed and L02 reinforced is what makes L03's "when does CoT hurt?" subgoal land.

The single sentence to leave students with at the end of L02 is something like: *"You now know how to ask the model for what you want in the shape you want — L03 is about making it think harder before it answers."*

## Open authoring questions

- <!-- *NEED INPUT*: estimated lecture duration — best guess 75–90 minutes as one lecture covering all three objectives. Structured output (Subgoal 2) is the deepest of the three and may want extra time, especially the parse-defensively beat. -->
- <!-- *NEED INPUT*: should L02 introduce prompt caching as a concrete technique (it most naturally lands when discussing the "system message is durable, user message is per-call" split in Subgoal 1), or strictly defer to L17 (context management)? Mirrored from [L01 objectives](../L01/objectives.md) where it was raised as an L01-vs-L14 question. -->
- <!-- *NEED INPUT*: should L02 demo the "model overrides the system message under user pressure" failure mode, or treat that as a security/safety topic out of scope for this course? Affects how strongly the lecture frames the system message as "weighted but not inviolable." -->
- <!-- *NEED INPUT*: are there specific Anthropic-SDK conveniences (message helpers, streaming, content blocks) that should be introduced here vs. left for later lessons? Risk of bloating L02 if too many SDK features land at once. -->
- <!-- *NEED INPUT*: how much L03 foreshadowing is appropriate? The bridge-to-L03 section assumes students will see structured-output and few-shot composed with CoT in L03 — confirm L03 covers that composition rather than treating its scratchpad/few-shot as standalone. -->
