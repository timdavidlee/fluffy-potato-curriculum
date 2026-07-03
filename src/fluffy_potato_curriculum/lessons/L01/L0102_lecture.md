# LLM and token basics

```yaml
title: LLM and token basics
keywords: next-word prediction, tokens, tokenizer, sub-word, bpe, model scale, temperature, sampling, preamble, context window, cost, pricing, claude sonnet
estimated duration: 85
```

> **Lesson:** L01. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L01/objectives.md).
> This is the written reference lecture — thorough on purpose, so a student who missed the verbal
> delivery can rebuild the lesson from the page. It follows one connected chain, not a list of
> topics: **an LLM predicts the next token → the pieces are sub-word tokens → tokenization
> fragments real strings → a bigger model and better context sharpen the prediction → temperature
> reshapes it → you reuse a preamble → and now you pay to carry all that overhead every call.**
> The teacher demos in this lesson's
> [demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L01/demos_or_activities.md)
> run in that same order; hands-on practice is in the L01 labs.
> **Anchor model for the live/API parts: Claude Sonnet 4.6 (200k-token context window).**
> **The prediction/scale demos use a local GPT-2 ladder (offline, deterministic) so the raw
> next-token probabilities are visible.**

## section 1. An LLM is a next-word predictor

### slide 1.1 The one loop

- An LLM does exactly one thing: given the text so far, it predicts the **next token**, a sampler
  picks one, that token is appended, and the loop repeats until a stop signal or `max_tokens`.
- "Writing a paragraph" is not a special mode — it is this single loop run a few hundred times.
  Every capability later in the course is built on top of this loop, not on top of some separate
  "reasoning engine."
- diagram: `text so far → model → distribution over next token → sampler picks one → append →
  (loop back to "text so far")`, with a "stop?" branch leaving the loop.

### slide 1.2 The output is a distribution, not an answer

- On each step the model produces a **probability distribution over the next token** — a number for
  every token in its vocabulary. It does not "know" the answer; it *ranks* candidates.
- Example: after `Water is made of hydrogen and`, a small model leads with ` oxygen` (~0.46) but
  hedges across ` helium` (~0.28), ` carbon`, ` nitrogen`, … It *ranks* candidates; it doesn't
  *know* the answer. The word "distribution" is the one to hold onto — section 4 (model scale) and
  section 5 (temperature) are both about *reshaping this exact distribution*.
- diagram: a bar chart over candidate next tokens after `Water is made of hydrogen and` — a tall
  bar (`oxygen`) with a real runner-up (`helium`) and a scatter of short bars — labeled "the model
  ranks; the sampler picks."

### slide 1.3 The consequence that runs the rest of the lesson: no memory

- Each forward pass sees **only the text you send it**. Between calls the model remembers nothing.
- A chat *feels* continuous only because your client re-sends the entire history every call. That
  re-sent text is re-read and (section 8) re-billed every single time.
- This one fact is the thread tying the whole lesson together: it is *why* front-loading context
  works, *why* a reusable preamble is overhead, *why* the context window fills, and *why* a
  conversation's cost climbs. Write it down now.

## section 2. Why the pieces are sub-word tokens

### slide 2.1 The "next piece" is a token, not a word

- The unit the model predicts is a **token** — often a whole common word, often a fragment.
  `running` may be one token; a rare or invented word splits into several (`fli|bber|ti|gib|beting`).
- So "predict the next word" is really "predict the next *token*." Everything downstream — window,
  cost — is counted in tokens, so we have to know what one is.

### slide 2.2 Why sub-word — not whole words, not characters

- **Why not whole words?** An unbounded vocabulary. Every name, typo, hashtag, and new word would
  need its own entry, and you'd still miss tomorrow's words. No fixed list can cover language.
- **Why not single characters?** Sequences get very long and each step carries little signal, which
  is slow and wasteful.
- **Sub-word is the compromise:** a *fixed* vocabulary of common chunks whose pieces **compose** to
  spell anything. Common strings get a short encoding; rare strings are spelled out in more pieces.
  Most modern tokenizers use **BPE** (byte-pair encoding) or a close cousin, *learned* from
  training data — so different vendors' tokenizers split the same string differently.

### slide 2.3 A token is really an integer

- The model never sees characters. It sees **integer IDs** (e.g. `running` → `[16, 5143]`). The
  readable "pieces" we show are a decoding of those IDs for *human* benefit.
- Takeaway to say out loud: the tokenizer is a *chosen* encoding, not a natural fact about language.
  That choice is exactly why the next section's strings fragment the way they do.

## section 3. What tokenization does to real strings

### slide 3.1 Names, novel words, code, and non-Latin fragment

- Because the vocabulary is *learned* from training data, anything **rare** in that data gets
  spelled out in many pieces: proper names, invented words, long numbers, code identifiers, URLs,
  and non-Latin scripts. A name a human reads as one word is often 3–5 tokens.
- These are exactly the inputs agents marinate in (JSON, code, transcripts, names) — which is why
  eyeball estimates fail precisely where it costs you.
- table: rough tokens-per-character behavior by input type.

| Input type            | Example                                  | Tokenizes like…                  |
| --------------------- | ---------------------------------------- | -------------------------------- |
| Plain English         | `The quick brown fox…`                   | dense — close to the ≈4 chars/tok rule |
| Proper names / novel  | `Nnamdi Azikiwe deployed Kubernetes…`    | fragments — each unfamiliar name splits into pieces |
| Code                  | `def f(x): return x ** 2`                | denser — operators/punctuation split off |
| JSON                  | `{"user_id": 12345, "events": [...]}`    | much denser — every brace/quote/colon is a token |
| Non-Latin script      | a short Japanese/Arabic/Hindi phrase     | often 3–5× more tokens per character |

### slide 3.2 The rule of thumb (and why it's only a rule of thumb)

- Rule of thumb for **plain English**: ≈ 4 characters per token, or ≈ ¾ of a word per token.
- It is only a rule of thumb because it was calibrated on ordinary prose. It breaks on the input
  shapes above — often by 3× or more — because those strings were rare in training data and are
  spelled out in pieces.
- diagram: the string `{"user_id": 12345}` shown twice — once split by words (3 chunks) and once by
  tokens (~9 chunks) — showing the gap between the human view and the model's view.

### slide 3.3 Why this is the foundation for everything after

- Every cost number and every window number later in this lesson is **downstream of the token
  count**. Get tokens wrong and every estimate is wrong by the same factor.
- Hold this thought: the reason budgeting (section 8) is unavoidable is that all the context you
  add — names, code, examples, history — turns into *more tokens than you'd guess*, and you re-send
  them every call.

## section 4. A more capable model is a sharper predictor

### slide 4.1 Scale concentrates the probability

- Run the *same* prompt through a small, a medium, and a large model and watch the next-token
  distribution: as the model grows, probability **concentrates** on the sensible continuation and
  the long tail of noise thins out.
- Example (local GPT-2 ladder, `Water is made of hydrogen and`): ` oxygen` carries ~0.46 of the
  mass on the small model (124M), ~0.63 on medium (355M), and ~0.84 on the large one (774M) — the
  top token grows and the tail thins as the model scales. Same loop, sharper prediction.
- diagram: three stacked bar charts (small / medium / large) over the same candidate tokens — the
  top bar grows taller and the tail flattens as size increases.

### slide 4.2 What this is — and is not

- This is a **mechanistic** point: "more capable = sharper distribution." It is one of the two
  levers on prediction quality; the other (the context you provide) is section 6.
- It is **not** a model-selection lesson. *Which* model or provider you'd actually pick for a job —
  a vision model for OCR, a strong reasoner for planning, a small fast model for cheap execution,
  trading capability against cost, latency, and context length — is **L13 (choosing models &
  providers)**. Here we only establish *that* capability sharpens prediction.

## section 5. Temperature: the knob on the distribution

### slide 5.1 Temperature reshapes the distribution before sampling

- Point back to the distribution from sections 1 and 4. **Temperature** reshapes it *before* the
  sampler picks: low temperature **sharpens** it (the top token dominates); high temperature
  **flattens** it (more candidates become competitive).
- It does not change what the model "knows" — only how aggressively the sampler commits to the most
  likely token.
- diagram: the same bar chart at three temperatures — `temp 0` (one tall bar), `temp ≈ 0.7` (a few
  competitive bars), `temp ≈ 1.0+` (many similar-height bars).

### slide 5.2 Temperature 0 is *low* variance, not *zero* variance

- Predict the qualitative effect: temperature 0 → near-identical answers run to run; temperature 1
  → varied, sometimes creative, sometimes off.
- But even at temperature 0, output can differ across runs: floating-point non-determinism,
  server-side batching, and tie-breaking between equally-likely tokens all leak through. Frame it as
  *low* variance from day one, or a future eval that flakes will look like a bug when it's expected.

### slide 5.3 Other sampling controls, and how to choose

- **top-p (nucleus):** sample only from the smallest set of tokens whose probabilities sum to `p`.
  **top-k:** sample only from the `k` most likely tokens. Both *restrict the candidate set*;
  temperature *reshapes the distribution*. Different levers — we won't tune top-p/top-k here, but
  you'll see them in API docs and shouldn't be surprised.
- table: pick a temperature by task type.

| Task                                            | Temperature | Why |
| ----------------------------------------------- | ----------- | --- |
| Classification / extraction / structured output | low (≈0)    | you want the single most-likely, repeatable answer |
| Tool routing (preview of L07)                   | low (≈0)    | a wrong "creative" tool choice is just a bug |
| Brainstorming / creative writing                | higher (≈0.7–1.0) | variety is the point |

## section 6. Front-loading and reusable preambles

### slide 6.1 Front-loading: the lever you control

- Section 4's lever (model scale) is mostly not yours to change call-to-call. The lever that *is*
  yours is the **context you put in front**. Because the model conditions its next-token
  distribution on everything before, putting the relevant instructions, definitions, and examples
  **early** steers the whole continuation.
- Same model, same task, two prompts — a bare `Summarize this.` versus a front-loaded version with a
  role, an audience, a format, and one worked example — produce visibly different quality. The
  front-loaded context did the work.

### slide 6.2 Reusable preambles — and the sting in the tail

- Once front-loading helps, the natural move is to **reuse** the same block of instruction / persona
  / reference context across many calls. That block is a **preamble** — an informal precursor to the
  system message L02 will formalize.
- The sting: because there is **no server-side memory** (section 1), that preamble is **re-sent on
  every single call** — re-read, re-counted against the window, and re-billed each time. The very
  thing that made the output good is now **overhead you carry on every call**.
- This is the hinge into budgeting: you have just built up overhead on purpose. Section 8 is the
  bill.

## section 7. Budgeting, part one — the context window (space)

### slide 7.1 One shared budget

- The context window is a hard ceiling on how many tokens a single call can involve — **input and
  output combined**.
- Everything competes for that one budget: the **preamble / system message**, every prior
  conversation turn, tool definitions (relevant from L07 on), the current input, *and* the model's
  own response.
- Anchor number: **Claude Sonnet 4.6 has a 200,000-token standard window.** (A 1M-token
  long-context variant also exists; we use 200k as the course default.)

### slide 7.2 The window meter and reserving room for the answer

- diagram: a horizontal bar sized to 200k tokens, segmented and labeled `preamble | conversation
  history | current input | (reserved for output)`. As history and preambles grow, the free space
  shrinks.
- Reserve room for the answer: fill 199k of a 200k window with input and there is no room to
  respond. `max_tokens` is your reservation for the output segment.

### slide 7.3 Three failure modes when you run out

- table: the three ways "out of window" shows up, and which is most dangerous.

| Failure mode          | What happens                                              | Danger level |
| --------------------- | -------------------------------------------------------- | ------------ |
| Hard rejection        | The API refuses the request before running it            | Loud — easy to notice and fix |
| Silent truncation     | Some clients/frameworks quietly drop the oldest turns    | **Quiet — the call succeeds but the model "forgot"** |
| Quality degradation   | Even when it fits, models can lose track of material buried mid-context | Subtle — answers get vaguer, no error |

- The dangerous one is **silent truncation**: no error, but the model no longer has information you
  assumed it had. It also motivates later lessons — context management (L19) and RAG (L21) exist to
  *push back* on window pressure rather than just buying a bigger window.

## section 8. Budgeting, part two — cost (money)

### slide 8.1 You pay per token, both directions, every call

- Billing is per token, with **separate input and output rates**, on **every** call. No free
  server-side memory: the re-sent preamble and history are re-billed each turn.
- diagram: a single call annotated `input_tokens × input_rate + output_tokens × output_rate =
  call cost`.

### slide 8.2 The input/output asymmetry

- Output tokens typically cost **3–5× more** than input tokens.
- Consequence that flips intuition: a **long prompt + short answer** is often *cheaper* than a
  **short prompt + long answer**. Paying to read is cheaper than paying to write.
- diagram: two bars — "2k-in / 50-out" vs. "50-in / 2k-out" — the second taller, labeled "output is
  the expensive direction."

### slide 8.3 The conversation-history staircase (with the preamble riding along)

- Because the client re-sends the whole history **plus the preamble** each turn, input tokens climb
  every turn even when each new message is small.
- table: cumulative input across a 5-turn chat, ~200 tokens/turn — the staircase that catches people
  out.

| Turn | New tokens this turn | Cumulative input re-sent | Note |
| ---- | -------------------- | ------------------------ | ---- |
| 1    | ~200                 | ~200                     | baseline (preamble + first message) |
| 2    | ~200                 | ~400                     | turn 1 re-sent |
| 3    | ~200                 | ~600                     | turns 1–2 re-sent |
| 4    | ~200                 | ~800                     | turns 1–3 re-sent |
| 5    | ~200                 | ~1000                    | the bill grows even though each message is small |

- This staircase is exactly what **prompt caching** and context management (L19) and retrieval (L21)
  exist to fight. We only name it here.

### slide 8.4 Order-of-magnitude: from "free" to "a real budget"

- One call costs ~nothing. The number that matters is what happens when you *multiply*:
  one call → a 10-step agent run (L10) → 100 dev iterations → a small production deployment.
- diagram: a ladder — `1 call ≈ $0.000X` → `×10 (agent run)` → `×100 (dev iteration)` →
  `×1000 (small deployment)` — the final rung landing on a number students can *feel*.
- ⚠️ **Pricing note:** per-token rates change. Always pull current Claude Sonnet pricing from
  Anthropic's pricing page on the day you teach or estimate; never trust a hard-coded number.

## section 9. Wrap-up and the bridge to L02

### slide 9.1 The whole chain in one breath

- An LLM predicts the next **token**; the pieces are **sub-word**, so real strings fragment; a more
  capable **model** and better **front-loaded context** sharpen the prediction; **temperature**
  reshapes it; you **reuse a preamble** to keep quality high; and because there's **no memory**, you
  re-send and **re-pay** that preamble plus history on every call — against both the **window** and
  the **bill**.
- The one sentence to leave with: *everything you front-load to make the model predict better is
  overhead you re-send, re-count, and re-pay on every call — so every prompt is a budget decision in
  tokens, dollars, and window space at once.*

### slide 9.2 What L02 does with this

- L02 (prompting fundamentals) turns the informal **preamble** into explicit system/user/assistant
  **roles** — and every one of those turns is billed against the window L01 just taught.
- **Structured output** is partly a don't-pay-for-tokens-you-don't-need move; **few-shot examples**
  are front-loading made deliberate — a context-window-vs-quality trade-off. Students who felt L01's
  "input tokens cost money and eat the window" treat few-shot as expensive-but-sometimes-worth-it,
  which is the right intuition.
- See the bridge in this lesson's roadmap:
  [objectives.md § Bridge to L02](../../../../docs/origin/lesson_roadmaps/L01/objectives.md).
