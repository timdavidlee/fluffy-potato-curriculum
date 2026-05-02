# L05: Teacher-led demos — Designing good tools

> Sibling docs: [objectives.md](objectives.md) (what the lesson aims for), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md).
>
> **Audience for this file:** the teacher running L05. Every demo below is *teacher-driven, no student participation*. Student-driven exercises live in the L05 labs (separate file).

## How to read this file

Each demo is a self-contained block with:

- **Goal** — the single insight the demo should land. Tied to a learning objective from [objectives.md](objectives.md).
- **Pre-flight** — what the teacher needs loaded before class.
- **Live script** — the order of operations during the demo. Treat it as a checklist, not a teleprompter.
- **What to highlight** — the moment(s) where the teacher should slow down and call out the takeaway out loud.
- **If the demo misbehaves** — graceful fallback for when the model surprises you (because it will).

The demos are ordered to match the four learning objectives from [objectives.md](objectives.md). Demo 4 (idempotency / side effects) builds on Demo 3 (errors), so run the sequence in order on the first delivery of the lesson.

## Pre-flight (once, at the top of the lesson)

The teacher should have, before the first demo starts:

- A working REPL or notebook with the project's Claude SDK setup (per the project's `uv` env).
- A small **demo harness** that wraps every model call to print: the model's tool-use request (name + arguments), the tool result (or error) handed back, the next model turn, and per-call `input_tokens` / `output_tokens` / wall-clock time. This is the same kind of wrapper used in [L03's demos](../L03/demos_or_activities.md), extended to also surface the tool call/result pair. Without this wrapper, the L05 demos read as "the model did something" instead of "the model picked *this* tool with *these* arguments because of *that* description."
- All four demo tools below pre-implemented as Python functions, registered with the SDK, and ready to swap in/out by name. Each demo intentionally swaps the *same* tool's description, schema, or error shape — *not* the implementation — so the contrast lands cleanly.
- A second tool registry pre-loaded with the **bad-design variants** (cryptic name, sparse description, loose schema, opaque errors). The teacher should be able to flip between "good" and "bad" registries with a single line.
- A way to display the active tool's full schema (name, description, parameter list with descriptions) on screen alongside the model's output — so the audience sees what the model is reading when it decides to call the tool.

> Why pre-built variants: L05 lives or dies on contrast — same task, same model, *different tool design*, different model behavior. Editing tool descriptions live during the demo eats time and breaks pacing. Have the variants ready.

<!-- *NEED INPUT*: which model class anchors the demos — the "description quality" and "schema design" demos land more sharply on a smaller model where the design errors bite harder. Best guess Sonnet 4.6 as the primary, with one Demo 2 re-run on Haiku 4.5 to show the gap widens. Pin once the course-wide model choice is settled in CURRICULUM_PRD. -->

## Demo 1 — Tool or no tool? (Objective 1)

**Goal:** show that the same task can be answered model-alone or with a tool, and that the right call depends on the kind of question. Land the framing from [objectives.md](objectives.md): *tool design starts with the decision to add a tool at all.*

**Pre-flight:**

- Three task prompts pre-loaded:
  - **Task A — model has it cold:** a general-knowledge question the model nails zero-shot (e.g. *"What is the capital of France?"*). Adding a tool here is pure overhead.
  - **Task B — model can't have it:** a question that depends on data the model can't have memorized (e.g. *"What is the current time in Tokyo?"* or *"What's the weather in Seattle right now?"*). The model has no choice but to guess or refuse without a tool.
  - **Task C — borderline:** an arithmetic problem at the edge of model reliability (e.g. *"What's 18,374 × 92,431?"* or *"How many days between 1987-03-12 and 2024-11-04?"*). The model often produces a wrong answer with confidence — exactly the case where a tool is warranted even though the model *will* attempt it.
- A single `calculator(expression: str) -> str` tool and a single `current_time(tz: str) -> str` tool, both with clean designs. Save the design walkthrough for Demo 2 — here the tools are just props.

**Live script:**

1. Run Task A model-alone. Note: instant, free, correct. Run Task A *with* the calculator tool registered. The model usually answers without calling the tool — point that out (good model, no tool needed). If it does call the tool, the result is the same answer at higher cost.
2. Run Task B model-alone. The model either refuses, hedges ("I don't have access to real-time data"), or hallucinates a time. Run Task B with `current_time` registered. The model calls the tool, gets the real answer, returns it.
3. Run Task C model-alone three times. Show the answers — often inconsistent across runs, sometimes wrong. Run Task C with `calculator` registered. The model calls the tool, gets a deterministic right answer.

**What to highlight:**

- The four "tool warranted" signals from [objectives.md](objectives.md) — data the model can't memorize (B), precise computation it's bad at (C), side effects (not in this demo, foreshadow), verification against ground truth (foreshadow Demo 4). Name the signals as they appear.
- The "no tool needed" cases (A): adding a tool to a task the model already handles wastes round-trips and tokens, and gives the model a wrong-tool option to pick by mistake.
- Task C is the subtle one: the model *will* answer without the tool, and confidently. The tool isn't there to fill a gap the model knows about — it's there to fill a gap the *designer* knows about.

**If the demo misbehaves:**

- If the model nails Task C zero-shot on the day, swap to a harder arithmetic problem (more digits) or a date-math problem with a leap year. Have one in reserve.
- If the model on Task A insists on calling the calculator anyway, lean into it: this previews the "tool soup" failure mode in Demo 2 — too many tools, too eager a hand.

## Demo 2 — The description is the tool (Objective 2)

**Goal:** show that the same tool, with the same name and schema, behaves differently depending on the description the model reads. Land the framing from [objectives.md](objectives.md): *the description is the model's only training signal at inference time for when to use the tool.*

**Pre-flight:**

- One tool implementation: `lookup_user(query: str) -> dict` that returns user records from a tiny in-memory dict (3–5 fake users keyed by both email and username).
- Three description variants of the same tool:
  - **Sparse:** `"Looks up a user."` — no guidance on when to call, what `query` accepts, what comes back.
  - **Rich:** a 3–5 sentence description that names the tool's purpose, lists the accepted query formats with examples (`"e.g. 'tim@example.com' (email) or 'tim_lee' (username)"`), states the return shape, and names when *not* to call the tool (e.g. "do not call this if the user has not been mentioned by name in the conversation — ask the user instead").
  - **Misleading:** a description that overstates the tool's capabilities (e.g. *"Looks up any information about any user — email, billing, preferences, history."*) when the implementation only returns a name and email. This previews how a description-implementation mismatch produces hard-to-debug failures.
- Two test prompts:
  - **Prompt P1:** *"Find me the email for the user named Alex."* — straightforward case, all three descriptions should produce a tool call.
  - **Prompt P2:** *"Tell me about our users."* — ambiguous case. Sparse description: model often calls the tool with garbage queries. Rich description: model usually asks for clarification or refuses. Misleading description: model calls the tool expecting rich data and is then confused by the thin response.

**Live script:**

1. Show all three descriptions side-by-side on screen. Read them aloud. Ask the audience (rhetorically) to predict which produces the best tool use.
2. Run P1 with the sparse description. Note tool args and result.
3. Run P1 with the rich description. Note: usually tool args are formatted more precisely (e.g. uses the example format from the description).
4. Run P2 with each description in turn. Show how model behavior diverges — sparse leads to bad arguments, rich leads to clarification or refusal, misleading leads to confused follow-up.
5. Run P1 once with the misleading description, then immediately follow up with: *"Now show me their billing history."* The model often tries to call the same tool again expecting more data, because the description promised it.

**What to highlight:**

- Same tool, same model, same task — only the *description* changed. Behavior changed dramatically.
- A description is two things at once: a *recruitment ad* (when to reach for the tool) and a *contract* (what the tool will return). Mismatches in either dimension cascade into bad calls.
- The audience to write *for* is the model's selection step at inference time — not the human reader of the source code. Comments in code are for humans; tool descriptions are for the model.
- This is also where students should start to feel that designing tools is *prompt engineering* (back-reference [L02](../L02/objectives.md) when that roadmap exists, and [L03](../L03/objectives.md) on token-level reasoning).

**If the demo misbehaves:**

- If P2 with the sparse description happens to produce a clean call, re-run with a slightly more ambiguous prompt (*"Look up our customers"*). The lesson is the *distribution* of behavior, not a single run — if the first run is clean, do a second to show it isn't.
- If the rich-description variant calls the tool with garbage anyway, point out that descriptions reduce variance, not eliminate it. This sets up Demo 3's schema discussion (validation as a second line of defense).

## Demo 3 — Schemas as a teaching tool (Objective 2 + 3)

**Goal:** show that a tight schema produces structured validation errors the model can recover from on the next turn, while a loose schema pushes the ambiguity into runtime failures the model can't interpret. Land the framing from [objectives.md](objectives.md): *errors are part of the tool's interface.*

**Pre-flight:**

- Two schema variants of a `book_meeting` tool:
  - **Loose:** `book_meeting(details: str) -> str` — one free-form string parameter.
  - **Tight:** `book_meeting(attendee_email: str, start_iso: str, duration_minutes: int, title: str) -> dict` — typed, all required, with per-parameter descriptions specifying formats (RFC 5322 email, ISO 8601 datetime, integer between 15 and 240).
- Two error-handler variants on the *tight* tool, swappable:
  - **Informative errors:** validation errors return `{"error": "validation", "field": "<name>", "message": "<constraint>"}` with the offending field and the constraint. E.g. `{"error": "validation", "field": "duration_minutes", "message": "must be between 15 and 240, got 500"}`.
  - **Opaque errors:** validation errors return a generic `"error: bad input"` with no field or constraint info.
- One ambiguous test prompt: *"Book a 90-minute design review with Priya next Tuesday afternoon."* This deliberately omits an email, leaves "afternoon" vague, and uses a relative date — exactly the conditions under which a loose schema lets the model paper over the gaps and a tight schema forces them into the open.

**Live script:**

1. Run the prompt against the **loose** schema. The model packs everything into the `details` string and "succeeds" — the tool returns "Meeting booked." Show that whether the meeting was actually booked correctly is impossible to tell from the conversation.
2. Run the prompt against the **tight** schema with **opaque** errors. The model takes a guess at each field and submits. The runtime returns `"error: bad input"`. The model's next turn typically retries with a different guess — still wrong, still opaque. Run it twice to show the loop.
3. Run the same prompt against the **tight** schema with **informative** errors. The model submits, gets a structured error naming the offending field, and on the next turn either asks the user for the missing detail (e.g. Priya's email) or fixes the field and retries. Show the recovery path.

**What to highlight:**

- The loose schema *appears* to work and is the worst outcome — silent wrongness. The tight schema with opaque errors *fails noisily but unhelpfully*. The tight schema with informative errors *fails productively* — the model learns from each turn.
- An error message is a *prompt* for the model's next turn. Write it as if it were a system message, not as if it were a Python traceback. (Stage-2 lab idea: have students rewrite a stack-trace error into an informative one.)
- The three error classes from [objectives.md](objectives.md): this demo is the *validation error* case. Point at recoverable runtime errors (transient API failures) and unrecoverable errors (entity does not exist) as the next two cases — Demo 4 will cover the latter.

**If the demo misbehaves:**

- If the model on the tight-schema run guesses an email so confidently that it submits a fake `priya@example.com` and the validation passes (because email format is correct even if the address is fake), use it as a teaching moment: schemas validate *shape*, not *truth*. Then add a note that this is exactly why the next demo (errors for nonexistent entities) matters.
- If the loose-schema run produces a tool call that happens to be parseable, run a second variant of the prompt with even more vagueness (*"Book me a meeting with the design folks soon"*) to provoke the failure.

## Demo 4 — Errors that close the loop, side effects that don't (Objectives 3 + 4)

**Goal:** show the difference between recoverable, unrecoverable, and side-effecting errors — and the model's behavior in each case. Land the framing from [objectives.md](objectives.md): *the model will retry on its own when results look ambiguous, regardless of whether retry is safe.*

**Pre-flight:**

- The tight `book_meeting` tool from Demo 3 with informative errors enabled.
- A `lookup_user_by_email(email: str)` tool with two response shapes wired up:
  - **Returns `{"found": false, "email": "..."}`** when the email is not in the user database — clean unrecoverable signal.
  - **Returns `{"error": "lookup_failed"}`** when a hidden `--simulate-flake` flag is on — fake transient error, recoverable on retry.
- A `send_message(recipient_id: str, body: str)` tool that:
  - **Logs every call to a visible "outbox" panel on screen** so the audience can see when a message is sent.
  - **Has no idempotency key.** Calling it twice with the same arguments sends two messages.
  - Has a description that *does not mention* the side effect. We'll fix this mid-demo.
- One test prompt: *"Look up the user with email priya@example.com, then send them a message saying the design review is at 2pm Tuesday."*

**Live script:**

1. **Unrecoverable error path.** Run the prompt with `lookup_user_by_email` returning `{"found": false}` for that address. The model sees a clean "no such user" signal in the tool result and either reports back to the user or asks for the right email — *no retry loop*. Show the trace.
2. **Recoverable error path.** Flip the `--simulate-flake` flag and re-run. The lookup returns `{"error": "lookup_failed"}`. The model usually retries the same call once, sometimes twice. Show this in the trace. Then turn the flake off and the retry succeeds. Discuss: who should retry — the runtime (silently, with backoff) or the model (visibly, costing a turn)?
3. **Hidden side effects.** Replace the `lookup_user_by_email` tool with one that *also creates a user record if not found* (a deliberately bad design). Re-run prompt 1. Show the audience the outbox panel: a message went out *and* a user was silently created. The model didn't intend the side effect — the tool description hid it.
4. **Fixing the side effect.** Update the description in place to say *"Looks up a user by email. If the user does not exist, this tool will create one with default settings — call only when a missing user should be auto-created."* Re-run. The model now reasons about the side effect before calling and often pauses to ask the user.
5. **Non-idempotent retry.** Manually trigger the model to retry the `send_message` call (e.g. by saying *"I'm not sure that went through, try again"*). Show the outbox: two identical messages. Discuss the mitigation options from [objectives.md](objectives.md): runtime-level idempotency keys, an explicit confirmation step, a tool description that warns against retry.

**What to highlight:**

- The three error classes are *interfaces*, not just edge cases. The model's recovery behavior is determined by the shape of the error.
- A side effect that isn't named in the description is a side effect the model can't reason about — and therefore can't avoid. Naming it isn't paranoia; it's part of the contract.
- Idempotency is a *system* concern, not just a tool-author concern. Even a perfectly described tool can be called twice by a confused model. The mitigation lives at the runtime/design layer.
- Bridge forward: L12 (human-in-the-loop and approval gates) revisits this exact tension for high-stakes side effects. L05 plants the seed; L12 builds the structure.

**If the demo misbehaves:**

- If the model refuses to retry the flaky lookup at all (and just reports the error to the user), that's a fine outcome — name it as the *other* end of the design spectrum and discuss when each is preferable.
- If the model on step 5 catches the duplicate-send risk and refuses to retry, lean into it: well-trained models sometimes get this right zero-shot, but you can't *rely* on that — design for the worst case.

## Optional bridge demo — toward MCP (L06)

If time allows, run one final demo that previews L06: take one of the well-designed tools from Demos 2–4 and walk through how its name, description, schema, and error shape would translate one-to-one into an MCP server's tool spec. Don't teach the MCP wire format here; just show that the *design* survives the packaging change. The point is to set up L06's framing: MCP is about portability, not about redoing the design work.

<!-- *NEED INPUT*: include this bridge demo, or save it as the opener for L06? -->

## Pacing notes for the teacher

- **Per-demo time:** 10–15 minutes including post-demo discussion. Demo 4 is the longest (5 sub-steps). Four demos plus the optional bridge fits in a 60–80 minute block. <!-- *NEED INPUT*: confirm against the lesson-time budget once duration is pinned in [objectives.md](objectives.md)'s open questions. -->
- **Variance budget:** model behavior varies run-to-run, especially in Demo 2 where the whole point is *distributional* behavior. Budget at least one re-run per demo, and on Demo 2 explicitly run each variant twice so the audience sees variance, not just a single result.
- **The audience watches, doesn't participate.** Resist the temptation to ask "what would *you* call this tool?" — that is a lab pattern, not a demo pattern. Hands-on practice is for the L05 labs.
- **Keep the same task across Demos 2–3 where possible.** Repetition of the same input across changing tool designs is what makes the contrast legible. Don't rotate problems for variety's sake.

## Open authoring questions

- <!-- *NEED INPUT*: which model class(es) anchor the demos — see top-of-file pre-flight. This decision propagates to every demo, especially Demo 2 where the description-quality gap widens on smaller models. -->
- <!-- *NEED INPUT*: are the demos run in a Jupyter notebook the teacher projects, or in a slide-embedded REPL, or via a custom demo runner script? Affects how the tool-registry swap (good vs. bad variants) is wired. -->
- <!-- *NEED INPUT*: should Demo 4's recoverable-error case introduce *runtime-level* retry logic with backoff, or stay strictly at the model-visible layer? Going deeper foreshadows L07 (hand-rolled agent loop), which may be the better home. -->
- <!-- *NEED INPUT*: should the side-effect discussion in Demo 4 introduce typed effects (read vs. write vs. external) or keep it informal? Mirrors the same open question in [objectives.md](objectives.md). Forward link to L12 (approval gates) may be sufficient. -->
- <!-- *NEED INPUT*: do the L05 demo tools share an implementation with the L05 lab tools, or are lab tools designed from scratch by students? Affects how much of the demo code is reusable. Mirrors the lab-design question in [objectives.md](objectives.md). -->
- <!-- *NEED INPUT*: a pointer/link to where the demo tools live as code (a `demos/` subdir? inline in a notebook?) — not yet decided in non-draft docs. -->
