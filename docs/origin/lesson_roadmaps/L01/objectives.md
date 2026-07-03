# L01: LLM and token basics

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (lesson-plan row L01).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).

## Where this lesson sits

L01 is the first lesson of the course. Students arrive with basic Python familiarity but, by assumption, no working mental model of what an LLM *is* at the API level. This lesson installs that model **in one connected story** rather than as four disconnected facts.

The spine of the lesson is a single chain of "why":

1. **An LLM is a next-word predictor** — given the text so far, it produces a probability distribution over what comes next, samples one piece, appends it, and repeats. Everything else in the lesson is a consequence of this one fact.
2. **The pieces it predicts are *tokens*, not words** — so we motivate *why* the unit is sub-word, and look at what tokenization does to the strings agents actually handle (proper names, novel words, code, non-English).
3. **How good the prediction is depends on the model and on the context you give it** — bigger models put more probability on the right continuation (a *mechanistic* foreshadow of L13, not model-selection), and *front-loading* relevant context steers the whole continuation.
4. **So you build reusable preambles** — stable blocks of instruction/context you reuse across calls.
5. **…and now budgeting is unavoidable** — because there is no server-side memory, every call re-sends that preamble plus the whole history, all measured in tokens. Those tokens hit two budgets at once: **space** (the context window) and **money** (per-token pricing, both directions, every call).

The four assessable PRD subgoals — tokenize a string, reason about context windows, explain temperature and sampling, estimate cost — all live inside this chain. The point of the rework is that a student should never feel the lesson "jump" from tokens to budgeting: budgeting is where the chain *lands*, because you spend the whole lesson accumulating the overhead you then have to pay for.

Everything from L02 (prompting fundamentals) onward presumes a student can look at a prompt, predict roughly how many tokens it will consume, predict roughly how much it will cost, and reason about why two runs of the same prompt might disagree. If the student leaves L01 without that, the rest of the course feels like magic instead of engineering.

## Prerequisites

Students arriving at L01 should already be able to:

- Read and write basic Python — functions, classes, types, calling a third-party library (per [CURRICULUM_PRD.md § Prerequisites](../../CURRICULUM_PRD.md)).
- Make an HTTP call or use a Python SDK — they don't need to know *which* SDK yet; just the shape of "import library, instantiate client, call a method, read a response."
- Reason about strings as sequences of characters. (We deliberately break this intuition during the lesson — see Main Points — but they need the starting point.)

No prior LLM, prompting, or AI-API experience is assumed. This is the entry lesson.

<!-- *NEED INPUT*: do students already have an Anthropic API key issued before L01, or is "set up your API key" part of L01's lab? This determines whether the cost-estimation objective uses real spend or simulated counts. -->

## Learning objectives

By the end of L01, a student should be able to:

1. **Describe the next-word-prediction loop.** Concretely:
   - Explain, in their own words, the loop: the model reads the text so far, produces a probability distribution over the next token, a sampler picks one, it is appended, and the loop repeats until a stop condition. "Generating a paragraph" is this loop run a few hundred times.
   - State the consequence that anchors the rest of the lesson: **the model has no memory between calls.** Any appearance of memory is the client re-sending prior text. (This objective is new framing; it is the mental model the other three PRD subgoals hang off of.)

2. **Tokenize a string and explain the result — including *why* the unit is sub-word.** *(PRD subgoal: tokenize a string.)* Concretely:
   - Use a tokenizer (`tiktoken` for an offline, deterministic view; Anthropic's count-tokens endpoint for the anchor model's own numbers) to convert a short string into token IDs and back.
   - Explain *why* models use sub-word tokens rather than whole words (an unbounded vocabulary can't cover every name, misspelling, or new word) or raw characters (sequences get too long and carry too little signal per step). Sub-word is the compromise: a fixed vocabulary whose pieces compose to spell anything.
   - Predict, before tokenizing, whether a string will be "short" or "long" in tokens, and identify where intuition breaks: **proper names, invented words, long numbers, code identifiers, URLs, and non-Latin scripts** all shatter into many pieces because the tokenizer never learned them as units.
   - Articulate the rule of thumb (≈4 chars per token for English, much worse for code/JSON/non-Latin) and explain *why* it is only a rule of thumb — tokenizers are *learned* from training data, so anything rare in that data fragments.

3. **Explain how prediction quality depends on model scale and on provided context.** *(New framing; foreshadows L13 and motivates preambles — not itself a PRD subgoal.)* Concretely:
   - Describe, from seeing a small→medium→large model predict the *same* next token, that a more capable model concentrates more probability on the sensible continuation and less on noise. Frame this as a *mechanistic* observation about prediction quality — **the engineering decision of *which* model or provider to use for a given capability (say, a vision model for OCR, a strong reasoner for planning, a cheap fast model for execution), with its cost/latency trade-offs, is deferred to L13 (choosing models & providers).** L01 only shows *that* capability sharpens prediction, not *how to choose*.
   - Explain **front-loading**: because the model conditions its next-token distribution on everything before, putting the relevant instructions, definitions, and examples *early* steers the whole continuation. Better input context is the lever the student controls (model scale is mostly not).

4. **Recognize reusable preambles as accumulated overhead.** Concretely:
   - Explain why, once front-loading helps, you naturally reuse the same block of instruction/persona/reference context across many calls — a *preamble* (an informal precursor to the system message L02 formalizes).
   - State the sting in the tail: because there's no server-side memory (objective 1), that preamble is **re-sent on every single call**, so it is overhead you carry — and therefore pay for — every time. This is the hinge into budgeting.

5. **Explain temperature and sampling as the knob on the distribution.** *(PRD subgoal: explain temperature and sampling.)* Concretely:
   - Point back to the distribution from objective 1 and define `temperature` as a knob that sharpens (→0) or flattens (→1+) that distribution *before* the sampler picks. Predict the qualitative effect: temperature 0 → near-deterministic; temperature 1 → varied, sometimes creative, sometimes wrong.
   - Name at least one other sampling control (top-p / nucleus, top-k) and how it differs. Articulate that temperature 0 is *low* variance, **not** *zero* variance — it reduces variance, it doesn't eliminate it.
   - Pick a temperature for a task and defend it: classification/extraction → low; brainstorming/creative → higher; agent tool-routing (preview of L07) → low.

6. **Reason about context windows.** *(PRD subgoal: reason about context windows.)* Concretely:
   - State the anchor model's window: **Claude Sonnet 4.6, 200k tokens** standard. (A 1M-token long-context variant exists; use 200k as the L01 default and mention 1M only if asked.)
   - Given a system message / preamble, prior turns, current input, and a target output length, estimate whether the call fits and how much headroom remains — explicitly counting the preamble overhead from objective 4.
   - Recognize the three failure modes of running out of window: hard rejection at request time, silent truncation of history, and quality degradation as earlier context is "forgotten." Name which applies in which API.
   - Foreshadow why this matters later: every multi-turn agent (L10+) fights the window, and the techniques in L19 (context management) and L21 (RAG) exist to push back.

7. **Estimate cost.** *(PRD subgoal: estimate cost.)* Concretely:
   - Read per-token pricing (input vs. output rates) and compute the cost of a single call from its input and output token counts.
   - Estimate a multi-turn conversation's cost, accounting for prior turns **and the preamble** being re-sent every call (no server-side memory — the fact that motivates prompt caching and L19/L21).
   - Recognize the input/output asymmetry (output typically 3–5× input) and what it implies for prompt design (long prompt + short answer is often cheaper than the reverse).
   - Order-of-magnitude estimate an agent run's cost (preview of L10/L12) without needing exact numbers.

## Main points the lecture should land

- **An LLM does exactly one thing: predict the next token, then do it again.** Text generation is that loop. Get this and temperature, streaming, "hallucination," and cost all become consequences rather than separate mysteries.
- **There is no memory between calls.** The model does not "remember" the conversation; the client re-sends it. This single fact is the thread that ties front-loading, preambles, the context window, and cost together — and it is the one students most need corrected before they run up a bill.
- **A token is not a word, a letter, or a syllable — it is whatever the tokenizer learned.** The unit is sub-word *on purpose*: it trades a fixed vocabulary against the ability to spell anything. That trade is exactly why rare strings — names, code, JSON, non-English — fragment, and why eyeball estimates fail on the inputs agents actually consume.
- **Prediction quality has two levers: the model, and the context you give it.** A more capable model sharpens the distribution (shown mechanistically here; *which* model/provider you match to each capability is L13). Front-loading relevant context is the lever the student controls — and it is *why* preambles exist.
- **Reusable preambles are overhead you pay for on every call.** The same instruction block that makes prediction better is re-sent (and re-billed, and re-counted against the window) every time. Budgeting is not a new topic bolted onto the end — it is the bill for the overhead the lesson spent its first half building up.
- **The context window is a hard ceiling on input *and* output combined**, and the preamble/history sit inside it alongside the current prompt and the model's own response.
- **The model produces a probability distribution; the sampler picks one token; temperature reshapes the distribution first.** This is the right altitude for the audience — high enough to skip transformer internals, low enough that "why did it answer differently this time" has a real answer.
- **Temperature 0 is *low* variance, not *zero* variance.** Floating-point non-determinism, batching, and tie-breaking leak through. Promising "deterministic output" sets students up to be confused when an eval flakes.
- **You pay per token, both directions, every call.** Input and output prices differ (output ~3–5× input). Multi-turn conversations re-bill the entire history plus preamble. This is the foundation that makes prompt caching, context management (L19), and retrieval (L21) read as cost-and-quality moves rather than abstract best practices.

## Common student confusions to watch for

- *"The model remembers our previous conversation."* It does not, by default. The illusion of memory is the client re-sending prior turns — and now, prior preambles too. This confusion causes real bills if not corrected here; it is the load-bearing correction of the lesson.
- *"One token equals one word."* Wrong almost everywhere — especially on the structured strings (JSON, code, URLs) and proper names that agents deal in. The lab should include a deliberate "guess then tokenize" exercise on exactly those.
- *"A bigger/newer model is just 'smarter' in some vague way."* Reframe: it puts more probability on good continuations. And resist letting this become a model-selection discussion — that is L13.
- *"Temperature 0 is deterministic."* See Main Points — frame as low variance, not zero.
- *"Bigger context window = always better."* No: more tokens cost more, slow inference, and can degrade quality near the long-context tail. Revisited in L12 and L16.
- *"Cost is too small to matter."* True for one call, false for a 10-step agent run, doubly false when iterating a prompt 100× in development. The cost objective exists to build the back-of-envelope habit *before* students run agents.

## Bridge to L02

L02 (prompting fundamentals) builds directly on this chain:

- **System/user/assistant roles** (L02 subgoal 1) are the formal version of the *reusable preamble* L01 introduces informally — and every one of those turns is billed against the window L01 just taught.
- **Structured output** (L02 subgoal 2) is partly parseability and partly *not paying for tokens you don't need* — an L01 cost-awareness move applied to prompt design.
- **Few-shot examples** (L02 subgoal 3) are front-loading made deliberate: a context-window-vs-quality trade-off. Students who felt L01's "input tokens cost money and eat the window" treat few-shot examples as expensive-but-sometimes-worth-it, which is the right intuition.

The single sentence to leave students with at the end of L01: *"Everything you front-load to make the model predict better is overhead you re-send, re-count, and re-pay on every call — so every prompt is a budget decision in tokens, dollars, and window space at once."*

## Open authoring questions

- <!-- *NEED INPUT*: the model-scale beat (objective 3 / demo 3.5) uses a local small→medium→large model ladder (GPT-2 124M → 355M → 774M via HuggingFace) so the next-token distribution is visible offline and deterministically. Confirm we accept transformers+torch as lesson dependencies for this one demo, versus a lighter (but softer) API-tier quality comparison. -->
- **RESOLVED:** the model-scale beat gets a one-line note on the L01 row in `CURRICULUM_PRD.md`, flagging it as a mechanistic foreshadow of L13 rather than a separately assessed subgoal.
- **RESOLVED:** L01 stays a single lecture item (~75–90 min) — not split into two blocks.
- <!-- *NEED INPUT*: is prompt caching introduced here (as a foreshadow when discussing the "every call re-sends the preamble + history" cost surprise), or strictly deferred to L19 (context management)? -->
- <!-- *NEED INPUT*: confirm token *counting* stays on `tiktoken` (offline, deterministic) for the labs, with Anthropic's count-tokens endpoint shown once for the anchor model — versus standardizing on one of them. -->
- <!-- *NEED INPUT*: prerequisite-API-key setup — handled in a pre-lesson onboarding doc, in L01 itself, or as the first lab? Determines whether the cost-estimation objective uses real spend. -->
