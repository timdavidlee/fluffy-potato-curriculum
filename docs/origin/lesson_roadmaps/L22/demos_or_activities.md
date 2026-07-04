# L22: Teacher-led demos — Skills: just-in-time capabilities for agents

> Sibling docs: [objectives.md](objectives.md) (what the lesson aims for), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md).
>
> **Audience for this file:** the teacher running L22. Every demo below is *teacher-driven, no student participation*. Student-driven exercises live in the L22 labs (separate file, stage 2).
>
> **Anchor model for the demos: Claude Sonnet 4.6.** **In the mini cut this is the final lesson — a capstone.**

## How to read this file

Each demo is a self-contained block with:

- **Goal** — the single insight the demo should land. Tied to a learning objective from [objectives.md](objectives.md).
- **Pre-flight** — what the teacher needs loaded before class.
- **Live script** — the order of operations during the demo. Treat it as a checklist, not a teleprompter.
- **What to highlight** — the moment(s) where the teacher should slow down and say the takeaway out loud.
- **If the demo misbehaves** — graceful fallback for when the model surprises you (it will).

The demos are ordered to match the four learning objectives. Demo 1 lands the taxonomy (tool vs. skill vs. system prompt); Demo 2 authors a skill and shows the description *is* the trigger; Demo 3 shows just-in-time loading and the token payoff; Demo 4 applies the where-does-capability-live decision. The optional capstone demo reveals the real Anthropic Agent Skills format as "what you just hand-built, productized." Run them in order on first delivery — each builds on the prior.

## Pre-flight (once, at the top of the lesson)

The teacher should have, before the first demo:

- **The L11 shallow agent** (the LangGraph agent students built) running on Sonnet 4.6, with the shared tools from `common/tools.py` (`calculator`, `lookup`, `flaky_fetch`). Skills attach to *this* agent — the message is "add just-in-time capability to the agent you already built," not a new toy. <!-- *NEED INPUT*: confirm the demos host on the L11 shallow agent (vs. the L10 hand-rolled loop). Recommendation: L11, so the lesson reads as the capstone of the agent the students just finished. -->
- **A context/token readout** — the L12 trace (or the shared Langfuse instance) showing tokens-per-call and what's in the context window, so "always-on vs. just-in-time" is *visible in numbers*, not asserted.
- **A minimal hand-rolled JIT skill loader**: the agent is handed a registry of skills as `{name, description}` only; a `load_skill(name)` step reads the *full* markdown body into context, and the model is told to call it when a skill's description matches the task. The teacher writes the core of this live in Demo 3; keep a completed version in a sibling file to paste if live-coding falls behind. <!-- *NEED INPUT*: tooling — hand-rolled JIT loader for the concept (no new dep), then a real `.claude/skills/` `SKILL.md` for the "production" reveal (uses the already-present `claude` tooling). Mirrors the objectives open question; confirm no new runtime dep is needed. -->
- **Two prepared skills as markdown files** (Anthropic Agent Skills `SKILL.md` shape — YAML frontmatter `name` + `description`, markdown body, optional bundled script):
  - A **good** skill, e.g. `refund-policy` — description that clearly states *when* it applies, a body of step-by-step instructions, and a tiny supporting script (e.g. compute a refund amount) the skill tells the agent to run.
  - A **deliberately vague** copy of the same skill whose description is too generic to trigger reliably (used in Demo 2 to show the failure).
  <!-- *NEED INPUT*: confirm the exact `SKILL.md` format taught (frontmatter name+description + body + optional scripts, matching `.claude/skills/`) and whether the demo skill ships a runnable script or is instructions-only. Mirrors the objectives open question. -->
- **One real skill from this repo** open in an editor — e.g. `.claude/skills/author-lesson-roadmap/` — as the production reference for the capstone demo. (Meta-note worth saying out loud: the curriculum students are taking is itself built from skills.)

> Why host on the existing agent: L22 is about *where capability lives*, not about building an agent. Re-deriving an agent mid-demo wastes the capstone. Spend the time on the skill/tool/prompt contrast and the JIT mechanism, which *are* the point.

## Demo 1 — The same capability, three ways (Objective 1)

**Goal:** land the taxonomy from [objectives.md](objectives.md): **a tool is *called*, a skill is *read* on demand, the system prompt is *always seen*.** Make the always-on cost of tools and system prompts visceral before skills are introduced as the fix.

**Pre-flight:**

- One capability to express three ways — e.g. *"draft a support reply that follows company refund policy."*
- The token readout visible.

**Live script:**

1. **As system-prompt content:** paste the full refund-policy instructions into the agent's system prompt. Run a task that *doesn't* need refunds (e.g. a calculator question). Show the policy text sitting in the context window, paid for, on a call that never used it. Read the token count.
2. **As a tool:** sketch the same capability as a tool with a schema. Note the awkwardness — procedural "how to phrase a refusal" know-how doesn't fit a structured input/output cleanly — and that the tool *definition* is in every request regardless (callback to L07's "tools cost tokens twice over").
3. **As a skill:** show the same instructions as a `SKILL.md` sitting on disk, *not* in context — only its one-line description is registered. Run the non-refund task again: the skill never loads, context stays lean. Run a refund task: the skill loads, the agent follows it.
4. Put the three side by side and say the discriminator: **called vs. read vs. always-seen.**

**What to highlight:**

- The system prompt and the tool schema are paid for on *every* call; the skill body is paid for only when relevant. That difference is the whole lesson.
- "Procedural know-how" is an awkward fit for a tool's schema but a natural fit for a skill's markdown body.

**If the demo misbehaves:**

- If the model answers the refund task *without* loading the skill, that's the Demo 2 lesson early — note it and tighten the description, or strengthen the loader's instruction to consult skills first.

## Demo 2 — Author a skill; the description is the trigger (Objective 2)

**Goal:** write a real skill live, and prove that **whether a skill works is mostly whether its description makes the model load it at the right time.**

**Pre-flight:**

- An empty `SKILL.md` to fill in live, plus the prepared good/vague pair as backup.
- A task that should trigger the skill and one that should not.

**Live script:**

1. Live-author a `SKILL.md`: `name`, a **description that states *when* it applies**, a body of imperative instructions, and a pointer to a supporting script for the deterministic part (e.g. "run `refund_amount.py` to compute the figure"). Narrate each part.
2. Register it and run the triggering task → skill loads → correct, policy-following answer (and the script runs for the number).
3. Swap in the **vague-description** version ("helps with customer stuff"). Re-run the triggering task → the model fails to load it (silent miss) or loads it on the wrong inputs. Show the miss in the trace.
4. Tighten the description back to something discriminating → it fires correctly again.

**What to highlight:**

- The description is a *design artifact*, not a label — it's the skill analogue of L08's tool naming/schema design. This is where skill-authoring craft lives.
- Instructions are written *for an agent to follow* (imperative, self-contained), and deterministic steps are pushed into a script rather than described in prose.

**If the demo misbehaves:**

- If even the tightened description won't fire reliably on Sonnet, show the loader's skill list and point out competing/overlapping descriptions; prune them. Reliability of selection is itself a teachable failure mode.

## Demo 3 — Just-in-time loading and progressive disclosure (Objective 3)

**Goal:** show the *mechanism* (progressive disclosure) and the *payoff* (tokens kept out of the window), using the token readout.

**Pre-flight:**

- Five skills registered (the refund one plus four more stubs with distinct descriptions).
- The hand-rolled JIT loader (write its core live here).

**Live script:**

1. Live-code the loader's core: the agent sees only `{name, description}` for all five skills. Read the context token count — five one-line descriptions, cheap.
2. Pose a task matching one skill. Watch the model select it; the *body* loads into context for that turn only (token count jumps, then the contrast is clear); the *script* runs only when actually invoked. Narrate the three levels of disclosure: name+description → body → script.
3. **The money slide:** put "5 skills, JIT-loaded" next to "5 tools, all schemas always-on" and compare the always-on context size. This is L07's tool-cost problem, solved.
4. Name the costs you *do* pay: an extra model turn to load, and the risk the model fails to load a skill it needed (Demo 2's failure mode).

**What to highlight:**

- Progressive disclosure is *why* an agent can have many capabilities available without carrying all their instructions every call.
- Skills are **cheap, not free** — each still costs its description in always-on context, and overlapping descriptions degrade selection.
- Forward pointer (one line, don't teach it): keeping a long-running agent's context lean is the broader topic of L19 (context management, full course).

**If the demo misbehaves:**

- If the token deltas are undramatic with tiny skills, use one skill with a genuinely long body so the "loaded only when needed" saving is obvious on the readout.

## Demo 4 — Where does this capability live? (Objective 4)

**Goal:** apply the decision heuristic to concrete cases and show that **skills compose with tools rather than replace them.**

**Pre-flight:**

- A slide of 3–4 candidate capabilities, e.g.: (a) "compute sales tax" (b) "our brand voice / tone rules" (c) "the multi-step refund-handling procedure" (d) "look up an order by id."

**Live script:**

1. Classify each live, defending the call: (a) tax math → **tool** (deterministic, structured I/O); (b) always-true brand voice → **system prompt**; (c) multi-step procedure used sometimes → **skill**; (d) order lookup → **tool**.
2. Show **composition**: the refund *skill* (c) tells the agent to call the order-lookup *tool* (d) and the tax *tool* (a). A skill orchestrates tools; it doesn't compete with them.
3. Show a skill that pushes a deterministic step into a **script** rather than reasoning through it — cheaper and more reliable.
4. Name the anti-patterns out loud: occasionally-needed instructions crammed into the system prompt (always-on cost); a tool built for procedural know-how (rigid); a skill made for a one-line always-true rule (just use the system prompt).

**What to highlight:**

- The question is never "skill or tool?" in the abstract — it's "where does *this particular* capability belong?"
- Skills are the natural home for *orchestration* know-how ("to handle a refund, first look up the order, then…").

**If the demo misbehaves:**

- If students push back on a classification (good — it's a judgment call), use the disagreement to surface the heuristic's edges rather than insisting on one answer.

## Optional capstone demo — the real thing (Anthropic Agent Skills)

If time allows, close the loop: open a real skill from this repo (`.claude/skills/author-lesson-roadmap/`) and show that it's the *same* shape students just hand-built — frontmatter `name` + `description`, a markdown instruction body, supporting structure — loaded just-in-time by Claude Code. Punchline: **the JIT loader you wrote in Demo 3 is what the Agent SDK / Claude Code does for real; the curriculum you're taking is itself built from skills.**

Don't teach the SDK's mechanics — just land that the hand-rolled concept and the production product are the same idea, the way L12's hand-rolled trace mapped to Langfuse and L11's loop mapped to LangGraph.

<!-- *NEED INPUT*: include this capstone demo as the mini-cut closer, or hold the real-Agent-Skills reveal for a lab? Recommendation: include it — it's the satisfying "you built the real thing" capstone moment for the final mini-cut lesson. -->

## Optional bridge demo — toward multi-agent (L24, full course only)

For the full-course track only (L24 follows): one line and a sketch — a *subagent* is capability-as-a-whole-agent, the same "where should capability live" lens scaled up from a skill to an entire agent. Skip entirely in the mini cut, where L22 is the final lesson.

## Pacing notes for the teacher

- **Per-demo time:** Demo 1 is 10–15 minutes (three-way contrast). Demo 2 is 12–18 (live authoring). Demo 3 is the centerpiece, 15–20 (live loader + token readout). Demo 4 is 8–12. Capstone is 5–8. Total ~50–75 minutes plus discussion — fits a 75–100 minute block. <!-- *NEED INPUT*: confirm against the duration in [objectives.md](objectives.md) once pinned; also confirm depth target — full ~2hr lesson vs. lighter capstone, since L22 is the one mini-cut lesson not tied to a core objective. -->
- **Live-coding budget:** only Demo 3's JIT loader needs live-coding; Demos 1, 2, 4 reuse prepared skills + the loader. Keep a completed loader to paste.
- **Variance budget:** skill *selection* is model-driven and not deterministic — budget a re-run for Demos 2 and 3, where "does the model load the right skill?" is the whole point.
- **The audience watches, doesn't participate.** Resist "what should this be — tool or skill?" as a group question — that's a lab pattern. Hands-on classification is for the L22 labs.

## Open authoring questions

- <!-- *NEED INPUT*: tooling — hand-rolled JIT loader for the concept, then a real `.claude/skills/` `SKILL.md` for the production reveal. Confirm no new runtime dep is needed (the real-skills demo uses the already-present `claude` tooling). Mirrors the objectives open question. -->
- <!-- *NEED INPUT*: exact `SKILL.md` format (frontmatter name+description + markdown body + optional bundled scripts, matching `.claude/skills/`), and whether the demo skill ships a runnable supporting script or is instructions-only. Mirrors the objectives open question. -->
- <!-- *NEED INPUT*: confirm the demos host on the L11 shallow agent with the shared `common/tools.py` tools, for continuity with the rest of the mini cut. -->
- <!-- *NEED INPUT*: how to make the token-savings payoff vivid — read real counts off the L12 trace / Langfuse, or a prepared side-by-side slide? Recommendation: live trace numbers, with a slide as fallback. -->
- <!-- *NEED INPUT*: depth/duration target for this capstone lesson (full ~2hr vs. lighter), since it is the one mini-cut lesson "added by request" and not anchored to a core course objective. Mirrors the objectives open question. -->
- <!-- *NEED INPUT*: include the optional capstone (real Agent Skills) in the lecture, or move it to a lab? Recommendation: include it as the closer. -->
