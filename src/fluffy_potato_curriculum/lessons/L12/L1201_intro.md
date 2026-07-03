# L12 intro: Evaluation — first pass

```yaml
title: "L12 intro: Evaluation — first pass"
keywords: evaluation, eval set, eval case, scorer, runner, pass rate, regression, ratchet, agent, trace
estimated duration: 10
```

> **Lesson:** L12 — Evaluation: first pass.
> **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L12/objectives.md) · [demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L12/demos_or_activities.md)
> **Read in order:** this intro → `L0902_lecture` (build the harness: case / scorer / runner) → `L0903_lab` → `L0904_lecture` (non-determinism → pass rate, and a model A/B) → `L0905_lab` → `L0906_lecture` (eval cost + the scorer spectrum) → `L0907_lecture` (carry it forward).
> **Anchor model: Claude Sonnet 4.6**, with **Haiku 4.5 as the contrast** in the model A/B. Every notebook runs **offline with no API key** (the scripted `FakeModel` from L11); the live Sonnet-vs-Haiku A/B and the live LLM-judge are clearly-marked optional cells.

## Where this lesson sits

In [L11](../L11/L0801_intro.md) you learned to *read* what your agent did: you instrumented the L10 loop so `run(...)` returns a `RunResult` carrying a **trace** — an ordered list of `TraceEvent` spans — and you read that trace to reconstruct a run, locate a failure, and eyeball-diff two runs of the same task. L11's framing was **"produce the record."** L12 is the turn from *observation* to *judgment*:

> **L11 produces the record; L12 judges it.** Tracing tells you *what happened* on one run. Evaluation tells you *whether it was good* — and, crucially, whether it is *still* good after you change something.

The headline move is to stop asking "did this one run look right?" (the L11 eyeball diff) and start asking **"do my agent's runs pass a fixed set of cases I defined in advance?"** That fixed set of cases, plus a way to score them, is an **eval set**. It turns L11's ad-hoc failure-spotting into a repeatable practice.

## The one idea, said three ways

- **Good eval cases come from real failures, not imagination.** The traces you captured in L11 are the source of your cases. The loop is plain: **trace a failure → write a case that catches it → keep the case forever.** A case grown from an observed failure stays relevant; one invented up front tends to test the wrong thing.
- **An eval set is a ratchet against regressions.** Its real payoff isn't the first green run — it's catching the day a prompt tweak or a model swap silently breaks something that used to work. Without the ratchet you rediscover the bug in production weeks later; with it you catch it before shipping.
- **You measure rates, not verdicts.** The agent loop is non-deterministic (L11's "variance budget"). One green run can be luck. The cheapest honest answer is a **pass rate** over a few samples — and a flaky case is itself a *finding*, not noise to ignore.

## What you'll be able to do

By the end of L12 you can:

1. **Build a minimal eval set** for the hand-rolled loop — a **case** (input + what "good" means), a **scorer** (turns one run into a verdict), and a **runner** (runs every case and reports a summary) — and score the **answer**, the **path** (trajectory), or both.
2. **Design regression cases** that target failure modes you saw in L11 traces — each a check that *fails when the bug is present and passes when it's fixed*.
3. **Compare two runs** of the same task to flag regressions — and confront non-determinism by moving from a single pass/fail to a **pass rate** over K samples.
4. **Reason about eval cost** — back-of-envelope *and* off the real token numbers in a trace — and place each scorer on the **cost/judgment spectrum**: exact assertion → fuzzy check → LLM-as-judge → human review.
5. **Carry the practice forward:** when you build or change an agent, you add or run an eval set. The harness you build here lives in `common/evals.py` and is the seed every later agent plugs into.

## The vocabulary this lesson fixes

Use these terms verbatim — they line up with real eval platforms (LangSmith's *Example / Evaluator / `evaluate()`*, Langfuse's *dataset item / score*), so they transfer if you adopt a tool later:

- **Eval set** — a fixed collection of cases plus the machinery to run and score them. The unit of "is my agent good, and is it still good?"
- **Case** (`EvalCase`) — one input the agent runs on (`inputs`), paired with what "good" means (`reference_outputs`: an expected answer, an expected trajectory, or both).
- **Scorer / check** (`Scorer`) — a function `(*, run, example) -> EvalResult` that turns one run into a verdict (`key`, `score`, `comment`).
- **Runner** (`evaluate`) — runs every case (optionally K times), applies the scorers, and reports a per-case **pass rate**.
- **Regression** — a case that used to pass and now fails after a change. The thing an eval set exists to catch.
- **Outcome vs. trajectory** — checking the *final answer* (`run.final_text`) vs. checking the *path* through the trace (`run.trace`). For agents, the path often matters as much as the answer.

## A note on the code you'll see

The eval harness is the new shared module `fluffy_potato_curriculum.common.evals` — `EvalCase`, the `Scorer` protocol, `EvalResult`, and the `evaluate(...)` runner. It sits alongside L10's `common/agent_loop.py` (`run()` → `RunResult`), L11's `common/tracing.py` (`TraceEvent`), and `common/tools.py` (`calculator`, `lookup`, `flaky_fetch`). You'll *read* the harness end-to-end — it's about thirty lines of plain Python, not a framework. The labs drive the loop with the scripted `FakeModel`, so an eval run is deterministic and keyless.

## This is a first pass, on purpose

L12 is a tiny, readable harness over the hand-rolled loop — **not** a production eval system. That smallness is deliberate: the goal is to make the *habit* cheap enough to keep. [L25 (Evaluation revisited)](../../../../docs/origin/CURRICULUM_PRD.md) — outside the mini cut — scales the same discipline to multi-step graphs, retrieval quality (precision@k / recall@k), LLM-as-judge done properly, and multi-agent systems. Knowing where the first pass stops is part of the lesson.

## The takeaway

Tracing without evaluation tells you *what happened*; evaluation without tracing tells you *that something is wrong but not where*. They are a pair, and tracing came first because you cannot evaluate a run you cannot read. The failures you found in L11 traces are your first eval cases — bring them.
