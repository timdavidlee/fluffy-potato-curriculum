"""`PotatoLLMClient` backed by the official OpenAI SDK.

The mirror image of the Anthropic client: OpenAI keeps the system prompt **inside**
the message list as a `system`-role turn, and reports token counts as
`prompt_tokens`/`completion_tokens`. The pure helpers below normalize both back to
the shape the rest of the curriculum expects.
"""

from __future__ import annotations

import openai
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from fluffy_potato_curriculum.common.config import require_openai_key

from .base import ChatResponse, Message, Usage

DEFAULT_MODEL = "gpt-4o-mini"
"""A safe, inexpensive default. Override per call site to use a larger model."""


def to_openai_messages(messages: list[Message]) -> list[ChatCompletionMessageParam]:
    """Map our messages to OpenAI's list, keeping the system turn in place."""
    params: list[ChatCompletionMessageParam] = []
    for m in messages:
        if m.role == "system":
            params.append(ChatCompletionSystemMessageParam(role="system", content=m.content))
        elif m.role == "user":
            params.append(ChatCompletionUserMessageParam(role="user", content=m.content))
        else:
            params.append(ChatCompletionAssistantMessageParam(role="assistant", content=m.content))
    return params


def extract_text(completion: ChatCompletion) -> str:
    """Read the assistant reply, treating a missing/empty choice as empty text."""
    if not completion.choices:
        return ""
    return completion.choices[0].message.content or ""


def extract_usage(completion: ChatCompletion) -> Usage:
    """Normalize OpenAI's prompt/completion counts to our `Usage` shape."""
    usage = completion.usage
    if usage is None:
        return Usage(input_tokens=0, output_tokens=0)
    return Usage(input_tokens=usage.prompt_tokens, output_tokens=usage.completion_tokens)


def to_chat_response(completion: ChatCompletion) -> ChatResponse:
    """Normalize a raw OpenAI completion into our provider-agnostic `ChatResponse`.

    Shared by the sync and async call paths so both return the identical shape."""
    return ChatResponse(
        text=extract_text(completion),
        model=completion.model,
        usage=extract_usage(completion),
        raw=completion,
    )


class OpenAIClient:
    """Talk to an OpenAI model through the `PotatoLLMClient` seam.

    Holds **both** a sync and an async OpenAI SDK client, so it can serve `chat`
    (blocking) and `achat` (awaitable) off the same configuration. Pass `client=`
    and/or `async_client=` to inject pre-built (or fake) SDK clients — a test that
    only exercises one path need only inject that one. Whenever a real client has to
    be constructed, the key is resolved from `api_key`, falling back to the
    configured `OPENAI_API_KEY` (see `common.config`); a missing key raises a clear
    error up front rather than failing later mid-call.
    """

    def __init__(
        self,
        *,
        model: str = DEFAULT_MODEL,
        api_key: str | None = None,
        client: openai.OpenAI | None = None,
        async_client: openai.AsyncOpenAI | None = None,
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
            resolved_key = api_key or require_openai_key()
            self._api_key = resolved_key
            self._client = openai.OpenAI(api_key=resolved_key)
            self._async_client = openai.AsyncOpenAI(api_key=resolved_key)

    def _sync(self) -> openai.OpenAI:
        """The sync SDK client, built (and key-resolved) on first use if injected as None."""
        if self._client is None:
            self._client = openai.OpenAI(api_key=self._api_key or require_openai_key())
        return self._client

    def _async(self) -> openai.AsyncOpenAI:
        """The async SDK client, built (and key-resolved) on first use if injected as None."""
        if self._async_client is None:
            self._async_client = openai.AsyncOpenAI(api_key=self._api_key or require_openai_key())
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
        completion = self._sync().chat.completions.create(
            model=self._model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=to_openai_messages(messages),
        )
        return to_chat_response(completion)

    async def achat(
        self,
        messages: list[Message],
        *,
        max_tokens: int = 1024,
        temperature: float = 1.0,
    ) -> ChatResponse:
        """`await`-able twin of `chat`: the async SDK client, same request/response."""
        completion = await self._async().chat.completions.create(
            model=self._model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=to_openai_messages(messages),
        )
        return to_chat_response(completion)
