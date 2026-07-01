# L09 Proctor Notes — Evaluation: first pass

Covers both L09 labs: **L0903** (write your first eval set) and **L0905** (pass rates and
regressions). Both run **offline with no API key** (scripted `FakeModel` / a deterministic model
simulator). One section per problem.

General setup gotchas:

- Everything imports from `fluffy_potato_curriculum.common` — the loop (`agent_loop.run` → `RunResult`),
  the tools (`common.tools.TOOLS`), and the new eval harness (`common.evals`). If imports fail, the
  student's environment isn't synced: `uv sync` from the repo root.
- The harness is ~30 lines in `common/evals.py`. Encourage a student who is stuck on *what a scorer
  returns* to open that file and read `EvalResult` and `evaluate` — it is meant to be read.
- A **scorer** is keyword-only: `def my_scorer(*, run, example) -> EvalResult`. Forgetting the `*`
  (or calling it positionally) is the most common signature error.

---

## L0903_lab problem 1

**Task:** write the `answer_correct` outcome scorer (reference answer is a substring of `final_text`).

COMMON GOTCHAS:
- Returning a bare `bool` instead of an `EvalResult`. The scorer must return
  `EvalResult(key="answer_correct", score=<bool>)`.
- Comparing against `example.reference_outputs` (the dict) instead of `["answer"]` (the value).
- `reference_outputs["answer"]` is a **string** here (`"37000000"`); `in run.final_text` is a plain
  substring test — no `int` conversion needed.

UNBLOCKERS:
- "A scorer is a function from one run to one verdict. Read `run.final_text`; does the expected
  answer appear in it? Return that as the `score`."
- Point them at the `EvalResult` fields: `key`, `score`, optional `comment`.

TIME: ~4 min. STRETCH: add a `comment=` that records what it was looking for, then print the
report and read the comment off `report.sample_results[0].results[0]`.

## L0903_lab problem 2

**Task:** write the `expected_tools` trajectory scorer using `tool_trajectory(run)`.

COMMON GOTCHAS:
- Confusing **outcome** with **trajectory**: this scorer reads `run.trace` (via `tool_trajectory`),
  **not** `run.final_text`. If a student is parsing the answer text here, redirect.
- `tool_trajectory(run)` returns a `list[str]` of tool **names** in order. Compare it to
  `example.reference_outputs["expected_tools"]` with `==` (order matters).
- Comparing a `list` to a `tuple`, or forgetting the call order, makes a correct path look wrong.

UNBLOCKERS:
- "The path is data: `tool_trajectory(run)` is the ordered list of tool names. Does it equal the
  expected list?"
- Have them `print(tool_trajectory(run))` for the `tokyo` run to see `['calculator', 'lookup']`.

TIME: ~4 min. STRETCH: switch to `tool_calls(run)` and assert on the **arguments** too, not just the
names (this is the L08 "arguments are where the truth is" point).

## L0903_lab problem 3

**Task:** write `no_runaway` (a trajectory check) and a regression case — red on `atlantis_runaway`,
green on `atlantis_fixed`.

COMMON GOTCHAS:
- The runaway signature is **two** things: a repeated `(name, args)` pair **or** `termination ==
  "max_steps"`. Checking only one misses cases; the lab's `atlantis_runaway` trips both.
- `dict`s aren't hashable, so you can't put `args` in a `set` directly — hence
  `tuple(sorted(args.items()))`. A student who tries `set(tool_calls(run))` will hit
  `TypeError: unhashable type: 'dict'`. That error *is* the teaching moment.
- Misreading "red when broken" — the runaway case should score **0/1** (fail), not 1/1. A check that
  passes on the broken run tests nothing.

UNBLOCKERS:
- "A regression case is defined by its behavior under the bug: it must **fail when the bug is present
  and pass when it's fixed.**"
- For the hashing snag: "make each call hashable first — `tuple(sorted(args.items()))` — then count
  duplicates."

TIME: ~8 min (the hardest problem in this lab). STRETCH: add a `comment` reporting the termination
cause and the number of tool calls, so a failing run explains itself.

## L0903_lab problem 4

**Task:** loosen the brittle check (`answer_correct_loose`, normalize commas/spaces) and answer the
written question (a quality only a judge/human can score).

COMMON GOTCHAS:
- The point is **not** to make the check pass by any means — it's the *loosest check that still
  catches the bug*. Normalizing commas/spaces is right; switching to "always return True" is the
  anti-lesson (it would stop catching real errors).
- Normalize **both** sides (expected and `final_text`) before comparing, not just one.
- The written answer should name a *genuinely* un-stringifiable quality: tone, "did it acknowledge
  the failure gracefully," factual correctness beyond the reference answer. "Spelling" or "a longer
  number" don't count — those are still string checks.

UNBLOCKERS:
- "Why did the correct run go red? Look at the punctuation in the answer." (the commas)
- "What could you *never* express as a substring rule, no matter how clever?" → leads to the judge.

TIME: ~6 min. STRETCH: this is exactly the quality `L0906_lecture` builds an LLM-judge for — point
finishers there.

---

## L0905_lab problem 1

**Task:** run the weak model at `samples=5` and read the `no_runaway` pass *rate* (a fraction).

COMMON GOTCHAS:
- Leaving `samples` at its default of 1 — then the "rate" is only ever 0/1 or 1/1 and the assert
  `0.0 < rate < 1.0` fails. They must pass `samples=5`.
- Calling `report.pass_rate` with the wrong order of arguments — it's `pass_rate(case_id, key)`,
  i.e. `report.pass_rate("hard_lookup", "no_runaway")`.
- Expecting the *same* number every run. It is deterministic here (the simulator is seeded by
  attempt count) and should read `3/5`; reassure students the real loop would jitter, which is the
  whole reason to sample.

UNBLOCKERS:
- "One run is a coin flip. Run it 5 times and report how often it passed — that's `evaluate(...,
  samples=5)` and then `report.pass_rate(...)`."

TIME: ~5 min. STRETCH: re-run with `samples=20` and watch the rate stabilize; discuss the
cost/confidence trade (the lead-in to `L0906`).

## L0905_lab problem 2

**Task:** build strong and weak reports and `compare(before, after)` to flag regressions.

COMMON GOTCHAS:
- Argument **order** to `compare`: `compare(before, after)` — strong (baseline) first, weak
  (changed) second. Reversing them turns the regressions into "fixes" and the assert fails.
- A regression is reported per **(case, scorer)** pair as a tuple, e.g. `("recover",
  "answer_correct")` — students sometimes look for just the case id.
- `compare` uses `min_rate=1.0` by default (must pass on *every* sample to count as passing). That's
  intended — mention it if a student asks why a 4/5 case counts as failing.

UNBLOCKERS:
- "Baseline first, changed second. `compare` returns `.regressions` (pass→fail) and `.fixes`
  (fail→pass)."

TIME: ~6 min. STRETCH: frame it as a *prompt edit* instead of a model swap — build two strong-ish
run_cases that differ slightly and compare them; same machinery, the regression-guard framing.

## L0905_lab problem 3

**Task:** print both tables and write why a single run can't be trusted.

COMMON GOTCHAS:
- This is a *reading/writing* problem — the code is provided. The written answer should make two
  points: (1) the agent is non-deterministic, so one run is luck; (2) report a **pass rate over K
  samples**, not a single pass/fail.
- Watch for answers that say "run it again until it passes" — that's cherry-picking, the opposite of
  the lesson.

UNBLOCKERS:
- "If your teammate had run it a second time, what might they have seen? What single number would
  you trust instead?"

TIME: ~4 min. STRETCH: ask what pass rate they'd require before calling a case "passing" for a
release gate, and why that threshold is itself a judgment call.
