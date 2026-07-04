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


def to_chat_response(response: AnthropicMessage) -> ChatResponse:
    """Normalize a raw Anthropic response into our provider-agnostic `ChatResponse`.

    Shared by the sync and async call paths so both return the identical shape —
    the mapping (text blocks joined, usage renamed) lives in one place."""
    return ChatResponse(
        text=extract_text(response),
        model=response.model,
        usage=Usage(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        ),
        raw=response,
    )


class AnthropicClient:
    """Talk to Claude through the `PotatoLLMClient` seam.

    Holds **both** a sync and an async Anthropic SDK client, so it can serve `chat`
    (blocking) and `achat` (awaitable) off the same configuration. Pass `client=`
    and/or `async_client=` to inject pre-built (or fake) SDK clients — a test that
    only exercises one path need only inject that one. Whenever a real client has to
    be constructed, the key is resolved from `api_key`, falling back to the
    configured `ANTHROPIC_API_KEY` (see `common.config`); a missing key raises a
    clear error up front rather than failing later mid-call.
    """

    def __init__(
        self,
        *,
        model: str = DEFAULT_MODEL,
        api_key: str | None = None,
        client: anthropic.Anthropic | None = None,
        async_client: anthropic.AsyncAnthropic | None = None,
    ) -> None:
        self._model = model
        self._api_key = api_key
        self._client = client
        self._async_client = async_client
        # Fail fast on the *real* path: if the caller injected neither client they
        # mean to talk to a live model, so resolve the key now (a clear error up
        # front, not mid-call) and build both SDK clients. If a (fake) client was
        # injected we stay lazy — a test that drives only `chat` or only `achat`
        # shouldn't need a key or the other real client (see `_sync`/`_async`).
        if client is None and async_client is None:
            resolved_key = api_key or require_anthropic_key()
            self._api_key = resolved_key
            self._client = anthropic.Anthropic(api_key=resolved_key)
            self._async_client = anthropic.AsyncAnthropic(api_key=resolved_key)

    def _sync(self) -> anthropic.Anthropic:
        """The sync SDK client, built (and key-resolved) on first use if injected as None."""
        if self._client is None:
            self._client = anthropic.Anthropic(api_key=self._api_key or require_anthropic_key())
        return self._client

    def _async(self) -> anthropic.AsyncAnthropic:
        """The async SDK client, built (and key-resolved) on first use if injected as None."""
        if self._async_client is None:
            self._async_client = anthropic.AsyncAnthropic(
                api_key=self._api_key or require_anthropic_key()
            )
        return self._async_client

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
        response = self._sync().messages.create(
            model=self._model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=extract_system(messages),
            messages=to_anthropic_messages(messages),
        )
        return to_chat_response(response)

    async def achat(
        self,
        messages: list[Message],
        *,
        max_tokens: int = 1024,
        temperature: float = 1.0,
    ) -> ChatResponse:
        """`await`-able twin of `chat`: the async SDK client, same request/response."""
        response = await self._async().messages.create(
            model=self._model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=extract_system(messages),
            messages=to_anthropic_messages(messages),
        )
        return to_chat_response(response)
