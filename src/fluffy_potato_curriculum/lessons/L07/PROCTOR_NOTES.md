# L07 Proctor Notes

Notes for whoever runs the L07 labs. One section per problem, keyed by lab id and problem number.
Times are rough and assume a semi-technical student with basic Python who completed L01–L06.

> Cross-cutting note: the four teacher demos (L0703 a tool call is tokens / L0704 one wired
> round-trip / L0706 trace the round-trip / L0708 three outcomes) plus the **L0705** lab make
> **live** Claude calls and need `ANTHROPIC_API_KEY` set (copy `.env.example` to `.env`). The other
> two labs stay **offline** (pure Python): **L0707** (trace a round-trip) and **L0709** (validate
> tool calls). L0706 is also offline — it dissects a crafted transcript. Every live notebook is
> gated on `LIVE = bool(get_settings().anthropic_api_key)`, so a keyless restart-and-run-all still
> passes (the live cells just print an "offline" note).
>
> **LangChain, not the raw SDK.** From L03 on the course drives every model call through a LangChain
> chat model (`ChatAnthropic` here), so the tool code is **model-agnostic** — swap `ChatAnthropic`
> for `ChatOpenAI` and it runs unchanged. The tool is a plain typed function; `model.bind_tools([fn])`
> derives its JSON-Schema definition from the signature and docstring (Demo 1 prints it). A tool call
> arrives as an entry in `AIMessage.tool_calls` (a `{"name", "args", "id"}` dict), and the result goes
> back as a `ToolMessage(content=..., tool_call_id=...)`. The API key still loads through
> `common.config` (`require_anthropic_key`), never hard-coded. Students never touch the raw
> `tool_use`/`tool_result` wire blocks — LangChain normalizes those into `.tool_calls` / `ToolMessage`.
>
> Because the model varies run to run, a live run may not reproduce every effect the prose calls
> out — especially Demo 4 / L0709's hallucinated call. Dry-run the demos before class and clear any
> cell outputs that hit the API before committing. The labs map to the L07 subgoals: **L0705** →
> wire a single tool; **L0707** → trace one round-trip; **L0709** → describe the protocol by writing
> the validation the application owns.

## L0705_lab problem 1 — Invoke the tool-bound model and find the tool call

- **Common gotchas:** invoking the plain `model` instead of `bound` (the tool-bound model) — with no
  tools bound the reply is text and `.tool_calls` is empty; expecting an answer in `.text` on a
  tool-calling turn (it is usually empty — the request lives in `.tool_calls`); treating
  `call["args"]` as a JSON string (it is already a parsed dict).
- **Unblockers:** "`first = bound.invoke([HumanMessage(PROMPT)])`, then `call = first.tool_calls[0]`
  — a `{'name','args','id'}` dict." If `.tool_calls` is empty, the prompt may be too easy — `PROMPT`
  is large multiplication on purpose.
- **Time:** ~7 min.
- **Note:** needs `ANTHROPIC_API_KEY`.

## L0705_lab problem 2 — Dispatch: run the real function

- **Common gotchas:** passing the whole `call["args"]` dict to `calculator` instead of
  `call["args"]["expression"]`; skipping the name check (fine for one tool, but the habit matters once
  there are several).
- **Unblockers:** "`assert call['name'] == 'calculator'`, then `calculator(call['args']['expression'])`."
  The result is a string — that's what the `ToolMessage` wants.
- **Time:** ~5 min.
- **Key point:** *this* number is computed by the application; the number in the model's proposed
  args was just generated tokens.

## L0705_lab problem 3 — Continue: hand the result back

- **Common gotchas:** forgetting to append the assistant's turn (`messages.append(first)` — the
  `AIMessage` object itself) before the result; building a fresh dict instead of appending the
  `AIMessage`; omitting `tool_call_id` on the `ToolMessage`, or using a different id than the call's;
  invoking the plain `model` on the second call instead of `bound`.
- **Unblockers:** "Append `first` (the `AIMessage`), then
  `ToolMessage(content=result, tool_call_id=call['id'])`. Call `bound.invoke(messages)` again and read
  `.text`." Final answer should be **43,123,800** (6,150 × 7,012).
- **Time:** ~10 min.

## L0705_lab problem 4 — Why re-send the tool definition? (written)

- **Common gotchas:** "so the model remembers it" — backwards; the model is stateless and remembers
  nothing between calls.
- **Unblockers:** expected: the model is **stateless across calls**, so the bound tool definitions
  (and the whole history) are part of the prompt on *every* request; `bind_tools` re-sends them each
  `.invoke`. Drop them and the model no longer knows the tool exists. Tie to the L0706 demo's "tools
  cost tokens twice over."
- **Time:** ~3 min.

## L0707_lab problem 1 — Summarize each message

- **Common gotchas:** not distinguishing the three message classes — an `AIMessage` with `.tool_calls`,
  a `ToolMessage` with a `.tool_call_id`, and a plain-text message; reaching for `.content` blocks
  instead of the helpers (`.tool_calls`, `.text`).
- **Unblockers:** "`isinstance(msg, AIMessage) and msg.tool_calls` → show the call name(s);
  `isinstance(msg, ToolMessage)` → show `.tool_call_id`; else show `msg.text`."
  Expected down the four messages: `HumanMessage` text, `AIMessage` tool call → calculator,
  `ToolMessage` result, `AIMessage` text.
- **Time:** ~6 min.

## L0707_lab problem 2 — Match the result to the request by id

- **Common gotchas:** comparing the wrong fields (`tool_calls[0]["id"]` lives on the `AIMessage`;
  `tool_call_id` lives on the `ToolMessage`); reaching into the wrong message index.
- **Unblockers:** "Message 2 is the `AIMessage` (`.tool_calls[0]['id']`); message 3 is the
  `ToolMessage` (`.tool_call_id`). Return whether they're equal." Expect `True`.
- **Time:** ~5 min.
- **Key point:** with one call in flight the id seems redundant; it becomes essential the moment two
  calls are outstanding (L10).

## L0707_lab problem 3 — Tell the three outcomes apart

- **Common gotchas:** classifying by whether there's *any* text rather than by `.tool_calls`; treating
  a tool call with empty `args` as `answered` (it's `malformed` — the call was attempted).
- **Unblockers:** "No `.tool_calls` → `answered`. A tool call whose `args` lacks `expression` →
  `malformed`. Otherwise → `called`." Expected: A=called, B=answered, C=malformed.
- **Time:** ~7 min.

## L0707_lab problem 4 — Why four messages? (written)

- **Common gotchas:** counting three (forgetting the application's `ToolMessage` turn) or conflating
  the model's two `AIMessage` turns.
- **Unblockers:** expected: `HumanMessage(question)` → `AIMessage(tool call)` →
  `ToolMessage(result, produced by the application)` → `AIMessage(final)`. Four is the minimum, not a
  fixed number.
- **Time:** ~4 min.

## L0709_lab problem 1 — Write the validator

- **Common gotchas:** letting `calculator`'s `ValueError` propagate instead of catching it and
  returning a `REJECTED` string; checking `expression` truthiness instead of membership (an empty
  `args` dict has no key); only handling one of the three failure classes.
- **Unblockers:** "Three guards in order: unknown `call['name']` → reject; `'expression' not in
  call['args']` → reject; else `try: calculator(...) except ValueError: reject`." The good call returns
  `415668857`.
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
  not enforced at *generation* time; and LangChain's tidy `.tool_calls` dict is a clean *shape*, not a
  validated *value*.
- **Unblockers:** expected: the schema is part of the *prompt* — it tells the model what shape exists,
  but the model still *samples* tokens and can emit malformed or invented arguments; nothing checks
  them until the application does. The definition is a contract about shape, not a guarantee about
  behavior.
- **Time:** ~4 min.
