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

The four demos map one-to-one to the four learning objectives in [objectives.md](objectives.md). Run them in order on the first delivery — Demo 4 (cost) only lands cleanly once Demos 1–3 have made tokens, windows, and sampling concrete.

L01 is the very first lesson of the course. Students arrive cold. Spend a few extra minutes before Demo 1 on the "what is a Claude API call, mechanically" framing — even a 60-second whiteboard sketch of "your code → HTTP → model → response" pays for itself across all four demos.

## Pre-flight (once, at the top of the lesson)

The teacher should have, before the first demo starts:

- A working REPL or notebook with the project's Anthropic SDK setup (per the project's `uv` env). Both async and sync clients are fine; the demos use sync calls for clarity.
- An API key with a small spend cap (the cost demo runs real calls; a $5 cap is more than enough for a class delivery).
- A small wrapper that prints, after every call: `input_tokens`, `output_tokens`, wall-clock time, and the running per-call cost. This wrapper is the through-line for all four demos and **especially** Demo 4. <!-- *NEED INPUT*: standardize this wrapper as part of the L01 lab repo so the teacher and students share it — name and location TBD. -->
- A tokenizer available locally for the side-by-side comparison in Demo 1: Anthropic's token-counting endpoint (or `tiktoken` for an OpenAI-family contrast). <!-- *NEED INPUT*: do we use Anthropic's count-tokens endpoint exclusively, or include `tiktoken` as a "tokenizers are a *family* of choices" beat? Mirrored from [objectives.md](objectives.md). -->
- A way to project token IDs alongside the source string. Demo 1 hinges on the student *seeing* the boundaries. A simple "decode each token ID separately and join with `|`" output is enough.
- The four demo prompts and inputs pre-loaded as variables or cells so each demo is a *single keystroke* to run. Live-typing prompts during demos eats time and breaks pacing.

> Why pre-loaded prompts: L01 lives or dies on contrast — same string, different tokenizer; same prompt, different temperature; same call, different cost depending on conversation length. If the teacher mistypes a prompt mid-demo, the contrast breaks and the lesson lands as "the API is unpredictable" instead of "this primitive caused this change."

## Demo 1 — Tokens are not characters, words, or syllables (Subgoal 1)

**Goal:** show that the tokenizer's view of a string is materially different from a human's. Land the framing from [objectives.md](objectives.md): *"a token is whatever the model's tokenizer says it is."*

**Pre-flight:**

Pick four short strings designed to break human intuition in different directions:

1. **Plain English:** `"The quick brown fox jumps over the lazy dog."` — the baseline. Tokens roughly track words.
2. **Code:** `"def f(x): return x ** 2"` — punctuation and operators get their own tokens; `**` may or may not be one token; `def` and `return` are usually whole tokens.
3. **JSON:** `'{"user_id": 12345, "events": ["click", "scroll"]}'` — quotes, braces, colons, commas all consume tokens; numbers tokenize unpredictably.
4. **Non-Latin script:** a short phrase in Japanese, Arabic, or Hindi (something the teacher can read aloud or romanize). Tokens-per-character ratio explodes for most non-Latin scripts in BPE tokenizers.

Use Anthropic's count-tokens endpoint against **Claude Sonnet 4.6** (the course's anchor model) for the canonical numbers. The teacher should run the four strings through the endpoint once before class and update the on-screen counts to match. <!-- *NEED INPUT*: optionally also show `tiktoken`'s differing counts on the same strings as a "tokenizers disagree across vendors" beat — keep or drop? -->

**Live script:**

1. Put all four strings on screen. Ask the room (rhetorically — no participation): "Which of these is the longest in tokens?" Take a beat for the audience to commit silently to a guess.
2. Run the tokenizer on each string. Show the integer token IDs *and* the decoded boundaries side-by-side (e.g. `The| quick| brown| fox| jumps| over| the| lazy| dog|.`).
3. Print the token counts in a small table next to the strings. Highlight the surprises:
   - Code is denser-than-expected.
   - JSON is *much* denser-than-expected — every brace and quote is a token.
   - Non-Latin script is often 3–5x more tokens-per-character than English.
4. Show the rule of thumb (≈4 chars per token for English) on the English example, then point at the JSON and non-Latin examples and say: "this rule of thumb is wrong by a factor of 3 here."

**What to highlight:**

- The model never sees characters. It sees integers. The decoded "boundaries" are a visualization for *us* — the model sees `[464, 2068, 7586, ...]`.
- Tokenizers are *learned*, not designed. They reflect what was common in training data, which is why English is dense and JSON is sparse.
- Every later cost and context-window number in L01 depends on getting this right. If the student leaves with a "1 token = 1 word" model, every back-of-envelope estimate will be off by 2–10x on the strings agents actually consume.

**If the demo misbehaves:**

- If the token counts come out unsurprising (rare, but possible if the chosen strings are too tame), pull up a longer JSON blob — a full event payload, say — and show the count climb visibly. The contrast is the point.
- If the tokenizer endpoint is slow or rate-limited, fall back to a pre-recorded screenshot of the same demo. The lesson does not require the call to be live — it requires the *contrast* to be visible.

## Demo 2 — The context window is one shared budget (Subgoal 2)

**Goal:** show that input, system message, prior turns, and output all draw from the same window — and what happens when you push past the edge.

**Pre-flight:**

- A "window meter" visual: a horizontal bar showing the model's context window (e.g. 200,000 tokens), with a labeled segment for system message, conversation history, current input, and reserved output. This can be a slide, a tiny matplotlib plot, or a printed `█████████░░░░░░` bar.
- Three prepared inputs:
  1. **Tiny call:** a one-line system message, a one-line user prompt. Should fit easily.
  2. **Conversation-history call:** the same prompt, but with 20 prior fake assistant/user turns of ~500 tokens each prepended. Still fits, but the bar visibly fills.
  3. **Overflow call:** the same prompt, but with a deliberately oversized blob (e.g. a 250k-token concatenation of public-domain text) prepended. Will be rejected by the API.
- The Anthropic SDK's error-message output ready to read from. Don't catch and prettify it — the raw error is the lesson.

Anchor model is **Claude Sonnet 4.6**, 200k-token standard context window. Size the bar visual to 200k.

**Live script:**

1. Start with the tiny call. Show the response and the window-meter bar barely moving.
2. Run the conversation-history call. Show the bar visibly filling with the "history" segment dominating. Note the input cost going up — this previews Demo 4.
3. Run the overflow call. Let the API reject it. Read the raw error message aloud. Point out the specific token count in the error vs. the model's window limit.
4. Without re-running, walk the room through the three failure modes from [objectives.md](objectives.md):
   - **Hard rejection** — what they just saw.
   - **Silent truncation** — some clients/wrappers (or some agent frameworks they'll use later) will quietly drop the oldest turns. Name this as a *footgun*: the call succeeds but the model has forgotten things you assumed it remembered.
   - **Quality degradation** near the long-context tail — even when a call fits, models can struggle to attend to material in the middle of a very long context. Foreshadow that this motivates the techniques in L17 (context management) and L19 (RAG).

**What to highlight:**

- The window is shared. Every byte of system message, every prior turn, every tool definition (relevant from L04 onward), and every output token competes for the same budget.
- The illusion of "the model remembers our conversation" is the client re-sending history. Demo 4 will make the cost of that illusion visible.
- "Bigger window" does not mean "use it all." More tokens = more cost, more latency, and (often) lower quality near the tail. Foreshadow L10 (model power) and L14.

**If the demo misbehaves:**

- If the API does not reject the overflow call as expected (window sizes change; vendor behavior changes), fall back to the SDK's pre-flight token-count endpoint and *show* the count exceeding the documented limit. The point is "there is a hard ceiling," not "the API call must fail today."
- If the conversation-history call is too fast to feel meaningful, narrate the wrapper output: input tokens, latency, cost. The numbers are the demo.

## Demo 3 — Temperature is a knob, not a switch (Subgoal 3)

**Goal:** show the same prompt producing different outputs at different temperatures — and show that temperature 0 reduces variance but does not eliminate it.

**Pre-flight:**

- A single prompt with multiple plausible answers. Avoid "what is 2+2" (no variance space) and avoid "write a poem" (variance is too noisy to talk about). A good middle ground: *"Suggest a name for a coffee shop on a rainy street in Seattle. Just the name — one or two words."*
- The wrapper from pre-flight, configured to print the chosen output token IDs (not just the decoded text) so students can see when two "different" answers actually tokenized similarly.
- A tiny diagram of "model produces a probability distribution over the next token; sampler picks one." This can be a hand-drawn bar chart on a slide. Show the *same* distribution before and after temperature scaling: temperature 0 sharpens to a single tall bar; temperature 1 flattens.

Anchor model is **Claude Sonnet 4.6**. At temperature 0, Sonnet 4.6 is reliably low-variance on this prompt; at temperature 1 it spreads across many distinct names. The teacher should dry-run both temperatures once before class to confirm the behavior on the day.

**Live script:**

1. Show the diagram first. Don't run a single API call until the room understands what the sampler is choosing from. *This is the conceptual core of Subgoal 3 and the only demo where the slide comes before the call.*
2. Run the prompt at `temperature=0`. Run it 5 times in quick succession (a small loop is fine). Show the outputs — likely identical, or nearly so.
3. Run the prompt at `temperature=1`. Run it 5 times. Show the outputs — likely all different.
4. Run the prompt at `temperature=0` *again*, 10 more times. Look for one or two outputs that differ. If you find one, that is the demo's punchline: temperature 0 is *low* variance, not *zero* variance.
5. Mention `top_p` and `top_k` briefly — name them, describe each in one sentence, and say "we won't tune these in this course but you'll see them in API docs and you should not be surprised by them."

**What to highlight:**

- Temperature acts on the distribution *before* sampling. It does not change what the model "knows" — it changes how aggressively the sampler commits to the most-likely token.
- Temperature 0 is the right default for classification, extraction, structured output, and tool-routing (foreshadow L04). Temperature 1-ish is for brainstorming, creative writing, and deliberate exploration.
- Reproducibility is a *separate* problem from temperature. Even at temperature 0, floating-point math, server-side batching, and tie-breaking can cause output to vary across runs. Set the expectation now so future evals don't shock anyone.

**If the demo misbehaves:**

- If temperature 0 produces visibly identical output across all 15 runs (lucky day, or strongly-conditioned prompt), say so out loud and point at the diagram: "this is what 'sharp distribution' looks like in practice — but the *next* prompt might surprise us." Do not fake a variance result.
- If temperature 1 produces only one or two distinct answers (under-conditioned prompt), swap to a more open-ended backup prompt (e.g. "give me a one-sentence story opener about a fox") to see clearer spread.

## Demo 4 — Cost is per token, both directions, every call (Subgoal 4)

**Goal:** show real dollar amounts for real calls, and show how multi-turn conversations re-bill the entire history. Land the framing from [objectives.md](objectives.md): *"every prompt you write is a budget decision."*

**Pre-flight:**

- The latest published per-token pricing for **Claude Sonnet 4.6** (the course's anchor model), on a slide. Input rate and output rate as separate numbers. The teacher must pull current numbers from Anthropic's pricing page on the day of delivery — pricing changes and a stale slide undermines every cost claim that follows.
- The wrapper from pre-flight, with the per-call cost calculation already wired in. Display the running session cost in a corner.
- A tiny multi-turn conversation script: 5 user/assistant turns, each ~200 tokens. Run as a real conversation against the API.
- The same script, but instrumented to print the *cumulative input tokens* sent on each turn (so students see the staircase: turn 1 sends 200, turn 2 sends ~400, turn 3 sends ~600, etc.).

**Live script:**

1. Run a single call (use Demo 3's coffee-shop prompt — already familiar). Show the wrapper output: `input_tokens=20, output_tokens=3, cost=$0.0001`. Read the cost aloud and say "yes, that is one ten-thousandth of a dollar."
2. Run a longer prompt (paste in a paragraph of context, ask for a short answer). Show input tokens up, output tokens flat, cost up.
3. Now flip it: short prompt, ask for a 500-word answer. Show input tokens flat, output tokens up *a lot*, cost up *a lot* — typically more than the long-input case, because output tokens cost ~3–5x more.
4. Run the multi-turn conversation script. Print the cumulative input tokens at each turn. Show the staircase. Compute the total session cost.
5. Order-of-magnitude: take the per-turn cost, multiply by 10 (a typical agent run length, foreshadowing L07), then by 100 (a typical iteration count during development), then by 1000 (a small production deployment running once a minute for ~16 hours). Read the final number aloud. This is the punchline — students should leave the room with a felt sense for what an agent budget looks like.
6. Briefly mention prompt caching exists as a way to push back on the staircase cost in step 4. <!-- *NEED INPUT*: introduce prompt caching here as a one-line foreshadow, or strictly defer to L17 (context management)? Mirrored from [objectives.md](objectives.md). -->

**What to highlight:**

- Output tokens cost more than input tokens. Long prompt + short answer is often cheaper than short prompt + long answer. This flips most students' intuition.
- The conversation history staircase is the single biggest cost surprise students will encounter on their own. Naming it now prevents a surprise bill in the lab.
- The order-of-magnitude jump from "one call costs ~nothing" to "an agent in dev iteration costs real money" is the moment cost becomes a design concern, not an accounting concern.
- Bridge: the cost-awareness mindset installed here is what makes L17 (context management), L10 (model power), and prompt-caching design moves *land* later. Without L01, those lessons feel like premature optimization.

**If the demo misbehaves:**

- If the API is rate-limited or fails partway through the multi-turn script, walk through the pre-printed numbers. The math is the demo, not the live call.
- If pricing has changed since the slide was prepared, *say so out loud* and update the number live. Do not let a student catch a pricing mismatch unflagged — it undermines every cost claim in the rest of the course.

## Optional bridge demo — toward prompting fundamentals (L02)

If time allows, run one final mini-demo to set up L02. Take Demo 4's multi-turn conversation script and show how the same call would be structured if we used the system/user/assistant role separation that L02 will introduce. Don't *teach* role design — just point at the structure and say: "L02 makes this contract explicit, and shows why pushing instructions into the system message vs. the user message changes results." The point is to seed the role concept while it can ride on the still-warm context-window-and-cost intuition from Demo 4.

<!-- *NEED INPUT*: include this bridge demo, or save it as the opener for L02? -->

## Pacing notes for the teacher

- **Per-demo time:** 10–15 minutes including the post-demo discussion. Four demos plus the optional bridge fits in a 60–75 minute block, matching the duration estimate in [objectives.md](objectives.md). <!-- *NEED INPUT*: confirm against the lesson-time budget once duration is pinned in objectives.md's open questions. -->
- **Variance budget:** model outputs vary run-to-run (Demo 3 makes this explicit, but it applies to all four). Budget at least one re-run per demo. If a demo lands cleanly the first time, don't re-run for the sake of it — use the time to extend the discussion.
- **Resist live-coding tangents.** Students may ask "what about embedding tokens?" or "what about prompt caching?" or "what about images and multimodal tokens?" — name each as a "we'll get there" callback (embeddings → L18, caching → L17, multimodal → out of scope for this course unless the PRD changes) and *do not detour*. L01 is foundational; depth lives in later lessons.
- **The audience watches, doesn't participate.** Resist the temptation to ask "what do you think will happen?" — that is a lab pattern, not a demo pattern. Hands-on tokenization, temperature sweeps, and cost estimation are for the L01 labs.

## Open authoring questions

- <!-- *NEED INPUT*: do we use the Anthropic SDK exclusively from L01, or briefly show `tiktoken` / a tokenizer comparison so students see that tokenization is a *family* of choices? Mirrored from [objectives.md](objectives.md). -->
- <!-- *NEED INPUT*: is prompt caching introduced here (as a one-line foreshadow in Demo 4), or strictly deferred to L17 (context management)? Mirrored from [objectives.md](objectives.md). -->
- <!-- *NEED INPUT*: should "rate limits" (RPM/TPM, retry/backoff) be demoed here alongside cost, or deferred until students hit them in L07? Mirrored from [objectives.md](objectives.md). -->
- <!-- *NEED INPUT*: are the demos run in a Jupyter notebook the teacher projects, or in a slide-embedded REPL, or via a custom demo runner script? Affects how prompts are pre-loaded. -->
- <!-- *NEED INPUT*: a pointer/link to where the demo wrapper (token + cost + latency printer) lives as code — not yet decided. -->
- <!-- *NEED INPUT*: include the optional L02 bridge demo here, or save it as the opener for L02? -->
