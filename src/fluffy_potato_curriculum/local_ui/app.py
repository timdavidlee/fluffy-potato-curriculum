# pyright: reportUnusedFunction=false
# ^ FastAPI route handlers are registered on the app via the @app.get(...)
#   decorators; pyright can't see that and would flag each as unused.
"""The FastAPI application: JSON endpoints over the catalog + a static frontend.

Endpoints (all read-only):

- ``GET /api/tracks``                     -> ``list[Track]``
- ``GET /api/lessons``                    -> ``list[LessonSummary]``
- ``GET /api/lessons/{lesson_id}``        -> ``LessonDetail``
- ``GET /api/lessons/{lesson_id}/items/{item_id}`` -> ``RenderedItem``
- ``GET /api/lessons/{lesson_id}/items/{item_id}/raw`` -> the item file as-is

The frontend (``static/index.html`` + ``app.js``) is a dependency-free single page that
calls these and injects the returned HTML fragment — except standalone ``.html`` slide
decks (full documents), which it opens from the ``/raw`` route in a new tab.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from fluffy_potato_curriculum.local_ui import catalog
from fluffy_potato_curriculum.local_ui.models import (
    LessonDetail,
    LessonSummary,
    RenderedItem,
    Track,
)
from fluffy_potato_curriculum.local_ui.render import render_item

_STATIC_DIR = Path(__file__).resolve().parent / "static"


def create_app(lessons_dir: Path = catalog.LESSONS_DIR) -> FastAPI:
    """Build the app. ``lessons_dir`` is injectable so tests use a temp tree."""
    app = FastAPI(title="Fluffy Potato — lesson viewer", docs_url="/api/docs")

    @app.get("/api/tracks")
    def get_tracks() -> list[Track]:
        return catalog.load_tracks(lessons_dir)

    @app.get("/api/lessons")
    def get_lessons() -> list[LessonSummary]:
        return catalog.load_lessons(lessons_dir)

    @app.get("/api/lessons/{lesson_id}")
    def get_lesson(lesson_id: str) -> LessonDetail:
        detail = catalog.load_lesson_detail(lesson_id, lessons_dir)
        if detail is None:
            raise HTTPException(status_code=404, detail=f"No such lesson: {lesson_id}")
        return detail

    @app.get("/api/lessons/{lesson_id}/items/{item_id}")
    def get_item(lesson_id: str, item_id: str) -> RenderedItem:
        found = catalog.find_item(lesson_id, item_id, lessons_dir)
        if found is None:
            raise HTTPException(status_code=404, detail=f"No such item: {lesson_id}/{item_id}")
        item, path = found
        if item.fmt == "html":
            # Standalone HTML slide decks are whole documents, not injectable
            # fragments — they're served verbatim from the ``/raw`` route instead.
            raise HTTPException(
                status_code=415,
                detail=f"{item_id} is a standalone HTML document; GET items/{item_id}/raw",
            )
        return RenderedItem(item=item, html=render_item(item, path))

    @app.get("/api/lessons/{lesson_id}/items/{item_id}/raw")
    def get_item_raw(lesson_id: str, item_id: str) -> FileResponse:
        """Serve an item's file as-is. Used for standalone ``.html`` slide decks, which
        are full documents opened in their own tab rather than injected as a fragment."""
        found = catalog.find_item(lesson_id, item_id, lessons_dir)
        if found is None:
            raise HTTPException(status_code=404, detail=f"No such item: {lesson_id}/{item_id}")
        _item, path = found
        return FileResponse(path)

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(_STATIC_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")
    return app
