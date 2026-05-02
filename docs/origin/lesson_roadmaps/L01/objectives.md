# L01: LLM and token basics

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (lesson-plan row L01).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).

## Where this lesson sits

L01 is the first lesson of the course. Students arrive with basic Python familiarity but, by assumption, no working mental model of what an LLM *is* at the API level. This lesson exists to install the four primitives every later lesson assumes: tokens, context windows, sampling controls (temperature et al.), and the cost-per-call arithmetic that follows from the first three.

Everything from L02 (prompting fundamentals) onward presumes that a student can look at a prompt, predict roughly how many tokens it will consume, predict roughly how much it will cost, and reason about why two runs of the same prompt might disagree. If the student leaves L01 without those four primitives, the rest of the course will feel like magic instead of engineering.

## Prerequisites

Students arriving at L01 should already be able to:

- Read and write basic Python — functions, classes, types, calling a third-party library (per [CURRICULUM_PRD.md § Prerequisites](../../CURRICULUM_PRD.md)).
- Make an HTTP call or use a Python SDK — they don't need to know *which* SDK yet; just the shape of "import library, instantiate client, call a method, read a response."
- Reason about strings as sequences of characters. (We'll deliberately break this intuition during the lesson — see Main Points — but they need the starting point.)

No prior LLM, prompting, or AI-API experience is assumed. This is the entry lesson.

<!-- *NEED INPUT*: do students already have an Anthropic API key issued before L01, or is "set up your API key" part of L01's lab? This determines whether the cost-estimation objective uses real spend or simulated counts. -->

## Learning objectives

By the end of L01, a student should be able to:

1. **Tokenize a string** and explain the result. Concretely:
   - Use a tokenizer (e.g. Anthropic's token-counting endpoint, or `tiktoken` for an OpenAI-family comparison) to convert a short string into its token IDs and back.
   - Predict, before tokenizing, whether a given string will be "short" or "long" in tokens — and identify cases where intuition is wrong (whitespace, punctuation, non-English text, code, repeated characters).
   - Articulate the rule of thumb (≈4 chars per token for English, much worse for code/JSON/non-Latin scripts) and explain *why* it is only a rule of thumb.

2. **Reason about context windows.** Concretely:
   - State the context-window size (in tokens) of the course's anchor model: **Claude Sonnet 4.6, 200k tokens** standard. (Sonnet 4.6 also has a 1M-token long-context offering; use the 200k number as the default for L01 and only mention the 1M variant if asked.)
   - Given a prompt, a system message, prior conversation turns, and a target output length, estimate whether the call will fit in the window and how much headroom remains.
   - Recognize the three failure modes of running out of window: hard rejection at request time, silent truncation of conversation history, and degraded quality as the model "forgets" earlier context. Name which one applies in which API.
   - Foreshadow why this matters later: every multi-turn agent (L07+) is fighting the context window, and the techniques in L14 (context management) and L15 (RAG) exist to push back against that pressure.

3. **Explain temperature and sampling.** Concretely:
   - Describe what the model is doing on a single forward pass (producing a probability distribution over the next token) and how a sampler turns that distribution into a chosen token.
   - Define `temperature` as a knob that flattens or sharpens the distribution before sampling, and predict the qualitative effect: temperature 0 → near-deterministic, same answer every time; temperature 1 → varied, sometimes creative, sometimes wrong.
   - Name at least one other sampling control (top-p / nucleus, top-k) and explain how it differs from temperature. Articulate that temperature 0 is *not* a guarantee of identical output across runs — it reduces variance, it doesn't eliminate it.
   - Pick a temperature for a task and defend the choice: classification or extraction → low; creative writing or brainstorming → higher; agent tool-routing (preview of L04) → low.

4. **Estimate cost.** Concretely:
   - Read a model's published per-token pricing (input vs. output rates) and compute the cost of a single call given input and output token counts.
   - Estimate the cost of a multi-turn conversation, accounting for the fact that prior turns are re-sent on every call (no server-side memory by default — a fact that surprises most students and motivates everything from prompt caching to L14/L15).
   - Recognize the asymmetry between input and output token pricing (output tokens typically cost 3–5x more) and what that implies for prompt design (long prompt + short answer is often cheaper than short prompt + long answer).
   - Order-of-magnitude estimate the cost of an agent run (preview of L07/L09) — e.g. "a 10-step agent with 2k-token context per step on Sonnet costs roughly $X" — without needing exact numbers.

## Main points the lecture should land

- **A token is not a word, a letter, or a syllable — it is whatever the model's tokenizer says it is.** Tokenizers are learned from training data; they fragment rare strings, punctuation, code, and non-English text in ways that defeat eyeball estimates. This is why a 200-character SQL query can easily be 100+ tokens while a 200-character English sentence is closer to 50. Get this wrong and every cost and context-window estimate is wrong.
- **The context window is a hard ceiling on everything the model considers at once — input *and* output combined.** Students often think of "the prompt" as the only thing that consumes window. In reality the system message, prior turns, tool definitions (relevant from L04 onward), and the model's own response all share the same budget. This single fact drives the design of half the techniques in this course.
- **The model produces a probability distribution; the sampler picks one token from it.** This is the right level of abstraction for the audience — too high and "temperature" becomes mystical, too low and we're teaching transformer internals. Everything about reproducibility, creativity, and "why did it answer differently this time" follows from this one diagram.
- **Temperature 0 is *low* variance, not *zero* variance.** Floating-point non-determinism, server-side batching, and tie-breaking between equally-likely tokens all leak through. Promising students "deterministic output" sets them up to be confused later when an eval flakes.
- **You pay per token, both directions, every call.** Input and output prices differ. Multi-turn conversations re-bill the entire history. There is no free server-side memory. This is the foundation that makes prompt caching (a topic the SDK exposes), context management (L14), and retrieval (L15) make sense as cost-and-quality moves rather than abstract "best practices."
- **The four primitives are connected, not independent.** Tokens feed into context-window math; context-window math feeds into cost; sampling temperature affects how many output tokens you tend to generate. A change to one cascades. The lesson should land them as a *system*, not as four bullet points.

## Common student confusions to watch for

- *"One token equals one word."* Wrong almost everywhere — and especially wrong on the kinds of structured strings (JSON, code, URLs) that agents deal in. The lab should include a deliberate "guess then tokenize" exercise so the student feels the gap.
- *"The model remembers our previous conversation."* It does not, by default. The illusion of memory is the client re-sending prior turns. This confusion will cause real bills if not corrected here.
- *"Temperature 0 is deterministic."* See Main Points — frame as low variance, not zero.
- *"Bigger context window = always better."* No: more tokens cost more, more tokens slow inference down, and models can degrade in quality near the long-context tail. The course revisits this in L09 and L14.
- *"Cost is too small to matter at this scale."* True for one call, false for a 10-step agent run, doubly false when iterating on a prompt 100 times during development. The cost-estimation objective is here so that students develop a habit of back-of-envelope math *before* they start running agents.
- *"Counting characters is good enough."* Sometimes — and the rule of thumb works for plain English — but it is the wrong default for the input shapes (code, JSON, transcripts) that agents actually consume.

## Bridge to L02

L02 (prompting fundamentals) builds directly on every primitive from L01:

- **System/user/assistant roles** (L02 subgoal 1) are how prior conversation turns are structured — and every one of those turns is billed against the context window L01 just taught.
- **Structured output** (L02 subgoal 2) is partly about parseability and partly about *not paying for tokens you don't need* — an L01 cost-awareness move applied to prompt design.
- **Few-shot examples** (L02 subgoal 3) are a deliberate context-window-vs-quality trade-off. Students who understood L01's "input tokens cost money and eat the window" will treat few-shot examples as expensive-but-sometimes-worth-it, which is the right intuition.

The single sentence to leave students with at the end of L01 is something like: *"From here on, every prompt you write is a budget decision — token count, dollar count, and context-window count, all at once."*

## Open authoring questions

- <!-- *NEED INPUT*: estimated lecture duration — best guess 60–75 minutes as one lecture covering all four objectives, with the lab handling hands-on tokenization and cost estimation. -->
- <!-- *NEED INPUT*: do we use the Anthropic SDK exclusively from L01, or briefly show `tiktoken` / a tokenizer comparison so students see that tokenization is a *family* of choices (BPE, WordPiece, etc.) made differently by different vendors? -->
- <!-- *NEED INPUT*: is prompt caching introduced here (as a foreshadow when discussing the "every call re-sends history" cost surprise), or strictly deferred to L14 (context management)? -->
- <!-- *NEED INPUT*: should "rate limits" (RPM/TPM, retry/backoff) sit in L01 alongside cost, or be deferred until students are running multi-step agents and actually hit them in L07? -->
- <!-- *NEED INPUT*: confirm that L01 teaches Anthropic's Claude API specifically vs. a provider-agnostic framing — affects whether the tokenizer demo uses Anthropic's token-counting endpoint, `tiktoken`, both, or a generic explanation. -->
- <!-- *NEED INPUT*: prerequisite-API-key setup — handled in a pre-lesson onboarding doc, in L01 itself, or as the first lab? Determines whether the cost-estimation objective uses real spend. -->
