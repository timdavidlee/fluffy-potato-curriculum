# 2026-07-03 — LangChain notebook migration (L07/L08 done; L22 + roadmaps remain)

**Decision (user):** the tool/agent lessons go **fully model-agnostic via LangChain** — the raw
Anthropic SDK is retired from the curriculum's loop/tool code in favor of a LangChain chat model
(`ChatAnthropic` / `init_chat_model("provider:model")`, `.bind_tools()`, `AIMessage.tool_calls`,
`ToolMessage`). See `[[project_provider_abstraction]]` memory.

## Done

- `common/agent_loop.py`, `common/fake_model.py`, `common/tools.py` migrated to the LangChain
  chat-model interface; `tests/common/` updated; gate green (pyright 0, pytest passing).
- `common/CLAUDE.md`, `common/*.py` docstrings updated (incl. stale reorder lesson-refs the
  earlier renumber missed).
- **L07** (Tool calling) — all 10 notebooks + the markdown companions migrated (notebooks in
  PR #38, markdown in PR #40). `ChatAnthropic().bind_tools([fn])` → `AIMessage.tool_calls` →
  `ToolMessage`; tool definition inferred from a typed `Annotated` function (no hand-written JSON
  schema). No `tool_use`/`tool_result`/`client.messages.create`/"under the seam" framing left.
  Empty-lab written answers still `_TODO_` (solutions filled); live restart-run-all still needs an
  `ANTHROPIC_API_KEY` run before class.
- **L08** (Designing good tools) — 4 lectures (L0803/L0805/L0807/L0809) + markdown migrated;
  `ToolMessage(status="error")` for the L0807 error path. L0806 schema-design lab recast around
  "the typed function *is* the schema": `Literal` → enum, `Annotated` → per-field description,
  no-default → required, inspected via `convert_to_openai_tool`. The other lab pairs
  (L0804/L0808/L0810) were already pure-Python design exercises — no model calls, left as-is
  (PR #40).
- **L10** (Hand-rolled loop): L1003, L1004, L1005, L1006 — verified migrated (`bind_tools` /
  `.tool_calls` / `ToolMessage`, no old symbols).
- **L11** (Tracing): L1102, L1103, L1104, L1105 — verified migrated.
- **L12** (Eval): L1202, L1203, L1204, L1205, L1206 — verified migrated.
- **L14** (Shallow agent): L1407 — verified migrated.

## Pending — regenerate these notebooks (they still import removed symbols / call `.create(...)`)

`response` / `text_block` / `tool_use_block` (removed) → use `text_reply` / `tool_reply` /
`tool_call`. Raw `client.messages.create(..., tools=[...])` / `tool_use` / `tool_result` blocks →
`model.bind_tools(TOOL_LIST)` + `.invoke(messages)` → `AIMessage.tool_calls` + `ToolMessage`.
`TOOL_SCHEMAS` (removed) → `TOOL_LIST`.

- **L22** (Skills): L2203, L2204 (lab) — uses the loop/tools; align to the new API.

## Also (Phase 4)

- Update L07/L08/L10 roadmaps (`docs/origin/lesson_roadmaps/`) to drop the raw-SDK framing.
  (L10 notebooks are already migrated, but its roadmap still describes `tool_use`/`tool_result`.)
- Update `potato_llm/CLAUDE.md` — the seam is now L01–L02 only; the framework client (LangChain)
  is the through-line from L03 on, including tools.
