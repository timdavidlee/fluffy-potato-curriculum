"""Catalog parsing: tracks.toml + the filesystem scan of lesson item files."""

from __future__ import annotations

from pathlib import Path

import pytest

from fluffy_potato_curriculum.local_ui import catalog


def test_load_tracks_puts_full_first(lessons_dir: Path) -> None:
    names = [t.name for t in catalog.load_tracks(lessons_dir)]
    assert names == ["full", "mini"]


def test_load_tracks_reads_order(lessons_dir: Path) -> None:
    full = next(t for t in catalog.load_tracks(lessons_dir) if t.name == "full")
    assert full.lesson_ids == ["L01", "L02"]


def test_load_titles_maps_ids(lessons_dir: Path) -> None:
    assert catalog.load_titles(lessons_dir)["L01"] == "First lesson"


def test_load_lessons_finds_both(lessons_dir: Path) -> None:
    assert [lesson.lesson_id for lesson in catalog.load_lessons(lessons_dir)] == ["L01", "L02"]


def test_lesson_records_track_membership(lessons_dir: Path) -> None:
    l01 = next(lesson for lesson in catalog.load_lessons(lessons_dir) if lesson.lesson_id == "L01")
    assert l01.tracks == ["full", "mini"]


def test_scan_ignores_non_item_files(lessons_dir: Path) -> None:
    # notes.txt must not be counted; 5 real items live in L01.
    l01 = next(lesson for lesson in catalog.load_lessons(lessons_dir) if lesson.lesson_id == "L01")
    assert l01.item_count == 5


def test_items_are_ordered_intro_first_proctor_last(lessons_dir: Path) -> None:
    detail = catalog.load_lesson_detail("L01", lessons_dir)
    assert detail is not None
    assert [it.item_id for it in detail.items] == [
        "L0101_intro",
        "L0102_lecture",
        "L0103_lab_empty",
        "L0103_lab_solutions",
        "PROCTOR_NOTES",
    ]


@pytest.mark.parametrize(
    ("item_id", "expected_kind"),
    [
        ("L0101_intro", "intro"),
        ("L0102_lecture", "lecture"),
        ("L0103_lab_empty", "lab_empty"),
        ("L0103_lab_solutions", "lab_solutions"),
        ("PROCTOR_NOTES", "proctor_notes"),
    ],
)
def test_item_kind_derived_from_filename(
    lessons_dir: Path, item_id: str, expected_kind: str
) -> None:
    detail = catalog.load_lesson_detail("L01", lessons_dir)
    assert detail is not None
    item = next(it for it in detail.items if it.item_id == item_id)
    assert item.kind == expected_kind


def test_load_lesson_detail_unknown_returns_none(lessons_dir: Path) -> None:
    assert catalog.load_lesson_detail("L99", lessons_dir) is None


def test_load_lesson_detail_rejects_malformed_id(lessons_dir: Path) -> None:
    assert catalog.load_lesson_detail("L1", lessons_dir) is None


def test_find_item_resolves_to_real_path(lessons_dir: Path) -> None:
    found = catalog.find_item("L01", "L0101_intro", lessons_dir)
    assert found is not None
    _item, path = found
    assert path == lessons_dir / "L01" / "L0101_intro.md"


def test_find_item_unknown_returns_none(lessons_dir: Path) -> None:
    assert catalog.find_item("L01", "nope", lessons_dir) is None


def test_find_item_cannot_escape_lessons_tree(lessons_dir: Path) -> None:
    # A traversal-style item_id has no matching catalog entry, so it resolves to None
    # rather than reading an arbitrary file.
    assert catalog.find_item("L01", "../../tracks", lessons_dir) is None
