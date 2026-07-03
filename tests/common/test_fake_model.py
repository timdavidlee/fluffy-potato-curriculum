from fluffy_potato_curriculum.common.fake_model import (
    FakeModel,
    text_reply,
    tool_call,
    tool_reply,
)


def test_tool_reply_carries_tool_calls() -> None:
    reply = tool_reply(tool_call("c1", "calculator", {"expression": "17*23"}))
    assert reply.tool_calls[0]["name"] == "calculator"


def test_text_reply_has_no_tool_calls() -> None:
    assert text_reply("done").tool_calls == []


def test_reply_reports_usage_metadata() -> None:
    assert text_reply("hi", input_tokens=100, output_tokens=20).usage_metadata == {
        "input_tokens": 100,
        "output_tokens": 20,
        "total_tokens": 120,
    }


def test_bind_tools_returns_the_model_itself() -> None:
    model = FakeModel([text_reply("x")])
    assert model.bind_tools([]) is model


def test_fake_model_returns_scripted_replies_in_order() -> None:
    first = text_reply("a")
    second = text_reply("b")
    model = FakeModel([first, second])
    assert [model.invoke([]), model.invoke([])] == [first, second]


def test_fake_model_repeats_last_reply_when_script_is_exhausted() -> None:
    last = text_reply("only")
    model = FakeModel([last])
    model.invoke([])
    assert model.invoke([]) is last
