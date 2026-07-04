# L22: Skills — just-in-time capabilities for agents

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (lesson-plan row L22).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).
> Neighbors: in the full plan, L21 (RAG pipeline) precedes and L24 (Multi-agent / subagent architecture) follows (neither roadmap is written yet). **In the mini cut, L22 is the final lesson** — the previous taught lesson is [L11 Shallow agents in LangGraph](../L11/objectives.md), and L09 (MCP) is **not** in the mini cut.

## Where this lesson sits

By L22, students have built and reasoned about the full agent stack: prompting and structured output (L02), tools — what they are, how they're wired, and what they cost (L07, L08), the hand-rolled agent loop (L10), and the same loop expressed as a LangGraph workflow and agent (L04, L11). They have one nagging, unsolved problem from all of that: **everything the agent might need has to be in the context window all the time.** Every tool's schema is re-sent on every request (L07's "tools cost tokens, twice over"); every instruction the agent might need lives in the system prompt, paid for on every call whether it's relevant or not. Add enough tools and instructions and the context bloats, the model gets distracted, and cost climbs — for capability the agent uses only occasionally.

**A skill is the answer to that problem: a capability the agent loads *just in time*, only when it's relevant, instead of carrying it always-on.** Concretely, a skill is a small **markdown instruction file** (a name, a description of *when it applies*, a body of instructions, and optionally some supporting scripts/resources) that sits dormant until the agent decides it's needed. Only the skill's short name + description stay in context by default; the full instructions load when the model judges them relevant, and any bundled scripts run only when actually invoked. This is **progressive disclosure** — the same idea that lets a person keep a shelf of reference manuals without memorizing all of them.

This lesson is **concept-first, then tooled**, matching the rest of the course (L12 hand-builds a trace before Langfuse; L11 hand-builds the loop before LangGraph). Students first build a **minimal just-in-time skill loader** on the **LangGraph agent they already own** — the L11 `create_agent` shallow agent, handed the skill *catalog* (each skill's name + description) as its system prompt and a single `load_skill` tool. Only when the model picks a skill does `load_skill` read the full instruction body into context. The loop, routing, and message bookkeeping are `create_agent` freebies (L11), so the **new** thing students build is the skill mechanism — the catalog + the `load_skill` tool — not another hand-rolled loop. Once they've felt the mechanism, they meet the real thing — **Anthropic Agent Skills** (the same `SKILL.md`-style format this very curriculum is authored with, under `.claude/skills/`) — and recognize it as the production version of what they just built. **Decision (resolved): the loader is built on the L11 `create_agent` agent, not a from-scratch loop — L11 already replaced the hand-rolled loop, so re-deriving one here would be a regression; the "hand-roll then meet the product" spine is preserved because the *product reveal* is Agent Skills, not `create_agent`.** The token payoff stays visible by reading the run's returned `messages` (the L11 run-inspection idiom).

In the mini cut this is the **capstone**: it ties together tools (L07/L08), prompting (L02), and the agent loop (L10/L11) into the question "*where should a capability live?*" In the full plan it also sets up L24 (multi-agent), where a subagent is itself a kind of loadable capability.

## Prerequisites

Students arriving at L22 should already be able to:

- Write a system prompt and structured-output prompt, and reason about what belongs in the **system** message vs. the per-call **user** message (L02). A skill is a third place a capability can live, contrasted against the system prompt.
- Wire a tool to a model call, and explain that a tool's **schema is part of the prompt on every request** — tools cost tokens twice over, definition *and* result (L07, L08). This always-on cost is the exact problem skills address.
- Decide *when a tool is needed vs. model-alone* (L08). L22 extends that decision to *skill vs. tool vs. system-prompt content*.
- Run an agent loop that calls the model repeatedly (L10) or as a LangGraph graph (L11). A skill is something **that loop loads** — students need a working agent to attach skills to.
- Reason about token cost and the context window (L01). Just-in-time loading is a context-economics move; the payoff is measured in tokens kept out of the window.

L22 does **not** assume L09 (MCP), which is outside the mini cut — MCP is referenced only as "another way to package capability," with the full treatment pointed at L09 for the full-course track. <!-- *NEED INPUT*: in the full course L22 follows L09 (MCP) and can contrast skill-vs-tool-vs-MCP-vs-prompt as a four-way taxonomy; in the mini cut (no L09) it must stand on skill-vs-tool-vs-prompt only and name MCP as a forward/aside. Confirm the lesson is written to serve both — full taxonomy with MCP clearly flagged as "L09, full course." -->

## Learning objectives

By the end of L22, a student should be able to:

1. **Explain what a skill is and how it differs from a tool, a prompt, and (briefly) an MCP server.** Concretely:
   - Define a **skill**: a named, described, markdown-based bundle of *instructions* (and optionally scripts/resources) that an agent loads **on demand**, when the model judges it relevant — as opposed to being always present in context.
   - Place it precisely against the alternatives students already know, and reuse this taxonomy verbatim:
     - **Tool** — a function with a structured schema the model calls and gets a structured result back; its schema is **always in context** (L07). Good for *deterministic operations with structured I/O*.
     - **System-prompt content** — always-on instructions/persona; paid for on **every** call. Good for *always-true behavior*.
     - **Skill** — procedural know-how / a capability needed *sometimes*, loaded **just in time**; can carry helper scripts. Good for *occasionally-needed, possibly multi-step capabilities you don't want bloating every call*.
     - **MCP server** — a *portable packaging/transport* for tools across clients (L09, full course). Orthogonal to the skill/tool/prompt question: MCP is about *how a tool is shipped*, not *when knowledge is loaded*.
   - State the one-sentence discriminator: **a tool is something the model *calls*; a skill is something the model *reads*; the system prompt is something the model *always sees*.**

2. **Author a markdown skill** with instructions and supporting scripts. Concretely:
   - Write a skill as a markdown file with the parts that make just-in-time loading work: a **name**, a **description that states *when* the skill applies** (this is the trigger the model matches on — the most important and most-often-botched part), a **body of instructions** (the steps/know-how), and optional **supporting scripts or resources** the skill tells the agent to run or read.
   - Make the description *discriminating*: it must let the model decide relevance from the description alone, without loading the body. Practice writing descriptions that fire on the right inputs and stay quiet otherwise (the skill analogue of L08's "name and schema-design a tool").
   - Reference the project's own skills (e.g. `.claude/skills/author-lesson-roadmap/`) as a concrete, real-world example of the format — the curriculum students are using is itself built from skills.
   - Keep instructions written *for an agent to follow*, not for a human to read: imperative, unambiguous, self-contained, and pointing at scripts for anything deterministic rather than describing it in prose. <!-- *NEED INPUT*: pin the exact skill file format taught — Anthropic Agent Skills `SKILL.md` with YAML frontmatter (name, description) + markdown body, matching `.claude/skills/`. Confirm we teach that concrete format (so it transfers to Claude Code / the Agent SDK) vs. a generic made-up format. Recommendation: teach the real `SKILL.md` shape. -->

3. **Reason about just-in-time loading vs. always-on context.** Concretely:
   - Explain **progressive disclosure** as the mechanism: only the skill *name + description* are always in context (cheap); the *body* loads when the model selects the skill; *scripts/resources* load only when run. Contrast directly with a tool, whose **full schema is in every request** (L07) — ten tools is ten schemas on every call; ten skills is ten one-line descriptions.
   - Quantify the trade with the L01/L07 cost lens: estimate the tokens saved by keeping a rarely-used capability's instructions out of the window until needed, and name the cost you *do* pay (an extra model turn to load the skill, plus the risk the model fails to load a skill it needed).
   - Connect to context management broadly: skills are one tool for keeping a long-running agent's context lean; the general problem (window overflow, instruction loss, cost spiral) and its other techniques are L19's topic (Static system prompt vs. context management, full course) — name it as the bigger picture without re-teaching it.
   - Identify the failure modes of JIT loading: a description too vague to trigger (skill never loads when needed), too broad (skill loads constantly, defeating the savings), or instructions that assume context the agent no longer has.

4. **Decide when a capability belongs as a skill vs. a tool vs. system-prompt content.** Concretely:
   - Apply a decision heuristic to concrete cases and defend the call:
     - Deterministic operation, structured input/output, called mid-reasoning → **tool**.
     - Always-true behavior, persona, or a rule that must hold on every call → **system prompt**.
     - Multi-step procedure / domain know-how / a capability used only sometimes, especially if it bundles scripts → **skill**.
   - Recognize hybrids: a skill often *describes how to use* one or more tools; the two compose rather than compete. A skill can also tell the agent to run a script (deterministic) instead of reasoning through steps (cheap + reliable).
   - Name the anti-patterns: cramming occasionally-needed instructions into the system prompt (always-on cost), building a tool for something that's really procedural know-how (rigid, hard to express as a schema), or making a skill for a one-line always-true rule (just put it in the system prompt).

## What a skill is (vocabulary the lecture must establish)

Define these explicitly and reuse them verbatim through the labs:

- **Skill** — a named, described, markdown-based bundle of instructions (+ optional scripts) an agent loads *just in time*, when relevant.
- **Just-in-time (JIT) loading** — bringing a capability's full content into context only when it's needed, rather than always-on.
- **Progressive disclosure** — the layered visibility that makes JIT work: name+description always visible → body on selection → scripts on execution.
- **Description (the trigger)** — the line that tells the model *when* the skill applies; relevance is decided from this alone, so it's the load-bearing part of a skill.
- **Always-on context** — content present in every request (system prompt, tool schemas); the thing skills exist to keep small.
- **Skill vs. tool vs. system prompt** — *read on demand* vs. *called with a schema* vs. *always seen*. The lesson's core taxonomy.

## Main points the lecture should land

- **Skills solve the "everything is always in context" problem.** Tools and system prompts are always-on; skills are loaded on demand. After three lessons of paying for tool schemas and system prompts on every call, this is the relief valve. Open here.
- **A tool is *called*; a skill is *read*; the system prompt is *always seen*.** This one-liner is the whole taxonomy. Drill it until students can classify a capability on sight.
- **The description is the skill.** Whether a skill works is mostly whether its description makes the model load it at the right time and not otherwise. Like tool naming/schema design (L08), this is where the real skill-authoring craft lives.
- **Progressive disclosure is the mechanism, token economics is the payoff.** Name + description are cheap and always present; the expensive body loads only when chosen. This is how an agent can have *many* capabilities available without carrying all their instructions every call — directly attacking L07's "tools cost tokens twice over."
- **Skills compose with tools, they don't replace them.** A skill commonly explains *how to use* tools, or tells the agent to run a script. The question is never "skill or tool?" in isolation — it's "where does this particular capability belong?"
- **You built the mechanism before you met the product.** The JIT loader students build (a catalog + a `load_skill` tool on their L11 `create_agent`) *is* what Anthropic Agent Skills / Claude Code skills do for real (this curriculum is built from them). Building the mechanism yourself first means the real format reads as familiar, not magic — same payoff as trace→Langfuse and loop→LangGraph.

## Common student confusions to watch for

- *"A skill is just a tool."* No — a tool is *called* with a structured schema and is always in context; a skill is *read* on demand and is mostly absent from context until needed. Different mechanism, different cost profile.
- *"A skill is just a long system prompt."* No — a system prompt is paid for on every call; a skill is loaded only when relevant. The whole point is that it's *not* always-on.
- *"Skills are an Anthropic-only / Claude-Code-only thing I'll never build."* The *mechanism* (name+description visible, body loaded on demand) is general — students build a minimal one themselves. The `SKILL.md` format is one concrete instance of it.
- *"More skills is free."* Not quite — each skill still costs its name+description in always-on context, and a pile of overlapping descriptions makes the model's selection worse. Skills are cheap, not free; curate them.
- *"The model will figure out when to load a skill."* Only if the description tells it. A vague description means the skill silently never fires; an over-broad one means it fires constantly. The description is a design artifact, not an afterthought.
- *"Put the instructions in the system prompt to be safe."* That's the anti-pattern skills exist to fix — it pays always-on cost for sometimes-needed content and crowds the window.

## Bridge / capstone

**In the mini cut, L22 is the final lesson and serves as a capstone:** it reframes everything students built — tools (L07/L08), prompts (L02), the agent loop (L10) and its LangGraph form (L04/L11) — around the single question *"where should a capability live, and when should it be in context?"* A good closing exercise has students take a capability they added to their L11 agent and decide (and justify) whether it belongs as a tool, a skill, or system-prompt content.

**In the full plan, L22 bridges to L24 (Multi-agent / subagent architecture):** a subagent is itself a loadable, specialized capability, and the skill-vs-tool-vs-prompt "where does capability live" framing extends naturally to "when is a whole *subagent* the right container." It also leans on L09 (MCP) for the fuller capability-packaging taxonomy and L19 (context management) for the broader JIT-loading picture. <!-- *NEED INPUT*: confirm the dual framing — capstone in the mini cut (last lesson), bridge-to-L24 in the full course. When L24's roadmap is authored, frame a subagent as "capability as a whole agent," reusing L22's where-should-capability-live lens rather than re-introducing it. -->

## Open authoring questions

- <!-- *NEED INPUT*: estimated lecture duration — best guess 75–100 minutes including a live build of a minimal JIT skill loader and authoring one real `SKILL.md`. Could split into "what a skill is / the taxonomy" and "author a skill + JIT loading + where-does-capability-live". -->
- **Anchor model:** Claude **Sonnet 4.6** (inherits the course precedent). Skills are model-agnostic, but pin demos to Sonnet 4.6 for consistency; mention that smaller models may need more discriminating descriptions to select skills reliably.
- **Tooling for the hands-on (resolved): LangGraph-native.** The loader is built on the L11 `create_agent` shallow agent — its one tool is `load_skill`, its system prompt is the skill catalog — not a from-scratch loop. Then the lesson reveals a real `SKILL.md` under `.claude/skills/` as the production form. **No new runtime dependency**: `langchain` / `langgraph` are already present from L11, and the real-skills reveal just *reads* a shipped `.claude/skills/*/SKILL.md` (no `claude` CLI invocation needed). Runs fully offline on the scripted `FakeModel`, which already drives `create_agent` (see L11).
- <!-- *NEED INPUT*: exact skill file format — teach Anthropic Agent Skills `SKILL.md` (YAML frontmatter name+description + markdown body + optional bundled scripts), matching `.claude/skills/`. Confirm, and confirm whether the lab ships a runnable example skill (with a supporting script) or just authors the markdown. -->
- **Host agent (resolved): the L11 `create_agent` shallow agent.** Skills attach to the agent students already built, so the lesson reads as "add JIT capability to your agent," not a new toy. (The support-desk skills here use their own small demo tool surface via `load_skill`; the point is the *mechanism* on the same `create_agent` object, not reusing `calculator`/`lookup`/`flaky_fetch` specifically.)
- **Quantifying the token savings (resolved).** Two moves: (1) a back-of-envelope estimate — "all N skill bodies always-on" vs. "catalog + only the one body loaded" (the money slide); and (2) reconstruct the **context size before each model turn** from the agent's returned `messages` — the L11 run-inspection idiom — so the body's just-in-time arrival shows as a token jump on the turn it loads. A `rough_tokens` (~4 chars/token) helper keeps it offline and deterministic; no Langfuse dependency in the mini cut.
- <!-- *NEED INPUT*: overlap with L09 (MCP) and L19 (context management), both full-course-only. Confirm L22 names them as the fuller treatments (capability packaging; JIT/context-management at large) without re-teaching, and reads cleanly in the mini cut where neither exists. -->
- <!-- *NEED INPUT*: this is the only mini-cut lesson not anchored to one of the five core course objectives (it's "added by request", per the PRD mini-cut note). Confirm its depth target — a full ~2hr lesson, or a lighter capstone session — given it sits at the end of the compressed track. -->
