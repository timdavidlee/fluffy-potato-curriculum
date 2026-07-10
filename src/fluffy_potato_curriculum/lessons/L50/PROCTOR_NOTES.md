# L50 Proctor Notes — Agent mini-project walkthrough

**This lesson is a walkthrough, not a lecture+lab.** There are **no student labs** and no
`_empty`/`_solutions` pair. You drive one guided-build notebook — [`L5003_lecture.ipynb`](L5003_lecture.ipynb) —
from a blank cell to a traced, evaluated shallow agent, and students rebuild it alongside you, cell
by cell. Read the framing deck [`L5002_lecture`](L5002_lecture.md) first (≈15 min), then build.
So these notes are keyed by the notebook's **six segments**, not by lab problems.

The build is **integrative, not additive** — it teaches no new concept. Every primitive comes from
`fluffy_potato_curriculum.common`; the *only* new code is one small tool. If you find yourself
re-teaching how tracing or eval works, you've left L50's lane — recall the owning lesson in one line
and move on.

## The one framing you must have ready: `create_agent` vs `agent_graph.run`

Students met the shallow agent in **L11** as `create_agent(model, tools)`. The walkthrough does
**not** call `create_agent` — it calls **`agent_graph.run` / `arun`**. Have this answer ready,
because a sharp student will ask:

> `create_agent` is the *concept* — the L10 model→tool→model loop, packaged into one line. But the
> LangChain object it returns hands you back raw messages, not a **`RunResult` with a `.trace`**.
> From L12 on, the mini-arc runs that same ReAct loop through `agent_graph.run`, which returns the
> traced `RunResult` that Sections 4 and 5 depend on. **Same loop; one produces an observable run.**
> It's the exact call L12 and L13 already used — one stable symbol, not a new agent.

Don't belabor it unless asked; the notebook states it in one line in Section 3.

## Pre-flight (before class)

The notebook is written to run **reproducibly offline** on a scripted `FakeModel` — a keyless
`Restart & Run All` passes top to bottom. Only **one** cell (Section 4's Langfuse push) is live, and
it soft-skips when the stack isn't configured. So a stack hiccup never strands the build. Still, do
this before class:

- **Sync + smoke-test the tool.** `uv sync` from the repo root, then
  `uv run pytest tests/lessons/L50/` — the new tool `find_matching_record` lives in the tested sibling
  [`receipt_tools.py`](receipt_tools.py) so you *write it live* in Section 2 without *debugging* it
  live. If imports fail in the notebook, the student's env isn't synced.
- **Restart & Run All once**, keyless, to confirm your machine reproduces it end to end (the buggy
  run trips `max_steps`; the scorers read `buggy → False / fixed → True`).
- **The live cell (optional but ideal).** To light up Section 4's Langfuse push, set
  `ANTHROPIC_API_KEY` + `LANGFUSE_HOST` / `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` (via the
  repo-root `.env`, read through `common/config.py`, **never hard-coded**). Dry-run **a trace write**
  before class and have the Langfuse project open on the projector — this is the same K06 stack you
  traced to in L12. The core walkthrough does **not** upload a dataset or run an experiment (that's
  the Section 5 student bonus), so no dataset/experiment dry-run is needed.
- **The failure is pre-scripted, not live-reproduced.** Section 4's runaway is a scripted `FakeModel`
  sequence on the malformed receipt, so "find a real failure" never depends on coaxing a
  non-deterministic bug out of a live model on the projector (the L12 "read the captured trace, don't
  re-run" discipline).

General gotchas:

- Everything imports from `fluffy_potato_curriculum.common` — `agent_graph` (`await arun` →
  `RunResult`), `evals` (`EvalCase` / `EvalResult` / `tool_calls` / `tool_trajectory`), `tools`
  (`calculator`), `fake_model`. The lesson-local imports are `check_expense_policy` (Section 2) and
  the stretch `check_reimbursement` (Section 6) from `receipt_tools.py`; `find_matching_record` is
  written inline in Section 2, not imported.
- The notebook is async-first: runs are `await arun(...)`. Jupyter allows top-level `await`; a plain
  `.py` port would need `asyncio.run`.
- A **scorer is keyword-only**: `def scorer(*, run, example) -> EvalResult`. Dropping the `*` is the
  most common signature slip (carried over from L13).

---

## Section 0 — Setup

**Time:** ~2 min. One cell: imports, the offline data bundle, two helpers (`receipt_text`,
`narrate`), and the `LIVE_LLM` / `LIVE_LANGFUSE` gates.

- The data bundle is located via the installed package (`fluffy_potato_curriculum.__file__`), **not**
  the notebook's cwd — so it loads no matter where Jupyter is launched. If it can't find `data/`, the
  package isn't installed (`uv sync`).
- Point out the print line: `live model: False | live Langfuse: False` offline is expected and fine.

## Section 1 — Scope the vertical slice (~10 min)

**Goal:** turn a one-line goal into a buildable spec — one task, one tool, a "done" line, and an
explicit non-goal list. Land **build the thinnest thing that exercises all five objectives, then
stop.**

- **What to say:** a capstone is a *vertical slice, not a product*. Naming the non-goals **is** the
  skill. Scope creep is *this exact lesson's* failure mode.
- **Apply the L08 test on screen:** could the model reconcile a receipt in its head? No — cross-format
  normalize-and-match is fiddly and deterministic, so the tool is warranted, so there's something
  real to trace and eval.
- **If the room pushes for a bigger scope:** write the bigger idea into the non-goal list as
  "v2 / your own project." It becomes the Section 6 hand-off, not today's build. Don't argue it down —
  park it.

## Section 2 — Design the one new tool (~15 min)

**Goal:** author `find_matching_record` live with the L07/L08 checklist — the *only* tool you write
today (the agent's other two, `calculator` and `check_expense_policy`, are reused/provided).

COMMON GOTCHAS:
- This is the one segment with real live-coding. Keep it moving: the normalization is an **alias
  table** (`merchant`/`company`/… → vendor) plus a text-parse branch for the folio. Don't gold-plate
  it — it handles exactly the bundle's formats.
- The **contract is graceful failure**: a malformed receipt returns `{"match": null, ...}`, it does
  **not** raise. That's the whole setup for Section 4 — narrate it as you write `_coerce_amount`
  returning `None` on `"amt": "??"`.
- Registering the tools is a dict `{"name": fn}` — the exact shape `agent_graph` binds and dispatches
  (mirrors `common.tools.TOOLS`). Two of the three come free: the reused `calculator` from
  `common/tools.py`, and `check_expense_policy` **imported pre-built from `receipt_tools.py`**.
- `check_expense_policy` is a **second core tool but not a second live-coding task** — it's provided,
  not authored. Frame it in one line: the policy is **free-form prose** (`data/expense_policy.md`), so
  instead of a cap lookup this tool does a **single LLM read** that interprets the prose and cites the
  rule — the lesson's one *LLM-in-the-loop* tool, warranted by the same L08 test (a model shouldn't
  recall *your* company's policy from memory). Offline it runs on a **scripted policy judge** so the
  walkthrough stays reproducible/keyless; the gated cell in Section 2 flips it to live Sonnet. The
  point is that the agent now makes a real three-way tool choice, not that students write it.

UNBLOCKERS:
- "The *authoring* budget is one tool. The agent runs three, but the only one you write is
  `find_matching_record` — if you're *writing* a second, that's your own project (Section 6)."
- If a student's inline copy drifts from the run, the tested reference is `receipt_tools.py` — the
  smoke-test cells (`R-coffee … R-mystery`, and the meals/lodging policy check) are the fast check.

**If it misbehaves:** if a live model later never calls the tool, that's a live L08 moment — tighten
the name/description and rerun; don't paper over it.

## Section 3 — Assemble the shallow agent (~10 min)

**Goal:** wire the three tools (`find_matching_record` + `calculator` + `check_expense_policy`) into
`agent_graph.arun` and run the happy path; read the `RunResult`; confirm `natural` termination.

- **What to say:** *this is the same model→tool→model loop you hand-rolled in L10* — you're just not
  typing the loop. It's now doing work *you* scoped. See the framing note above for the
  `create_agent` question.
- **`max_steps` is a design choice, not a default.** Reconciling one receipt is a few tool
  calls (match → total → policy), so a low cap is a cheap runaway guard — which is exactly what
  Section 4 exploits.
- **The `FakeModel` is the point, not a limitation:** it scripts the *decisions* so the run is
  reproducible, but the *tools really run* and the *trace is real*. Say this out loud or students
  think the whole thing is faked.

## Section 4 — Trace it and find a real failure (~15 min)

**Goal:** read the buggy run's trace, name the failure in L12 vocabulary, then (optionally) push a
live run to Langfuse.

COMMON GOTCHAS:
- The runaway signature is **two** things in the trace: the *same `(name, args)` pair repeats* **and**
  the run ends on `termination == "max_steps"` (never `natural`). And the tool returned `"match":
  null` *every time* — the agent had the answer on turn one and ignored it.
- **Read the trace, don't theorize.** Use `narrate(buggy)` and point at the repetition. This is L12's
  "read the captured trace, don't re-run a non-deterministic bug."
- **The live cell needs BOTH keys** (`ANTHROPIC_API_KEY` *and* the three Langfuse vars). With either
  unset it prints the skip note and you stay on the FakeModel trace — expected, not a bug.

UNBLOCKERS:
- "Now the failure is *yours* — the course didn't plant it. Spotting it in your own trace is the
  capstone version of L12."

**If it misbehaves:** if Langfuse is down mid-segment, read the returned `RunResult.trace` inline
(`narrate`) and move on — the finding is identical; the dashboard just renders it. Reconnect and
re-push after if you like.

## Section 5 — Turn the failure into one eval case (~10 min)

**Goal:** convert the Section 4 runaway into **one regression case** — a scorer that *fails when the
bug is present and passes when it's fixed* — and run it once (buggy → False, fixed → True). Pure
Python; **no Langfuse write in the core.**

COMMON GOTCHAS:
- A regression case is *defined* by failing on the broken run. If the scorer passes against `buggy`,
  it's catching nothing — tighten it live.
- The trajectory scorer needs hashable calls: `tuple(sorted(args.items()))` (dicts aren't hashable).
  Same snag as L13 Problem 3 — that `TypeError` is the teaching moment if it comes up.
- **Stop at one case, one scorer, one run.** Do **not** drift into uploading a dataset or launching an
  experiment on the projector — that's the bonus. The point to land is the *habit* (a failure becomes
  a kept case), not the platform.

UNBLOCKERS:
- "A good eval case comes from a real failure, not imagination — you just watched yours happen in the
  trace. That's why L12 came before L13, and both before this capstone."
- The line to land: **the slice isn't done when it runs — it's done when it's traced and has one case
  that would catch its regression.**

**Student bonus (do NOT demo):** take the case to the platform on their own agent — add an outcome
*and* trajectory score, `upload_dataset` as a Langfuse Dataset, run an Experiment with K samples for a
pass *rate*, and re-run against **Haiku 4.5** for a Sonnet-vs-Haiku comparison. They learned this
machinery in L13; here it's the "try it yourself" on-ramp to the end-of-week project.

## Section 6 — Reflect and hand off (~10 min)

**Goal:** narrate the finished artifact as one story and point every student at their own build.

- Scroll top to bottom — *goal → tool → agent → trace → eval* — and name, on this concrete agent,
  where each of the five objectives showed up (the notebook lists them).
- The **stretch tool** `check_reimbursement` is imported here (from `receipt_tools.py`) as the concrete
  "first thing you'd add next" — a *second* tool, deliberately kept out of the core slice. Run it only
  if the room is ahead of the clock; otherwise just name it. It seams into the end-of-week project.
- **Point at [`MINI_WRAPUP.md`](../MINI_WRAPUP.md)** as the next read — the course-level retrospective
  L50 deliberately does not try to be.
- **If short on time:** this segment compresses to two minutes of scrolling-and-naming without losing
  its point.

---

## Pacing (≈70 min of content inside a 90-min ceiling)

| Segment | Beat | Time |
| --- | --- | --- |
| 1 | Scope the slice | ~10 |
| 2 | Write the one tool (live) | ~15 |
| 3 | Assemble with `agent_graph.run` | ~10 |
| 4 | Trace + find the failure | ~15 |
| 5 | One eval case (minimal) | ~10 |
| 6 | Reflect + hand off | ~10 |

**Out of the base budget (always left to students / only if ahead):** the Langfuse
Dataset/Experiment/pass-rate work and the Haiku A/B (Section 5 bonus), and running the
`check_reimbursement` stretch tool (Section 6). If you somehow overrun, the clean split point is the
**Section 3/4 boundary** ("scope → tool → agent" | "trace → eval → hand-off") — but at ~70 minutes
the whole slice is meant to land in one session.

**Format reminder:** resist turning this into "everyone invent your own agent now." That divergence is
the [end-of-week project](../../../../docs/origin/PROJECT_BRIEF_DESIGN.md); doing it here overruns the
clock and fragments the room. Everyone builds the *same* agent, guided.
