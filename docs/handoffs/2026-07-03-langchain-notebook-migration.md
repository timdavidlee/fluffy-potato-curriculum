# Handoff — migrate the tool/agent lesson notebooks to LangChain

**Status: DONE (2026-07-04).** All batches (A/B/C) landed — the `common/` runtime, every tool/agent
notebook (L07, L08, L10, L11, L12, L14, L22), and the L07/L08/L10 roadmaps are on LangChain. The final
prose follow-up also landed (L09 MCP lectures + the L11 roadmap: `tool_use`/`tool_result` →
`AIMessage.tool_calls`/`ToolMessage`). The one *out-of-scope* straggler (L04/L05/L12 roadmap prose,
tracked in a separate todo) has since been resolved too — as of 2026-07-06 a repo-wide grep for
`tool_use`/`tool_result` across `docs/origin/lesson_roadmaps/` returns zero hits, and that todo was
deleted. The in-progress detail below is kept as the historical record of how the work was staged.
**Date:** 2026-07-03 · **Slug owner:** curriculum LangChain migration

---

## 1. Goal & decision

Make the tool/agent code **model-agnostic** by driving every model call through a **LangChain chat
model** instead of the raw Anthropic SDK. Swap the provider prefix (`"anthropic:…"` → `"openai:…"`)
and the same code runs unchanged. User decision (2026-07-03): **"Full LangChain everywhere"** for
the tool/agent lessons — the raw Anthropic SDK is retired from the curriculum's loop/tool code.

Consequences of the decision, already accepted:
- L07 ("Tool calling: how it works") now teaches LangChain's **normalized** `.tool_calls`
  interface, **not** the raw Anthropic `tool_use`/`tool_result` wire blocks. The "reach under the
  seam to the raw SDK" framing is **removed**.
- `potato_llm` (the hand-rolled seam) is now used **only in L01–L02** (text-in/text-out). From L03
  on, everything — graphs, tools, the loop, eval — uses LangChain.

See memory `[[project_provider_abstraction]]` for the full decision record.

## 2. What is already done (do not redo)

Migrated and merged in PR #19 — the `common/` runtime layer + its tests, gate green (pyright 0,
pytest passing):

- **`common/agent_loop.py`** — `run()` drives a LangChain chat model. New signature:
  `run(model, tools, user_msg, max_steps=8)` (the old `tool_schemas` / `model_name` params are
  **gone** — it binds `tools` itself). `dispatch(tools, call)` returns a `ToolMessage`.
  `DEFAULT_MODEL = "anthropic:claude-sonnet-4-6"`. `RunResult(final_text, iterations, termination, trace)`
  is unchanged, and the `TraceEvent` schema is unchanged.
- **`common/fake_model.py`** — `FakeModel` now mimics a LangChain chat model: `.bind_tools(tools)`
  (returns self) + `.invoke(messages)` (returns the next scripted `AIMessage`). Build scripts with
  `text_reply(...)` / `tool_reply(...)` / `tool_call(...)`. The old `response` / `text_block` /
  `tool_use_block` helpers are **removed**.
- **`common/tools.py`** — `TOOLS` (name→function, for dispatch) unchanged; **`TOOL_SCHEMAS` removed**,
  replaced by **`TOOL_LIST`** (the functions, to pass to `model.bind_tools(TOOL_LIST)`).
- Docstrings / `common/CLAUDE.md` updated (incl. stale reorder lesson-refs the renumber missed).

**Verified:** both `ChatAnthropic(model="claude-sonnet-4-6")` and
`init_chat_model("anthropic:claude-sonnet-4-6")` type-check as valid `run()` arguments.

## 3. The before → after patterns (apply these in the notebooks)

### 3a. Scripted offline model (used in L11/L12 reading & lab cells, and any offline demo)

```python
# BEFORE
from fluffy_potato_curriculum.common.fake_model import (
    FakeModel, response, text_block, tool_use_block,
)
model = FakeModel([
    response([tool_use_block("c1", "calculator", {"expression": "17*23"})]),
    response([text_block("17*23 is 391.")]),
])

# AFTER
from fluffy_potato_curriculum.common.fake_model import (
    FakeModel, text_reply, tool_call, tool_reply,
)
model = FakeModel([
    tool_reply(tool_call("c1", "calculator", {"expression": "17*23"})),
    text_reply("17*23 is 391."),
])
```

### 3b. A real model call with tools (L07/L08/L10 demo & solution cells)

```python
# BEFORE (raw Anthropic SDK)
import anthropic
from fluffy_potato_curriculum.common.tools import TOOL_SCHEMAS
client = anthropic.Anthropic(api_key=require_anthropic_key())
resp = client.messages.create(model=SONNET, max_tokens=512, tools=TOOL_SCHEMAS, messages=messages)
for block in resp.content:
    if block.type == "tool_use":
        name, args, call_id = block.name, block.input, block.id
# return a result:
messages.append({"role": "user", "content": [
    {"type": "tool_result", "tool_use_id": call_id, "content": out},
]})

# AFTER (LangChain, model-agnostic)
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, ToolMessage
from fluffy_potato_curriculum.common.tools import TOOL_LIST
model = init_chat_model("anthropic:claude-sonnet-4-6")   # or ChatAnthropic(model="claude-sonnet-4-6")
bound = model.bind_tools(TOOL_LIST)
ai = bound.invoke(messages)                 # -> AIMessage
for call in ai.tool_calls:                  # each: {"name", "args", "id"}
    name, args, call_id = call["name"], call["args"], call["id"]
messages.append(ai)                         # record the assistant turn
messages.append(ToolMessage(content=out, tool_call_id=call_id))
```

Key shape changes: `resp.content` blocks → `ai.tool_calls` (a list of dicts); `block.input` →
`call["args"]`; `tool_result` dict → `ToolMessage(content=..., tool_call_id=...)`; the assistant
turn is the `AIMessage` object itself (append it, don't rebuild it). Token usage:
`resp.usage.input_tokens` → `ai.usage_metadata["input_tokens"]`.

### 3c. Using the canonical loop (L11 tracing, L12 eval)

```python
from fluffy_potato_curriculum.common.agent_loop import run
from fluffy_potato_curriculum.common.tools import TOOLS
result = run(model, TOOLS, "what is 17*23?", max_steps=8)   # model = any bind_tools-capable chat model
#          ^ no more tool_schemas= / model_name= kwargs
```

### 3d. Labs that were "fully offline" via a homemade `StubChat`

The L04/L05 lab `StubChat` is **text-only** (`.invoke(prompt).content -> str`) and does **not**
support tool calls. For a *tool/loop* lab, use `common.fake_model.FakeModel` scripted with
`tool_reply`/`text_reply` instead (it exposes `.bind_tools()` + `.invoke()` and returns an
`AIMessage` with `.tool_calls`) — that keeps labs offline, deterministic, and keyless while
matching the real interface. Do **not** invent a new tool-capable StubChat unless a lab genuinely
needs one; `FakeModel` already is it.

## 4. Remaining work — batches (each is one PR)

Item files flagged below still import removed symbols or call `.create(...)` / build raw
`tool_use`/`tool_result` blocks. Some flags are **prose-only** (a lecture explaining the concept) —
those need framing updates, not code rewrites; the heavy ones are code cells.

### Batch A — L07 (Tool calling) + L08 (Designing good tools)
The biggest reframe: L07 stops teaching raw `tool_use`/`tool_result` and teaches `.bind_tools()` +
`.tool_calls` + `ToolMessage`.
- **L07:** `L0701_intro.md`, `L0702_lecture.md`, `L0703_lecture.ipynb`, `L0704_lecture.ipynb`,
  `L0705_lab_empty/solutions.ipynb`, `L0706_lecture.ipynb`, `L0707_lab_empty/solutions.ipynb`,
  `L0708_lecture.ipynb`, `PROCTOR_NOTES.md`.
- **L08:** `L0801_intro.md`, `L0803_lecture.ipynb`, `L0805_lecture.ipynb`, `L0807_lecture.ipynb`,
  `L0809_lecture.ipynb`, `PROCTOR_NOTES.md`.

### Batch B — L10 (Hand-rolled loop) + L11 (Tracing) + L12 (Eval)
L10 hand-rolls the loop against a LangChain chat model (`.invoke()` → check `.tool_calls` → append
`ToolMessage`). L11/L12 trace & eval the migrated `common/` loop and swap the `FakeModel` script API.
- **L10:** `L1001_intro.md`, `L1002_lecture.md`, `L1003_lecture.ipynb`,
  `L1004_lab_empty/solutions.ipynb`, `L1005_lab_empty/solutions.ipynb`, `L1006_lecture.ipynb`,
  `PROCTOR_NOTES.md`.
- **L11:** `L1102_lecture.ipynb`, `L1103_lab_empty/solutions.ipynb`, `L1104_lecture.ipynb`,
  `L1105_lab_empty/solutions.ipynb`.
- **L12:** `L1202_lecture.ipynb`, `L1203_lab_empty/solutions.ipynb`, `L1204_lecture.ipynb`,
  `L1205_lab_empty/solutions.ipynb`, `L1206_lecture.ipynb`.

### Batch C — L14 (Shallow agent) + L22 (Skills) + roadmaps + potato_llm docs
Likely lighter (L14 already uses `ChatAnthropic` for the graph; the flags are mostly the
tool_use/tool_result *concept* in prose plus the `common/` import).
- **L14:** `L1401_intro.md`, `L1402_lecture.md`, `L1403_lecture.ipynb`, `L1405_lecture.ipynb`,
  `L1406_lab_empty/solutions.ipynb`.
- **L22:** `L2203_lecture.ipynb`, `L2204_lab_empty/solutions.ipynb`.
- **Docs:** update the L07/L08/L10 roadmaps under `docs/origin/lesson_roadmaps/` to drop the
  raw-SDK framing; update `src/fluffy_potato_curriculum/potato_llm/CLAUDE.md` to say the seam is
  L01–L02 only and LangChain is the through-line from L03 on.

## 5. Conventions to follow (unchanged)

- **Notebook rules:** `.claude/rules/notebooks.md` — numbered-heading TOC, `<a id="top">` +
  back-to-top anchors, ≤ ~25 cells, one concept per notebook, **clear outputs on `_empty` labs**,
  live-by-default with a `LIVE = bool(get_settings().anthropic_api_key)` gate so a keyless
  restart-run-all still passes. Edit notebooks via the `NotebookEdit` tool, not raw JSON.
- **Keys** load through `common/config.py` (`require_anthropic_key()` / `get_settings()`), never
  hard-coded.
- **Model ids** `claude-sonnet-4-6` / `claude-haiku-4-5` are placeholders pending an open
  `<need input>` on the exact snapshot string — keep them consistent, don't invent new ones.
- **Anchors:** Sonnet 4.6 for heavy steps, Haiku 4.5 for light ones (see `[[project_anchor_model]]`).

## 6. Verification checklist (per lesson, before its PR)

1. No removed symbols remain: `grep -rE 'text_block|tool_use_block|TOOL_SCHEMAS|\.create\(|anthropic\.Anthropic|response\(\[' <lesson dir>` returns nothing in code cells (a prose mention of "tool_result" while explaining history is acceptable only if it doesn't imply the course still uses it).
2. Notebooks parse as JSON and follow notebooks.md (TOC, anchors, cell budget, `_empty` outputs cleared).
3. Offline path is keyless-clean; live cells are `LIVE`-gated.
4. Gate green: `uv run ruff format && uv run ruff check && uv run pyright && uv run pytest`.
5. Item-file cross-refs still resolve (the repo-wide `L####_...` resolution sweep — see the renumber history).

## 7. Related artifacts

- Landing PR: #19 (`2377969`). Tracking note: `docs/todos/2026-07-03-langchain-notebook-migration.md`.
- Decision record: memory `[[project_provider_abstraction]]` (updated 2026-07-03).
- The migrated code to read as the reference for the new API: `src/fluffy_potato_curriculum/common/{agent_loop,fake_model,tools}.py` and `tests/common/test_{agent_loop,fake_model,evals}.py`.
