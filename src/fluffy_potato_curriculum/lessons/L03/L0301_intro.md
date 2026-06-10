# Teaching an LLM to think: reasoning is tokens on the page

```yaml
title: Teaching an LLM to think: reasoning is tokens on the page
keywords: chain-of-thought, cot, scratchpad, thinking tags, self-critique, sycophancy, reasoning cost, anthropic, claude
estimated duration: 10
```

> **Lesson:** L03 — Teaching an LLM to think via prompting.
> **Roadmap:** see this lesson's [objectives.md](../../../../docs/origin/lesson_roadmaps/L03/objectives.md).
> This is a short framing piece. Read it before the written reference lecture
> ([L0302_lecture.md](L0302_lecture.md)) and the four teacher demo notebooks
> (CoT [L0303_lecture.ipynb](L0303_lecture.ipynb), scratchpad [L0305_lecture.ipynb](L0305_lecture.ipynb),
> self-critique [L0307_lecture.ipynb](L0307_lecture.ipynb), when-reasoning-hurts
> [L0309_lecture.ipynb](L0309_lecture.ipynb)).
> **Anchor model throughout: Claude Sonnet 4.6.**

## Where this lesson sits

L02 was about the *shape* of a prompt — roles, structured output, few-shot. It taught you to ask
the model for what you want, in the form you want. L03 is about a different lever: the *content* of
the prompt, specifically prompting techniques that make the model produce **visibly better answers
on harder problems** by surfacing intermediate reasoning before it commits to a final answer.

The whole lesson rests on one claim, which the demos make concrete:

> *Reasoning is a tokens-on-the-page phenomenon, not a separate model mode. The model isn't
> "thinking harder" — it is generating intermediate tokens that condition the tokens that come
> after.*

That single framing explains both why these techniques **help** (more intermediate steps draw the
final answer from a better distribution) *and* why they sometimes **hurt** (more tokens means more
chances to drift, more latency, more cost).

## The four techniques, in one breath

L03 hands you four tools for shaping reasoning. They are the bridge between "prompting" (L02) and
"the model decides whether to call a tool" (L04 — that decision is itself a reasoning step).

- **Chain-of-thought (CoT)** — ask for step-by-step reasoning before the answer. The trigger can be
  a plain *"let's think step by step,"* an explicit numbered scaffold, or a worked-example few-shot
  (reusing L02's few-shot lever). Helps most on multi-step arithmetic, logical deduction, ambiguous
  classification, and multi-constraint generation.
- **Scratchpad / `<thinking>` block** — wrap the reasoning in tags so the final answer is cleanly
  separable. The tags add **zero capability** — they are an interface contract for downstream code,
  exactly like the structured-output contract from L02.
- **Self-critique** — a second pass where the model reviews its own first answer and revises it. A
  *sampling technique, not a correctness oracle*: it works only when the critic has information the
  first pass lacked (a different framing, a different model, retrieved context, ground truth).
- **Knowing when *not* to reason** — CoT on a two-token classification is pure overhead; on some
  tasks the model "talks itself into" a wrong answer. The skill L03 builds is making this trade-off
  *consciously*.

## Three mental models to carry out of L03

Each demo lands one sentence. If you remember nothing else, remember these:

1. **Reasoning is just more tokens.** CoT works because predicting *"the answer is X"* after
   *"step 1, step 2, step 3"* draws from a different distribution than predicting it cold. Nothing
   mystical changed — the page got longer.
2. **Scratchpad tags are a contract about *shape*, not *substance*.** The model could already reason
   inline; `<thinking>` just gives your parser a clean boundary to ignore or surface. Same move as
   JSON-mode output in L02.
3. **Self-critique without new information is sycophancy.** A critic that is the same model, same
   prompt, looking at its own answer will tend to agree with it — right or wrong. Inject new
   information or expect a rubber stamp.

## How L01 and L02 carry forward

Every L03 technique has an L01 cost shadow, and we keep printing the numbers:

- **Reasoning is not free.** Every CoT or scratchpad token is paid for (L01's per-token cost), adds
  latency, and competes for the context window. L03 is the first lesson where you must consciously
  weigh reasoning *quality* against *cost*.
- **The scratchpad contract is L02's structured-output discipline reused.** You ask for
  `<thinking>…</thinking><answer>…</answer>`, and you **parse defensively** — the model agreed to the
  shape, it did not guarantee it.
- **Self-critique can reuse L02's roles.** A two-step critique is just another `user`/`assistant`
  turn in the messages list you already know how to build.

## What L03 deliberately does *not* teach

This lesson is scoped to **prompt-only** reasoning:

- **Not extended-thinking / thinking-mode APIs.** Some providers expose a dedicated reasoning mode.
  L03 stays prompt-only on purpose — the point is to see that reasoning *is* tokens, which a
  built-in mode would hide. <!-- *NEED INPUT*: confirm extended-thinking stays out of scope, per the open question in objectives.md. -->
- **Not tool calling.** Deciding *whether* to call a tool is a reasoning step, but the tool-calling
  protocol itself is **L04**. L03 hands L04 a model that already reasons before it answers.

The one sentence to leave L03 with:

> *You can now make the model think before it answers — and, just as importantly, decide when it
> shouldn't bother.*

Next: the written reference lecture in [L0302_lecture.md](L0302_lecture.md), then the live demos
(L0303 / L0305 / L0307 / L0309) and the hands-on labs (L0304 / L0306 / L0308 / L0310).
