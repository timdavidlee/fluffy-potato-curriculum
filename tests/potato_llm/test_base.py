from fluffy_potato_curriculum.potato_llm import (
    ChatResponse,
    Message,
    PotatoLLMClient,
    Usage,
)


def test_message_constructors_set_role() -> None:
    assert Message.system("s") == Message(role="system", content="s")
    assert Message.user("u") == Message(role="user", content="u")
    assert Message.assistant("a") == Message(role="assistant", content="a")


def test_usage_total_is_sum() -> None:
    assert Usage(input_tokens=3, output_tokens=4).total_tokens == 7


def test_chat_response_holds_normalized_fields() -> None:
    resp = ChatResponse(
        text="hi",
        model="some-model",
        usage=Usage(input_tokens=1, output_tokens=2),
        raw={"untouched": True},
    )
    assert resp.text == "hi"
    assert resp.usage.total_tokens == 3
    assert resp.raw == {"untouched": True}


class _Conforming:
    @property
    def model(self) -> str:
        return "x"

    def chat(
        self,
        messages: list[Message],
        *,
        max_tokens: int = 1024,
        temperature: float = 1.0,
    ) -> ChatResponse:
        return ChatResponse("", "x", Usage(0, 0), None)


class _NotConforming:
    pass


def test_protocol_is_structural() -> None:
    assert isinstance(_Conforming(), PotatoLLMClient)
    assert not isinstance(_NotConforming(), PotatoLLMClient)
