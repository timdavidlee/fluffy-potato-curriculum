"""Render lesson item files to self-contained HTML fragments.

Two source formats: plain ``.md`` (rendered with the ``markdown`` library) and
``.ipynb`` notebooks (walked cell by cell into HTML here rather than via nbconvert,
so the output is a small fragment we fully control — no external template, no
``<html>`` wrapper, and no surprise CSS).
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any, cast

import markdown

from fluffy_potato_curriculum.local_ui.models import LessonItem

_MD_EXTENSIONS = ["fenced_code", "tables", "toc", "sane_lists"]


def _render_markdown(text: str) -> str:
    """Render a markdown document to an HTML fragment."""
    return markdown.markdown(text, extensions=_MD_EXTENSIONS)


def _source_to_text(source: Any) -> str:
    """Notebook cell ``source`` is a list of lines or a single string."""
    if isinstance(source, list):
        lines = cast("list[object]", source)
        return "".join(str(line) for line in lines)
    return str(source)


def _code_block(text: str) -> str:
    return f'<pre class="nb-code"><code>{html.escape(text)}</code></pre>'


def _render_output(output: dict[str, Any]) -> str:
    """Render one notebook cell output to HTML (text, rich data, or an error)."""
    output_type = output.get("output_type")

    if output_type == "stream":
        return (
            f'<pre class="nb-stream">{html.escape(_source_to_text(output.get("text", "")))}</pre>'
        )

    if output_type == "error":
        traceback = cast("list[object]", output.get("traceback", []))
        # Tracebacks carry ANSI colour codes; strip to plain text for display.
        joined = "\n".join(_strip_ansi(str(line)) for line in traceback)
        return f'<pre class="nb-error">{html.escape(joined)}</pre>'

    if output_type in ("execute_result", "display_data"):
        raw_data = output.get("data", {})
        if not isinstance(raw_data, dict):
            return ""
        data = cast("dict[str, Any]", raw_data)
        if "image/png" in data:
            b64 = _source_to_text(data["image/png"]).strip()
            return f'<img class="nb-image" alt="cell output" src="data:image/png;base64,{b64}">'
        if "text/html" in data:
            # Trusted local materials; render inline. Not for untrusted input.
            return f'<div class="nb-html">{_source_to_text(data["text/html"])}</div>'
        if "text/plain" in data:
            return (
                f'<pre class="nb-result">{html.escape(_source_to_text(data["text/plain"]))}</pre>'
            )

    return ""


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def _render_notebook(raw: str) -> str:
    """Render a ``.ipynb`` JSON document to an HTML fragment, cell by cell."""
    nb = cast("dict[str, Any]", json.loads(raw))
    cells = nb.get("cells", [])
    if not isinstance(cells, list):
        return ""
    parts: list[str] = []
    for cell in cast("list[dict[str, Any]]", cells):
        cell_type = cell.get("cell_type")
        source = _source_to_text(cell.get("source", ""))

        if cell_type == "markdown":
            parts.append(f'<div class="nb-md">{_render_markdown(source)}</div>')
        elif cell_type == "code":
            block = [f'<div class="nb-cell">{_code_block(source)}']
            outputs = cell.get("outputs", [])
            if isinstance(outputs, list):
                for output in cast("list[Any]", outputs):
                    if isinstance(output, dict):
                        block.append(_render_output(cast("dict[str, Any]", output)))
            block.append("</div>")
            parts.append("".join(block))
        # raw cells and unknown types are skipped
    return "\n".join(parts)


def render_item(item: LessonItem, path: Path) -> str:
    """Render a lesson item file at ``path`` to an HTML fragment."""
    raw = path.read_text()
    if item.fmt == "notebook":
        return _render_notebook(raw)
    return _render_markdown(raw)
