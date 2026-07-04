# L50: Agent mini-project — end-to-end walkthrough (mini-track capstone)

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (lesson-plan note below the master table + the "Condensed Mini Lesson Plan" row).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).
> Position: **the last taught unit of the mini cut.** In mini teaching order the preceding lesson is [L23 Skill patterns & composition](../L23/objectives.md); there is no following lesson. L50 is numbered out at 50 on purpose — parked at the end with a gap (L26–L49) so future lessons can slot *before* it without renumbering (the same "park it out of the way" move the `K` prework uses). It is registered on the **mini track only, for now** (a deliberate, flagged exception to the otherwise-invariant mini ⊆ full — see the `<!-- *NEED INPUT* -->` in the PRD on whether to promote it to `full`).
>
> **This is not a standard proctor-led lecture+lab lesson.** L50 is a hands-on, end-to-end **walkthrough**: the proctor builds one small ("mini") tool-calling agent from a blank file to a traced, evaluated, working artifact, narrating each decision, while students follow along and rebuild it. It teaches **no new concept** — its whole job is to *assemble* the mini-cut's five-objective arc into one continuous build. The course's overall closing/retrospective framing is owned by [`MINI_WRAPUP.md`](../../../../src/fluffy_potato_curriculum/lessons/MINI_WRAPUP.md) (read *after* L50), not by this lesson.

## Where this lesson sits

By the time students reach L50 they have built every piece of a shallow tool-calling agent, but always **one piece at a time, on a tool/task the course handed them** (the shared `calculator` / `lookup` / `flaky_fetch` in [`common/tools.py`](../../../../src/fluffy_potato_curriculum/common/CLAUDE.md)). They have:

- designed and bound a tool and traced one tool round-trip ([L07](../L07/objectives.md)) and reasoned about *when a tool is warranted vs. model-alone* and how to name/schema/error-handle it ([L08](../L08/objectives.md));
- hand-rolled the model → tool → model loop ([L10](../L10/objectives.md), `agent_loop.run(...)` → `RunResult`) and then re-expressed it as the one-line **`create_agent`** shallow agent ([L11](../L11/objectives.md));
- instrumented that agent to emit a structured **`TraceEvent`** trace and read it in the cohort's self-hosted **Langfuse** ([L12](../L12/objectives.md));
- built a first-pass **eval set** — `EvalCase` / `Scorer` / `EvalResult`, uploaded as a Langfuse **Dataset** and run as an **Experiment** ([L13](../L13/objectives.md));
- and, on the skills thread, composed capabilities into a small system ([L22](../L22/objectives.md)/[L23](../L23/objectives.md)).

What they have **never** done is drive the whole arc themselves, in order, on a task that is *theirs* — decide what the agent is for, design its tool, wire the shallow agent, trace it, find a failure in the trace, and turn that failure into an eval case — as one connected motion. L50 is that motion. It is the difference between *"I can do each step when told to"* and *"I can take a blank file and a fuzzy goal and produce a traced, evaluated shallow agent."*

The lesson is deliberately **integrative, not additive**: every primitive it uses already exists in the shared [`common/`](../../../../src/fluffy_potato_curriculum/common/CLAUDE.md) layer, and the walkthrough **reuses it rather than re-deriving it** — `create_agent` for the loop (L11), `TraceEvent` + the Langfuse bridge for observability (L12), and `EvalCase`/`Scorer` + `upload_dataset`/`emit_score` for evaluation (L13). The *only* genuinely new authoring is the **one small domain tool** the mini-project needs, so students see the L07/L08 design step happen once more, fresh, on a task the course did not pre-build for them.

**Relationship to the end-of-week project (keep the lane clear).** L50 is a **proctor-led walkthrough** — everyone builds *the same* small agent together, guided. It is the worked example that primes, but is **not**, the student-driven [end-of-week project](../../PROJECT_BRIEF_DESIGN.md) (an open-ended 12–16 hr team hackathon in `projects/`). L50's value is exactly that it de-risks the project: after watching one agent go blank-file-to-evaluated, a team knows the shape of the thing they are about to build alone. <!-- *NEED INPUT*: confirm L50 is positioned as the on-ramp to (not a replacement for) the end-of-week project — the walkthrough is the shared worked example; the project is the independent build. If the mini track ships without the end-of-week project, L50 becomes the sole integrative build and its "hand off to your own project" beat should be rewritten as a standalone extension exercise. -->

## Prerequisites

L50 assumes **all five mini-cut agent-arc objectives are already fluent** — it is a capstone, so every prerequisite is "you built this earlier and we now use it without re-teaching":

- **Design a tool**: write a plain-Python function, give it a clear name + schema + docstring, decide *when* a tool is warranted vs. model-alone, and handle its errors ([L07](../L07/objectives.md), [L08](../L08/objectives.md)). L50's new domain tool is authored with exactly this checklist — recalled in one line, not re-taught.
- **Stand up a shallow agent**: `from langchain.agents import create_agent`, bind tools, run it, read a `RunResult` (final text, iterations, termination), and reason about termination as a design choice ([L11](../L11/objectives.md), building on the [L10](../L10/objectives.md) loop).
- **Trace and read it**: emit a `TraceEvent` trace, send it to the cohort's **Langfuse** instance, and locate a failure from the trace alone — tool error, wrong arguments, runaway loop, premature termination ([L12](../L12/objectives.md)).
- **Evaluate it**: build a minimal eval set (`EvalCase` / `Scorer` / `EvalResult`), upload it as a Langfuse **Dataset**, run an **Experiment**, and read a pass rate / regression across two runs ([L13](../L13/objectives.md)).
- **Config + environment**: keys through the [`common/config.py`](../../../../src/fluffy_potato_curriculum/common/CLAUDE.md) seam and a live, healthy Langfuse from the [K06 Docker stack](../K06/objectives.md) — L50 makes **live** model calls and **live** Langfuse writes, so the K02 keys gate and K06 stack gate are hard prerequisites here, exactly as in L12/L13.

If a student is shaky on any single step, the fix is to revisit *that* lesson's lab — L50 does not slow down to re-teach a primitive; it moves at the speed of assembly. A student who can't yet produce a trace *and see it in Langfuse* should be redirected to L12 first (same redirect L13 makes).

## Learning objectives

By the end of L50, a student should be able to:

1. **Scope a small agent from a fuzzy goal to a buildable spec — the "vertical slice."** Concretely:
   - Turn a one-line goal ("an agent that helps with X") into a **minimal end-to-end slice**: one clear task, the *one* tool it needs, a definition of "done," and an explicit non-goal list (what this mini-agent deliberately will *not* do). Land the capstone habit: **build the thinnest thing that exercises all five objectives, then stop** — a mini-project is a vertical slice, not a product.
   - Apply the L08 *when-is-a-tool-warranted* test to the chosen task: does it need a tool at all, or is this model-alone? Choosing a task whose single tool is genuinely justified is part of the scoping skill.
   - Recognize scoping failure modes: too big to finish (no vertical slice), or too trivial to need a tool (nothing to trace or eval).

2. **Design and build the one new tool the mini-project needs, reusing the L07/L08 checklist.** Concretely:
   - Author a single, small, deterministic domain tool (plain function + clear name + typed schema + docstring + error handling), the way [L08](../L08/objectives.md) prescribes, and register it alongside the shared [`common/tools.py`](../../../../src/fluffy_potato_curriculum/common/CLAUDE.md) tools rather than re-inventing tool plumbing.
   - Decide deliberately what stays a tool vs. what the model handles in prose — the L08 line, applied once more on a fresh task.
   - Keep the tool *offline/deterministic where possible* so the agent stays cheap to run and its eval stays reproducible (the `common/` design stance).

3. **Assemble the shallow agent with `create_agent` and run it end-to-end.** Concretely:
   - Wire the new tool (plus any reused shared tools) into a **`create_agent`** shallow agent — the [L11](../L11/objectives.md) one-liner — and run it on the mini-project task, reading the `RunResult` and confirming natural termination.
   - Reason about the step cap / termination for *this* task, not in the abstract — pick a `max_steps` that fits the slice and explain the choice.
   - Land the capstone framing: this is the same model → tool → model loop from L10, now doing a job the student defined.

4. **Instrument the mini-agent and read its trace in Langfuse to find a real failure.** Concretely:
   - Emit a **`TraceEvent`** trace and push the run to the cohort's Langfuse instance (the [L12](../L12/objectives.md) bridge), then read the trace to narrate what the agent actually did — model calls, tool calls with arguments, tool results, termination.
   - Deliberately provoke or surface **one failure** on the student's own task (a bad tool argument, an unhandled tool error, a runaway loop) and **locate it from the trace alone** — the L12 skill, now on an agent the student built, where the failure is not one the course pre-planted.

5. **Turn that observed failure into an eval case and run a Langfuse experiment.** Concretely:
   - Convert the failure found in objective 4 into a **regression case** — an `EvalCase` plus a `Scorer` that *fails* when the bug is present and *passes* when fixed — following the L13 loop **trace a failure → add a dataset item that catches it → keep the case forever**.
   - Add at least one **outcome** score (reads `final_text`) and one **trajectory** score (reads the trace), upload the small set as a Langfuse **Dataset** via `upload_dataset`, and run it as an **Experiment**; read the pass rate.
   - Optionally run the experiment on the anchor model **and** the cheap contrast model (Sonnet 4.6 vs. Haiku 4.5) and read the pass-rate delta in Langfuse's run comparison — the L13 A/B, now on the student's own agent.

6. **Reflect on the whole slice and hand off to independent work.** Concretely:
   - Narrate the finished artifact as one connected story — *goal → tool → agent → trace → eval* — and name, for their own agent, where each of the five mini-cut objectives shows up. This is the "you built the real thing" moment L50 exists to produce.
   - Identify the **first thing they would add next** (a second tool, a harder task, a tighter scorer) and recognize it as the seam between this guided walkthrough and the independent [end-of-week project](../../PROJECT_BRIEF_DESIGN.md) — so students leave L50 pointed at their own build, then read [`MINI_WRAPUP.md`](../../../../src/fluffy_potato_curriculum/lessons/MINI_WRAPUP.md) for the course-level retrospective.

## Vocabulary the walkthrough must establish

L50 introduces almost no new terms — it **reuses** the vocabulary of L07/L08 (tool, schema, tool-vs-model), L10/L11 (the loop, shallow agent, `create_agent`, `RunResult`, termination), L12 (`TraceEvent`, trace, Langfuse, failure signature), and L13 (eval set, `EvalCase`, `Scorer`, `EvalResult`, Dataset, Experiment, score, regression, pass rate, outcome vs. trajectory). Assume all of these; do not redefine them. The handful of terms L50 *does* own:

- **Mini-project** — the smallest agent that still exercises all five mini-cut objectives end to end: one task, one new tool, a running shallow agent, a trace, and an eval case. The unit L50 builds.
- **Vertical slice** — a build that goes *all the way through* the stack on a *narrow* task (one path from goal to evaluated agent), rather than a broad feature that only reaches partway. The capstone's design discipline: thin and complete beats wide and half-wired.
- **Capstone walkthrough** — the teacher-led, everyone-builds-the-same-thing format of this lesson (contrast with the student-driven end-of-week project). A guided assembly of prior skills, not a new concept.

## Main points the walkthrough should land

- **Nothing here is new — that's the point.** L50 is the arc you already built, run once as a single motion. If a step feels unfamiliar, the fix is the lesson that owns it, not L50.
- **Build the thinnest thing that touches all five objectives, then stop.** A mini-project is a vertical slice: one task, one tool, one trace, one eval case. Scope creep is the capstone's main failure mode.
- **The only fresh authoring is one small tool.** Everything else — the loop, tracing, eval — is imported from `common/`. Reuse over re-derive is the whole design stance of the shared layer, made visible.
- **You find your *own* failure now.** In L12/L13 the course handed you failure modes to catch. Here the failure is on your task, in your trace — spotting it and turning it into a kept eval case is the capstone skill.
- **A traced, evaluated agent is the deliverable — not just an agent that "worked once."** The habit the mini course has been building (trace before you guess; eval or it's vibes) is what makes this a *finished* slice rather than a demo that happened to pass.
- **This primes your own project.** The walkthrough is the shared worked example; the independent build (the end-of-week project) is next. Leaving L50, you should know the *shape* of the thing you're about to build alone.

## Common student confusions to watch for

- *"A capstone should be big / impressive."* No — the capstone skill is *finishing a thin slice*. A tiny agent that is scoped, built, traced, and evaluated end-to-end beats an ambitious one that never gets past "it ran."
- *"I need to write a lot of new code."* Almost none — the loop, tracing, and eval are all in `common/`. If you're re-implementing the agent loop or a trace emitter, stop and import it.
- *"Every task needs a tool."* Apply the L08 test — some tasks are model-alone. Pick a mini-project whose one tool is genuinely warranted, or there's nothing to trace and eval.
- *"It passed once, so I'm done."* One green run of a non-deterministic agent proves little (L13). The slice is done when it's traced *and* has at least one eval case that would catch its regression.
- *"The trace and the eval are extra polish."* They are the deliverable. An agent with no trace and no eval is exactly the pre-L12 vibes-based agent the mini course spent two lessons teaching you to leave behind.
- *"This is my end-of-week project."* It's the guided warm-up for it. Everyone builds the same agent here; you build your own next.

## Bridge / capstone

L50 **is** the mini cut's integrative capstone — the lesson where the five objectives stop being separate skills and become one build. It does not bridge *forward* to another lesson (there is none in the mini cut); its two hand-offs are:

- **To the student's own work** — the [end-of-week project](../../PROJECT_BRIEF_DESIGN.md): L50 is the shared worked example that makes the independent team build tractable. The last walkthrough beat (objective 6) is deliberately a pointer at "the first thing you'd add," which is where the project begins.
- **To the course retrospective** — [`MINI_WRAPUP.md`](../../../../src/fluffy_potato_curriculum/lessons/MINI_WRAPUP.md), read immediately after L50, which owns the "here's the whole system you built, here's where to go next" framing at the course level (no lesson roadmap does).

<!-- *NEED INPUT*: if L50 is later promoted into the `full` track, add a forward bridge here to the full course's continuation (deep agents / RAG / multi-agent / eval-at-scale), positioning the mini-project as the shallow-agent baseline those lessons extend. Left out now because L50 is mini-only. -->

## Open authoring questions

- <!-- *NEED INPUT (format)*: L50 is a WALKTHROUGH, not the standard proctor-led lecture+lab. Stage 2's format guides ([LECTURES.md](../../LECTURES.md), [LAB_DESIGN.md](../../LAB_DESIGN.md)) assume a lecture + paired `_empty`/`_solutions` lab. Recommendation: realize L50 as a SINGLE guided build notebook (proctor drives; students rebuild cell-by-cell) plus PROCTOR_NOTES, closer in spirit to the K-prework "runbook" shape than to a lecture+lab pair — the demos_or_activities.md sibling is the primary artifact, and there is no separate student-invented lab. Confirm this format before stage 2 runs, since it deviates from the default material set. -->
- <!-- *NEED INPUT (the concrete mini-project)*: the walkthrough needs ONE small, self-contained domain to build against. Opinionated default: a "receipt / expense line-item helper" — one deterministic tool (parse-and-total a small line-item list, or normalize a currency/unit), a task the model can't reliably do in its head (so the tool is warranted), and a natural failure to catch (malformed input → tool error, or a runaway when the model retries). Alternatives considered: a units/measurement converter, a tiny FAQ-lookup-plus-calc helper. Pick one deterministic, offline-friendly domain so the eval stays reproducible; confirm the choice before stage 2 authors the tool. -->
- **Anchor model + contrast:** Claude **Sonnet 4.6** is the anchor (inherits the L01–L13 precedent), with **Haiku 4.5** as the cheap contrast for the optional objective-5 A/B experiment — same stance as [L13](../L13/objectives.md). Pin the walkthrough's live calls to Sonnet 4.6; keep them small and few (low `max_tokens`, a handful of calls) per the notebook cost rules.
- **Live-call posture:** like L12/L13, L50 makes **live** model calls and **live** Langfuse writes — restart-and-run-all assumes keys (via `common/config.py`) and a healthy Langfuse. It is *not* a keyless/offline notebook. State this in PROCTOR_NOTES and pre-flight. <!-- *NEED INPUT*: whether a `FakeModel`-backed offline fallback path is worth providing for a student without a live key on the day, or whether L50 (like L13) simply hard-requires the live stack. Recommendation: hard-require the live stack (consistent with L13); the whole point is a real traced/evaluated run. -->
- <!-- *NEED INPUT (duration)*: best guess ~90–120 minutes for the full walkthrough — ~15 scope, ~20 tool, ~15 assemble the agent, ~20 trace + find a failure, ~30 eval case + experiment, ~10 reflect/hand-off. Could split into "scope → tool → agent" and "trace → eval → hand-off" if it runs long. Confirm against demos_or_activities.md once that sibling is drafted. -->
- <!-- *NEED INPUT (reuse vs. fresh domain)*: should the walkthrough reuse an existing `common/tools.py` tool as the second (already-built) tool so the agent has more than one to choose between (making the trace more interesting), or stay strictly single-tool for simplicity? Recommendation: one NEW domain tool + one REUSED shared tool (e.g. `calculator`), so the model has a real tool-selection decision to trace — but keep the new authoring to exactly one tool. -->
