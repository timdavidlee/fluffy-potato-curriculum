# L09: Evaluation — first pass

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (lesson-plan row L09).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).
> Preceding lesson: [L08 Tracing — reading what your agent did](../L08/objectives.md). Following lesson: L10 Choosing model power for the task (roadmap not yet written; in the mini cut the next taught lesson is L11 Shallow agents in LangGraph).

## Where this lesson sits

By L08, students can *read* what their agent did: they instrument the hand-rolled L07 loop (`agent_loop.run(...)` → `RunResult(final_text, iterations, termination)`) to emit a **structured trace**, read that trace to reconstruct a run, locate a failure from the trace alone, and compare two traces of the same task to separate a real change from run-to-run noise. L08 framed itself as "produce the record"; L09 is **"judge the record."**

L09 is the turn from *observation* to *judgment*. Tracing tells you *what happened* on one run; evaluation tells you *whether it was good*, and — crucially — whether it is *still* good after you change something. The headline move is to stop asking "did this one run look right?" (the L08 eyeball diff) and start asking "do my agent's runs pass a fixed set of cases I defined in advance?" An **eval set** is that fixed set of cases plus a way to score them. It turns the ad-hoc failure-spotting of L08 into a repeatable practice.

This is also the lesson the PRD singles out as a *practice to carry forward*: "establish the practice that every later lesson will carry forward." After L09, every agent students build — the LangGraph shallow agent in L11, and beyond — should come with at least a minimal eval set. L09's job is to make that habit cheap enough to keep.

L09's eval harness stays deliberately **small and hand-rolled**: students write a handful of eval cases and a tiny runner in plain Python against the *same hand-rolled loop they have been tracing*. (This is "concept-first, then tooled," same as L08 — L08 hand-builds a trace before meeting Langfuse; L09 hand-builds an eval harness before any platform eval.) Hosted eval platforms — including the **datasets/experiments feature of the same self-hosted Langfuse** students already use — and LLM-as-judge at scale are named as forward pointers but not taught here; L20 (Evaluation revisited, outside the mini cut) is where evaluation is generalized to multi-step, RAG, and multi-agent systems. <!-- *NEED INPUT*: confirm L09's eval harness stays hand-rolled and defers Langfuse-backed / large-scale LLM-judge eval to L20. Recommendation: yes — L09 is "first pass," built on the hand-rolled loop; keep it a tiny Python harness students can read end-to-end. -->

## Prerequisites

Students arriving at L09 should already be able to:

- Run the hand-rolled model→tool→model loop from L07 and read its `RunResult` (final text, iteration count, termination cause).
- Instrument that loop to emit a **structured trace** — an ordered list of typed events (model calls, tool calls with arguments, tool results with `is_error`, token usage, latency, termination) — and read it (L08, objectives 1 & 3).
- Locate a failure from a trace alone and classify it by signature: tool error, wrong tool arguments, runaway loop, premature termination (L08, objective 2). These failure classes are exactly the targets L09's eval cases attack.
- Compare two traces of the same task and recognize that the loop is **non-deterministic**, so a single differing run proves nothing (L08, objective 4). L09 builds the disciplined version of this comparison.
- Reason about token usage and cost from L01 (cost estimation) and the per-call token/latency fields a trace records — L09's "eval cost" objective leans on this directly.

If a student cannot yet produce and read a trace, redirect to the L08 labs first — L09 evaluates *traced runs*, and the trace's failure signatures are the raw material for designing cases.

## Learning objectives

By the end of L09, a student should be able to:

1. **Build a minimal eval set for a tool-calling / hand-rolled-loop agent.** Concretely:
   - Define the three parts of an **eval set** and reuse the terms verbatim through the lesson: a **case** (an input the agent runs on plus what "good" means for it), a **scorer / check** (the function that turns one run into a pass/fail or a number), and the **runner** (the harness that runs every case and reports a summary).
   - Write a small set of cases (start with ~5–10) for the L07/L08 loop — e.g. the `calculator`+`lookup` chaining task and the `flaky_fetch` failure task — each as a typed record: the task prompt, and the expected outcome expressed as a *checkable* assertion, not a vibe.
   - Implement a tiny **runner** in plain Python: for each case, call `agent_loop.run(...)`, capture the `RunResult` *and* the trace, apply the case's scorer, and print a pass/fail summary across the set. Keep it readable end-to-end — this is a teaching harness, not a framework.
   - Distinguish **what** you can check and pick deliberately: the **final answer** (did `final_text` contain the right city?), the **trajectory** (did the trace show the expected tool sequence?), and **operational** signals (did it terminate `natural` rather than `max_steps`? under a token budget?). Land that an eval set can score the *answer*, the *path*, or both — and that for agents the path often matters as much as the answer.

2. **Design eval cases that target failure modes already seen in traces from L08.** Concretely:
   - Take the failure signatures students found in L08 traces — wrong tool arguments, a runaway loop ending in `max_steps`, an unrecovered tool error, premature `natural` termination on an incomplete answer — and turn each into a **regression case**: an input that reproduces (or used to reproduce) the failure, plus a check that *fails* when the bug is present and *passes* when it's fixed.
   - Explain *why this ordering matters*: good eval cases come from observed failures, not from imagination. The trace is the source of truth for "what actually goes wrong"; L08 produced those traces precisely so L09 has real failure modes to target. State the loop plainly: **trace a failure → write a case that catches it → keep the case forever.**
   - Write at least one **trajectory-based** case (asserting on the trace, e.g. "did not call the same tool with the same args twice") and at least one **outcome-based** case (asserting on `final_text`), so students feel the difference between checking the path and checking the answer.
   - Recognize the limits of brittle checks: an exact-string match on `final_text` is fragile against harmless rewording; choose the *loosest check that still catches the bug* (substring, normalized number, "contains the right tool call"), and name when a more semantic check (an LLM-as-judge) would be needed — without building one yet (forward pointer to L20).

3. **Compare two runs of the same task to flag regressions.** Concretely:
   - Promote L08's eyeball trace-diff into a *repeatable* comparison: run the eval set on version A (e.g. before a prompt edit, or model A) and version B (after the edit, or model B), and report which cases changed pass→fail (a **regression**) or fail→pass (a **fix**).
   - Confront **non-determinism head-on**: because the loop's path varies run-to-run, a single A-vs-B difference can be noise. Introduce the cheapest mitigation — run each case **more than once** and look at how often it passes (a pass *rate*, not a single pass/fail) — and explain why a flaky case needs either a looser check, more samples, or a redesign.
   - Articulate the practice the PRD asks L09 to establish: an eval set is a **ratchet**. Once a case passes, a later change that breaks it is a regression you catch *before* shipping, instead of rediscovering it in a trace weeks later. Every subsequent lesson's agent should carry its eval set forward.

4. **Reason about eval cost — sample size, model calls, and human review.** Concretely:
   - Account for the real cost of an eval run: each case is at least one full `agent_loop.run(...)`, which is *multiple* model calls (one per loop iteration) plus tool calls; running N cases × K samples multiplies that. Use the per-call token counts the trace already records (L01 cost-estimation, L08 token fields) to put a rough dollar/latency figure on a full eval run.
   - Reason about the **sample-size trade-off**: more samples per case give a more trustworthy pass *rate* but cost linearly more. Pick a sample count deliberately for the lesson's toy set and name how you'd choose it for a real one.
   - Place **human review** in the cost model: some qualities can't be auto-checked cheaply and need a person to read the trace and judge. Human review is the most *accurate* and most *expensive* scorer; an automated check is cheaper and scales but can be fooled (objective 2's brittleness). Name the spectrum — exact assertion → fuzzy/automated check → LLM-as-judge → human review — ordered by cost and by how much judgment each can exercise.
   - Decide, for a given quality, *which* scorer is worth its cost — and recognize that this is a design choice, not a default. <!-- *NEED INPUT*: how concretely to quantify cost in the lesson — a back-of-envelope formula (cases × samples × avg model-calls-per-run × per-call cost), a live token tally from the trace, or both? Recommendation: show the formula, then read the actual numbers off a trace so the estimate is grounded. -->

5. **Establish evaluation as a practice every later lesson carries forward.** Concretely:
   - State the discipline as a rule students will reuse: *when you build or change an agent, you add or run an eval set.* Frame the L09 harness as the seed that L11's LangGraph agent (and every agent after) plugs into.
   - Recognize what L09 is *not*: it is a *first pass* — a small, hand-rolled harness — not a production eval system. L20 (Evaluation revisited) scales the same discipline to multi-step graphs, retrieval quality (precision@k / recall@k), LLM-as-judge, and multi-agent systems. Knowing where the first pass stops is part of the objective. **Decision:** the eval harness — `EvalCase`, the `Scorer` protocol, and the runner — is promoted to `common/evals.py` (alongside L08's `common/tracing.py` and the shared `common/tools.py`), so L11 and later lessons import it rather than redefine it. (The exact *case shape / scorer interface* is still being pinned — see open questions.)

## What an eval set is (vocabulary the lecture must establish)

Define these explicitly and reuse them verbatim through the labs and into L11/L20:

- **Eval set** — a fixed collection of cases plus the machinery to run and score them. The unit of "is my agent good, and is it still good?"
- **Case** — one input the agent runs on, paired with a definition of "good" for that input (an expected answer, an expected trajectory, an operational bound, or a mix). Stored as a typed record, like an L08 trace event.
- **Scorer / check** — the function that turns one run (its `RunResult` + trace) into a verdict: pass/fail, a number, or a label. Ranges from an exact assertion to an LLM-as-judge to a human.
- **Runner / harness** — the loop that executes every case (optionally K times), applies the scorer, and reports a summary.
- **Regression** — a case that used to pass and now fails after a change. The thing an eval set exists to catch.
- **Pass rate** — for a non-deterministic agent, the fraction of K samples a case passes; replaces a single pass/fail once runs vary.
- **Outcome vs. trajectory scoring** — checking the *final answer* vs. checking the *path through the trace*. Agents often need both.

### Decided eval schema (approximate, industry-shaped)

**Decision:** like the L08 trace, the eval types are a deliberately *approximate* match to how real eval platforms model evaluation — close enough that a student who later uses one recognizes the structure, but a tiny hand-rolled Python harness, not an SDK. The vocabulary lines up with both **LangSmith** (Example / Evaluator / `evaluate()`) and **Langfuse** (dataset item with expected output / score), so the names transfer to whichever tool students meet. Authored in `common/evals.py` (shared `common/` layer), consuming the `RunResult.trace` from `common/tracing.py`.

- **`EvalCase`** (LangSmith calls this an *Example*): `id`, `inputs: dict` (the task/prompt), `reference_outputs: dict` (the expected answer and/or expected tool trajectory, e.g. `{"answer": "...", "expected_tools": ["calculator", "lookup"]}`).
- **`Scorer`** (LangSmith calls this an *Evaluator*): a callable `(*, run: RunResult, example: EvalCase) -> EvalResult`. It reads `run.final_text` for **outcome** scoring or `run.trace` for **trajectory** scoring.
- **`EvalResult`** (LangSmith: *EvaluationResult*): `key: str` (metric name, e.g. `"answer_correct"`, `"no_runaway"`), `score: float | bool`, `comment: str | None`.
- **`evaluate(cases, scorers, *, samples=K)`** (LangSmith: `evaluate()`): runs each case K times, applies scorers, returns a per-case summary including **pass rate**.
- These names (`inputs` / `reference_outputs` Examples, `{key, score}` Evaluators, an `evaluate()` driver) reappear if students later adopt LangSmith — that recognition is the payoff. Exact field-name fidelity to the current version is explicitly **not** required.

## Main points the lecture should land

- **Evaluation is the judgment built on L08's observation.** Tracing told you *what happened*; evaluation tells you *whether it was good and whether it still is*. They are a pair — L08 produces the record, L09 judges it. Say it first, reusing the L08 framing students just saw.
- **Good eval cases come from real failures, not imagination.** The traces from L08 are the source of cases. Trace a failure, write a case that catches it, keep the case forever. An eval set grown from observed failures stays relevant; one invented up-front tends to test the wrong things.
- **An eval set is a ratchet against regressions.** Its real payoff is not the first green run — it's catching the day a prompt tweak or model swap silently breaks something that used to work. Without the ratchet you rediscover the bug in production; with it you catch it before shipping.
- **Non-determinism means you measure rates, not verdicts.** The agent loop varies run-to-run (L08's variance budget). A single pass or fail can be luck. The cheapest honest answer is a pass *rate* over a few samples — and a flaky case is itself a finding, not just noise to ignore.
- **Score the path, not only the answer.** For agents, *how* it got there matters: the right answer reached by a runaway, over-budget trajectory is still a problem. Trajectory checks (read the trace) catch what an answer-only check misses. This is why L08 came first.
- **Every scorer trades cost for judgment.** Exact assertions are cheap and dumb; humans are expensive and wise; LLM-as-judge sits in between. Choosing a scorer is choosing a point on that curve for a given quality. There is no free, perfect, automatic check.
- **This is a first pass, on purpose.** A tiny readable harness over the hand-rolled loop, not a platform. It establishes the *habit*; L20 scales the *machinery*. Naming that boundary keeps the lesson honest and the scope small.

## Common student confusions to watch for

- *"Evaluation is just testing."* Related, but unit tests assert deterministic outputs; agent eval scores a *non-deterministic* system, often on a *rate* and often on the *trajectory*, sometimes with a fuzzy or human judge. A `==` assertion is one scorer on the cheap end, not the whole picture.
- *"One run passed, so the case passes."* Not for a non-deterministic agent — one green run can be luck. Sample a few times and read the pass rate before believing it.
- *"Exact-match the final answer."* Usually too brittle — harmless rewording fails the check and trains you to ignore reds. Use the loosest check that still catches the bug; escalate to a semantic/LLM judge only when a cheap check genuinely can't express the quality.
- *"Checking the final answer is enough."* Often not — a correct answer reached via a broken, expensive, or runaway path is still a failure you want to catch. Score the trajectory when the path matters.
- *"More eval cases / more samples is always better."* Every case and every sample costs real model calls. A focused set targeting observed failures beats a huge set of invented ones, and sample count is a deliberate cost/confidence trade, not "max it out."
- *"I'll write the eval set from scratch imagining what could go wrong."* Start from L08 traces of what *did* go wrong. Imagined failures test your imagination; traced failures test your agent.
- *"An LLM-as-judge is a free way to check anything."* It's a scorer with its own cost and its own errors — it can be wrong, biased, or gameable. L09 only name-drops it; L20 unpacks what it can and can't reliably score.

## Bridge to L11 (and forward to L20)

In the mini cut, the next taught lesson is **L11 (Shallow agents in LangGraph)**. The handoff is the *practice*, not a specific artifact: when students rebuild the agent as a LangGraph graph in L11, they should bring an eval set with them and run it against the new implementation. That is the cleanest possible demonstration of L09's ratchet — *same cases, different implementation, did anything regress?* — and it makes "evaluate every agent you build" concrete the very next lesson. <!-- *NEED INPUT*: confirm L11's lab is expected to reuse the L09 eval harness against the LangGraph agent. This is the strongest reinforcement of L09's "carry it forward" objective and should be coordinated when L11's roadmap is written. -->

Looking further ahead, **L20 (Evaluation revisited)** — outside the mini cut — extends this first pass to systems L09 deliberately doesn't touch: per-node vs. end-to-end metrics for multi-step graphs, retrieval quality (precision@k / recall@k) for RAG, LLM-as-judge done properly, and multi-agent evaluation. L09 should explicitly signpost L20 as "where this scales," so students read L09's smallness as a starting point, not a ceiling.

> Tooling forward pointer: the same **self-hosted Langfuse** instance students met in L08 (and reuse in L11) also has a datasets/experiments feature that stores eval runs and scores — i.e. the platform version of L09's hand-rolled `evaluate()`. L09 stays the hand-rolled harness (so students see the mechanism), with Langfuse-backed evaluation named as a forward pointer toward L20, consistent with the L08 "concept first, then tooled" stance. <!-- *NEED INPUT*: confirm L09's eval harness stays hand-rolled and Langfuse-backed eval is only a name-drop here (full treatment in L20). Recommendation: yes. -->

> Note on lesson numbering: in the full 20-lesson plan, L10 (Choosing model power) sits between L09 and L11. In the mini cut, L10 is dropped, so L09 hands directly to L11. If the L10 roadmap is later authored, revisit this bridge — L09's cost-and-model-class reasoning (objective 4) is a natural lead-in to L10's model-power trade-offs. <!-- *NEED INPUT*: confirm whether L09 should pre-link L10 at all in the mini-cut delivery, or only mention it in the full-course delivery. Recommendation: keep the bridge pointed at L11 for the mini cut; mention L10 only as a parenthetical so the doc serves both cuts. -->

## Open authoring questions

- <!-- *NEED INPUT*: estimated lecture duration — best guess 75–100 minutes including a code-along that builds the runner and turns two L08 trace failures into regression cases. Likely one lecture; split into "build an eval set / score answer vs. trajectory" and "compare runs / reason about cost" if it runs long. -->
- **Decided (anchor model + contrast):** Claude **Sonnet 4.6** is the anchor (inherits the L01–L07 precedent), and **Haiku 4.5 is used as the contrast** in the objective-3 A/B comparison. The teaching point: run the *same eval set* against both models and watch the cheaper model's **pass rate visibly drop** — a concrete, *quantified* demonstration of what a lower-powered model can and "cannot" do on the same task. This makes the eval set the measurement instrument (not just a regression guard) and grounds objective 4's cost/capability reasoning. (A Sonnet-vs-Sonnet before/after-a-prompt-edit comparison still works for the pure *regression* framing; the model contrast is the headline.) This is the `project_anchor_model` Haiku-4.5-contrast intent, now confirmed.
- **Decided (case/scorer representation):** approximate industry-shaped schema (lines up with LangSmith *and* Langfuse) — `EvalCase` (Example: `inputs` + `reference_outputs`), `Scorer` (Evaluator: `(run, example) -> EvalResult{key, score, comment}`), `evaluate(..., samples=K)` returning per-case pass rates. Authored in `common/evals.py`, consuming `RunResult.trace`. See *Decided eval schema* above.
- **Decided (promote to `common/`):** the eval harness is promoted to `common/evals.py` (`EvalCase`, `Scorer`, runner), alongside L08's `common/tracing.py` (`TraceEvent`) and the shared `common/tools.py`. L11 and later lessons import these rather than redefine them — this is the shared-code rule applied, and the mechanism by which "carry it forward" (objective 5) actually works.
- <!-- *NEED INPUT*: how many samples per case for the toy set, and whether to surface a pass *rate* from the first demo or introduce it only when a flaky case forces it. Recommendation: introduce single pass/fail first, then let a flaky case motivate sampling — the confusion is the lesson. -->
- <!-- *NEED INPUT*: do L09's cases reuse L07/L08's exact tools and tasks (`calculator`, `lookup`, `flaky_fetch` with its four URL behaviors)? Recommendation: yes — evaluating a loop students already traced keeps the focus on eval design, not new tools, and the `flaky_fetch` failure modes give objective 2 ready-made regression cases. -->
- <!-- *NEED INPUT*: how far to go on LLM-as-judge — name-drop only, or show one tiny example of a judge prompt scoring a `final_text` for the limits discussion? Recommendation: one minimal illustrative judge, clearly flagged as "the L20 version is more rigorous," to make the cost/judgment spectrum concrete without expanding scope. -->
- <!-- *NEED INPUT*: overlap check with L08 — L08 already teaches comparing two traces by eye. Confirm L09 *reinforces and formalizes* that into a repeatable eval-set comparison (regression flagging) rather than re-teaching trace reading. The trace-reading skill is assumed from L08, not re-derived here. -->
