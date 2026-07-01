# 2026-07-01 — Gotcha + anti-pattern demos across the mini cut

**Status: DELEGATED — handle in a separate session.**

A cross-cutting initiative: every **mini-cut** lesson should teach its **failure modes** (gotchas +
anti-patterns), not just the happy path. Right now this is uneven — [L21](../origin/lesson_roadmaps/L21/demos_or_activities.md)
has a dedicated anti-pattern demo (Demo 5: over-chaining · shared-skill-that's-really-a-tool ·
description collisions), but most earlier lessons don't call their gotchas out explicitly.

**Goal:** each mini lesson's `demos_or_activities.md` (and, in stage 2, its materials) gains a short
**"gotchas / anti-patterns" beat** — a teacher-led demo of the wrong way + the fix. Use **L21 Demo 5 as
the template**: name the anti-pattern, *show* it failing (live where possible), state the cure, tie it
back to the lesson's payoff.

- **Scope:** the 11 mini-cut lessons only (see [SYLLABUS.md](../../src/fluffy_potato_curriculum/lessons/SYLLABUS.md) — mini column). Full-course-only lessons are out of scope for this pass.
- **Not-yet-authored roadmaps:** several mini lessons don't have `demos_or_activities.md` yet (L08/L09/L11/L12 per the [2026-06-09 tracker](2026-06-09-prd-curriculum.md)); for those, bake the gotcha beat in when the demos doc is first authored rather than retrofitting.
- **Candidate gotchas below are a starting list**, not final — the delegated session should refine against each lesson's actual objectives.

---

## Per-lesson checklist (mini cut, teaching order)

- [ ] **L01 — LLM & token basics.** Gotchas: word ≠ token (whitespace/punctuation/emoji/non-English cost
      more); silent **context-window overflow / truncation**; cost estimates that ignore **output** tokens;
      "temperature = randomness knob" oversimplifications.
- [ ] **L02 — Prompting fundamentals.** Anti-patterns: instructions in the **wrong role** (user vs system);
      trusting structured output **without defensive parsing/validation** (callback to L0206 fixtures);
      few-shot examples that **leak format or bias** the answer; bloated always-on system prompts.
- [ ] **L04 — Tool calling.** Gotchas: forgetting the **schema is in every request** (tokens twice over);
      model **hallucinating/omitting args**; mishandling the tool-call **round-trip**; assuming the model
      *always* calls the tool when it should.
- [ ] **L05 — Designing good tools.** Anti-patterns: **over-tooling** (a tool for what the model can do
      alone); vague tool **name/description**; **unhandled tool errors**; one tool doing too much (no clean
      schema).
- [ ] **L07 — Hand-rolled agent loop.** Gotchas: **no termination condition** (infinite loop) / no
      max-iterations guard; **not handling tool failures**; **unbounded context growth** across turns.
- [ ] **L08 — Tracing.** Anti-patterns: tracing **too little** (can't locate the failure) vs **too much**
      (noise, prompt bodies, PII); **not instrumenting tool calls**; reading spans out of order. *(bake in
      when the demos doc is authored)*
- [ ] **L09 — Evaluation.** Anti-patterns: eval set that only tests the **happy path**; **sample too small**;
      **over-trusting LLM-as-judge**; not targeting **failure modes seen in L08 traces**; regressions that
      slip through. *(bake in when the demos doc is authored)*
- [ ] **L11 — Explicit graphs & workflows (DAGs).** Gotchas: using a **workflow where an agent is needed**
      (or vice versa); **model-driven looping** sneaking into a "deterministic" DAG; **wrong model per node**
      (overpaying); brittle branch conditions. *(bake in when the demos doc is authored)*
- [ ] **L12 — Shallow LangGraph agent.** Gotchas: **state mismanagement** (messages vs counter / reducers /
      typing); **no termination**; conflating **prebuilt vs hand-assembled** `StateGraph`. *(bake in when the
      demos doc is authored)*
- [ ] **L20 — Skills.** Anti-patterns: description **too vague** (never triggers) or **too broad** (always
      triggers); a **skill that should be a tool** or **system-prompt content**; cramming occasionally-needed
      instructions into the system prompt. *(objectives.md already lists these; ensure a demo BEAT exists)*
- [x] **L21 — Skill patterns & composition.** ✅ **Already done** — Demo 5 (over-chaining ·
      shared-skill-that's-really-a-tool · description collisions). This is the **template** for the others.

---

## Approach notes for the delegated session

- **Template = L21 Demo 5's block shape:** Goal → Pre-flight → Live script (show it break) → What to
  highlight (name it + the cure) → If the demo misbehaves.
- **Prefer showing the failure live** where the mechanism is model-driven (selection, tool-calling,
  routing); use a **drawn/prepared** example where live failure is unreliable or destructive (e.g. L07
  infinite loop — cap iterations, don't actually hang the room).
- **Reuse the running examples** (`common/tools.py`: `calculator`/`lookup`/`flaky_fetch`; the L12 agent)
  so gotchas land on code students already know.
- **Cross-reference forward/back** — many gotchas are another lesson's main point (L01 context overflow →
  L17 context mgmt, full course; L04 token cost → L20/L21 JIT). Name the link; don't re-teach.
- Decide whether each gotcha beat is its **own demo** or a **"common pitfalls" coda** to an existing demo —
  likely per-lesson judgment (a full anti-pattern demo for L05/L20/L21; a shorter coda for L01/L08).
