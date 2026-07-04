# common/

The shared runtime layer for the agent-arc lessons. Logic lands here once it's used by more
than one lesson, so every lesson traces and evaluates the *same* agent instead of re-deriving
it (see the reuse rule in [.claude/rules/python-style.md](../../../.claude/rules/python-style.md)).

## What lives here

- `config.py` — the **config seam**. `Settings` (a `pydantic-settings` model) reads API keys
  from the environment and a repo-root `.env`; the `require_*_key` helpers raise a clear error
  when a key is missing. All notebooks and clients load keys through here — never scatter
  `os.environ[...]` lookups or hard-code a key.
- `potato_llm` is the client seam that *uses* these keys; this is the config seam that
  *supplies* them. (The client lives one level up in [../potato_llm/](../potato_llm/CLAUDE.md).)
- `agent_loop.py` — the hand-rolled model → tool → model loop (canonical copy of what students
  build inline in L10), instrumented to emit a trace. `run()` drives a **LangChain chat model**
  (`model.bind_tools(...)` → `.invoke(messages)` → `AIMessage.tool_calls` → `ToolMessage`), so any
  `bind_tools`-capable model works — `ChatAnthropic`, `ChatOpenAI`, an `init_chat_model("provider:model")`
  handle, or the offline `FakeModel`. That is what makes the loop **provider-agnostic**.
- `tracing.py` — `TraceEvent`, an OpenTelemetry-shaped span model; the L12 teaching artifact,
  reused by L13 and the LangGraph lessons and exportable to Langfuse.
- `evals.py` — a tiny eval harness (`EvalCase`, `Scorer`, `evaluate`); the L13 artifact.
- `tools.py` — the shared, deterministic tools the loop dispatches (calculator, lookup, etc.).
- `fake_model.py` — a scripted, offline stand-in for a LangChain chat model (implements
  `.bind_tools()` + `.invoke()` returning scripted `AIMessage`s) so reading demos and labs run with
  no API key and no network, producing the same trace every time. Build scripts with `text_reply` /
  `tool_reply` / `tool_call`.

## Conventions

- **Instrumentation observes; it never changes control flow.** Tracing wraps the loop — if a
  trace ever altered a run's behavior, that's a bug.
- **Prefer the `FakeModel`/canned path in tests and CI**; live calls are for the demos where
  producing a fresh trace is the point. Same mocking stance as
  [.claude/rules/pytest.md](../../../.claude/rules/pytest.md).
- Each module owns its lesson's concept — check the module docstring for which L<NN> it backs
  before extending it. Tests mirror this dir at [tests/common/](../../../tests/common/).

See the root [CLAUDE.md](../../../CLAUDE.md) for the toolchain and the full pre-commit gate.
