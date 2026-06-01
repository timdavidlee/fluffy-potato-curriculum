from typing import cast

import anthropic
from anthropic import omit
from anthropic.types import Message as AnthropicMessage
from anthropic.types import TextBlock

from fluffy_potato_curriculum.potato_llm import AnthropicClient, Message, PotatoLLMClient
from fluffy_potato_curriculum.potato_llm.anthropic_client import (
    extract_system,
    extract_text,
    to_anthropic_messages,
)


def test_extract_system_omitted_when_absent() -> None:
    assert extract_system([Message.user("hi")]) is omit


def test_extract_system_joins_multiple() -> None:
    msgs = [Message.system("a"), Message.user("hi"), Message.system("b")]
    assert extract_system(msgs) == "a\n\nb"


def test_to_anthropic_messages_drops_system_and_keeps_order() -> None:
    msgs = [
        Message.system("ignored"),
        Message.user("u1"),
        Message.assistant("a1"),
    ]
    assert to_anthropic_messages(msgs) == [
        {"role": "user", "content": "u1"},
        {"role": "assistant", "content": "a1"},
    ]


def test_extract_text_concatenates_text_blocks() -> None:
    msg = cast(
        AnthropicMessage,
        _FakeResponse(
            content=[
                TextBlock(type="text", text="Hello ", citations=None),
                TextBlock(type="text", text="world", citations=None),
            ]
        ),
    )
    assert extract_text(msg) == "Hello world"


class _FakeUsage:
    def __init__(self, input_tokens: int, output_tokens: int) -> None:
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


class _FakeResponse:
    def __init__(
        self,
        content: list[TextBlock],
        model: str = "claude-test",
        usage: _FakeUsage | None = None,
    ) -> None:
        self.content = content
        self.model = model
        self.usage = usage if usage is not None else _FakeUsage(11, 22)


class _FakeMessages:
    def __init__(self, response: _FakeResponse) -> None:
        self._response = response
        self.last_kwargs: dict[str, object] = {}

    def create(self, **kwargs: object) -> _FakeResponse:
        self.last_kwargs = kwargs
        return self._response


class _FakeAnthropic:
    def __init__(self, response: _FakeResponse) -> None:
        self.messages = _FakeMessages(response)


def test_chat_wires_request_and_normalizes_response() -> None:
    fake = _FakeAnthropic(
        _FakeResponse(content=[TextBlock(type="text", text="hi there", citations=None)])
    )
    client = AnthropicClient(model="claude-test", client=cast(anthropic.Anthropic, fake))

    assert isinstance(client, PotatoLLMClient)

    resp = client.chat(
        [Message.system("be brief"), Message.user("hello")],
        max_tokens=64,
    )

    assert resp.text == "hi there"
    assert resp.model == "claude-test"
    assert resp.usage.input_tokens == 11
    assert resp.usage.output_tokens == 22

    sent = fake.messages.last_kwargs
    assert sent["system"] == "be brief"
    assert sent["messages"] == [{"role": "user", "content": "hello"}]
    assert sent["max_tokens"] == 64
