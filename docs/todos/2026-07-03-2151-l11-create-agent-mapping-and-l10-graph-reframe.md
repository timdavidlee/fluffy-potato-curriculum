# TODO — L11 (shallow agents): add the `create_agent` mapping table + reframe L10 as a graph

**Date:** 2026-07-03
**Status:** deferred — **another process is actively editing L11**; do NOT edit `lessons/L11/*` directly until that lands. This note captures the work so it isn't lost.
**Root cause:** L10 was redesigned from a plain-Python "hand-rolled loop" into a cyclic LangGraph `StateGraph` (merged as `54ba342`). L11 still talks about L10 as a hand-rolled loop, and never shows the explicit by-hand→prebuilt mapping that would make `create_agent` land as "the graph you already built, packaged."

## 1. Add an explicit "hand-built (L10) → `create_agent` (L11)" mapping table

Place it at L11's `create_agent` reveal. This table *is* the payoff of L10 building the graph by hand — it turns the prebuilt from a black box into "the thing you already wired":

| You wired by hand in L10 | `create_agent` gives you |
| --- | --- |
| `TypedDict` state + `add_messages` reducer | `MessagesState` (same thing, prebuilt) |
| `agent_node` = `bind_tools(...)` + `.invoke(...)` | `model` + `prompt` args |
| `ToolNode(tools, handle_tool_errors=True)` | `tools=` arg |
| your hand-written `route` function | the prebuilt `tools_condition` |
| `add_edge("tools","agent")` back-edge | built in |
| `recursion_limit`, `handle_tool_errors` | same knobs, exposed |

Teaching point: L10 already reveals `ToolNode` as "the bookkeeping, prebuilt"; showing that the hand-written `route` **is** `langgraph.prebuilt.tools_condition` is the same move for the *edge*. Two "oh, the framework just packaged what I wrote" beats.

## 2. Reframe L10 references in L11 materials (8 files) — "hand-rolled loop" → "the graph you wired by hand"

L11's hook shifts from *"you built the loop by hand in L10, `create_agent` packages it"* → *"you wired the agent **graph** by hand in L10 (agent node + `ToolNode` + conditional back-edge); `create_agent` builds that exact graph in one line."* This is a **tighter** bridge, not a weaker one.

Files that currently call L10 a "hand-rolled loop" (from `grep -rln -i "hand-rolled\|hand-built\|plain python loop"` on `lessons/L11/`):
- `L1101_intro.md`
- `L1102_lecture.md`
- `L1103_lecture.ipynb`
- `L1104_lab_empty.ipynb`, `L1104_lab_solutions.ipynb`
- `L1105_lecture.ipynb`
- `L1107_lecture.ipynb`
- `L1108_lecture.md`

## Related (broader ripple — track separately if it grows)

The same L10-is-now-a-graph reframe is still owed elsewhere:
- **L12 (tracing)** — ~7 files (`L1201_intro.md`, `L1202/L1204_lecture.ipynb`, `L1203/L1205` labs) still import `common/agent_loop.py` (the plain loop) and call L10 a "hand-rolled loop." Decide: re-point L12 to instrument the L10 **graph** (via the `stream` events students now learn from L03), or keep the plain-loop reference (`common/agent_loop.py` is unchanged and still runs). See the L10 reconcile todo.
- **L04 objectives/demos** — already reframed in the `feat/graph-stream-thread` branch (Bridge-to-L11 now says "built by hand as a graph in L10, prebuilt in L11").

## Verify when done
- L11 renders the mapping table at the `create_agent` reveal.
- `grep -rin "hand-rolled" lessons/L11/` returns nothing.
- The L10 → L11 hand-off reads: "you wired this graph by hand (L10) → here it is in one line (L11)."
