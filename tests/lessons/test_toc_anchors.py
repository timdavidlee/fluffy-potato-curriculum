"""Guard against broken in-page TOC / back-to-top anchors in lesson materials.

Notebook tables of contents and ``[↑ Back to top]`` links are hand-authored
``](#slug)`` targets. When a heading is later reworded (or its punctuation
changes), the anchor silently stops resolving because GitHub rebuilds the
heading slug from the new text. This test walks every ``lessons/**`` markdown
document (``.md`` files and the markdown cells of ``.ipynb`` notebooks) and
asserts every same-document ``#anchor`` points at a real heading.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

import fluffy_potato_curriculum

LESSONS_DIR = Path(fluffy_potato_curriculum.__file__).parent / "lessons"

# Fenced code blocks (```...``` or ~~~...~~~) so a ``#`` comment or a ``](#...)``
# inside example code is not mistaken for a heading or an anchor link.
_FENCE = re.compile(r"(?ms)^([ \t]*)(`{3,}|~{3,}).*?^\1\2[ \t]*$")
_HEADING = re.compile(r"(?m)^#{1,6}\s+(.*)$")
_ANCHOR_LINK = re.compile(r"\]\(#([^)]+)\)")
_PUNCT = re.compile(r"[^\w\s-]", re.UNICODE)


def github_slug(heading: str) -> str:
    """Mirror GitHub's heading-slug algorithm (github-slugger).

    Lowercase, strip punctuation (keeping word chars, whitespace, and hyphens),
    then replace each remaining space with a hyphen *without* collapsing runs.
    So ``"Problem 1 — Foo: bar"`` -> ``"problem-1--foo-bar"`` (the em-dash is
    dropped but its surrounding spaces survive as a double hyphen).
    """
    s = heading.strip().lower()
    s = _PUNCT.sub("", s)
    return s.replace(" ", "-")


def _strip_fences(markdown: str) -> str:
    return _FENCE.sub("", markdown)


def _heading_slugs(markdown: str) -> set[str]:
    """All heading slugs, applying GitHub's ``-1``/``-2`` dedup for repeats."""
    seen: dict[str, int] = {}
    slugs: set[str] = set()
    for match in _HEADING.finditer(markdown):
        base = github_slug(match.group(1))
        count = seen.get(base, 0)
        slugs.add(base if count == 0 else f"{base}-{count}")
        seen[base] = count + 1
    return slugs


def _markdown_of(path: Path) -> str:
    """The markdown text of a doc: file body for ``.md``, joined markdown cells otherwise."""
    if path.suffix == ".md":
        return path.read_text(encoding="utf-8")
    nb: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    cells: list[dict[str, Any]] = nb["cells"]
    return "\n".join("".join(cell["source"]) for cell in cells if cell["cell_type"] == "markdown")


def _broken_anchors(markdown: str) -> list[str]:
    body = _strip_fences(markdown)
    headings = _heading_slugs(body)
    return sorted(
        {
            anchor
            for anchor in _ANCHOR_LINK.findall(body)
            if anchor != "top" and anchor not in headings
        }
    )


def _lesson_docs() -> list[Path]:
    docs = [
        p
        for p in LESSONS_DIR.rglob("*")
        if p.suffix in {".md", ".ipynb"} and ".ipynb_checkpoints" not in p.parts
    ]
    return sorted(docs)


@pytest.mark.parametrize(
    "doc",
    _lesson_docs(),
    ids=lambda p: str(p.relative_to(LESSONS_DIR)),
)
def test_in_page_anchors_resolve(doc: Path) -> None:
    broken = _broken_anchors(_markdown_of(doc))
    assert broken == [], f"{doc.relative_to(LESSONS_DIR)} has unresolved anchors: {broken}"
