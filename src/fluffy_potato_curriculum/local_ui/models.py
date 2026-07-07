"""Typed shapes for the lesson catalog the local UI serves.

These are the JSON payloads the frontend consumes. Kept deliberately small: the
UI needs enough to build a sidebar (tracks -> lessons -> items) and to fetch one
item's rendered HTML.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

ItemKind = Literal[
    "intro",
    "lecture",
    "lecture_deck",
    "lab_empty",
    "lab_solutions",
    "proctor_notes",
    "guide",
    "demo",
]
"""What role a file plays inside a lesson, derived from its filename.

``lecture_deck`` is a self-contained HTML slide deck that accompanies a lecture.
``guide`` and ``demo`` are the prework (``K<NN>``) kinds: a self-paced written guide and
its optional runnable demo notebook. The rest are the ``L<NN>`` lesson kinds.
"""

ItemFormat = Literal["markdown", "notebook", "html"]
"""How the file is stored — a ``.md`` document, a ``.ipynb`` notebook, or a standalone
``.html`` page (a self-contained lecture slide deck)."""


class LessonItem(BaseModel):
    """One file inside a lesson directory (e.g. ``L1102_lecture.ipynb``).

    ``item_id`` is the filename stem (``L1102_lecture``, or ``PROCTOR_NOTES``) and
    is what the content endpoint takes to look the file back up — never a raw path
    from the client, so there is no path-traversal surface.
    """

    item_id: str
    lesson_id: str
    order: int
    kind: ItemKind
    fmt: ItemFormat
    title: str
    filename: str


class LessonSummary(BaseModel):
    """A lesson as it appears in the sidebar list (no item bodies)."""

    lesson_id: str
    number: int
    title: str
    item_count: int
    tracks: list[str]


class LessonDetail(LessonSummary):
    """A single lesson with its full ordered item list."""

    items: list[LessonItem]


class Track(BaseModel):
    """A named course track (``full`` / ``mini``) as an ordered lesson list."""

    name: str
    lesson_ids: list[str]


class RenderedItem(BaseModel):
    """A lesson item plus its rendered HTML fragment, ready to inject.

    Example::

        {"item": {"item_id": "L1101_intro", ...}, "html": "<h1>...</h1>"}
    """

    item: LessonItem
    html: str
