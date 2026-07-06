# Teaching an LLM to think: chain-of-thought, scratchpads, and self-critique

```yaml
title: Teaching an LLM to think: chain-of-thought, scratchpads, and self-critique
keywords: chain-of-thought, cot, numbered scaffold, worked example, scratchpad, thinking tags, defensive parsing, self-critique, sycophancy, reasoning cost, when not to reason
estimated duration: 80
```

> **Lesson:** L06. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L06/objectives.md).
> This page is your written reference — thorough on purpose, so if you missed the live session you
> can rebuild the whole lesson from it. The live demos are split one per technique
> ([L0603](L0603_lecture.ipynb) CoT, [L0605](L0605_lecture.ipynb) scratchpad,
> [L0607](L0607_lecture.ipynb) self-critique, [L0609](L0609_lecture.ipynb) when-it-hurts); you get
> hands-on in the L06 labs (L0604 / L0606 / L0608 / L0610).
> **Anchor model throughout: Claude Sonnet 4.6.**

## section 1. The lesson in one claim

### slide 1.1 From the shape of the prompt to the content of the answer

- In L02 you learned the *shape* of a prompt — roles, structured output, few-shot. Here you pick up
  a technique that lives in the *content*: getting the model to surface intermediate reasoning
  before it commits.
- The whole lesson rests on one claim: **reasoning is a tokens-on-the-page phenomenon, not a
  separate model mode.** The model isn't "thinking harder"; it's generating intermediate tokens that
  condition its later tokens.
- Hold onto this claim — it explains why chain-of-thought *helps* and why it sometimes *hurts*, and
  it turns every later technique in this lesson from magic into something predictable.

### slide 1.2 Why more tokens change the answer

- An LLM predicts the next token from everything on the page so far. Predicting *"the answer is 0.32"*
  right after *"step 1 … step 2 … step 3 …"* draws from a **different distribution** than predicting
  it cold, with no working shown.
- So the reasoning text isn't a window into a hidden thought process — it *is* the process. The
  tokens are the computation.
- diagram: two prompts side by side — "Q → A" (cold, ink-faint) vs "Q → step1 → step2 → step3 → A"
  (CoT), the intermediate step-tokens in **cyan** (they're the point) — with an arrow noting that
  the second conditions A on those tokens. This two-prompt contrast is the lesson's reusable motif:
  slide 2.4 re-shows it with results attached.

### slide 1.3 The four techniques you'll pick up

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
- It helps you most on a recognizable problem class: **multi-step arithmetic, logical deduction,
  ambiguous classification, and multi-constraint generation** — anything where a single forward pass
  to the answer is error-prone.
- It's the most reliable single lever in this lesson, and the cheapest for you to try first.

### slide 2.2 Three CoT triggers, cheapest to most controlled

- **"Let's think step by step."** One appended instruction. Cheapest to write, least controllable —
  the model picks its own structure.
- **Numbered scaffold.** You name the steps: *"(1) count the total ways, (2) count the favorable
  outcomes, (3) divide."* More tokens to write, far more consistent structure, more brittle if the
  input drifts off the template.
- **Worked-example few-shot.** Reuse L02's few-shot lever: show the model one or two fully-worked
  problem→reasoning→answer examples, then the real problem. It imitates the *reasoning style*, not
  just the answer format.
- diagram: a three-step ladder of CoT triggers, each step taller (more tokens, more control) —
  "free-form (cheap, loose)" → "numbered scaffold (structured)" → "worked-example (most guided,
  most tokens)" — with the production step (numbered scaffold) in **cyan** and the other two steps
  ink-faint; nothing here is a failure, so no coral.

### slide 2.3 The shape of the reasoning matters

- A free-form *"think step by step"* is cheapest but least predictable; numbered scaffolds and
  worked examples buy you **consistent structure** at the cost of tokens and brittleness.
- Match the trigger to your need: exploratory one-off → free-form; a production prompt that must
  return the same shape every time → scaffold or worked example.
- Newer models often reason *without* an explicit trigger — the trigger is one tool, not the only
  one. Don't assume CoT is absent just because you didn't say the magic words.

### slide 2.4 Always compare with and against

- Build the discipline: run the **same input** with and without the CoT scaffold, and read off what
  changed — accuracy, structure, latency, token count. The contrast is your evidence.
- This with/against comparison is exactly what the L0604 lab has you build, and what
  [Demo 1](L0603_lecture.ipynb) shows you live.
- diagram: slide 1.2's two-prompt contrast re-shown (same motif, one change) — the same input run
  cold vs with the CoT scaffold, each panel now annotated with its result, output-token count, and
  latency; the intermediate step-tokens stay **cyan**, because they're what bought the accuracy
  delta the annotations show.

[↑ Back to top](#teaching-an-llm-to-think-chain-of-thought-scratchpads-and-self-critique)

## section 3. Scratchpads: separate the thinking from the answer

### slide 3.1 The problem CoT creates

- CoT is great for *accuracy* and terrible for *parsing*: the answer is now buried at the end of a
  paragraph of reasoning. Your downstream code, your eval harness, and your UI all want just the
  answer.
- The fix is a **scratchpad**: ask the model to reason inside `<thinking>…</thinking>` and put only
  the final answer inside `<answer>…</answer>`.
- diagram: the *before* to slide 3.2's split block — one tall ink-faint blob of free-form reasoning
  with the answer a tiny buried line at the bottom, and a **coral** "?" arrow from downstream code
  poking at the blob, unable to find it. Slides 3.2–3.4 re-show this same response block, fixed.

### slide 3.2 Tags are a contract, not a capability

- The model could already reason inline — wrapping it in tags adds **zero capability**. The tags are
  purely a boundary you can use to ignore (the thinking) or surface (the answer).
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
- One tag-violation teaches you more than ten clean runs: it proves the contract is best-effort,
  which is exactly why your parser exists.
- diagram: a defensive parse flow — a model response that broke the contract (a missing
  `</answer>`, the answer outside the tag, or two `<answer>` blocks) feeding a parser: try the
  `<answer>` regex (happy path, cyan) → a fallback → and a **coral** "fail loud" terminal, captioned
  "never silently return an empty string."

### slide 3.4 Why the separation matters downstream

- **Parseability** — your code reads a field, not a paragraph.
- **UX** — you can show the user the answer and hide (or collapse) the reasoning.
- **Evals & tracing** — a clean answer field is what L12 (tracing) and L13 (evaluation) score against;
  reasoning logged separately is debugging gold without polluting the metric.
- diagram: slide 3.2's split block re-shown (same motif, one change) — three **cyan** arrows now
  fan out of the `<answer>` block, labeled *parsing code*, *user-facing UI*, and *evals & tracing
  (L12/L13)*; the greyed `<thinking>` block sits above with no arrows leaving it.

[↑ Back to top](#teaching-an-llm-to-think-chain-of-thought-scratchpads-and-self-critique)

## section 4. Self-critique: a second pass over the answer

### slide 4.1 What self-critique is

- **Self-critique** takes the model's first answer as input and asks for a *critique plus a revised
  answer*. It's a second sampling pass, not a verification oracle.
- Two shapes:
  - **Single-prompt** — one round-trip; the model answers, critiques, and revises inline.
  - **Two-step** — two round-trips; you feed the first answer into a second call (possibly a
    different prompt or a different model). More expensive, more controllable.
- diagram: the two self-critique shapes side by side — **single-prompt** (one round-trip: a single
  call where the model answers → critiques → revises inline) vs **two-step** (two round-trips: call 1
  produces the answer, then call 2 — possibly a different prompt or model — critiques and revises
  it), the two-step tagged "a whole extra round-trip: costlier, more controllable." Both shapes stay
  cyan/neutral here — no failure yet. This answer→critic flow is the section's motif: slide 4.2
  re-shows it failing, slide 4.3 re-shows it fixed.

### slide 4.2 The sycophancy failure mode

- The dominant failure: the critic **agrees with the original answer regardless of correctness** —
  "yes, that looks right" — especially when it's the *same model, same prompt, seeing its own
  answer*.
- A critic with **no new information** is a weak critic. It has nothing to disagree *with*.
- Watch for this every time you reach for self-critique — that's sycophancy, and it's the failure
  mode to keep in mind.
- diagram: slide 4.1's answer→critic flow re-shown (same motif, one change) — the critic (same
  model, same prompt, reading its own answer) stamps a **coral** "yes, looks right" loop straight
  back onto the original answer; no new-information arrow enters the picture anywhere.

### slide 4.3 Mitigations — inject new information

- table: four ways to give the critic something the first pass lacked.

| Mitigation | What new information it injects |
| --- | --- |
| Different **framing** | *"You are a skeptical reviewer; find the flaw."* shifts the prior toward disagreement |
| Different **model** | a second model has different failure modes (revisited rigorously in L13) |
| **Adversarial role** | force the critic to argue the answer is wrong before deciding |
| **Ground-truth check** | compare against a known answer, a tool result, or retrieved evidence |

- The common thread: your critique is only as good as the *new information* it brings. Re-asking the
  same model the same way is theatre.
- diagram: the third beat of the slide-4.1 motif — the same answer→critic flow, now with a **cyan**
  new-information arrow feeding the critic (a skeptical framing, a second model, an adversarial
  role, or ground truth), the one added arrow that turns 4.2's coral rubber-stamp into a real
  critique.

### slide 4.4 Single-prompt vs two-step — the trade-off

- **Single-prompt:** cheaper (one call), lower latency, but the critique is conditioned on the same
  context that produced the error — weaker.
- **Two-step:** a full extra round-trip (cost + latency), but lets you change the model, the framing,
  or inject evidence between passes — stronger.
- Choose deliberately, the same way you chose a CoT trigger: by what the task can afford.

[↑ Back to top](#teaching-an-llm-to-think-chain-of-thought-scratchpads-and-self-critique)

## section 5. When reasoning hurts

### slide 5.1 Reasoning is not free

- Every CoT, scratchpad, or critique token is **paid for** (L01's per-token cost), **adds latency**,
  and **competes for the context window**. None of that is hypothetical — the demos print the numbers
  for you.
- This is the first lesson where you must consciously weigh reasoning *quality* against *cost*. That
  trade-off returns in L13 (model power) and L16 (context management).
- diagram: bar chart of output tokens for the same task — a zero-shot bar (ink-faint) beside a CoT
  bar **3–10× taller in coral** (the balloon is the cost you pay), with a matching latency pair of
  bars alongside making the second price visible.

### slide 5.2 Three cases where it backfires

- **Zero-shot-easy tasks.** A clear-cut sentiment classification needs a two-token answer; a 200-token
  CoT preamble adds latency and cost with **no accuracy gain**.
- **"Talks itself into the wrong answer."** On some problems, free-form reasoning constructs a
  plausible-but-wrong justification and the model follows it off a cliff — CoT *lowers* accuracy.
- **Tight-latency, user-facing flows.** A chat UI or real-time agent often can't afford CoT on every
  call even when it would help accuracy — your latency budget says no.
- diagram: three compact panels of reasoning backfiring — (1) an **easy** task (a 2-token answer
  weighed down by a 200-token CoT preamble: cost + latency, no accuracy gain); (2) a **trap** task
  (free-form reasoning building a plausible-but-wrong path the model then follows off a cliff —
  accuracy *drops*, mark it coral); (3) a **latency-bound** flow (a real-time chat/agent whose budget
  says no even when CoT would help).

### slide 5.3 Make the trade-off on purpose

- Given a task, an accuracy requirement, and a latency/cost budget, **decide and defend**: reason, or
  answer cold? That decision is the skill you're building here — the L0610 lab has you make it on a
  table of tasks.
- Heuristic: reach for reasoning when the task is in the help-class from section 2 *and* the budget
  allows; skip it when the task is easy, latency-bound, or prone to talked-into-it errors.
- diagram: a decision-tree flow — "in section 2's help-class?" → "latency/cost budget allows?" —
  with the reason branch in **cyan** and the answer-cold branch in **ink-faint** (answering cold is
  a legitimate outcome, not a failure — no coral here); this is the exact decision the L0610 lab
  has you make and defend.

[↑ Back to top](#teaching-an-llm-to-think-chain-of-thought-scratchpads-and-self-critique)

## section 6. Bridge to L07

### slide 6.1 Reasoning becomes a step inside a loop

- L07 introduces **tool calling**, which adds an outer loop: the model decides whether to answer
  directly or call a tool. *That decision is itself a reasoning step.*
- Everything you learned in L06 applies inside that loop — eliciting reasoning about *which* tool to
  call, separating that reasoning from the tool-call output, and recognizing when reasoning about the
  tool is wasted.
- diagram: your first look at the agent loop — a flow where the model node's reasoning step (a
  **cyan** chip, the piece you now own) decides between answering directly and calling a tool, with
  the tool node and its back-edge into the model drawn **dashed ink-faint** ("lands in L07" —
  deferred, not a failure).

### slide 6.2 What to carry forward

- **Reasoning is tokens** → a tool call is also just tokens the model emits in a structured shape
  (L07's central framing — the parallel is deliberate).
- **Parse defensively** → tool-call arguments can be malformed exactly like a broken `<answer>` tag;
  the same discipline applies.
- One sentence to carry into L07: *you can now make the model think before it answers; next you'll
  let that thinking decide to reach for a tool.*

[↑ Back to top](#teaching-an-llm-to-think-chain-of-thought-scratchpads-and-self-critique)
