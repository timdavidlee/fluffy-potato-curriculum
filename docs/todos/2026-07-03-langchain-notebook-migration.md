# 2026-07-03 — LangChain notebook migration (code done; L09/L11/L14 prose follow-up)

**Status: closed 2026-07-04.** All code batches plus the final prose follow-up (L09 MCP lectures + the
L11 roadmap) are aligned to `AIMessage.tool_calls` / `ToolMessage`. See the resolution note at the
bottom. A separate, newly-spotted roadmap drift (L04/L05/L12) is tracked in its own todo.

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
- **L22** (Skills): L2203 (JIT skill-loader demo) + L2204 lab pair migrated. `FakeModel` script
  via `text_reply` / `tool_reply` / `tool_call`; `load_skill` is a typed closure whose schema
  `bind_tools` infers; the loop is `model.bind_tools([load_skill])` → `.invoke([HumanMessage])` →
  `AIMessage.tool_calls` → append the body. Token readouts unchanged (`FakeModel` deterministic);
  gate green, empty lab cleared. (L2206 was already offline pure-Python — untouched.)

## Phase 4 — roadmaps + docs (done)

- **L07/L08/L10 roadmaps** (`docs/origin/lesson_roadmaps/`) re-vocabularized to LangChain. L07/L10
  carried the raw-protocol framing (`tool_use`/`tool_result` blocks, "the result goes in a
  *user-role* message", hand-written `input_schema`); reframed to `AIMessage.tool_calls` →
  `ToolMessage` (its own tool role, paired by `tool_call_id`), `bind_tools`-inferred schemas, and
  the `HumanMessage → AIMessage(tool_calls) → ToolMessage → AIMessage(final)` round-trip. The
  now-settled "which SDK" `*NEED INPUT*` markers were resolved to LangChain `ChatAnthropic`;
  unrelated open questions (model class, duration, lab design, parallel-call scope) left as-is.
  L08's roadmap only needed a light touch (no raw-protocol vocabulary there).
- **`potato_llm/CLAUDE.md`** reframed — the hand-rolled seam is the **L01–L02 teaching artifact**;
  LangChain `ChatAnthropic` is the through-line from L03 on (tools, the agent loop, tracing,
  evals), not a parallel client that grows alongside it.

**Retired code symbols fully removed.** No lesson notebook or roadmap still *calls* a retired
symbol — verified zero hits for `tool_use_block` / `text_block(` / `client.messages.create(` /
`TOOL_SCHEMAS` / `import anthropic` across `lessons/` and `lesson_roadmaps/`. The tool/agent
teaching arc (L07, L08, L10, L11, L12, L14, L22) and the L07/L08/L10 roadmaps now use LangChain
vocabulary throughout.

## Follow-up (resolved 2026-07-04)

`tool_use` / `tool_result` appeared as **conceptual / protocol prose** (not code) in a few downstream
lessons back-referencing "the L10 pairing invariant". Status after the 2026-07-04 consistency pass:

- **L09** (MCP) — ✅ done. `L0901_intro.md`, `L0902_lecture.md`, `L0905_lecture.md` re-vocabularized:
  the model emits an `AIMessage` with `tool_calls`; the client feeds the server's structured result
  back as a `ToolMessage`. The MCP wire step is now described as "returns a structured result" rather
  than borrowing Anthropic's `tool_result` block name (MCP's response is a `CallToolResult`, which the
  LangChain client wraps into a `ToolMessage` anyway).
- **L14** (LangGraph) — ✅ already clean; no `tool_use`/`tool_result` prose remains in `L1401`–`L1406`.
- **L11 roadmap** — ✅ done. `objectives.md` / `demos_or_activities.md` now describe the L10 loop as
  `AIMessage.tool_calls` → `ToolMessage` (tool failures → `ToolMessage(status="error")`).
- **L14 roadmap** — ✅ already clean.

**Migration follow-up closed.** A *separate*, newly-spotted drift — **out of this migration's scope** —
remains and is tracked in [`2026-07-04-1716-roadmap-tool-use-prose-drift.md`](2026-07-04-1716-roadmap-tool-use-prose-drift.md):
the **L04 / L05 / L12 roadmaps** still use `tool_use`/`tool_result` prose (L04 even still says L07–L08
"reach under the seam to the raw Anthropic SDK for `tool_use` blocks", contradicting this migration).
