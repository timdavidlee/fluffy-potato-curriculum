# 2026-07-04 — Roadmap `tool_use`/`tool_result` prose drift (L04 / L05 / L12)

Spun off from the LangChain migration ([`2026-07-03-langchain-notebook-migration.md`](2026-07-03-langchain-notebook-migration.md),
now closed). That effort swept every tool/agent **lesson** plus the L07/L08/L10/L11 **roadmaps** to
`AIMessage.tool_calls` / `ToolMessage`. While closing it, three more roadmaps turned up with the same
`tool_use`/`tool_result` prose drift — these were **never in the migration's enumerated scope**, so
they're captured here as a separate, low-priority consistency pass.

All are **prose in stage-1 roadmaps** (no broken code). None is draft-marked. The migrated code is the
reference: `common/agent_loop.py` checks `AIMessage.tool_calls` and appends `ToolMessage`; tool
failures become `ToolMessage(status="error")` (see the migration handoff §3b).

## Open items

- **L04** `objectives.md:17` — **highest priority; factually contradicts the migration.** Still says
  the tool lessons "deliberately reach *under* the seam to the raw Anthropic SDK for `tool_use`
  blocks" and frames a now-obsolete "non-monotonic client story" (framework client at L03–L05, raw
  SDK at L07–L08). L07–L08 no longer use the raw SDK — they use LangChain `bind_tools` /
  `AIMessage.tool_calls`. This line also carries a `<need input: confirm framework-client-before-raw-SDK…>`
  marker that the migration decision has since resolved (LangChain everywhere from L03 on) — retire
  the marker as part of the fix.
- **L05** `objectives.md:52`, `objectives.md:89`, `demos_or_activities.md:142` — describe L11's
  conditional edge as reading "whether the model's last message contains a `tool_use`". In LangChain
  terms the router checks whether the last `AIMessage` has `tool_calls`; swap `tool_use` → `tool_calls`
  (or "the `AIMessage` has `tool_calls`"). The pedagogy (source-of-authority: model output vs.
  developer-owned state) is unchanged — only the token.
- **L12** `objectives.md:92` — "a `tool_result` with `is_error: true` (the L10 exception-to-`tool_result`
  conversion…)" → `ToolMessage(status="error")` (the L10 exception-to-`ToolMessage` conversion), matching
  the migrated loop.

## Not in scope

- The `input_schema` / `inputSchema` framing in **L09** (L0903 demo, L0904 lab, PROCTOR_NOTES) is
  **correct and load-bearing** — `input_schema` is Anthropic's genuine wire-format key, and the whole
  L09 offline demo/lab teaches "the tool spec is that JSON with one renamed key". Do **not** touch it.
