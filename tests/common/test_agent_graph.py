from fluffy_potato_curriculum.common.agent_graph import (
    arun,
    atrace_graph,
    build_agent,
    run,
    trace_graph,
)
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
    """A model that keeps asking for the same failing tool — it never finishes.

    The tool calls carry *distinct* ids (``r0``, ``r1``, …): the ``add_messages``
    reducer keys on message id, so repeating one identical ``AIMessage`` would be
    de-duplicated and the cycle would stop early instead of running away.
    """
    return FakeModel(
        [tool_reply(tool_call(f"r{i}", "lookup", {"city": "Atlantis"})) for i in range(8)]
    )


def test_run_terminates_naturally_when_model_stops_calling_tools() -> None:
    assert run(_chaining_model(), TOOLS, "q", max_steps=8).termination == "natural"


def test_run_iteration_count_matches_llm_span_count() -> None:
    result = run(_chaining_model(), TOOLS, "q", max_steps=8)
    llm_spans = [event for event in result.trace if event.run_type == "llm"]
    assert result.iterations == len(llm_spans)


def test_run_emits_a_chain_span_first() -> None:
    assert run(_chaining_model(), TOOLS, "q", max_steps=8).trace[0].run_type == "chain"


def test_llm_spans_are_named_for_the_agent_node() -> None:
    result = run(_chaining_model(), TOOLS, "q", max_steps=8)
    llm_spans = [event for event in result.trace if event.run_type == "llm"]
    assert {span.name for span in llm_spans} == {"agent"}


def test_run_spans_share_one_trace_id() -> None:
    result = run(_chaining_model(), TOOLS, "q", max_steps=8)
    assert len({event.trace_id for event in result.trace}) == 1


def test_run_tool_span_records_the_arguments() -> None:
    result = run(_chaining_model(), TOOLS, "q", max_steps=8)
    tool_spans = [event for event in result.trace if event.run_type == "tool"]
    assert tool_spans[0].inputs == {"expression": "17*23"}


def test_run_tool_span_names_follow_the_trajectory() -> None:
    result = run(_chaining_model(), TOOLS, "q", max_steps=8)
    tool_names = [event.name for event in result.trace if event.run_type == "tool"]
    assert tool_names == ["calculator", "lookup"]


def test_run_hits_max_steps_on_a_runaway() -> None:
    assert run(_runaway_model(), TOOLS, "q", max_steps=3).termination == "max_steps"


def test_runaway_iteration_count_matches_the_cap() -> None:
    assert run(_runaway_model(), TOOLS, "q", max_steps=3).iterations == 3


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


def test_trace_graph_accepts_a_prebuilt_compiled_graph() -> None:
    graph = build_agent(_chaining_model(), TOOLS)
    assert trace_graph(graph, "q", max_steps=8).termination == "natural"


def test_trace_serializes_to_jsonl_and_back() -> None:
    result = run(_chaining_model(), TOOLS, "q", max_steps=8)
    assert from_jsonl(to_jsonl(result.trace)) == result.trace


async def test_arun_terminates_naturally_when_model_stops_calling_tools() -> None:
    result = await arun(_chaining_model(), TOOLS, "q", max_steps=8)
    assert result.termination == "natural"


async def test_arun_hits_max_steps_on_a_runaway() -> None:
    result = await arun(_runaway_model(), TOOLS, "q", max_steps=3)
    assert result.termination == "max_steps"


async def test_arun_tool_span_names_follow_the_trajectory() -> None:
    result = await arun(_chaining_model(), TOOLS, "q", max_steps=8)
    tool_names = [event.name for event in result.trace if event.run_type == "tool"]
    assert tool_names == ["calculator", "lookup"]


async def test_atrace_graph_drives_a_prebuilt_compiled_graph() -> None:
    graph = build_agent(_chaining_model(), TOOLS)
    result = await atrace_graph(graph, "q", max_steps=8)
    assert result.termination == "natural"


async def test_arun_emits_the_same_span_sequence_as_run() -> None:
    # `astream` drives the same compiled graph as `stream`, so the async producer
    # emits the identical ordered chain/llm/tool spans.
    sync_types = [event.run_type for event in run(_chaining_model(), TOOLS, "q", max_steps=8).trace]
    async_result = await arun(_chaining_model(), TOOLS, "q", max_steps=8)
    assert [event.run_type for event in async_result.trace] == sync_types
