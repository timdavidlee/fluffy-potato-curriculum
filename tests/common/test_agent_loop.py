from fluffy_potato_curriculum.common.agent_loop import dispatch, run
from fluffy_potato_curriculum.common.fake_model import (
    FakeModel,
    text_reply,
    tool_call,
    tool_reply,
)
from fluffy_potato_curriculum.common.tools import TOOLS
from fluffy_potato_curriculum.common.tracing import from_jsonl, to_jsonl


def _chaining_model() -> FakeModel:
    """A fresh model scripted to call calculator, then lookup, then answer."""
    return FakeModel(
        [
            tool_reply(tool_call("c1", "calculator", {"expression": "17*23"})),
            tool_reply(tool_call("c2", "lookup", {"city": "Tokyo"})),
            text_reply("17*23 is 391, and Tokyo has 37,000,000 people."),
        ]
    )


def _runaway_model() -> FakeModel:
    """A model that always asks for the same failing tool — it never finishes."""
    return FakeModel([tool_reply(tool_call("c", "lookup", {"city": "Atlantis"}))])


def test_dispatch_success_returns_a_tool_message() -> None:
    result = dispatch(TOOLS, tool_call("c1", "calculator", {"expression": "17*23"}))
    assert (result.content, result.tool_call_id, result.status) == ("391", "c1", "success")


def test_dispatch_unknown_tool_is_marked_error() -> None:
    assert dispatch(TOOLS, tool_call("c1", "nope", {})).status == "error"


def test_dispatch_tool_exception_becomes_error() -> None:
    assert dispatch(TOOLS, tool_call("c1", "lookup", {"city": "Atlantis"})).status == "error"


def test_run_terminates_naturally_when_model_stops_calling_tools() -> None:
    assert run(_chaining_model(), TOOLS, "q", max_steps=8).termination == "natural"


def test_run_iteration_count_matches_llm_span_count() -> None:
    result = run(_chaining_model(), TOOLS, "q", max_steps=8)
    llm_spans = [event for event in result.trace if event.run_type == "llm"]
    assert result.iterations == len(llm_spans)


def test_run_emits_a_chain_span_first() -> None:
    assert run(_chaining_model(), TOOLS, "q", max_steps=8).trace[0].run_type == "chain"


def test_run_spans_share_one_trace_id() -> None:
    result = run(_chaining_model(), TOOLS, "q", max_steps=8)
    assert len({event.trace_id for event in result.trace}) == 1


def test_run_tool_span_records_the_arguments() -> None:
    result = run(_chaining_model(), TOOLS, "q", max_steps=8)
    tool_spans = [event for event in result.trace if event.run_type == "tool"]
    assert tool_spans[0].inputs == {"expression": "17*23"}


def test_run_hits_max_steps_on_a_runaway() -> None:
    assert run(_runaway_model(), TOOLS, "q", max_steps=3).termination == "max_steps"


def test_runaway_records_the_repeated_tool_call() -> None:
    result = run(_runaway_model(), TOOLS, "q", max_steps=3)
    tool_names = [event.name for event in result.trace if event.run_type == "tool"]
    assert tool_names == ["lookup", "lookup", "lookup"]


def test_tool_error_sets_the_error_field_on_its_span() -> None:
    model = FakeModel(
        [
            tool_reply(tool_call("c1", "flaky_fetch", {"url": "https://crash"})),
            text_reply("could not fetch"),
        ]
    )
    result = run(model, TOOLS, "q", max_steps=8)
    tool_span = next(event for event in result.trace if event.run_type == "tool")
    assert tool_span.error is not None


def test_final_text_is_the_last_llm_reply() -> None:
    result = run(_chaining_model(), TOOLS, "q", max_steps=8)
    assert result.final_text == "17*23 is 391, and Tokyo has 37,000,000 people."


def test_trace_serializes_to_jsonl_and_back() -> None:
    result = run(_chaining_model(), TOOLS, "q", max_steps=8)
    assert from_jsonl(to_jsonl(result.trace)) == result.trace
