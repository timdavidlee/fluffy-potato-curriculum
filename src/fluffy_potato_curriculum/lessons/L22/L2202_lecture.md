# Skills, tools, and prompts: where does a capability live?

```yaml
title: "Skills, tools, and prompts: where does a capability live?"
keywords: skill, tool, system prompt, taxonomy, called vs read vs always-seen, description, trigger, just-in-time, progressive disclosure, always-on context, mcp, token cost, agent skills
estimated duration: 25
```

> **Lesson:** L22. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L22/objectives.md).
> This is the written reference lecture — **slides + discussion, no live build**. It establishes the
> vocabulary and the core taxonomy the rest of the lesson leans on. The live JIT-loader build is the
> demo notebook ([L2203_lecture.ipynb](L2203_lecture.ipynb)); the decision heuristic and the real
> Agent Skills reveal are the closing lecture ([L2205_lecture.md](L2205_lecture.md)).
> **Anchor model: Claude Sonnet 4.6.**

## section 1. The problem skills solve

### slide 1.1 Everything is always in context

- After L07, L08, L10 and L11 you have a working agent — and one unsolved cost problem.
- Every **tool schema** is re-sent on *every* request (L07: "tools cost tokens, twice over").
- Every **system-prompt instruction** is paid for on *every* call, relevant or not.
- Ten tools the agent uses occasionally = ten schemas in the window on the call that needed none of
  them. This is the tax skills exist to remove.
- diagram: the lesson's window motif, beat one — a tall context-window column stuffed with 10 tool
  schema blocks + a long system-prompt block, a single user question at the bottom. The one schema
  the question actually needed is cyan; the nine unused schemas and the irrelevant prompt sections
  are coral ("paid for, unused" — the always-on tax). Re-shown slimmed in 1.2 and priced in 3.2/3.3.

### slide 1.2 The relief valve: load it *just in time*

- A **skill** is a capability the agent loads **only when it's relevant**, instead of carrying it
  always-on.
- It lives on disk as a small markdown file; only a one-line summary of it stays in context by
  default.
- The full instructions load **when the model decides they're needed** — not before.
- This is the first time in the course a capability is *not* always-on. That difference is the whole
  lesson.
- diagram: window motif, beat two — the same column re-drawn after the relief valve: the ten fat
  schema blocks replaced by ten one-line catalog entries (cyan), one full skill body arriving via a
  cyan arrow from a shelf of markdown files on disk, the other nine bodies dashed ink-faint on the
  shelf (dormant, not failed), the freed space in the column left visibly empty. No coral — this is
  the fix, not the failure.

## section 2. The core taxonomy

### slide 2.1 Called vs. read vs. always-seen

- table: the one-line discriminator for the three places a capability can live.

| Capability lives as… | The model… | Cost profile | Good for |
| --- | --- | --- | --- |
| **Tool** | *calls* it (structured schema in, structured result out) | schema in **every** request | deterministic operations with structured I/O |
| **System prompt** | *always sees* it | paid on **every** call | always-true behavior, persona, rules |
| **Skill** | *reads* it on demand | mostly **absent** until loaded | occasionally-needed, possibly multi-step know-how |

- Say it out loud until you can classify on sight: **a tool is *called*, a skill is *read*, the
  system prompt is *always seen*.**
- diagram: the taxonomy as three verbs around one context-window column — a tool schema chip welded
  inside the window with a call→result arrow pair ("called"), a system-prompt block welded in
  ("always seen"), and a skill card sitting *outside* on the disk shelf with a dashed arrow into the
  window ("read on demand"). Skill lane cyan (the lesson's contribution); tool and system-prompt
  lanes ink-faint neutral — established homes, not failures. No coral anywhere.

### slide 2.2 What a skill actually is

- A **named, described, markdown-based bundle of instructions** (plus optional scripts/resources) an
  agent loads just in time.
- Its four parts:
  - **name** — a short handle.
  - **description** — states *when* the skill applies. This is the **trigger**; the model decides
    relevance from this line alone.
  - **body** — imperative instructions written *for an agent to follow*, not prose for a human.
  - **optional scripts/resources** — deterministic steps the skill tells the agent to *run* rather
    than reason through.
- diagram: the skill-card motif, debut — a `SKILL.md` file split into four labeled bands: name +
  description bands cyan (the always-in-context catalog line), body band ink/neutral, scripts band
  dashed ink-faint ("not loaded yet"), with a bracket mapping each band to when it's paid for
  ("always / on selection / on invocation"). Re-shown as the disclosure ladder in 3.1 and echoed by
  L2205's real-`SKILL.md` reveal.

### slide 2.3 Where MCP fits (a one-line aside — full treatment is L09)

- **MCP** is *portable packaging/transport* for tools across clients. It answers *how a tool is
  shipped*, not *when knowledge is loaded*.
- It is **orthogonal** to the skill/tool/prompt question — an MCP-shipped tool is still a *tool* (a
  schema, always in context).
- We name it and move on; the full treatment is **L09 (MCP), full course**. In the mini cut we
  reason about **skill vs. tool vs. system prompt** only.
- diagram: re-draw L08's bridge picture — a tool spec card unchanged inside a dashed ink-faint MCP
  envelope ("packaging/transport — full treatment L09, full course"), its schema still welded into
  the always-on window; beside it, 2.2's cyan skill card untouched by the envelope (orthogonal
  axes). Dashed = deferred, not broken; no coral — MCP is an aside, not a failure.

## section 3. Progressive disclosure — the mechanism

### slide 3.1 Three levels of visibility

- **Progressive disclosure** is the layering that makes just-in-time loading work:
  - **name + description** — *always* in context (cheap, one line each).
  - **body** — loads *only when the model selects the skill*.
  - **scripts/resources** — load/run *only when actually invoked*.
- diagram: skill-card motif, beat two — 2.2's four-band card re-drawn as a three-step disclosure
  ladder: "name+description (always)" the small first step in cyan, "body (on selection)" a taller
  ink/neutral step, "scripts (on run)" the tallest step dashed ink-faint — a token-cost meter
  rising with each step. Cyan marks the only part that's always paid for; no coral — the deeper
  levels are deferred cost, not failure.

### slide 3.2 The payoff, in tokens

- Ten **tools** = ten full schemas on every call. Ten **skills** = ten one-line descriptions on
  every call; the bodies stay on disk until needed.
- table: the always-on cost, side by side.

| | Always-on context cost | When the full content is paid for |
| --- | --- | --- |
| 10 tools | 10 full schemas, every call | always |
| 10 skills | 10 one-line descriptions, every call | only the one(s) actually loaded |

- This is L07's "tools cost tokens twice over" problem, directly attacked. You'll read the real token
  deltas off a trace in the demo notebook.
- diagram: the money slide — the window motif priced as a bar chart: left bar "10 tools" a stack of
  ten fat schema segments in coral (the always-on tax, paid on every call); right bar "10 skills"
  ten thin cyan description slivers plus one cyan body segment that appears only on the call that
  loaded it — bar heights making the delta obvious. This is the chart the demo notebook's
  `rough_tokens` numbers land on.

### slide 3.3 Skills are cheap, not free

- Each skill still costs its **name + description** in always-on context — a pile of them adds up.
- Overlapping or vague descriptions make the model's *selection* worse, so more skills can mean
  *worse* behavior, not just more cost.
- And you pay two real costs when a skill *does* load: an **extra model turn** to load it, and the
  **risk the model fails to load** a skill it actually needed.
- **Curate.** Skills are a shelf you keep tidy, not a junk drawer.
- diagram: third beat of 3.2's chart — the skills bar re-drawn at 30 skills: the description-sliver
  stack now visibly tall, its top slivers turning coral (the catalog itself becoming always-on
  bloat), with two coral cost chips pinned beside the bar ("extra turn to load", "needed skill
  never fired"). Caption: cheap, not free — curate the shelf.

## section 4. The description is the skill

### slide 4.1 Whether a skill works is mostly whether its description fires

- The **description is a design artifact**, not a label — the skill analogue of L08's tool
  naming/schema design.
- It must be **discriminating**: fire on the right inputs, stay quiet otherwise, all decided from the
  description *alone* (the body isn't loaded yet).
- diagram: contrast two-up of one skill card — left panel cyan: a tight description ("Apply when
  the user asks to process a refund or return") firing on the right request, cyan check; right
  panel coral: a vague description ("helps with customer stuff") that either never loads or loads
  on everything, coral X. Cyan = the description that discriminates; coral = the one that can't.
  Seeds 4.2's failure strips.

### slide 4.2 The failure modes of just-in-time loading

- **Description too vague** → the skill silently never loads when it was needed.
- **Description too broad** → the skill loads constantly, defeating the token savings.
- **Body assumes lost context** → instructions that reference state the agent no longer has once the
  skill loads mid-run.
- Each is a *design* failure in the skill, not a model failure — which is why authoring the
  description is the craft.
- diagram: three failure strips under one cyan reference strip (4.1's healthy fire: request →
  description matches → body loads). Strip one: vague description, the body dashed and never
  arriving, coral tag "needed, never fired". Strip two: broad description, a coral body loading on
  *every* turn, the token savings struck through. Strip three: body loaded mid-run with a coral "?"
  pointing at context the agent no longer has. Coral marks each design fault; the mechanism itself
  stays cyan.

## section 5. Vocabulary to carry into the labs

### slide 5.1 The terms, defined once

- table: reuse these verbatim through the demo and the labs.

| Term | Definition |
| --- | --- |
| **Skill** | a named, described, markdown bundle of instructions (+ optional scripts) loaded just in time |
| **Just-in-time (JIT) loading** | bringing a capability's full content into context only when needed |
| **Progressive disclosure** | name+description always visible → body on selection → scripts on run |
| **Description (the trigger)** | the line that tells the model *when* a skill applies; the load-bearing part |
| **Always-on context** | content in every request (system prompt, tool schemas) — what skills keep small |
| **Skill vs. tool vs. system prompt** | *read on demand* vs. *called with a schema* vs. *always seen* |

### slide 5.2 What's next

- Next you'll **build** the mechanism on the agent you already own: your L11 `create_agent`
  shallow agent, given one `load_skill` tool and the catalog as its system prompt
  ([L2203_lecture.ipynb](L2203_lecture.ipynb)), and watch the body load only when the description
  fires.
- Then you'll decide **where a capability belongs** and meet the **real** Agent Skills format
  ([L2205_lecture.md](L2205_lecture.md)) — the production version of what you built.
- diagram: bridge — re-draw the L11 `create_agent(...)` bracket (the picture L11 closed on): the
  loop inside unchanged, now with a cyan `load_skill` tool chip and a cyan skill-catalog chip wired
  in as the system prompt — the only two new parts you add in the demo. A dashed ink-faint arrow
  points from the loaded body to a small `SKILL.md` card labeled "the real thing — L2205". Cyan =
  what you build next; dashed = the reveal ahead.
