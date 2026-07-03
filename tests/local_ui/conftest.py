"""Shared fixtures: a small fake ``lessons/`` tree the local_ui reads from.

Everything is built under ``tmp_path`` so tests never touch the real materials.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

_TRACKS_TOML = """
[full]
order = ["L01", "L02"]

[mini]
order = ["L01"]

[titles]
L01 = "First lesson"
L02 = "Second lesson"
"""

# A tiny but structurally-real notebook: one markdown cell, one code cell with a
# stream output, plus an error cell whose traceback carries an ANSI escape.
_NOTEBOOK: dict[str, Any] = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {},
    "cells": [
        {"cell_type": "markdown", "source": ["# Notebook heading\n", "Body text."]},
        {
            "cell_type": "code",
            "source": ["print('hi <b>')\n"],
            "outputs": [{"output_type": "stream", "name": "stdout", "text": ["hi <b>\n"]}],
        },
        {
            "cell_type": "code",
            "source": ["boom\n"],
            "outputs": [
                {
                    "output_type": "error",
                    "ename": "NameError",
                    "evalue": "boom",
                    "traceback": ["\x1b[31mNameError\x1b[0m: boom is not defined"],
                }
            ],
        },
    ],
}


@pytest.fixture
def lessons_dir(tmp_path: Path) -> Path:
    """Write a fake lessons tree and return its root."""
    root = tmp_path / "lessons"
    root.mkdir()
    (root / "tracks.toml").write_text(_TRACKS_TOML)

    l01 = root / "L01"
    l01.mkdir()
    (l01 / "__init__.py").write_text("")
    (l01 / "L0101_intro.md").write_text("# Intro\nWelcome.")
    (l01 / "L0102_lecture.md").write_text("## Lecture\nContent.")
    (l01 / "L0103_lab_empty.ipynb").write_text(json.dumps(_NOTEBOOK))
    (l01 / "L0103_lab_solutions.ipynb").write_text(json.dumps(_NOTEBOOK))
    (l01 / "PROCTOR_NOTES.md").write_text("# Proctor\nNotes.")
    # A stray file that must be ignored by the scanner.
    (l01 / "notes.txt").write_text("ignore me")

    l02 = root / "L02"
    l02.mkdir()
    (l02 / "L0201_intro.md").write_text("# L02 Intro")

    return root
