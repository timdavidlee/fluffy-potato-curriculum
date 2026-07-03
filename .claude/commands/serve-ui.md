---
description: Start the local read-only lesson-viewer UI server
model: sonnet
---

Start the local lesson-viewer UI — a read-only FastAPI server for browsing the
generated `L<NN>/` materials (`.md` + `.ipynb`) in a browser. It's a
developer/reviewer tool, not student-facing course code.

Run it via the helper script (starts a long-running server, so run it in the
background):

```sh
scripts/serve_ui.sh
```

That wraps `uv run python -m fluffy_potato_curriculum.local_ui` and serves
**http://127.0.0.1:8000/**.

Notes:
- Override the bind address with env vars: `HOST=0.0.0.0 PORT=9000 scripts/serve_ui.sh`.
- It's read-only — it renders lesson files, never writes them. Safe to leave running.
- Source + shape: [local_ui/CLAUDE.md](../../src/fluffy_potato_curriculum/local_ui/CLAUDE.md).

After launching, report the URL and confirm the server came up (check the log for
the uvicorn "Application startup complete" line). To stop it, kill the background
process.

If `$ARGUMENTS` is provided, treat it as `HOST`/`PORT` overrides where sensible.
