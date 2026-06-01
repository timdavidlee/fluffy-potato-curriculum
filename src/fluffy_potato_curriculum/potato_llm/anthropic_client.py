"""`PotatoLLMClient` backed by the official Anthropic SDK.

The interesting wrinkle this client hides: Anthropic does **not** accept a
"system" message inside the message list. The system prompt is its own top-level
parameter, and the message list may only contain `user`/`assistant` turns. The
pure helper functions below do that translation, so the logic is testable
without a network call or an API key.
"""

from __future__ import annotations

import anthropic
from anthropic import Omit, omit
from anthropic.types import Message as AnthropicMessage
from anthropic.types import MessageParam, TextBlock

from fluffy_potato_curriculum.common.config import require_anthropic_key

from .base import ChatResponse, Message, Usage

DEFAULT_MODEL = "claude-sonnet-4-6"
"""The course anchor model. Override per call site as models evolve."""


def extract_system(messages: list[Message]) -> str | Omit:
    """Pull the system prompt(s) out of the message list.

    Anthropic wants the system prompt as a separate argument. If a conversation
    has several system messages we join them; if it has none we return the SDK's
    `omit` sentinel so the parameter is simply left off the request.
    """
    system_parts = [m.content for m in messages if m.role == "system"]
    if not system_parts:
        return omit
    return "\n\n".join(system_parts)


def to_anthropic_messages(messages: list[Message]) -> list[MessageParam]:
    """Map our messages to Anthropic's `user`/`assistant` turns, dropping system."""
    params: list[MessageParam] = []
    for m in messages:
        if m.role == "system":
            continue
        params.append({"role": m.role, "content": m.content})
    return params


def extract_text(message: AnthropicMessage) -> str:
    """Concatenate the text blocks of a response, ignoring non-text blocks."""
    return "".join(block.text for block in message.content if isinstance(block, TextBlock))


class AnthropicClient:
    """Talk to Claude through the `PotatoLLMClient` seam.

    Pass `client=` to inject a pre-built (or fake) SDK client; otherwise one is
    constructed from `api_key`, falling back to the configured `ANTHROPIC_API_KEY`
    (see `common.config`). Constructing a real client with no key available raises
    a clear error rather than failing later mid-call.
    """

    def __init__(
        self,
        *,
        model: str = DEFAULT_MODEL,
        api_key: str | None = None,
        client: anthropic.Anthropic | None = None,
    ) -> None:
        self._model = model
        if client is not None:
            self._client = client
        else:
            self._client = anthropic.Anthropic(api_key=api_key or require_anthropic_key())

    @property
    def model(self) -> str:
        return self._model

    def chat(
        self,
        messages: list[Message],
        *,
        max_tokens: int = 1024,
        temperature: float = 1.0,
    ) -> ChatResponse:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=extract_system(messages),
            messages=to_anthropic_messages(messages),
        )
        return ChatResponse(
            text=extract_text(response),
            model=response.model,
            usage=Usage(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
            ),
            raw=response,
        )
