"""A scripted, offline stand-in for the Anthropic client.

The agent loop needs a model object with a ``.create(...)`` method that returns a
response carrying ``content`` blocks (``tool_use`` / ``text``). The real Anthropic
SDK provides that; ``FakeModel`` provides a *deterministic* version so the L08
reading demos and the labs run with **no API key and no network**, and produce the
exact same trace every time.

This matters pedagogically: objectives 1, 2, and 4 of L08 are *reading* skills,
clearest on a fixed, known trace. A scripted model gives that — the model's moves
are decided in advance, so a "runaway", a "wrong-arguments" run, or a clean run is
reproducible on demand. The real model only appears in the live instrument/export
demos, where *producing* a fresh trace is the point.

The block/response shapes mimic the SDK closely enough that the same loop code
reads both: it touches ``block.type``, ``block.text``, ``block.id``,
``block.name``, ``block.input``, ``response.content``, and ``response.usage``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FakeTextBlock:
    """A scripted assistant text block (mimics the SDK's text content block)."""

    text: str
    type: str = "text"


@dataclass(frozen=True)
class FakeToolUseBlock:
    """A scripted assistant tool-use block (mimics the SDK's tool_use block)."""

    id: str
    name: str
    input: dict[str, Any]
    type: str = "tool_use"


@dataclass(frozen=True)
class FakeUsage:
    """Scripted token counts, so ``llm`` spans carry a believable ``usage``."""

    input_tokens: int
    output_tokens: int


@dataclass(frozen=True)
class FakeResponse:
    """A scripted model response: the content blocks plus token usage."""

    content: list[FakeTextBlock | FakeToolUseBlock]
    usage: FakeUsage
    stop_reason: str


def text_block(text: str) -> FakeTextBlock:
    """Build a scripted text block."""
    return FakeTextBlock(text=text)


def tool_use_block(call_id: str, name: str, args: dict[str, Any]) -> FakeToolUseBlock:
    """Build a scripted tool-use block (``call_id`` becomes the ``tool_use_id``)."""
    return FakeToolUseBlock(id=call_id, name=name, input=args)


def response(
    blocks: list[FakeTextBlock | FakeToolUseBlock],
    *,
    input_tokens: int = 100,
    output_tokens: int = 20,
) -> FakeResponse:
    """Build a scripted response. ``stop_reason`` is ``tool_use`` if any block is
    a tool call, else ``end_turn`` — matching how the real SDK reports it."""
    has_tool_use = any(isinstance(block, FakeToolUseBlock) for block in blocks)
    stop = "tool_use" if has_tool_use else "end_turn"
    return FakeResponse(
        content=blocks,
        usage=FakeUsage(input_tokens=input_tokens, output_tokens=output_tokens),
        stop_reason=stop,
    )


@dataclass
class FakeModel:
    """A model whose replies are scripted in advance.

    ``create`` ignores its keyword arguments and returns the next scripted
    response. When the script runs out it **repeats the last line** — which is how
    a runaway loop (the ``max_steps`` case) is simulated: keep asking for the same
    tool forever.

    Example::

        model = FakeModel([
            response([tool_use_block("c1", "calculator", {"expression": "17*23"})]),
            response([text_block("17 * 23 is 391.")]),
        ])
    """

    scripted: list[FakeResponse]
    calls: int = field(default=0)

    def create(self, **kwargs: Any) -> FakeResponse:
        index = min(self.calls, len(self.scripted) - 1)
        self.calls += 1
        return self.scripted[index]
