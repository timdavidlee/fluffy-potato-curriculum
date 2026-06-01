# L01 Proctor Notes

Notes for whoever runs the L01 labs. One section per problem, keyed by lab id. Times are rough and
assume a semi-technical student with basic Python.

> Cross-cutting setup gotcha: the first `tiktoken.get_encoding(...)` call downloads the vocabulary
> over the network and caches it. The very first run in a fresh environment needs internet; after
> that it is offline. If a student is fully air-gapped, have them run the setup cell once on the
> classroom network before disconnecting.

## L0104_lab problem 1 — Count tokens

- **Common gotchas:** forgetting to `return len(...)` (returns `None`); calling `.encode` on the
  encoding *name* string instead of getting the encoding first.
- **Unblockers:** "What does `enc.encode(text)` give you back?" (a list of ints) → "so how many
  tokens is that?" (`len`).
- **Time:** ~5 min.
- **Stretch:** have them guess the four counts *before* running; note where intuition was wrong.

## L0104_lab problem 2 — See the boundaries

- **Common gotchas:** decoding the whole id list at once (`enc.decode(ids)`) instead of one id at a
  time — that just reconstructs the original string with no boundaries shown.
- **Unblockers:** point them back to the demo's `|`-joined output; the key is `enc.decode([id])`
  for each `id` individually (note the single-element list).
- **Time:** ~5 min.
- **Stretch:** run `show_boundaries` on the JSON sample and count how many tokens the braces/quotes eat.

## L0104_lab problem 3 — Tokenizers disagree

- **Common gotchas:** `o200k_base` missing on a very old `tiktoken` — the repo pins a current
  version, so this should be fine, but if it errors, any second encoding (e.g. `p50k_base`) makes
  the point.
- **Unblockers:** the answer they should reach: there is no single universal token count because the
  count depends on *which* tokenizer, and tokenizers are trained per model family.
- **Time:** ~5 min including the written answer.

## L0104_lab problem 4 — Where the rule of thumb breaks

- **Common gotchas:** leaving `ratio = 0.0`; integer vs float division (Python 3 `/` is float, so
  this is usually fine).
- **Unblockers:** "chars per token = characters ÷ tokens" — they already have both numbers.
- **Time:** ~5 min.
- **Key point to land:** JSON is far below 4 chars/token because structural characters each cost a
  token; the ≈4 rule is an English-prose rule.

## L0105_lab problem 1 — Headroom

- **Common gotchas:** adding instead of subtracting; forgetting to include `reserved_output` in the
  budget (the answer must fit *with room for the reply*).
- **Unblockers:** "Everything competes for the same 200k — list the four things, then subtract them
  all from `WINDOW`." A negative result means it won't fit.
- **Time:** ~5 min.

## L0105_lab problem 2 — Match the failure mode

- **Common gotchas:** confusing silent truncation with quality degradation. Truncation = turns are
  *dropped* (gone); degradation = everything is *present* but the model attends poorly.
- **Unblockers:** scenario 1 = hard rejection, 2 = silent truncation, 3 = quality degradation.
- **Time:** ~5 min.

## L0105_lab problem 3 — Cost of one call

- **Common gotchas:** dividing by 1,000 instead of 1,000,000 (rates are per *million* tokens); this
  yields a cost 1000× too high — a great teachable moment.
- **Unblockers:** "the rate is per million tokens, so divide the token count by 1,000,000 first."
- **Time:** ~5 min.

## L0105_lab problem 4 — The input/output asymmetry

- **Common gotchas:** expecting the larger *total* token count to be cheaper/pricier; the point is
  the *direction*, not the total (both calls are ~2,050 tokens).
- **Unblockers:** "Which call has more *output* tokens? Output costs ~5× input here."
- **Time:** ~5 min.
- **Key point:** long prompt + short answer is often cheaper than short prompt + long answer.

## L0105_lab problem 5 — The conversation-history staircase

- **Common gotchas:** not accumulating `cumulative` (re-counting only the new turn); forgetting that
  the *whole* history is re-sent each turn.
- **Unblockers:** "Each turn, the input you send is everything so far — add `PER_TURN_INPUT` to a
  running total before computing cost."
- **Time:** ~7 min.

## L0105_lab problem 6 (stretch) — Order-of-magnitude agent budget

- **Common gotchas:** none mechanical; this is about *feeling* the multiplication.
- **Unblockers:** "One step is ~nothing. Multiply by steps, then by dev iterations. Is the
  three-figure-cents/dollars number still 'too small to matter' when you iterate 100×?"
- **Time:** ~5 min. Skip if running short.

## L0106_lab problem 1 — Five runs at temperature 0

- **Environment gotcha:** this lab makes **real API calls** and needs `ANTHROPIC_API_KEY`. Without
  it, `sample_n` returns placeholder strings so the notebook still runs — make sure students know
  the placeholders are not real model output. A `$5` spend cap is plenty for the class.
- **Common gotchas:** forgetting `max_tokens=16` (long, rambling names); rebuilding the client every
  call is fine here but mention it's wasteful at scale.
- **Unblockers:** point to the demo's `sample_n`; the shape is a loop calling
  `client.chat([Message.user(PROMPT)], max_tokens=16, temperature=temperature)`.
- **Time:** ~7 min (network-bound).

## L0106_lab problem 2 — Five runs at temperature 1

- **Common gotchas:** expecting *guaranteed* variety — occasionally temperature 1 repeats. If the
  spread is dull, that's a real (if anticlimactic) observation, not a bug.
- **Unblockers:** none; it reuses `sample_n`.
- **Time:** ~3 min.
- **Stretch:** swap in a more open-ended prompt ("a one-sentence story opener about a fox") for a
  wider spread.

## L0106_lab problem 3 — Pick a temperature

- **Common gotchas:** choosing high temperature for extraction/classification "to be safe" — the
  opposite of what you want.
- **Unblockers:** expected answers: classification → low; brainstorming → high; JSON extraction →
  low; tool routing → low.
- **Time:** ~5 min.

## L0106_lab problem 4 — Why isn't temperature 0 perfectly deterministic?

- **Common gotchas:** answering "because temperature 0 is random" — it is the *lowest*-variance
  setting, not a random one.
- **Unblockers:** acceptable causes: floating-point non-determinism, server-side batching,
  tie-breaking between equally-likely tokens.
- **Time:** ~5 min.
- **Key point:** set the expectation now so a flaky eval later doesn't read as a bug.
