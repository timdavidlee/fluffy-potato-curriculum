# Where does a capability live? And the real thing: Agent Skills

```yaml
title: "Where does a capability live? And the real thing: Agent Skills"
keywords: decision heuristic, skill vs tool vs system prompt, composition, orchestration, anti-patterns, agent skills, SKILL.md, frontmatter, claude code, capstone, subagent, l22
estimated duration: 22
```

> **Lesson:** L22 — its closing lecture, and a capstone of the *"where does a single capability
> live?"* question. It is **not** the end of the mini cut: L23 and L50 still follow (see §5.2).
> **Roadmap:** [demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L22/demos_or_activities.md).
> Closing lecture — **decision + reveal, diagram and discussion, no live build**. It applies the
> heuristic from Demo 4 and then opens a real `SKILL.md` from *this repo* to show the production
> version of the loader you built in [L2203_lecture.ipynb](L2203_lecture.ipynb).
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
- diagram: the lesson's motif debut — the **three-homes row**: one capability chip on the left
  feeding a three-way fork into three home boxes side by side — a **tool** box ("called"), a
  **system-prompt** band ("always seen"), a **skill** card ("read on demand") — each fork edge
  labeled with its discriminator from the table. All three homes and edges cyan (none is a failure
  — the point is *placement*, not avoidance); this exact row recurs in 1.2, 3.1, and 5.1.

### slide 1.2 Four capabilities, classified

- table: run the heuristic on concrete cases (Demo 4's set).

| Capability | Home | Why |
| --- | --- | --- |
| compute sales tax | **tool** | deterministic math, structured I/O |
| our brand voice / tone rules | **system prompt** | always-true, applies to every reply |
| the multi-step refund-handling procedure | **skill** | procedural, needed only on refunds |
| look up an order by id | **tool** | deterministic lookup, structured I/O |

- Defend each out loud. Disagreement is healthy — the edges are where the judgment lives.
- diagram: second beat of the three-homes row — the same three boxes, now with Demo 4's four
  capability chips landed in their homes: `sales_tax` and `lookup_order` chips inside the tool
  box, "brand voice" inside the system-prompt band, "refund procedure" inside the skill card.
  Chips and homes all cyan — every placement here is correct; coral is reserved for §3's
  mis-placements.

## section 2. Skills compose with tools — they don't replace them

### slide 2.1 A skill orchestrates tools

- A skill often *describes how to use* one or more tools. The refund **skill** (procedure) tells
  the agent to call the order-lookup **tool** and the sales-tax **tool** in the right order.
- diagram: the `refund-policy` skill card (cyan — the orchestration know-how is this slide's
  point) at the top with its numbered steps; numbered cyan arrows down to slide 1.2's two tool
  chips, now opened as tool boxes (`lookup_order`, `sales_tax`) drawn neutral ink-faint (the
  operations — L07/L08 material, not the new idea); caption "the skill is the *procedure*; the
  tools are the *operations*." No coral — nothing here fails.
- Skills are the natural home for **orchestration** know-how: *"to handle a refund, first look up
  the order, then compute the refund, then reply."*

### slide 2.2 A skill can push work into a script

- Deterministic steps don't belong in prose reasoning — a skill can tell the agent to **run a
  script** (`refund_amount.py`) instead of doing arithmetic in its head. Cheaper, and reliable.
- This is the third layer of progressive disclosure: **scripts load only when actually invoked**.
- So a skill has two ways to stay lean: it's *read* only when relevant, and its deterministic parts
  *run* as code rather than as tokens.
- diagram: the 2.1 picture extended one step — the skill's "compute the refund" step forks two
  ways: a coral struck-through path into a blob of prose-token arithmetic ("reasoned in its head —
  expensive, unreliable") vs a cyan path into a `refund_amount.py` script chip ("run, not
  reasoned"); the script chip drawn dashed until invoked, tagged "loads only on run" (progressive
  disclosure's third layer, echoing L2202's rings).

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
- diagram: third beat of the three-homes row — the same three boxes, with the table's three
  mis-placed capabilities drawn as coral chips sitting in the wrong home (sometimes-needed
  instructions jammed into the system-prompt band; a procedure forced into a tool schema; a
  one-line always-true rule wrapped in a skill card), each with a cyan relocation arrow carrying
  it to its correct home. Coral marks the wrong *placement* only — the homes themselves stay
  cyan; caption "cost follows placement."

## section 4. The reveal: you already built Agent Skills

### slide 4.1 The loader you built, productized

- Open a real skill from this repo: `.claude/skills/author-lesson-roadmap/SKILL.md`.
- It is the *same shape* you built in Demo 3:
  - YAML **frontmatter** with `name` + `description` — the always-on catalog entry (your
    `Skill.name` / `Skill.description`).
  - a markdown **body** of imperative instructions — loaded on demand (your `Skill.body`).
  - supporting structure/scripts in the skill's folder — run when invoked.
- diagram: the reveal, side by side — left: your L11 `create_agent(...)` bracket re-drawn as in
  the L1102 deck (cyan loop) with your `Skill` catalog pills and the `load_skill` tool attached;
  right: a `SKILL.md` file under `.claude/skills/` drawn as L2202's four-band card (name /
  description / body / scripts) loaded by Claude Code; a large cyan `=` between them. Both sides
  fully cyan — explicitly no coral anywhere; the whole slide is a happy-path equality.

### slide 4.2 The meta-punchline

- **The curriculum you are taking is itself built from skills.** These lessons were generated by
  `generate-materials-from-roadmap` — a skill — loaded just in time by Claude Code, exactly like
  the loader you built.
- Same payoff as the rest of the course's spine: L12's hand-rolled trace became Langfuse; L11's
  hand-rolled loop became LangGraph's `create_agent`; **the `load_skill` tool + catalog you added
  to that agent is Agent Skills.** You met the mechanism before the product, so the product reads
  as familiar, not magic.
- You're not learning the Agent SDK's mechanics here — just landing that the concept and the
  product are the same idea.
- diagram: the course-spine ladder — three "you built → the product" rungs stacked: L12
  hand-rolled trace → **Langfuse**; L11 hand-rolled loop → **LangGraph `create_agent`**; this
  lesson's `load_skill` + catalog → **Agent Skills**. The two earlier rungs in ink-dim (already
  landed, context only), the bottom rung and its "became" arrow cyan (today's punchline); caption
  "you met the mechanism before the product."

## section 5. Capstone — and where you go next

### slide 5.1 The one sentence to leave with

- **A tool is *called*, a skill is *read*, the system prompt is *always seen* — and "where should
  this capability live?" is answered by *when* it needs to be in context.**
- That single question ties together everything you built this course: prompts (L02), tools
  (L07/L08), the agent loop (L10), and its LangGraph form (L04/L11).
- diagram: motif bookend — the three-homes row one last time, each home with a small context-cost
  bar beneath showing *when* it's in context: the system prompt a full-width always-on bar
  (ink-faint, "always seen"), the tool a full-width schema bar (ink-faint, "schema every call") —
  and the skill just a thin description sliver plus a dashed body block that pops in only on
  load, both cyan (the lesson's whole point: skills stay small until *read*). Echoes L2202's
  stuffed-window opener, now solved.

### slide 5.2 What's next

- **Next — [L23: Skill patterns & composition](../L23/L2301_intro.md)** (both tracks). You authored
  *one* skill well; L23 composes *many* into a **system**: skill archetypes, the two composition moves
  (sequential handoff and a shared sub-skill), the dependency graph that just-in-time loading runs
  across, and the **composition anti-patterns** — the system-scale sequel to §3's "wrong container"
  faults.
- **Then the mini cut closes with L50 — the agent mini-project walkthrough** (an end-to-end build:
  tool → agent loop → trace → eval). So L22 is a capstone of *"where does a single capability live?"*,
  **not** the last mini lesson; the track's closing recap is [MINI_WRAPUP.md](../MINI_WRAPUP.md), owned by
  no single lesson. (Full mini sequence: [SYLLABUS.md](../SYLLABUS.md).)
- **Full-course-only branches — name them, don't teach them here.** In the full course L22 also bridges
  to **L24 (multi-agent / subagents)**: a *subagent* is capability-as-a-whole-agent — the same "where
  should capability live" lens, scaled from a skill up to an entire agent. The broader "keep a
  long-running agent's context lean" problem is **L19 (context management)**, and the fuller
  capability-packaging taxonomy (with MCP) is **L09**. All three are outside the mini cut.
- diagram: the road ahead as a small map — a solid cyan "L22 — one capability, one home" node
  (you are here) with a cyan arrow to a dashed **L23** box sketched as several small skill cards
  joined by dependency edges ("many skills → a system"), then a dashed arrow on to a dashed
  **L50** box drawn as the mini-project chain (tool → loop → trace → eval); off to one side,
  three ink-faint dashed ghosts for the full-course-only branches — **L24** as a whole tiny agent
  loop inside a capability chip ("capability as an agent"), **L19** context management, **L09**
  MCP. Dashed ink-faint = deferred, not failure — nothing on this slide is coral.
