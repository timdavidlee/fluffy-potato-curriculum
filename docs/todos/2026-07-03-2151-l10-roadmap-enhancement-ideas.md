# TODO — L10 roadmap enhancement ideas (not yet folded in)

**Date:** 2026-07-03
**Status:** open — candidate additions to the L10 (Cyclic graphs: the ReAct agent loop) roadmap, proposed but **not** yet written into `docs/origin/lesson_roadmaps/L10/`. Pick by value vs. the "keep notebooks short" budget — L10 already has 4 objectives + 2 optional extensions, so anything added should either replace weight or be clearly optional.

> **⚠️ Groomed 2026-07-06 — re-triage before applying.** The L10 roadmap and materials have been
> substantially reworked since this list was written (LangChain migration, gotcha coda,
> graph-trace repointing, diagram densification). Spot-checks against the current roadmap: the
> **checkpointer** primitive now appears there via the optional `interrupt`/approval-gate
> extension (adjacent to, but not the same as, the multi-turn-memory idea below), and the
> `add_messages`-appends beat is taught — but the **id-based-upsert nuance (#4)**, the
> **system-prompt beat (#1)**, **state-beyond-messages (#2)**, and the **`tools_condition` /
> `MessagesState` reveals (#3)** are still absent (zero grep hits). Re-read the current
> `docs/origin/lesson_roadmaps/L10/` before folding anything in.

## Already handled (don't re-do)
- **`graph.stream` as the "watch the loop" tool** — DONE on `feat/graph-stream-thread`: threaded L03 → L04 → L05 → L10 with a consistent `stream_mode="updates"`.
- **The hand-built → `create_agent` mapping table** — moved to L11 (see the sibling `...-l11-create-agent-mapping...` todo), since it belongs at the prebuilt reveal.

## Candidate core beats (teach before L11's `create_agent`)
1. **Where the system prompt lives.** In a hand-built `agent_node` *you* decide how the system message gets in (prepend a `SystemMessage`, or wrap the model). Concrete "you own this" beat; maps 1:1 to `create_agent(prompt=...)`. Cheap; closes a gap (the roadmap is currently vague on the system prompt).
2. **State can hold more than `messages`.** Because state is a `TypedDict`, students can add a field (a `step_count`, a scratchpad, retrieved docs) and read/write it in a node. This (a) explains *why* a graph beats a bare `while` loop, and (b) motivates **when to drop the prebuilt and hand-build** — the real L15/deep-agent decision. Worth a small core beat (even one added field), not just an aside.
3. **The prebuilt-reveal pair, made explicit.** L10 already reveals `ToolNode` as "the bookkeeping, prebuilt." Add the matching reveals: the hand-written `route` **is** `langgraph.prebuilt.tools_condition`, and the `TypedDict + add_messages` state **is** `MessagesState`. (This overlaps the L11 mapping-table todo — decide whether the *reveal* lives in L10 or is saved for L11.)
4. **`add_messages` is id-based upsert, not naive append.** Subtle but real: re-emitting a message with the same id *replaces* it. Visible when you build by hand; hidden by the prebuilt. One-line note.

## Candidate optional explorations (clearly optional; pick by time)
- **Checkpointer → multi-turn memory.** `compile(checkpointer=MemorySaver())` + a `thread_id`; two `invoke`s where the second remembers the first. Motivates `create_agent(checkpointer=...)`, and **shares the exact primitive with the existing `interrupt` extension** — pair them for efficiency. Keep to "it remembers"; full semantics are L17/L19.
- **Swap the model on the agent node** (Sonnet vs Haiku) and watch chaining depth change — clean foreshadow of L14 (choosing model power), proof the node is just a seam.
- **Parallel tool calls in one turn** — a task emitting two `.tool_calls` in one `AIMessage`; watch `ToolNode` run both and append two `ToolMessage`s. Deepens the "ToolNode runs all of them" line already in the roadmap.
- **Structured final answer** — deepen the existing `respond`-node extension into a real schema coercion, foreshadowing `create_agent(response_format=...)`.

## Keep OUT of L10 (scope guardrails)
Subgraphs, the `Send`/map-reduce API, supervisor/multi-agent (L15/L24), middleware (L16), full checkpointer/HITL semantics (L17/L19), token-level streaming. Name them as "later"; teaching them here blows the one-concept budget.

## Recommendation
If picking up: promote **#1** and **#2** to small core beats, decide where the **#3** reveals live (L10 vs L11 table), and offer the **checkpointer + model-swap** pair as the optional additions. Everything else is nice-to-have.
