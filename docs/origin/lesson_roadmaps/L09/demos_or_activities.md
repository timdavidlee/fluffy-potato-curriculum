# L09: Teacher-led demos — Evaluation: first pass

> Sibling docs: [objectives.md](objectives.md) (what the lesson aims for), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md).
>
> **Audience for this file:** the teacher running L09. Every demo below is *teacher-driven, no student participation*. Student-driven exercises live in the L09 labs (separate file, stage 2).
>
> **Anchor model for the demos: Claude Sonnet 4.6** (inherits the L01–L07 precedent so the traced loop behaves as students saw it). **Contrast model: Claude Haiku 4.5**, used in Demo 3 to make a lower-powered model's pass rate visibly drop on the *same* eval set.

## How to read this file

Each demo is a self-contained block with:

- **Goal** — the single insight the demo should land. Tied to a learning objective from [objectives.md](objectives.md).
- **Pre-flight** — what the teacher needs loaded before class.
- **Live script** — the order of operations during the demo. Treat it as a checklist, not a teleprompter.
- **What to highlight** — the moment(s) where the teacher should slow down and say the takeaway out loud.
- **If the demo misbehaves** — graceful fallback for when the model surprises you (it will).

The demos are ordered to match the five learning objectives from [objectives.md](objectives.md). Demo 1 builds the harness (case → scorer → runner) and lands outcome-vs-trajectory scoring; Demo 2 turns two real L08 trace failures into regression cases; Demo 3 introduces non-determinism → pass rate, then runs the *same* eval set against Sonnet and Haiku so the cheaper model's pass rate drops on screen; Demo 4 puts a dollar/latency figure on an eval run and walks the scorer cost/judgment spectrum (including one minimal LLM-as-judge). The optional bridge demo carries the eval set forward to L11/L12 (objective 5). They build on each other — every demo reuses Demo 1's harness and the same handful of cases, never a fresh one. Run them in order on first delivery.

> **The spine of L09: reinforce, don't re-teach.** L09 sits directly on top of [L08 (Tracing)](../L08/objectives.md). Students already know how to read a trace and eyeball-diff two runs — L09 does **not** re-derive that skill. It *formalizes* it: the ad-hoc "did this run look right?" of L08 becomes "does my agent pass a fixed set of cases I defined in advance?" When a demo reads a trace, recall the L08 move in one line and move on; the new material is the **harness**, the **regression case**, the **pass rate**, and the **cost model**.

## Pre-flight (once, at the top of the lesson)

The teacher should have, before the first demo starts:

- **The shared agent loop importable, not rebuilt.** `from fluffy_potato_curriculum.common.agent_loop import run` (the canonical reference copy of L07's hand-rolled loop) and the shared tools from `common/tools.py` (`calculator`, `lookup`, `flaky_fetch` with its four URL behaviors). L09 *evaluates* a loop students already built and traced — re-deriving it would waste the lesson. `agent_loop.run(...)` returns a `RunResult` carrying `final_text`, `iterations`, `termination`, and — from L08 — `trace: list[TraceEvent]`.
- **A small set of saved L08 traces of *known failures*, captured ahead of class** — the raw material for Demo 2. At minimum: (a) a **runaway loop** that ended in `max_steps` (same `(tool_name, args)` repeating), and (b) a **wrong-arguments** or **unrecovered tool-error** run on the `flaky_fetch` task. These are exactly the failure signatures students hunted for in L08; here they become eval cases. Capture them as `.to_jsonl()` files (the L08 helper) so the demo doesn't depend on reproducing a non-deterministic failure live. <!-- *NEED INPUT*: pick the exact two-or-three saved failures Demo 2 converts into cases. Recommendation: one runaway/`max_steps` case from the lookup-chaining task and one tool-error-handling case from the flaky_fetch task, so the two demos cover both a trajectory bug and an outcome bug. Stage 2 captures and ships these `.jsonl` fixtures. -->
- **The `common/evals.py` harness — written *live* in Demo 1, kept complete in a sibling file to paste if live-coding falls behind.** Its three pieces match the *Decided eval schema* in [objectives.md](objectives.md): `EvalCase` (`id`, `inputs: dict`, `reference_outputs: dict`), a `Scorer` callable `(*, run: RunResult, example: EvalCase) -> EvalResult` (`key`, `score`, `comment`), and `evaluate(cases, scorers, *, samples=K)` returning a per-case summary including a **pass rate**. Use these names verbatim — they line up with LangSmith (*Example / Evaluator / `evaluate()`*) and Langfuse (dataset item / score), which is the recognition payoff if students adopt a platform later.
- **~5–10 prepared eval cases over the L07/L08 tasks**, reusing the tools above — e.g. the `calculator`+`lookup` chaining task ("the population of the city whose name is `17**2 - 1`") and the `flaky_fetch` failure task. Mix outcome cases (`reference_outputs={"answer": "..."}`) and trajectory cases (`reference_outputs={"expected_tools": ["calculator", "lookup"]}`). <!-- *NEED INPUT*: confirm the final case list and the exact reference_outputs shape. Recommendation: 6–8 cases — enough to make a pass-rate table legible, few enough to run live in seconds. -->
- **Two model clients configured: Sonnet 4.6 (anchor) and Haiku 4.5 (contrast)**, both read through `common/config.py`, for Demo 3's A/B. The *same* eval set runs against both.
- **A token/cost readout for Demo 4** — either the per-call `usage` fields the L08 trace already records, or the same run open in the cohort's shared Langfuse instance. The cost demo reads *real numbers off a trace*, not a hand-wave.

> Why reuse L07/L08's loop, tools, and tasks: L09 is about *eval design*, not new agent code or new tools. Evaluating a loop students already traced keeps every minute on the eval concepts — the case, the scorer, the pass rate, the cost — which *are* the lesson. New tools mid-demo would dilute the message exactly as a new loop would.

## Demo 1 — Case, scorer, runner: the eval harness made visible (Objective 1)

**Goal:** build a tiny eval harness from scratch in front of the class and run it on the loop students already know. Land the three-part vocabulary from [objectives.md](objectives.md) — **a case is an input plus what "good" means; a scorer turns one run into a verdict; the runner runs every case and reports a summary** — and the outcome-vs-trajectory distinction.

**Pre-flight:**

- An empty `common/evals.py` (or notebook cell) the teacher fills in live.
- Two prepared cases on the slide: one **outcome** case (the calculator+lookup task, `reference_outputs={"answer": "<the city's population>"}`) and one **trajectory** case (same task, `reference_outputs={"expected_tools": ["calculator", "lookup"]}`).

**Live script:**

1. Sketch the shape on the whiteboard before typing: *case in → run the agent → scorer reads the result → pass/fail.* Name each piece with the verbatim term.
2. Live-code `EvalCase` (`id`, `inputs`, `reference_outputs`) and one **outcome scorer** — `answer_correct`: call `agent_loop.run(case.inputs["task"])`, then check `run.final_text` contains `case.reference_outputs["answer"]`. Return an `EvalResult(key="answer_correct", score=True/False, comment=...)`.
3. Live-code the **runner** `evaluate(cases, scorers)`: for each case, run the loop once, apply each scorer, collect results, print a pass/fail table. Run it on the two cases. Read the table out loud.
4. Now add a **trajectory scorer** — `expected_tools`: read `run.trace`, extract the ordered tool-call names, check they match `case.reference_outputs["expected_tools"]`. Re-run. Show that the *same run* is now scored two ways: did it get the right answer, *and* did it take the right path.

**What to highlight:**

- The three terms, said out loud and pointed at in the code: **case**, **scorer**, **runner**. These reappear in every lab and in L12 — fix them now.
- **An eval set can score the answer, the path, or both.** For agents the path often matters as much as the answer — the trajectory scorer is reading the L08 trace, which is *why* L08 came first. Say that connection explicitly.
- The scorer is just a function from `(run, example)` to a verdict. Nothing magic — the "framework" is ~30 lines they can read end-to-end.

**If the demo misbehaves:**

- If live-coding falls behind, paste the completed `common/evals.py` and walk it line by line. Don't sacrifice the *run* — the printed pass/fail table is where "eval set" stops being abstract.
- If the outcome scorer fails on a *correct* run because of exact-string matching (e.g. the model wrote "8.3 million" vs your "8,336,817"), don't fix it silently — flag it as the brittleness Demo 2 tackles, and loosen to a substring or normalized-number check.

## Demo 2 — From a trace to a regression case (Objective 2)

**Goal:** take two *real* failures from L08 traces and turn each into a case whose check **fails when the bug is present and passes when it's fixed**. Land the headline loop from [objectives.md](objectives.md): **trace a failure → write a case that catches it → keep the case forever.** Good eval cases come from observed failures, not imagination.

**Pre-flight:**

- The two saved L08 failure traces from pre-flight (`.to_jsonl()` fixtures): the runaway/`max_steps` run and the tool-error/wrong-args run.
- Demo 1's harness, unchanged.

**Live script:**

1. Open the **runaway** trace. Recall the L08 reading in one line — "same `(tool_name, args)` repeating, terminated `max_steps`" — *don't* re-teach trace reading. Then write the case it deserves: a **trajectory** check `no_runaway` that reads `run.trace` and fails if any `(tool_name, args)` pair repeats (or if `run.termination == "max_steps"`). Show it **failing** against the saved bad run.
2. Open the **tool-error** trace (the `flaky_fetch` task). Write an **outcome** check that fails when the final answer never recovered. Show it failing against the saved bad run, then passing against a good run.
3. State the ordering rule out loud and put it on a slide: **trace a failure → write a case that catches it → keep it forever.** The trace from L08 is the source of truth for "what actually goes wrong"; L08 produced these traces precisely so L09 has real failure modes to attack.
4. **The brittleness beat.** Show an exact-string match on `final_text` failing against a *correct* run that just reworded the answer. Loosen it to the *loosest check that still catches the bug* — substring, normalized number, "contains the right tool call." Name when you'd need a more semantic check (an LLM-as-judge) — and defer building one to Demo 4.

**What to highlight:**

- **Trajectory case vs. outcome case, felt side by side:** `no_runaway` asserts on the *path* (the trace), the answer check asserts on the *result* (`final_text`). Students should leave able to write one of each.
- A regression case is defined by its behavior under the bug: it **fails when broken, passes when fixed.** A "case" that passes no matter what tests nothing.
- The loosest check that still catches the bug. An over-tight check (exact string) trains you to ignore reds when harmless rewording trips it — that's worse than no check.

**If the demo misbehaves:**

- If you can't reproduce a failure live, that's *why* the saved `.jsonl` fixtures exist — score against the saved trace. The whole L08 lesson was "don't chase a non-deterministic failure by re-running; read the captured trace." Model that here.
- If a student asks "why not just assert the exact answer?" — that's the Demo 2 punchline arriving early. Run the reworded-but-correct example and let the brittle check fail.

## Demo 3 — Same eval set, two models: the pass rate drops (Objective 3)

**Goal:** the headline demo. First confront **non-determinism** — a single pass can be luck — and move from a pass/fail to a **pass rate** over K samples. Then run the *same* eval set against **Sonnet 4.6 and Haiku 4.5** and watch the cheaper model's pass rate visibly drop. Land that **an eval set is both a regression ratchet and a measurement instrument.**

**Pre-flight:**

- Demo 1's harness extended with `evaluate(cases, scorers, *, samples=K)` — runs each case K times and reports a pass *rate*. <!-- *NEED INPUT*: confirm K for the toy set. Recommendation: K = 3–5 — enough for a rate to read as a rate (e.g. "2/3"), cheap enough to run live. The concrete count is a stage-2 detail; the *concept* (rate, not verdict) is the lesson. -->
- The full prepared case set, plus a deliberately **flaky** case — one whose trajectory varies run-to-run so it sometimes passes, sometimes fails. <!-- *NEED INPUT*: pick a case that flakes reliably on Sonnet — e.g. a task where the model sometimes makes an extra lookup call. Dry-run before class; a flaky case that never flakes on the day defeats the beat. -->
- Both model clients (Sonnet 4.6, Haiku 4.5) ready.

**Live script:**

1. **Single pass/fail first — let the flaky case bite.** Run the eval set once with `samples=1`. The flaky case passes. Re-run. It fails. Pause: *"Which run do we believe?"* Make the confusion land — don't pre-empt it. This *is* the lesson.
2. Introduce the cheapest honest fix: run each case **K times** and report how often it passes — a **pass rate** (e.g. `no_runaway: 2/3`), not a single verdict. Re-run with `samples=K`. The flaky case now reads as a rate; a flaky case is itself a *finding*, not noise to ignore.
3. **The A/B.** Run the same eval set against **Sonnet 4.6**, then against **Haiku 4.5**, K samples each. Put the two pass-rate columns side by side. Watch Haiku's rates drop — especially on the multi-step chaining and the failure-recovery cases. This is a *quantified* demonstration of what a lower-powered model can and "cannot" do on the same task.
4. Reframe the same comparison as a **regression** check: run Sonnet *before* and *after* a small prompt edit and report which cases went pass→fail (a **regression**) or fail→pass (a **fix**). Same machinery, different question: "did my change break anything that used to work?"

**What to highlight:**

- **You measure rates, not verdicts.** One green run on a non-deterministic agent can be luck. The pass rate over a few samples is the cheapest answer you can actually trust. (This is the disciplined version of L08's "a single differing run proves nothing.")
- **The eval set is a measurement instrument, not just a guard.** Sonnet vs. Haiku on identical cases turns "Haiku is weaker here" from an assertion into a number — and feeds Demo 4's cost/capability trade-off directly.
- **The ratchet.** Once a case passes, a later change that breaks it is a regression you catch *before* shipping. That is the payoff students carry into every later lesson.

**If the demo misbehaves:**

- If the flaky case refuses to flake on the day, force variance: raise the task's ambiguity, or lower the iteration cap so a borderline run sometimes hits `max_steps`. The point is to *show* a rate mattering, not to shame a model.
- If Haiku happens to match Sonnet on your toy cases, add one genuinely multi-step case (deeper chaining, or the full four-URL `flaky_fetch` recovery) where capability separates them. Don't manufacture a gap that isn't there — pick a harder case that honestly exposes one.
- If both models pass everything, your cases are too easy to be a measurement instrument — that's a teachable point in itself: a green eval set tells you nothing about *headroom*.

## Demo 4 — What does an eval run cost, and which scorer is worth it? (Objective 4)

**Goal:** put a real dollar/latency figure on an eval run two ways — a back-of-envelope formula *and* actual token numbers read off a trace — then walk the scorer **cost/judgment spectrum** and show one minimal LLM-as-judge. Land that **every scorer trades cost for judgment; there is no free, perfect, automatic check.**

**Pre-flight:**

- The token/cost readout from pre-flight (trace `usage` fields, or the run open in Langfuse).
- A tiny LLM-as-judge scorer prepared: a small judge prompt that scores a `final_text` for a quality a cheap check can't express (e.g. "did the answer acknowledge the failures gracefully?"). Keep it minimal and clearly flagged as "the L23 version is more rigorous." <!-- *NEED INPUT*: confirm the one judged quality and the judge prompt. Recommendation: judge the flaky_fetch task's "gave up gracefully" answer — a genuinely fuzzy quality no substring check captures — so the judge earns its place rather than duplicating a cheap check. -->

**Live script:**

1. **Back-of-envelope first.** Write the formula on the board: `cost ≈ cases × samples × avg model-calls-per-run × per-call cost`. Plug in the toy set's numbers (e.g. 8 cases × 3 samples × ~3 calls/run). Get a rough figure. Note that **each case is a *full* `agent_loop.run(...)`** — multiple model calls, not one.
2. **Ground it in real data.** Open the trace (or Langfuse) for one run and read the *actual* per-call `usage` token counts. Multiply through. Compare to the estimate — close enough to trust the formula, real enough to not hand-wave. This is the "both ways" the objectives ask for.
3. **The sample-size trade-off.** More samples → a more trustworthy pass rate, but cost grows *linearly*. State how you'd pick K for a real set vs. the toy set.
4. **The scorer spectrum.** Put it on a slide, ordered by cost and by how much judgment each exercises: **exact assertion → fuzzy/automated check → LLM-as-judge → human review.** Then run the prepared **LLM-as-judge** on the "gave up gracefully" quality — show it scoring something a substring check can't. Flag its own costs out loud: it's a model call (so it costs tokens), and it can be wrong, biased, or gameable.
5. Place **human review** at the expensive end: the most *accurate* and most *expensive* scorer, the only one that can judge qualities nothing automated captures cheaply. Choosing a scorer is choosing a point on that curve — a design decision, not a default.

**What to highlight:**

- **An eval run is not free** — it's N cases × K samples × several model calls each. "More cases / more samples" is a deliberate cost/confidence trade, not "max it out."
- **Every scorer trades cost for judgment.** Exact assertions are cheap and dumb; humans are expensive and wise; the LLM-as-judge sits in between with its *own* error modes. The L09 judge is a one-screen illustration; L23 unpacks what an LLM-judge can and can't reliably score.
- The token numbers you're reading are the *same* fields L08 told you to trace and L01 taught you to cost. The eval cost model is those two lessons cashing out.

**If the demo misbehaves:**

- If the LLM-judge gives an obviously wrong verdict on the day, **keep it** — that's the most honest possible demonstration that a judge is a fallible scorer, not an oracle. Name it and move on.
- If the live cost numbers are tiny and undramatic on the toy set, extrapolate out loud to a realistic set (hundreds of cases, K=10, on every commit) so the linear cost growth is felt, not dismissed.

## Optional bridge demo — carry the eval set forward (Objective 5)

If time allows, close on the practice the PRD asks L09 to *establish*. Don't build anything new — make the handoff concrete:

1. State the rule on a slide and say it out loud: **when you build or change an agent, you add or run an eval set.** The L09 harness in `common/evals.py` is the seed every later agent plugs into.
2. Preview L12: the *same* `EvalCase`s built today will run against the **LangGraph shallow agent** students build in L12 — *same cases, different implementation, did anything regress?* That is the cleanest possible demonstration of the ratchet, and it's already settled by the shared-`common/` decision (L12's lab imports `common/evals.py`). (In the mini cut the very next lesson is [L11 (workflows/DAGs)](../L11/objectives.md), whose deterministic flow is itself trivially evaluable — a natural place to reinforce the habit even earlier.)
3. Signpost L23 as "where this scales" — multi-step graphs, retrieval quality (precision@k / recall@k), LLM-as-judge done properly, multi-agent systems. L09 is a *first pass* on purpose; naming the boundary keeps the lesson honest and the scope small.

Don't teach LangGraph or the L23 machinery here — just land that the tiny harness students just built is the thing they'll carry forward, the same way L08's hand-rolled trace mapped onto Langfuse.

<!-- *NEED INPUT*: include this bridge demo as the L09 closer, or fold its "carry it forward" message into Demo 3's ratchet beat? Recommendation: keep it as a short explicit closer — objective 5 is a *practice* objective, and a named handoff lands it better than a buried aside. -->

## Pacing notes for the teacher

- **Per-demo time:** Demo 1 is the long one (15–20 minutes including the live-code build of the harness). Demo 2 is 12–18 (two cases from saved traces + the brittleness beat). Demo 3 is the centerpiece, 15–22 (single→rate, then the Sonnet/Haiku A/B). Demo 4 is 12–18 (cost both ways + the scorer spectrum + the LLM-judge). Bridge is 5–8. Total ~60–85 minutes plus discussion — fits the **~75–100 minute** single lecture pinned in [objectives.md](objectives.md). If it runs long, split at the Demo 2/3 boundary: "build an eval set / score answer vs. trajectory" then "compare runs / reason about cost."
- **Live-coding budget:** only Demo 1's harness and Demo 2's two scorers need live-coding. Demos 3 and 4 *reuse* that harness with small additions (`samples=K`, the judge scorer); do **not** re-derive the harness in each demo. Keep the completed `common/evals.py` ready to paste.
- **Variance budget:** the agent loop is non-deterministic — that's the *subject* of Demo 3, not just a nuisance. Budget a re-run wherever a specific tool-call path matters, and **capture the saved failure traces ahead of class** so Demo 2 never depends on reproducing a failure live.
- **The audience watches, doesn't participate.** Resist "what should this case check?" as a group question — that's a lab pattern. Hands-on case-writing and the run-it-yourself eval are for the L09 labs.

## Open authoring questions

Most of L09's big decisions are already pinned in [objectives.md](objectives.md) (anchor + Haiku contrast, the `EvalCase`/`Scorer`/`evaluate()` schema in `common/evals.py`, reuse of `common/tools.py`, single-pass-then-rate, cost-both-ways, one illustrative LLM-judge, reinforce-don't-re-teach L08). The remaining open items are stage-2 mechanics:

- <!-- *NEED INPUT*: the exact two-or-three saved L08 failure traces Demo 2 converts into cases, captured as `.jsonl` fixtures. Recommendation in the pre-flight (one runaway/`max_steps`, one flaky_fetch tool-error). -->
- <!-- *NEED INPUT*: the final eval-case list and the precise `reference_outputs` shape for outcome vs. trajectory cases (6–8 cases recommended). -->
- <!-- *NEED INPUT*: the sample count K for the toy set (3–5 recommended) — concept is the pass rate, not the number. -->
- <!-- *NEED INPUT*: which case is the deliberately flaky one in Demo 3, and that it flakes reliably on Sonnet on a dry-run. -->
- <!-- *NEED INPUT*: the one quality the Demo 4 LLM-as-judge scores, and its judge prompt (the flaky_fetch "gave up gracefully" answer recommended). -->
- <!-- *NEED INPUT*: are the demos run in a projected Jupyter notebook, a slide-embedded REPL, or a demo-runner script? Affects how the harness is shown live. Mirrors the same open question in L07's demos. -->
- <!-- *NEED INPUT*: whether to show the cost readout (Demo 4) off the in-memory trace `usage` fields or the shared Langfuse instance — the latter ties back to L08's hosted-tracer step but adds a dependency on the cohort instance being up. -->
