from typing import cast

import openai
from openai.types.chat import ChatCompletion

from fluffy_potato_curriculum.potato_llm import Message, OpenAIClient, PotatoLLMClient
from fluffy_potato_curriculum.potato_llm.openai_client import (
    extract_text,
    extract_usage,
    to_openai_messages,
)


def test_to_openai_messages_keeps_system_in_list() -> None:
    msgs = [Message.system("s"), Message.user("u"), Message.assistant("a")]
    assert to_openai_messages(msgs) == [
        {"role": "system", "content": "s"},
        {"role": "user", "content": "u"},
        {"role": "assistant", "content": "a"},
    ]


class _FakeMessage:
    def __init__(self, content: str | None) -> None:
        self.content = content


class _FakeChoice:
    def __init__(self, content: str | None) -> None:
        self.message = _FakeMessage(content)


class _FakeUsage:
    def __init__(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class _FakeCompletion:
    def __init__(
        self,
        content: str | None,
        model: str = "gpt-test",
        usage: _FakeUsage | None = None,
    ) -> None:
        self.choices = [_FakeChoice(content)] if content is not None else []
        self.model = model
        self.usage = usage


def test_extract_text_handles_none_and_empty() -> None:
    with_text = cast(ChatCompletion, _FakeCompletion(content="hi"))
    no_choices = cast(ChatCompletion, _FakeCompletion(content=None))
    assert extract_text(with_text) == "hi"
    assert extract_text(no_choices) == ""


def test_extract_usage_defaults_to_zero_when_missing() -> None:
    no_usage = cast(ChatCompletion, _FakeCompletion(content="hi"))
    usage = extract_usage(no_usage)
    assert usage.input_tokens == 0
    assert usage.output_tokens == 0


class _FakeCompletions:
    def __init__(self, completion: _FakeCompletion) -> None:
        self._completion = completion
        self.last_kwargs: dict[str, object] = {}

    def create(self, **kwargs: object) -> _FakeCompletion:
        self.last_kwargs = kwargs
        return self._completion


class _FakeChat:
    def __init__(self, completion: _FakeCompletion) -> None:
        self.completions = _FakeCompletions(completion)


class _FakeOpenAI:
    def __init__(self, completion: _FakeCompletion) -> None:
        self.chat = _FakeChat(completion)


def test_chat_wires_request_and_normalizes_response() -> None:
    fake = _FakeOpenAI(
        _FakeCompletion(content="hi there", usage=_FakeUsage(prompt_tokens=5, completion_tokens=6))
    )
    client = OpenAIClient(model="gpt-test", client=cast(openai.OpenAI, fake))

    assert isinstance(client, PotatoLLMClient)

    resp = client.chat([Message.system("be brief"), Message.user("hello")])

    assert resp.text == "hi there"
    assert resp.model == "gpt-test"
    assert resp.usage.input_tokens == 5
    assert resp.usage.output_tokens == 6

    sent = fake.chat.completions.last_kwargs
    assert sent["messages"] == [
        {"role": "system", "content": "be brief"},
        {"role": "user", "content": "hello"},
    ]
