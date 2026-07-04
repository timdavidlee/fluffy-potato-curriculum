# L23: Teacher-led demos — Skill patterns & composition

> Sibling docs: [objectives.md](objectives.md) (what the lesson aims for), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md).
>
> **Audience for this file:** the teacher running L23. Every demo below is *teacher-driven, no student participation*. Student-driven exercises live in the L23 labs (separate file, stage 2).
>
> **Anchor model for the demos: Claude Sonnet 4.6** (matches [L22](../L22/objectives.md)). L23 is the **composition capstone of the skills thread**; it is *not* framed as the end of the mini curriculum — the closing/retrospective is `MINI_WRAPUP.md` at the `lessons/` root (see [objectives.md](objectives.md)).

## How to read this file

Each demo is a self-contained block with:

- **Goal** — the single insight the demo should land. Tied to a learning objective from [objectives.md](objectives.md).
- **Pre-flight** — what the teacher needs loaded before the demo.
- **Live script** — the order of operations during the demo. Treat it as a checklist, not a teleprompter.
- **What to highlight** — the moment(s) where the teacher should slow down and say the takeaway out loud.
- **If the demo misbehaves** — graceful fallback for when the model (or a live edit) surprises you.

The demos are ordered to match the five learning objectives. Demo 1 lands the **archetypes** (classify three real skills). Demo 2 shows **the archetype dictates the authoring** (the body shape follows the archetype). Demo 3 shows **sequential handoff** on the repo's own two-stage flow and names the **seam contract**. Demo 4 adds a **shared lower-level skill**, draws the **dependency graph**, and shows **JIT loading across it**. Demo 5 walks the **three anti-patterns**. Run them in order on first delivery — each builds on the prior.

**The through-line:** unlike L22, which could demo on invented skills, L23 demos on the **real skill system this curriculum is authored from** — `.claude/skills/` (`author-lesson-roadmap`, `generate-materials-from-roadmap`, `sync-lesson-numbering`) and the `.claude/rules/*.md` guidance files. Composition is not hypothetical here; students are watching the machine that built their course. Say that out loud early.

## Pre-flight (once, at the top of the lesson)

The teacher should have, before the first demo:

- **The repo's real skills open in an editor**, ready to read on screen:
  - `.claude/skills/author-lesson-roadmap/SKILL.md` — the **operating-model runbook** archetype (read docs in order → draft → cross-check → report).
  - `.claude/skills/generate-materials-from-roadmap/SKILL.md` — the downstream half of the **sequential handoff**.
  - `.claude/skills/sync-lesson-numbering/SKILL.md` — a supporting/utility skill (candidate shared node).
  - `.claude/rules/python-style.md`, `.claude/rules/pytest.md` — real **review/rubric (principle-centric)** content the project applies as judgment. <!-- *NEED INPUT*: the rules files are referenced *by* CLAUDE.md rather than packaged as `SKILL.md` files. Confirm it's fair to present them as the "rubric archetype" worked example (they're real, on-disk, principle-centric guidance the agents in this repo actually apply) even though they aren't frontmatter-wrapped skills. Recommendation: yes — call them "rubric-style guidance" and note that packaging them as a `SKILL.md` with a discriminating description is exactly Demo 2's authoring exercise. -->
- **The LangGraph skill-loading agent**: the **[L04](../L04/objectives.md)/[L11](../L11/objectives.md) LangGraph agent** (Sonnet 4.6) extended with two **LangChain tools** that implement JIT loading — **`list_skills()`** returns every registered skill's `{name, description}` (discovery), and **`load_skill(name)`** reads that skill's full `SKILL.md` body into context (load). The model **calls `list_skills` to see what's available, then `load_skill` to pull the one it needs.** This is L22's JIT mechanism realized *as agent tools* on the agent students built in L11 — not a hand-rolled loader. L23 runs the agent live only where the model actually *selects* a skill (Demo 4's JIT-across-the-graph, Demo 5's description collisions); Demos 1–3 are mostly *reading and graphing real skills*. <!-- DECIDED (2026-07-01): runtime = the L04/L11 LangGraph agent with `list_skills` + `load_skill` LangChain tools (Sonnet 4.6), not L22's hand-rolled loader. L22 hand-rolls to demystify; L23 does it 'properly' as tools, which also makes each dependency-graph edge concrete (an edge = one skill's body calling `load_skill` on another). No new runtime dependency beyond LangGraph, in use since L04. -->
- **A token/context readout** — the L12 trace (or the shared Langfuse instance) showing tokens-per-call and what's in context, so "N descriptions always-on vs. bodies loaded along the path" is *visible in numbers* (reused from L22's setup).
- **A drawing surface** (whiteboard or a slide) for the **dependency graph** in Demo 4 — nodes = skills, edges = "invokes / hands off to."
- **Two prepared "bad" skills** for Demo 5's anti-patterns:
  - A pair with **colliding descriptions** (two skills whose descriptions overlap enough that the model picks wrong).
  - A **fake "shared skill"** that is really a deterministic script-with-a-one-line-wrapper (the "shared skill that's really a tool" anti-pattern).
  <!-- *NEED INPUT*: confirm the anti-pattern demo material — a colliding-description pair + a shared-skill-that's-really-a-tool stub + a hand-drawn over-chained pipeline. Recommendation: keep over-chaining as a *drawn* example (a 5-hop chain vs. a 2-step skill) rather than a runnable one; it's a design smell best shown on the graph, not executed. -->

> Why host on the repo's own skills: L23 is about *composition in the real world*, and the strongest possible evidence is the skill system the students' own course is built from. Inventing toy skills would forfeit that. Reserve any live agent runs for the two demos where model-driven *selection* is the actual point.

## Demo 1 — Three skills, three archetypes (Objective 1)

**Goal:** land the three **archetypes** from [objectives.md](objectives.md) — **script-centric (API/integration recipe)**, **principle-centric (review/rubric)**, **procedure-centric (operating-model runbook)** — by classifying *real* skills on screen. The payoff: the archetype tells you **where the content lives**.

**Pre-flight:**

- The four files open (the three `SKILL.md`s + a `.claude/rules/*.md`).

**Live script:**

1. Open `author-lesson-roadmap/SKILL.md`. Read its shape aloud: a numbered, ordered **procedure** (read these docs in order → draft → cross-check → report). Name it: **operating-model runbook** — center of gravity is the *ordered procedure*.
2. Open `python-style.md` (or `pytest.md`). It's a **list of rules/principles** the agent applies as judgment — no single deterministic output, no script that could replace it. Name it: **review/rubric** — center of gravity is the *rule list*.
3. Sketch (or open, if one exists) a **script-centric** skill: a thin markdown wrapper whose real work is a bundled script — "to do X, run `foo.py` and parse its output." Name it: **API/integration recipe** — center of gravity is the *script*. <!-- *NEED INPUT*: the repo doesn't ship a purely script-centric `.claude/skills/` example today. Options: (a) point at a hypothetical `get_order.py`-style wrapper drawn on a slide, or (b) treat one of `sync-lesson-numbering`'s deterministic steps as the script-centric illustration. Recommendation: draw a small `get_order`-style example so the archetype is clean and unambiguous; note that real skills often *embed* a script step rather than being purely script-centric. -->
4. Put the three side by side and state the discriminator: **the archetype tells you where the content belongs** — a *script* (determinism), a *rule list* (judgment/standards), or an *ordered procedure* (do-the-steps-in-order).

**What to highlight:**

- These are **real** skills — the course you're taking is authored from them. Archetypes are a working vocabulary, not a taxonomy exercise.
- Archetypes are a **spotting heuristic for the primary shape**, not rigid boxes — a runbook can *call* a script for one step; a review skill can *end* by running a formatter. Classify to guide authoring, not to file paperwork.
- One-line aside (don't dwell): a fourth **reference/knowledge** shape exists — a skill whose body is just *facts to read* (a small glossary/schema). It's the cheap right answer for a handful of terms; RAG (L21, full course) is for when the knowledge outgrows in-context. Not one of the three you'll author today. Frame all four as "which of *instructions / scripts / resources* is the center of gravity."

**If the demo misbehaves:**

- If students argue a skill is "two archetypes at once" — good. Use it to make the "primary shape / borrows from others" point rather than forcing one label.

## Demo 2 — The archetype dictates the authoring (Objective 2)

**Goal:** show that **the same `SKILL.md` format takes a different body shape per archetype**, and that writing the wrong shape (prose where a script belongs, a linear procedure where a rubric belongs) is the archetype-level version of L22's "wrong container" mistake.

**Pre-flight:**

- An empty `SKILL.md` to fill in live, plus the three real examples from Demo 1 as references.

**Live script:**

1. **Script-centric, done right:** author a thin wrapper — a discriminating `description` (the trigger, straight from [L22](../L22/objectives.md)), a one-line "when to run it," the *exact invocation*, and how to read the output. Say the rule: **the deterministic logic lives in the script, not the markdown.**
2. **Rubric, done right:** author an explicit, *scannable* list of rules with just enough example to apply each — written as **judgment criteria, not a linear procedure**. Contrast with #1: no single "run this and you're done."
3. **Runbook, done right:** author numbered, imperative, self-contained steps with explicit decision points and a clear done-condition — written *for an agent to follow*, deterministic sub-steps delegated to scripts. Point back at `author-lesson-roadmap` as the real instance.
4. **The anti-move (preview of Demo 5):** briefly show a runbook that *prose-describes* a deterministic step instead of scripting it — verbose, unreliable — and a rubric mis-written as a rigid linear procedure. State: the format is the same; the *shape* must follow the archetype.

**What to highlight:**

- Every archetype still needs L22's **discriminating description** — but now across a *set* of skills, descriptions must stay **mutually distinct** (setup for Demo 5's collisions).
- The craft L22 taught for one skill (description-as-trigger, instructions-for-an-agent) is assumed; L23 adds *"shape the body to the archetype."*

**If the demo misbehaves:**

- If live-authoring runs long, paste a prepared version of any two archetypes and author only the third live. The contrast between shapes is the point, not the typing.

## Demo 3 — Sequential handoff: the repo's own two-stage flow (Objective 3)

**Goal:** show **sequential handoff (A → B)** on a real pipeline, and name the **seam / handoff contract** — the artifact the upstream skill must produce for the downstream to work.

**Pre-flight:**

- Both `author-lesson-roadmap/SKILL.md` and `generate-materials-from-roadmap/SKILL.md` open. The `docs/origin/lesson_roadmaps/L<NN>/` directory shown as the artifact that passes between them.

**Live script:**

1. Read the two skills' descriptions back to back. `author-lesson-roadmap` = *stage 1: write the roadmap docs* (`objectives.md`, `demos_or_activities.md`). `generate-materials-from-roadmap` = *stage 2: generate student materials from those docs*. Say it: **stage 1's output is stage 2's input.** That's a handoff.
2. Point at the **seam contract** concretely: the roadmap `.md` files under `docs/origin/lesson_roadmaps/L<NN>/` *are* the contract — stage 2 can only run because stage 1 produced them in an agreed shape/location. Open the actual L22 (or L23) roadmap dir as the artifact-in-transit. (Meta-moment: *this very lesson* was produced by stage 1; the students are looking at the handoff that built their course.)
3. Ask the design question aloud and answer it: **why two skills instead of one mega-skill?** Each half is *separately loadable* (JIT-loaded only for the stage you're in), *separately testable*, and *separately re-runnable* (regenerate materials without re-drafting the roadmap).
4. Draw the two-node chain: `author-lesson-roadmap` → *(roadmap docs)* → `generate-materials-from-roadmap`. This is the seed of Demo 4's graph. Make the edge concrete on the runtime: at execution the agent runs stage 1, and stage 1's body ends by telling the agent to **`load_skill("generate-materials-from-roadmap")`** — the arrow *is* a `load_skill` call.

**What to highlight:**

- **The seam is the design.** A handoff is worth it *only* when the boundary is a real, stable contract (a well-defined artifact) — that's what buys separate loading/testing/re-running. A handoff added for tidiness, with a fuzzy seam, is just **over-chaining** (Demo 5).
- The handoff is *not* automatic control flow — each hop is still a model-driven `list_skills`→`load_skill` selection when the stage becomes relevant, and it can miss.

**If the demo misbehaves:**

- If the two-stage flow is too abstract on the page, run stage 1 for a throwaway lesson number to *produce* a roadmap doc, then point at that fresh artifact as "the thing stage 2 would consume." Keep it short — the artifact, not a full generation, is the point.

## Demo 4 — Shared lower-level skill, the dependency graph & JIT across it (Objectives 3 & 4)

**Goal:** add the second composition shape — a **shared lower-level skill (A → C ← B)** — draw the resulting **skill dependency graph**, and show **JIT loading across the graph**: only skills on the path taken load; a shared skill loads *per use*, not per caller; the always-on cost is still just every skill's name+description.

**Pre-flight:**

- A shared-skill candidate. Best real candidate: a small skill both operating skills would call — e.g. a **lesson-link/numbering check** that both `author-lesson-roadmap` (validating cross-refs in a roadmap) and `generate-materials-from-roadmap` (validating cross-refs in generated materials) could invoke, rather than each re-implementing it. `sync-lesson-numbering` is the nearest real relative. <!-- *NEED INPUT*: confirm the shared-sub-skill example. Real candidate: a `check-lesson-links` / numbering-validation skill invoked by *both* stages (write-once, reuse-many). `sync-lesson-numbering` exists and is close but is more a standalone maintenance runbook than a shared sub-skill. Recommendation: introduce a small illustrative `check-lesson-links` shared skill (drawn/prepared, need not be fully implemented) so the fan-in shape is unambiguous, and name `sync-lesson-numbering` as the real cousin. -->
- The L04/L11 LangGraph agent with `list_skills`/`load_skill` and all skills registered. Token readout visible.

**Live script:**

1. Introduce the shared skill `C` and show that *two* operating skills (`A` = author-roadmap, `B` = generate-materials) both invoke it. Contrast the two shapes explicitly: Demo 3 was **A → B** (output-to-input, a *pipeline*); this is **A → C ← B** (two callers, one *dependency*). On the runtime, both `A`'s body and `B`'s body call **`load_skill("C")`**.
2. **Draw the full dependency graph** on the board: nodes = skills, edges = **`load_skill` calls**. Identify the pieces by name — a *pipeline* (A→B), a *fan-in / shared node* (C), and *leaves* (the scripts a skill runs). Say it plainly: the graph is the map of possible `load_skill` calls; `list_skills` is how the agent discovers what it *could* call.
3. **JIT across the graph, in numbers:** show what's actually always-on — just the **two tool schemas** (`list_skills`, `load_skill`), *not* the skills. Pose a task; watch the agent call **`list_skills`** (all `{name, description}` surface for that turn), pick one, call **`load_skill`** (one body loads), and — for the handoff or the shared dependency — call `load_skill` again for the next node. Only skills on the path taken load their bodies; the shared skill `C` loads **per use**, not baked in per caller. Contrast with L22, where the name+description layer sat always-on: routing discovery through `list_skills` pushes even *that* to just-in-time.
4. **Depth costs loads:** point out that each hop (a handoff, or a level of sub-skill nesting) is an extra load and often an extra model turn. Say the trade-off out loud: **wide-and-shallow** graphs (many independent skills, few hops) load cheaply and fail locally; **deep chains** concentrate risk — a miss anywhere breaks the pipeline. (This is the setup for *over-chaining* in Demo 5.)

**What to highlight:**

- The graph is a **map of possible `load_skill` calls, not guaranteed control flow** — every edge is a model-driven `list_skills`→`load_skill` *selection* that can miss. (Common confusion from [objectives.md](objectives.md).)
- The always-on cost is **two tool schemas, no matter how many skills or the shape**; discovery (`list_skills`) and bodies (`load_skill`) are paid only along the path actually taken. This is L07's "tools cost tokens twice over," now managed across a whole system — and a step *sharper* than L22, which kept all descriptions always-on.
- One-line forward pointers (don't teach): keeping a long-running agent's context lean across many loads is L19 (context management, full course); orchestrating whole *agents* this way is [L24](../L24/objectives.md).

**If the demo misbehaves:**

- If token deltas are undramatic with small skill bodies, use one shared skill with a genuinely long body so "loaded once, only when on the path" is obvious on the readout (same trick as L22's Demo 3).
- If the model loads a skill *off* the expected path, that's Demo 5's description-collision lesson early — flag it and carry it forward.

## Demo 5 — The three composition anti-patterns (Objective 5)

**Goal:** name and *show* the three ways composition silently makes things worse — **over-chaining**, **a shared "skill" that's really a tool**, and **description collisions** — and tie each back to the payoff: a skill *system* is a win only when it's cheaper to run and easier to reason about than the monolith it replaced.

**Pre-flight:**

- The Demo 4 graph still on the board.
- The prepared colliding-description pair and the fake "shared skill that's really a tool" stub. A drawn 5-hop over-chained pipeline next to an equivalent 2-step skill.

**Live script:**

1. **Over-chaining (shown on the graph):** put the 5-hop chain next to the 2-step version that does the same work. Count the extra loads/turns and the extra places selection can miss. State the cure: **collapse hops** — a handoff should exist because the seam is a real reusable/testable boundary (Demo 3), not for tidiness.
2. **A shared "skill" that's really a tool:** open the fake shared skill — a deterministic operation with structured I/O that every caller invokes the same way, wrapped in a one-line "run this" markdown. Apply L08/L22's discriminator: *is the model **reading** judgment, or **calling** a deterministic op with a schema?* It's the latter → it's a **tool**, not a skill. Cure: make it a tool (or let the script be the interface) and drop the skill wrapper.
3. **Description collisions (run it):** register the colliding pair so both surface in `list_skills`; pose a task both descriptions plausibly match. Watch the agent `load_skill` the wrong one or dither. Make the point: collisions degrade the `list_skills`→`load_skill` selection **across the whole set**, not just the colliding pair. Cure: rewrite descriptions to be **mutually discriminating** — each says what it's for *and implicitly what it's not*. Re-run → correct selection.
4. Close by tying all three to the payoff line: composition earns its keep only when the system beats the monolith on cost *and* clarity. These are the three ways it silently doesn't.

**What to highlight:**

- The anti-patterns map to the two good moves inverted: over-chaining is *handoff without a real seam*; the fake shared skill is *reuse of the wrong container*; collisions are *L22's description-as-trigger failure, scaled to a set*.
- "A shared skill that's really a tool" is the **one place L23 deliberately re-invokes L22's skill-vs-tool line** — so name L22 explicitly.

**If the demo misbehaves:**

- If the colliding descriptions *don't* cause a wrong pick on Sonnet 4.6 (it's capable), make them collide harder, or point out that a *smaller/cheaper* model would fail sooner — selection robustness degrades with model power and with set size (callback to the anchor-model note in [objectives.md](objectives.md)).

## Optional bridge demo — from skills-that-call-skills to agents-that-call-agents (L24, full course only)

For the full-course track only ([L24](../L24/objectives.md) follows): one line and a sketch — redraw the Demo 4 dependency graph, then relabel the nodes from *skills* to *subagents*. Sequential handoff → a subagent **pipeline**; the shared sub-skill → a shared **worker**; the dependency graph → the **supervisor/worker** orchestration graph; and the three anti-patterns transfer (over-chaining → too-many-subagents; shared-skill-that's-really-a-tool → subagent-that-should've-been-a-tool-call). Don't build a multi-agent system — just land that L24 is "the same composition lens, scaled from skills to whole agents."

Skip in the mini cut (no L24). In the mini cut, the closing recap is `MINI_WRAPUP.md` at the `lessons/` root, **not** this lesson (see [objectives.md](objectives.md)).

## Pacing notes for the teacher

- **Per-demo time:** Demo 1 (classify real skills) 12–15 min. Demo 2 (author per archetype) 15–20, the biggest live-authoring block. Demo 3 (sequential handoff) 12–15. Demo 4 (shared skill + graph + JIT) is the centerpiece, 18–25 (drawing + token readout). Demo 5 (anti-patterns) 12–18. Optional bridge 3–5. Total ~75–100 minutes plus discussion. <!-- *NEED INPUT*: confirm against the duration in [objectives.md](objectives.md) once pinned (best guess there is 90–120 min, with a possible split into "archetypes & authoring" and "composition, the graph & anti-patterns"). If split, Demos 1–2 are lecture A and Demos 3–5 are lecture B. -->
- **Live-coding budget:** only Demo 2 (authoring) and the model-selection moments in Demos 4–5 need live work; Demos 1 and 3 are mostly *reading and graphing real skills*. Keep prepared versions of each archetype and the bad-skill stubs to paste. Keep the `list_skills`/`load_skill` tool plumbing **prepared** — don't live-code it; the point is composition, not the tools' wiring.
- **Variance budget:** skill *selection* is model-driven and non-deterministic — budget a re-run for Demo 4 (path selection) and Demo 5 (collisions), where "which skill does the agent `load_skill`?" is the whole point.
- **Build on L04/L11, not L22's loader:** the runtime is the LangGraph agent from L04/L11 plus two small tools (`list_skills`, `load_skill`); L22's hand-rolled loader was the demystifying version and is *not* reused here. L23 spends its time on *composition*, not on re-deriving the loading mechanism.
- **The audience watches, doesn't participate.** Resist "what archetype is this?" or "where should this handoff split?" as group questions — those are lab patterns (stage 2). Hands-on classification, authoring, and graphing are for the L23 labs.

## Open authoring questions

- <!-- *NEED INPUT*: confirm the demos host on the repo's real `.claude/skills/` as the worked example (author-lesson-roadmap → generate-materials-from-roadmap for the handoff; the `.claude/rules/*.md` as the rubric archetype; sync-lesson-numbering as the shared-node cousin), running on the L04/L11 LangGraph agent with `list_skills` + `load_skill` LangChain tools only for the model-selection demos. This mirrors the objectives.md open question and needs no new runtime dependency beyond LangGraph. -->
- <!-- *NEED INPUT*: the repo lacks a purely *script-centric* skill and a clean *shared lower-level* skill today. Demos 1 and 4 currently fill those with small drawn/prepared examples (a `get_order`-style wrapper; a `check-lesson-links` shared skill). Confirm whether stage 2 should *build* these as real example skills under `.claude/skills/` (so the lesson is fully live) or keep them as illustrative sketches. Recommendation: build a minimal real pair in stage 2 so every archetype and both composition shapes have an on-disk instance. -->
- **Anchor model:** Claude **Sonnet 4.6** (matches [L22](../L22/objectives.md) and course precedent). Note for Demo 5: a *larger* skill set and a *smaller* model both make description collisions bite sooner — useful if a live collision won't reproduce on Sonnet.
- <!-- *NEED INPUT*: does the lab (stage 2) reuse the single skill each student authored in L22 as one node of an L23 system — growing it into a handoff or adding a shared sub-skill — so the capstone is "grow your one skill into a small system"? Mirrors the objectives.md open question. Recommendation: yes. -->
- <!-- DECIDED (2026-07-01): conditional/dispatch is NOT a taught pattern — punted to L24 as supervisory orchestration (agent-level routing). Keep it out of the demos; mention only as a one-line forward-pointer if a student raises it. -->
- <!-- *NEED INPUT*: overlap guardrail with L22 — Demos here must *reuse* L22's single-skill authoring, description-as-trigger, and JIT-loading as callbacks, not re-teach them. Confirm the boundary holds: L22 = author one skill well; L23 = classify archetypes + compose many. The "shared skill that's really a tool" anti-pattern (Demo 5) is the one intentional re-invocation of L22's skill-vs-tool line. -->
- <!-- *NEED INPUT*: overlap guardrail with L24 (full course only) — the optional bridge demo must only *forward-point* to agent composition (relabel the graph), never build a multi-agent system, so L24 isn't pre-empted. -->
