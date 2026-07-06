# L03 — Proctor notes

Single lesson, single lab (`L0304_lab`). The lab is **fully offline** (a deterministic `StubChat`
stands in for `ChatAnthropic`), so no API key is needed and every student gets identical output. The
teacher demos (`L0303_lecture.ipynb`) *do* make live calls and need `ANTHROPIC_API_KEY`. The L0302
LangChain/LangGraph primer also makes small live `ChatAnthropic` calls.

**Whole-lesson reminder:** L03 stays at **one node**. Resist wiring a second node "to show what's
coming" — that reveal belongs to L04. Keep repeating the refrain: *"a node is one LLM call you wire;
state goes in, state comes out."*

## L0304_lab problem 1 (the typed state)

- **COMMON GOTCHAS:** students reach for `Annotated[..., add]` reducers or an `Annotated` import
  because they half-remember it from somewhere. Redirect: reducers merge *multiple* nodes' updates —
  there is only one node here, so the two plain fields are all that's needed. Reducers are L04.
- **UNBLOCKERS:** the two fields are `raw_text: str` (input) and `summary: str` (output). If stuck,
  point them at `ExtractState` in the lecture notebook — same shape, different field names.
- **TIME:** ~3 min.

## L0304_lab problem 2 (the node)

- **COMMON GOTCHAS:** (1) returning the whole state (`return state`) or the bare string instead of an
  update dict — reinforce "return only the field you changed: `{"summary": ...}`." (2) Returning the
  `reply` object rather than `reply.content` — remind them a node returns plain data, and `.content`
  is the text off the response.
- **UNBLOCKERS:** the body is three lines — build a prompt string, `sonnet.invoke(prompt)`, return
  `{"summary": str(reply.content)}`.
- **TIME:** ~5 min. Longest problem.

## L0304_lab problem 3 (wire, compile, render)

- **COMMON GOTCHAS:** forgetting `set_entry_point("summarize")` (graph won't compile), or forgetting
  `add_edge("summarize", END)`. The node name string in `add_node` must match the string used in
  `set_entry_point`/`add_edge`.
- **UNBLOCKERS:** four builder calls then `compile()`; the pattern is identical to the lecture's
  section 5, just the one node. `draw_mermaid()` needs no key.
- **TIME:** ~4 min.

## L0304_lab problem 4 (invoke and inspect)

- **COMMON GOTCHAS:** expecting `invoke()` to return just the summary. It returns the *whole state* —
  that is the teachable moment ("input intact, output added"). Pass the input as a dict:
  `{"raw_text": ...}`, not a bare string.
- **UNBLOCKERS:** `result = summarize_app.invoke({"raw_text": TICKETS["billing"]})`, then print both
  `result["raw_text"]` and `result["summary"]`.
- **TIME:** ~3 min.

## L0304_lab problem 5 (written)

- **COMMON GOTCHAS:** answers that say "the node changes too." Redirect to the interface point: the
  node only calls `.invoke(prompt).content`; both `StubChat` and `ChatAnthropic` expose that, so the
  node is untouched. Only the client-construction line changes.
- **STRETCH (early finishers):** have them actually swap `StubChat(SONNET)` for a real
  `ChatAnthropic(model=SONNET, api_key=require_anthropic_key())` (if a key is available) and confirm
  the node code runs unchanged — the cleanest possible proof of the point.
- **TIME:** ~4 min written.
