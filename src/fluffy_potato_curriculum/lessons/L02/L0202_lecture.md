# Prompting fundamentals: roles, structured output, few-shot

```yaml
title: Prompting fundamentals: roles, structured output, few-shot
keywords: prompting, system user assistant roles, messages list, structured output, json, defensive parsing, few-shot, in-context examples, task shapes, extraction, classification, ranking, constrained generation, summarization, cost
estimated duration: 110
```

> **Lesson:** L02. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L02/objectives.md).
> This page is your written reference — thorough on purpose, so if you missed the live session you can
> rebuild the whole lesson from the page. The live demos are split one per lever
> ([L0203](L0203_lecture.ipynb) roles, [L0205](L0205_lecture.ipynb) structured output,
> [L0207](L0207_lecture.ipynb) few-shot); hands-on practice is in the L02 labs
> (L0204 / L0206 / L0208).
> **Anchor model throughout: Claude Sonnet 4.6.**

## section 1. The lesson in one claim

### slide 1.1 From the container to the contents

- In L01 you learned the *container*: tokens, context window, temperature, cost. Here you learn
  what goes *in* it — the prompt.
- The whole lesson rests on one claim: **the same content, arranged differently, produces a
  different answer.** Structure is a lever, not decoration.
- You'll pick up three levers here — **roles**, **structured output**, **few-shot** — and then a
  **catalog** of the single-step task shapes they unlock (extract, classify, rank,
  generate-to-a-constraint, summarize). The levers are the minimum toolkit L06 (reasoning) and L07
  (tools) assume you already have; the catalog (section 5) is what one call can *do* with them.
- diagram: a zoom-in / nesting block — an outer box "L01: the container (tokens · context window · temperature · cost)" with an inner box "L02: the contents = the prompt (roles · structured output · few-shot)", and a magnifier arrow from outer to inner captioned "same call — now we fill what goes inside."

### slide 1.2 The three levers at a glance

- table: the three levers, the one sentence each lands, and the L01 cost shadow each carries.

| Lever | The mental model | L01 cost shadow |
| --- | --- | --- |
| Roles | system = always-true, user = per-call; the model treats them differently | system is re-sent every turn — keep it lean |
| Structured output | a *negotiation*, not a guarantee — parse defensively | tight schema ⇒ fewer output tokens (output is pricey) |
| Few-shot | a behavior nudge, priced in tokens; diversity beats volume | every example costs input tokens on every call |

- The three levers are *mechanics*; **section 5** turns them on the five everyday **task shapes** —
  extraction, classification, ranking, constrained generation, summarization.

### slide 1.3 What L02 does not teach

- **Not chain-of-thought.** Scratchpad / `<thinking>` reasoning is L06's job. Here you get the
  structured-*answer* half, and you'll see the `<thinking>`/`<answer>` channel split (slide 3.6 —
  mini-essential, since the mini skips L06); L06 is where you pick up the *thinking* half: what to
  reason about and when it helps.
- **Not tool calling.** Forcing schema-conformant output via the tool-use protocol is L07. Here you
  ask for JSON *by instruction only* and parse defensively.
- **Not orchestration.** Chaining several single-step tasks into a pipeline is L03–L05. Section 5's
  catalog is the menu of what *one* node can do; wiring nodes together comes with the graph ramp.
- Resist broadening past these shapes for now — no reasoning, no tools, no multi-step control yet.
  Your job in L02 is the prompting toolkit and the single-step tasks it unlocks.
- diagram: a scope fence — a solid "IN L02" box (roles · structured output · few-shot · the five single-step task shapes) beside a dashed "NOT YET" box whose three chips point to their lessons: chain-of-thought → L06, tool calling → L07, orchestration / pipelines → L03–L05.

[↑ Back to top](#prompting-fundamentals-roles-structured-output-few-shot)

## section 2. Roles: who said what

### slide 2.1 A prompt is a list, and you own it

- "The conversation" is a Python `list` of `{role, content}` messages that *your code* assembles
  and re-sends every call. There's no hidden server-side memory — recall that from L01.
- Three roles you're working with: **system** (out-of-band steering, the always-true context),
  **user** (inputs from the caller), **assistant** (the model's prior replies — or planted
  in-context examples, see section 4).
- diagram: a growing `messages=[...]` list — `[system, user, assistant, user, assistant, …]` —
  with a label "the caller builds and re-sends this whole list every turn."

### slide 2.2 system = always-true, user = per-call

- The rule of thumb to carry forward: **durable identity-and-policy content goes in `system`;
  per-call task content goes in `user`.** The system message is the part that's true on *every*
  call of this prompt.
- Why it matters two ways: (a) **reuse** — a lean, durable system message can front many different
  user requests unchanged; (b) **cost** — the system message gets re-sent every turn, so any bloat
  there is paid for forever (and it's exactly what *prompt caching*, a later L19 topic, exists to
  fight).
- diagram: two boxes — `system: "You are a triage assistant. Answer in two short paragraphs…"`
  (stamped "always true") and `user: "My head has hurt for three days."` (stamped "this call only").

### slide 2.3 Persona: the durable "who you are"

- A **persona** is the slice of the `system` message that says *who the model is, how it speaks,
  and what it always does* — its **role** ("You are a triage assistant"), its **tone / register**
  (terse, warm, formal), and any **standing format or policy** ("answer in two short paragraphs;
  never give dosage advice"). It's the reusable identity that fronts every `user` request
  unchanged — the "always-true" content from slide 2.2, given a name.
- **A persona is a behavior-and-voice nudge, not a capability unlock.** It reliably steers *how*
  the model answers — register, format, what it declines to do — but *"You are an expert
  oncologist"* does **not** make the medical facts more correct. Reach for a persona to fix
  **voice, tone, and adherence**; accuracy comes from better context, reasoning (L06), or a
  stronger model (L14), not from a flattering job title.
- Keep it **lean and durable** (slide 2.2 again): a persona earns its permanent seat in `system`
  only because it's true on *every* call. Per-call specifics still belong in `user` — a bloated
  persona is the same always-on-token footgun by another name.
- This is the seed of a much bigger idea. **From L11 on, an agent's persona *is* its `system`
  prompt** — its role, its guardrails, and its job within a multi-agent split. You'll meet it again
  as the shallow agent's system prompt (L11) and as "static system prompt vs. context management"
  (L19). Same lever you're learning now, higher stakes later.
- diagram: a `system` message split into two stacked bands — a durable **persona** band (role ·
  tone/register · standing policy: "You are a triage assistant · warm, plain language · two short
  paragraphs · no dosage advice") over the rest — stamped "true on every call"; a side caption
  "shapes *how* it answers (voice · format · adherence), **not** whether the facts are right."

### slide 2.4 The two mis-attribution footguns

- **Instructions buried in the user message** get re-sent and re-stated every turn — that's more
  tokens, and now the policy competes with the actual request for the model's attention.
- **Per-call data crammed into the system message** *poisons reuse*: the system message stops being
  always-true, so the next user request inherits stale data — the model may end up answering about
  the *last* caller's problem instead of this one.
- table: where each kind of content belongs.

| Content | Belongs in | Why |
| --- | --- | --- |
| Persona, tone, output format, standing policy | `system` | true on every call; enables reuse |
| This call's question, document, or data | `user` | changes every call |
| A worked example you're planting | `assistant` (or a labeled block in `user`) | see section 4 |

### slide 2.5 The system message is weighted, not enforced

- The model treats `system` as conversational context with a **privileged label** — it tends to
  follow it, but it's **not invulnerable** to instructions in user messages. Frame it for yourself
  as "always-true context," not "inviolable rules."
- Anything close to a **security or policy guarantee belongs outside the model** (in your code),
  not inside the system prompt. The system prompt is not a sandbox.
- A misconception worth dropping right now: *"the system message is enforced; the user can't override
  it."* It isn't — strongly weighted ≠ enforced.
- diagram: a "nudge, not a wall" contrast — the system message drawn as a thick *weighted* arrow biasing the model (not a solid barrier), a thinner user-message arrow still able to push against it, and a separate hard wall labeled "real guarantees live in your code, outside the model." Caption: "privileged label ≠ enforced."

### slide 2.6 Multi-turn, and the first-call vs. Nth-call axis

- A multi-turn conversation is just appending alternating `user`/`assistant` messages and
  re-sending the **whole list**. Every continued turn re-bills the history — that's the L01
  staircase again.
- **Prompt quality has a first-call vs. Nth-call axis:** a prompt that behaves on call 1 can
  *degrade* by call 5 as the model accumulates its own (sometimes flawed) prior turns. This is
  usually the first place you'll feel "the model got worse" with nothing obviously changed.
- Decide deliberately: **continue** when the history is load-bearing context; **start fresh** when
  it isn't, so you dodge both the cost staircase and accumulated drift.
- diagram: a turn-by-turn staircase — the `messages` list growing `[u, a, u, a, u, a…]` across calls 1→5, each step taller (re-billed history = the L01 cost staircase), with a dashed "quality" line drifting downward by call 5; a fork at the end labeled "continue (history is load-bearing) vs. start fresh (dodge cost + drift)."

[↑ Back to top](#prompting-fundamentals-roles-structured-output-few-shot)

## section 3. Structured output: a negotiation, not a guarantee

### slide 3.1 Why ask for structure at all

- Structured output makes the model's response **programmatic** rather than **conversational** — a
  dict your code can index, not a paragraph you have to read.
- It's the precondition for almost everything later: evals (L13), tool calling (L07), and
  multi-step pipelines all need the model's output to be *machine-readable*.
- The shapes you'll ask for: a **JSON object**, a **fixed list of fields**, or **XML-ish tags**
  like `<answer>…</answer>`.
- diagram: one model reply splitting into two lanes — top lane "conversational: a paragraph a human must read", bottom lane "programmatic: a dict your code can index" — with the bottom lane flowing on to downstream chips (evals L13 · tools L07 · pipelines) that all *require* machine-readable output.

### slide 3.2 The L02 method: prompt-instruction-only

- Here you get structure **by instruction alone**: you *tell* the model the exact shape in the
  prompt ("Return a single JSON object with exactly these keys, no prose") and then parse the
  reply.
- diagram: prompt with an explicit schema spec → model reply (hopefully JSON) → `parse()` → dict.
- A quick look ahead — you won't need it yet: *in production you'd reach for Anthropic's
  **tool-use-as-schema** to force schema-conformant output — that's L07. The parsing discipline
  below still applies there, because tool-call arguments can also be malformed.*

### slide 3.3 The model agrees to the contract; it does not enforce it

- Even when told "JSON only," the model can hand you: **extra prose** around the JSON,
  **mismatched field names**, **missing required fields**, **wrong enum values it invented**, or
  an occasional **fully-malformed** blob.
- An **enum is a contract, not a constraint** — listing the allowed values asks the model to pick
  one; it doesn't stop the model from inventing a new one.
- The mental model to hold onto: **ask for structure, parse defensively, fail loudly on parse
  failure.**
- diagram: a fan-out — one request box "return JSON only" branching to five bad-output cards: extra prose around the JSON · mismatched field names · missing required field · invented enum value · fully-malformed blob. Caption: "an enum is a contract, not a constraint — ask, then verify."

### slide 3.4 The defensive parser

- The standard three-step parser you'll use:
  1. `json.loads` the whole reply — the happy path.
  2. On failure, **regex out the first `{...}` block** and retry — this salvages JSON wrapped in
     prose.
  3. On failure again, **raise loudly** with the raw response in the error message.
- **Fail loudly, never silently.** A silent fallback (say, returning `{}` on parse failure) hides
  a bug that *compounds* downstream in agent loops (L10) and traces (L12). A logged, raised error
  is a diagnosis; a silent empty dict is a time bomb waiting for you later.
- Validate the *contents*, not just "did it parse": are the required keys present? Is the enum
  value in the allowed set? You decide whether a missing optional field is `null`-tolerant or an
  error — and make that call on purpose.
- diagram: a three-step parser flowchart with fallbacks — `json.loads` the whole reply → on failure, regex out the first `{…}` block and retry → on failure again, raise loudly with the raw response — then a "validate contents" gate (required keys present? enum in the allowed set?). Never a silent `{}` fallback.

```text
  raw reply
     │
     ▼
  ① json.loads(whole reply) ──ok──▶ dict
     │ fail
     ▼
  ② regex first {…} block, retry ──ok──▶ dict
     │ fail
     ▼
  ③ raise loudly (raw response in the error)   ← never a silent {}

  then, on any dict: validate contents — required keys present? enum in ALLOWED?
```

### slide 3.5 Temperature, verbosity, and cost for structured output

- Use **low temperature (≈0)** for extraction and classification — you want the single
  most-likely, repeatable answer here, not creative variety (that's your L01 callback).
- Ask for a **tight schema and no prose** — this typically *reduces* output tokens versus a chatty
  answer. Structured output is often a **cost win** as well as a parseability win, since output is
  the expensive direction (L01 again).
- Keep input and output *shapes consistent*: a labeled, structured request yields cleaner
  structured output than the same request phrased in flowing English. Consistency reduces the
  model's degrees of freedom — and therefore your parse failures.
- diagram: two small gauges side by side — a temperature dial pinned near 0 for extraction / classification (the single repeatable answer), beside a token-size comparison "tight schema, no prose → fewer output tokens" vs. a chatty answer. Caption: "structured output is often a cost win too — output is the pricey direction."

### slide 3.6 The thinking/answer channel split (mini-essential)

- **First, the word:** a **channel** is a *labeled region of a single reply* — a `<tag>…</tag>`
  pair that carves the model's one text stream into named parts you can pull out separately. The
  tags are plain text you asked for in the prompt, **not** a special API field or token — which is
  exactly why the same defensive parser (slide 3.4) reads them.
- An assistant reply can carry **more than the answer**: a `<thinking>…</thinking>` scratchpad
  *then* a structured `<answer>{…}</answer>`. This is just structured output with a reasoning block
  in front — you extract the `<answer>` (a tag-match), then reuse the same defensive parser from
  slide 3.4.
- **L02 owns the answer channel; L06 owns the thinking channel.** *What* to put inside the
  `<thinking>` block — and when reasoning helps vs. hurts — is L06's job. Here you only see that
  the two **compose**: the parser handles the answer whether or not a thinking block precedes it.
- **Mini-track note:** the mini course skips L06, so this is your one look at the thinking
  channel — enough to recognize the `<thinking>`/`<answer>` shape and parse it. The reasoning craft
  waits for L06.
- diagram: one assistant reply drawn as two stacked blocks — `<thinking>…scratchpad…</thinking>` then `<answer>{…}</answer>` — with a parser arrow reaching *past* the thinking block to tag-match `<answer>` and hand it to the same defensive parser from slide 3.4. Label the split "L06 owns thinking · L02 owns the answer."

```text
  assistant reply
  ┌─────────────────────────────┐
  │ <thinking> … scratchpad … │   ◀ L06 owns this channel
  ├─────────────────────────────┤
  │ <answer> { … } </answer>    │   ◀ L02: tag-match, then defensive-parse (slide 3.4)
  └─────────────────────────────┘
```

[↑ Back to top](#prompting-fundamentals-roles-structured-output-few-shot)

## section 4. Few-shot examples: a precision tool

### slide 4.1 What few-shot is — and isn't

- A **few-shot prompt** is a small number of input→output **example pairs** placed before the real
  input, to show the model the desired output shape or behavior.
- Few-shot is **behavior conditioning, not teaching.** The model's underlying capabilities don't
  change; you're shifting the *in-context distribution*. Frame it for yourself as **showing, not
  teaching**.
- A misconception worth dropping: *"few-shot teaches the model new things."* It doesn't — it
  conditions this one call's behavior; nothing about the model itself is updated.
- diagram: a stack feeding one call — example pairs `[in₁→out₁] [in₂→out₂] [in₃→out₃]` placed before the real input, all flowing into a single model call; a side note "model weights unchanged — this conditions *this call's* behavior (showing), it does not train (teaching)."

### slide 4.2 Two placements, one trade-off

- **Alternating fake turns:** plant each example as a `user` message (the example input) followed
  by an `assistant` message (the desired output). Here's a surprise worth sitting with: the
  `assistant` role is the right home for fake "model said this" content.
- **Single block in the user message:** write all the examples as a labeled text block inside one
  `user` message, then the real input.
- Placement usually matters **less than content** — the two perform similarly. Pick whichever your
  downstream parser or cache strategy prefers.
- diagram: the two layouts side by side — left: `[user(ex1_in), assistant(ex1_out), user(ex2_in),
  assistant(ex2_out), user(real_in)]`; right: `[user("Examples:\n…\n\nNow classify: real_in")]`.

### slide 4.3 Diversity beats volume

- A few **well-chosen, contrasting** examples outperform many **similar** ones. Four examples
  covering four labels beat four examples of the same label.
- The failure mode to name: **"all examples look like the easy case."** A uniform example set
  makes the model **overfit to a surface pattern** — show it four `P0-bug` examples and it starts
  calling everything a P0 bug.
- Distinguish **few-shot for format** (showing the desired output *shape*) from **few-shot for
  behavior** (showing the desired *judgment*). Both work; they fail differently.
- diagram: a two-panel contrast — left "4× the same easy case (all `P0-bug`)" → the model overfits the surface pattern and starts calling everything P0; right "4 diverse examples covering the label set" → the model generalizes. Caption: "diversity > volume — watch for 'all examples look like the easy case.'"

### slide 4.4 Few-shot is priced on every call

- Each example consumes **input tokens on every single call** — your L01 callback again. Few-shot
  is a real **cost-vs-quality dial**, not a free improvement.
- It's also **editable**: every time you find a failing input, you can add an example that
  resembles it. That's its power *and* its trap — the list grows, the per-call cost grows, and at
  some point you should reach for a different tool.
- table: when few-shot is the right tool, and when it isn't.

| Situation | Reach for… |
| --- | --- |
| A single clear instruction already works | just the instruction — skip few-shot |
| The model needs the team's idiosyncratic format/labels | few-shot (for format) |
| The task needs *reasoning* steps, not pattern-matching | chain-of-thought — L06 |
| The example set would dominate the context window | a different approach (retrieval L21, model class L14, fine-tuning — out of scope) |

[↑ Back to top](#prompting-fundamentals-roles-structured-output-few-shot)

## section 5. The common single-step task shapes

### slide 5.1 One call, many shapes

- The three levers so far are *mechanics*. Point them at a goal and you get the everyday jobs a
  **single LLM call** does. Learn to **name the shape** — the name tells you which lever to reach
  for and, crucially, what to **validate**.
- The catalog is five shapes: **extraction**, **classification**, **ranking / recommendation**,
  **constrained generation**, **summarization / transformation**. Nothing here is a new
  technique — each is the three levers aimed at a different **output contract**.
- table: the five shapes, the lever each leans on, the output contract, and the failure a validator
  must catch.

| Shape | Leans on | Output contract | Watch-for failure |
| --- | --- | --- | --- |
| Extraction | structured output | JSON with the required fields | dropped / hallucinated fields |
| Classification | structured output (+ few-shot) | a value from a fixed label set | invented, out-of-set label |
| Ranking / recommendation | structured output | the candidate ids, reordered | dropped, duplicated, or rewritten candidates |
| Constrained generation | structured output + explicit rule | exactly N items / within a bound | wrong count, over-length |
| Summarization / transformation | system message (role) | shorter or restyled text, meaning kept | added facts, length drift |

### slide 5.2 Extraction — pull fields out of text

- **Extraction is structured output (section 3) pointed at "pull these fields."** You already did
  this in the structured-output demo: name the fields, ask for one JSON object, parse defensively.
- **Single-schema:** a fixed set of keys every time (e.g. `customer_name`, `order_id`, `intent`).
- **Mixed-schema:** pull a *list* of heterogeneous items whose fields differ (e.g. line-items where
  a product row has `sku` + `qty` and a discount row has `code` + `percent`). Ask for a JSON array
  of objects and validate each item against the shape it claims to be.
- The failure to watch for: the model **invents** a field it wasn't asked for, or **drops** one
  that was in the text — the required-keys check from section 3 is exactly what catches it.
- diagram: an extraction flow — a free-text blob → the model → a JSON object with named fields (`customer_name` · `order_id` · `intent`); a validator gate flags a **dropped** field (was in the text) and a **hallucinated** field (never asked for), tying straight back to the required-keys check from section 3.

### slide 5.3 Classification — sort into a fixed label set

- **Classification is structured output constrained to a label set** — and it's the place
  **few-shot (section 4)** most earns its keep, because a team's label *wording* is often
  idiosyncratic.
- Three flavours: **flat** (one of N labels), **hierarchical / taxonomy** (`category` then
  `subcategory` — ask for both keys), and **multi-label** (return a JSON *array* of labels when
  more than one applies).
- **An enum is a contract, not a constraint** (section 3 again): the model can return a label
  outside the set, so validate `label in ALLOWED` — and for a taxonomy, validate the subcategory
  belongs to the chosen category.
- diagram: an input ticket flowing into a flat label, then into a two-level `category → subcategory`
  pair, with the validator rejecting an out-of-set label.

### slide 5.4 Ranking / recommendation — order a candidate list

- **Give the candidates ids and ask the model to return the ids in order** — never ask it to
  rewrite the candidates. Referencing by id keeps the output tiny and the contract checkable.
- The contract to **validate**: every candidate id appears in the output **exactly once** — no
  drops, no duplicates, nothing invented. This is the classic silent failure: the ranking *looks*
  fine until you notice one item vanished.
- Optionally ask for a one-line justification per rank — useful, but it costs output tokens and
  isn't the thing you validate.
- table: candidate list in, ordered id list out, validator preserving the set.

| Prompt gives | Model returns | Validator checks |
| --- | --- | --- |
| `[{id: 1, …}, {id: 2, …}, {id: 3, …}]` + a criterion | `[3, 1, 2]` | each id present exactly once |

### slide 5.5 Constrained generation — produce exactly N, within a bound

- Generation is the one shape where you may *want* a higher temperature — but the **constraint**
  (a count, a length cap, a required format) must be **explicit in the prompt and re-checked in
  code**.
- Ask for a **JSON array of length N** rather than a prose list — a shape you can `len()`-check
  beats counting bullet points by eye.
- The contract to validate: the count is exactly N, and each item respects the bound (say,
  `≤ 8 words`). **A constraint you don't check is a constraint the model is free to miss** — and it
  will, some runs.
- The failure to watch for: the model returns 4 or 6 items, or one item blows the length cap. Your
  validator turns that into a caught error instead of a downstream surprise.
- diagram: a generate-then-check flow — prompt "exactly N items, ≤ 8 words each" → model → JSON array → a validator gate: `len(array) == N`? each item within the bound? → pass ✓ / caught error ✗. Caption: "a constraint you don't check is one the model is free to miss."

### slide 5.6 Summarization and the transformation family

- **Summarization, rewriting, normalization, translation** are one family: text in, *transformed*
  text out, **meaning preserved**. The **system message (section 2)** carries the durable policy —
  audience, length, register — because it's true on *every* call of this transformer.
- diagram: `system: "Summarize for a non-technical exec in one sentence."` + `user: <the document>`
  → a one-sentence summary; swap the system policy to restyle without touching the user text.
- The contract here is softer (there's no single right answer), so validation is about
  **guardrails, not equality**: length within bound, no invented facts, required elements present.
  Failure modes to name: **hallucinated additions** and **length drift**.
- Low temperature still helps for faithful summaries; lift it only for deliberately creative
  rewrites.

### slide 5.7 Picking the shape, and chaining shapes

- **Name the shape first.** "This is a classification problem" tells you to reach for a fixed
  label set, few-shot if the labels are idiosyncratic, and a `label in ALLOWED` validator — before
  you write a word of prompt.
- **Temperature by shape** (your L01 callback): near-0 for extraction / classification / ranking,
  since you want the single most-likely, repeatable answer; higher only where generation genuinely
  wants variety.
- **A hard task is usually a *pipeline* of these single steps** — extract, then classify, then
  summarize. That's exactly the seam **L03–L05** pick up, where each step becomes one **node** in a
  graph. L02 gives you the vocabulary of the single step; the graph ramp is where you wire several
  together.
- diagram: a three-node pipeline — extract → classify → summarize, the output of each box feeding the next; label each box "= one node" and caption "a hard task is a pipeline of single steps — that seam is L03–L05."

```text
  ┌─────────┐     ┌──────────┐     ┌───────────┐
  │ extract │ ──▶ │ classify │ ──▶ │ summarize │
  └─────────┘     └──────────┘     └───────────┘
   each box = one single-step shape = one node (L03–L05 wires them together)
```

[↑ Back to top](#prompting-fundamentals-roles-structured-output-few-shot)

## section 6. Wrap-up and the bridge to L06

### slide 6.1 The three levers and the catalog, reconnected

- **Roles** decide *where* content lives and how the model weights it. **Structured output**
  decides the *shape* of the answer and forces you to parse defensively. **Few-shot** *nudges
  behavior* at a per-call token price.
- Those three levers are exactly what the **task catalog** (section 5) runs on: extraction and
  classification lean on structured output (and few-shot for odd labels); ranking and constrained
  generation add a checkable rule; summarization leans on the system message. Same toolkit, five
  output contracts.
- They interlock: a good prompt often uses all three — a lean `system` message, a `user` request
  that asks for a tight JSON shape, and a couple of diverse `assistant`/`user` examples when an
  instruction alone won't cut it.
- The sentence to leave with: *you now know how to ask the model for what you want, in the shape
  you want.*
- diagram: a bipartite map — three levers on the left (roles · structured output · few-shot) with edges to the five task shapes on the right (extraction · classification · ranking · constrained generation · summarization), each edge showing which lever a shape leans on.

```text
  levers                     task shapes
  ─────────                  ─────────────────────────────
  roles ───────────────────▶ summarization  (system-message policy)
  structured output ───────▶ extraction · classification
                       └───▶ ranking · constrained generation  (+ a checkable rule)
  few-shot ────────────────▶ classification  (idiosyncratic labels)
```

### slide 6.2 Four prompting anti-patterns to catch yourself committing

- You saw each of these break in the demos; putting a name to them makes them easy to catch in
  your *own* prompts. All four share one root: **treating a strong nudge as a hard guarantee.** A
  role's weighting, a JSON contract, an example's pull, a system prompt's authority — each is
  *best-effort*, and building the validate-don't-assume reflex is L02's whole job.
- table: the four anti-patterns, the one-line cure, and where you saw it.

| Anti-pattern | Cure | Where you saw it |
| --- | --- | --- |
| **Instructions in the wrong role** — policy buried in `user`, or per-call data pinned in `system` | *system = always-true, user = per-call* | slide 2.4 (the two mis-attribution footguns) |
| **Trusting structured output as a guarantee** — `json.loads` on the raw reply, assuming it holds | the parser *is* the enforcement — try / validate / fail loudly, never silently return `{}` | slides 3.3–3.4 |
| **Few-shot that leaks format or biases the answer** — under-diverse examples that make the model overfit | diversity over volume; cover the label set | slide 4.3 ("all examples look like the easy case") |
| **Bloated always-on system prompt** — every rule and example crammed into `system`, re-sent on every call | keep `system` lean and durable; move occasional guidance to the `user` turn | slides 2.2 / 2.6 / 4.4 (the per-turn token staircase) |

- Two of the four point straight forward — **naming the link is enough, no need to re-teach it
  here**: defensive parsing carries into **L07** (tool-call arguments can be malformed too), and
  the lean-`system` discipline is the seed of context management (**L19**) and the
  skill-vs-system-prompt call in **L22**.

### slide 6.3 Where this goes next

- **Immediate next lesson: [L03](../../../../docs/origin/lesson_roadmaps/L03/objectives.md)
  (single-node operations).** You'll take one task shape from section 5 — **extraction** — and
  wrap it as a reusable **graph node**: the same structured-output discipline, now living inside a
  framework-managed function. L03–L05 then chain several single-step shapes into a graph.
- **Later: L06 (reasoning).** The three levers are also what L06 builds chain-of-thought on —
  that hand-off is the next slide.
- diagram: a forward roadmap arrow — L02 (single-step toolkit) → L03 (wrap extraction as a reusable node) → L04–L05 (chain nodes into a graph) → L06 (reasoning on the same three levers); mark L03 "immediate next."

### slide 6.4 What L06 does with this

- L06 (teaching an LLM to think) sends its chain-of-thought prompts through **the same role
  structure** you just learned — a `system` message that licenses reasoning plus a `user` message
  with the problem.
- L06's `<thinking>…</thinking><answer>{…}</answer>` pattern is **a specific use of structured
  output** (section 3): the parser pulls the answer out and optionally logs the thinking. The same
  defensive-parsing discipline carries over — `<answer>` blocks can be malformed too.
- L06's worked-example chain-of-thought is **a specific use of few-shot** (section 4), where each
  example pair *also* includes the reasoning trace. You saw few-shot as a generic technique here;
  L06 shows you one application of it.
- The hand-off sentence: *L06 is about making the model think harder before it answers — built
  entirely on the three levers you now own.*
- diagram: a hand-off map — the three L02 levers each feeding one L06 use: roles → a `system` message that licenses reasoning; structured output → the `<thinking>`/`<answer>` split; few-shot → worked-example chains-of-thought. Caption: "L06 = make the model think harder, built entirely on the three levers you now own."

[↑ Back to top](#prompting-fundamentals-roles-structured-output-few-shot)
