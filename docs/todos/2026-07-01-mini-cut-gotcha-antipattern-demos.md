# 2026-07-01 — Gotcha + anti-pattern demos across the mini cut

**Status: STAGE-1 DONE (2026-07-04).** All 10 in-scope roadmap `demos_or_activities.md` beats landed on branch `worktree-gotcha-antipattern-demos` (L23 was already the template). Each gotcha/anti-pattern beat now lives in the lesson's **roadmap**; carrying them into **stage-2 student materials** happens when each lesson's materials are (re)generated — not part of this pass.

A cross-cutting initiative: every **mini-cut** lesson should teach its **failure modes** (gotchas +
anti-patterns), not just the happy path. Right now this is uneven — [L23](../origin/lesson_roadmaps/L23/demos_or_activities.md)
has a dedicated anti-pattern demo (Demo 5: over-chaining · shared-skill-that's-really-a-tool ·
description collisions), but most earlier lessons don't call their gotchas out explicitly.

**Goal:** each mini lesson's `demos_or_activities.md` (and, in stage 2, its materials) gains a short
**"gotchas / anti-patterns" beat** — a teacher-led demo of the wrong way + the fix. Use **L23 Demo 5 as
the template**: name the anti-pattern, *show* it failing (live where possible), state the cure, tie it
back to the lesson's payoff.

- **Scope:** the 11 mini-cut lessons only (see [SYLLABUS.md](../../src/fluffy_potato_curriculum/lessons/SYLLABUS.md) — mini column). Full-course-only lessons are out of scope for this pass.
- **Not-yet-authored roadmaps:** several mini lessons don't have `demos_or_activities.md` yet (L11/L12/L04/L14 per the [2026-06-09 tracker](2026-06-09-prd-curriculum.md)); for those, bake the gotcha beat in when the demos doc is first authored rather than retrofitting.
- **Candidate gotchas below are a starting list**, not final — the delegated session should refine against each lesson's actual objectives.

---

## Per-lesson checklist (mini cut, teaching order)

> **⚠️ Numbering reconciliation (added 2026-07-04).** This checklist predates the 2026-07-04
> lesson reorder, so three agent-arc rows below carry **stale lesson numbers**. Map by *topic*,
> not by the printed `L<NN>`, before editing files:
> - "**L11 — Tracing**" → now **L12** ("What an agent generates: state, logs, traces & extracts").
> - "**L12 — Evaluation**" → now **L13** ("Evaluation: first pass").
> - "**L14 — Shallow LangGraph agent**" → now **L11** ("Shallow agents in LangGraph").
>
> Also: the *"bake in when the demos doc is authored"* notes are now moot — **every** targeted
> lesson's `demos_or_activities.md` already exists (L04/L11/L12/L13 included), so all are
> retrofit targets. Current-number scope for this pass (L23 done): **L01, L02, L04, L07, L08,
> L10, L11, L12, L13, L22** (10 lessons). L03/L05/L06/L50 are mini lessons *not* in the original
> checklist scope — flagged, not yet included.

- [x] **L01 — LLM & token basics.** ✅ **Done (2026-07-04)** — added a "Common pitfalls coda"
      naming the four gotchas (word ≠ token · temperature-as-randomness-knob · cost-ignores-output ·
      silent overflow/truncation). Coda (not a new demo): L01 already *shows* each inside the demo
      chain (Demos 2/3, 3.6, 5), so the beat **names** them + states the cure. Gotchas: word ≠ token
      (whitespace/punctuation/emoji/non-English cost more); silent **context-window overflow /
      truncation**; cost estimates that ignore **output** tokens; "temperature = randomness knob"
      oversimplifications.
- [x] **L02 — Prompting fundamentals.** ✅ **Done (2026-07-04)** — coda naming 4 (wrong role · trusting
      structured output · few-shot leak/bias · bloated system prompt). Anti-patterns: instructions in the
      **wrong role** (user vs system); trusting structured output **without defensive parsing/validation**
      (callback to L0206 fixtures); few-shot examples that **leak format or bias** the answer; bloated
      always-on system prompts.
- [x] **L07 — Tool calling.** ✅ **Done (2026-07-04)** — coda naming 4. Gotchas: forgetting the **schema is
      in every request** (tokens twice over); model **hallucinating/omitting args**; mishandling the
      tool-call **round-trip**; assuming the model *always* calls the tool when it should.
- [x] **L08 — Designing good tools.** ✅ **Done (2026-07-04)** — **full Demo 5** ("the four tool-design
      anti-patterns, named") with a genuinely new live **tool-soup** beat; the other three named from
      Demos 1–4. Anti-patterns: **over-tooling** (a tool for what the model can do alone); vague tool
      **name/description**; **unhandled tool errors**; one tool doing too much (no clean schema).
- [x] **L10 — Hand-rolled agent loop.** ✅ **Done (2026-07-04)** — coda naming 3 (infinite-loop stays
      shown-with-a-cap, never hung). Gotchas: **no termination condition** (infinite loop) / no
      max-iterations guard; **not handling tool failures**; **unbounded context growth** across turns.
- [x] **L11 → now L12 — Tracing.** ✅ **Done (2026-07-04)** on **L12** (the current tracing lesson) — coda
      naming 4; "reading spans out of order" reframed to the taught version ("reading the summary, not the
      trace"). Anti-patterns: tracing **too little** (can't locate the failure) vs **too much** (noise,
      prompt bodies, PII); **not instrumenting tool calls**; reading spans out of order.
- [x] **L12 → now L13 — Evaluation.** ✅ **Done (2026-07-04)** on **L13** — coda naming 5; the "L11 traces"
      cross-ref corrected to **L12 traces**. Anti-patterns: eval set that only tests the **happy path**;
      **sample too small**; **over-trusting LLM-as-judge**; not targeting **failure modes seen in L12
      traces**; regressions that slip through.
- [x] **L04 — Explicit graphs & workflows (DAGs).** ✅ **Done (2026-07-04)** — coda naming 4. Gotchas: using
      a **workflow where an agent is needed** (or vice versa); **model-driven looping** sneaking into a
      "deterministic" DAG; **wrong model per node** (overpaying); brittle branch conditions.
- [x] **L14 → now L11 — Shallow LangGraph agent.** ✅ **Done (2026-07-04)** on **L11** — coda naming 3.
      **Note:** the reducer/typing **state-mismanagement** gotcha this row listed assumed a *hand-assembled*
      `StateGraph`; that moved to **L15**, so L11's coda keeps only the `create_agent`-first shallow-agent
      gotchas (termination-still-applies · black-box-debugging · one-liner-vs-hand-built ceiling).
- [x] **L22 — Skills.** ✅ **Done (2026-07-04)** — coda naming 4 (two description faults + two
      wrong-container faults), promoting Demo 4 step 4's scattered mentions to a first-class beat + handoff
      to L23 Demo 5. Anti-patterns: description **too vague** (never triggers) or **too broad** (always
      triggers); a **skill that should be a tool** or **system-prompt content**; cramming occasionally-needed
      instructions into the system prompt.
- [x] **L23 — Skill patterns & composition.** ✅ **Already done** — Demo 5 (over-chaining ·
      shared-skill-that's-really-a-tool · description collisions). This is the **template** for the others.

---

## Approach notes for the delegated session

- **Template = L23 Demo 5's block shape:** Goal → Pre-flight → Live script (show it break) → What to
  highlight (name it + the cure) → If the demo misbehaves.
- **Prefer showing the failure live** where the mechanism is model-driven (selection, tool-calling,
  routing); use a **drawn/prepared** example where live failure is unreliable or destructive (e.g. L10
  infinite loop — cap iterations, don't actually hang the room).
- **Reuse the running examples** (`common/tools.py`: `calculator`/`lookup`/`flaky_fetch`; the L14 agent)
  so gotchas land on code students already know.
- **Cross-reference forward/back** — many gotchas are another lesson's main point (L01 context overflow →
  L19 context mgmt, full course; L07 token cost → L22/L23 JIT). Name the link; don't re-teach.
- Decide whether each gotcha beat is its **own demo** or a **"common pitfalls" coda** to an existing demo —
  likely per-lesson judgment (a full anti-pattern demo for L08/L22/L23; a shorter coda for L01/L11).
