"""The provider-agnostic seam for talking to an LLM.

`PotatoLLMClient` is a deliberately tiny interface. Everything in the curriculum
that "calls a model" goes through it, so that swapping Anthropic for OpenAI is a
one-line change at the edge of a program instead of a rewrite of the middle.

Nothing here is an official SDK type. The "Potato" prefix is a reminder that we
hand-rolled this for teaching: in production you would reach for a library like
LiteLLM (a thin translation layer) or a gateway like OpenRouter. We build it once
so you can see exactly what those tools do for you.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Protocol, runtime_checkable

Role = Literal["system", "user", "assistant"]
"""Who authored a message. Both providers understand these three roles, even
though they wire them up differently (see the two client implementations)."""


@dataclass(frozen=True, slots=True)
class Message:
    """One turn in a conversation.

    We keep content to plain text on purpose: images, tool calls, and the like
    are introduced in later lessons. A frozen dataclass means a message can't be
    mutated after it's built, which keeps conversation history honest.
    """

    role: Role
    content: str

    @classmethod
    def system(cls, content: str) -> Message:
        return cls("system", content)

    @classmethod
    def user(cls, content: str) -> Message:
        return cls("user", content)

    @classmethod
    def assistant(cls, content: str) -> Message:
        return cls("assistant", content)


@dataclass(frozen=True, slots=True)
class Usage:
    """Token accounting for a single call.

    Both providers report input/output tokens; we normalize the names so a
    program can compare cost across providers without special-casing.
    """

    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass(frozen=True, slots=True)
class ChatResponse:
    """What every `PotatoLLMClient.chat` call returns.

    `text` is the assistant's reply. `model` and `usage` let labs reason about
    which model actually answered and what it cost. `raw` holds the untouched
    provider object for the curious — reach into it to see what we threw away.
    """

    text: str
    model: str
    usage: Usage
    raw: object = field(repr=False)


@runtime_checkable
class PotatoLLMClient(Protocol):
    """The one method every provider client implements.

    It's a `Protocol`, so a class is a `PotatoLLMClient` simply by having a
    matching `chat` method — no base class to inherit, no registration. That is
    the whole point of the seam: code depends on this shape, not on Anthropic or
    OpenAI specifically.
    """

    @property
    def model(self) -> str:
        """The model id this client will call."""
        ...

    def chat(
        self,
        messages: list[Message],
        *,
        max_tokens: int = 1024,
        temperature: float = 1.0,
    ) -> ChatResponse:
        """Send a conversation, get one assistant reply back."""
        ...
