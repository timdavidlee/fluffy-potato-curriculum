---
description: Lint (and format-check) the codebase with ruff
model: haiku
---

Run the ruff lint gate for this repo and report results.

1. `uv run ruff format --check` — verify formatting (don't reformat unless asked).
2. `uv run ruff check` — lint with the configured rule sets (`E/W`, `F`, `I`, `B`, `UP`, `SIM`, `RUF`).

If there are failures:
- For mechanical issues, offer to apply `uv run ruff format` and `uv run ruff check --fix`.
- For real warnings, summarize each and fix by hand per [.claude/rules/python-style.md](../rules/python-style.md).

If `$ARGUMENTS` is provided, scope the commands to those paths instead of the whole repo.
