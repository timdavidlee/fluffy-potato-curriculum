# Designing good tools: name, schema, and error as interface

```yaml
title: Designing good tools: name, schema, and error as interface
keywords: tool design, tool description, json schema, parameter schema, validation errors, recoverable errors, unrecoverable errors, idempotency, side effects, tool soup, tool-or-no-tool, anthropic, claude
estimated duration: 80
```

> **Lesson:** L08. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L08/objectives.md).
> This is the written reference lecture — thorough on purpose, so a student who missed the verbal
> delivery can rebuild the lesson from the page. The live demos are split one per concept
> ([L0803](L0503_lecture.ipynb) tool-or-no-tool, [L0805](L0505_lecture.ipynb) the description,
> [L0807](L0507_lecture.ipynb) schemas + validation errors, [L0809](L0509_lecture.ipynb) errors &
> side effects); hands-on practice is in the L08 labs (L0804 / L0806 / L0808 / L0810).
> **Anchor model throughout: Claude Sonnet 4.6** (one Haiku 4.5 contrast in L0805).

## section 1. The lesson in one claim

### slide 1.1 From making a tool work to making a tool good

- L07 settled the *mechanics*: how a single tool wires to a model call, the round-trip on the wire,
  the protocol the model and runtime use to negotiate a call. By the end of L07 you can make a tool
  *work*.
- L08 is about a different thing entirely: making a tool *good*. The protocol is fixed — the open
  questions are *what to expose, how to name and shape it, and how to fail gracefully*.
- The whole lesson rests on one claim: **a tool is an API designed for an LLM consumer, not a human
  consumer.** The model has no IDE, no autocomplete, no Stack Overflow, no co-worker to ask. Its
  entire understanding of the tool is the name, the description, the parameter schema, and what comes
  back.

### slide 1.2 Why the LLM-consumer framing changes everything

- A human API client reads docs, experiments in a REPL, and asks a co-worker when stuck. The model
  does none of that. It reads the tool *spec* once, at inference time, and decides on the spot whether
  and how to call it.
- So every design choice optimizes for **the model's ability to choose and use the tool correctly on
  first read** — not for the human author's ergonomics.
- diagram: two columns — "Human consumer (IDE, autocomplete, docs, co-worker)" vs "LLM consumer (name
  + description + schema + return shape, read once)" — with an arrow noting the model has only the
  right column.

### slide 1.3 The four judgment calls, in one breath

- table: the four design decisions L08 builds, the one sentence each lands, and the demo + lab that
  drills it.

| Decision | The mental model | Demo / lab |
| --- | --- | --- |
| Tool, or no tool? | adding a tool is architecture, not convenience | [L0803](L0503_lecture.ipynb) / L0804 |
| The description is the tool | same name + schema, different description → different behavior | [L0805](L0505_lecture.ipynb) / L0806 |
| Schemas are a contract | a tight schema converts ambiguity into recoverable errors | [L0807](L0507_lecture.ipynb) / L0808 |
| Errors are the interface | an error is a prompt for the model's next turn | [L0809](L0509_lecture.ipynb) / L0810 |

[↑ Back to top](#designing-good-tools-name-schema-and-error-as-interface)

## section 2. Tool, or no tool?

### slide 2.1 Adding a tool is an architectural decision

- The set of tools the model has access to *is* the set of actions it can take in the world. Adding a
  tool is not a convenience — it is a decision about the agent's affordances.
- It also has a cost shadow ([L01](../L01/L0101_intro.md)): every tool eats system-prompt tokens,
  adds a per-turn decision, and adds another wrong-tool failure mode. *More tools ≠ more capable
  agent.* A 5-tool agent the model can navigate beats a 20-tool agent it gets lost in.

### slide 2.2 Four signals a tool *is* warranted

- table: the four "reach for a tool" signals from [objectives.md](../../../../docs/origin/lesson_roadmaps/L08/objectives.md),
  each with a one-line tell.

| Signal | The tell |
| --- | --- |
| Data the model can't have memorized | current time, user-specific state, recent events |
| Precise computation the model is bad at | large arithmetic, exact date math, hashing |
| A side effect outside the conversation | sending email, writing to a DB, calling an external API |
| Verification against ground truth | database lookup, fact retrieval |

- The subtle one is *computation the model is bad at*: the model **will** attempt it, confidently, and
  be wrong. The tool isn't filling a gap the model knows about — it's filling a gap the *designer*
  knows about.

### slide 2.3 Two signals *no* tool is needed

- **The model already knows it, reliably.** "What is the capital of France?" — a tool here is pure
  overhead and gives the model a wrong-tool option to pick by mistake.
- **The round-trip costs more than the marginal accuracy.** If the tool buys a tiny accuracy gain at
  the price of a full extra call + latency, skip it.
- The discipline: **run the task model-alone first**, see where it actually fails, and add a tool only
  where the failure is real. [Demo 1](L0503_lecture.ipynb) does exactly this across three tasks; the
  [L0804 lab](L0504_lab_empty.ipynb) has you classify a table of tasks and defend each call.

### slide 2.4 The worked test

- For any task, ask: *does the answer depend on data I can't have memorized, need precise computation,
  cause a side effect, or require verification?* If yes → tool. If the model nails it cold and the
  round-trip isn't worth it → no tool.
- Then **defend the call in one sentence.** "Tool: needs the live clock." / "No tool: general
  knowledge the model has cold." That one sentence is the deliverable — naming *why* is the skill.

[↑ Back to top](#designing-good-tools-name-schema-and-error-as-interface)

## section 3. Name and description: the model's only training signal

### slide 3.1 The name is read in isolation

- The model sees the tool **name without surrounding context**. So the name must be descriptive,
  action-oriented, and unambiguous on its own.
- Anti-patterns: cryptic abbreviations (`lu`, `gx2`), overlapping names across tools (`get_user` and
  `fetch_user` in the same registry), and — worst — **names that hide a side effect** (`get_user`
  that also *creates* one). A name that lies about what the tool does is a tool that will be misused.

### slide 3.2 The description is the most important field

- Names are constrained by length and convention; schemas are constrained by types. The **description
  is freeform prose** — it is the only place to teach the model *when* to reach for the tool and *when
  not to*.
- It is the model's **only training signal at inference time** for tool selection. Treat it like the
  system prompt of a tiny sub-policy: it has to land its point in a few sentences.
- A weak description is the single most common cause of an unused or a misused tool.
  [Demo 2](L0505_lecture.ipynb) makes this concrete — same name, same schema, three descriptions,
  three very different behaviors.

### slide 3.3 What a good description must answer

- A description is two things at once: a **recruitment ad** (when to reach for the tool) and a
  **contract** (what it returns). It must answer, concretely:
  - *What does this tool do?*
  - *When should the model reach for it — and when should it not?*
  - *What does it return* (the shape, so the model can plan its next turn)?
- diagram: a single tool description annotated with four call-outs — "what it does", "when to use",
  "when NOT to use", "what it returns" — over the same block of prose.

### slide 3.4 Write for the model, not the human reader

- The audience is the model's **selection step at inference time** — not the human reading the source.
  Code comments are for humans; tool descriptions are for the model.
- A common confusion: *"the description is for whoever reads the code."* No — it's the prompt the model
  reads to decide. Write it short, concrete, examples included.
- A description that **overstates** the tool (promises billing + history when the tool returns only a
  name) is as harmful as one that says too little: the model calls it expecting rich data and is
  confused by the thin response. Match the description to the implementation exactly.

[↑ Back to top](#designing-good-tools-name-schema-and-error-as-interface)

## section 4. The parameter schema is a contract

### slide 4.1 The model is a fuzzy producer of structured output

- Back-reference [L02](../L02/L0201_intro.md): the model produces structured output *best-effort*, not
  guaranteed. A schema is how you turn that fuzziness into something correctable.
- A **tight schema** — required fields, narrow types, enums where the value space is small, per-field
  descriptions — converts ambiguity into **validation errors the model can fix on the next turn**.
- A **loose schema** (one free-form `details: str`, everything optional) pushes the ambiguity *into
  the tool implementation*, which then rejects calls in ad-hoc ways the model can't anticipate — or,
  worse, silently "succeeds" on a malformed call.

### slide 4.2 The pieces of a good schema

- table: the schema levers and what each one buys you.

| Lever | What it buys |
| --- | --- |
| Typed parameters | the model knows `int` vs `str` vs `bool` up front |
| Required vs optional | required fields force the missing detail into the open |
| Enum constraints | a small value space the model can't misfill (`"low" \| "med" \| "high"`) |
| Per-parameter descriptions | the model's only source of truth for what a param *means* |

- **Rule of thumb:** every parameter description should include an **example or a constraint**
  (`"RFC 5322 email, e.g. 'tim@example.com'"`, `"integer between 15 and 240"`). The model has no other
  source of truth for the parameter.

### slide 4.3 Schemas validate shape, not truth

- A tight schema catches *malformed* arguments (`duration_minutes: 500` when the max is 240). It does
  **not** catch *false* arguments — a syntactically valid but fabricated `priya@example.com` passes
  email-format validation even if no such user exists.
- This is exactly why **errors** (section 6) matter as a second line of defense: the schema rejects bad
  *shape*; the tool's runtime errors reject bad *truth*. [Demo 3](L0507_lecture.ipynb) shows the model
  guessing a well-formed-but-fake value that passes validation and only fails at lookup.

### slide 4.4 The two extremes to avoid

- **Too-specific tools** → "tool soup": one tool per narrow use case, so the model has twenty
  near-identical options to pick through and picks wrong.
- **Too-generic tools** → the kitchen sink: a single tool with twenty parameters the model
  misconfigures.
- diagram: a dial from "20 narrow tools (tool soup)" on the left through "a focused 5-tool set" in the
  middle to "1 tool, 20 params (kitchen sink)" on the right, with the middle marked "navigable".
- **LLM tools ≠ REST endpoints.** REST conventions optimize for human readability and HTTP semantics;
  LLM tools optimize for *being chosen and called correctly from a description*. A `GET /users/{id}`
  and a `POST /users` may collapse into one LLM tool with an `action` parameter — or split differently.
  There is no universal rule; the right grouping is the one a model can navigate without confusion.

[↑ Back to top](#designing-good-tools-name-schema-and-error-as-interface)

## section 5. The return shape

### slide 5.1 Distinguish three outcomes cleanly

- The model branches on the *next turn* based on what the tool returned. So the return shape must let
  the model tell apart:
  - **Successful result** — here is the data.
  - **Successful call, no data** — the call worked, but there's nothing to return (e.g. a lookup with
    no match). This is **not** an error.
  - **Error** — the call could not be completed.
- diagram: three branches off a tool call — `{"results": [...]}`, `{"found": false}`,
  `{"error": ...}` — each leading to a different model next-turn.

### slide 5.2 Why "no data" must not look like an error

- If "no user found" returns the same shape as "lookup crashed", the model can't tell whether to retry
  (it might be transient) or to report (it's final). Conflating them produces undefined behavior.
- A clean `{"found": false}` is a *final, unrecoverable* signal — the model reports back or asks for a
  better key, and does **not** retry. [Demo 4](L0509_lecture.ipynb) shows this path explicitly.

[↑ Back to top](#designing-good-tools-name-schema-and-error-as-interface)

## section 6. Errors are part of the interface

### slide 6.1 The model treats an error as new context, not an exception

- When a tool returns an error, the model's next turn is **conditioned on that error text** — exactly
  like any other context. A well-shaped error teaches the model to fix its call; a bare exception
  teaches it nothing and it guesses, often wrongly.
- The principle: **errors should be informative for the model, not just for a human debugger.** A
  stack trace dumped into the tool result tells the model nothing actionable.

### slide 6.2 Three error classes and their handling

- table: the three error classes from [objectives.md](../../../../docs/origin/lesson_roadmaps/L08/objectives.md)
  and the model behavior each should produce.

| Class | Example | The error should… | Model behavior |
| --- | --- | --- | --- |
| **Validation** | bad arguments | name the field + the constraint | correct the field and retry |
| **Recoverable runtime** | rate limit, timeout, transient API failure | signal "try again" without burning budget | retry (or runtime retries silently) |
| **Unrecoverable** | entity doesn't exist, no permission, impossible action | be clear and **final** | stop retrying; report or route around |

- The shape of the error *is* the interface. An undocumented error class produces **undefined model
  behavior** — so add expected error shapes to the tool description.

### slide 6.3 Write the error like a system message

- Bad: `Traceback (most recent call last): ... KeyError: 'user_id'`. The model learns nothing
  actionable and retries with the same wrong call.
- Good: `{"error": "validation", "field": "user_id", "message": "must be a UUID, got 'tim@example.com'"}`.
  The model knows *which* field, *why* it was rejected, and *how* to fix it.
- diagram: the same failing call, two error returns side by side — a greyed-out stack trace ("model:
  ¯\\_(ツ)_/¯") vs a structured `{error, field, message}` ("model: oh, I'll pass a UUID").
- The [L0808 lab](L0508_lab_empty.ipynb) has you take raw stack traces and rewrite each into an
  informative `{error, field, message}` payload — pure Python, no model needed.

[↑ Back to top](#designing-good-tools-name-schema-and-error-as-interface)

## section 7. Idempotency and side effects

### slide 7.1 The model will retry on its own

- When a result looks ambiguous, the model **retries — regardless of whether retry is safe.** You
  cannot rely on the model to know a call is dangerous to repeat.
- So idempotency is a *system* concern, not just a tool-author concern. Even a perfectly described
  tool can be called twice by a confused model.

### slide 7.2 Safe-to-retry vs. not

- table: which tools tolerate retry and which don't.

| Safe to retry | Not safe to retry |
| --- | --- |
| read-only lookups | sending a message |
| pure computations | charging a card |
| idempotent upserts (with a key) | creating a record (without a key) |

- Mitigations for non-idempotent tools (apply at least one): **idempotency keys** passed by the
  runtime, an **explicit confirmation step**, or a **tool description that warns** the model not to
  retry on a success-with-no-result response.

### slide 7.3 Name every side effect in the description

- A side effect that isn't named in the description is a side effect the model **can't reason about —
  and therefore can't avoid.** Naming it isn't paranoia; it's part of the contract.
- [Demo 4](L0509_lecture.ipynb) shows a `lookup_user_by_email` that *also silently creates* a user:
  the model fires it, a record is created it never intended, because the description hid the effect.
  Add one sentence — *"if the user does not exist, this tool creates one"* — and the model pauses to
  ask first.
- Forward link: **L14 (human-in-the-loop / approval gates)** revisits this exact tension for
  high-stakes side effects. L08 plants the seed; L14 builds the structure.

[↑ Back to top](#designing-good-tools-name-schema-and-error-as-interface)

## section 8. Common confusions to leave behind

### slide 8.1 The five traps

- table: the recurring student confusions from [objectives.md](../../../../docs/origin/lesson_roadmaps/L08/objectives.md)
  and the correction for each.

| Confusion | The correction |
| --- | --- |
| "More tools = more capable agent" | usually the opposite — each tool dilutes attention and adds a failure mode |
| "The description is for the human reading the code" | it's for the model's selection step at inference time |
| "Errors should be hidden from the model" | errors are how the model learns to recover within the conversation |
| "A schema is just for type-checking" | it's also a teaching tool — shape + per-field descriptions guide the model |
| "My tool worked once, so the design is fine" | one clean round-trip barely tests it; design pays off under pressure |

[↑ Back to top](#designing-good-tools-name-schema-and-error-as-interface)

## section 9. Bridge to L09

### slide 9.1 The design survives the packaging change

- L09 introduces **MCP (Model Context Protocol)**, a portable packaging format that lets the *same*
  tool be exposed to many clients without rewiring.
- Everything L08 teaches — naming, descriptions, schemas, error shapes, idempotency — applies
  **unchanged** to an MCP tool. MCP standardizes only the *transport* and the *discovery* layer, not
  the design pressures.
- A poorly designed tool exposed via MCP is still a poorly designed tool — just available to more
  clients. L09 leans on the L08 vocabulary throughout.

### slide 9.2 What to carry forward

- **Name + description + schema + error shape** → these *are* an MCP tool spec; the packaging changes,
  the design work does not.
- **Idempotency and side effects** → still a runtime concern in an MCP world, and still must be named
  in the description.
- One sentence to L09: *you can now design a tool a model uses well; next you'll package that same
  design so any client can use it.*

[↑ Back to top](#designing-good-tools-name-schema-and-error-as-interface)
