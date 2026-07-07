# L07 Proctor Notes

Notes for whoever runs the L07 labs. One section per problem, keyed by lab id and problem number.
Times are rough and assume a semi-technical student with basic Python who completed L01–L06.

> Cross-cutting note: the four teacher demos (L0703 a tool call is tokens / L0704 one wired
> round-trip / L0706 trace the round-trip / L0708 three outcomes) plus the **L0705** lab make
> **live** Claude calls and need `ANTHROPIC_API_KEY` set (copy `.env.example` to `.env`). The other
> two labs stay **offline** (pure Python): **L0707** (trace a round-trip) and **L0709** (validate
> tool calls). L0706 is also offline — it dissects a crafted transcript.
>
> **Which client?** L07 uses LangChain's `ChatAnthropic` — the same framework client from L03.
> `model.bind_tools([calculator])` makes the plain function a tool (the definition is *inferred*
> from the function's name, docstring, and type hints); the model's request comes back as
> `AIMessage.tool_calls`, and the tool result goes back as a `ToolMessage`. The API key still loads
> through `common.config` (`require_anthropic_key`), never hard-coded. There is no raw-SDK detour —
> a LangChain chat model carries tool calls natively, so nothing "reaches under" the seam.
>
> Because the model varies run to run, a live run may not reproduce every effect the prose calls
> out — especially Demo 4 / L0709's hallucinated call. Dry-run the demos before class and clear any
> cell outputs that hit the API before committing. The labs map to the L07 subgoals: **L0705** →
> wire a single tool; **L0707** → trace one round-trip; **L0709** → describe the protocol by writing
> the validation the application owns.

## L0705_lab problem 1 — Send the first turn and find the tool call

- **Common gotchas:** invoking the bare `model` instead of `model_with_tools` (so the model just
  answers in text and `.tool_calls` is empty); forgetting to `await` (`ainvoke` returns a coroutine,
  not an `AIMessage`); expecting the reply to *be* the tool call rather than
  reading it off `.tool_calls`; treating `call["args"]` as a JSON string (it is already a parsed dict).
- **Unblockers:** "Build `messages = [HumanMessage(PROMPT)]`, then `first = await model_with_tools.ainvoke(messages)`,
  then `call = first.tool_calls[0]`." If `.tool_calls` is empty, the prompt may be too easy —
  `PROMPT` is large multiplication on purpose.
- **Time:** ~7 min.
- **Note:** needs `ANTHROPIC_API_KEY`.

## L0705_lab problem 2 — Dispatch: run the real function

- **Common gotchas:** passing the whole `call["args"]` dict to `calculator` instead of
  `call["args"]["expression"]`; skipping the name check (fine for one tool, but the habit matters
  once there are several).
- **Unblockers:** "`assert call['name'] == 'calculator'`, then `calculator(call['args']['expression'])`."
  The result is a string — that's what the `ToolMessage` wants.
- **Time:** ~5 min.
- **Key point:** *this* number is computed by the application; the number in the model's proposed
  args was just generated tokens.

## L0705_lab problem 3 — Continue: hand the result back

- **Common gotchas:** forgetting to first append the assistant's turn (`first`, the `AIMessage`
  carrying the tool call — the API needs the call before its result); building the tool result by
  hand instead of using `ToolMessage`; omitting `tool_call_id`, or using a different id than the one
  the model emitted; invoking the bare `model` on the second call (drops the tool definition).
- **Unblockers:** "`messages.append(first)`, then `messages.append(ToolMessage(content=result,
  tool_call_id=call['id']))`, then `final = await model_with_tools.ainvoke(messages)` and read
  `final.content`." Final answer should be **43,123,800** (6,150 × 7,012).
- **Time:** ~10 min.

## L0705_lab problem 4 — Why re-send the tool definition? (written)

- **Common gotchas:** "so the model remembers it" — backwards; the model is stateless and remembers
  nothing between calls.
- **Unblockers:** expected: the model is **stateless across calls**, so the tool definition (and the
  whole history) is part of the prompt on *every* request; drop it and the model no longer knows the
  tool exists. Keeping the same `model_with_tools` handle re-attaches the definition automatically.
  Tie to the L0706 demo's "tools cost tokens twice over."
- **Time:** ~3 min.

## L0707_lab problem 1 — Summarize what each message carries

- **Common gotchas:** checking `.content` block structure instead of the message *type*; forgetting
  that an `AIMessage` with an empty `.tool_calls` is plain text, not a tool call.
- **Unblockers:** "An `AIMessage` with a non-empty `.tool_calls` → the tool names; a `ToolMessage` →
  `'tool result'`; otherwise → `'text'`. Print `msg.type` alongside it." Expected types down the four
  messages: `human`, `ai`, `tool`, `ai`.
- **Time:** ~6 min.

## L0707_lab problem 2 — Match the result to the request by id

- **Common gotchas:** comparing the wrong fields (`tool_calls[0]["id"]` lives on the `AIMessage`,
  `tool_call_id` on the `ToolMessage`); reaching into the wrong message index.
- **Unblockers:** "Message 2 is the `AIMessage` — its call id is `t[1].tool_calls[0]['id']`; message 3
  is the `ToolMessage` — its id is `t[2].tool_call_id`. Return whether they're equal." Expect `True`.
- **Time:** ~5 min.
- **Key point:** with one call in flight the id seems redundant; it becomes essential the moment two
  calls are outstanding (L10).

## L0707_lab problem 3 — Tell the three outcomes apart

- **Common gotchas:** classifying by `.content` rather than `.tool_calls`; treating a tool call with
  empty `args` as `answered` (it's `malformed` — the call was attempted).
- **Unblockers:** "Empty `.tool_calls` → `answered`. A tool call whose `args` lacks `expression` →
  `malformed`. Otherwise → `called`." Expected: A=called, B=answered, C=malformed.
- **Time:** ~7 min.

## L0707_lab problem 4 — Why four messages? (written)

- **Common gotchas:** counting three (forgetting the application's `ToolMessage`) or conflating the
  model's two `AIMessage` turns.
- **Unblockers:** expected: `HumanMessage(question)` → `AIMessage(tool_calls)` → `ToolMessage(result,
  produced by the application)` → `AIMessage(final)`. Four is the minimum, not a fixed number.
- **Time:** ~4 min.

## L0709_lab problem 1 — Write the validator

- **Common gotchas:** letting `calculator`'s `ValueError` propagate instead of catching it and
  returning a `REJECTED` string; checking `expression` truthiness instead of membership (an empty
  dict has no key); only handling one of the three failure classes.
- **Unblockers:** "Three guards in order: unknown `call['name']` → reject; `'expression' not in
  call['args']` → reject; else `try: calculator(...) except ValueError: reject`." The good call
  returns `415668857`.
- **Time:** ~8 min.
- **Key point:** this *is* the protocol's safety layer — the application validates, the model only
  proposes.

## L0709_lab problem 2 — Run it over every crafted call

- **Common gotchas:** none beyond a stray crash if Problem 1's `validate_call` re-raises; if the loop
  dies, the validator is letting an exception escape.
- **Unblockers:** "Just `for call in CALLS: print(validate_call(call))`." Expect 1 OK and 3 REJECTED.
- **Time:** ~3 min.

## L0709_lab problem 3 — The three outcomes (written)

- **Unblockers:** expected: (1) the model calls the tool with valid args; (2) it answers without the
  tool; (3) it calls the tool with malformed/hallucinated args. Same three as L0707 problem 3, stated
  in prose.
- **Time:** ~3 min.

## L0709_lab problem 4 — Why doesn't the schema stop a bad call? (written)

- **Common gotchas:** "the schema validates the input" — it describes the input to the model but is
  not enforced at *generation* time.
- **Unblockers:** expected: the schema is part of the *prompt* — it tells the model what shape exists,
  but the model still *samples* tokens and can emit malformed or invented arguments; nothing checks
  them until the application does. The schema is a contract about shape, not a guarantee about
  behavior.
- **Time:** ~4 min.
