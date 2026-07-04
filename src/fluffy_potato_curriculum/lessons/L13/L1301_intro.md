# L13 intro: Evaluation — first pass

```yaml
title: "L13 intro: Evaluation — first pass"
keywords: evaluation, eval set, dataset, experiment, score, scorer, case, pass rate, regression, ratchet, Langfuse, LLM-as-judge, agent, trace
estimated duration: 10
```

> **Lesson:** L13 — Evaluation: first pass.
> **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L13/objectives.md) · [demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L13/demos_or_activities.md)
> **Read in order:** this intro → `L1302_lecture` (the concept in ~15 lines, then a Langfuse **Dataset**) → `L1303_lab` → `L1304_lecture` (non-determinism → pass rate, and two **Experiments**: Sonnet vs. Haiku) → `L1305_lab` → `L1306_lecture` (eval cost off the trace + the scorer spectrum → a managed **LLM-as-judge**) → `L1307_lecture` (carry the dataset forward).
> **Anchor model: Claude Sonnet 4.6**, with **Haiku 4.5 as the contrast** in the model A/B. **Platform: the cohort's self-hosted Langfuse** — the same instance you traced to in L12. The ~15-line *concept* beat runs offline on the scripted `FakeModel`; every **tooled** cell (dataset upload, experiments, scores, the live models, the LLM-judge) needs the live Langfuse instance and is clearly marked.

## Where this lesson sits

In [L12](../L12/L1201_intro.md) you learned to *read* what your agent did: you instrumented the L10 graph so `run(...)` returns a `RunResult` carrying a **trace** — an ordered list of `TraceEvent` spans — you read that trace to reconstruct a run and locate a failure, and then you **sent that run to the cohort's Langfuse instance** and found it in the UI. L12's framing was **"produce the record."** L13 is the turn from *observation* to *judgment*:

> **L12 produces the record; L13 judges it.** Tracing tells you *what happened* on one run. Evaluation tells you *whether it was good* — and, crucially, whether it is *still* good after you change something. Both live in the same Langfuse.

The headline move is to stop asking "did this one run look right?" (the L12 eyeball diff) and start asking **"do my agent's runs pass a fixed set of cases I defined in advance?"** That fixed set of cases, plus a way to score them, is an **eval set**. It turns L12's ad-hoc failure-spotting into a repeatable practice.

## Concept first, then the platform (the same shape as L12)

L13 teaches evaluation the way L12 taught tracing: **you build the primitive by hand once, so nothing about the tool is magic — then you do the real work in the tool.**

- **The concept, in ~15 lines.** A **case** is an input plus what "good" means; a **scorer** turns one run into a verdict; a **runner** runs every case and reports a summary. You'll see all three as plain Python against the L10/L12 graph — about fifteen lines, no framework.
- **Then Langfuse.** The eval set becomes a Langfuse **Dataset**, the runner becomes a Langfuse **Experiment** over that dataset, and each scorer becomes a Langfuse **score** (code-based *and*, at the end, a managed LLM-as-judge). Evaluation is where a platform pays off fastest — durable datasets, repeated experiments, and a one-toggle LLM-judge are tedious to hand-roll and trivial in Langfuse — so L13 spends most of its minutes in the tool.

## The one idea, said three ways

- **Good eval cases come from real failures, not imagination.** The traces you captured in L12 are the source of your cases. The rule is plain: **trace a failure → add a dataset item that catches it → keep the case forever.** A case grown from an observed failure stays relevant; one invented up front tends to test the wrong thing.
- **An eval set is a ratchet against regressions.** Its real payoff isn't the first green run — it's catching the day a prompt tweak or a model swap silently breaks something that used to work. Langfuse keeps every past experiment run, so the ratchet is durable across days and teammates, not a table that scrolls off a terminal.
- **You measure rates, not verdicts.** The agent graph is non-deterministic (L12's "variance budget"). One green run can be luck. The cheapest honest answer is a **pass rate** over a few samples — and a flaky case is itself a *finding*, not noise to ignore.

## What you'll be able to do

By the end of L13 you can:

1. **Build a minimal eval set** for the L10 graph agent — a **case** (input + what "good" means), a **scorer** (turns one run into a verdict), and a **runner** (runs every case and reports a summary) — and score the **answer**, the **path** (trajectory), or both. Then map each part onto Langfuse: case → **dataset item**, scorer → **score**, runner → **experiment**.
2. **Design regression cases** that target failure modes you saw in L12 traces — each a Langfuse dataset item plus a code-based score that *fails when the bug is present and passes when it's fixed*.
3. **Run an experiment across two models** — Sonnet 4.6 and Haiku 4.5 over the *same* dataset — and use Langfuse's **run-comparison view** to watch the cheaper model's pass rate drop and to flag regressions (pass→fail) after a change.
4. **Reason about eval cost** — back-of-envelope *and* off the real token numbers on a Langfuse experiment trace — and place each scorer on the **cost/judgment spectrum**: exact assertion → fuzzy check → **LLM-as-judge** → human review. You'll turn on Langfuse's managed LLM-judge on one fuzzy quality.
5. **Carry the practice forward:** when you build or change an agent, you add to or run your eval dataset. The Langfuse dataset you build here plus the thin `common/evals.py` types are the seed every later agent — the LangGraph agent in L11, and beyond — plugs into.

## The vocabulary this lesson fixes

Use these terms verbatim — each maps onto a Langfuse concept, so learn both names:

| Concept (you build it) | `common/evals.py` | Langfuse calls it |
| --- | --- | --- |
| **Eval set** — cases + machinery to run/score them | a list of `EvalCase` | a **Dataset** |
| **Case** — one input + what "good" means | `EvalCase(inputs, reference_outputs)` | a **Dataset item** (`input` + `expected_output`) |
| **Scorer / check** — one run → a verdict | `Scorer` → `EvalResult(key, score, comment)` | a **score** (code-based) or **evaluator** (managed LLM-judge) |
| **Runner / harness** — run every case, roll up | `evaluate(...)` (the concept sketch) | an **Experiment** over the dataset |
| **Regression** — used to pass, now fails | — | pass→fail in the **run comparison** |
| **Outcome vs. trajectory** — answer vs. path | reads `run.final_text` vs. `run.trace` | two scores on the same run |

## A note on the code you'll see

The eval vocabulary is the shared module `fluffy_potato_curriculum.common.evals` — `EvalCase`, the `Scorer` protocol, `EvalResult`, a ~15-line `evaluate(...)` kept as an under-the-hood *concept sketch*, and the **Langfuse bridge** (`upload_dataset` maps cases onto a Langfuse Dataset; `emit_score` maps a scorer's verdict onto a Langfuse score). It sits alongside L10's `common/agent_graph.py` (`run(model, tools, user_msg)` → `RunResult`, the reference L10 ReAct graph — `common/agent_loop.py` is the kept-alongside by-hand version), L12's `common/tracing.py` (`TraceEvent`), and `common/tools.py` (`calculator`, `lookup`, `flaky_fetch`). The **concept** cells drive the graph with the scripted `FakeModel`, so they're deterministic and keyless; the **tooled** cells need the live cohort Langfuse (and, for the A/B, an `ANTHROPIC_API_KEY`) — they read their config through `common/config.py` (`require_langfuse()`), never a hard-coded key.

## This is a first pass, on purpose

L13 is a small dataset scored by a handful of checks in a platform you already run — **not** a production eval system. That smallness is deliberate: the goal is to make the *habit* cheap enough to keep. A later *Evaluation revisited* lesson — outside the mini cut — scales the same discipline on the same Langfuse to multi-step graphs, retrieval quality (precision@k / recall@k), LLM-as-judge done rigorously, and multi-agent systems. Knowing where the first pass stops is part of the lesson.

## The takeaway

Tracing without evaluation tells you *what happened*; evaluation without tracing tells you *that something is wrong but not where*. They are a pair, and tracing came first because you cannot evaluate a run you cannot read. The failures you found in L12 traces — now sitting in Langfuse — are your first eval cases. Bring them.
