# L04 Proctor Notes

Covers the L04 lab: **L0404** (prompt chaining). Runs **fully offline** — a deterministic
`StubChat` stands in for `ChatAnthropic`, so no API key is needed and every run is reproducible.
The focus is **graph wiring** (state, nodes, edges, reducers), not model output. The lecture demo
([L0403](L0403_lecture.ipynb)) uses the real `ChatAnthropic` client; the lab deliberately doesn't,
so the wiring is the only variable.

> Keep repeating the lesson's spine: **in a workflow you wire the flow; the model lives inside the
> nodes.** L04 has no branches at all — every edge is fixed. Branching is [L05](../L05/objectives.md),
> next.

---

## L0404_lab problem 1 — The typed state

COMMON GOTCHAS:
- Forgetting the `add` reducer on `steps` — writing `steps: list[str]` instead of
  `steps: Annotated[list[str], add]`. Without it, each node *overwrites* `steps` and the final
  state shows only the last node's name. The symptom: `result["steps"] == ["policy_check"]` instead
  of all three. Have them re-read the reducer line in the lecture (section 2.3) — L03 never needed
  one; this is the first time a reducer matters.
- Importing `add` — it's `from operator import add` (already in the given setup cell). If they
  retype the import, watch for `from operator import add` vs. trying `+`.

UNBLOCKERS: Point at the docstring example in the solution-shaped prompt — five fields, only `steps`
is annotated. A `TypedDict` is just a class with typed attributes and no body logic.

TIME: 3–5 min. STRETCH: ask what reducer message history would need (append) — that's the L11 link.

## L0404_lab problem 2 — The three nodes

COMMON GOTCHAS:
- Returning the **whole state** instead of a partial update. A node returns only the fields it
  changed (`{"parsed": ..., "steps": ["parse"]}`), and LangGraph merges it. Returning everything
  usually still works but teaches the wrong model — correct it.
- Reading `reply` instead of `reply.content`. The stub (like `ChatAnthropic`) returns an object;
  the text is on `.content`. Wrap in `str(...)` to satisfy the typed return.
- Forgetting to `await` the `ainvoke(...)` call — a coroutine (not a reply) lands in the update,
  and `.content` fails. The nodes are `async def`, so every stub call is an `await`.
- Forgetting to append to `steps` in each node — then problem 4's path looks wrong.

UNBLOCKERS: Remind them which stub each node uses — `parse` → `haiku`, `draft`/`policy_check` →
`sonnet` — and that `policy_check`'s prompt must contain "compliance"/"policy" for the stub to
return an `OK:` verdict (it's keyword-driven on purpose).

TIME: 8–12 min. STRETCH: have them make `policy_check` a *plain Python* check (no model) — a node
need not call a model at all.

## L0404_lab problem 3 — Wire, compile, render

COMMON GOTCHAS:
- Mixing up `add_node("name", fn)` (string name + function) and `add_edge("a", "b")` (two string
  names). A frequent error is `add_edge(parse, draft)` passing the functions — pass the **names**.
- Forgetting `set_entry_point("parse")` → compile error or a graph that never starts.
- Forgetting the final `add_edge("policy_check", END)` → the run won't terminate cleanly.
- `END` is imported in setup (`from langgraph.graph import END`); don't quote it like a node name.

UNBLOCKERS: If compile fails, have them print the node/edge list mentally against the five-line recipe
in the lecture (section 2.1). The `draw_mermaid()` output is the fastest check that the shape is right.

TIME: 6–10 min. STRETCH: render `draw_mermaid_png()` if a renderer is available, else the Mermaid
text is fine.

## L0404_lab problem 4 — Run the workflow

COMMON GOTCHAS:
- Forgetting `steps: []` in the initial state. With the `add` reducer, omitting the starting list
  can raise or behave oddly — always seed it (`{"ticket": ..., "steps": []}`).
- Reaching for `chain_app.invoke(...)` — the nodes are async, so the graph runs with
  `await chain_app.ainvoke(...)` (a notebook cell can `await` at top level).
- Expecting the *draft text* to be stable. It's a stub, so here it is; with a real model the wording
  varies. The point is the **path** (`['parse','draft','policy_check']`) is stable — that's
  determinism.

UNBLOCKERS: If the path isn't all three names, send them back to problem 1 (reducer) or problem 2
(missing `steps` append).

TIME: 3–5 min. STRETCH: `ainvoke` on a different ticket and confirm the path is unchanged.

## L0404_lab problem 5 — From stub to real model (written)

EXPECTED ANSWER: Change only the **client construction** — `haiku = StubChat(HAIKU)` →
`haiku = ChatAnthropic(model=HAIKU, api_key=require_anthropic_key())` (same for `sonnet`). The
**node code never changes** because `StubChat` and `ChatAnthropic` share the same interface the nodes
rely on: `await .ainvoke(prompt)` → a reply with `.content`. That shared shape is exactly why a
seam/stub is swappable — the same point [L03's](../L03/objectives.md) lab problem 5 made with a
single node.

COMMON GOTCHAS: Students say "rewrite the nodes." Redirect: the nodes only `await .ainvoke(...)` and
read `.content` — that contract is identical, so the node bodies are untouched.

TIME: 3–5 min.
