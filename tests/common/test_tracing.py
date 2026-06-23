from pathlib import Path

from fluffy_potato_curriculum.common.tracing import (
    SpanUsage,
    TraceEvent,
    from_jsonl,
    read_jsonl,
    to_jsonl,
    write_jsonl,
)


def test_span_usage_total_is_sum_of_input_and_output() -> None:
    assert SpanUsage(input_tokens=100, output_tokens=20).total_tokens == 120


def test_duration_is_end_minus_start() -> None:
    event = TraceEvent(
        run_id="r", trace_id="t", run_type="llm", name="x", start_time=1.0, end_time=1.5
    )
    assert event.duration_s == 0.5


def test_duration_is_none_when_times_missing() -> None:
    assert TraceEvent(run_id="r", trace_id="t", run_type="tool", name="x").duration_s is None


def test_jsonl_round_trips_events() -> None:
    events = [
        TraceEvent(run_id="r1", trace_id="t", run_type="chain", name="agent_loop.run"),
        TraceEvent(
            run_id="r2",
            trace_id="t",
            run_type="tool",
            name="calculator",
            inputs={"expression": "17*23"},
            outputs={"content": "391"},
        ),
    ]
    assert from_jsonl(to_jsonl(events)) == events


def test_usage_survives_a_jsonl_round_trip() -> None:
    events = [
        TraceEvent(
            run_id="r",
            trace_id="t",
            run_type="llm",
            name="model.create",
            usage=SpanUsage(input_tokens=100, output_tokens=20),
        )
    ]
    assert from_jsonl(to_jsonl(events)) == events


def test_write_then_read_jsonl(tmp_path: Path) -> None:
    events = [TraceEvent(run_id="r", trace_id="t", run_type="chain", name="agent_loop.run")]
    path = tmp_path / "trace.jsonl"
    write_jsonl(events, path)
    assert read_jsonl(path) == events
