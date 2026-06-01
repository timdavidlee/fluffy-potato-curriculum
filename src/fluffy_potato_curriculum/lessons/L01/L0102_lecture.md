# LLM and token basics

```yaml
title: LLM and token basics
keywords: tokens, tokenizer, bpe, context window, temperature, sampling, top-p, top-k, cost, pricing, claude sonnet
estimated duration: 70
```

> **Lesson:** L01. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L01/objectives.md).
> This is the written reference lecture — thorough on purpose, so a student who missed the verbal
> delivery can rebuild the lesson from the page. The live demos are in
> [L0103_lecture.ipynb](L0103_lecture.ipynb); hands-on practice is in the L01 labs.
> **Anchor model throughout: Claude Sonnet 4.6 (200k-token context window).**

## section 1. The four primitives, as a system

### slide 1.1 What this lesson installs

- L01 gives you four primitives you will use in every later lesson: **tokens**, **context window**,
  **temperature/sampling**, and **cost**.
- They are *one system*, not four separate facts. Tokens are the unit; the context window is a
  budget measured in tokens; cost is dollars-per-token; temperature changes how many output tokens
  you tend to generate. Change one and the others move.
- diagram: a square with four labeled corners — Tokens, Context window, Temperature, Cost — and
  arrows showing Tokens → Context window → Cost, with Temperature feeding into output-token count
  which feeds Cost. The point of the picture: they form a loop, not a list.

### slide 1.2 The mechanical picture of an API call

- An LLM call is an ordinary network request: you send messages + settings, you get back text +
  a token accounting.
- The model reads *all* the text you send, every time, as a sequence of tokens. It then generates
  a reply one token at a time until it stops or hits `max_tokens`.
- diagram: `your code → HTTP request (messages + max_tokens + temperature) → model → HTTP response
  (reply text + input_tokens/output_tokens)`, with the response arrow looping back to your code.

### slide 1.3 Two facts that surprise everyone

- **The model has no memory.** A chat only *feels* continuous because your client re-sends the
  whole history on every call. That history is re-read and re-billed each time.
- **A token is not a word.** It is whatever the tokenizer says, learned from training data.
- These two facts are the root of most cost surprises and most "why did it forget?" confusion.
  We make both concrete in the demos.

## section 2. Tokens

### slide 2.1 What a token actually is

- The model never sees characters. It sees integers — token IDs. The "words" you read are a
  decoding of those IDs for *human* benefit.
- Tokenizers are **learned, not designed**: they carve text into common chunks found in training
  data. Common English words are often one token; rare strings, punctuation, and code fragments
  split into many.
- Most modern tokenizers use **BPE** (byte-pair encoding) or a close cousin. Different vendors
  train different tokenizers, so the *same string* can be a different number of tokens for Claude
  vs. an OpenAI model.

### slide 2.2 The rule of thumb (and why it's only a rule of thumb)

- Rule of thumb for **plain English**: ≈ 4 characters per token, or ≈ ¾ of a word per token.
- It is only a rule of thumb because it was calibrated on ordinary prose. It breaks on the input
  shapes agents actually handle: code, JSON, URLs, transcripts, non-Latin scripts.
- table: rough tokens-per-character behavior by input type — shows why one rule can't cover all.

| Input type            | Example                                  | Tokenizes like…                  |
| --------------------- | ---------------------------------------- | -------------------------------- |
| Plain English         | `The quick brown fox…`                   | dense — close to the ≈4 chars/tok rule |
| Code                  | `def f(x): return x ** 2`                | denser — operators/punctuation split off |
| JSON                  | `{"user_id": 12345, "events": [...]}`    | much denser — every brace/quote/colon is a token |
| Non-Latin script      | a short Japanese/Arabic/Hindi phrase     | often 3–5× more tokens per character |

### slide 2.3 Why this is the foundation

- Every cost number and every context-window number in this lesson is *downstream* of the token
  count. Get tokens wrong and every estimate is wrong by the same factor.
- The classic failure: assuming "1 token = 1 word." A 200-character SQL query can be 100+ tokens
  while a 200-character English sentence is ~50. For agents — which marinate in JSON and code —
  the word-based intuition is wrong most of the time.
- diagram: the string `{"user_id": 12345}` shown twice — once split by words (3 chunks) and once
  split by tokens (~9 chunks) — to show the gap between the human view and the model's view.

### slide 2.4 Seeing it: tokenizers in code

- We use two tools in the demo and labs: Claude's own token count (from the API) for the canonical
  number, and `tiktoken` (OpenAI's tokenizer) to *visualize boundaries*, because Claude's API
  returns a count but not the individual pieces.
- Takeaway to state out loud: "tokenizers are a *family* of choices. Use the right model's
  tokenizer for real cost/window math; use any of them to build intuition about boundaries."

## section 3. The context window

### slide 3.1 One shared budget

- The context window is a hard ceiling on how many tokens a single call can involve — **input and
  output combined**.
- Everything competes for that one budget: the system message, every prior conversation turn,
  tool definitions (relevant from L04 on), the current user input, *and* the model's own response.
- Anchor number: **Claude Sonnet 4.6 has a 200,000-token standard window.** (A 1M-token
  long-context variant also exists; we use 200k as the default for this course.)

### slide 3.2 The window meter

- diagram: a horizontal bar sized to 200k tokens, segmented and labeled: `system | conversation
  history | current input | (reserved for output)`. As history grows, the history segment expands
  and the free space shrinks.
- Reserve room for the answer: if you fill 199k of a 200k window with input, there is no room left
  for the model to respond. `max_tokens` is your reservation for the output segment.

### slide 3.3 Three failure modes when you run out

- table: the three ways "out of window" shows up, and which is most dangerous.

| Failure mode          | What happens                                              | Danger level |
| --------------------- | -------------------------------------------------------- | ------------ |
| Hard rejection        | The API refuses the request before running it            | Loud — easy to notice and fix |
| Silent truncation     | Some clients/frameworks quietly drop the oldest turns    | **Quiet — the call succeeds but the model "forgot"** |
| Quality degradation   | Even when it fits, models can lose track of material buried mid-context | Subtle — answers get vaguer, no error |

- The dangerous one is **silent truncation**: no error, but the model no longer has information you
  assumed it had. Name it now so it isn't a mystery later.

### slide 3.4 Why bigger isn't automatically better

- More tokens cost more and slow inference down; quality can sag near the long-context tail.
- "Use the whole window because it's there" is an anti-pattern. This tension drives later lessons:
  context management (L15) and RAG (L17) exist to *push back* against window pressure rather than
  just buying a bigger window.

## section 4. Temperature and sampling

### slide 4.1 What the model does on one step

- On each step the model produces a **probability distribution** over the entire vocabulary — a
  number for every possible next token. A **sampler** then picks one token from that distribution.
- This is the right altitude for us: not transformer internals, but "distribution in, one token
  out." Almost everything about reproducibility and creativity follows from this one picture.
- diagram: a bar chart over a handful of candidate next tokens (`coffee`, `rain`, `Seattle`, …)
  with different heights; an arrow labeled "sampler picks one" pointing to the chosen bar.

### slide 4.2 Temperature: a knob, not a switch

- Temperature reshapes the distribution *before* the sampler picks. Low temperature **sharpens**
  it (the top token dominates); high temperature **flattens** it (more candidates become likely).
- diagram: the same bar chart at three temperatures — `temp 0` (one tall bar), `temp ≈ 0.7`
  (a few competitive bars), `temp ≈ 1.0+` (many similar-height bars).
- Predict the qualitative effect: temperature 0 → near-identical answers run to run; temperature 1
  → varied, sometimes creative, sometimes off.

### slide 4.3 Temperature 0 is *low* variance, not *zero* variance

- Even at temperature 0, output can differ across runs: floating-point non-determinism,
  server-side batching, and tie-breaking between equally-likely tokens all leak through.
- Why it matters: if you promise yourself "temperature 0 = deterministic," a future eval that
  flakes will look like a bug when it is expected behavior. Frame it as low variance from day one.

### slide 4.4 Other sampling controls, and how to choose

- **top-p (nucleus):** sample only from the smallest set of tokens whose probabilities sum to `p`.
  **top-k:** sample only from the `k` most likely tokens. Both *restrict the candidate set*;
  temperature *reshapes the distribution*. They are different levers; we won't tune top-p/top-k in
  this course, but you'll see them in API docs and should not be surprised.
- table: pick a temperature by task type.

| Task                                         | Temperature | Why |
| -------------------------------------------- | ----------- | --- |
| Classification / extraction / structured output | low (≈0) | you want the single most-likely, repeatable answer |
| Tool routing (preview of L04)                | low (≈0)    | a wrong "creative" tool choice is just a bug |
| Brainstorming / creative writing             | higher (≈0.7–1.0) | variety is the point |

## section 5. Cost

### slide 5.1 You pay per token, both directions, every call

- Billing is per token, with **separate input and output rates**, on **every** call. There is no
  free server-side memory: re-sent history is re-billed.
- diagram: a single call annotated `input_tokens × input_rate  +  output_tokens × output_rate =
  call cost`.

### slide 5.2 The input/output asymmetry

- Output tokens typically cost **3–5× more** than input tokens.
- Design consequence that flips most students' intuition: a **long prompt + short answer** is often
  *cheaper* than a **short prompt + long answer**. Paying to read is cheaper than paying to write.
- diagram: two bars — "2k-token input, 50-token output" vs. "50-token input, 2k-token output" —
  with the second bar taller, labeled "output is the expensive direction."

### slide 5.3 The conversation-history staircase

- Because the client re-sends the whole history each turn, input tokens climb every turn even if
  each new message is small.
- table: cumulative input tokens across a 5-turn chat where each turn adds ~200 tokens — the
  staircase that catches people by surprise.

| Turn | New tokens this turn | Cumulative input re-sent | Note |
| ---- | -------------------- | ------------------------ | ---- |
| 1    | ~200                 | ~200                     | baseline |
| 2    | ~200                 | ~400                     | turn 1 re-sent |
| 3    | ~200                 | ~600                     | turns 1–2 re-sent |
| 4    | ~200                 | ~800                     | turns 1–3 re-sent |
| 5    | ~200                 | ~1000                    | the bill grows even though each message is small |

- This staircase is exactly what **prompt caching** (a later topic, L15 context management) and
  retrieval (L17) exist to fight. We only name it here.

### slide 5.4 Order-of-magnitude: from "free" to "a real budget"

- One call costs ~nothing. The number that matters is what happens when you *multiply*:
  one call → a 10-step agent run (L07) → 100 dev iterations → a small production deployment.
- diagram: a ladder — `1 call ≈ $0.000X` → `×10 (agent run)` → `×100 (dev iteration)` →
  `×1000 (small deployment)` — with the final rung landing on a number students can *feel*.
- The habit to build: do this back-of-envelope multiplication *before* you start running agents,
  not after the bill arrives.
- ⚠️ **Pricing note:** per-token rates change. Always pull current Claude Sonnet pricing from
  Anthropic's pricing page on the day you teach or estimate; do not trust a hard-coded number in a
  slide or a notebook.

## section 6. Wrap-up and the bridge to L02

### slide 6.1 The four primitives, reconnected

- Tokens are the unit. The context window is a token budget. Cost is dollars per token. Temperature
  changes how many output tokens you generate. Pull one thread and the others move.
- The one sentence to leave with: *every prompt you write is a budget decision — token count,
  dollar count, and context-window count, all at once.*

### slide 6.2 What L02 does with this

- L02 (prompting fundamentals) moves from "a prompt is N tokens you pay for" to "a prompt has
  *structure*, and the structure changes the answer."
- The L01 primitives carry directly: system/user/assistant **roles** are how re-sent history is
  structured (and billed); **structured output** is partly a don't-pay-for-tokens-you-don't-need
  move; **few-shot examples** are a deliberate context-window-vs-quality trade-off.
- See the bridge in this lesson's roadmap:
  [objectives.md § Bridge to L02](../../../../docs/origin/lesson_roadmaps/L01/objectives.md).
