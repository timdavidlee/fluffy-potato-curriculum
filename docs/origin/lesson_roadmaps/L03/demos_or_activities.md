# L03: Teacher-led demos — Single-node operations

> Sibling docs: [objectives.md](objectives.md) (what the lesson aims for), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md).
>
> **Audience for this file:** the teacher running L03. Every demo below is *teacher-driven, no student participation*. Student-driven exercises live in the L03 labs (separate file, stage 2).
>
> **Anchor model: Claude Sonnet 4.6**, and only Sonnet — L03 deliberately keeps the model constant so the *node* is the only new variable a student has to track. (No per-node model mixing here; that mechanism is [L04](../L04/objectives.md)'s.) **This is the course's first framework lesson:** the node calls the **native LangChain `ChatAnthropic`** client directly, *not* the hand-rolled `potato_llm` seam used in L01–L02. Call that departure out loud.

## How to read this file

Each demo is a self-contained block with:

- **Goal** — the single insight the demo should land. Tied to a learning objective from [objectives.md](objectives.md).
- **Pre-flight** — what the teacher needs loaded before class.
- **Live script** — the order of operations during the demo. Treat it as a checklist, not a teleprompter.
- **What to highlight** — the moment(s) where the teacher should slow down and say the takeaway out loud.
- **If the demo misbehaves** — graceful fallback for when the model surprises you (it will).

The demos are ordered to match the four learning objectives from [objectives.md](objectives.md). Demo 1 wraps a single LLM call as a typed node (objectives 1 & 2); Demo 2 compiles, invokes, and inspects that same node in isolation (objective 3); Demo 3 is a short contrast-and-discussion beat, not a build, that lands *why* a node is the unit worth wiring (objective 4). They build on each other — Demo 2 reuses Demo 1's node and state unchanged, and Demo 3 reuses Demo 1's code as the "explicit node" side of its comparison. Run them in order.

> **The spine of L03: one node, nothing wired to it.** L03 is the *first* LangGraph lesson and it deliberately stops at one node — no edges between nodes, no branching, no loop. Keep saying **"state goes in, state comes out"** and **"a node is one LLM call you wire."** The entire lesson is building toward the single sentence a student should leave with: *"you just wired one step — next lesson, you wire several of them together."*

## Pre-flight (once, at the top of the lesson)

The teacher should have, before the first demo starts:

- **LangGraph + the native LangChain Claude client ready.** `from langgraph.graph import StateGraph, END` and `from langchain_anthropic import ChatAnthropic`. Both `langgraph` and `langchain-anthropic` are already project dependencies (added via `uv add`); no install during class. The API key still loads through `common/config.py` (`ChatAnthropic` reads `ANTHROPIC_API_KEY` from the same environment the config seam populates) — key handling is unchanged, only the *client* is the framework's now.
- **One model client constructed and named:** `sonnet = ChatAnthropic(model="claude-sonnet-4-6-...")`. One client, used by the one node — keep it that simple. <!-- *NEED INPUT*: confirm exact model id string for the Sonnet 4.6 snapshot used by ChatAnthropic, read from common/config.py rather than hard-coded in cells. Mirrored from the equivalent open question in L04's demos. -->
- **A small running-example dataset for the single node.** Decided running example: an **`extract` node** that pulls a handful of structured fields out of a short piece of raw text (reusing L02's structured-output-by-instruction discipline, now returned as a typed state update instead of a hand-parsed script variable). <!-- *NEED INPUT*: confirm the exact domain/text for the extract node — recommend reusing a support-ticket-style snippet so L04 (whose first node is also a `parse`/extract step over support tickets) can plausibly be read as "the next lesson takes this exact kind of node and adds two more." A different, unrelated domain is also fine if the intent is to keep L03 visually distinct from L04's running example. -->
- **The one-node graph definition in a sibling file** to paste if live-coding falls behind.
- LangGraph's own run/stream output ready to call (`stream()` on the compiled graph) — **not** Langfuse. Real trace tooling is [L12](../L12/objectives.md); name it as a forward pointer, don't reach for it.

> Why one node, one model, one dataset: L03's entire pedagogical job is to make "what is a node" land cleanly before any wiring exists. Every extra moving part (a second model, a second node, a tracing platform) borrows attention from that one idea and belongs to a later lesson instead.

## Demo 1 — Wrapping one LLM call as a typed node (Objectives 1 & 2)

**Goal:** take a plain L01/L02-style model call and show, step by step, what changes when it becomes a **node**: a typed state schema appears, the function signature becomes state-in/state-out, and the model client switches from `potato_llm` to native `ChatAnthropic`. Land the **purity contract** — same relevant state in, same shape of update out, no hidden reads or side effects beyond the one LLM call.

**Pre-flight:**

- A short reminder cell showing the L01/L02-style call: a plain function that takes a string, builds a prompt, calls `potato_llm`, and returns a parsed dict. Keep this on screen as the "before."
- The `extract` task's target fields and one sample input text ready to paste.

**Live script:**

1. Put the "before" cell on screen: a bare function calling `potato_llm` and returning a dict. Ask nothing of the room — this is a recap, not a quiz — just point at it and say: "this is everything you know how to do already."
2. Live-code the **typed state** schema: a `TypedDict` with an input field (e.g. `raw_text: str`) and the output fields the node will populate (e.g. `extracted_fields: dict`). Keep it to two or three fields — this is the smallest state that makes the point.
3. Live-code the **node** as a plain typed function: `def extract_node(state: ExtractState) -> dict:`. Inside, build the same structured-output prompt from L02 (ask for a shape, e.g. JSON with named fields), but call it through **`ChatAnthropic`** instead of `potato_llm`. Say the departure out loud: *"the framework brings its own client — this is the first of a few you'll meet."*
4. Parse the model's response defensively (the same discipline from L02 Demo 2 — `json.loads` first, a regex fallback second) and **return a state update**, not the raw model response: `return {"extracted_fields": parsed}`. Underline that the function returns *an update*, not "the answer."
5. Put the "before" and "after" functions side by side. Walk the diff out loud: same underlying API call, same structured-output discipline from L02 — what changed is the *signature* (state in, state-update out) and the *client* (`ChatAnthropic`, not `potato_llm`).

**What to highlight:**

- **State goes in, state comes out.** The node doesn't hand back "the answer" the way L01–L02 code did — it hands back an *update* to a shared object. Say this is a small but real shift in mental model.
- **The purity contract.** Given the same relevant state, the node does the same unit of work and returns the same *shape* of update. What's non-deterministic is the model's sampling, not the function's contract — the function doesn't secretly read a global, mutate something outside state, or depend on call order.
- **This is the first framework lesson.** Name the client swap explicitly and don't let it pass silently: `potato_llm` was the course's own seam; `ChatAnthropic` is LangChain's. Both are still "just an API call" underneath.
- **The node's job is narrow on purpose.** One node does one unit of work — here, extraction. Chaining several narrow steps together is next lesson's entire subject.

**If the demo misbehaves:**

- If the model's structured output comes back malformed on the sample input, that's a free bonus — run the L02-style defensive parser live and show it absorbing the failure. Don't treat it as a demo failure; it reinforces the L02 callback.
- If a student asks "why does this need a `TypedDict` at all, a dict would work" — answer honestly: for *one* node it mostly would; the typed shape is the contract a *future* node (L04) will read without opening this node's source. The payoff isn't visible yet at one node.

## Demo 2 — Compile, invoke, and inspect one node in isolation (Objective 3)

**Goal:** take Demo 1's node and put it through the smallest possible `StateGraph`: one node, entry point, straight to `END`. Compile it, invoke it, and inspect the returned state. Use LangGraph's own stream output to "watch it run," and name — but do not use — real trace tooling as an L12 forward pointer.

**Pre-flight:**

- Demo 1's `extract_node` function and `ExtractState` schema, already defined and on screen.
- Two or three sample input texts of varying difficulty (one clean, one with a missing/ambiguous field) to invoke against.

**Live script:**

1. Live-code the graph: `builder = StateGraph(ExtractState)`, `builder.add_node("extract", extract_node)`, `builder.set_entry_point("extract")`, `builder.add_edge("extract", END)`. Say out loud that there is exactly **one** node and **one** edge, and that edge goes straight to `END` — there is nothing to wire yet, on purpose.
2. `graph = builder.compile()`. Note this turns the *declaration* into a *runnable* — nothing has executed yet.
3. `graph.invoke({"raw_text": sample_1})`. Show the returned state on screen: the `raw_text` field is still there unchanged, and `extracted_fields` is now populated. Point at both — the input survived, the output appeared.
4. Re-run with a second, harder sample text (missing or ambiguous field). Show the returned state again — reinforce that "state comes out" every time, even when the underlying extraction quality varies.
5. Call `graph.stream({"raw_text": sample_1}, stream_mode="updates")` and watch the single step fire — one chunk, `{"extract": {...}}` (the node name → the state update it wrote). Say explicitly: *"this is LangGraph's own built-in way to watch a run, one update per node — for one node it's almost overkill, but it's the **same call, in the same mode, you'll reuse the rest of the course**: to watch several nodes fire in sequence (L04), which branch runs (L05), and the agent loop turn (L10) — before routing that same run to a real tracer in L12."*
6. Forward-pointer, one line, do not demo it: *"Later, in L12, you'll route runs like this to a real tracing platform and read a structured trace — for now, the return value and the stream are all you need to answer 'did my node run, and what came back.'"*

**What to highlight:**

- **Compile then invoke is two separate steps.** Compiling declares the runnable; invoking runs it on a specific input. Worth saying plainly since students haven't seen this two-step shape before.
- **The returned state has both the old and the new.** `invoke()` doesn't return "just the output" — it returns the whole state, input field intact, output field populated. This is the direct, hands-on version of "state comes out."
- **More ceremony than just calling the function — and that's the point, not yet paid off.** Be honest: for one node, `graph.invoke(...)` is more setup than `extract_node_plain(sample_1)` would have been. The payoff is coming in L04, not here.
- **This is not tracing.** `stream()` shows *that* the node ran; it is not a substitute for the structured, comparable traces L12 will teach. Naming the gap now makes L12 land as "now you get the real tool," not a redundant repeat.

**If the demo misbehaves:**

- If `stream()`'s single-step output feels anticlimactic (it will — there's only one step), lean into it: *"one node, one step in the stream — next lesson this same call shows three or four steps firing in order, and it'll look a lot more interesting."*
- If a student asks to see the graph diagram rendered, it's fine to show it (`get_graph().draw_mermaid_png()` or the Mermaid text) as a curiosity, but don't build the lesson around it — a one-node diagram is nearly content-free. L04 is where the diagram earns its keep.

## Demo 3 — Why wire a node at all? (Objective 4)

**Goal:** a short contrast-and-discussion beat, not a build. Put Demo 1's clean node-based `extract_node` next to an equivalent "just write one long function" version that does extraction *and* a second, unrelated step inline. Use the comparison to land *why* an explicit, narrow step is the unit worth orchestrating — and close with the exact forward pointer to L04.

**Pre-flight:**

- Demo 1's `extract_node`, already on screen.
- A second, pre-written function — call it `extract_and_summarize_inline` — that does the same extraction *and* then, in the same function body with intermediate variables, drafts a one-line summary from the extracted fields. No state schema, no typed return — just sequential Python.

**Live script:**

1. Put both functions on screen side by side: `extract_node` (Demo 1's, one job, typed state in/out) and `extract_and_summarize_inline` (two jobs, one function, plain intermediate variables).
2. Ask the room to imagine a very small, concrete change: *"the extraction prompt needs a fourth field."* Walk each version: in `extract_node`, the edit is contained to the node's own prompt and parser — the state schema and the function signature might need a field, but nothing about "what calls this" changes. In `extract_and_summarize_inline`, the same edit still works, but now imagine testing extraction *alone* — you can't easily run just that half without also running (and paying for) the summarize half.
3. Name the concrete costs of the inline version out loud: harder to test one step alone, harder to swap the step's model or prompt without touching its neighbor, harder to see the shape of the pipeline at a glance (there is no diagram, no list of steps — just a function body).
4. Name the concrete benefit the node version buys back: it can be **composed**, **reordered**, **tested in isolation** (Demo 2 just did this), and **swapped out**, in ways the inline version resists.
5. Close with the exact forward pointer: *"L04 is this idea multiplied — the same typed-state-in, typed-state-out node design, several of them, wired with fixed edges into a sequence. If you understood today's one node, you already understand most of what L04 needs — it's mostly wiring, not new node design."* Say the bridge sentence from [objectives.md](objectives.md) verbatim: *"You just wired one step — next lesson, you wire several of them together."*

**What to highlight:**

- **This is a discussion, not a build.** No new code is written in this demo — the point is entirely in the comparison and the framing.
- **Be honest about the break-even point.** For a single node, the ceremony from Demos 1–2 is not obviously worth it over a plain function — say so. The value shows up the moment there's a second step, which is exactly next lesson.
- **Don't preview multi-node wiring mechanics.** It's fine to say "several of them, wired with fixed edges" as a *description*, but do not live-code two nodes or an edge here — that would pre-empt L04's own Demo 1, which builds exactly that from scratch.

**If the demo misbehaves:**

- If a student pushes back with "but I could just write good docstrings and keep my inline function organized" — that's a fair challenge, not a derail. Acknowledge it: discipline can get you partway there, but discipline isn't *enforced* by the language the way a typed state schema and a separate function are. Then return to the testability point (Demo 2 just ran the node alone) as the sharpest concrete difference.

## Pacing notes for the teacher

- **Per-demo time:** Demo 1 is the longest (15–20 minutes, including the before/after walkthrough and the client-swap discussion). Demo 2 is short (10–12 minutes — compile/invoke/inspect is mechanically quick). Demo 3 is a discussion beat (8–10 minutes, no live-coding). Total ~35–42 minutes plus discussion, fitting a lesson noticeably shorter than L02 or L04. <!-- *NEED INPUT*: confirm against the lesson-time budget once duration is pinned in objectives.md's open questions (current estimate there is 40–55 minutes). -->
- **Resist the urge to wire a second node "just to show what's coming."** It is tempting to tease L04 with a live two-node example — don't. L03's discipline is staying at one node; let L04 own that reveal on its own first day.
- **Reinforce L01/L02 vocabulary at every opportunity.** Tokens, cost, structured-output-by-instruction, defensive parsing. Every demo should read as "the thing you already know, now inside a node" rather than a wholesale new topic.
- **The audience watches, doesn't participate.** Resist "what field should we extract?" as a group question — that's a lab pattern. Hands-on node-building is for the L03 labs.

## Open authoring questions

- <!-- *NEED INPUT*: confirm the exact domain/text for the extract node (see Pre-flight) — recommend reusing a support-ticket-style snippet so L04's first node plausibly continues from it, but a distinct domain is also acceptable. -->
- <!-- *NEED INPUT*: confirm exact model id string for the Sonnet 4.6 snapshot used by ChatAnthropic, read from common/config.py rather than hard-coded in cells. Mirrored from the equivalent open question in L04's demos and in objectives.md. -->
- <!-- *NEED INPUT*: estimated lecture duration — demo pacing above sums to ~35–42 minutes; confirm this reconciles with the 40–55 minute estimate left open in objectives.md, and with the course's per-lesson time budget generally. -->
- <!-- *NEED INPUT*: are the demos run in a projected Jupyter notebook, a slide-embedded REPL, or a demo-runner script? Mirrors the same open question in L02's and L04's demos. -->
- <!-- *NEED INPUT*: should Demo 2 show the one-node graph diagram render (draw_mermaid_png/Mermaid text) as a brief curiosity, or skip it entirely as content-free at one node? Mirrors the same open question left in objectives.md. -->
