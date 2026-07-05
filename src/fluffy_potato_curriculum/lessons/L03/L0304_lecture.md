<a id="top"></a>

# Why wire a node at all? Node vs. one long function

```yaml
title: "Why wire a node at all? Node vs. one long function"
keywords: langgraph, node, pure function, composability, testability, break-even, workflow, why a graph, bridge to l04
estimated duration: 9
```

> **Lesson:** L03 — Single-node operations. Wrap-up discussion (Demo 3 in the
> [roadmap](../../../../docs/origin/lesson_roadmaps/L03/demos_or_activities.md)).
> This is a **discussion beat, not a build** — no new code. It reuses the `extract_node` from the
> build demo ([L0302_lecture.ipynb](L0302_lecture.ipynb)) as one side of a comparison.

## Contents

- [1. The comparison](#1-the-comparison)
- [2. What the node buys you](#2-what-the-node-buys-you)
- [3. Be honest about the break-even](#3-be-honest-about-the-break-even)
- [4. The bridge to L04](#4-the-bridge-to-l04)

## 1. The comparison

Put two things side by side. On the left, the `extract_node` you just built: one job, a typed state
in, a state update out. On the right, imagine the *inline* version — one long function that extracts
the fields **and** then, in the same body with intermediate variables, drafts a one-line summary from
them:

```python
def extract_and_summarize_inline(raw_text: str) -> dict[str, object]:
    fields = parse_fields(sonnet.invoke(extract_prompt(raw_text)).content)
    summary = sonnet.invoke(f"Summarize these fields in one line: {fields}").content
    return {"fields": fields, "summary": summary}
```

No state schema, no typed return, no graph — just sequential Python. It *works*. So why did we go to
the trouble of a `StateGraph` for a single node?

Try a concrete, tiny change: **the extraction prompt needs a fourth field.** In `extract_node`, the
edit is contained — the node's prompt and parser change, the state schema gains a field, and nothing
about *what calls this* moves. In the inline version the same edit works too — but now try to **test
extraction alone.** You can't easily run just that half without also running (and paying for) the
summarize half. The two jobs are fused.

[↑ Back to top](#top)

## 2. What the node buys you

Naming it plainly, the node version can be:

- **Tested in isolation** — you did exactly this in the build demo: `invoke()` the one node, inspect
  its output, done. The inline function gives you no seam to test one step alone.
- **Composed and reordered** — a node is a unit an orchestrator can plug in, drop, or move. L04 is
  entirely about wiring several such units into a sequence; you can't wire a step you never separated
  out.
- **Swapped** — a node's model or prompt can change without touching its neighbors, because the
  neighbors only depend on the *state shape*, not the node's internals.
- **Seen at a glance** — a graph is inspectable data (`draw_mermaid()`, a list of nodes and edges).
  An inline function body is not; you have to read it to know the shape of the pipeline.

The through-line: an explicit, **narrow** step is the unit worth orchestrating. The ceremony exists to
make one LLM call *reusable and inspectable* instead of a one-off.

[↑ Back to top](#top)

## 3. Be honest about the break-even

For a **single** node, that ceremony is not obviously worth it over a plain function — and you should
say so out loud. `extract_app.invoke({"raw_text": ...})` is more setup than `extract_plain(...)`.
Discipline (good docstrings, tidy functions) can get an inline version partway to "organized." The
difference is that a typed state schema and a separate node function make the seam **enforced by the
structure**, not merely by a convention you have to keep up.

The value shows up the moment there is a *second* step — which is exactly the next lesson. L03's honest
position is: *you built the unit; the payoff arrives when you start wiring units together.*

[↑ Back to top](#top)

## 4. The bridge to L04

[L04](../../../../docs/origin/lesson_roadmaps/L04/objectives.md) is this idea multiplied — the same
typed-state-in, state-update-out node design, several of them, wired with fixed edges into a sequence.
If you understood today's one node, you already understand most of what L04 needs: it is mostly
*wiring*, not new node design.

> **You just wired one step — next lesson, you wire several of them together.**

[↑ Back to top](#top)
