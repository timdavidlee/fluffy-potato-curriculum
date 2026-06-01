---
description: Type-check the codebase with pyright (strict)
---

Run the pyright type gate for this repo and report results.

- `uv run pyright` — runs in **strict** mode (every public `def` fully annotated, no implicit `Any`).

If there are errors:
- Summarize each error with its `file:line`.
- Fix by tightening types per [.claude/rules/python-style.md](../rules/python-style.md) — narrow or
  cast untyped third-party values deliberately rather than letting `Any` propagate. Avoid
  `# type: ignore`; if unavoidable, scope it (`# pyright: ignore[reportX]`) with a one-line why.

If `$ARGUMENTS` is provided, scope pyright to those paths instead of the whole repo.
