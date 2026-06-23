# L03: Teacher-led demos — Teaching an LLM to think via prompting

> Sibling docs: [objectives.md](objectives.md) (what the lesson aims for), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md).
>
> **Audience for this file:** the teacher running L03. Every demo below is *teacher-driven, no student participation*. Student-driven exercises live in the L03 labs (separate file).

## How to read this file

Each demo is a self-contained block with:

- **Goal** — the single insight the demo should land. Tied to a learning objective from [objectives.md](objectives.md).
- **Pre-flight** — what the teacher needs loaded before class.
- **Live script** — the order of operations during the demo. Treat it as a checklist, not a teleprompter.
- **What to highlight** — the moment(s) where the teacher should slow down and call out the takeaway out loud.
- **If the demo misbehaves** — graceful fallback for when the model surprises you (because it will).

The demos are ordered to match the four subgoals from the lesson-plan row, but they are not strictly sequential — Demo 4 ("when CoT hurts") deliberately uses a contrast that builds on Demos 1–3, so run them in order on the first delivery of the lesson.

## Pre-flight (once, at the top of the lesson)

The teacher should have, before the first demo starts:

- A working REPL or notebook with the project's Claude SDK setup (per the project's `uv` env).
- The four demo prompts below pre-loaded as variables or cells, so each demo is a *single keystroke* to run. Live-typing prompts during demos eats time and breaks pacing.
- A second model client configured for Demo 3's "different-model critic" beat. **Primary model: Claude Sonnet 4.6** (the course's anchor). **Cheap critic: Claude Haiku 4.5** (introduced briefly here as a different-model critic; treated more rigorously in L09).
- A way to project token counts and latency alongside outputs (a small wrapper that prints `input_tokens`, `output_tokens`, and wall-clock time after every call). This is essential for Demo 4, where the *cost* of reasoning is the punchline.

> Why pre-loaded prompts: L03 lives or dies on contrast — same input, different framing, different output. If the teacher mistypes a prompt mid-demo, the contrast breaks and the lesson lands as "the model is unpredictable" instead of "this technique caused this change."

## Demo 1 — CoT made visible (Subgoal 1)

**Goal:** show that asking for step-by-step reasoning changes the answer on a problem the model gets wrong zero-shot. Land the framing from [objectives.md](objectives.md): *"reasoning is a tokens-on-the-page phenomenon."*

**Pre-flight:**

- Pick a problem the chosen model gets wrong roughly half the time zero-shot but reliably right with CoT. Multi-step probability and constraint-satisfaction problems work well for current Claude models. Suggested prompt:

  > A bag contains 5 red, 7 blue, and 3 green marbles. I draw 3 without replacement. What is the probability all three are different colors? Answer with a single number.

  <!-- *NEED INPUT*: confirm this problem is in the right difficulty band for the target model — the teacher should dry-run it 5x before class and see at least 2 zero-shot failures, or pick a different problem. If pinning to a smaller model, use a harder problem; for a larger model, use a multi-step constraint puzzle instead. -->

- Have a known-correct answer pre-computed and on a slide (so the teacher can confirm correctness in one glance).

**Live script:**

1. Run the prompt zero-shot, output answer only. Read the model's answer aloud, mark it ✓ or ✗ against the slide.
2. Re-run the *exact same prompt* with `Let's think step by step.` appended. Read the reasoning aloud (or have it on screen), then the final answer.
3. Re-run again with a numbered scaffold:
   > Solve the problem in this order: (1) count total ways to draw 3 marbles, (2) count favorable outcomes, (3) divide.
4. Show all three outputs side by side: zero-shot, free-form CoT, scaffolded CoT.

**What to highlight:**

- The model isn't different across the three runs — only the prompt is. The "thinking" is just more tokens.
- Free-form CoT vs. scaffolded CoT: free-form is cheaper to write, scaffolded is more controllable. Foreshadow Subgoal 4 ("when does which help?").
- Token counts: scaffolded CoT typically costs 3–10x more output tokens than zero-shot.

**If the demo misbehaves:**

- If the model nails the zero-shot answer on the day, fall back to a harder backup prompt (keep one warmed up). Do not change the *technique* on the fly — the contrast is the whole demo.
- If the CoT reasoning is wrong but the final answer is right, lean into it: this is exactly the failure mode Subgoal 3 (self-critique) addresses, and it foreshadows that demo nicely.

## Demo 2 — Scratchpad as interface contract (Subgoal 2)

**Goal:** show that `<thinking>` tags don't *do* anything — they're a contract for downstream parsers. Wrap the same reasoning, but make it cleanly extractable.

**Pre-flight:**

- Reuse Demo 1's problem so students see the technique stack on something familiar.
- Have a tiny Python parser ready (regex or `re.search` on `<answer>...</answer>`) so the teacher can show the extracted answer in one line.

**Live script:**

1. Take Demo 1's scaffolded CoT prompt and add: *"Put your reasoning inside `<thinking>...</thinking>` tags. Put only your final numeric answer inside `<answer>...</answer>` tags."*
2. Run it. Show the structured output.
3. Run the parser: pull the contents of `<answer>` and print them. Note that the reasoning is right there for debugging if needed, but the program-readable answer is now trivial to extract.
4. Compare to Demo 1's free-form CoT output — to extract the final number from that, the teacher would need to scan the last line, hope the model is consistent, and write fragile parsing.

**What to highlight:**

- The model already reasoned in Demo 1. The tags add zero capability — they add a *contract*. This is the same kind of move as JSON-mode output: shape, not substance.
- Why this matters for evals and tool-calling pipelines (foreshadow L04): downstream code consumes structured fields, not prose.
- The model can ignore the tag contract. Showing a single failure (e.g. it puts the answer outside `<answer>` tags) is *more* educational than a clean run — it teaches that contracts are best-effort and need parser fallbacks.

**If the demo misbehaves:**

- If the model stubbornly emits clean tags every run, run a deliberately ambiguous prompt to provoke a tag-violation (e.g. ask for the answer "as a fraction or a decimal"). Use the failure to discuss validation.

## Demo 3 — Self-critique: the good, the bad, the sycophantic (Subgoal 3)

**Goal:** show self-critique improving an answer, *and* show it failing via sycophantic agreement, in the same demo. Land that self-critique is a sampling technique, not a correctness oracle.

**Pre-flight:**

- A prompt where the model often produces a plausible-but-wrong first answer. A classic: a logic puzzle with a misleading surface (e.g. *"A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?"* — many models still fall for "$0.10").
- Three critique framings prepared:
  1. **Same-model, neutral framing** — *"Review your answer above. Is it correct?"*
  2. **Same-model, adversarial framing** — *"You are a skeptical reviewer. Find the flaw in the answer above and produce a corrected version."*
  3. **Different-model critique** — same as (1) but routed to the secondary model client.

  <!-- *NEED INPUT*: the lesson-plan row mentions self-critique without specifying single-prompt vs. two-step. The objectives doc keeps both in scope; this demo uses two-step (separate calls). If the course settles on single-prompt as the canonical pattern, swap (1)–(3) for inline-critique variants. -->

**Live script:**

1. Run the prompt with no CoT, capture the (probably wrong) answer.
2. Run critique framing (1) — the neutral same-model self-check. Roughly half the time the model will agree with its wrong answer. Read it aloud either way.
3. Run framing (2) — adversarial same-model. Show the higher catch rate. Discuss *why*: the framing shifts the model into a different "role" with a different prior over what constitutes a good answer.
4. Run framing (3) — different-model critique. Show the result. Discuss the trade-off: usually catches more, costs more, adds latency.

**What to highlight:**

- Sycophancy is the failure mode to remember. Name it explicitly. If framing (1) catches the error this run, do framing (1) again with a slightly different problem and let the audience watch sycophancy happen live. (This is one of the few demos worth running twice.)
- A critic that has *no new information* is a weak critic. Adversarial framing, different model, retrieved evidence — these are all ways of injecting new information.
- Foreshadow that L10 (model power) revisits the "use a small cheap model as critic" pattern more rigorously.

**If the demo misbehaves:**

- If the model gets the puzzle right zero-shot every time on the day, fall back to a multi-step arithmetic problem and tweak the numbers until the model errs. Have one ready.

## Demo 4 — When reasoning hurts (Subgoal 4)

**Goal:** show explicit reasoning making things *worse* — slower, more expensive, no accuracy gain (or even *worse* accuracy). The whole point of L03 is that reasoning is a tool, not a default.

**Pre-flight:**

- Two contrasting tasks:
  - **Task A — easy zero-shot:** a sentiment classification on a clearly-positive review (*"I love this product, it's amazing — five stars!"* → `positive`). The model nails this in one or two output tokens.
  - **Task B — talked-into-the-wrong-answer:** a simple factual question with a misleading hint (e.g. *"Most people think the answer to X is Y, but is that actually correct? Reason carefully."*) where free-form CoT often constructs a plausible but wrong justification. <!-- *NEED INPUT*: pick a task in this style that fits the target model — needs a dry-run pass to confirm the failure mode reproduces. The point is to show CoT making things worse, so if the model handles it cleanly, find a harder one or use a different model class. -->
- The token-count + latency wrapper from pre-flight is essential here.

**Live script:**

1. Run Task A zero-shot. Note the output: ~2 tokens, near-zero latency, correct.
2. Run Task A with `Let's think step by step.` Note the output: 50–200 tokens of reasoning, higher latency, **same answer**. Show the cost difference numerically.
3. Run Task B zero-shot vs. Task B with free-form CoT. Show the case where CoT actually *changes the answer in the wrong direction* (or, if that doesn't reproduce on the day, where CoT and zero-shot disagree and CoT is the one that's wrong).
4. Tie back to the budget: every CoT token is paid for. Reasoning is not free.

**What to highlight:**

- The decision to use CoT/scratchpad/self-critique is a *trade-off*, not a default. By the end of L03, students should be making this trade-off consciously.
- Latency-sensitive flows (chat UIs, real-time agents) often can't afford CoT on every call even when accuracy would benefit.
- Bridge to L09: choosing the right *model* for a step is a sibling decision to choosing the right *reasoning depth* for a step.

**If the demo misbehaves:**

- If Task B doesn't reproduce a CoT-induced error on the day, fall back to a token-cost demo only. The latency/cost contrast on Task A still lands the main point.

## Optional bridge demo — toward tool calling (L04)

If time allows, run one final demo that previews L04: ask the model the same Task B question but give it a single tool (a calculator, or a "lookup" stub). Show that *the decision to call the tool* is itself a reasoning step — and that everything from Demos 1–4 (CoT, scratchpad, self-critique, when-not-to-reason) applies inside the tool-calling loop. Don't teach the tool-calling protocol here; just show the shape.

<!-- *NEED INPUT*: include this bridge demo, or save it as the opener for L04? -->

## Pacing notes for the teacher

- **Per-demo time:** 8–12 minutes including the post-demo discussion. Four demos plus the optional bridge fits in a 50–60 minute block. <!-- *NEED INPUT*: confirm against the lesson-time budget once duration is pinned in objectives.md's open questions. -->
- **Variance budget:** model outputs vary run-to-run. Budget at least one re-run per demo. If a demo lands cleanly the first time, don't re-run for the sake of it — use the time to extend the discussion.
- **The audience watches, doesn't participate.** Resist the temptation to ask "what do you think will happen?" — that is a lab pattern, not a demo pattern. Hands-on practice is for the L03 labs.

## Open authoring questions

- <!-- *NEED INPUT*: are the demos run in a Jupyter notebook the teacher projects, or in a slide-embedded REPL, or via a custom demo runner script? Affects how prompts are pre-loaded. -->
- <!-- *NEED INPUT*: should Demo 3 introduce different-model critique here, or defer to L10 (model power)? Mirrors the same open question in [objectives.md](objectives.md). -->
- <!-- *NEED INPUT*: should this lesson use Anthropic's extended-thinking API anywhere, or stay strictly prompt-only? Mirrored from [objectives.md](objectives.md). -->
- <!-- *NEED INPUT*: a pointer/link to where the demo prompts live as code (a `demos/` subdir? inline in a notebook?) — not yet decided in non-draft docs. -->
