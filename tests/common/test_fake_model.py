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


def test_bind_tools_tolerates_extra_kwargs() -> None:
    # create_agent binds tools with tool_choice=...; FakeModel must accept the kwarg.
    model = FakeModel([text_reply("x")])
    assert model.bind_tools([], tool_choice="auto") is model


def test_invoke_tolerates_extra_positional_and_keyword_args() -> None:
    # A framework may call invoke(messages, config, **kwargs); FakeModel must ignore them.
    reply = text_reply("scripted")
    model = FakeModel([reply])
    assert model.invoke([], {"configurable": {}}, tags=["x"]) is reply


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


async def test_ainvoke_returns_scripted_replies_in_order() -> None:
    first = text_reply("a")
    second = text_reply("b")
    model = FakeModel([first, second])
    assert [await model.ainvoke([]), await model.ainvoke([])] == [first, second]


async def test_ainvoke_shares_the_call_counter_with_invoke() -> None:
    # A script drives sync and async runs identically: invoke then ainvoke advances
    # through the script, it does not restart it.
    first = text_reply("a")
    second = text_reply("b")
    model = FakeModel([first, second])
    model.invoke([])
    assert await model.ainvoke([]) is second
