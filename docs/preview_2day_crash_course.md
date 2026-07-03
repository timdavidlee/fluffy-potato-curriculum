# 2-Day Preview / Crash Course — draft plan

> **Status: draft / WIP.** A planning sketch to revisit later, not a committed track.
> Not wired into [tracks.toml](../src/fluffy_potato_curriculum/lessons/tracks.toml) or
> [SYLLABUS.md](../src/fluffy_potato_curriculum/lessons/SYLLABUS.md).

## Goal & constraints

- **Format:** 2 days × 5 slots × 1.5 hr = **10 slots / 15 hrs total.** Each slot is
  either all-lecture or lecture + lab.
- **Purpose:** a *preview*, not mastery — optimize for the through-line and the
  "aha" moments, not depth.

## Why this is a downselect *and* a condense

The **mini track is 11 lessons at ~26 hrs** (L01, L02, L04, L05, L07, L08, L09, L11,
L12, L20, L21). This preview has **15 hrs**, so the mini cut does not fit as-is — every
kept lesson is trimmed (~60% of its natural length) and two pairs are merged. See the
mini rationale in [CURRICULUM_PRD.md](origin/CURRICULUM_PRD.md) ("Condensed Mini Lesson
Plan").

## Narrative spine

Reordered from the mini so **structured workflows come right after prompting** (they
depend only on L01/L02 — prompt-chaining + routing, no tools or agent loop). This gives
the two days a clean contrast:

- **Day 1 — *you* wire the flow** (deterministic workflows)
- **Day 2 — the *model* drives the flow** (agents), then measure & extend

The "workflow vs. agent" contrast from L11's objectives now spans both days instead of
living in one slot: Day 1 you build the workflow, Day 2 you build the agent and compare.

## The 10-slot plan

| Slot | Lesson(s) | Format | The "aha" |
|---|---|---|---|
| **Day 1 — you wire the flow** | | | |
| 1 | L01 LLM & token basics | Lecture + short lab | It's just tokens & probabilities |
| 2 | L02 Prompting fundamentals | Lecture + lab | Structure changes output |
| 3 | L11a — prompt-chaining: multi-step task as a graph (sequential nodes + shared state) | Lecture + lab | Chain prompts into a pipeline |
| 4 | L11b — routing: branch on a classification or user input | Lecture + lab | **You wired a deterministic LLM workflow** |
| 5 | L08 Tracing — see what each node did | Lecture + lab | Look inside the flow you built |
| **Day 2 — the model drives** | | | |
| 6 | L04 Tool calling: how it works (CoT + **thinking / answer** message split, L03 folded in) | Lecture + lab | The model asks *you* to run code — and *deciding* to is a reasoning step |
| 7 | L05 Designing good tools (when a tool beats the model) | Lecture + lab | *When* to reach for a tool |
| 8 | **L07 + L12 merged** — hand-rolled agent loop, then the same in LangGraph (+ **narration** messages between steps) | Lecture + lab | Now the *model* drives — contrast Day 1 |
| 9 | L09 Evaluation: first pass | Lecture + lab | Is the workflow/agent actually good? |
| 10 | **L20 + L21 merged** — Skills + composition + wrap-up | Lecture (+ mini-lab) | Just-in-time capabilities, composed |

**Coverage:** all mini objectives survive — tool design (L04/L05), when-to-use (L05),
shallow LangGraph agent (L12), eval (L09), tracing (L08) — plus workflows (L11) and
skills (L20/L21).

**Condensations:** merge **L07+L12** (agent hand-rolled → framework) and **L20+L21**
(skills → composition/wrap); L11 gets two slots to breathe.

**CoT placement:** chain-of-thought (L03) is folded into **Day 2 / slot 6 (tool calling)**,
not the Day-1 prompting slot. Rationale: L04's objectives already frame *"the decision to
call a tool is itself a reasoning step,"* so CoT lands where it's immediately used (reason →
act) and then reinforces through the ReAct loop in slot 8. Day 1's workflow nodes stay
plain prompts — they don't need CoT to make the point.

**Assistant message types (Day 2 thread):** teach the three kinds of assistant output as
a running thread, not a standalone topic:
- **Thinking** and **answer** messages — L03's `<thinking>`/`<answer>` scratchpad contract
  (separate reasoning from the final, user-facing answer). Introduced at **slot 6** with
  the CoT fold-in; parsing them out reuses L02's structured-output discipline.
- **Narration** messages — the agent's interstitial "here's what I'm doing" text emitted
  *between* reasoning and tool calls. Only meaningful once a multi-step loop exists, so it
  lands at **slot 8** (agent loop) and is exactly what makes the slot-5/8 **trace** readable.
Framing to land: thinking / narration / answer are three *channels* of assistant output —
one for the model's private reasoning, one for running commentary, one for the final
result — and good agent UX decides which to surface vs. hide.

## Caveats / content surgery needed

- **L08 tracing moved to Day 1 (slot 5).** Its built lab traces the **L07 agent** (it
  was generated in mini order L07 → L08 → L09). To use it on Day 1 it must be adapted to
  **trace the L11 workflow** instead. Upside: a deterministic workflow produces a cleaner,
  more legible trace than a looping agent — arguably a *better* first exposure.
- **L11 before tools/agent** — fine as-is; prompt-chaining is self-contained.
- **L21 is roadmap-only (not built).** Built on disk: L01–L09, L11, L12, L20. Slot 10
  leans on L20 + [MINI_WRAPUP.md](../src/fluffy_potato_curriculum/lessons/MINI_WRAPUP.md)
  unless L21 is generated first.
- **Labs are the first thing to cut for time.** Budget ~50 min lecture / ~40 min lab per
  slot; expect to convert some `_empty` labs into guided walk-throughs of `_solutions`.

## Note: evaluating the Day-2 free-form agent (slot 9)

Slot 9 is where the workflow↔agent contrast pays off in eval terms. A Day-1 workflow is
deterministic (tight outcome checks work); the Day-2 agent is free-form (model-driven,
non-deterministic), so eval must loosen up — score **outcome + trajectory + operational**
surfaces, use **pass rate** over K samples instead of pass/fail, harvest cases from traced
failures, and forward-point to LLM-as-judge / human review for the un-assertable parts.
The difficulty of evaluating the free-form thing is itself the lesson. (See
[L09 objectives.md](origin/lesson_roadmaps/L09/objectives.md).) Note: the built L09 lab
targets the hand-rolled loop's `RunResult`/trace, which is what you'd demo.

## Open decisions for later

- Coverage (this plan — whole mini spine, condensed) vs. depth (drop the LangGraph/Skills
  tail, ~7 lessons near full depth). This draft chooses coverage.
- Whether to generate L21 materials or run slot 10 as a lighter lecture + wrap-up.
- Whether to formalize this as a `preview` track in `tracks.toml` + a per-slot schedule
  doc with timings and keep/cut lab cells.
