# Where does a capability live? And the real thing: Agent Skills

```yaml
title: "Where does a capability live? And the real thing: Agent Skills"
keywords: decision heuristic, skill vs tool vs system prompt, composition, orchestration, anti-patterns, agent skills, SKILL.md, frontmatter, claude code, capstone, subagent, l22
estimated duration: 22
```

> **Lesson:** L22 (the mini cut's **final lesson** — a capstone).
> **Roadmap:** [demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L22/demos_or_activities.md).
> Closing lecture — **decision + reveal, diagram and discussion, no live build**. It applies the
> heuristic from Demo 4 and then opens a real `SKILL.md` from *this repo* to show the production
> version of the loader you hand-built in [L2203_lecture.ipynb](L2203_lecture.ipynb).
> **Anchor model: Claude Sonnet 4.6.**

## section 1. The decision: where should a capability live?

### slide 1.1 The heuristic

- table: match a capability to its home by its shape.

| If the capability is… | It belongs as… | Because… |
| --- | --- | --- |
| a deterministic operation with structured input/output, called mid-reasoning | a **tool** | the model *calls* it and gets a structured result |
| always-true behavior, persona, or a rule that must hold on *every* call | **system-prompt content** | it must *always* be seen |
| a multi-step procedure / domain know-how used only *sometimes*, maybe bundling scripts | a **skill** | it can be *read* just in time, kept out of context otherwise |

- The question is never "skill or tool?" in the abstract — it is **"where does *this particular*
  capability belong?"**

### slide 1.2 Four capabilities, classified

- table: run the heuristic on concrete cases (Demo 4's set).

| Capability | Home | Why |
| --- | --- | --- |
| compute sales tax | **tool** | deterministic math, structured I/O |
| our brand voice / tone rules | **system prompt** | always-true, applies to every reply |
| the multi-step refund-handling procedure | **skill** | procedural, needed only on refunds |
| look up an order by id | **tool** | deterministic lookup, structured I/O |

- Defend each out loud. Disagreement is healthy — the edges are where the judgment lives.

## section 2. Skills compose with tools — they don't replace them

### slide 2.1 A skill orchestrates tools

- A skill often *describes how to use* one or more tools. The refund **skill** (procedure) tells
  the agent to call the order-lookup **tool** and the sales-tax **tool** in the right order.
- diagram: the `refund-policy` skill body at the top with numbered steps; arrows down to two tool
  boxes (`lookup_order`, `sales_tax`) it invokes; caption "the skill is the *procedure*; the tools
  are the *operations*."
- Skills are the natural home for **orchestration** know-how: *"to handle a refund, first look up
  the order, then compute the refund, then reply."*

### slide 2.2 A skill can push work into a script

- Deterministic steps don't belong in prose reasoning — a skill can tell the agent to **run a
  script** (`refund_amount.py`) instead of doing arithmetic in its head. Cheaper, and reliable.
- This is the third layer of progressive disclosure: **scripts load only when actually invoked**.
- So a skill has two ways to stay lean: it's *read* only when relevant, and its deterministic parts
  *run* as code rather than as tokens.

## section 3. The anti-patterns

### slide 3.1 Three ways to put a capability in the wrong home

- table: the smell, and the fix.

| Anti-pattern | Why it hurts | Fix |
| --- | --- | --- |
| occasionally-needed instructions crammed into the **system prompt** | always-on cost for sometimes-needed content; crowds the window | make it a **skill** |
| a **tool** built for procedural know-how | rigid; multi-step "how to phrase a refusal" doesn't fit a schema | make it a **skill** |
| a **skill** made for a one-line always-true rule | pays an extra load turn + a miss risk for something that should just always apply | put it in the **system prompt** |

- The recurring lesson: **cost follows placement.** Put a capability where its *usage pattern*
  says it belongs, not where it's convenient to drop.

## section 4. The reveal: you already built Agent Skills

### slide 4.1 The hand-rolled loader, productized

- Open a real skill from this repo: `.claude/skills/author-lesson-roadmap/SKILL.md`.
- It is the *same shape* you hand-built in Demo 3:
  - YAML **frontmatter** with `name` + `description` — the always-on catalog entry (your
    `Skill.name` / `Skill.description`).
  - a markdown **body** of imperative instructions — loaded on demand (your `Skill.body`).
  - supporting structure/scripts in the skill's folder — run when invoked.
- diagram: side by side — your `Skill` dataclass + `jit_run` loop on the left; a `SKILL.md` file
  under `.claude/skills/` loaded by Claude Code on the right — with `=` between them.

### slide 4.2 The meta-punchline

- **The curriculum you are taking is itself built from skills.** These lessons were generated by
  `generate-materials-from-roadmap` — a skill — loaded just in time by Claude Code, exactly like
  the loader you wrote.
- Same payoff as the rest of the course's spine: L12's hand-rolled trace was Langfuse; L11's
  hand-rolled loop was LangGraph; **L22's hand-rolled loader is Agent Skills.** You met the
  mechanism before the product, so the product reads as familiar, not magic.
- We are **not** teaching the Agent SDK's mechanics here — just landing that the concept and the
  product are the same idea.

## section 5. Capstone — and one line beyond

### slide 5.1 The one sentence to leave with

- **A tool is *called*, a skill is *read*, the system prompt is *always seen* — and "where should
  this capability live?" is answered by *when* it needs to be in context.**
- That single question ties together everything you built this course: prompts (L02), tools
  (L07/L08), the agent loop (L10), and its LangGraph form (L04/L11).

### slide 5.2 The forward pointer (full course only — don't teach it here)

- In the full course, L22 bridges to **L24 (multi-agent / subagents)**: a *subagent* is
  capability-as-a-whole-agent — the same "where should capability live" lens, scaled from a skill up
  to an entire agent.
- The broader "keep a long-running agent's context lean" problem is **L19 (context management)**;
  the fuller capability-packaging taxonomy (with MCP) is **L09**. Name them; the mini cut ends here.
