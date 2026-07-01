---
description: Run the full pre-commit gate (format, lint, typecheck, tests)
model: sonnet
---

Run the complete pre-commit gate for this repo, in order, and report results.

1. `uv run ruff format` — format the code.
2. `uv run ruff check` — lint with the configured rule sets.
3. `uv run pyright` — type-check in strict mode.
4. `uv run pytest` — run the test suite.

Run them as a single chained command so a failure stops the gate:
`uv run ruff format && uv run ruff check && uv run pyright && uv run pytest`.

If a step fails:
- Summarize what failed (with `file:line` where relevant).
- Fix per [.claude/rules/python-style.md](../rules/python-style.md) and
  [.claude/rules/pytest.md](../rules/pytest.md), then re-run the gate.

If `$ARGUMENTS` is provided, scope the commands to those paths where it makes sense.
