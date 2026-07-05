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
- diagram: a fat context window stuffed with 10 tool schemas + a long system prompt, with a single
  user question at the bottom that only needed one of them — the rest greyed out as "paid for,
  unused."

### slide 1.2 The relief valve: load it *just in time*

- A **skill** is a capability the agent loads **only when it's relevant**, instead of carrying it
  always-on.
- It lives on disk as a small markdown file; only a one-line summary of it stays in context by
  default.
- The full instructions load **when the model decides they're needed** — not before.
- This is the first time in the course a capability is *not* always-on. That difference is the whole
  lesson.

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
- diagram: a `SKILL.md` file split into four labeled bands (name, description, body, scripts) with a
  bracket showing "name + description = always in context; body loads on selection; scripts run on
  invocation."

### slide 2.3 Where MCP fits (a one-line aside — full treatment is L09)

- **MCP** is *portable packaging/transport* for tools across clients. It answers *how a tool is
  shipped*, not *when knowledge is loaded*.
- It is **orthogonal** to the skill/tool/prompt question — an MCP-shipped tool is still a *tool* (a
  schema, always in context).
- We name it and move on; the full treatment is **L09 (MCP), full course**. In the mini cut we
  reason about **skill vs. tool vs. system prompt** only.

## section 3. Progressive disclosure — the mechanism

### slide 3.1 Three levels of visibility

- **Progressive disclosure** is the layering that makes just-in-time loading work:
  - **name + description** — *always* in context (cheap, one line each).
  - **body** — loads *only when the model selects the skill*.
  - **scripts/resources** — load/run *only when actually invoked*.
- diagram: three concentric rings — outer "name+description (always)", middle "body (on selection)",
  inner "scripts (on run)" — with a token cost meter rising as you move inward.

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

### slide 3.3 Skills are cheap, not free

- Each skill still costs its **name + description** in always-on context — a pile of them adds up.
- Overlapping or vague descriptions make the model's *selection* worse, so more skills can mean
  *worse* behavior, not just more cost.
- And you pay two real costs when a skill *does* load: an **extra model turn** to load it, and the
  **risk the model fails to load** a skill it actually needed.
- **Curate.** Skills are a shelf you keep tidy, not a junk drawer.

## section 4. The description is the skill

### slide 4.1 Whether a skill works is mostly whether its description fires

- The **description is a design artifact**, not a label — the skill analogue of L08's tool
  naming/schema design.
- It must be **discriminating**: fire on the right inputs, stay quiet otherwise, all decided from the
  description *alone* (the body isn't loaded yet).
- diagram: two copies of one skill — a tight description ("Apply when the user asks to process a
  refund or return") that fires correctly, and a vague one ("helps with customer stuff") that either
  never loads or loads on everything — with a check and an X.

### slide 4.2 The failure modes of just-in-time loading

- **Description too vague** → the skill silently never loads when it was needed.
- **Description too broad** → the skill loads constantly, defeating the token savings.
- **Body assumes lost context** → instructions that reference state the agent no longer has once the
  skill loads mid-run.
- Each is a *design* failure in the skill, not a model failure — which is why authoring the
  description is the craft.

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
