# L13: Teacher-led demos — Evaluation: first pass (Langfuse-forward)

> Sibling docs: [objectives.md](objectives.md) (what the lesson aims for), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md).
>
> **Audience for this file:** the teacher running L13. Every demo below is *teacher-driven, no student participation*. Student-driven exercises live in the L13 labs (separate file, stage 2).
>
> **Anchor model for the demos: Claude Sonnet 4.6** (inherits the L01–L10 precedent so the traced loop behaves as students saw it). **Contrast model: Claude Haiku 4.5**, used in Demo 3 as a second experiment over the same dataset to make a lower-powered model's pass rate visibly drop.
>
> **Platform: the cohort's self-hosted Langfuse instance** — the same one L12's tooled half sent traces to. L13 assumes it is up and reachable (keys read through `common/config.py`); the notebooks raise a clear error if not (**Decided:** require live Langfuse, no offline fallback — see [objectives.md](objectives.md) open questions).

## How to read this file

Each demo is a self-contained block with:

- **Goal** — the single insight the demo should land. Tied to a learning objective from [objectives.md](objectives.md).
- **Pre-flight** — what the teacher needs loaded before class.
- **Live script** — the order of operations during the demo. Treat it as a checklist, not a teleprompter.
- **What to highlight** — the moment(s) where the teacher should slow down and say the takeaway out loud.
- **If the demo misbehaves** — graceful fallback for when the model (or the platform) surprises you (it will).

The demos are ordered to match the five learning objectives. **Demo 1** hand-builds the case→scorer→run concept in ~15 lines *and then* uploads the cases as a Langfuse **Dataset** — the "concept first, then tooled" move; **Demo 2** turns two real L12 trace failures into dataset items with code-based **regression scores** (outcome vs. trajectory); **Demo 3** runs the dataset as Langfuse **Experiments** against Sonnet and Haiku, introduces non-determinism → pass rate, and compares the two runs in the Langfuse UI so the cheaper model's pass rate drops on screen; **Demo 4** reads real token cost off a Langfuse experiment trace, walks the scorer cost/judgment spectrum, and turns on **Langfuse's managed LLM-as-judge**. The optional bridge demo carries the *dataset* forward to L04/L11 (objective 5). They build on each other — every demo reuses Demo 1's dataset and the same handful of cases, never a fresh one. Run them in order on first delivery.

> **The spine of L13: reinforce, don't re-teach — and lean on the platform students already have.** L13 sits directly on top of [L12 (Tracing)](../L12/objectives.md). Students already know how to read a trace, eyeball-diff two runs, *and send runs to Langfuse* — L13 does **not** re-derive any of that. It *formalizes* it: the ad-hoc "did this run look right?" of L12 becomes "does my agent pass a fixed dataset I defined in advance?", scored and compared in the same Langfuse. When a demo reads a trace or opens Langfuse, recall the L12 move in one line and move on; the new material is the **dataset**, the **regression score**, the **experiment comparison**, the **cost model**, and the **managed LLM-judge**.

## Pre-flight (once, at the top of the lesson)

The teacher should have, before the first demo starts:

- **A live, reachable cohort Langfuse instance**, with host + keys set in the environment and read through `common/config.py`. Confirm you can open the UI and that the notebook's `require_langfuse()`-style guard passes. **This is a hard dependency for every demo** — dry-run the connection before class. <!-- *NEED INPUT (stage-2 infra)*: confirm the exact config surface (host + public/secret key env vars) and the guard helper name. -->
- **The shared agent loop importable, not rebuilt.** `from fluffy_potato_curriculum.common.agent_loop import run` (the canonical reference copy of L10's hand-rolled loop) and the shared tools from `common/tools.py` (`calculator`, `lookup`, `flaky_fetch` with its four URL behaviors). L13 *evaluates* a loop students already built and traced. `agent_loop.run(...)` returns a `RunResult` carrying `final_text`, `iterations`, `termination`, and — from L12 — `trace: list[TraceEvent]`.
- **The thin `common/evals.py` types + Langfuse bridge** — `EvalCase` (`id`, `inputs: dict`, `reference_outputs: dict`), a `Scorer` callable `(*, run: RunResult, example: EvalCase) -> EvalResult` (`key`, `score`, `comment`), and the bridge helpers (upload `list[EvalCase]` as a Langfuse dataset; emit an `EvalResult` as a Langfuse score on a run). Use these names verbatim — they line up with Langfuse (dataset item / score) and LangSmith (*Example / Evaluator*), the recognition payoff if students adopt a platform later.
- **A ~15-line hand-rolled `evaluate()` sketch** kept in a sibling file — shown *once* in Demo 1 to demystify what a Langfuse experiment does under the hood, then set aside. It is not the deliverable.
- **~5–10 prepared eval cases over the L10/L12 tasks**, reusing the tools above — e.g. the `calculator`+`lookup` chaining task ("the population of the city whose name is `17**2 - 1`") and the `flaky_fetch` failure task. Mix outcome cases (`reference_outputs={"answer": "..."}`) and trajectory cases (`reference_outputs={"expected_tools": ["calculator", "lookup"]}`). <!-- *NEED INPUT (stage-2)*: confirm the final case list and the exact `reference_outputs` → Langfuse `expected_output` mapping. Recommendation: 6–8 cases — enough to make a pass-rate table legible, few enough to run live in seconds. -->
- **Two saved L12 failure runs, captured ahead of class** — the raw material for Demo 2: (a) a **runaway loop** that ended in `max_steps` (same `(tool_name, args)` repeating), and (b) a **wrong-arguments** or **unrecovered tool-error** run on the `flaky_fetch` task. Capture them as `.to_jsonl()` fixtures (the L12 helper) so the demo doesn't depend on reproducing a non-deterministic failure live. <!-- *NEED INPUT (stage-2)*: pick the exact two-or-three saved failures Demo 2 converts into dataset items. Recommendation: one runaway/`max_steps` from the lookup-chaining task, one tool-error from the flaky_fetch task, covering a trajectory bug and an outcome bug. -->
- **Two model clients configured: Sonnet 4.6 (anchor) and Haiku 4.5 (contrast)**, both read through `common/config.py`, for Demo 3's two experiments over the same dataset.
- **The Langfuse project open on the projector** — you will switch to the UI to show the dataset, the experiment runs, the run comparison, and (Demo 4) the per-call token usage and the managed evaluator config.

> Why reuse L10/L12's loop, tools, tasks, *and* Langfuse instance: L13 is about *eval design*, not new agent code, new tools, or a new platform. Evaluating a loop students already traced, in the Langfuse they already use, keeps every minute on the eval concepts — the case, the scorer, the pass rate, the cost, the judge — which *are* the lesson.

## Demo 1 — Concept in 15 lines, then a Langfuse Dataset (Objective 1)

**Goal:** land the three-part vocabulary — **a case is an input plus what "good" means; a scorer turns one run into a verdict; the runner runs every case and reports a summary** — by hand-building it once in ~15 lines, *then* mapping it straight onto Langfuse so students see the platform is the same idea, hosted. Land the outcome-vs-trajectory distinction.

**Pre-flight:**

- The `common/evals.py` types + Langfuse bridge imported.
- Two prepared cases on the slide: one **outcome** case (the calculator+lookup task, `reference_outputs={"answer": "<the city's population>"}`) and one **trajectory** case (same task, `reference_outputs={"expected_tools": ["calculator", "lookup"]}`).

**Live script:**

1. Sketch the shape on the whiteboard before typing: *case in → run the agent → scorer reads the result → pass/fail.* Name each piece with the verbatim term.
2. Show the **~15-line concept**: an `EvalCase`, one **outcome scorer** `answer_correct` (call `agent_loop.run(case.inputs["task"])`, check `run.final_text` contains `case.reference_outputs["answer"]`, return `EvalResult(key="answer_correct", score=..., comment=...)`), and a trivial one-case run that prints the verdict. Say out loud: *"That's the whole idea. A Langfuse experiment is this, hosted and durable."*
3. **Now go tooled.** Upload the prepared cases as a Langfuse **Dataset** using the bridge helper. Switch to the Langfuse UI: show the dataset items, each with its `input` and `expected_output`. This is the *same* `EvalCase` list, now stored where every future run can find it.
4. Add a **trajectory scorer** `expected_tools`: read `run.trace`, extract the ordered tool-call names, check they match `case.reference_outputs["expected_tools"]`. Note that in Langfuse this is just a second **score** on the same run — the *same run* scored two ways: did it get the right answer, *and* did it take the right path.

**What to highlight:**

- The three terms, said out loud and pointed at in both the 15-line code *and* the Langfuse UI: **case** = dataset item, **scorer** = score, **runner** = experiment. Fix them now — they reappear in every lab and in L11.
- **Langfuse is not magic.** The 15-line sketch *is* what an experiment does; the platform makes it durable and comparable, not different. This is the same "concept first, then tooled" move as L12's trace → Langfuse.
- **An eval set can score the answer, the path, or both** — the trajectory scorer reads the L12 trace, which is *why* L12 came first. Both are just scores in Langfuse.

**If the demo misbehaves:**

- If the Langfuse upload fails, that's the hard-dependency biting — check the guard/keys live (model the `require_langfuse()` error being informative). Don't fake it; the platform being real is the point.
- If the outcome scorer fails on a *correct* run because of exact-string matching (e.g. "8.3 million" vs "8,336,817"), don't fix it silently — flag it as the brittleness Demo 2 tackles, and loosen to a substring/normalized-number check.

## Demo 2 — From a trace to a scored regression case in the dataset (Objective 2)

**Goal:** take two *real* failures from L12 traces and turn each into a **dataset item + code-based score** whose check **fails when the bug is present and passes when it's fixed**. Land the headline loop: **trace a failure → add a dataset item that catches it → keep the case forever.** Good eval cases come from observed failures, not imagination.

**Pre-flight:**

- The two saved L12 failure runs (`.to_jsonl()` fixtures): the runaway/`max_steps` run and the tool-error/wrong-args run.
- Demo 1's dataset and scorers, unchanged.

**Live script:**

1. Open the **runaway** trace. Recall the L12 reading in one line — "same `(tool_name, args)` repeating, terminated `max_steps`" — *don't* re-teach trace reading. Add the **dataset item** it deserves and write a **trajectory** score `no_runaway` that reads `run.trace` and fails if any `(tool_name, args)` pair repeats (or if `run.termination == "max_steps"`). Show the score coming back **False** against the saved bad run.
2. Open the **tool-error** trace (the `flaky_fetch` task). Add its dataset item and write an **outcome** score that fails when the final answer never recovered. Show it failing against the saved bad run, then passing against a good run.
3. State the ordering rule out loud and put it on a slide: **trace a failure → add a dataset item that catches it → keep it forever.** The trace from L12 is the source of truth for "what actually goes wrong"; L12 produced these traces (in Langfuse) precisely so L13 has real failure modes to attack.
4. **The brittleness beat.** Show an exact-string match on `final_text` failing against a *correct* run that just reworded the answer. Loosen it to the *loosest check that still catches the bug* — substring, normalized number, "contains the right tool call." Name when you'd need a more semantic check — and defer it to Demo 4's **managed LLM-judge**, not a hand-built one.

**What to highlight:**

- **Trajectory case vs. outcome case, felt side by side:** `no_runaway` asserts on the *path* (the trace), the answer check asserts on the *result* (`final_text`) — two scores on the same dataset. Students should leave able to write one of each.
- A regression case is defined by its behavior under the bug: it **fails when broken, passes when fixed.** A "case" that passes no matter what tests nothing.
- The loosest check that still catches the bug. An over-tight check (exact string) trains you to ignore reds when harmless rewording trips it — worse than no check.

**If the demo misbehaves:**

- If you can't reproduce a failure live, that's *why* the saved `.jsonl` fixtures exist — score against the saved trace. The whole L12 lesson was "don't chase a non-deterministic failure by re-running; read the captured trace." Model that here.
- If a student asks "why not just assert the exact answer?" — that's the Demo 2 punchline arriving early. Run the reworded-but-correct example and let the brittle check fail.

## Demo 3 — Two experiments, one dataset: the pass rate drops in Langfuse (Objective 3)

**Goal:** the headline demo. First confront **non-determinism** — a single pass can be luck — and move from a pass/fail to a **pass rate** over K samples. Then run the *same* dataset as **two Langfuse Experiments** — Sonnet 4.6 and Haiku 4.5 — and use Langfuse's **run-comparison view** to watch the cheaper model's pass rate visibly drop. Land that **an eval dataset is both a regression ratchet and a measurement instrument.**

**Pre-flight:**

- Demo 1's dataset, plus a deliberately **flaky** case — one whose trajectory varies run-to-run so it sometimes passes, sometimes fails. <!-- *NEED INPUT (stage-2)*: pick a case that flakes reliably on Sonnet — e.g. a task where the model sometimes makes an extra lookup call. Dry-run before class; a flaky case that never flakes on the day defeats the beat. -->
- The experiment runner configured for **K samples per item** (Langfuse experiments support repeated runs). <!-- *NEED INPUT (stage-2)*: confirm K for the toy set. Recommendation: K = 3–5 — enough for a rate to read as a rate ("2/3"), cheap enough to run live. -->
- Both model clients (Sonnet 4.6, Haiku 4.5) ready.

**Live script:**

1. **Single run first — let the flaky case bite.** Run the dataset once (one sample per item) against Sonnet. The flaky case passes. Re-run. It fails. Pause: *"Which run do we believe?"* Make the confusion land — don't pre-empt it. This *is* the lesson.
2. Introduce the cheapest honest fix: run each case **K times** and read how often it passes — a **pass rate** (e.g. `no_runaway: 2/3`), not a single verdict. Launch the experiment with K samples; open its aggregated scores in Langfuse. The flaky case now reads as a rate; a flaky case is itself a *finding*, not noise.
3. **The A/B.** Run the same dataset as a second experiment against **Haiku 4.5**, K samples. Open Langfuse's **run comparison** and put the two experiments' pass-rate columns side by side. Watch Haiku's rates drop — especially on the multi-step chaining and failure-recovery cases. A *quantified* demonstration of what a lower-powered model can and "cannot" do on the same task.
4. Reframe the same comparison as a **regression** check: run Sonnet *before* and *after* a small prompt edit as two experiments and let Langfuse show which cases went pass→fail (a **regression**) or fail→pass (a **fix**). Same machinery, different question: "did my change break anything that used to work?" — and Langfuse keeps both runs, so the ratchet is durable.

**What to highlight:**

- **You measure rates, not verdicts.** One green run on a non-deterministic agent can be luck. The pass rate over a few samples is the cheapest answer you can trust. (The disciplined version of L12's "a single differing run proves nothing.")
- **The dataset is a measurement instrument, not just a guard.** Sonnet vs. Haiku on identical cases turns "Haiku is weaker here" from an assertion into two columns in Langfuse — and feeds Demo 4's cost/capability trade-off directly.
- **The ratchet is durable.** Langfuse keeps every experiment run; a regression is caught by comparing today's run to last week's, not by remembering a terminal table. That is the payoff students carry into every later lesson.

**If the demo misbehaves:**

- If the flaky case refuses to flake on the day, force variance: raise the task's ambiguity, or lower the iteration cap so a borderline run sometimes hits `max_steps`. The point is to *show* a rate mattering, not to shame a model.
- If Haiku happens to match Sonnet on your toy cases, add one genuinely multi-step case (deeper chaining, or the full four-URL `flaky_fetch` recovery) where capability separates them. Don't manufacture a gap — pick a harder case that honestly exposes one.
- If the Langfuse comparison view is slow to populate, keep talking through the concept while runs land; if the instance is unreachable mid-demo, that's the hard dependency — fall back to reading the returned `EvalResult`s inline and reconnect after.

## Demo 4 — What does an eval run cost, and which scorer is worth it? (Objective 4)

**Goal:** put a real dollar/latency figure on an eval run — read actual token numbers **off a Langfuse experiment trace** and cross-check a back-of-envelope formula — then walk the scorer **cost/judgment spectrum** and turn on **Langfuse's managed LLM-as-judge**. Land that **every scorer trades cost for judgment; there is no free, perfect, automatic check.**

**Pre-flight:**

- One of Demo 3's experiment runs open in Langfuse, with per-call `usage` token counts visible on the traces.
- **A managed LLM-as-judge evaluator prepared in Langfuse** — a small judge scoring a `final_text` for a quality a cheap check can't express (e.g. "did the answer acknowledge the failure gracefully?"). Configure it before class; keep it minimal and clearly flagged as "the L25 version adds rubrics and bias checks." <!-- *NEED INPUT (stage-2)*: confirm the one judged quality and the judge prompt/evaluator config. Recommendation: judge the flaky_fetch task's "gave up gracefully" answer — a genuinely fuzzy quality no substring check captures — so the judge earns its place. -->

**Live script:**

1. **Ground it in real data first.** Open the Langfuse trace for one experiment run and read the *actual* per-call `usage` token counts. Note that **each case is a *full* `agent_loop.run(...)`** — multiple model calls, not one — and multiply through for the dataset (N cases × K samples × calls/run).
2. **Cross-check the formula.** Write `cost ≈ cases × samples × avg model-calls-per-run × per-call cost` on the board, plug in the toy set's numbers, and compare to the trace-grounded figure — close enough to trust, real enough to not hand-wave. This is the "both ways" the objectives ask for.
3. **The sample-size trade-off.** More samples → a more trustworthy pass rate, but cost grows *linearly*. State how you'd pick K for a real set vs. the toy set.
4. **The scorer spectrum.** Put it on a slide, ordered by cost and by how much judgment each exercises: **exact assertion → fuzzy/automated check → LLM-as-judge → human review.** Then **turn on the managed LLM-as-judge in Langfuse** on the "gave up gracefully" quality — show it scoring runs a substring check can't. Flag its own costs out loud: it's a model call (so it costs tokens), and it can be wrong, biased, or gameable. Emphasize this was **one toggle**, not a lesson's worth of prompt engineering — the reason the platform earns its place here.
5. Place **human review** at the expensive end (Langfuse's annotation/manual-scoring UI): the most *accurate* and most *expensive* scorer, the only one that can judge qualities nothing automated captures cheaply. Choosing a scorer is choosing a point on that curve — a design decision, not a default.

**What to highlight:**

- **An eval run is not free** — it's N cases × K samples × several model calls each, plus the judge's own calls. "More cases / more samples" is a deliberate cost/confidence trade, not "max it out."
- **Every scorer trades cost for judgment.** Exact assertions are cheap and dumb; humans are expensive and wise; the LLM-as-judge sits in between with its *own* error modes — even as a one-toggle Langfuse evaluator. The L13 judge is a one-screen illustration; L25 unpacks what an LLM-judge can and can't reliably score.
- The token numbers you're reading are the *same* fields L12 told you to trace and L01 taught you to cost — now sitting in Langfuse. The eval cost model is those two lessons cashing out.

**If the demo misbehaves:**

- If the managed judge gives an obviously wrong verdict on the day, **keep it** — the most honest possible demonstration that a judge is a fallible scorer, not an oracle. Name it and move on.
- If the live cost numbers are tiny and undramatic on the toy set, extrapolate out loud to a realistic set (hundreds of cases, K=10, on every commit) so the linear cost growth is felt, not dismissed.

## Optional bridge demo — carry the dataset forward (Objective 5)

If time allows, close on the practice the PRD asks L13 to *establish*. Don't build anything new — make the handoff concrete:

1. State the rule on a slide and say it out loud: **when you build or change an agent, you add to or run your eval dataset.** The L13 Langfuse dataset plus the `common/evals.py` types are the seed every later agent plugs into.
2. Preview L11: the *same* Langfuse **dataset** built today will run as an experiment against the **LangGraph shallow agent** students build in L11 — *same dataset, different implementation, did anything regress?* — read directly in Langfuse's run comparison. Already settled by the shared-`common/` decision (L11's lab imports `common/evals.py` and reuses the dataset). (In the mini cut the very next lesson is [L04 (workflows/DAGs)](../L04/objectives.md), whose deterministic flow is itself trivially evaluable — a natural place to reinforce the habit even earlier.)
3. Signpost L25 as "where this scales" — multi-step graphs, retrieval quality (precision@k / recall@k), LLM-as-judge done rigorously, multi-agent systems, all on the same Langfuse. L13 is a *first pass* on purpose; naming the boundary keeps the lesson honest and the scope small.

Don't teach LangGraph or the L25 machinery here — just land that the dataset students just built is the thing they'll carry forward, the same way L12's hand-rolled trace mapped onto Langfuse.

<!-- *NEED INPUT (stage-2)*: include this bridge demo as the L13 closer, or fold its "carry it forward" message into Demo 3's ratchet beat? Recommendation: keep it as a short explicit closer — objective 5 is a *practice* objective, and a named handoff lands it better than a buried aside. -->

## Pacing notes for the teacher

- **Per-demo time:** Demo 1 is 15–20 minutes (the 15-line concept + the dataset upload + the two scorers). Demo 2 is 12–18 (two cases from saved traces + the brittleness beat). Demo 3 is the centerpiece, 15–22 (single→rate, then the two-experiment Sonnet/Haiku comparison in the UI). Demo 4 is 12–18 (cost off the trace + the scorer spectrum + turning on the managed judge). Bridge is 5–8. Total ~60–85 minutes plus discussion — fits the **~75–100 minute** single lecture pinned in [objectives.md](objectives.md). If it runs long, split at the Demo 2/3 boundary: "concept → dataset → scores" then "compare experiments / cost / judge."
- **Live-coding budget:** only Demo 1's 15-line concept and Demo 2's two scorers need live-coding. Demo 1's dataset upload and Demos 3–4 are mostly **SDK calls + Langfuse UI**; do **not** re-derive scorers in each demo. Keep the completed `common/evals.py` and the prepared dataset ready.
- **Platform dependency:** Langfuse being up is a *hard* pre-flight check, not a nice-to-have — the notebooks require it (no offline fallback). Dry-run the connection, the dataset upload, an experiment run, and the managed evaluator before class. If the shared instance is flaky, that lands worse than any model surprise.
- **Variance budget:** the agent loop is non-deterministic — that's the *subject* of Demo 3, not just a nuisance. Budget a re-run wherever a specific tool-call path matters, and **capture the saved failure traces ahead of class** so Demo 2 never depends on reproducing a failure live.
- **The audience watches, doesn't participate.** Resist "what should this case check?" as a group question — that's a lab pattern. Hands-on case-writing, dataset upload, and the run-it-yourself experiment are for the L13 labs.

## Open authoring questions

Most of L13's big decisions are pinned in [objectives.md](objectives.md) (Langfuse-forward hybrid, require-live-Langfuse, anchor + Haiku contrast as two experiments, the `EvalCase`/`Scorer`/`EvalResult` types + Langfuse bridge in `common/evals.py`, reuse of `common/tools.py`, single-pass-then-rate, cost-off-the-trace, managed LLM-judge, reinforce-don't-re-teach L12). The remaining open items are stage-2 mechanics:

- <!-- *NEED INPUT*: the exact Langfuse config surface in `common/config.py` (host + public/secret key env vars) and the `require_langfuse()`-style guard the notebooks call at the top. -->
- <!-- *NEED INPUT*: the exact two-or-three saved L12 failure runs Demo 2 converts into dataset items + regression scores (one runaway/`max_steps`, one flaky_fetch tool-error recommended). -->
- <!-- *NEED INPUT*: the final eval-case list and the precise `reference_outputs` → Langfuse `expected_output` mapping for outcome vs. trajectory cases (6–8 cases recommended). -->
- <!-- *NEED INPUT*: the sample count K for the toy set (3–5 recommended) — concept is the pass rate, not the number. -->
- <!-- *NEED INPUT*: which case is the deliberately flaky one in Demo 3, and that it flakes reliably on Sonnet on a dry-run. -->
- <!-- *NEED INPUT*: the one quality the Demo 4 managed LLM-as-judge scores, and its evaluator config (the flaky_fetch "gave up gracefully" answer recommended). -->
- <!-- *NEED INPUT*: whether experiments are launched purely from the notebook via the Langfuse SDK (`langfuse>=4.7.1`, already a dep) or partly clicked in the UI on the projector — affects how the runner is shown live. -->
