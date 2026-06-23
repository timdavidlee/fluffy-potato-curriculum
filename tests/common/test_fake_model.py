from fluffy_potato_curriculum.common.fake_model import (
    FakeModel,
    response,
    text_block,
    tool_use_block,
)


def test_response_stop_reason_is_tool_use_when_a_tool_block_is_present() -> None:
    reply = response([tool_use_block("c1", "calculator", {"expression": "17*23"})])
    assert reply.stop_reason == "tool_use"


def test_response_stop_reason_is_end_turn_for_text_only() -> None:
    assert response([text_block("done")]).stop_reason == "end_turn"


def test_fake_model_returns_scripted_responses_in_order() -> None:
    first = response([text_block("a")])
    second = response([text_block("b")])
    model = FakeModel([first, second])
    assert [model.create(), model.create()] == [first, second]


def test_fake_model_repeats_last_response_when_script_is_exhausted() -> None:
    last = response([text_block("only")])
    model = FakeModel([last])
    model.create()
    assert model.create() is last
