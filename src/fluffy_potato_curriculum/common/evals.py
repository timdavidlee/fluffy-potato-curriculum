"""A tiny, hand-rolled evaluation harness for the agent loop (the L09 artifact).

L08 taught you to *read* a run — its trace. L09 teaches you to *judge* it: stop
asking "did this one run look right?" and start asking "do my agent's runs pass a
fixed set of cases I defined in advance, and do they *still* pass after I change
something?" An **eval set** is that fixed set of cases plus the machinery to run
and score them.

The harness is deliberately small — three nouns and one verb you can read
end-to-end:

- **case** (:class:`EvalCase`) — one input the agent runs on, paired with what
  "good" means for it (an expected answer, an expected tool trajectory, or both).
- **scorer** (:class:`Scorer`) — a function that turns one run into a verdict
  (:class:`EvalResult`): pass/fail, a number, plus a comment.
- **runner** (:func:`evaluate`) — runs every case (optionally K times), applies
  the scorers, and reports a per-case **pass rate**.

The names are a deliberate, approximate match to real eval platforms so they
transfer: LangSmith calls a case an *Example* (``inputs`` / ``reference_outputs``),
a scorer an *Evaluator* returning ``{key, score}``, and the runner ``evaluate()``;
Langfuse calls a case a *dataset item* with an expected output and a *score*.
Exact field-name fidelity to any one vendor is **not** the goal — recognizable
structure is. This is a *first pass*; L22 scales the same discipline to multi-step
graphs, retrieval quality, LLM-as-judge done properly, and multi-agent systems.

Promoted to ``common/`` (alongside ``agent_loop.py`` and ``tracing.py``) so the
LangGraph lessons import the *same* harness and run the *same* cases against a new
implementation — that import is how "evaluate every agent you build" becomes a
habit you carry forward.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

from pydantic import BaseModel, Field

from .agent_loop import RunResult

# --- the three core pieces: case, scorer, result ----------------------------


class EvalCase(BaseModel):
    """One eval case: an input to run the agent on, plus what "good" means.

    ``inputs`` seeds the run (the task prompt); ``reference_outputs`` says what to
    check against. A scorer reads one or both. (LangSmith calls this an *Example*.)

    Example::

        EvalCase(
            id="chain_calc_lookup",
            inputs={"task": "What is the population of the city '17*23'... "},
            reference_outputs={"answer": "37000000", "expected_tools": ["calculator", "lookup"]},
        )
    """

    id: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    reference_outputs: dict[str, Any] = Field(default_factory=dict)


class EvalResult(BaseModel):
    """The verdict one scorer reaches on one run. (LangSmith: *EvaluationResult*.)

    ``key`` names the metric (e.g. ``"answer_correct"``, ``"no_runaway"``);
    ``score`` is the verdict; ``comment`` is an optional human-readable why.

    L09's scorers return a **bool** ``score`` (pass/fail). The ``float`` option
    exists so a graded scorer (an LLM-judge returning a confidence) fits the same
    type; :attr:`passed` treats any truthy score — ``True`` or a nonzero number —
    as a pass.
    """

    key: str
    score: float | bool
    comment: str | None = None

    @property
    def passed(self) -> bool:
        """Whether this result counts as a pass (a truthy score)."""
        return bool(self.score)


class Scorer(Protocol):
    """A callable that turns one run into one :class:`EvalResult`.

    Keyword-only by design, so a scorer's call site reads like a sentence:
    ``answer_correct(run=result, example=case)``. (LangSmith calls this an
    *Evaluator*.) A scorer reads ``run.final_text`` for **outcome** scoring or
    ``run.trace`` for **trajectory** scoring — or both.
    """

    def __call__(self, *, run: RunResult, example: EvalCase) -> EvalResult: ...


# The "target" under test: how to produce a run for one case. Two run_cases over
# the same cases (e.g. one per model) is exactly the A/B in L09's headline demo.
# (LangSmith calls this argument the *target* of ``evaluate()``.)
RunCase = Callable[[EvalCase], RunResult]


# --- trace readers a trajectory scorer leans on -----------------------------


def tool_trajectory(run: RunResult) -> list[str]:
    """The ordered tool-call *names* a run made, read off its trace.

    The path, name-only — e.g. ``["calculator", "lookup"]``. The cheapest thing a
    trajectory scorer checks: did it take the expected route?
    """
    return [span.name for span in run.trace if span.run_type == "tool"]


def tool_calls(run: RunResult) -> list[tuple[str, dict[str, Any]]]:
    """The ordered ``(tool_name, args)`` pairs a run made, read off its trace.

    The path *with arguments* — e.g. ``[("lookup", {"city": "Tokyo"})]``. Use this
    when the bug is in the arguments (the L08 "wrong arguments" signature) or to
    detect a runaway (the same pair repeating).
    """
    return [(span.name, span.inputs) for span in run.trace if span.run_type == "tool"]


# --- the runner and its report ----------------------------------------------


@dataclass
class SampleResult:
    """One run of one case, plus every scorer's verdict on it.

    Kept around so you can inspect *why* a case flaked — the run (and its trace)
    that produced a particular sample's scores is right here.
    """

    case_id: str
    sample_index: int
    run: RunResult
    results: list[EvalResult]


def _empty_samples() -> list[SampleResult]:
    return []


@dataclass
class CaseSummary:
    """Per-case roll-up across the K samples: how often each check passed.

    ``pass_counts`` maps a scorer ``key`` to the number of samples (out of
    :attr:`samples`) it passed. A single deterministic run gives ``samples=1`` and
    counts of 0 or 1; sampling a flaky case K times turns a verdict into a *rate*.
    """

    case_id: str
    samples: int
    pass_counts: dict[str, int]
    all_pass_count: int  # samples where EVERY scorer passed

    def pass_rate(self, key: str) -> float:
        """Fraction of samples the scorer ``key`` passed (0.0 to 1.0)."""
        return self.pass_counts[key] / self.samples

    @property
    def all_pass_rate(self) -> float:
        """Fraction of samples where *every* scorer passed."""
        return self.all_pass_count / self.samples


@dataclass
class EvalReport:
    """The result of an eval run: per-case pass rates plus the raw samples.

    Read it as a table (:meth:`table`), query a single rate (:meth:`pass_rate`),
    or compare two reports for regressions (:func:`compare`).
    """

    scorer_keys: list[str]
    samples: int
    case_summaries: list[CaseSummary]
    sample_results: list[SampleResult] = field(default_factory=_empty_samples)

    def summary_for(self, case_id: str) -> CaseSummary:
        """The :class:`CaseSummary` for ``case_id`` (raises if absent)."""
        for summary in self.case_summaries:
            if summary.case_id == case_id:
                return summary
        raise KeyError(f"no case {case_id!r} in this report")

    def pass_rate(self, case_id: str, key: str) -> float:
        """The pass rate for one (case, scorer) pair."""
        return self.summary_for(case_id).pass_rate(key)

    def is_pass(self, case_id: str, key: str, *, min_rate: float = 1.0) -> bool:
        """Whether a (case, scorer) pair counts as passing overall.

        With ``min_rate=1.0`` (the strict default) a case must pass on *every*
        sample to count as a pass — the right bar for a regression ratchet.
        """
        return self.pass_rate(case_id, key) >= min_rate

    def table(self) -> str:
        """Render the report as a fixed-width ``count/samples`` table.

        Rows are cases; columns are scorer keys plus an ``ALL`` column (samples
        where every scorer passed). Example::

            case                 answer_correct  no_runaway  ALL
            chain_calc_lookup    3/3             3/3         3/3
            flaky_recover        1/3             3/3         1/3
        """
        id_width = max([len("case"), *(len(s.case_id) for s in self.case_summaries)])
        columns = [*self.scorer_keys, "ALL"]
        col_widths = [max(len(col), len(f"{self.samples}/{self.samples}")) for col in columns]

        def row(label: str, cells: list[str]) -> str:
            parts = [label.ljust(id_width)]
            parts += [cell.ljust(width) for cell, width in zip(cells, col_widths, strict=True)]
            return "  ".join(parts)

        lines = [row("case", columns)]
        for summary in self.case_summaries:
            cells = [f"{summary.pass_counts[key]}/{self.samples}" for key in self.scorer_keys]
            cells.append(f"{summary.all_pass_count}/{self.samples}")
            lines.append(row(summary.case_id, cells))
        return "\n".join(lines)


def evaluate(
    run_case: RunCase,
    cases: Sequence[EvalCase],
    scorers: Sequence[Scorer],
    *,
    samples: int = 1,
) -> EvalReport:
    """Run every case ``samples`` times, score each run, and roll up pass rates.

    For each case: call ``run_case(case)`` to produce a :class:`RunResult` (one
    full ``agent_loop.run`` — several model calls, not one), apply every scorer to
    that run, and record the verdicts. Repeating ``samples`` times turns a single
    pass/fail into a **pass rate**, which is the only honest summary for a
    non-deterministic agent.

    ``run_case`` is the seam that makes the model A/B trivial: pass a ``run_case``
    that drives Sonnet, then one that drives Haiku, over the *same* cases and
    scorers, and compare the two reports.
    """
    sample_results: list[SampleResult] = []
    per_case: dict[str, list[SampleResult]] = {}

    for case in cases:
        case_samples: list[SampleResult] = []
        for sample_index in range(samples):
            result = run_case(case)
            verdicts = [scorer(run=result, example=case) for scorer in scorers]
            sample = SampleResult(
                case_id=case.id,
                sample_index=sample_index,
                run=result,
                results=verdicts,
            )
            case_samples.append(sample)
            sample_results.append(sample)
        per_case[case.id] = case_samples

    # The scorer keys (the report's columns) are whatever the scorers actually
    # returned, in first-seen order — no need to probe the scorers ahead of time.
    scorer_keys = _ordered_keys(sample_results)

    case_summaries: list[CaseSummary] = []
    for case in cases:
        pass_counts: dict[str, int] = dict.fromkeys(scorer_keys, 0)
        all_pass_count = 0
        for sample in per_case[case.id]:
            sample_all_passed = True
            for verdict in sample.results:
                if verdict.passed:
                    pass_counts[verdict.key] += 1
                else:
                    sample_all_passed = False
            if sample.results and sample_all_passed:
                all_pass_count += 1
        case_summaries.append(
            CaseSummary(
                case_id=case.id,
                samples=samples,
                pass_counts=pass_counts,
                all_pass_count=all_pass_count,
            )
        )

    return EvalReport(
        scorer_keys=scorer_keys,
        samples=samples,
        case_summaries=case_summaries,
        sample_results=sample_results,
    )


def _ordered_keys(sample_results: Sequence[SampleResult]) -> list[str]:
    """The metric keys seen across all sample verdicts, in first-seen order."""
    keys: list[str] = []
    for sample in sample_results:
        for verdict in sample.results:
            if verdict.key not in keys:
                keys.append(verdict.key)
    return keys


# --- comparing two runs: the regression ratchet -----------------------------


@dataclass
class Comparison:
    """What changed between two eval reports (e.g. before/after, or model A/B).

    A **regression** is a (case, scorer) that passed in ``before`` and fails in
    ``after`` — the thing an eval set exists to catch. A **fix** is the reverse.
    """

    regressions: list[tuple[str, str]]
    fixes: list[tuple[str, str]]

    @property
    def has_regressions(self) -> bool:
        return bool(self.regressions)


def compare(before: EvalReport, after: EvalReport, *, min_rate: float = 1.0) -> Comparison:
    """Flag which (case, scorer) pairs went pass->fail (regression) or fail->pass (fix).

    A pair counts as passing when its pass rate is ``>= min_rate`` (default
    ``1.0``: must pass on every sample). Only pairs present in *both* reports are
    compared. This is L08's eyeball trace-diff, promoted to a repeatable check.
    """
    regressions: list[tuple[str, str]] = []
    fixes: list[tuple[str, str]] = []
    before_ids = {summary.case_id for summary in before.case_summaries}

    for summary in after.case_summaries:
        if summary.case_id not in before_ids:
            continue
        for key in after.scorer_keys:
            if key not in before.scorer_keys:
                continue
            was_pass = before.is_pass(summary.case_id, key, min_rate=min_rate)
            now_pass = after.is_pass(summary.case_id, key, min_rate=min_rate)
            if was_pass and not now_pass:
                regressions.append((summary.case_id, key))
            elif not was_pass and now_pass:
                fixes.append((summary.case_id, key))

    return Comparison(regressions=regressions, fixes=fixes)
