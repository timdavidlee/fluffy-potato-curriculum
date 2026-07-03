# L01 Proctor Notes

Notes for whoever runs L01. The lesson is **one connected chain** — next-word prediction → tokens
→ tokenization reality → model scale → temperature → preambles → budgeting. Teach the demos in
number order; each hands the next its premise. Times are rough (semi-technical student, basic
Python).

## Cross-cutting setup gotchas

- **GPT-2 ladder download (Demos 1, 3.5, 3.6, temperature lab).** The prediction/scale demos load
  local models via `transformers`: `gpt2` (124M), `gpt2-medium` (355M), `gpt2-large` (774M) —
  together ~5 GB on first download, then cached and fully offline. **Download them once before
  class**, not live. They run on CPU; no GPU or API key needed. These demos are deterministic — the
  numbers below reproduce exactly.
- **tiktoken vocab (tokenization demos + lab).** The first `tiktoken.get_encoding(...)` call
  downloads the vocabulary over the network, then caches it. Air-gapped rooms: run the setup cell
  once on the classroom network first.
- **Live API notebooks.** Temperature §2 (**L0107**), the temperature lab's Problem 2 (**L0108**),
  and the preambles demo (**L0109**) make **live** Claude calls — set `ANTHROPIC_API_KEY` (copy
  `.env.example` to `.env`). Constructing `AnthropicClient()` raises a clear error if it's missing.
  Keep `max_tokens` small; remind students to clear outputs of any cell that hit the API before
  committing. The budgeting demo/lab (**L0110/L0111**) are **offline** (tiktoken + illustrative
  rates) — no key needed.

## Teacher demo notebooks (no student participation)

- **L0103 — next-word prediction.** Land the one mental model: text in → a *distribution* over the
  next token → sample → append → repeat. On `"Water is made of hydrogen and"`, `gpt2` leads with
  ` oxygen` (~0.46) but *hedges* (` helium` ~0.28) — say "it ranked oxygen, it didn't *know* it."
  The greedy loop shows a sentence assembling one token at a time. End on **no memory between calls**
  — the fact the whole lesson hangs on.
- **L0104 — sub-word tokens.** Motivate *why* sub-word (unbounded word vocab vs. too-long char
  sequences). Then the real-string fragmentation: names, code, JSON, non-Latin. English ≈ 4.4
  chars/token; JSON ≈ 2.9. "Every cost and window number later is downstream of this count."
- **L0106 — model scale ladder.** Same prompt, three sizes: ` oxygen` climbs **0.46 → 0.63 → 0.84**.
  Draw the boundary out loud — this is *mechanistic* (capability sharpens prediction); **which**
  model/provider to pick per capability (OCR, planning, execution) is **L13**, not here.
- **L0107 — temperature.** §1 is offline: temperature reshapes the *same* GPT-2 distribution
  (T=0.5 sharpens ` oxygen` → ~0.73; T=2.0 flattens → ~0.03). §2 is the live Claude sweep. Land
  "temperature 0 is *low* variance, not zero."
- **L0109 — front-loading & preambles.** Bare vs front-loaded output (the context *you* provide is
  the lever you control). Then the sting: the reusable preamble is re-sent — count it once, watch
  it ride along in every call's `input_tokens`. Hands straight to budgeting.
- **L0110 — budgeting.** The payoff: the overhead you built (preamble + history) hits two budgets —
  the 200k window (space) and per-token cost (money). Watch the window meter fill, the cost
  asymmetry (output ~5× input), and the conversation staircase. **Rates in the notebook are
  illustrative — pull live Claude pricing before quoting a real figure.**

## L0105_lab problem 1 — Count tokens

- **Common gotchas:** forgetting `return len(...)` (returns `None`); calling `.encode` on the
  encoding *name* instead of the `ENC` object.
- **Unblockers:** "What does `ENC.encode(text)` return?" (a list of ints) → "so how many tokens?" (`len`).
- **Time:** ~4 min.

## L0105_lab problem 2 — See the boundaries

- **Common gotchas:** decoding the whole id list at once (`ENC.decode(ids)`) instead of one id at a
  time — that just rebuilds the string with no boundaries.
- **Unblockers:** the key is `ENC.decode([tid])` per id (note the single-element list), joined with `|`.
- **Time:** ~5 min.

## L0105_lab problem 3 — Proper names fragment

- **Common gotchas:** expecting a familiar-looking name to be one token; `Reykjavik` is ~4 tokens,
  `Nnamdi Azikiwe` ~6 — names rare in training data are spelled out in pieces.
- **Unblockers:** "count tokens for each name and compare to its letter count."
- **Time:** ~4 min.
- **Key point:** this is *why* eyeball/character estimates fail on the inputs agents actually see.

## L0105_lab problem 4 — Chars per token: English vs JSON

- **Common gotchas:** expecting JSON to obey the ≈4 rule; leaving the ratio unset.
- **Unblockers:** "chars per token = characters ÷ tokens" — they have both numbers.
- **Time:** ~5 min.
- **Key point:** English ≈ 4.4, JSON ≈ 2.9 — every structural character (`{ } " :`) costs a token;
  the ≈4 rule is an English-prose rule.

## L0108_lab problem 1 — Reshape a distribution with temperature (offline)

- **Common gotchas:** dividing after softmax instead of before (temperature scales the **logits**,
  then softmax); forgetting `float(...)`.
- **Unblockers:** `torch.softmax(LOGITS / temperature, dim=-1).max()`. Sharp (T=0.5) should give a
  higher top probability than flat (T=2.0).
- **Time:** ~6 min.
- **Key point:** temperature reshapes the distribution *before* sampling — same model, same prompt.

## L0108_lab problem 2 — Measure spread at two temperatures (live)

- **Environment note:** **live** Claude calls — `ANTHROPIC_API_KEY` required; outputs vary run to
  run. Low temperature stays tight, high spreads. Remind students to clear outputs before committing.
- **Common gotchas:** not returning the list; forgetting `.text` on the response.
- **Unblockers:** a list comprehension calling
  `client.chat([Message.user(COFFEE)], max_tokens=16, temperature=temperature).text.strip()` n times.
- **Time:** ~7 min.

## L0108_lab problem 3 — Pick a temperature per task

- **Common gotchas:** choosing high temperature for extraction/classification "to be safe" — the
  opposite of what you want.
- **Unblockers:** classify → low; brainstorm → high; JSON extraction → low; tool routing → low.
- **Time:** ~4 min.

## L0108_lab problem 4 — Why temperature 0 still varies

- **Common gotchas:** answering "because temperature 0 is random" — it is the *lowest*-variance
  setting, not a random one.
- **Unblockers:** acceptable causes — floating-point non-determinism, server-side batching,
  tie-breaking between equally-likely tokens.
- **Time:** ~4 min.
- **Key point:** set the expectation now so a flaky eval later doesn't read as a bug.

## L0111_lab problem 1 — Headroom in the window

- **Common gotchas:** adding instead of subtracting; forgetting `reserved` (the reply needs room too).
- **Unblockers:** "everything competes for the same 200k — subtract preamble + history + current +
  reserved from `WINDOW`." A negative result means overflow.
- **Time:** ~5 min.

## L0111_lab problem 2 — Match the failure mode

- **Common gotchas:** confusing silent truncation with quality degradation. Truncation = turns are
  *dropped*; degradation = everything is *present* but attended to poorly.
- **Unblockers:** (a) hard rejection, (b) silent truncation, (c) quality degradation.
- **Time:** ~4 min.

## L0111_lab problem 3 — Cost of a call

- **Common gotchas:** dividing by 1,000 instead of 1,000,000 (rates are per *million* tokens) — a
  1000× error, and a great teachable moment.
- **Unblockers:** "rate is per million tokens, so divide token counts by 1,000,000 first." Then note
  the 50-in/2000-out call costs more — output is the expensive direction (~5×).
- **Time:** ~6 min.
- **Key point:** long prompt + short answer is often cheaper than short prompt + long answer.

## L0111_lab problem 4 — The conversation staircase

- **Common gotchas:** re-counting only the new turn instead of the running total; forgetting the
  *whole* history is re-sent each turn.
- **Unblockers:** "each turn's input is everything so far — add ~200 to a running total before each
  turn." Total across 5 turns = 200+400+600+800+1000 = 3000.
- **Time:** ~6 min.
