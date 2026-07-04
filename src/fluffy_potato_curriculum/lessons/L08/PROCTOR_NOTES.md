# L08 Proctor Notes

Notes for whoever runs the L08 labs. One section per problem, keyed by lab id and problem number.
Times are rough and assume a semi-technical student with basic Python who completed L01–L07.

> Cross-cutting note: the four teacher demos (L0803 tool-or-no-tool / L0805 the description / L0807
> schemas + validation errors / L0809 errors & side effects) make **live** Claude calls and need
> `ANTHROPIC_API_KEY` set (copy `.env.example` to `.env`). Dry-run them before class — model
> behavior **varies**, and several demos (L0805's sparse-vs-rich, L0809's retry) are *distributional*,
> so run the named variants twice. Clear any API-touching cell outputs before committing.
>
> **All four L08 labs are OFFLINE / pure Python** — no API key required. L08 is about *design
> judgment*, and you practice that by designing schemas, rewriting errors, and classifying tasks, not
> by spending tokens. The labs map to the four subgoals: **L0804** → tool-or-no-tool; **L0806** →
> name + schema design; **L0808** → error shapes; **L0810** → idempotency + side effects.
>
> **Which client:** L08's demos use LangChain's `ChatAnthropic` (the framework client from L03/L07).
> A tool is a plain typed function — `model.bind_tools([fn])` infers the definition from its name,
> docstring, and type hints; the model's choice comes back in `AIMessage.tool_calls`, and results go
> back as a `ToolMessage`. The key still loads through `common.config` (`require_anthropic_key`). The
> labs don't call a model at all — they're pure-Python design exercises.
>
> L08 assumes the L07 mechanics work. If a student is shaky on the tool-call round-trip, redirect to
> the L07 lab before this lesson — L08 does **not** re-teach the protocol.

## L0804_lab problem 1 — Decide tool-or-not for each task

- **Common gotchas:** picking *more than one* signal per task (the lab wants the single dominant one);
  flipping T6 to a tool ("summarize" feels tool-ish, but the model does it well unaided — it's a
  no-tool case); reading T5 as `model_knows` rather than `verify` (a subscription status must be
  checked against the database, not recalled).
- **Unblockers:** "Ask the worked test: does it depend on data the model can't have (T2), need precise
  computation (T3), cause a side effect (T4), or need verification (T5)? If the model nails it cold
  (T1, T6), no tool."
- **Time:** ~7 min.
- **Note:** there is real judgment room on borderline tasks; what matters is that the chosen *signal*
  matches the chosen *decision* (Problem 2 checks exactly that).

## L0804_lab problem 2 — Check your signals are valid

- **Common gotchas:** checking the signal against the *wrong* family (a `tool: True` decision whose
  signal is from `NO_TOOL` should fail); hard-coding `True` instead of looking the key up.
- **Unblockers:** "If `decision['tool']` is True, the signal must be in `WARRANTED`; otherwise it must
  be in `NO_TOOL`." All six should print `True` once Problem 1 is internally consistent.
- **Time:** ~4 min.
- **Key point:** this is a *consistency* check, not a correctness oracle — it catches a tool decision
  paired with a no-tool reason, which is the most common slip.

## L0804_lab problem 3 — Defend each call in one sentence

- **Common gotchas:** writing prose by hand instead of pulling the signal's description text;
  forgetting the `Tool:` / `No tool:` prefix.
- **Unblockers:** "Look up `WARRANTED[signal]` (or `NO_TOOL[signal]`) and wrap it: `f\"Tool:
  {...}.\"`." The one-sentence defense *is* the deliverable — naming *why* is the skill.
- **Time:** ~5 min.

## L0804_lab problem 4 — Why is 'more tools' usually worse? (written)

- **Common gotchas:** "more tools = more capable" — the exact confusion the lecture corrects.
- **Unblockers:** expected: each extra tool eats system-prompt tokens (L01 context cost), dilutes the
  model's attention across a longer tool list, and adds another wrong-tool failure mode; a focused
  5-tool set the model can navigate beats a 20-tool grab bag.
- **Time:** ~4 min.

## L0806_lab problem 1 — Rewrite the description for the model

- **Common gotchas:** writing a code-comment-style description ("sets the priority field") instead of
  one for the model's selection step; omitting the *when NOT to call* clause; not stating the return
  shape. The `assert len(... .split()) >= 25` nudges past a one-liner.
- **Unblockers:** "Answer four things: what it does, when to call, when NOT to call, what it returns —
  and name the allowed levels with an example." The checks look for `ticket`, `low`, `high`, `return`;
  wording is the student's.
- **Time:** ~8 min.
- **Key point:** the audience is the model, not a human reading the source.

## L0806_lab problem 2 — Type the function (and read its inferred schema)

- **Common gotchas:** giving `level` a default (that makes it *optional* — both fields should be
  required, so no defaults); typing `level` as a plain `str` instead of `Literal["low","medium","high"]`
  (the `Literal` is what becomes the enum); dropping the `Annotated` per-field descriptions (rule of
  thumb: each carries an example or a constraint); forgetting `set_priority.__doc__ = RICH_DESCRIPTION`.
- **Unblockers:** "Both params `Annotated[..., 'desc']` with no defaults; `level`'s type is
  `Literal['low','medium','high']`; then `TIGHT_SCHEMA = inferred_schema(set_priority)['parameters']`."
  The printed schema should show `required: [ticket_id, level]`, a `level.enum`, and a `description` on
  each property.
- **Time:** ~7 min.
- **Key point:** they never hand-write JSON — `bind_tools` infers it. A good schema is a well-typed
  function.

## L0806_lab problem 3 — Validate sample arguments against your schema

- **Common gotchas:** forgetting that `bool` is a subclass of `int` in Python (so `True` would pass an
  `integer` check unless guarded); checking enum on fields that have none (use `if \"enum\" in spec`);
  not handling the missing-required case before the type checks.
- **Unblockers:** "Three passes: required keys present? each present value the right `type`? enum
  members where an enum exists?" Expected: sample 1 `ok`, the other three each a distinct reason.
- **Time:** ~9 min.
- **Key point:** this tiny validator is the *shape* line of defense — it does not (and can't) check
  whether a well-formed value is *true* (L0808/L0809's job).

## L0806_lab problem 5 — Why an enum over a free string? (written)

- **Common gotchas:** "it's just type-checking" — misses that the enum also *teaches* the model the
  value space.
- **Unblockers:** expected: the enum shrinks the value space to three legal options the model can't
  misfill, and turns an out-of-range guess into a recoverable validation error instead of a silent
  bad write. (Problem is numbered 5 because Problem 4 is the written schema-tightening reflection folded
  into Problem 2's discussion — keep the numbering as printed.)
- **Time:** ~4 min.

## L0808_lab problem 1 — Rewrite the traceback as a structured error

- **Common gotchas:** echoing the traceback text into `message` instead of writing an *actionable*
  sentence; forgetting the `field` key; using `error=\"error\"` instead of the class `\"validation\"`.
- **Unblockers:** "`{'error': 'validation', 'field': 'duration_minutes', 'message': 'must be an integer
  between 15 and 240, got ...'}`. The message tells the model *which* field and *how* to fix it."
- **Time:** ~7 min.
- **Key point:** the error is a *prompt for the next turn*, not a debugger dump.

## L0808_lab problem 2 — Rewrite the missing-field error

- **Common gotchas:** classifying a missing required field as `unrecoverable` (it's `validation` — the
  model can supply the field); leaving out the example email.
- **Unblockers:** "Same shape as Problem 1: name `attendee_email`, say it's required, give the format
  to supply."
- **Time:** ~5 min.

## L0808_lab problem 3 — Classify each error into one of three classes

- **Common gotchas:** marking `no_such_user` / `forbidden` as recoverable (they are *final* —
  unrecoverable, stop retrying); marking `timeout` / `rate_limited` as validation (they're transient
  recoverable runtime errors, not bad arguments).
- **Unblockers:** "Bad arguments → validation. Transient (rate limit, timeout) → recoverable. Final
  (no such entity, no permission) → unrecoverable." Expected: bad_duration/missing_field=validation,
  rate_limited/timeout=recoverable, no_such_user/forbidden=unrecoverable.
- **Time:** ~7 min.

## L0808_lab problem 4 — Which class should the model retry? (written)

- **Unblockers:** expected: validation → retry *with a fix* (correct the named field); recoverable →
  retry *as-is* (the same call may succeed, ideally with runtime backoff); unrecoverable → *stop and
  report* / route around — retrying just burns budget. The error *shape* is what lets the model pick.
- **Time:** ~4 min.

## L0810_lab problem 1 — Tag each tool safe-or-unsafe to retry

- **Common gotchas:** marking `upsert_contact` unsafe (it has a *stable key*, so a repeat is
  idempotent — safe); marking `add_numbers` unsafe (pure computation, no side effect); treating
  `create_ticket` as safe (no key → a second ticket each call).
- **Unblockers:** "Read-only / pure / keyed-upsert → safe. Sending / charging / create-without-key →
  unsafe." From the lecture's safe-vs-not table.
- **Time:** ~6 min.

## L0810_lab problem 2 — Recommend a mitigation for each unsafe tool

- **Common gotchas:** giving a mitigation to a *safe* tool (should be `none_needed`); inventing a
  mitigation outside the three named ones.
- **Unblockers:** "Pick one of `idempotency_key`, `confirmation_step`, `warn_in_description` per unsafe
  tool — any defensible mapping. A high-stakes `charge_card` is a natural `confirmation_step`; a
  `create_ticket` a natural `idempotency_key`."
- **Time:** ~5 min.
- **Note:** there is judgment room — accept any of the three so long as it's defensible for that tool.

## L0810_lab problem 3 — Show a duplicate slips through without a key

- **Common gotchas:** returning `None` instead of `len(sent)`; resetting the log between the two calls
  (then it never shows the duplicate); deduping inside `send_email` (that would *be* a mitigation — the
  point here is to show the unmitigated failure).
- **Unblockers:** "Just append `(to, body)` and return `len(sent)`. Call it twice on the same `log`;
  expect length 2." This mirrors the L0809 demo's OUTBOX growing to two entries.
- **Time:** ~5 min.

## L0810_lab problem 4 — Write the side-effect sentence (written)

- **Common gotchas:** describing *what the tool returns* instead of *the side effect*; burying the
  create in soft language ("may update records") instead of stating it plainly.
- **Unblockers:** expected: something like *\"If the user does not exist, this tool will create one
  with default settings — call only when a missing user should be auto-created.\"* Name the effect so
  the model can reason about it before calling. Forward-link to L14 (approval gates).
- **Time:** ~4 min.
