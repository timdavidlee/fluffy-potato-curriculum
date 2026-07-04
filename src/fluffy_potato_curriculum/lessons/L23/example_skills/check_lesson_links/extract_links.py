"""Link-extraction helper for the L23 ``example-check-lesson-links`` shared skill.

Teaching material for L23. This is the *mechanical* half of the shared skill:
pull every Markdown link out of a document and say, for each one, whether its
target is an on-disk file (and if so, whether it exists), an in-page anchor, or
an external URL. Deciding what to *do* about an unresolved file link — a real
broken cross-reference vs. an illustrative ``L<NN>`` placeholder vs. a
not-yet-authored target — is judgment, and that judgment is what the
`SKILL.md` adds on top. Splitting it this way is deliberate: the deterministic
extraction could be a plain tool; the classification needs a skill.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

# ``[text](target)`` — good enough for lesson prose, not a full CommonMark parser
# (that isn't the teaching point). ``text`` stops at the first ``]``; ``target``
# runs to the closing ``)``.
_LINK_RE = re.compile(r"\[(?P<text>[^\]]*)\]\((?P<target>[^)]+)\)")

LinkKind = Literal["file", "anchor", "external"]


class MarkdownLink(BaseModel):
    text: str
    target: str
    kind: LinkKind
    # Only meaningful when ``kind == "file"``: does the target resolve on disk?
    # Stays ``None`` for anchors and external URLs, and for file links when no
    # base directory was given to resolve against.
    resolves: bool | None = None


def classify_target(target: str) -> LinkKind:
    """Classify a link target as ``external``, ``anchor``, or ``file``."""
    if target.startswith(("http://", "https://", "mailto:")):
        return "external"
    if target.startswith("#"):
        return "anchor"
    return "file"


def extract_links(markdown: str, base_dir: Path | None = None) -> list[MarkdownLink]:
    """Extract every Markdown link and resolve file targets against ``base_dir``.

    Example input:
        "see [objectives](objectives.md) and [top](#top) and [x](https://x.io)"
    Example output (as objects):
        [MarkdownLink(text="objectives", target="objectives.md", kind="file", resolves=...),
         MarkdownLink(text="top", target="#top", kind="anchor", resolves=None),
         MarkdownLink(text="x", target="https://x.io", kind="external", resolves=None)]

    File targets are resolved relative to ``base_dir`` (the document's own
    directory). When ``base_dir`` is ``None`` file existence is not checked and
    ``resolves`` stays ``None``. A ``path#anchor`` target is resolved on its path
    part only.
    """
    links: list[MarkdownLink] = []
    for match in _LINK_RE.finditer(markdown):
        target = match.group("target")
        kind = classify_target(target)
        resolves: bool | None = None
        if kind == "file" and base_dir is not None:
            path_part = target.split("#", 1)[0]
            resolves = (base_dir / path_part).exists()
        links.append(
            MarkdownLink(text=match.group("text"), target=target, kind=kind, resolves=resolves)
        )
    return links


def unresolved_file_links(links: list[MarkdownLink]) -> list[MarkdownLink]:
    """The file links whose targets did not resolve on disk — candidates for judgment."""
    return [link for link in links if link.kind == "file" and link.resolves is False]
