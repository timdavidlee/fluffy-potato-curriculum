# L08: Designing good tools

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (lesson-plan row L08).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).

## Where this lesson sits

L07 covered the *mechanics* of tool calling: how a single tool is wired to a model call, what the tool-call round-trip looks like on the wire, and the protocol the model and runtime use to negotiate a call. By the end of L07 a student can make a tool work.

L08 takes the next step: making a tool *good*. The protocol is settled — now the open question is what to expose, how to name and shape it, and how to fail gracefully when the world disagrees with the model. This is the first lesson in the course where the student designs an *interface for an LLM to consume* rather than for a human to consume, and the design pressures are different.

L08 is the last lesson before L09 (MCP), where the same tool design choices get packaged as a portable contract across clients. Everything from L08 — naming, schemas, errors — carries forward; L09 only changes the *transport*, not the design pressures.

## Prerequisites

Students arriving at L08 should already be able to:

- Wire a single tool to a model call and execute one round-trip end-to-end (L07).
- Describe the tool-call protocol — what the model sends to request a tool, what shape the runtime must send back (L07).
- Trace a single tool-call round-trip and identify each phase: model emits a tool-use request, runtime executes the tool, runtime returns the tool result, model continues (L07).
- Request structured output from a model and parse it (L02), since tool schemas are a special case of structured-output contracts.
- Reason about reasoning steps as token-level decisions (L06) — choosing *whether* to call a tool is itself a reasoning step.

If a student is shaky on the L07 mechanics, redirect to the L07 lab before continuing. L08 assumes the wiring works and focuses entirely on design.

## Learning objectives

By the end of L08, a student should be able to:

1. **Decide when a tool is needed vs. when the model can answer alone.** Concretely:
   - Name at least four signals that a tool is warranted: the answer depends on data the model can't have memorized (current time, user-specific state, recent events), the answer requires precise computation the model is bad at (large arithmetic, exact date math, hashing), the action has a side effect outside the conversation (sending email, writing to a database, calling an external API), or the answer requires verification against ground truth (database lookup, fact retrieval).
   - Name at least two signals that *no* tool is needed: the model already has the knowledge with high reliability, or the cost of a tool round-trip exceeds the value of the marginal accuracy gain.
   - Apply the test on a worked example: given a task description, decide tool-or-not and defend the choice in one sentence.

2. **Name and schema-design a tool.** Concretely:
   - Choose a tool name that is descriptive, action-oriented, and unambiguous when read in isolation (the model sees the name without surrounding context). Recognize anti-patterns: cryptic abbreviations, overlapping names across multiple tools, names that hide side effects (`get_user` that also creates one).
   - Write a tool **description** aimed at the model — not the human reader. The description must answer: *what does this tool do, when should the model reach for it, when should it not, what does it return.* Recognize that this description is the model's only training signal at inference time for *when* to use the tool.
   - Design the **parameter schema**: typed parameters, required vs. optional, enum constraints where the value space is small, per-parameter descriptions. Apply the rule of thumb that every parameter description should include an example or a constraint, since the model has no other source of truth for what the parameter means.
   - Decide the **return shape**: a stable, structured value the model can consume on the next turn. Distinguish "successful result" from "successful call but no data" from "error" cleanly enough that the model can branch on it.
   - Recognize the two extremes to avoid: *too-specific tools* (one tool per narrow use case → "tool soup" the model has to pick through) and *too-generic tools* (a single kitchen-sink tool with twenty parameters → the model misconfigures it).

3. **Handle tool errors so the model can recover.** Concretely:
   - Distinguish three error classes and their handling:
     - **Validation errors** (the model passed bad arguments) — return a structured error message that names the offending field and the constraint, so the model can correct on the next turn.
     - **Recoverable runtime errors** (transient API failure, rate limit, timeout) — return an error that signals "try again" without burning a permanent budget, and decide whether the *runtime* retries silently or surfaces the error to the model.
     - **Unrecoverable errors** (the requested entity does not exist, the user lacks permission, the action is impossible) — return a clear, final error so the model stops retrying and either reports or routes around the failure.
   - Recognize that errors are part of the tool's *interface*: an undocumented error class will produce undefined model behavior. Add expected error shapes to the tool description.
   - Apply the principle: *tool errors should be informative for the model, not just for a human debugger.* A stack trace dumped into the tool result tells the model nothing actionable. A message like `"error: 'user_id' must be a UUID, got 'tim@example.com'"` tells the model exactly how to retry.

4. **Reason about idempotency and side effects.** Concretely:
   - Identify which tools are safe to retry (read-only lookups, pure computations) and which are not (sending a message, charging a card, creating a record). Recognize that the model *will* retry on its own when a result looks ambiguous, regardless of whether retry is safe.
   - Apply at least one mitigation for non-idempotent tools: idempotency keys passed by the runtime, explicit confirmation steps, or a tool description that warns the model not to retry on success-with-no-result responses.
   - Surface side effects in the tool description so the model can reason about them before calling. A tool whose name and description hide its side effect is a tool that will be misused.

## Main points the lecture should land

- **A tool is an API designed for an LLM consumer, not a human consumer.** The model has no IDE, no autocomplete, no Stack Overflow, no co-worker to ask. Its entire understanding of the tool comes from the name, description, parameter schema, and the few examples it has seen during training. Every design choice should optimize for *the model's ability to choose and use the tool correctly on first read*, not for the human author's ergonomics.
- **The tool description is the most important field.** Names are constrained by length and convention; schemas are constrained by types. The description is freeform prose that teaches the model *when* to reach for the tool and *when not to*. A weak description is the single most common cause of an unused or misused tool. Treat the description like the system prompt of a tiny sub-policy: it has to land its point in a few sentences.
- **Schemas are a contract, not a suggestion.** The model is a fuzzy producer of structured output (back-reference L02). A tight schema — required fields, enums, narrow types — converts ambiguity into validation errors the model can correct on the next turn. A loose schema (everything optional, free-form strings) pushes the ambiguity into the tool implementation, which then has to reject calls in ad-hoc ways the model can't anticipate.
- **The model treats tool errors as new context, not as exceptions.** When a tool returns an error, the model's next turn is conditioned on that error message. A well-shaped error ("missing required field `user_id`") teaches the model to fix its call. A bare exception or a 500 with no detail teaches the model nothing — it will guess, often wrongly.
- **Designing tools is designing the agent's affordances.** The set of tools the model has access to is the set of actions it can take in the world. Adding a tool is an architectural decision, not a convenience. A 20-tool agent that could be a 5-tool agent is harder for the model to navigate (longer system prompt, more decisions per turn, more chances to pick wrong) and harder for the author to maintain. L08 is where students start treating the tool list as a designed surface, not a grab bag.
- **Designing for an LLM consumer ≠ designing for a human REST client.** REST conventions optimize for human readability and HTTP semantics; LLM tools optimize for being chosen and called correctly from a description. Common REST patterns (separate `GET /users/{id}` and `POST /users`) often collapse into one LLM tool with a clear `action` parameter, or split differently than they would in a human-facing API. There is no universal rule; the right grouping is the one a model can navigate without confusion.

## Common student confusions to watch for

- *"More tools = more capable agent."* Usually the opposite. Each additional tool dilutes the model's attention across the tool list, eats system-prompt tokens (back-reference L01 on context-window cost), and adds another wrong-tool failure mode. A focused tool set beats a sprawling one.
- *"The tool description is for the human reading the code."* It's for the model. The audience is the LLM's selection step at inference time. Write it accordingly — short, concrete, examples included.
- *"Errors should be hidden from the model."* The opposite: errors are how the model learns to recover within the conversation. Hide errors and the model retries blindly with the same wrong arguments.
- *"A schema is just for type-checking."* It's also a teaching tool. The shape and per-field descriptions tell the model what's expected — often more reliably than the top-level description alone.
- *"My tool worked once, so the design is fine."* A tool used in one round-trip on a clean input is barely tested. Tool design pays off (or fails) under pressure: ambiguous user requests, model retries, partial failures. The L08 lab is where that pressure shows up.

## Bridge to L09

L09 introduces MCP (Model Context Protocol), which is a portable packaging format for tools that lets the same tool be exposed to many clients without rewiring. Everything L08 teaches about tool design — naming, descriptions, schemas, error shapes, idempotency — applies unchanged to MCP tools; MCP only standardizes the *transport* and the *discovery* layer. A poorly designed tool exposed via MCP is still a poorly designed tool, just available to more clients. L09 will lean on the L08 vocabulary throughout.

## Open authoring questions

- <!-- *NEED INPUT*: estimated lecture duration — best guess 60–90 minutes as one lecture covering all four subgoals, with a separate lab block. Or split into two: design (subgoals 1–2) and robustness (subgoals 3–4)? -->
- <!-- *NEED INPUT*: which model(s) the L08 demos and labs target — the "tool description quality" demos land differently across model classes. Pin once the course-wide model choice is settled in CURRICULUM_PRD. -->
- <!-- *NEED INPUT*: should L08 introduce the concept of *tool composition* (one tool's output feeding the next call's input), or defer that to L10 (hand-rolled agent loop) where the loop makes composition first-class? -->
- <!-- *NEED INPUT*: how deep on the schema spec — JSON Schema fully, or just the subset Anthropic's tool-use API actually validates? Affects how much time the lecture spends on schema syntax vs. design principles. -->
- <!-- *NEED INPUT*: is "describing side effects in the tool description" enough, or should L08 also introduce a notion of *typed* side effects (read vs. write vs. external) that the runtime can reason about? The latter foreshadows L17 (human-in-the-loop approval gates), so a forward link may suffice. -->
- <!-- *NEED INPUT*: does the L08 lab use a fresh tool the student designs from scratch, or extend the L07 lab's tool with a richer schema and error handling? The former teaches design end-to-end; the latter shows refactoring an existing tool, which is closer to real practice. -->
- <!-- *NEED INPUT*: any specific L07 labs that must be completed before this lesson is taught, beyond the prerequisite skills above? -->
