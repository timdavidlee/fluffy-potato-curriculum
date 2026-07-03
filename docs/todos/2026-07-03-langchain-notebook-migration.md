# 2026-07-03 — LangChain notebook migration (foundation landed; notebooks pending)

**Decision (user):** the tool/agent lessons go **fully model-agnostic via LangChain** — the raw
Anthropic SDK is retired from the curriculum's loop/tool code in favor of a LangChain chat model
(`ChatAnthropic` / `init_chat_model("provider:model")`, `.bind_tools()`, `AIMessage.tool_calls`,
`ToolMessage`). See `[[project_provider_abstraction]]` memory.

## Done

- `common/agent_loop.py`, `common/fake_model.py`, `common/tools.py` migrated to the LangChain
  chat-model interface; `tests/common/` updated; gate green (pyright 0, pytest passing).
- `common/CLAUDE.md`, `common/*.py` docstrings updated (incl. stale reorder lesson-refs the
  earlier renumber missed).

## Pending — regenerate these notebooks (they still import removed symbols / call `.create(...)`)

`response` / `text_block` / `tool_use_block` (removed) → use `text_reply` / `tool_reply` /
`tool_call`. Raw `client.messages.create(..., tools=[...])` / `tool_use` / `tool_result` blocks →
`model.bind_tools(TOOL_LIST)` + `.invoke(messages)` → `AIMessage.tool_calls` + `ToolMessage`.
`TOOL_SCHEMAS` (removed) → `TOOL_LIST`.

- **L07** (Tool calling): L0703, L0704, L0705 (lab pair), L0708 — teach `.bind_tools()` +
  `.tool_calls` instead of raw `tool_use`/`tool_result`. Drop the "reach under the seam to the raw
  SDK" framing.
- **L08** (Designing good tools): L0803, L0805, L0807, L0809 — tools bound to a LangChain model.
- **L10** (Hand-rolled loop): L1003, L1004 (lab), L1005 (lab), L1006 — hand-roll the loop against
  a LangChain chat model (`.invoke()` → check `.tool_calls` → append `ToolMessage`), not the SDK.
- **L11** (Tracing): L1102, L1103 (lab), L1104, L1105 (lab) — trace the migrated `common/` loop;
  swap `FakeModel(response([...]))` for `FakeModel([tool_reply(...), text_reply(...)])`.
- **L12** (Eval): L1202, L1203 (lab), L1204, L1205 (lab), L1206 — same `FakeModel` API swap.
- **L14** (Shallow agent): L1407 — imports `common/`; confirm it aligns (LangGraph already uses
  `ChatAnthropic`, so this is likely light).
- **L22** (Skills): L2203, L2204 (lab) — uses the loop/tools; align to the new API.

## Also (Phase 4)

- Update L07/L08/L10 roadmaps (`docs/origin/lesson_roadmaps/`) to drop the raw-SDK framing.
- Update `potato_llm/CLAUDE.md` — the seam is now L01–L02 only; the framework client (LangChain)
  is the through-line from L03 on, including tools.
