# L06 Proctor Notes

Notes for whoever runs the L06 labs. One section per problem, keyed by lab id and problem number.
Times are rough and assume a semi-technical student with basic Python who completed L01–L02.

> Cross-cutting note: the four teacher demos (L0603 CoT / L0605 scratchpad / L0607 self-critique /
> L0609 when-it-hurts) make **live** Claude calls and need `ANTHROPIC_API_KEY` set (copy
> `.env.example` to `.env`). Two labs are also live — **L0604** (write a CoT prompt) and **L0608**
> (self-critique) — so they need a key too. The other two labs stay **offline** (pure Python):
> **L0606** (parse the scratchpad contract) and **L0610** (decide when to reason). Because the model
> varies run to run, a live run may not reproduce every effect the prose calls out — that variance is
> part of the lesson. Dry-run the demos before class (especially the marble problem in L0603 and the
> bat-and-ball in L0607/L0608 — confirm they actually fail zero-shot some of the time), and clear any
> cell outputs that hit the API before committing.
>
> The labs map to the four L06 subgoals: **L0604** → write a CoT prompt; **L0606** → scratchpad /
> structured-answer parsing; **L0608** → self-critique; **L0610** → recognize when reasoning helps
> vs. hurts.

## L0304_lab problem 1 — Trigger CoT with "let's think step by step"

- **Common gotchas:** forgetting to actually send both prompts (building strings but not calling
  `run`); using a high `temperature` so the zero-shot answer wobbles run to run; not printing the
  token count, which is half the point.
- **Unblockers:** "Make two prompts from `PROBLEM`: one ending in *'Answer with a single number
  only.'* and one ending in *'Let's think step by step.'* Run both with `run(...)` and print the
  returned text and token count." Expected final answer is **34** (48 pencils + 30 erasers − 9 − 5).
- **Time:** ~7 min.
- **Note:** needs `ANTHROPIC_API_KEY`. The zero-shot answer is *sometimes* wrong — that miss is the
  motivation for CoT, so don't "fix" it by picking an easier problem.

## L0304_lab problem 2 — Trigger CoT with a numbered scaffold

- **Common gotchas:** writing a scaffold that just restates "think step by step" without naming the
  steps; numbering steps that don't match the problem's actual structure.
- **Unblockers:** "Name the concrete steps: (1) total pencils, (2) total erasers, (3) subtract the
  give-aways, (4) add the remainders." Point out the output is more *consistently structured* than
  Problem 1's free-form CoT, even though both reach 34.
- **Time:** ~6 min.
- **Key point:** free-form vs. scaffold is the controllability dial — scaffold costs more tokens to
  write but stabilizes the output shape.

## L0304_lab problem 3 — Which trigger for which task? (written)

- **Common gotchas:** answering "step-by-step" for everything (misses that the easy classification
  wants `none`); confusing "idiosyncratic format" (a few-shot/worked-example job) with a reasoning job.
- **Unblockers:** expected: row 1 → `none` (zero-shot-easy, CoT is overhead); row 2 → `numbered` or
  `step-by-step` (multi-step, must show work); row 3 → `worked-example` (the model can't guess your
  format — show it one); row 4 → `numbered` (production prompt needs a *consistent* shape).
- **Time:** ~5 min.

## L0304_lab problem 4 — token-cost reasoning

- **Common gotchas:** none beyond reading the token counts off Problems 1–2; some students expect CoT
  to be "free."
- **Unblockers:** "Look at the `output_tokens` you printed. CoT is typically 3–10× the zero-shot
  output. That multiplier is the price of the accuracy."
- **Time:** ~3 min.
- **Key point:** this seeds L0610 — the cost is real, so reasoning is a trade-off, not a default.

## L0306_lab problem 1 — Extract the answer, fail loudly

- **Common gotchas:** returning `""` (or `None`) instead of raising when there's no `<answer>` block
  (the lesson's whole point is *fail loudly*); forgetting `re.DOTALL`, so a multi-line answer block
  won't match; using a greedy `(.*)` instead of the non-greedy `(.*?)`.
- **Unblockers:** "`re.search(r'<answer>(.*?)</answer>', reply, re.DOTALL)`. If it's `None`, `raise
  ValueError(reply)`; otherwise return `match.group(1).strip()`." The `answer_outside` and
  `no_tags_at_all` replies are the ones that must raise.
- **Time:** ~8 min.
- **Stretch:** ask what `no_closing` does — the unclosed `<thinking>` is irrelevant because the
  `<answer>` block is still well-formed, so it parses to `6`. A nice "parse what you need, ignore the
  rest" point.

## L0306_lab problem 2 — Separate thinking from answer

- **Common gotchas:** raising when `<thinking>` is missing (it's *optional* — return `None`); not
  reusing `extract_answer`, so the loud-failure behavior gets duplicated or lost.
- **Unblockers:** "Search for `<thinking>` separately and allow `None`; for the answer, just call
  your `extract_answer`. Return the tuple `(thinking, answer)`." Expected for `clean`:
  `("1 + 1 = 2, then 2 * 3 = 6.", "6")`.
- **Time:** ~6 min.
- **Key point:** the split is the deliverable — log `thinking`, consume `answer`.

## L0306_lab problem 3 — Run it over every crafted case

- **Common gotchas:** letting the first `ValueError` crash the loop instead of catching it and
  continuing; validating a reply that never parsed.
- **Unblockers:** "Wrap `extract_answer(reply)` in `try/except ValueError`; on the exception print a
  loud notice and continue." Expected: `clean`, `prose_then_answer`, `no_closing` → `6`;
  `answer_outside`, `no_tags_at_all` → CONTRACT BROKEN.
- **Time:** ~6 min.

## L0306_lab problem 4 — Why separate thinking from answer? (written)

- **Common gotchas:** giving one reason three ways ("it's cleaner"); missing the downstream framing.
- **Unblockers:** acceptable points: (1) **parsing** — code reads a field, not a paragraph; (2)
  **UX** — show the answer, hide/collapse the reasoning; (3) **evals/tracing** (L11–L12) score a clean
  answer field while the logged reasoning stays available for debugging.
- **Time:** ~5 min.

## L0308_lab problem 1 — First answer, then critique (two-step)

- **Common gotchas:** building the critique as a single user message instead of the three-turn
  `user(question) → assistant(answer) → user(framing)` shape; forgetting that the *first answer* must
  be captured before it can be critiqued.
- **Unblockers:** "The critique is a fresh `chat` over three messages: the original question, the
  model's first answer as an `assistant` turn, then your framing as a `user` turn." This reuses the
  multi-turn `messages` list from L02.
- **Time:** ~8 min.
- **Note:** needs `ANTHROPIC_API_KEY`. The first answer is *often* the wrong $0.10 — that's the setup
  for the sycophancy demo, so don't pick a question the model nails.

## L0308_lab problem 2 — Trigger sycophancy with a neutral framing

- **Common gotchas:** running the neutral critique once, seeing it catch the error, and concluding
  "self-critique works"; the point is the *distribution* — run it several times.
- **Unblockers:** "Call `critique(first, 'Review your answer above. Is it correct?')` a few times.
  Note how often it agrees with a wrong answer — that agreement is sycophancy."
- **Time:** ~5 min.
- **Key point:** a same-model, same-context critic has no new information to disagree with.

## L0308_lab problem 3 — Mitigate with adversarial framing

- **Common gotchas:** thinking the adversarial framing adds *facts* (it doesn't — it shifts the
  prior); expecting a 100% catch rate (it's higher, not perfect).
- **Unblockers:** "Use a framing that tells the model to *find the flaw* and *show the algebra*.
  Compare its catch rate to Problem 2." The correct answer is the ball costing **$0.05**.
- **Time:** ~6 min.

## L0308_lab problem 4 — When is two-step worth it? (written)

- **Common gotchas:** naming "ask again" as a mitigation (that's the failure, not a fix); claiming
  two-step is always better (it costs an extra round-trip).
- **Unblockers:** acceptable mitigations: different model as critic, retrieved evidence / ground
  truth, adversarial role. Two-step earns its cost when you need to *change the model, framing, or
  inject evidence* between passes; single-prompt is fine when latency/cost is tight and a light check
  suffices.
- **Time:** ~5 min.

## L0310_lab problem 1 — Reason, or answer cold?

- **Common gotchas:** marking the easy classification (row 2) and the short translation (row 4) as
  `reason` — both are zero-shot-easy, where CoT is wasted overhead; under-valuing the multi-constraint
  puzzle (row 3).
- **Unblockers:** "Ask: is this in the help-class — multi-step math, logical deduction, ambiguous
  classification, multi-constraint generation? If yes → `reason`; if the model nails it cold → `cold`."
  Answers: 1 reason, 2 cold, 3 reason, 4 cold.
- **Time:** ~5 min.

## L0310_lab problem 2 — Estimate what CoT costs

- **Common gotchas:** dividing by 1,000 instead of 1,000,000 for "per-million-token" pricing;
  computing the cost once instead of recognizing it's paid on *every* call.
- **Unblockers:** "`reasoning_tokens / 1_000_000 * OUTPUT_USD_PER_MTOK`. The long-CoT preamble costs
  ~5× the short one — linear in the reasoning length, every call."
- **Time:** ~4 min.
- **Key point:** output tokens are the expensive direction (recall L01), and CoT spends them.

## L0310_lab problem 3 — Defend a choice against a budget (written)

- **Common gotchas:** ignoring the stated budget (answering on accuracy alone); treating the
  talked-itself-wrong row as a cost question when it's an *accuracy* question.
- **Unblockers:** expected: row 1 → `reason` (offline batch, accuracy matters, latency is free); row
  2 → `cold` (300ms budget can't afford a reasoning preamble); row 3 → `cold` (CoT actively *lowers*
  accuracy here — more reasoning is worse, not slower).
- **Time:** ~5 min.

## L0310_lab problem 4 — Two ways reasoning hurts (written)

- **Common gotchas:** giving two phrasings of "it costs more"; missing the *accuracy* failure mode.
- **Unblockers:** acceptable: (1) zero-shot-easy tasks — added latency/tokens, no accuracy gain; (2)
  the model "talks itself into" a wrong answer — CoT lowers accuracy; (3) tight-latency user-facing
  flows can't afford it. Any two distinct cases.
- **Time:** ~4 min.
