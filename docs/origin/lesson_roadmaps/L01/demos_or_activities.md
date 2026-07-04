# L01: Teacher-led demos — LLM and token basics

> Sibling docs: [objectives.md](objectives.md) (what the lesson aims for), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md).
>
> **Audience for this file:** the teacher running L01. Every demo below is *teacher-driven, no student participation*. Student-driven exercises live in the L01 labs (separate file).

## How to read this file

Each demo is a self-contained block with:

- **Goal** — the single insight the demo should land. Tied to a learning objective from [objectives.md](objectives.md).
- **Pre-flight** — what the teacher needs loaded before class.
- **Live script** — the order of operations during the demo. Treat it as a checklist, not a teleprompter.
- **What to highlight** — the moment(s) where the teacher should slow down and call out the takeaway out loud.
- **If the demo misbehaves** — graceful fallback for when the model surprises you (because it will).

**The demos form one continuous chain, not four independent set-pieces.** Run them in order — each demo hands the next its premise. The chain is:

> next-word prediction (Demo 1) → the pieces are sub-word *tokens* (Demo 2) → what tokenization does to real strings (Demo 3) → scale sharpens the prediction (Demo 3.5) → temperature reshapes the same distribution (Demo 3.6) → front-loading + reusable preambles (Demo 4) → you re-send and re-pay that overhead every call: window + cost (Demo 5).

The budgeting demo (Demo 5) only lands cleanly once Demos 1–4 have made the student *feel* how much overhead accumulates. That is the whole point of the reordering: budgeting is the bill, not a new topic.

L01 is the very first lesson of the course. Students arrive cold. Spend a few minutes before Demo 1 on the "what is an API call, mechanically" framing — a 60-second whiteboard sketch of "your code → HTTP → model → response" pays for itself across every demo.

## Pre-flight (once, at the top of the lesson)

The teacher should have, before the first demo starts:

- A working notebook with the project's `uv` env. Both async and sync clients are fine; the demos use sync calls for clarity.
- An API key with a small spend cap (Demo 5 runs real calls; a $5 cap is more than enough for a class delivery).
- **The local model ladder for Demo 3.5** loaded and cached ahead of time: `gpt2` (124M), `gpt2-medium` (355M), `gpt2-large` (774M) via HuggingFace `transformers`. First load downloads weights — do it before class, not live. These run on CPU; no GPU or API key needed.
- A small wrapper that prints, after every *API* call: `input_tokens`, `output_tokens`, wall-clock time, and running per-call cost. This wrapper is the through-line for Demo 5 especially. <!-- *NEED INPUT*: standardize this wrapper in the L01 lab package so teacher and students share it — name/location TBD. -->
- A tokenizer available locally: `tiktoken` (offline, deterministic) for the counts on screen, with Anthropic's count-tokens endpoint shown once for the anchor model's own numbers.
- A way to project token IDs alongside the source string — a "decode each token separately and join with `|`" output is enough. Demos 2 and 3 hinge on the student *seeing* the boundaries.
- All demo prompts/inputs pre-loaded as variables or cells so each demo is a single keystroke to run. Live-typing during demos eats time and breaks the contrast the lesson depends on.

> Why pre-loaded: L01 lives or dies on contrast — same string / different tokenizer; same prompt / different model; same distribution / different temperature; same call / different cost as history grows. A mistype mid-demo breaks the contrast and the lesson lands as "the API is unpredictable" instead of "this primitive caused this change."

## Demo 1 — An LLM is a next-word predictor (Objective 1)

**Goal:** install the one mental model the whole lesson hangs off — the model reads the text so far, produces a distribution over the next token, samples one, appends it, and repeats.

**Pre-flight:**

- The `gpt2` (small) model from the Demo 3.5 ladder, loaded locally. GPT-2 is perfect here because you can read its raw next-token probabilities directly — no API, no key, fully offline and deterministic.
- One seed string with an obvious continuation: `"Water is made of hydrogen and"`. (Empirically validated on the local ladder — see Demo 3.5. Avoid `"The capital of France is"`: GPT-2's factual recall on it is weak and non-monotonic across the ladder, which breaks the contrast.)

**Live script:**

1. Show the seed string. Ask the room (rhetorically): "what's the next word?" Everyone thinks *oxygen*.
2. Run one forward pass of `gpt2` and print the top-10 next-token probabilities. ` oxygen` leads (~0.46) but the model **hedges** — ` helium` (~0.28), ` carbon`, ` nitrogen` all carry real mass. **The model didn't 'know' oxygen; it ranked it.**
3. Sample one token, append it, and run again. Do this 5–6 times so the room watches a sentence *assemble* one token at a time. Narrate: "this loop is the entire show — everything else today is a consequence of it."
4. State the load-bearing consequence out loud: **each forward pass sees only the text you give it. Between calls there is no memory.** Write it on the board; you will point back to it in Demos 4 and 5.

**What to highlight:**

- "Generation" is not retrieval and not reasoning-from-a-store — it is this loop run hundreds of times.
- The output is a *distribution*, not an answer. That word — distribution — is what Demo 3.6 (temperature) reshapes.
- No memory between calls. This is the single most consequential fact in the lesson; everything about preambles, windows, and cost follows from it.

**If the demo misbehaves:**

- If GPT-2's top token is something odd (it is a small, old model), lean in: "this is a *weak* predictor — hold that thought, Demo 3.5 is about exactly this." The weakness sets up the scale demo.

## Demo 2 — The pieces are sub-word tokens, not words (Objective 2, part 1: *why* sub-word)

**Goal:** show that the "next piece" the model predicts is a *token*, and motivate *why* the unit is sub-word rather than words or characters.

**Pre-flight:**

- `tiktoken` loaded. Three contrast strings: a common word (`"running"`), a rare/spelled-out one (`"antidisestablishmentarianism"`), and an invented one (`"flibbertigibbeting"`).

**Live script:**

1. Recall Demo 1: the model predicts the next *piece*. What is a piece? Tokenize `"running"` → often a single token. Tokenize the long and invented words → several sub-word pieces (`fli|bber|ti|gib|beting`-style).
2. Pose the design question out loud: *why not just use whole words?* Answer on the board: an unbounded vocabulary — every name, typo, and new word would need its own entry, and you'd still miss tomorrow's words. *Why not characters?* Sequences get long and each step carries little signal. **Sub-word is the compromise: a fixed vocabulary whose pieces compose to spell anything.**
3. Show that a piece is really just an integer ID (`[16, 5143]`), and the decoded boundaries are a visualization for humans — the model sees integers.

**What to highlight:**

- The unit is chosen, not natural: it trades a fixed vocabulary against the ability to spell any string.
- Common strings get short encodings; rare strings pay in pieces. That asymmetry *is* the setup for Demo 3.

**If the demo misbehaves:**

- If a chosen word tokenizes more tamely than expected across tokenizers, swap in a longer invented word — the fragmentation is the point.

## Demo 3 — What tokenization does to names, code, and non-English (Objective 2, part 2)

**Goal:** show that the strings agents actually consume — proper names, code, JSON, non-Latin scripts — fragment in ways that defeat eyeball estimates. This is where token counts stop being intuitive, which is what makes budgeting (Demo 5) bite.

**Pre-flight:**

Four short strings that break intuition in different directions:

1. **Proper names / novel words:** `"Nnamdi Azikiwe deployed Kubernetes to Reykjavík"` — real names, a product name, and a non-English place name all fragment.
2. **Code:** `"def f(x): return x ** 2"` — operators and punctuation get their own tokens.
3. **JSON:** `'{"user_id": 12345, "events": ["click", "scroll"]}'` — every brace, quote, colon, comma is a token; numbers tokenize unpredictably.
4. **Non-Latin script:** a short phrase in Japanese, Arabic, or Hindi. Tokens-per-character explodes for most non-Latin scripts in BPE tokenizers.

Show `tiktoken` counts on screen; run Anthropic's count-tokens endpoint on **Claude Sonnet 4.6** once so students see the anchor model's own numbers differ.

**Live script:**

1. Put all four strings on screen. Ask (rhetorically): "which is longest in tokens?" Let the room commit to a guess.
2. Tokenize each; show integer IDs *and* decoded boundaries side-by-side (`Nn|am|di| Az|iki|we|...`). The proper-name fragmentation is visceral — a name a human reads as one word is 3–5 tokens.
3. Show the counts in a small table. Highlight: names/rare words fragment, code is dense, JSON is *much* denser than expected, non-Latin is 3–5× English per character.
4. Apply the ≈4-chars-per-token rule to the English baseline, then point at the JSON and non-Latin examples: "this rule is wrong by 3× here."

**What to highlight:**

- Tokenizers are *learned*, not designed — they fragment whatever was rare in training data. That is *why* the rule of thumb is only a rule of thumb.
- Every cost and window number later in the lesson rides on this. A "1 token = 1 word" mental model makes every budget estimate wrong by 2–10× on the inputs agents consume.

**If the demo misbehaves:**

- If counts come out tame, pull up a longer JSON event payload — the count climbs visibly. Contrast is the point.
- If the count-tokens endpoint is slow, fall back to a pre-recorded screenshot; the lesson needs the *contrast* visible, not the call live.

## Demo 3.5 — A bigger model is a sharper predictor (Objective 3, model-scale beat)

**Goal:** show, mechanistically, that a more capable model concentrates more probability on the sensible next token — *not* how to choose a model (that is L14).

**Pre-flight:**

- The local ladder loaded: `gpt2` (124M) → `gpt2-medium` (355M) → `gpt2-large` (774M). Same seed string from Demo 1 (`"Water is made of hydrogen and"`), plus one harder seed where the small model visibly flounders: `"The Eiffel Tower is located in the city of"` (small model spreads across cities; the larger models commit to Paris).

**Live script:**

1. Reuse Demo 1's seed. Run all three models on the *same* string and print each one's top-5 next-token probabilities side by side.
2. Read the trend aloud: as the model grows, probability mass **concentrates** on the right continuation (` oxygen` climbs ~0.46 → ~0.63 → ~0.84 across 124M → 355M → 774M) and the long tail of noise thins out. (These numbers are validated on the current `transformers`/`gpt2*` weights; re-run once before class in case weights update.)
3. Run the harder seed. The small model spreads its bets or picks something wrong; the large model commits correctly. Same loop, better predictor.
4. Draw the boundary explicitly: "more capable = sharper distribution. *Which* model or provider you'd actually pick for a given capability — a vision model for OCR, a strong reasoner for planning, a cheap fast model for execution, trading capability against cost and latency — is a real decision we make in **L14**. Today we're only establishing *that* a more capable model sharpens prediction."

**What to highlight:**

- Model quality is not vague "smartness" — it is where the probability mass goes.
- This is one of two levers on prediction quality. The other — the context *you* provide — is Demo 4, and it is the lever the student actually controls.

**If the demo misbehaves:**

- The ladder is deterministic offline, so it should be stable. If a seed doesn't separate the models cleanly, switch to the prepared harder seed. Keep a screenshot of a clean run as backup.

## Demo 3.6 — Temperature reshapes the same distribution (Objective 5; PRD subgoal: temperature and sampling)

**Goal:** show that temperature is a knob on the distribution *before* sampling — and that temperature 0 reduces variance without eliminating it.

**Pre-flight:**

- Reuse the *same* GPT-2 next-token distribution from Demo 3.5 — the payoff of the ordering is that "distribution" is already on screen, so temperature has something concrete to act on. Compute the softmax at temperature 0.5, 1.0, and 2.0 and show the bars sharpen/flatten.
- Then an API prompt with several plausible answers for the live half: *"Suggest a name for a coffee shop on a rainy street in Seattle. Just the name — one or two words."* Anchor model **Claude Sonnet 4.6**; dry-run both temperatures before class.

**Live script:**

1. Start on the GPT-2 distribution from Demo 3.5. Reshape it live: temperature < 1 sharpens toward the top token; temperature > 1 flattens toward uniform. *This is the conceptual core — the slide (distribution) comes before the API call.*
2. Switch to the anchor model. Run the coffee-shop prompt 5× at `temperature=0` — outputs likely identical.
3. Run 5× at `temperature=1` — outputs likely all different.
4. Run `temperature=0` 10 more times, hunting for one that differs. If you find it, that's the punchline: **temperature 0 is *low* variance, not *zero* variance.**
5. Name `top_p` and `top_k` in one sentence each: "we won't tune these here, but you'll see them in the docs — don't be surprised."

**What to highlight:**

- Temperature acts on the distribution before sampling; it doesn't change what the model "knows," only how aggressively the sampler commits to the top token.
- Temperature 0 → classification, extraction, structured output, tool-routing (foreshadow L07). Temperature ~1 → brainstorming, creative, deliberate exploration.
- Reproducibility is a *separate* problem from temperature — floating-point, batching, and tie-breaking cause variance even at 0. Set the expectation now so future evals don't shock anyone.

**If the demo misbehaves:**

- If temperature 0 is visibly identical across all 15 runs, say so and point at the sharpened distribution: "that's what a sharp distribution looks like — the next prompt might surprise us." Don't fake a variance result.
- If temperature 1 gives only one or two distinct answers, swap to a more open-ended backup prompt.

## Demo 4 — Front-loading and reusable preambles (Objective 3 front-loading + Objective 4)

**Goal:** show that *what you put in front* steers the whole continuation, and that the natural move — reusing a preamble across calls — quietly accumulates overhead.

**Pre-flight:**

- Anchor model **Claude Sonnet 4.6**. Two versions of the same task:
  1. **Bare:** `"Summarize this."` + a short passage.
  2. **Front-loaded:** a preamble — role, audience, format constraints, one worked example — then the *same* passage and instruction.
- A reusable `PREAMBLE` string you'll send on multiple calls, with the wrapper printing input tokens each time.

**Live script:**

1. Run the bare version; show a generic result. Run the front-loaded version; show a sharper, on-format result. Same model, same passage — the *front-loaded context* did the work. Tie back to Demo 3.5: model scale is one lever, provided context is the other, and this one is yours.
2. Now reuse that `PREAMBLE` across three different passages. Point at the wrapper: **every call re-sends the preamble's ~N input tokens.** The preamble that made the output good is overhead on every call.
3. Foreshadow explicitly: "this reusable block is an informal *system prompt* — L02 makes it a formal role. But notice what we've built: overhead we now carry every single time." Hand directly to Demo 5.

**What to highlight:**

- Front-loading is the controllable lever on prediction quality (contrast with model scale in 3.5).
- No memory (Demo 1) means the preamble isn't stored server-side — it rides along on every request, counted and billed each time.
- This is the emotional setup for budgeting: the student has just seen *why* they'd add overhead. Demo 5 shows the bill.

**If the demo misbehaves:**

- If the bare vs. front-loaded difference is subtle, use a task with a strict format (JSON with specific keys, or a fixed 3-bullet shape) where the preamble's effect is unmistakable.

## Demo 5 — Carrying the overhead: context window and cost (Objectives 6 & 7; PRD subgoals: context windows, cost)

**Goal:** land the payoff — because you re-send the preamble plus the whole history every call (no memory), those tokens hit two budgets at once: **space** (the 200k window) and **money** (per-token, both directions). This is where "tokens" becomes "budgeting," and by now it should feel inevitable.

**Pre-flight:**

- A **window meter** visual: a horizontal bar for the 200k window, segmented for system/preamble, conversation history, current input, and reserved output.
- Prepared inputs: (1) a tiny call; (2) the same call with the Demo 4 preamble + 20 prior turns prepended, so the bar visibly fills; (3) an overflow call with a ~250k-token blob prepended, which the API rejects. Have the raw SDK error ready to read — don't prettify it.
- Latest **Claude Sonnet 4.6** per-token pricing (input and output rates as separate numbers), pulled the day of delivery. The wrapper with per-call cost wired in, showing running session cost.
- A 5-turn conversation script (~200 tokens/turn) instrumented to print *cumulative input tokens* per turn (the staircase: 200 → 400 → 600 → 800 → 1000), each turn *also* carrying the preamble from Demo 4.

**Live script:**

*Space (window):*

1. Tiny call — bar barely moves.
2. Preamble + history call — bar visibly fills; the "history" and "preamble" segments dominate. Note input cost climbing (previews the money half).
3. Overflow call — let the API reject it; read the raw error; point at the token count vs. the 200k limit.
4. Walk the three failure modes without re-running: **hard rejection** (just seen), **silent truncation** (some frameworks quietly drop oldest turns — a footgun), **quality degradation** near the long-context tail (foreshadow L19/L21).

*Money (cost):*

5. Single call — show `input_tokens`, `output_tokens`, `cost`. Read the tiny number aloud.
6. Long input / short output, then short input / long output — show output tokens cost *more* (~3–5×), flipping intuition.
7. Run the multi-turn script. Print cumulative input per turn — the staircase — with the preamble riding along every turn. Compute total session cost.
8. Order-of-magnitude ladder: per-turn cost ×10 (agent run, foreshadow L10) ×100 (dev iteration) ×1000 (small deployment). Read the final number aloud — the punchline.
9. Tie the bow: "every token you front-loaded to predict better, you just paid for on every call, in both budgets. *That* is why every prompt is a budget decision." <!-- *NEED INPUT*: one-line prompt-caching foreshadow here, or defer strictly to L19? -->

**What to highlight:**

- The window is shared: system/preamble, every prior turn, tool definitions (L07+), and output all compete for one 200k budget.
- The "model remembers" illusion is the client re-sending history *and preamble* — now the student has watched the cost of that illusion accumulate across the whole lesson.
- Output tokens cost more than input; long prompt + short answer often beats the reverse.
- The order-of-magnitude jump from "one call ≈ nothing" to "a dev iteration loop costs real money" is when cost becomes a design concern, not an accounting one.

**If the demo misbehaves:**

- If the API doesn't reject the overflow (window/vendor behavior changes), fall back to the pre-flight count-tokens endpoint and *show* the count exceeding 200k. The point is "there is a hard ceiling," not "the call must fail today."
- If rate-limited mid-script, walk the pre-printed numbers — the math is the demo, not the live call.
- If pricing changed since the slide, *say so out loud* and update live. An unflagged pricing mismatch undermines every cost claim in the course.

## Optional bridge demo — toward prompting fundamentals (L02)

If time allows, take Demo 4's reusable preamble and Demo 5's multi-turn script and show how the same call looks with explicit system/user/assistant role separation. Don't *teach* role design — just point at the structure: "L02 makes this preamble a formal contract and shows why instructions in the system vs. user message change results." It seeds the role concept while the preamble-and-cost intuition is still warm.

<!-- *NEED INPUT*: include this bridge demo, or save it as the opener for L02? -->

## Pacing notes for the teacher

- **Per-demo time:** 8–12 minutes including discussion. Seven demos (1, 2, 3, 3.5, 3.6, 4, 5) plus the optional bridge run ~75–90 minutes. <!-- RESOLVED: L01 stays a single ~75–90 min lecture item (a "mega" lesson), not split into two blocks. -->
- **The chain is the lesson.** If you're short on time, compress *within* demos, but don't drop one — each hands the next its premise. Dropping Demo 4 (preambles) in particular breaks the "why budgeting" payoff.
- **Variance budget:** API outputs vary run-to-run (Demo 3.6 makes this explicit). Budget one re-run per API demo. The GPT-2 demos (1, 3.5, 3.6-first-half) are deterministic offline — they won't surprise you.
- **Resist tangents.** "What about embeddings / prompt caching / multimodal tokens?" → name each as a "we'll get there" callback (embeddings → L20, caching → L19, multimodal → out of scope) and don't detour.
- **Audience watches, doesn't participate.** Hands-on tokenization, temperature sweeps, and cost estimation are for the labs.

## Open authoring questions

- <!-- *NEED INPUT*: confirm the local GPT-2 ladder (transformers+torch) is acceptable as a lesson dependency for Demos 1/3.5/3.6, versus an API-tier quality comparison that needs no new deps but can't show the raw distribution. Mirrored from [objectives.md](objectives.md). -->
- <!-- *NEED INPUT*: is prompt caching introduced here (a one-line foreshadow in Demo 5), or strictly deferred to L19? Mirrored from [objectives.md](objectives.md). -->
- <!-- *NEED INPUT*: should "rate limits" (RPM/TPM, retry/backoff) be demoed here alongside cost, or deferred until students hit them in L10? -->
- <!-- *NEED INPUT*: are the demos run in a projected Jupyter notebook, a slide-embedded REPL, or a custom runner? Affects how prompts/models are pre-loaded. -->
- <!-- *NEED INPUT*: include the optional L02 bridge demo here, or save it as the opener for L02? -->
