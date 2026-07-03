# L02 Proctor Notes

Notes for whoever runs the L02 labs. One section per problem, keyed by lab id and problem number.
Times are rough and assume a semi-technical student with basic Python who completed L01.

> Cross-cutting note: the teacher demos (L0203 / L0205 / L0207 / L0209) make **live** Claude calls
> and need `ANTHROPIC_API_KEY` set (copy `.env.example` to `.env`); the **L0206 and L0210 labs** are
> mostly pure-Python but each ends with one live call (L0206 Problem 3, L0210 Problem 3), so they
> need a key too. The **L0204 and L0208 labs stay offline** (pure Python — building message lists,
> counting tokens), no key required. Because the model varies run to run, a live run may not
> reproduce every effect the prose calls out — that variance is part of the lesson. Run the demos
> yourself before class, and clear cell outputs (any that hit the API) before committing.
>
> The labs are: **L0204** (roles & content placement), **L0206** (structured output & defensive
> parsing), **L0208** (few-shot & its cost), **L0210** (the single-step task catalog). The first
> three map one-to-one to the first three L02 subgoals; **L0210 covers Subgoal 4** (the task shapes:
> extraction, classification, ranking, constrained generation, summarization).

## L0204_lab problem 1 — Build a multi-turn conversation

- **Common gotchas:** forgetting the leading `system` message; appending only `user` turns (no
  placeholder `assistant`), so the list doesn't alternate; building the list but not returning it.
- **Unblockers:** "Start the list with `Message.system(system)`. Then for each question, append two
  things: the user turn and a placeholder assistant turn." Expected length is `1 + 2*len(questions)`.
- **Time:** ~6 min.
- **Stretch:** ask why we fake the assistant replies here (the point is the *shape* of the list you
  own and re-send, not the content).

## L0204_lab problem 2 — system or user?

- **Common gotchas:** putting per-call data (snippet 4, the user's name/ticket) in `system` — this
  is exactly the reuse-poisoning footgun from the demo; flagging the policy snippets (1, 3, 5) as
  `user`.
- **Unblockers:** "Ask: is this true on *every* call of this prompt, or just this one call?
  Always-true → `system`; this-call-only → `user`." Answers: 1 system, 2 user, 3 system, 4 user,
  5 system.
- **Time:** ~5 min.
- **Key point:** snippet 3 ("never reveal .env") goes in `system` but is *weighted, not enforced* —
  a real secret belongs outside the model, not in the prompt.

## L0204_lab problem 3 — The cost of a fat system message

- **Common gotchas:** counting the system message once instead of once *per turn*; multiplying by
  the wrong turn count; expecting the fat/lean gap to be small (the `* 60` repetition makes it
  large on purpose).
- **Unblockers:** "The system message is re-sent on every call, so over `turns` turns it is counted
  `turns` times — `est_tokens(system) * turns`."
- **Time:** ~5 min.
- **Key point:** this is the cost half of "keep `system` lean," and the motivation for prompt
  caching (L19). Don't teach caching here — just name it.

## L0204_lab problem 4 — Continue or start fresh? (written)

- **Common gotchas:** answering "always continue" (ignores the cost staircase and accumulated
  drift) or "always fresh" (throws away load-bearing context).
- **Unblockers:** expected: row 1 → continue (the follow-up needs the prior answers); row 2 →
  fresh (unrelated task; dodge the 40-turn cost staircase); row 3 → fresh (the model is looping on
  its own bad prior turns — the first-call-vs-Nth-call degradation).
- **Time:** ~5 min.

## L0206_lab problem 1 — The defensive parser

- **Common gotchas:** returning a silent `{}` on failure instead of raising (the lesson's whole
  point is *fail loudly*); forgetting `re.DOTALL`, so the regex won't match a `{...}` block that
  spans newlines; catching a bare `Exception` instead of `json.JSONDecodeError`.
- **Unblockers:** "Three steps: try `json.loads`; on failure `re.search(r'\{.*\}', reply,
  re.DOTALL)` and retry; still nothing → `raise ValueError(...)` with the raw reply." The
  `prose_wrapped` reply is the one the regex step must save.
- **Time:** ~10 min.
- **Stretch:** ask what happens if the reply contains *two* JSON objects (the greedy `{.*}` grabs
  the outermost span — a real-world wrinkle to name, not fix here).

## L0206_lab problem 2 — Validate the contract

- **Common gotchas:** treating "it parsed" as "it's valid" and skipping validation; rejecting a
  `null`/missing `assignee` (the spec allows it); not handling a `status` of `None` before the
  membership check.
- **Unblockers:** "A successful parse is not an honored contract. Check the two required keys are
  present, then check `status` is in `ALLOWED_STATUS`. Return a list of problem strings; empty
  list means valid." `"blocked"` should produce a status problem.
- **Time:** ~7 min.
- **Key point:** an enum is a *contract, not a constraint* — the model can return a value outside
  the set, and validation is what catches it.

## L0206_lab problem 3 — Run it over crafted cases, then a live reply

- **Common gotchas:** letting the `malformed` reply's `ValueError` crash the loop instead of
  catching it and continuing; validating a record that never parsed; forgetting the second part —
  pointing the same parser at a live model reply.
- **Unblockers:** "Wrap `parse_json_object` in try/except `ValueError`; on the exception, print a
  loud notice and `continue`; only validate the records that parsed." Expected: `clean` valid,
  `prose_wrapped` salvaged-and-valid, `malformed` fails loudly. The live reply is *usually* clean —
  that's the point: the crafted `malformed`/`prose_wrapped` cases exist because a well-behaved model
  rarely produces them, yet your parser must survive them when it does.
- **Note:** needs `ANTHROPIC_API_KEY` for the live call; remind students to clear that output.
- **Time:** ~8 min.

## L0206_lab problem 4 — Why structured output, before agents? (written)

- **Common gotchas:** answering only "so it's neat"; missing the core idea that it makes the
  response *programmatic* (indexable) rather than *conversational* (prose you must read).
- **Unblockers:** acceptable points: it's the precondition for evals (L12), tool calling (L07), and
  multi-step pipelines; L07 adds tool-use-as-schema to *force* conformance, but defensive parsing
  still applies because tool-call arguments can be malformed too.
- **Time:** ~5 min.

## L0208_lab problem 1 — Few-shot as alternating turns

- **Common gotchas:** putting the example *label* in a `user` turn instead of an `assistant` turn
  (the surprise: the assistant role holds the fake "model said this" output); forgetting to append
  the real input as the final `user` turn.
- **Unblockers:** "For each `(text, label)`: append `Message.user(text)` then
  `Message.assistant(label)`. After the loop, append `Message.user(real_input)`." Expected length
  is `2*len(EXAMPLES) + 1`.
- **Time:** ~7 min.

## L0208_lab problem 2 — Few-shot as a single block

- **Common gotchas:** returning multiple messages instead of one; not including the real input in
  the block; over-formatting the block (the exact layout doesn't matter, the single-message shape
  does).
- **Unblockers:** "Build one string: an `Examples:` header, one `text -> label` line per example,
  then the real input. Return `[Message.user(that_string)]` — a single message." Result should have
  `len == 1`.
- **Time:** ~6 min.
- **Key point:** placement (turns vs block) matters less than content; this problem just makes the
  two layouts concrete.

## L0208_lab problem 3 — The per-call cost of examples

- **Common gotchas:** counting only the example inputs and not the labels; computing the cost once
  instead of recognizing it is paid on *every* call.
- **Unblockers:** "Sum `est_tokens(text) + est_tokens(label)` over the examples. The loop shows the
  total growing as you add examples — and that whole total rides along on every single call."
- **Time:** ~5 min.
- **Key point:** few-shot is a real cost-vs-quality dial, linear in example count and paid forever.

## L0208_lab problem 4 — When is few-shot the wrong tool? (written)

- **Common gotchas:** answering "few-shot" for everything; missing that a *reasoning* task wants
  chain-of-thought (L06), not more examples.
- **Unblockers:** expected: row 1 → not few-shot (a clear instruction already works); row 2 →
  few-shot (idiosyncratic format the model can't guess); row 3 → not few-shot (needs reasoning →
  L06's CoT); row 4 → not few-shot (examples would dominate the window → retrieval/other approach).
- **Time:** ~5 min.

## L0210_lab problem 1 — Classification: prompt + validator

- **Common gotchas:** `validate_label` checking `label == allowed` (comparing to the whole list)
  instead of `label in allowed`; returning a bare bool instead of a list of problem strings;
  over-engineering `classify_prompt` (it just needs to name the labels and say "return only the
  label").
- **Unblockers:** "`classify_prompt` = an instruction plus `', '.join(labels)`. `validate_label` =
  `[] if label in allowed else ["...not in set..."]`." The `"bug"` case should produce a problem
  (the model's near-miss for `"P0-bug"`).
- **Time:** ~6 min.
- **Key point:** this is the enum-is-a-contract idea from L0206 applied to labels — the model can
  return anything; the validator is what enforces the set.

## L0210_lab problem 2 — Ranking: validate the set is preserved

- **Common gotchas:** checking only length (misses a dropped-and-duplicated pair that keeps the
  length the same); forgetting the duplicate check entirely; comparing lists instead of sets (a
  valid reordering is not equal as a list).
- **Unblockers:** "Two checks: `len(ranked_ids) != len(set(ranked_ids))` catches duplicates;
  `set(ranked_ids) != set(candidate_ids)` catches drops and inventions." The `[3, 1, 2, 2]` case
  exercises both at once (2 duplicated, 4 missing).
- **Time:** ~6 min.
- **Key point:** ranking's failure is *silent* — the output looks like a plausible order even when an
  item vanished. The set check is the whole reason to reference candidates by id.

## L0210_lab problem 3 — Constrained generation: count + length, then a live call

- **Common gotchas:** validating only the count and not the per-item length bound; using
  `len(line)` (characters) instead of `len(line.split())` (words); letting a malformed live reply's
  `ValueError` crash the cell instead of noting it (the parser is *given*, so this is rare, but the
  live reply can still surprise).
- **Unblockers:** "`if len(items) != n` for the count; a loop with `len(line.split()) > max_words`
  for the bound. Collect problems in a list." The live call usually returns a clean array of 5 — the
  point is that the *validator* would catch it if it didn't.
- **Note:** needs `ANTHROPIC_API_KEY` for the live call; remind students to clear that output before
  committing.
- **Time:** ~9 min.
- **Key point:** a constraint you don't re-check in code is one the model is free to miss; higher
  temperature (0.7 here, for variety) makes a miss more likely, which is exactly why the check exists.

## L0210_lab problem 4 — Name the shape (written)

- **Common gotchas:** naming a *technique* (e.g. "few-shot") instead of a *task shape*; giving a
  validation check that doesn't match the shape (e.g. "check it parses" for summarization).
- **Unblockers:** expected: row 1 → extraction (validate required keys present); row 2 → ranking
  (every id present exactly once); row 3 → constrained generation (exactly 3, each ≤ 280 chars);
  row 4 → summarization/transformation (no invented facts, length within bound). The solutions
  notebook fills the table in; use it as the answer key.
- **Time:** ~5 min.
- **Key point:** naming the shape *first* is the habit — it tells you the prompt to write and the
  validator to reach for before you touch the model.
