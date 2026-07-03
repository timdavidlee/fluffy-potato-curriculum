#!/usr/bin/env bash
# Start the local, read-only lesson-viewer UI.
#
# Serves http://127.0.0.1:8000/ by default. Override the bind address with the
# HOST / PORT env vars, e.g. `HOST=0.0.0.0 PORT=9000 scripts/serve_ui.sh`.
# See src/fluffy_potato_curriculum/local_ui/CLAUDE.md for what it is.
set -euo pipefail

# Run from the repo root so uv picks up the pinned .venv regardless of cwd.
cd "$(dirname "$0")/.."

exec uv run python -m fluffy_potato_curriculum.local_ui
