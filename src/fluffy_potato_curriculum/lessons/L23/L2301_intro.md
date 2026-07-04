# Skill patterns & composition: from one skill to a system

```yaml
title: "Skill patterns & composition: from one skill to a system"
keywords: skill archetype, script-centric, principle-centric, procedure-centric, rubric, runbook, composition, sequential handoff, shared skill, dependency graph, just-in-time loading, list_skills, load_skill, over-chaining, description collision, composition capstone
estimated duration: 8
```

> **Lesson:** L23 — Skill patterns & composition.
> **Roadmap:** see this lesson's [objectives.md](../../../../docs/origin/lesson_roadmaps/L23/objectives.md)
> and [demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L23/demos_or_activities.md).
> This is a short framing piece. Read it first, then the written archetypes lecture
> ([L2302_lecture.md](L2302_lecture.md)) and its lab ([L2303_lab_empty.ipynb](L2303_lab_empty.ipynb)),
> then the composition + dependency-graph demo notebook ([L2304_lecture.ipynb](L2304_lecture.ipynb)),
> the anti-patterns notebook ([L2305_lecture.ipynb](L2305_lecture.ipynb)), and the capstone lab
> ([L2306_lab_empty.ipynb](L2306_lab_empty.ipynb)).
> **Anchor model: Claude Sonnet 4.6** — the same model the whole course anchors on. Skills and
> their composition are model-agnostic; we pin the demos to one model so the only new thing is
> *how capabilities are shaped and wired together*, not *which model runs them*.

## Where this lesson sits

In [L22](../L22/L2201_intro.md) you met **the skill**: a named, described, markdown instruction
file an agent loads **just in time**, only when its **description** matches, instead of carrying it
always-on. You hand-built a minimal just-in-time loader on your [L11](../L11/L1101_intro.md)
`create_agent` shallow agent, authored one `SKILL.md`, and drilled the one-line taxonomy:

> **A tool is something the model *calls*. A skill is something the model *reads*. The system
> prompt is something the model *always sees*.**

L22 answered *"where should a **single** capability live?"* L23 picks up the two questions L22
deliberately left open:

1. **Skills are not all the same shape.** L22 treated "skill" as one thing. In practice skills fall
   into a few recurring **archetypes**, each with a different *center of gravity* — a bundled
   **script**, a **rule list**, or an ordered **procedure**. The archetype tells you *where the
   real content belongs*, and writing the wrong shape is the archetype-level version of L22's
   "wrong container" mistake.
2. **Skills compose into systems.** One skill rarely stands alone. Two composition moves turn a
   pile of skills into a system: a **sequential handoff** (one skill's output feeds the next) and a
   **shared lower-level skill** (several skills all invoke one). Once skills call skills there's a
   **dependency graph**, and just-in-time loading now happens *across* that graph — which is where
   the interesting cost reasoning and the failure modes live.

So the arc is: **classify** a skill by archetype → **author** each archetype well → **compose**
skills two ways → **reason about the dependency graph and its JIT loading** → **spot the
anti-patterns** that make a skill system worse than the pile of prompts it replaced.

## The runtime: discovery becomes a tool

In L22 the agent's skill catalog (every skill's name + description) sat in the **system prompt** —
always-on. L23 sharpens that. The runtime is still your L11/L04 `create_agent` shallow agent, but
now it carries **two skill-loading tools**:

- **`list_skills()`** — returns every registered skill's `{name, description}` (**discovery**).
- **`load_skill(name)`** — reads one skill's full body into context (**load**).

The model *calls `list_skills` to see what's available, then `load_skill` to pull the one it needs.*
This is L22's just-in-time mechanism expressed as **agent tools** rather than a hand-rolled loader —
and it makes composition concrete: *"skill A invokes skill B"* is literally *A's body telling the
agent to `load_skill("B")`.* It also refines L22's cost story: now the only always-on skill cost is
**two tool schemas**, no matter how many skills exist — the descriptions load per-`list_skills`
call, and bodies load per-`load_skill` along the path actually taken.

## This is not hypothetical — you're sitting in a skill system

The strongest evidence that composition is real is the repo in front of you. This curriculum is
authored by a small **skill system** under [`.claude/skills/`](../../../../.claude/skills): a
**sequential handoff** — `author-lesson-roadmap` (write the roadmap) → `generate-materials-from-roadmap`
(build the student materials from it) — plus supporting skills, and the `.claude/rules/*.md` files
as real rubric-style guidance. This very lesson was produced by that handoff. Two more example
skills built specifically for L23 live in [`example_skills/`](example_skills/README.md): a
**script-centric** `get_order` skill over a mock API with a messy JSON contract, and a **shared**
`check_lesson_links` skill. You'll read and graph these, not invented toys.

## What you'll be able to do by the end

- **Classify a skill by archetype** — script-centric (API/integration recipe), principle-centric
  (review/rubric), procedure-centric (operating-model runbook) — and say why the archetype dictates
  where the content belongs.
- **Author each archetype** in the `SKILL.md` format, shaping the body to the archetype.
- **Compose skills two ways** — a sequential handoff and a shared lower-level skill — and name the
  **seam contract** that makes a handoff worth it.
- **Draw the skill dependency graph** and reason about just-in-time loading across it, quantifying
  the always-on cost as *two tool schemas*.
- **Recognize the three composition anti-patterns** — over-chaining, a shared "skill" that's really
  a tool, and description collisions — and audit a system for them.

> This is the **composition capstone of the skills thread** — you turn the individual pieces
> (prompts, tools, the agent loop, one skill) into a *system of skills*. It is **not** the end of
> the course: the closing recap lives in [`MINI_WRAPUP.md`](../MINI_WRAPUP.md).
