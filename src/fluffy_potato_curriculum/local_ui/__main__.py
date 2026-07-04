"""Run the lesson viewer: ``uv run python -m fluffy_potato_curriculum.local_ui``.

Serves on http://127.0.0.1:8000/ by default; override with ``HOST`` / ``PORT``.
"""

from __future__ import annotations

import os

import uvicorn

from fluffy_potato_curriculum.local_ui.app import create_app


def main() -> None:
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    # RELOAD=1 restarts the server on code changes. Reload needs an import
    # string (so the worker can re-import) rather than a live app instance, so
    # we point uvicorn at create_app as a factory instead of calling it here.
    reload = os.environ.get("RELOAD", "").lower() in {"1", "true", "yes"}
    if reload:
        uvicorn.run(
            "fluffy_potato_curriculum.local_ui.app:create_app",
            host=host,
            port=port,
            reload=True,
            factory=True,
        )
    else:
        uvicorn.run(create_app(), host=host, port=port)


if __name__ == "__main__":
    main()
