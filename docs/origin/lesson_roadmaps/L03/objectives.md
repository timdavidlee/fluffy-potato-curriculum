# L03: Teaching an LLM to think via prompting

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (lesson-plan row L03).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).

## Where this lesson sits

L02 covered the mechanics of prompting — how to talk to a model with system/user/assistant roles, request structured output, and use few-shot examples. L03 takes the next step: the *content* of those prompts. Specifically, we explore prompting techniques that let a model produce visibly better answers on harder problems by surfacing intermediate reasoning before committing to a final answer.

This is the last lesson before L04, where the model is given the ability to call tools. The mental models built here — "give the model space to think" — directly inform the tool-calling loop, since deciding *whether* to call a tool is itself a reasoning step.

## Prerequisites

Students arriving at L03 should already be able to:

- Send a multi-turn chat completion with system/user/assistant roles (L02).
- Request structured output (e.g. JSON) from a model and parse it (L02).
- Estimate the token cost of a prompt and reason about context-window pressure (L01).

If a student is shaky on any of these, redirect to the corresponding L01/L02 lab before continuing.

## Learning objectives

By the end of L03, a student should be able to:

1. **Write a chain-of-thought (CoT) prompt** that elicits step-by-step reasoning on a problem the model would otherwise solve incorrectly. Concretely:
   - Recognize a problem class where CoT helps (multi-step arithmetic, logical deduction, ambiguous classification, multi-constraint generation).
   - Use one of the standard CoT triggers — a "let's think step by step" instruction, an explicit numbered-step scaffold, or a worked-example few-shot — and articulate why they chose that variant.
   - Compare the model's answer with and without the CoT scaffold on the same input and explain what changed (accuracy, structure, latency, token count).

2. **Use a scratchpad or `<thinking>` block** to separate intermediate reasoning from the final answer. Concretely:
   - Structure a prompt that asks the model to reason inside `<thinking>...</thinking>` tags and emit only the final answer outside them.
   - Parse the model's output to extract the final answer cleanly while optionally inspecting or logging the scratchpad for debugging.
   - Explain why separating scratchpad from answer matters for downstream consumers (parseability, user-facing UX, eval pipelines).

3. **Apply self-critique** as a second pass over the model's own answer. Concretely:
   - Write a self-critique prompt that takes the model's first answer as input and asks for a critique plus a revised answer.
   - Decide between a single-prompt self-critique (one round-trip, critique inline) and a two-step critique (two round-trips, possibly with a different model or prompt) — and name the trade-offs.
   - Recognize the common failure mode where the critic agrees with the original answer regardless of correctness, and apply at least one mitigation (different model, different framing, adversarial role, ground-truth check).

4. **Recognize when explicit reasoning helps vs. hurts.** Concretely:
   - Name at least two situations where CoT or scratchpad reasoning is counterproductive — e.g. zero-shot-easy classification tasks (added latency and tokens with no accuracy gain), tasks where the model "talks itself into" the wrong answer, or user-facing flows with tight latency budgets.
   - Make a deliberate trade-off given a task description, accuracy requirement, and latency/cost budget — and defend the choice.

## Main points the lecture should land

- **Reasoning is a tokens-on-the-page phenomenon, not a separate model mode.** The model isn't "thinking harder"; it is generating intermediate tokens that condition its later tokens. CoT works because predicting "the answer is X" after "step 1, step 2, step 3" draws from a different distribution than predicting it cold. This framing matters because it explains both why CoT helps *and* why it sometimes hurts: more tokens means more chances to drift.
- **The shape of the reasoning matters.** A free-form "think step by step" instruction is the cheapest CoT to write but the least controllable. Numbered scaffolds, named sub-tasks, and worked-example few-shots give the model a template — useful when you need consistent structure, more brittle to off-distribution inputs.
- **Scratchpads are an interface contract, not a capability.** The model can already reason inline; wrapping reasoning in `<thinking>` tags is purely about giving downstream code (parsers, evals, UIs) a clean boundary to ignore or surface. Treat it the same way as JSON-mode output: a contract about *shape*, not *substance*.
- **Self-critique is a sampling technique, not a correctness oracle.** It works best when the critic has information the original generator didn't — a different model, a different prompt, retrieved context, ground-truth examples. Without that, the critic is prone to sycophantic agreement: "yes, that answer looks right" regardless of whether it is.
- **Reasoning is not free.** Every CoT or scratchpad token is paid for, latency-incurring, and competing with other content for the context window. L03 is the first lesson where the student must consciously weigh reasoning quality against cost — a theme that returns in L08 (model power) and L12 (context management).

## Common student confusions to watch for

- *"CoT only works if you tell the model to think step by step."* Newer models often reason without an explicit trigger; the trigger is one tool, not the only one.
- *"Scratchpad tags do something special."* They don't — they are delimiters. The model treats them like any other tokens unless the surrounding prompt teaches it what they mean.
- *"Self-critique always improves the answer."* It doesn't, especially when the critic is the same model, same prompt, seeing its own answer.
- *"More reasoning is always better."* A 2-token classification answer does not need a 200-token preamble.

## Bridge to L04

L04 introduces tool calling, which adds an outer loop: the model decides whether to answer directly or call a tool. That decision is itself a reasoning step. Everything from L03 — eliciting reasoning, separating reasoning from output, recognizing when reasoning is wasted — applies inside the tool-calling loop, especially when reasoning about *which* tool to call and whether the tool's response is sufficient to answer.

## Open authoring questions

- <need input: estimated lecture duration — best guess 60–90 minutes as one lecture, or split into two (CoT + scratchpad, then self-critique + when-to-use)?>
- <need input: which model(s) the L03 labs should target — pinning to a specific Claude class affects which CoT examples land cleanly. Sonnet 4.6 vs. Haiku 4.5 will show different-shaped wins from CoT.>
- <need input: should self-critique introduce the idea of using a *different* model as the critic, or defer that to L08 (model power)?>
- <need input: any specific L01/L02 labs that must be completed before this lesson is taught, beyond the prerequisite skills above?>
- <need input: is "extended thinking" / Anthropic's thinking-mode API in scope here, or is L03 deliberately scoped to prompt-only reasoning with deeper API features deferred?>
