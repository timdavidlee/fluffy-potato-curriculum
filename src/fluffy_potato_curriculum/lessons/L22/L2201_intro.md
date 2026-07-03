# Skills: capabilities the agent loads just in time

```yaml
title: "Skills: capabilities the agent loads just in time"
keywords: skill, just-in-time, jit loading, progressive disclosure, description, trigger, tool vs skill vs system prompt, always-on context, SKILL.md, agent skills, capstone, where should capability live
estimated duration: 8
```

> **Lesson:** L22 — Skills: just-in-time capabilities for agents.
> **Roadmap:** see this lesson's [objectives.md](../../../../docs/origin/lesson_roadmaps/L22/objectives.md)
> and [demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L22/demos_or_activities.md).
> This is a short framing piece. Read it first, then the written reference lecture on the
> taxonomy ([L2202_lecture.md](L2202_lecture.md)), the hand-rolled JIT-loader demo notebook
> ([L2203_lecture.ipynb](L2203_lecture.ipynb)), and the closing decision + real-Agent-Skills
> lecture ([L2205_lecture.md](L2205_lecture.md)). Hands-on practice is in the L22 labs
> (L2204, L2206).
> **Anchor model: Claude Sonnet 4.6** — the same model the whole course anchors on. Skills are
> model-agnostic; we pin the demos to one model so the only new thing is *how a capability is
> loaded*, not *which model runs it*.

## Where this lesson sits

In the mini cut this is the **final lesson**, and it is a **capstone**. By now you have built the
whole agent stack: prompting and structured output ([L02](../L02/L0201_intro.md)); tools — what
they are, how they're wired, and what they cost ([L07](../L07/L0701_intro.md),
[L08](../L08/L0801_intro.md)); the hand-rolled model → tool → model loop
([L10](../L10/L1001_intro.md)); and that same loop drawn as a LangGraph graph
([L04](../L04/L0401_intro.md), [L14](../L14/L1401_intro.md)).

All of that shares one nagging, unsolved problem: **everything the agent might need has to sit in
the context window all the time.** Every tool's schema is re-sent on every request (L07's "tools
cost tokens, twice over"). Every instruction the agent might need lives in the system prompt, paid
for on every call whether it's relevant or not. Add enough tools and instructions and the context
bloats, the model gets distracted, and cost climbs — for capability the agent uses only
occasionally.

## The one idea: load the capability *just in time*

A **skill** is the answer to that problem: a capability the agent loads **just in time**, only when
it's relevant, instead of carrying it always-on.

Concretely, a skill is a small **markdown instruction file** — a `name`, a `description` of *when it
applies*, a body of instructions, and optionally some supporting scripts. It sits dormant on disk
until the agent decides it's needed. Only the skill's short **name + description** stay in context
by default; the full **body** loads when the model judges it relevant, and any bundled **scripts**
run only when actually invoked. That layering is **progressive disclosure** — the same idea that
lets you keep a shelf of reference manuals without memorizing all of them.

The one-line discriminator you'll drill this whole lesson:

> **A tool is something the model *calls*. A skill is something the model *reads*. The system
> prompt is something the model *always sees*.**

## Concept first, then the real thing

This lesson follows the course's spine — **hand-roll it, then meet the product** — exactly like L11
(you built a trace before Langfuse) and L14 (you built the loop before LangGraph):

1. First you build a **minimal just-in-time skill loader** on the agent you already own. The agent
   sees a list of skill *names + descriptions*; only when it picks one does the full instruction
   file get read into context. You *feel* the mechanism.
2. Then you meet the real thing — **Anthropic Agent Skills**, the same `SKILL.md`-shaped format
   this very curriculum is authored with (look under `.claude/skills/`). You recognize it as the
   production version of what you just built — familiar, not magic.

## What you'll be able to do by the end

- Explain what a skill is and how it differs from a tool, a prompt, and (briefly) an MCP server.
- Author a markdown skill whose **description** reliably triggers on the right inputs.
- Reason about just-in-time loading vs. always-on context, and quantify the token payoff.
- Decide when a capability belongs as a **skill** vs. a **tool** vs. **system-prompt content** —
  the capstone question, *"where should a capability live?"*
