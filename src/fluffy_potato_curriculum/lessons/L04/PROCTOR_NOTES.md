# L04 Proctor Notes

Notes for whoever runs the L04 labs. One section per problem, keyed by lab id and problem number.
Times are rough and assume a semi-technical student with basic Python who completed L01–L03.

> Cross-cutting note: the four teacher demos (L0403 a tool call is tokens / L0404 one wired
> round-trip / L0406 trace the round-trip / L0408 three outcomes) plus the **L0405** lab make
> **live** Claude calls and need `ANTHROPIC_API_KEY` set (copy `.env.example` to `.env`). The other
> two labs stay **offline** (pure Python): **L0407** (trace a round-trip) and **L0409** (validate
> tool calls). L0406 is also offline — it dissects a crafted transcript.
>
> **Why the raw Anthropic SDK and not `potato_llm` in L04?** The course's `potato_llm` seam is
> text-only — its `Message` cannot carry `tool_use`/`tool_result` blocks, which are exactly what L04
> teaches. So the L04 notebooks call the raw Anthropic SDK directly; the API key still loads through
> `common.config` (`require_anthropic_key`), never hard-coded. This is the one lesson that reaches
> under the seam. (Open design question for the course: extend `potato_llm` to model tool blocks, or
> keep L04+ on the raw SDK — flagged for the curriculum author.)
>
> Because the model varies run to run, a live run may not reproduce every effect the prose calls
> out — especially Demo 4 / L0409's hallucinated call. Dry-run the demos before class and clear any
> cell outputs that hit the API before committing. The labs map to the L04 subgoals: **L0405** →
> wire a single tool; **L0407** → trace one round-trip; **L0409** → describe the protocol by writing
> the validation the application owns.

## L0405_lab problem 1 — Send the first turn and find the tool call

- **Common gotchas:** forgetting `tools=[CALCULATOR_TOOL]` (so the model just answers in text and
  there is no `tool_use` block to find); using `[0]` to grab the block instead of searching by type
  (a response can lead with a `text` block before the `tool_use`); treating `tool_use.input` as a
  JSON string (it is already a parsed dict).
- **Unblockers:** "Call `client.messages.create(model=MODEL, max_tokens=400, tools=[CALCULATOR_TOOL],
  messages=messages)`, then `next(b for b in resp.content if b.type == 'tool_use')`." If no
  `tool_use` appears, the prompt may be too easy — `PROMPT` is large multiplication on purpose.
- **Time:** ~7 min.
- **Note:** needs `ANTHROPIC_API_KEY`.

## L0405_lab problem 2 — Dispatch: run the real function

- **Common gotchas:** passing the whole `tool_use.input` dict to `calculator` instead of
  `input["expression"]`; skipping the name check (fine for one tool, but the habit matters once there
  are several).
- **Unblockers:** "`assert tool_use.name == 'calculator'`, then `calculator(tool_use.input['expression'])`."
  The result is a string — that's what the tool_result wants.
- **Time:** ~5 min.
- **Key point:** *this* number is computed by the application; the number in the model's proposed
  args was just generated tokens.

## L0405_lab problem 3 — Continue: hand the result back

- **Common gotchas:** putting the `tool_result` in an `assistant` message instead of a **user**
  message; forgetting to first append the assistant's `tool_use` turn (the API needs the call before
  its result); omitting `tool_use_id`, or using a different id than the one the model emitted;
  dropping `tools=` on the second call.
- **Unblockers:** "Append `{'role':'assistant','content': first.content}`, then a `user` message whose
  content is `[{'type':'tool_result','tool_use_id': tool_use.id,'content': result}]`. Call
  `messages.create` again *with tools* and join the `text` blocks." Final answer should be
  **43,123,800** (6,150 × 7,012).
- **Time:** ~10 min.

## L0405_lab problem 4 — Why re-send the tool definition? (written)

- **Common gotchas:** "so the model remembers it" — backwards; the model is stateless and remembers
  nothing between calls.
- **Unblockers:** expected: the model is **stateless across calls**, so the tool definition (and the
  whole history) is part of the prompt on *every* request; drop it and the model no longer knows the
  tool exists. Tie to the L0406 demo's "tools cost tokens twice over."
- **Time:** ~3 min.

## L0407_lab problem 1 — Summarize each message's blocks

- **Common gotchas:** assuming every `content` is a list (message 1's is a plain string); indexing
  into a string character by character.
- **Unblockers:** "If `content` is a `str`, return `'text'`; otherwise join `b['type']` for each block."
  Expected: `text`, `tool_use`, `tool_result`, `text` down the four messages.
- **Time:** ~6 min.

## L0407_lab problem 2 — Match the result to the request by id

- **Common gotchas:** comparing the wrong fields (`id` vs `tool_use_id` live on different blocks);
  reaching into the wrong message index.
- **Unblockers:** "Message 2's content[0] is the `tool_use` (its `id`); message 3's content[0] is the
  `tool_result` (its `tool_use_id`). Return whether they're equal." Expect `True`.
- **Time:** ~5 min.
- **Key point:** with one call in flight the id seems redundant; it becomes essential the moment two
  calls are outstanding (L07).

## L0407_lab problem 3 — Tell the three outcomes apart

- **Common gotchas:** classifying by the *number* of blocks rather than their types; treating a
  `tool_use` with empty `input` as `answered` (it's `malformed` — the call was attempted).
- **Unblockers:** "No `tool_use` block → `answered`. A `tool_use` whose `input` lacks `expression` →
  `malformed`. Otherwise → `called`." Expected: A=called, B=answered, C=malformed.
- **Time:** ~7 min.

## L0407_lab problem 4 — Why four messages? (written)

- **Common gotchas:** counting three (forgetting the application's `tool_result` user turn) or
  conflating the assistant's two turns.
- **Unblockers:** expected: `user(question)` → `assistant(tool_use)` → `user(tool_result, produced by
  the application)` → `assistant(final)`. Four is the minimum, not a fixed number.
- **Time:** ~4 min.

## L0409_lab problem 1 — Write the validator

- **Common gotchas:** letting `calculator`'s `ValueError` propagate instead of catching it and
  returning a `REJECTED` string; checking `expression` truthiness instead of membership (an empty
  dict has no key); only handling one of the three failure classes.
- **Unblockers:** "Three guards in order: unknown name → reject; `'expression' not in call.input` →
  reject; else `try: calculator(...) except ValueError: reject`." The good call returns
  `415668857`.
- **Time:** ~8 min.
- **Key point:** this *is* the protocol's safety layer — the application validates, the model only
  proposes.

## L0409_lab problem 2 — Run it over every crafted call

- **Common gotchas:** none beyond a stray crash if Problem 1's `validate_call` re-raises; if the loop
  dies, the validator is letting an exception escape.
- **Unblockers:** "Just `for call in CALLS: print(validate_call(call))`." Expect 1 OK and 3 REJECTED.
- **Time:** ~3 min.

## L0409_lab problem 3 — The three outcomes (written)

- **Unblockers:** expected: (1) the model calls the tool with valid args; (2) it answers without the
  tool; (3) it calls the tool with malformed/hallucinated args. Same three as L0407 problem 3, stated
  in prose.
- **Time:** ~3 min.

## L0409_lab problem 4 — Why doesn't the schema stop a bad call? (written)

- **Common gotchas:** "the schema validates the input" — it describes the input to the model but is
  not enforced at *generation* time.
- **Unblockers:** expected: the schema is part of the *prompt* — it tells the model what shape exists,
  but the model still *samples* tokens and can emit malformed or invented arguments; nothing checks
  them until the application does. The schema is a contract about shape, not a guarantee about
  behavior.
- **Time:** ~4 min.
