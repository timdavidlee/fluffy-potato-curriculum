from collections.abc import Callable

import pytest

from fluffy_potato_curriculum.common.agent_loop import RunResult, run
from fluffy_potato_curriculum.common.evals import (
    EvalCase,
    EvalReport,
    EvalResult,
    compare,
    evaluate,
    tool_calls,
    tool_trajectory,
)
from fluffy_potato_curriculum.common.fake_model import (
    FakeModel,
    response,
    text_block,
    tool_use_block,
)
from fluffy_potato_curriculum.common.tools import TOOLS


def _chaining_run() -> RunResult:
    """A clean calculator -> lookup -> answer run that terminates naturally."""
    model = FakeModel(
        [
            response([tool_use_block("c1", "calculator", {"expression": "17*23"})]),
            response([tool_use_block("c2", "lookup", {"city": "Tokyo"})]),
            response([text_block("17*23 is 391, and Tokyo has 37000000 people.")]),
        ]
    )
    return run(model, TOOLS, "q", max_steps=8)


def _runaway_run() -> RunResult:
    """A run that repeats one failing call until max_steps halts it."""
    model = FakeModel([response([tool_use_block("c", "lookup", {"city": "Atlantis"})])])
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
