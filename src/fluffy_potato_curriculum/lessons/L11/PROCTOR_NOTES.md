# L11 Proctor Notes

Covers the one L11 lab: **L1104** (build a shallow agent with `create_agent`). It runs **fully
offline** — a scripted `FakeModel` stands in for `ChatAnthropic`, and the **real** `common/tools.py`
tools run inside the **real** `create_agent` graph — so no API key is needed and every run is
reproducible. The focus is *building and configuring* the one-line agent and *reading its returned
messages*, not model output. The build-and-run lecture demo ([L1103](L1103_lecture.ipynb)) has an
optional live section that uses the real `ChatAnthropic` client (Sonnet 4.6); the lab deliberately
stays offline so `create_agent` is the only variable.

> Keep repeating the lesson's spine: **`create_agent` is the L10 loop, packaged.** Model → tool →
> model until termination is unchanged from L10; the one call just writes the loop, routing, message
> bookkeeping, and step cap for the student. If a student thinks the framework is doing something
> *fundamentally different* from their L10 loop, slow down and map it back — the returned `messages`
> list is the same sequence they appended by hand in L10.

## Environment notes (whole lab)

- **`create_agent` needs a `FakeModel` that tolerates extra kwargs.** The shared
  `common/fake_model.py` `FakeModel` was extended so `bind_tools(tools, **kwargs)` and
  `invoke(messages, *args, **kwargs)` accept the arguments `create_agent` passes (it binds tools
  with `tool_choice=...`). Students don't touch this — it's already handled in `common` — but if a
  student pastes an *older* `FakeModel` they hand-wrote, they'll hit
  `TypeError: bind_tools() got an unexpected keyword argument 'tool_choice'`. Redirect them to import
  `FakeModel` from `common`, not reuse an L10 copy.
- **`create_agent` re-raises uncaught tool exceptions by default.** Unlike the L10 loop (which caught
  every exception into an error `ToolMessage`), the prebuilt tool node re-raises a raised Python
  exception. The lab only ever drives tools that *succeed* or *return an error as data*, so this
  won't bite — but if a curious student scripts `flaky_fetch("https://crash")` and the notebook
  blows up with `RuntimeError: connection reset by peer`, that's expected: configuring tool-error
  handling lives *below* the one-liner (L15). Name it as a real boundary difference, not a bug.
- **The `tqdm`/`IProgress` warning on the first cell is harmless** — it's a Jupyter widget notice,
  not an error. Ignore it.
- Invoking the agent takes a **dict**: `agent.invoke({"messages": [HumanMessage(...)]})`. The most
  common beginner error is passing the string or the list directly. The result is also a dict — read
  `result["messages"]`, not `result` itself.

---

## L1104_lab problem 1 — Build the agent in one line

COMMON GOTCHAS:
- Passing the tools as three positional args (`create_agent(model, calculator, lookup, ...)`) instead
  of **one list** (`create_agent(model, [calculator, lookup, flaky_fetch], ...)`). The second
  positional arg is the whole tool list.
- Passing the *model class* or a string instead of an instance. Here the model is
  `FakeModel(chaining_script)` — an instance built from the scripted replies.
- Forgetting `system_prompt=` is a keyword-only argument.

UNBLOCKERS:
- "It's three arguments: the model, the list of tools, the system prompt. One line." Point them at
  the one-liner in the intro / L1102 outline.
- If `type(agent).__name__` prints `ellipsis`, they left the `...` placeholder — the `agent = ...`
  line still needs filling in.

APPROX TIME: 3-5 min.

STRETCH: ask them to print `agent.get_graph().draw_mermaid()` and find the `tools -> model`
back-edge in the output — the same graph from the L1102 outline.

---

## L1104_lab problem 2 — Run it and read the tool sequence

COMMON GOTCHAS:
- `agent.invoke(chaining_task)` — passing the raw string. It must be
  `agent.invoke({"messages": [HumanMessage(content=chaining_task)]})`.
- Building `tool_sequence` off `ToolMessage`s instead of `AIMessage`s. The **tool calls** live on the
  assistant turn (`AIMessage.tool_calls`); the `ToolMessage` is the *result*, not the request.
- Reading `msg.tool_calls["name"]` — `tool_calls` is a **list** of calls; iterate it and read
  `call["name"]` on each.

UNBLOCKERS:
- Have them print `result["messages"]` first with `describe` and *look* at the shape before building
  the list comprehension. Seeing the `AIMessage -> tool call` lines makes the comprehension obvious.
- Expected result: `['calculator', 'lookup']` — the same sequence L10's hand-rolled loop produced.

APPROX TIME: 5-8 min.

STRETCH: have them compare this `messages` list to the one their L10 loop built — same user /
assistant-with-tool-calls / tool-result / assistant shape, none of it written by hand this time.

---

## L1104_lab problem 3 — Pull the final answer off the messages

COMMON GOTCHAS:
- Over-thinking it — the final answer is just `result["messages"][-1].content`. Some students search
  for a `.final_text` or `.output` attribute that doesn't exist on a `create_agent` result.
- Confusing the last message (the plain-text answer) with the last *tool* message. Natural
  termination means the last message is an `AIMessage` with **no** tool calls.

UNBLOCKERS:
- "The last message is the model's plain-text answer — that's what natural termination looks like.
  Its `.content` is your answer."

APPROX TIME: 2-3 min.

STRETCH: ask *how the code would know* the run terminated naturally vs. hit the step cap. (Natural =
last message is a text `AIMessage`; a capped run would raise a recursion error instead — the
framework's `max_steps`.)

---

## L1104_lab problem 4 — Swap the system prompt (config surface)

COMMON GOTCHAS:
- Expecting the *scripted* `FakeModel` reply text to change when the prompt changes. It won't — the
  `FakeModel` returns fixed lines regardless of the prompt. The teaching point is "same agent, new
  instruction," i.e. you reconfigured behavior by changing one knob; against a live model the answer
  shape would actually shift.
- Reusing the *same* `FakeModel` instance across both agents. A `FakeModel` is stateful (it advances
  through its script), so build a **fresh** `FakeModel(chaining_script)` for `terse_agent`. (The
  solution does this; watch for students who hoist the model into a shared variable.)

UNBLOCKERS:
- "The system prompt is one of the three knobs. You're building the *same* agent with a different
  instruction — nothing about the loop changes."
- If they ask why the answer looks identical: "because the `FakeModel` is scripted. On a live model
  the terse prompt would visibly shorten the answer. The point is the *configuration*, not the
  wording."

APPROX TIME: 5-7 min.

STRETCH: if a key is available, have them run this problem's two prompts against a live
`ChatAnthropic` (Sonnet 4.6) and see the answer shape actually change.

---

## L1104_lab problem 5 — Swap the tool set (config surface)

COMMON GOTCHAS:
- Scripting the `FakeModel` to call a tool that isn't in the passed list (e.g. `lookup` when only
  `[calculator]` was given). The scripted call and the tool list must agree, or the tool node won't
  find the tool.
- Forgetting to build a fresh `FakeModel(calc_script)` — same statefulness gotcha as problem 4.

UNBLOCKERS:
- "The tools you pass *are* the agent's whole capability. Fewer tools is a real configuration choice —
  script the model to use only what you gave it."

APPROX TIME: 4-6 min.

STRETCH: ask what happens if the model asks for a tool that wasn't passed (it can't — the model only
sees the tools you bind; a good segue to "the tool list is the capability surface").

---

## L1104_lab problem 6 — What did `create_agent` write for you? (written)

COMMON GOTCHAS:
- Vague answers ("it makes it easier"). Push for a *specific* L10 line: the `while` driver, the
  `if reply.tool_calls` routing, the `messages.append(...)` bookkeeping, the `max_steps`/recursion
  cap, or the tool dispatch.
- Naming a freebie but not what breaks without it. The prompt asks for one concrete failure mode.

UNBLOCKERS:
- Point back to the freebies table in the [L1103 demo](L1103_lecture.ipynb) (section 7) — each row is
  a freebie paired with the exact L10 twin.
- A good answer names two distinct pieces and, for one, a concrete break (e.g. "without the message
  append, the next model call is malformed — the L10 message-history invariant").

APPROX TIME: 4-6 min.

STRETCH: ask which freebie they'd *most* want to keep control of, and when — a natural lead-in to
Demo 3 / L1105 (the ceiling of the one-liner) and L15.
