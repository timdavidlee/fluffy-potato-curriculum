# Prompting fundamentals: roles, structured output, few-shot

```yaml
title: Prompting fundamentals: roles, structured output, few-shot
keywords: prompting, system user assistant roles, messages list, structured output, json, defensive parsing, few-shot, in-context examples, task shapes, extraction, classification, ranking, constrained generation, summarization, cost
estimated duration: 110
```

> **Lesson:** L02. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L02/objectives.md).
> This is the written reference lecture — thorough on purpose, so a student who missed the verbal
> delivery can rebuild the lesson from the page. The live demos are split one per lever
> ([L0203](L0203_lecture.ipynb) roles, [L0205](L0205_lecture.ipynb) structured output,
> [L0207](L0207_lecture.ipynb) few-shot); hands-on practice is in the L02 labs
> (L0204 / L0206 / L0208).
> **Anchor model throughout: Claude Sonnet 4.6.**

## section 1. The lesson in one claim

### slide 1.1 From the container to the contents

- L01 taught the *container*: tokens, context window, temperature, cost. L02 teaches what goes
  *in* it — the prompt.
- The whole lesson rests on one claim: **the same content, arranged differently, produces a
  different answer.** Structure is a lever, not decoration.
- L02 hands you three levers — **roles**, **structured output**, **few-shot** — and then a **catalog**
  of the single-step task shapes they unlock (extract, classify, rank, generate-to-a-constraint,
  summarize). The levers are the minimum toolkit L06 (reasoning) and L07 (tools) assume; the catalog
  (section 5) is what one call can *do* with them.

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

- **Not chain-of-thought.** Scratchpad / `<thinking>` reasoning is L06. L02 teaches the
  structured-*answer* half; L06 teaches the *thinking* half. They compose later.
- **Not tool calling.** Forcing schema-conformant output via the tool-use protocol is L07. Here we
  ask for JSON *by instruction only* and parse defensively.
- **Not orchestration.** Chaining several single-step tasks into a pipeline is L03–L05. Section 5's
  catalog is the menu of what *one* node can do; wiring nodes together is the graph ramp.
- Resist broadening past these shapes — no reasoning, no tools, no multi-step control yet. The job of
  L02 is the prompting toolkit and the single-step tasks it unlocks.

[↑ Back to top](#prompting-fundamentals-roles-structured-output-few-shot)

## section 2. Roles: who said what

### slide 2.1 A prompt is a list, and you own it

- "The conversation" is a Python `list` of `{role, content}` messages that *your code* assembles
  and re-sends every call. There is no hidden server-side memory (recall L01).
- Three roles: **system** (out-of-band steering, the always-true context), **user** (inputs from
  the caller), **assistant** (the model's prior replies — or planted in-context examples, see
  section 4).
- diagram: a growing `messages=[...]` list — `[system, user, assistant, user, assistant, …]` —
  with a label "the caller builds and re-sends this whole list every turn."

### slide 2.2 system = always-true, user = per-call

- The rule of thumb: **durable identity-and-policy content goes in `system`; per-call task content
  goes in `user`.** The system message is the part that is true on *every* call of this prompt.
- Why it matters two ways: (a) **reuse** — a lean, durable system message can front many different
  user requests unchanged; (b) **cost** — the system message is re-sent every turn, so bloat there
  is paid for forever (and it is exactly what *prompt caching*, a later L19 topic, exists to fight).
- diagram: two boxes — `system: "You are a triage assistant. Answer in two short paragraphs…"`
  (stamped "always true") and `user: "My head has hurt for three days."` (stamped "this call only").

### slide 2.3 The two mis-attribution footguns

- **Instructions buried in the user message** get re-sent and re-stated every turn — more tokens,
  and the policy competes with the actual request for the model's attention.
- **Per-call data crammed into the system message** *poisons reuse*: the system message stops being
  always-true, so the next user request inherits stale data (the model may answer about the *last*
  caller's problem).
- table: where each kind of content belongs.

| Content | Belongs in | Why |
| --- | --- | --- |
| Persona, tone, output format, standing policy | `system` | true on every call; enables reuse |
| This call's question, document, or data | `user` | changes every call |
| A worked example you're planting | `assistant` (or a labeled block in `user`) | see section 4 |

### slide 2.4 The system message is weighted, not enforced

- The model treats `system` as conversational context with a **privileged label** — it tends to
  follow it, but it is **not invulnerable** to instructions in user messages. Frame it as
  "always-true context," not "inviolable rules."
- Anything close to a **security or policy guarantee belongs outside the model** (in your code),
  not inside the system prompt. The system prompt is not a sandbox.
- Common confusion to kill now: *"the system message is enforced; the user can't override it."* No —
  strongly weighted ≠ enforced.

### slide 2.5 Multi-turn, and the first-call vs. Nth-call axis

- A multi-turn conversation is just appending alternating `user`/`assistant` messages and re-sending
  the **whole list**. Every continued turn re-bills the history (L01 staircase).
- **Prompt quality has a first-call vs. Nth-call axis:** a prompt that behaves on call 1 can
  *degrade* by call 5 as the model accumulates its own (sometimes flawed) prior turns. This is the
  first place students feel "the model got worse" with nothing obviously changed.
- Decide deliberately: **continue** when the history is load-bearing context; **start fresh** when
  it isn't, to dodge both the cost staircase and accumulated drift.

[↑ Back to top](#prompting-fundamentals-roles-structured-output-few-shot)

## section 3. Structured output: a negotiation, not a guarantee

### slide 3.1 Why ask for structure at all

- Structured output makes the model's response **programmatic** rather than **conversational** — a
  dict your code can index, not a paragraph you have to read.
- It is the precondition for almost everything later: evals (L12), tool calling (L07), and
  multi-step pipelines all need the model's output to be *machine-readable*.
- The shapes you'll ask for: a **JSON object**, a **fixed list of fields**, or **XML-ish tags**
  like `<answer>…</answer>`.

### slide 3.2 The L02 method: prompt-instruction-only

- In L02 we get structure **by instruction alone**: we *tell* the model the exact shape in the
  prompt ("Return a single JSON object with exactly these keys, no prose") and then parse the reply.
- diagram: prompt with an explicit schema spec → model reply (hopefully JSON) → `parse()` → dict.
- One-line foreshadow (do not teach here): *in production you'd use Anthropic's **tool-use-as-schema**
  to force schema-conformant output — that's L07. The parsing discipline below still applies there,
  because tool-call arguments can also be malformed.*

### slide 3.3 The model agrees to the contract; it does not enforce it

- Even when told "JSON only," the model can produce: **extra prose** around the JSON, **mismatched
  field names**, **missing required fields**, **wrong enum values it invented**, or an occasional
  **fully-malformed** blob.
- An **enum is a contract, not a constraint** — listing the allowed values asks the model to pick
  one; it does not stop the model from inventing a new one.
- The right mental model: **ask for structure, parse defensively, fail loudly on parse failure.**

### slide 3.4 The defensive parser

- The standard three-step parser:
  1. `json.loads` the whole reply — the happy path.
  2. On failure, **regex out the first `{...}` block** and retry — salvages JSON wrapped in prose.
  3. On failure again, **raise loudly** with the raw response in the error message.
- **Fail loudly, never silently.** A silent fallback (e.g. returning `{}` on parse failure) hides a
  bug that *compounds* downstream in agent loops (L10) and traces (L11). A logged, raised error is a
  diagnosis; a silent empty dict is a time bomb.
- Validate the *contents*, not just "did it parse": required keys present? enum value in the allowed
  set? You decide whether a missing optional field is `null`-tolerant or an error — and you decide
  it on purpose.

### slide 3.5 Temperature, verbosity, and cost for structured output

- Use **low temperature (≈0)** for extraction and classification — you want the single most-likely,
  repeatable answer, not creative variety (L01 callback).
- Ask for a **tight schema and no prose** — this typically *reduces* output tokens versus a chatty
  answer. Structured output is often a **cost win** as well as a parseability win (output is the
  expensive direction, L01).
- Keep input and output *shapes consistent*: a labeled, structured request yields cleaner structured
  output than the same request phrased in flowing English. Consistency reduces the model's degrees
  of freedom — and therefore the parse failures.

[↑ Back to top](#prompting-fundamentals-roles-structured-output-few-shot)

## section 4. Few-shot examples: a precision tool

### slide 4.1 What few-shot is — and isn't

- A **few-shot prompt** is a small number of input→output **example pairs** placed before the real
  input, to show the model the desired output shape or behavior.
- Few-shot is **behavior conditioning, not teaching.** The model's underlying capabilities don't
  change; you are shifting the *in-context distribution*. Frame it as **showing, not teaching**.
- Common confusion to kill: *"few-shot teaches the model new things."* No — it conditions this one
  call's behavior; nothing about the model is updated.

### slide 4.2 Two placements, one trade-off

- **Alternating fake turns:** plant each example as a `user` message (the example input) followed by
  an `assistant` message (the desired output). Surprising to students: the `assistant` role is the
  right home for fake "model said this" content.
- **Single block in the user message:** write all the examples as a labeled text block inside one
  `user` message, then the real input.
- Placement usually matters **less than content** — the two perform similarly. Pick whichever your
  downstream parser or cache strategy prefers.
- diagram: the two layouts side by side — left: `[user(ex1_in), assistant(ex1_out), user(ex2_in),
  assistant(ex2_out), user(real_in)]`; right: `[user("Examples:\n…\n\nNow classify: real_in")]`.

### slide 4.3 Diversity beats volume

- A few **well-chosen, contrasting** examples outperform many **similar** ones. Four examples
  covering four labels beat four examples of the same label.
- The failure mode to name: **"all examples look like the easy case."** A uniform example set makes
  the model **overfit to a surface pattern** — e.g. show four `P0-bug` examples and it starts calling
  everything a P0 bug.
- Distinguish **few-shot for format** (showing the desired output *shape*) from **few-shot for
  behavior** (showing the desired *judgment*). Both work; they fail differently.

### slide 4.4 Few-shot is priced on every call

- Each example consumes **input tokens on every single call** (L01 callback). Few-shot is a real
  **cost-vs-quality dial**, not a free improvement.
- It is also **editable**: every time you find a failing input, you can add an example that resembles
  it. That is its power *and* its trap — the list grows, the per-call cost grows, and at some point
  you should reach for a different tool.
- table: when few-shot is the right tool, and when it isn't.

| Situation | Reach for… |
| --- | --- |
| A single clear instruction already works | just the instruction — skip few-shot |
| The model needs the team's idiosyncratic format/labels | few-shot (for format) |
| The task needs *reasoning* steps, not pattern-matching | chain-of-thought — L06 |
| The example set would dominate the context window | a different approach (retrieval L21, model class L13, fine-tuning — out of scope) |

[↑ Back to top](#prompting-fundamentals-roles-structured-output-few-shot)

## section 5. The common single-step task shapes

### slide 5.1 One call, many shapes

- The three levers so far are *mechanics*. Point them at a goal and you get the everyday jobs a
  **single LLM call** does. Learn to **name the shape** — the name tells you which lever to reach for
  and, crucially, what to **validate**.
- The catalog is five shapes: **extraction**, **classification**, **ranking / recommendation**,
  **constrained generation**, **summarization / transformation**. Nothing here is a new technique —
  each is the three levers aimed at a different **output contract**.
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

- **Extraction is structured output (section 3) pointed at "pull these fields."** You already did it
  in the structured-output demo: name the fields, ask for one JSON object, parse defensively.
- **Single-schema:** a fixed set of keys every time (e.g. `customer_name`, `order_id`, `intent`).
- **Mixed-schema:** pull a *list* of heterogeneous items whose fields differ (e.g. line-items where a
  product row has `sku` + `qty` and a discount row has `code` + `percent`). Ask for a JSON array of
  objects and validate each item against the shape it claims to be.
- Failure to name out loud: the model **invents** a field it wasn't asked for, or **drops** one that
  was in the text — the required-keys check from section 3 is exactly what catches it.

### slide 5.3 Classification — sort into a fixed label set

- **Classification is structured output constrained to a label set** — and the place **few-shot
  (section 4)** most earns its keep, because a team's label *wording* is often idiosyncratic.
- Three flavours: **flat** (one of N labels), **hierarchical / taxonomy** (`category` then
  `subcategory` — ask for both keys), and **multi-label** (return a JSON *array* of labels when more
  than one applies).
- **An enum is a contract, not a constraint** (section 3 again): the model can return a label outside
  the set, so validate `label in ALLOWED` — and for a taxonomy, validate the subcategory belongs to
  the chosen category.
- diagram: an input ticket flowing into a flat label, then into a two-level `category → subcategory`
  pair, with the validator rejecting an out-of-set label.

### slide 5.4 Ranking / recommendation — order a candidate list

- **Give the candidates ids and ask the model to return the ids in order** — never ask it to rewrite
  the candidates. Referencing by id keeps the output tiny and the contract checkable.
- The contract to **validate**: every candidate id appears in the output **exactly once** — no drops,
  no duplicates, nothing invented. This is the classic silent failure: the ranking *looks* fine until
  you notice one item vanished.
- Optionally ask for a one-line justification per rank — useful, but it costs output tokens and is not
  the thing you validate.
- table: candidate list in, ordered id list out, validator preserving the set.

| Prompt gives | Model returns | Validator checks |
| --- | --- | --- |
| `[{id: 1, …}, {id: 2, …}, {id: 3, …}]` + a criterion | `[3, 1, 2]` | each id present exactly once |

### slide 5.5 Constrained generation — produce exactly N, within a bound

- Generation is the one shape where you may *want* a higher temperature — but the **constraint** (a
  count, a length cap, a required format) must be **explicit in the prompt and re-checked in code**.
- Ask for a **JSON array of length N** rather than a prose list — a shape you can `len()`-check beats
  counting bullet points by eye.
- The contract to validate: the count is exactly N, and each item respects the bound (e.g.
  `≤ 8 words`). **A constraint you don't check is a constraint the model is free to miss** — and it
  will, some runs.
- Failure to name: the model returns 4 or 6 items, or one item blows the length cap. The validator
  turns that into a caught error instead of a downstream surprise.

### slide 5.6 Summarization and the transformation family

- **Summarization, rewriting, normalization, translation** are one family: text in, *transformed* text
  out, **meaning preserved**. The **system message (section 2)** carries the durable policy — audience,
  length, register — because it is true on *every* call of this transformer.
- diagram: `system: "Summarize for a non-technical exec in one sentence."` + `user: <the document>`
  → a one-sentence summary; swap the system policy to restyle without touching the user text.
- The contract here is softer (there is no single right answer), so validation is about **guardrails,
  not equality**: length within bound, no invented facts, required elements present. Failure modes to
  name: **hallucinated additions** and **length drift**.
- Low temperature still helps for faithful summaries; lift it only for deliberately creative rewrites.

### slide 5.7 Picking the shape, and chaining shapes

- **Name the shape first.** "This is a classification problem" tells you to reach for a fixed label
  set, few-shot if the labels are idiosyncratic, and a `label in ALLOWED` validator — before you write
  a word of prompt.
- **Temperature by shape** (L01 callback): near-0 for extraction / classification / ranking (you want
  the single most-likely, repeatable answer); higher only where generation genuinely wants variety.
- **A hard task is usually a *pipeline* of these single steps** — extract, then classify, then
  summarize. That is exactly the seam **L03–L05** pick up, where each step becomes one **node** in a
  graph. L02 gives you the vocabulary of the single step; the graph ramp wires several together.

[↑ Back to top](#prompting-fundamentals-roles-structured-output-few-shot)

## section 6. Wrap-up and the bridge to L06

### slide 6.1 The three levers and the catalog, reconnected

- **Roles** decide *where* content lives and how the model weights it. **Structured output** decides
  the *shape* of the answer and forces you to parse defensively. **Few-shot** *nudges behavior* at a
  per-call token price.
- Those three levers are exactly what the **task catalog** (section 5) runs on: extraction and
  classification lean on structured output (and few-shot for odd labels); ranking and constrained
  generation add a checkable rule; summarization leans on the system message. Same toolkit, five
  output contracts.
- They interlock: a good prompt often uses all three — a lean `system` message, a `user` request
  that asks for a tight JSON shape, and a couple of diverse `assistant`/`user` examples when an
  instruction alone won't do it.
- The sentence to leave with: *you now know how to ask the model for what you want, in the shape you
  want.*

### slide 6.2 Where this goes next

- **Immediate next lesson: [L03](../../../../docs/origin/lesson_roadmaps/L03/objectives.md)
  (single-node operations).** It takes one task shape from section 5 — **extraction** — and wraps it as
  a reusable **graph node**: the same structured-output discipline, now living inside a
  framework-managed function. L03–L05 then chain several single-step shapes into a graph.
- **Later: L06 (reasoning).** The three levers are also what L06 builds chain-of-thought on — that
  hand-off is the next slide.

### slide 6.3 What L06 does with this

- L06 (teaching an LLM to think) sends its chain-of-thought prompts through **the same role
  structure** you just learned — a `system` message that licenses reasoning plus a `user` message
  with the problem.
- L06's `<thinking>…</thinking><answer>{…}</answer>` pattern is **a specific use of structured
  output** (section 3): the parser pulls the answer out and optionally logs the thinking. The same
  defensive-parsing discipline carries over — `<answer>` blocks can be malformed too.
- L06's worked-example chain-of-thought is **a specific use of few-shot** (section 4), where each
  example pair *also* includes the reasoning trace. You saw few-shot as a generic technique here;
  L06 shows one application.
- The hand-off sentence: *L06 is about making the model think harder before it answers — built
  entirely on the three levers you now own.*

[↑ Back to top](#prompting-fundamentals-roles-structured-output-few-shot)
