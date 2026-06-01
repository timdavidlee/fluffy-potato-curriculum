"""PotatoLLMClient — a tiny, hand-rolled seam over multiple LLM providers.

Use it like this::

    from fluffy_potato_curriculum.potato_llm import (
        AnthropicClient,
        Message,
        OpenAIClient,
        PotatoLLMClient,
    )

    def summarize(client: PotatoLLMClient, text: str) -> str:
        reply = client.chat([
            Message.system("You summarize in one sentence."),
            Message.user(text),
        ])
        return reply.text

    # The function above never names a provider. Pick one at the edge:
    summarize(AnthropicClient(), "...")   # talks to Claude
    summarize(OpenAIClient(), "...")      # talks to an OpenAI model

The "Potato" prefix is intentional: this is teaching code, not an official
library. In production you'd reach for LiteLLM or a gateway like OpenRouter.
"""

from .anthropic_client import AnthropicClient
from .base import ChatResponse, Message, PotatoLLMClient, Role, Usage
from .openai_client import OpenAIClient

__all__ = [
    "AnthropicClient",
    "ChatResponse",
    "Message",
    "OpenAIClient",
    "PotatoLLMClient",
    "Role",
    "Usage",
]
