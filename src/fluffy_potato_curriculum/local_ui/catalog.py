"""Build the lesson catalog by reading ``lessons/`` and ``lessons/tracks.toml``.

``tracks.toml`` is the single source of truth for track membership, order, and
titles (see ``lessons/CLAUDE.md``); this module layers a filesystem scan on top to
discover the individual item files inside each ``L<NN>/`` directory.

All functions take the ``lessons_dir`` root as a parameter (defaulting to the
real one) so tests can point them at a temporary tree.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any, cast

from fluffy_potato_curriculum.local_ui.models import (
    ItemFormat,
    ItemKind,
    LessonDetail,
    LessonItem,
    LessonSummary,
    Track,
)

LESSONS_DIR = Path(__file__).resolve().parent.parent / "lessons"
"""The real lesson-materials root, resolved relative to this file."""

# Item files are named ``L<NN><II>_<kind>.<ext>`` — e.g. ``L1102_lecture.ipynb``.
_ITEM_RE = re.compile(r"^L(?P<lesson>\d{2})(?P<order>\d{2})_(?P<kind>[a-z_]+)$")

_EXT_TO_FORMAT: dict[str, ItemFormat] = {".md": "markdown", ".ipynb": "notebook"}

_KIND_LABELS: dict[ItemKind, str] = {
    "intro": "Intro",
    "lecture": "Lecture",
    "lab_empty": "Lab (empty)",
    "lab_solutions": "Lab (solutions)",
    "proctor_notes": "Proctor notes",
}

# The kinds that appear as the ``_<kind>`` suffix on numbered item files. Values
# are the same strings, but typed as ``ItemKind`` so a filename match narrows.
_NUMBERED_KINDS: dict[str, ItemKind] = {
    "intro": "intro",
    "lecture": "lecture",
    "lab_empty": "lab_empty",
    "lab_solutions": "lab_solutions",
}

# PROCTOR_NOTES.md has no numeric index; sort it after every numbered item.
_PROCTOR_ORDER = 9999


def _item_title(kind: ItemKind, order: int) -> str:
    """Human label for the sidebar, e.g. ``"3. Lecture"`` or ``"Proctor notes"``."""
    label = _KIND_LABELS[kind]
    if kind == "proctor_notes":
        return label
    return f"{order}. {label}"


def _scan_items(lesson_dir: Path, lesson_id: str) -> list[LessonItem]:
    """Discover the item files in one lesson directory, in teaching order."""
    items: list[LessonItem] = []
    for path in lesson_dir.iterdir():
        if not path.is_file():
            continue

        if path.name == "PROCTOR_NOTES.md":
            items.append(
                LessonItem(
                    item_id="PROCTOR_NOTES",
                    lesson_id=lesson_id,
                    order=_PROCTOR_ORDER,
                    kind="proctor_notes",
                    fmt="markdown",
                    title=_item_title("proctor_notes", _PROCTOR_ORDER),
                    filename=path.name,
                )
            )
            continue

        fmt = _EXT_TO_FORMAT.get(path.suffix)
        if fmt is None:
            continue
        match = _ITEM_RE.match(path.stem)
        if match is None or match.group("lesson") != lesson_id[1:]:
            continue
        kind = _NUMBERED_KINDS.get(match.group("kind"))
        if kind is None:
            continue
        order = int(match.group("order"))
        items.append(
            LessonItem(
                item_id=path.stem,
                lesson_id=lesson_id,
                order=order,
                kind=kind,
                fmt=fmt,
                title=_item_title(kind, order),
                filename=path.name,
            )
        )

    items.sort(key=lambda it: (it.order, it.filename))
    return items


def _load_toml(lessons_dir: Path) -> dict[str, Any]:
    return tomllib.loads((lessons_dir / "tracks.toml").read_text())


def load_tracks(lessons_dir: Path = LESSONS_DIR) -> list[Track]:
    """Parse ``tracks.toml`` into ordered tracks (``full`` first, then the rest)."""
    data = _load_toml(lessons_dir)
    tracks: list[Track] = []
    # ``titles`` is metadata, not a track; every other table with an ``order`` is one.
    for name, table in data.items():
        if name == "titles" or not isinstance(table, dict):
            continue
        order = cast("dict[str, Any]", table).get("order")
        if not isinstance(order, list):
            continue
        ids = [str(x) for x in cast("list[object]", order)]
        tracks.append(Track(name=name, lesson_ids=ids))
    tracks.sort(key=lambda t: (t.name != "full", t.name))
    return tracks


def load_titles(lessons_dir: Path = LESSONS_DIR) -> dict[str, str]:
    """Map ``L<NN>`` -> human title from the ``[titles]`` table."""
    titles = _load_toml(lessons_dir).get("titles", {})
    if not isinstance(titles, dict):
        return {}
    return {str(k): str(v) for k, v in cast("dict[object, object]", titles).items()}


def load_lessons(lessons_dir: Path = LESSONS_DIR) -> list[LessonSummary]:
    """List every lesson present on disk, in numeric order, with track membership."""
    titles = load_titles(lessons_dir)
    tracks = load_tracks(lessons_dir)
    summaries: list[LessonSummary] = []
    for path in sorted(lessons_dir.iterdir()):
        if not path.is_dir() or not re.fullmatch(r"L\d{2}", path.name):
            continue
        lesson_id = path.name
        items = _scan_items(path, lesson_id)
        member_of = [t.name for t in tracks if lesson_id in t.lesson_ids]
        summaries.append(
            LessonSummary(
                lesson_id=lesson_id,
                number=int(lesson_id[1:]),
                title=titles.get(lesson_id, lesson_id),
                item_count=len(items),
                tracks=member_of,
            )
        )
    return summaries


def load_lesson_detail(lesson_id: str, lessons_dir: Path = LESSONS_DIR) -> LessonDetail | None:
    """Full detail (items included) for one lesson, or ``None`` if it doesn't exist."""
    if not re.fullmatch(r"L\d{2}", lesson_id):
        return None
    lesson_dir = lessons_dir / lesson_id
    if not lesson_dir.is_dir():
        return None
    titles = load_titles(lessons_dir)
    tracks = load_tracks(lessons_dir)
    items = _scan_items(lesson_dir, lesson_id)
    return LessonDetail(
        lesson_id=lesson_id,
        number=int(lesson_id[1:]),
        title=titles.get(lesson_id, lesson_id),
        item_count=len(items),
        tracks=[t.name for t in tracks if lesson_id in t.lesson_ids],
        items=items,
    )


def find_item(
    lesson_id: str, item_id: str, lessons_dir: Path = LESSONS_DIR
) -> tuple[LessonItem, Path] | None:
    """Resolve ``(lesson_id, item_id)`` to a catalog item and its on-disk path.

    The path is derived from the *catalog* (a real file we already discovered),
    never by joining the client-supplied ``item_id`` onto a directory — so a
    crafted ``item_id`` cannot escape the lessons tree.
    """
    detail = load_lesson_detail(lesson_id, lessons_dir)
    if detail is None:
        return None
    for item in detail.items:
        if item.item_id == item_id:
            return item, lessons_dir / lesson_id / item.filename
    return None
