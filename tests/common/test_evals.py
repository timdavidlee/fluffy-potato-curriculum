from collections.abc import Callable
from typing import Any

import pytest

from fluffy_potato_curriculum.common.agent_loop import RunResult, run
from fluffy_potato_curriculum.common.evals import (
    EvalCase,
    EvalReport,
    EvalResult,
    compare,
    emit_score,
    evaluate,
    tool_calls,
    tool_trajectory,
    upload_dataset,
)
from fluffy_potato_curriculum.common.fake_model import (
    FakeModel,
    text_reply,
    tool_call,
    tool_reply,
)
from fluffy_potato_curriculum.common.tools import TOOLS


def _chaining_run() -> RunResult:
    """A clean calculator -> lookup -> answer run that terminates naturally."""
    model = FakeModel(
        [
            tool_reply(tool_call("c1", "calculator", {"expression": "17*23"})),
            tool_reply(tool_call("c2", "lookup", {"city": "Tokyo"})),
            text_reply("17*23 is 391, and Tokyo has 37000000 people."),
        ]
    )
    return run(model, TOOLS, "q", max_steps=8)


def _runaway_run() -> RunResult:
    """A run that repeats one failing call until max_steps halts it."""
    model = FakeModel([tool_reply(tool_call("c", "lookup", {"city": "Atlantis"}))])
    return run(model, TOOLS, "q", max_steps=3)


def answer_contains(*, run: RunResult, example: EvalCase) -> EvalResult:
    """Outcome scorer: did final_text contain the reference answer?"""
    expected = str(example.reference_outputs["answer"])
    return EvalResult(key="answer_correct", score=expected in run.final_text)


def expected_tools(*, run: RunResult, example: EvalCase) -> EvalResult:
    """Trajectory scorer: did the tool-call path match the reference path?"""
    expected = list(example.reference_outputs["expected_tools"])
    return EvalResult(key="expected_tools", score=tool_trajectory(run) == expected)


def no_runaway(*, run: RunResult, example: EvalCase) -> EvalResult:
    """Trajectory scorer: did the run avoid hitting the step cap?"""
    return EvalResult(key="no_runaway", score=run.termination != "max_steps")


def test_tool_trajectory_reads_ordered_names() -> None:
    assert tool_trajectory(_chaining_run()) == ["calculator", "lookup"]


def test_tool_calls_reads_names_with_args() -> None:
    assert tool_calls(_chaining_run())[0] == ("calculator", {"expression": "17*23"})


@pytest.mark.parametrize(
    ("score", "expected"),
    [(True, True), (False, False), (1.0, True), (0.0, False), (0.5, True)],
)
def test_eval_result_passed_is_truthy_score(score: float | bool, expected: bool) -> None:
    assert EvalResult(key="k", score=score).passed is expected


def test_evaluate_scores_a_passing_outcome_case() -> None:
    case = EvalCase(id="tokyo", inputs={"task": "q"}, reference_outputs={"answer": "37000000"})
    report = evaluate(lambda _case: _chaining_run(), [case], [answer_contains])
    assert report.pass_rate("tokyo", "answer_correct") == 1.0


def test_evaluate_scores_a_failing_outcome_case() -> None:
    case = EvalCase(id="tokyo", inputs={"task": "q"}, reference_outputs={"answer": "999"})
    report = evaluate(lambda _case: _chaining_run(), [case], [answer_contains])
    assert report.pass_rate("tokyo", "answer_correct") == 0.0


def test_no_runaway_scorer_fails_on_a_runaway() -> None:
    case = EvalCase(id="atlantis")
    report = evaluate(lambda _case: _runaway_run(), [case], [no_runaway])
    assert report.pass_rate("atlantis", "no_runaway") == 0.0


def test_pass_rate_is_a_fraction_when_runs_vary() -> None:
    """A run_case that passes on 2 of 3 samples yields a 2/3 pass rate."""
    case = EvalCase(id="flaky", reference_outputs={"expected_tools": ["calculator", "lookup"]})
    outcomes = [_chaining_run(), _chaining_run(), _runaway_run()]

    def varying_run_case(_case: EvalCase) -> RunResult:
        return outcomes.pop(0)

    report = evaluate(varying_run_case, [case], [expected_tools], samples=3)
    assert report.pass_rate("flaky", "expected_tools") == 2 / 3


def test_all_pass_rate_requires_every_scorer() -> None:
    """The runaway fails no_runaway (max_steps) and the trajectory check, so ALL is 0/1."""
    case = EvalCase(id="atlantis", reference_outputs={"expected_tools": ["lookup"]})
    report = evaluate(lambda _case: _runaway_run(), [case], [no_runaway, expected_tools])
    assert report.summary_for("atlantis").all_pass_rate == 0.0


def test_table_includes_case_and_scorer_columns() -> None:
    case = EvalCase(id="tokyo", reference_outputs={"answer": "37000000"})
    report = evaluate(lambda _case: _chaining_run(), [case], [answer_contains])
    rendered = report.table()
    assert "tokyo" in rendered and "answer_correct" in rendered


def _report(run_case: Callable[[EvalCase], RunResult]) -> EvalReport:
    case = EvalCase(id="atlantis")
    return evaluate(run_case, [case], [no_runaway])


def test_compare_flags_a_regression() -> None:
    before = _report(lambda _case: _chaining_run())  # no_runaway passes
    after = _report(lambda _case: _runaway_run())  # no_runaway fails
    assert compare(before, after).regressions == [("atlantis", "no_runaway")]


def test_compare_flags_a_fix() -> None:
    before = _report(lambda _case: _runaway_run())  # fails
    after = _report(lambda _case: _chaining_run())  # passes
    assert compare(before, after).fixes == [("atlantis", "no_runaway")]


# --- the Langfuse bridge ----------------------------------------------------


class _FakeLangfuse:
    """An offline recorder that structurally satisfies ``LangfuseClient``.

    Records what the bridge would send to Langfuse so the tests can assert the
    mapping without a live instance (same offline stance as the rest of common/).
    """

    def __init__(self) -> None:
        self.datasets: list[dict[str, Any]] = []
        self.items: list[dict[str, Any]] = []
        self.scores: list[dict[str, Any]] = []

    def create_dataset(self, *, name: str, description: str | None = None) -> None:
        self.datasets.append({"name": name, "description": description})

    def create_dataset_item(
        self, *, dataset_name: str, id: str, input: Any, expected_output: Any
    ) -> None:
        self.items.append(
            {
                "dataset_name": dataset_name,
                "id": id,
                "input": input,
                "expected_output": expected_output,
            }
        )

    def create_score(
        self,
        *,
        name: str,
        value: float | str,
        trace_id: str,
        comment: str | None = None,
        data_type: str | None = None,
    ) -> None:
        self.scores.append(
            {
                "name": name,
                "value": value,
                "trace_id": trace_id,
                "comment": comment,
                "data_type": data_type,
            }
        )


def test_upload_dataset_creates_the_named_dataset() -> None:
    client = _FakeLangfuse()
    upload_dataset(client, [EvalCase(id="a")], name="l13", description="first pass")
    assert client.datasets == [{"name": "l13", "description": "first pass"}]


def test_upload_dataset_maps_each_case_to_a_dataset_item() -> None:
    client = _FakeLangfuse()
    cases = [
        EvalCase(id="a", inputs={"task": "q1"}, reference_outputs={"answer": "1"}),
        EvalCase(id="b", inputs={"task": "q2"}, reference_outputs={"expected_tools": ["lookup"]}),
    ]
    upload_dataset(client, cases, name="l13")
    assert client.items == [
        {
            "dataset_name": "l13",
            "id": "a",
            "input": {"task": "q1"},
            "expected_output": {"answer": "1"},
        },
        {
            "dataset_name": "l13",
            "id": "b",
            "input": {"task": "q2"},
            "expected_output": {"expected_tools": ["lookup"]},
        },
    ]


def test_emit_score_maps_result_fields_onto_a_langfuse_score() -> None:
    client = _FakeLangfuse()
    emit_score(client, EvalResult(key="no_runaway", score=True, comment="ok"), trace_id="trace-9")
    assert client.scores == [
        {
            "name": "no_runaway",
            "value": True,
            "trace_id": "trace-9",
            "comment": "ok",
            "data_type": "BOOLEAN",
        }
    ]


@pytest.mark.parametrize(
    ("score", "data_type"),
    [(True, "BOOLEAN"), (False, "BOOLEAN"), (1.0, "NUMERIC"), (0.5, "NUMERIC")],
)
def test_emit_score_tags_bool_as_boolean_and_number_as_numeric(
    score: float | bool, data_type: str
) -> None:
    client = _FakeLangfuse()
    emit_score(client, EvalResult(key="k", score=score), trace_id="t1")
    assert client.scores[0]["data_type"] == data_type
