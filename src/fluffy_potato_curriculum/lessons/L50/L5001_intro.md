# Your mini-project — one agent, end to end

```yaml
title: "Your mini-project — one agent, end to end"
keywords: capstone, mini-project, vertical slice, assembly, tool design, shallow agent, trace, eval case, receipt reconciliation, walkthrough
estimated duration: 5
```

> **Lesson:** L50 — Agent mini-project (mini-track capstone).
> **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L50/objectives.md) · [demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L50/demos_or_activities.md)
> **Read in order:** this intro → the framing deck [L5002_lecture](L5002_lecture.md) → the guided build [L5003_lecture](L5003_lecture.ipynb). Then read [MINI_WRAPUP](../MINI_WRAPUP.md) for the course-level wrap.
> **Format:** this is a **walkthrough**, not a lecture+lab. The proctor builds one small agent live; you rebuild it alongside, cell by cell. There's no separate student lab here — the independent build is the [end-of-week project](../../../../docs/origin/PROJECT_BRIEF_DESIGN.md), which this warms you up for.

## This is the whole arc, run once as one motion

Everything you've built in the agent thread, you built **one piece at a time, on a task the course handed you**. You designed a tool ([L07](../L07/L0701_intro.md), [L08](../L08/L0801_intro.md)). You wired the model→tool→model loop ([L10](../L10/L1001_intro.md)) and met its one-line form, `create_agent` ([L11](../L11/L1101_intro.md)). You traced a run and read it in Langfuse ([L12](../L12/L1201_intro.md)). You turned a failure into an eval case ([L13](../L13/L1301_intro.md)).

What you've **never** done is drive that whole arc yourself, in order, on a task that's *yours* — decide what the agent is for, design its one tool, wire the agent, trace it, find a failure in the trace, and turn that failure into an eval case, as one connected build. **That's L50.** It's the difference between *"I can do each step when told to"* and *"I can take a blank cell and a fuzzy goal and produce a traced, evaluated agent."*

## Nothing here is new — and that's the point

L50 teaches **no new concept**. Its whole job is to *assemble* skills you already have. So keep one rule in mind the entire time: **if a step feels unfamiliar, the fix is the lesson that owns it, not this one.** You are not re-implementing the loop, the trace emitter, or the eval types — every one of them lives in the shared `common/` layer, and you'll import it. The *only* genuinely new code you'll write is **one small tool**.

That constraint is the lesson. A capstone's skill isn't building something big and impressive — it's **finishing a thin slice**. You'll build the thinnest thing that still exercises all five objectives end to end — one task, one new tool, one running agent, one trace, one eval case — and then you'll **stop**. Scope creep is the failure mode of this exact lesson.

## What you'll build

A **receipt-reconciliation** agent. It takes one receipt — which arrives in a different shape from every source (a cafe's tidy JSON, a rideshare's differently-named fields, a hotel's raw printed text) — and matches it against a small offline ledger of expense records, checking whether the amounts agree and flagging a receipt it can't confidently place.

- The **one new tool you write** is `find_matching_record`: normalize a receipt from *any* of those formats to a common shape and look it up. It's genuinely warranted — reliable cross-format normalize-and-match is exactly what you don't want a model doing by eyeball — which is why there's something real to trace and eval.
- The **two tools the agent also runs** are `calculator` (reused straight from `common/tools.py` — total the line items and check the variance) and a pre-built `check_expense_policy` — an **LLM read** of the company's free-form policy prose that judges the expense and cites the rule (the one *LLM-in-the-loop* tool in the slice). You don't author these, but together they give the agent a real *three-tool* decision worth tracing. The authoring budget stays at one tool; the agent's toolset does not.
- The **failure you'll find** is a malformed receipt — OCR gave up, no readable vendor. A good agent reports "no confident match" and stops; a naive one keeps retrying the matcher on the same bad input. You'll spot that runaway **in the trace**, then write the one eval case that catches it forever.

## The deliverable is a *finished* slice

Leaving L50, the thing to hold onto: **an agent that "worked once" is not done.** The habit this mini course has been building — trace before you guess, eval or it's vibes — is what turns a demo that happened to pass into a finished slice. Your slice is done when it's traced *and* has at least one eval case that would catch its regression.

Then you'll name the **first thing you'd add next** — and that's the seam into your own [end-of-week project](../../../../docs/origin/PROJECT_BRIEF_DESIGN.md). You'll have watched one agent go blank-cell-to-evaluated; your team build is the same shape, wider and yours.

## Before you start

L50 makes **live** model calls and **live** Langfuse writes when the cohort stack is up — your keys from [K02](../K02/K0201_guide.md) and the Docker stack from [K06](../K06/K0601_guide.md), read through `common/config.py`. The guided-build notebook is written to run **reproducibly offline** on scripted stand-ins (a `FakeModel` for the agent's brain, a scripted judge for the policy read), with the **live** cells — a real Sonnet policy read (Section 2) and the Langfuse trace push (Section 4) — clearly gated, so a hiccup in the stack never strands you mid-build, and in class you flip the live cells on to see your run in the real dashboard.
