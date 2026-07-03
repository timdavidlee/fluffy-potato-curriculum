"""A small local FastAPI server for browsing and reviewing lesson materials.

This is a *developer/reviewer* tool, not student-facing course code. It reads the
generated lesson materials under ``lessons/`` (intros, lecture notebooks/markdown,
lab notebooks, proctor notes) plus ``lessons/tracks.toml`` and serves a read-only
web UI so you can page through a whole track's worth of materials in a browser
instead of opening files one at a time.

Run it with::

    uv run python -m fluffy_potato_curriculum.local_ui

Then open http://127.0.0.1:8000/.
"""

from fluffy_potato_curriculum.local_ui.app import create_app

__all__ = ["create_app"]
