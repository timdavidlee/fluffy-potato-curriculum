# Teaching an LLM to think: chain-of-thought, scratchpads, and self-critique

```yaml
title: Teaching an LLM to think: chain-of-thought, scratchpads, and self-critique
keywords: chain-of-thought, cot, numbered scaffold, worked example, scratchpad, thinking tags, defensive parsing, self-critique, sycophancy, reasoning cost, when not to reason
estimated duration: 80
```

> **Lesson:** L06. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L06/objectives.md).
> This is the written reference lecture — thorough on purpose, so a student who missed the verbal
> delivery can rebuild the lesson from the page. The live demos are split one per technique
> ([L0603](L0603_lecture.ipynb) CoT, [L0605](L0605_lecture.ipynb) scratchpad,
> [L0607](L0607_lecture.ipynb) self-critique, [L0609](L0609_lecture.ipynb) when-it-hurts); hands-on
> practice is in the L06 labs (L0604 / L0606 / L0608 / L0610).
> **Anchor model throughout: Claude Sonnet 4.6.**

## section 1. The lesson in one claim

### slide 1.1 From the shape of the prompt to the content of the answer

- L02 taught the *shape* of a prompt — roles, structured output, few-shot. L06 teaches a technique
  that lives in the *content*: getting the model to surface intermediate reasoning before it commits.
- The whole lesson rests on one claim: **reasoning is a tokens-on-the-page phenomenon, not a
  separate model mode.** The model is not "thinking harder"; it is generating intermediate tokens
  that condition its later tokens.
- This claim is load-bearing. It explains why chain-of-thought *helps* and why it sometimes *hurts*,
  and it makes every later technique in the lesson predictable instead of magical.

### slide 1.2 Why more tokens change the answer

- An LLM predicts the next token from everything on the page so far. Predicting *"the answer is 0.32"*
  right after *"step 1 … step 2 … step 3 …"* draws from a **different distribution** than predicting
  it cold, with no working shown.
- So the reasoning text is not a window into a hidden thought process — it *is* the process. The
  tokens are the computation.
- diagram: two prompts side by side — "Q → A" (cold) vs "Q → step1 → step2 → step3 → A" (CoT) — with
  an arrow noting that the second conditions A on the intermediate tokens.

### slide 1.3 The four techniques L06 hands you

- table: the four techniques, the one sentence each lands, and the cost shadow each carries.

| Technique | The mental model | Cost shadow (L01) |
| --- | --- | --- |
| Chain-of-thought | reasoning is just more tokens; show the work | output tokens balloon 3–10× |
| Scratchpad / `<thinking>` | a contract about *shape*, not capability | a few framing tokens; parse defensively |
| Self-critique | a sampling technique, not a correctness oracle | a whole extra round-trip (sometimes a 2nd model) |
| Knowing when *not* to | reasoning is a trade-off, not a default | wasted tokens + latency when it doesn't help |

[↑ Back to top](#teaching-an-llm-to-think-chain-of-thought-scratchpads-and-self-critique)

## section 2. Chain-of-thought: show the work

### slide 2.1 What CoT is

- **Chain-of-thought (CoT)** is any prompt that asks the model to produce step-by-step reasoning
  *before* its final answer, instead of jumping straight to the answer.
- It helps most on a recognizable problem class: **multi-step arithmetic, logical deduction,
  ambiguous classification, and multi-constraint generation** — anything where a single forward pass
  to the answer is error-prone.
- It is the most reliable single lever in this lesson, and the cheapest to try first.

### slide 2.2 Three CoT triggers, cheapest to most controlled

- **"Let's think step by step."** One appended instruction. Cheapest to write, least controllable —
  the model picks its own structure.
- **Numbered scaffold.** You name the steps: *"(1) count the total ways, (2) count the favorable
  outcomes, (3) divide."* More tokens to write, far more consistent structure, more brittle if the
  input drifts off the template.
- **Worked-example few-shot.** Reuse L02's few-shot lever: show one or two fully-worked
  problem→reasoning→answer examples, then the real problem. The model imitates the *reasoning style*,
  not just the answer format.
- diagram: a dial from "free-form (cheap, loose)" → "numbered (structured)" → "worked-example
  (most guided, most tokens)".

### slide 2.3 The shape of the reasoning matters

- A free-form *"think step by step"* is cheapest but least predictable; numbered scaffolds and
  worked examples buy you **consistent structure** at the cost of tokens and brittleness.
- Match the trigger to the need: exploratory one-off → free-form; a production prompt that must
  return the same shape every time → scaffold or worked example.
- Newer models often reason *without* an explicit trigger — the trigger is one tool, not the only
  one. Don't assume CoT is absent just because you didn't say the magic words.

### slide 2.4 Always compare with and against

- The discipline: run the **same input** with and without the CoT scaffold, and read off what
  changed — accuracy, structure, latency, token count. The contrast is the evidence.
- This with/against comparison is exactly what the L0604 lab has you build, and what
  [Demo 1](L0603_lecture.ipynb) shows live.

[↑ Back to top](#teaching-an-llm-to-think-chain-of-thought-scratchpads-and-self-critique)

## section 3. Scratchpads: separate the thinking from the answer

### slide 3.1 The problem CoT creates

- CoT is great for *accuracy* and terrible for *parsing*: the answer is now buried at the end of a
  paragraph of reasoning. Your downstream code, your eval harness, and your UI all want just the
  answer.
- The fix is a **scratchpad**: ask the model to reason inside `<thinking>…</thinking>` and put only
  the final answer inside `<answer>…</answer>`.

### slide 3.2 Tags are a contract, not a capability

- The model could already reason inline — wrapping it in tags adds **zero capability**. The tags are
  purely a boundary for downstream code to ignore (the thinking) or surface (the answer).
- This is the **same move as JSON-mode output in L02**: a contract about *shape*, not *substance*.
  Treat it identically — ask for the shape, then enforce it in code.
- diagram: a model response split into a greyed-out `<thinking>` block (logged, ignored by callers)
  and a highlighted `<answer>` block (consumed by the program).

### slide 3.3 Parse defensively — the model can break the contract

- The model **agreed** to the tags; it did not **guarantee** them. It may forget a closing tag, put
  the answer outside `<answer>`, or emit two answers.
- So you parse defensively, exactly like L02's JSON parser: try the happy path (`re.search` for the
  `<answer>` block), have a fallback, and **fail loudly** when you truly can't extract an answer —
  never silently return an empty string.
- A single tag-violation in front of the class teaches more than ten clean runs: it proves the
  contract is best-effort, which is why the parser exists.

### slide 3.4 Why the separation matters downstream

- **Parseability** — your code reads a field, not a paragraph.
- **UX** — you can show the user the answer and hide (or collapse) the reasoning.
- **Evals & tracing** — a clean answer field is what L11 (tracing) and L12 (evaluation) score against;
  reasoning logged separately is debugging gold without polluting the metric.

[↑ Back to top](#teaching-an-llm-to-think-chain-of-thought-scratchpads-and-self-critique)

## section 4. Self-critique: a second pass over the answer

### slide 4.1 What self-critique is

- **Self-critique** takes the model's first answer as input and asks for a *critique plus a revised
  answer*. It is a second sampling pass, not a verification oracle.
- Two shapes:
  - **Single-prompt** — one round-trip; the model answers, critiques, and revises inline.
  - **Two-step** — two round-trips; the first answer is fed into a second call (possibly a different
    prompt or a different model). More expensive, more controllable.

### slide 4.2 The sycophancy failure mode

- The dominant failure: the critic **agrees with the original answer regardless of correctness** —
  "yes, that looks right" — especially when it is the *same model, same prompt, seeing its own
  answer*.
- A critic with **no new information** is a weak critic. It has nothing to disagree *with*.
- Name it out loud — sycophancy is the thing to watch for every time you reach for self-critique.

### slide 4.3 Mitigations — inject new information

- table: four ways to give the critic something the first pass lacked.

| Mitigation | What new information it injects |
| --- | --- |
| Different **framing** | *"You are a skeptical reviewer; find the flaw."* shifts the prior toward disagreement |
| Different **model** | a second model has different failure modes (revisited rigorously in L12) |
| **Adversarial role** | force the critic to argue the answer is wrong before deciding |
| **Ground-truth check** | compare against a known answer, a tool result, or retrieved evidence |

- The common thread: a critique is only as good as the *new information* it brings. Re-asking the
  same model the same way is theatre.

### slide 4.4 Single-prompt vs two-step — the trade-off

- **Single-prompt:** cheaper (one call), lower latency, but the critique is conditioned on the same
  context that produced the error — weaker.
- **Two-step:** a full extra round-trip (cost + latency), but lets you change the model, the framing,
  or inject evidence between passes — stronger.
- Choose deliberately, the same way you choose a CoT trigger: by what the task can afford.

[↑ Back to top](#teaching-an-llm-to-think-chain-of-thought-scratchpads-and-self-critique)

## section 5. When reasoning hurts

### slide 5.1 Reasoning is not free

- Every CoT, scratchpad, or critique token is **paid for** (L01's per-token cost), **adds latency**,
  and **competes for the context window**. None of that is hypothetical — the demos print the numbers.
- L06 is the first lesson where you must consciously weigh reasoning *quality* against *cost*. That
  trade-off returns in L12 (model power) and L16 (context management).

### slide 5.2 Three cases where it backfires

- **Zero-shot-easy tasks.** A clear-cut sentiment classification needs a two-token answer; a 200-token
  CoT preamble adds latency and cost with **no accuracy gain**.
- **"Talks itself into the wrong answer."** On some problems, free-form reasoning constructs a
  plausible-but-wrong justification and the model follows it off a cliff — CoT *lowers* accuracy.
- **Tight-latency, user-facing flows.** A chat UI or real-time agent often can't afford CoT on every
  call even when it would help accuracy — the latency budget says no.

### slide 5.3 Make the trade-off on purpose

- Given a task, an accuracy requirement, and a latency/cost budget, **decide and defend**: reason, or
  answer cold? That decision *is* the L06 skill — the L0610 lab has you make it on a table of tasks.
- Heuristic: reach for reasoning when the task is in the help-class from section 2 *and* the budget
  allows; skip it when the task is easy, latency-bound, or prone to talked-into-it errors.

[↑ Back to top](#teaching-an-llm-to-think-chain-of-thought-scratchpads-and-self-critique)

## section 6. Bridge to L07

### slide 6.1 Reasoning becomes a step inside a loop

- L07 introduces **tool calling**, which adds an outer loop: the model decides whether to answer
  directly or call a tool. *That decision is itself a reasoning step.*
- Everything from L06 applies inside that loop — eliciting reasoning about *which* tool to call,
  separating that reasoning from the tool-call output, and recognizing when reasoning about the tool
  is wasted.

### slide 6.2 What to carry forward

- **Reasoning is tokens** → a tool call is also just tokens the model emits in a structured shape
  (L07's central framing — the parallel is deliberate).
- **Parse defensively** → tool-call arguments can be malformed exactly like a broken `<answer>` tag;
  the same discipline applies.
- One sentence to L07: *you can make the model think before it answers; next you'll let that thinking
  decide to reach for a tool.*

[↑ Back to top](#teaching-an-llm-to-think-chain-of-thought-scratchpads-and-self-critique)
