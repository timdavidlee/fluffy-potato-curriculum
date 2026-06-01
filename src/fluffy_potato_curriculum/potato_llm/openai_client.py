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


class OpenAIClient:
    """Talk to an OpenAI model through the `PotatoLLMClient` seam.

    Pass `client=` to inject a pre-built (or fake) SDK client; otherwise one is
    constructed from `api_key`, falling back to the configured `OPENAI_API_KEY`
    (see `common.config`). Constructing a real client with no key available raises
    a clear error rather than failing later mid-call.
    """

    def __init__(
        self,
        *,
        model: str = DEFAULT_MODEL,
        api_key: str | None = None,
        client: openai.OpenAI | None = None,
    ) -> None:
        self._model = model
        if client is not None:
            self._client = client
        else:
            self._client = openai.OpenAI(api_key=api_key or require_openai_key())

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
        completion = self._client.chat.completions.create(
            model=self._model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=to_openai_messages(messages),
        )
        return ChatResponse(
            text=extract_text(completion),
            model=completion.model,
            usage=extract_usage(completion),
            raw=completion,
        )
