# Why wire a node at all? Node vs. one long function

```yaml
title: "Why wire a node at all? Node vs. one long function"
keywords: langgraph, node, pure function, composability, testability, break-even, workflow, why a graph, bridge to l04
estimated duration: 9
```

> **Lesson:** L03 — Single-node operations. Wrap-up discussion (Demo 3 in the
> [roadmap](../../../../docs/origin/lesson_roadmaps/L03/demos_or_activities.md)).
> This is a **discussion beat, not a build** — no new code. It reuses the `extract_node` from the
> build demo ([L0303_lecture.ipynb](L0303_lecture.ipynb)) as one side of a comparison. The one line
> to leave with: *you built the unit; the payoff arrives when you start wiring units together.*

## section 1. Node vs. one long function

### slide 1.1 The same job, written two ways

- On the left, the `extract_node` you just built: **one job**, a typed state in, a state update out.
- On the right, the *inline* version — one long function that extracts the fields **and** drafts a
  one-line summary from them, in the same body with intermediate variables.
- No state schema, no typed return, no graph — just sequential Python. It *works*. So why did we go
  to the trouble of a `StateGraph` for a single node?
- diagram: two panels side by side — left, a single clean **cyan** `extract_node` box labeled
  `typed state in → state update out` (the cyan border *is* the seam); right, one wide **coral**
  `extract_and_summarize_inline` box with two fused calls (`extract` + `summarize`) crammed inside
  it, no seam between them. This node box is the deck's motif — slides 1.2, 2.1, 2.2, and 4.1
  re-draw the *same* box with exactly one thing changed each time.

### slide 1.2 The tell: try to test extraction alone

- Try a tiny change — **the extraction prompt needs a fourth field.** In `extract_node` the edit is
  contained: the node's prompt and parser change, the state gains a field, and nothing about *what
  calls it* moves.
- The inline version takes the same edit too — but now **test extraction alone.** You can't run just
  that half without also running (and paying for) the summarize half. The two jobs are **fused**.
- diagram: the slide-1.1 two-up again, one change — a coral ✂ / ✗ trying (and failing) to cut
  between the fused `extract` + `summarize` calls in the coral inline block ("no seam to test one
  half"); beside it the same cyan `extract_node` box, now wearing a dashed testable boundary around
  its single step.

## section 2. What the node buys you

### slide 2.1 Four affordances of a narrow node

- Naming it plainly — the node version can be tested, composed, swapped, and seen; the inline
  function gives you none of these seams.
- table: what an explicit node gives you that an inline function does not.

| Affordance | The node version | The inline function |
| --- | --- | --- |
| Tested in isolation | `ainvoke()` the one node, inspect its output | no seam to test one step alone |
| Composed & reordered | a unit an orchestrator can plug in, drop, or move | can't wire a step you never separated out |
| Swapped | model / prompt changes without touching neighbors | internals and callers are tangled |
| Seen at a glance | inspectable data (`draw_mermaid()`, nodes + edges) | you must read the body to know its shape |

- diagram: the slide-1.1 two-up again, one change — the four affordances pinned on: left, the same
  cyan `extract_node` box with four labeled seams (`ainvoke alone` · `compose` · `swap` · `draw`);
  right, the coral fused box with the same four labels struck through — "no seam, no affordance."

### slide 2.2 The through-line

- An explicit, **narrow** step is the unit worth orchestrating.
- The ceremony exists to make one LLM call **reusable and inspectable** instead of a one-off.
- diagram: the same cyan `extract_node` box, alone — the one change this time: a dashed ink-faint
  ghost row of future nodes trailing off to its right, labeled "lands in L04," pre-echoing the
  slide-4.1 chain.

## section 3. Be honest about the break-even

### slide 3.1 One node: not obviously worth it

- For a **single** node, the ceremony is not obviously worth it over a plain function — and you
  should say so out loud. `await extract_app.ainvoke({"raw_text": ...})` is more setup than
  `extract_plain(...)`.
- Discipline (good docstrings, tidy functions) gets an inline version partway to "organized." The
  difference: a typed state schema and a separate node make the seam **enforced by the structure**,
  not merely by a convention you have to keep up.
- The value shows up the moment there is a **second step** — which is exactly the next lesson.
- diagram: a break-even chart — x-axis "number of steps," two cost/complexity curves: `plain function`
  in **coral** (low at 1 step, rising steeply as steps grow — the cost you pay later) and
  `graph of nodes` in **cyan** (higher fixed start, near-flat), crossing just after step 1, with the
  crossover point labeled "payoff starts at step 2."

## section 4. The bridge to L04

### slide 4.1 One step now, several next

- [L04](../../../../docs/origin/lesson_roadmaps/L04/objectives.md) is this idea **multiplied** — the
  same typed-state-in, state-update-out node design, several of them, wired with fixed edges into a
  sequence.
- If you understood today's one node, you already understand most of what L04 needs: it is mostly
  **wiring**, not new node design.
- diagram: reuse the slide-1.1 node box — the same cyan `extract_node` box on the left, an arrow to
  three chained copies of it (`extract → summarize → format`) joined by fixed cyan edges: the
  slide-2.2 ghost row drawn solid — "one step now → several wired next."

> **You just wired one step — next lesson, you wire several of them together.**
