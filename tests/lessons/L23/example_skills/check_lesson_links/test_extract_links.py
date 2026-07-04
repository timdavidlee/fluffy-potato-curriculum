from pathlib import Path

import pytest

from fluffy_potato_curriculum.lessons.L23.example_skills.check_lesson_links.extract_links import (
    classify_target,
    extract_links,
    unresolved_file_links,
)


@pytest.mark.parametrize(
    ("target", "kind"),
    [
        ("https://example.com", "external"),
        ("mailto:a@b.io", "external"),
        ("#top", "anchor"),
        ("objectives.md", "file"),
        ("../L24/objectives.md", "file"),
    ],
)
def test_classify_target(target: str, kind: str) -> None:
    assert classify_target(target) == kind


def test_extracts_every_link() -> None:
    md = "see [a](a.md) and [t](#top) and [x](https://x.io)"
    assert len(extract_links(md)) == 3


def test_file_link_resolves_when_target_exists(tmp_path: Path) -> None:
    (tmp_path / "there.md").write_text("hi")
    links = extract_links("[here](there.md)", tmp_path)
    assert links[0].resolves is True


def test_file_link_unresolved_when_missing(tmp_path: Path) -> None:
    links = extract_links("[gone](missing.md)", tmp_path)
    assert links[0].resolves is False


def test_path_anchor_resolves_on_path_part(tmp_path: Path) -> None:
    (tmp_path / "doc.md").write_text("x")
    links = extract_links("[sec](doc.md#section)", tmp_path)
    assert links[0].resolves is True


def test_anchor_resolves_is_none() -> None:
    assert extract_links("[t](#top)")[0].resolves is None


def test_file_resolves_is_none_without_base_dir() -> None:
    assert extract_links("[a](a.md)")[0].resolves is None


def test_unresolved_filter_selects_missing_files(tmp_path: Path) -> None:
    (tmp_path / "ok.md").write_text("x")
    md = "[ok](ok.md) [bad](nope.md) [ext](https://x.io)"
    unresolved = unresolved_file_links(extract_links(md, tmp_path))
    assert [link.target for link in unresolved] == ["nope.md"]
