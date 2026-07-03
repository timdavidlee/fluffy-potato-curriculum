"""Rendering markdown and notebook items to HTML fragments."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fluffy_potato_curriculum.local_ui.catalog import find_item
from fluffy_potato_curriculum.local_ui.models import LessonItem
from fluffy_potato_curriculum.local_ui.render import render_item

_NB: dict[str, Any] = {
    "nbformat": 4,
    "cells": [
        {"cell_type": "markdown", "source": ["# Heading"]},
        {
            "cell_type": "code",
            "source": ["x = '<tag>'"],
            "outputs": [{"output_type": "stream", "name": "stdout", "text": ["out <tag>"]}],
        },
        {
            "cell_type": "code",
            "source": ["boom"],
            "outputs": [{"output_type": "error", "traceback": ["\x1b[31mError\x1b[0m: nope"]}],
        },
    ],
}


def _nb_item(tmp_path: Path) -> tuple[LessonItem, Path]:
    path = tmp_path / "nb.ipynb"
    path.write_text(json.dumps(_NB))
    item = LessonItem(
        item_id="L0101_lecture",
        lesson_id="L01",
        order=1,
        kind="lecture",
        fmt="notebook",
        title="1. Lecture",
        filename="nb.ipynb",
    )
    return item, path


def _md_item(tmp_path: Path) -> tuple[LessonItem, Path]:
    path = tmp_path / "doc.md"
    path.write_text("# Title\n\nHello.")
    item = LessonItem(
        item_id="L0101_intro",
        lesson_id="L01",
        order=1,
        kind="intro",
        fmt="markdown",
        title="1. Intro",
        filename="doc.md",
    )
    return item, path


def test_markdown_item_renders_heading(tmp_path: Path) -> None:
    item, path = _md_item(tmp_path)
    assert "<h1" in render_item(item, path)


def test_notebook_markdown_cell_rendered(tmp_path: Path) -> None:
    item, path = _nb_item(tmp_path)
    assert "<h1" in render_item(item, path)


def test_notebook_code_is_html_escaped(tmp_path: Path) -> None:
    item, path = _nb_item(tmp_path)
    # The literal ``<tag>`` in the source must be escaped, not emitted as an element.
    assert "&lt;tag&gt;" in render_item(item, path)


def test_notebook_code_is_syntax_highlighted(tmp_path: Path) -> None:
    item, path = _nb_item(tmp_path)
    # Pygments wraps highlighted code in a ``.highlight`` container.
    assert 'class="highlight"' in render_item(item, path)


def test_markdown_fenced_code_is_syntax_highlighted(tmp_path: Path) -> None:
    path = tmp_path / "doc.md"
    path.write_text("```python\nimport os\n```\n")
    item = LessonItem(
        item_id="L0101_intro",
        lesson_id="L01",
        order=1,
        kind="intro",
        fmt="markdown",
        title="1. Intro",
        filename="doc.md",
    )
    assert 'class="highlight"' in render_item(item, path)


def test_notebook_stream_output_rendered(tmp_path: Path) -> None:
    item, path = _nb_item(tmp_path)
    assert "nb-stream" in render_item(item, path)


def test_notebook_error_traceback_ansi_stripped(tmp_path: Path) -> None:
    item, path = _nb_item(tmp_path)
    html = render_item(item, path)
    assert "Error: nope" in html and "\x1b" not in html


def test_render_item_via_catalog_lookup(lessons_dir: Path) -> None:
    found = find_item("L01", "L0101_intro", lessons_dir)
    assert found is not None
    item, path = found
    assert "<h1" in render_item(item, path)
