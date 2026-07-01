# 2026-07-01 — L21 (Skill patterns & composition) open items

Tracking list for the **L21 Skill patterns & composition** roadmap (stage-1 complete this session:
`objectives.md` + `demos_or_activities.md` under `docs/origin/lesson_roadmaps/L21/`). Each item notes
the doc + line it lives in and the in-doc recommendation. Resolve items here or migrate them into the
roadmap docs as decisions land. Line numbers drift as docs are edited — grep `NEED INPUT` in the two
L21 docs for the authoritative set.

> **Context:** L21 is the **composition capstone of the skills thread**, following [L20 Skills](../origin/lesson_roadmaps/L20/objectives.md).
> It is deliberately **not** framed as the end of the mini curriculum (see item 1). Runtime substrate
> was corrected this session from L20's hand-rolled loader to the **L11/L12 LangGraph agent + `list_skills`/`load_skill`
> LangChain tools** (item 2).

> **Headline:** none of these block taking L21 into stage 2 (`generate-materials-from-roadmap`). Every
> item has an in-doc recommendation. The three worth a human decision before stage 2 are **#1 (wrap-up
> doc location), #3 (teach the sharper cost model?), #9 (build real example skills?)**; the rest are
> confirm-the-default.

---

## 🟡 Structural / cross-cutting — decide once

- [x] **1. End-of-mini-curriculum wrap-up doc — DECIDED (2026-07-01).** Two wrap-up docs live at the
      `lessons/` root, siblings of `SYLLABUS.md` / `tracks.toml`: **`MINI_WRAPUP.md`** (closes the mini
      cut) and **`FULL_WRAPUP.md`** (closes the full course). These — not any lesson roadmap — own the
      "end of course" framing. L21's docs now point at `MINI_WRAPUP.md` throughout. **Remaining actions:**
      (a) ~~author `MINI_WRAPUP.md` + `FULL_WRAPUP.md`~~ — **scaffolded** (heading-only skeletons at the
      `lessons/` root, 2026-07-01); still need content filled in once the tracks' lessons are generated
      (both carry `NEED INPUT` markers for granularity / add-back list / next-steps scope); (b) drop L20's
      stale "final lesson / capstone" self-framing when L20 is regenerated (L21 now follows it).
      *(resolved in objectives.md:5, :23, :96, :110, :123; demos_or_activities.md:7, :170)*
- [x] **2. Runtime substrate = LangGraph agent + `list_skills`/`load_skill` — DECIDED (2026-07-01).** The
      L11/L12 LangGraph agent (Sonnet 4.6) extended with two LangChain tools — `list_skills()` (discovery:
      all skills' `{name, description}`) and `load_skill(name)` (load: one skill's full body) — is the
      runtime, **not** L20's hand-rolled loader. L20 hand-rolls to demystify; L21 does it as real tools
      (same "hand-roll → real" spine as L08→Langfuse, L12→LangGraph). Makes dependency-graph edges concrete
      (edge = one skill's body calling `load_skill` on another). No new dep beyond LangGraph (in use since
      L11). *(resolved in objectives.md:19; demos_or_activities.md:32)*
- [x] **3. Teach the sharper cost model — DECIDED: yes, Option A (2026-07-01).** With `list_skills`,
      always-on cost is **two tool schemas** (not L20's "N descriptions"); the N descriptions become a
      per-`list_skills`-call cost, bodies load per-`load_skill` on the path taken. Taught explicitly as a
      *refinement of L20* (not a contradiction) — it's the payoff of the tool-based design from #2. Docs
      already frame it this way. *(resolved in objectives.md:65)*
- [x] **4. Anchor model — DECIDED: Sonnet 4.6 (2026-07-01).** Same baseline as L20 and the whole course
      (Haiku 4.5 remains the cheap-contrast model). Collision demo (Demo 5) is model-dependent — if it
      won't misfire on Sonnet, make descriptions collide harder or note a smaller model fails sooner
      (fallback already in the doc). *(objectives.md; demos_or_activities.md Demo 5 + pacing notes)*
- [ ] **5. Lecture duration / split.** Best guess **90–120 min**; optional split into "archetypes & authoring"
      (Demos 1–2) and "composition, graph & anti-patterns" (Demos 3–5). *(objectives.md:116; demos_or_activities.md:174)*

## 🟢 Scope of what's taught — in-doc recommendation, safe to batch-accept

- [x] **6. Archetype labels — DECIDED (2026-07-01).** Three **core** archetypes taught + authored
      (script-centric / principle-centric / procedure-centric, matching the PRD). Added: (a) the
      **{instructions | scripts | resources} center-of-gravity** framing that explains *why* these are the
      shapes; (b) a fourth **reference/knowledge (resource-centric)** archetype as a taught **aside** — the
      cheap right tool for a handful of facts, with RAG (L19) as the escalation when knowledge outgrows
      in-context; (c) an **industry-term vocabulary mapping** (tool-wrapper / checklist / runbook / SOP /
      playbook-ambiguity, etc.) in the vocabulary section. *(objectives.md Objective 1 + vocabulary;
      demos_or_activities.md Demo 1)*
- [x] **7. Two composition patterns only — DECIDED (2026-07-01).** Teach *only* sequential handoff +
      shared lower-level skill (per PRD). **Conditional/dispatch is punted to L22** as supervisory
      orchestration (agent-level routing-to-one-of-N); L21 mentions it as a one-line forward-pointer only,
      not a taught pattern or demo. *(resolved in objectives.md Objective 3; demos_or_activities.md open
      questions)*
- [~] **8. Anti-pattern demo material — DELEGATED (2026-07-01).** L21's own anti-pattern demo (Demo 5:
      colliding-description pair run live + fake-shared-skill-that's-really-a-tool stub + a *drawn*
      over-chained 5-hop-vs-2-step pipeline) is **already specified** in the demos doc. The bigger effort —
      giving **every mini-cut lesson** a gotcha/anti-pattern demo, using L21 Demo 5 as the template — is
      spun out to its own cross-cutting tracker, to be handled in a **separate session**:
      **[2026-07-01-mini-cut-gotcha-antipattern-demos.md](2026-07-01-mini-cut-gotcha-antipattern-demos.md)**.
      *(demos_or_activities.md:38)*

## 🟠 Example material — repo gaps (impacts stage-2 build)

- [ ] **9. Build real example skills — DIRECTION SET, needs follow-up (2026-07-01).** The repo has **no
      purely script-centric skill** and **no clean shared lower-level skill** today. **Decision so far:**
      to illustrate the *benefit* of complex skills convincingly, we'll build a **mock API with a
      genuinely complicated JSON contract** (nested/heterogeneous request+response) so the script-centric
      "API/integration recipe" archetype has a real, non-toy payoff — a skill that wraps the messy contract
      is clearly better than making the model reason through it each time. This is **deferred** — come back
      to design the mock API + the example skill pair (`get_order`-style wrapper + a `check-lesson-links`
      shared skill) before/at stage 2. *(demos_or_activities.md:54, :120, :183)*
- [ ] **10. Lean on the repo's own `.claude/skills/`** as the worked examples: `author-lesson-roadmap` →
      `generate-materials-from-roadmap` (real sequential handoff), `.claude/rules/*.md` (rubric archetype),
      `sync-lesson-numbering` (shared-node cousin). Rec: heavily. *(objectives.md:118; demos_or_activities.md:182)*
- [ ] **11. `.claude/rules/*.md` as the "rubric" archetype example** — they're referenced by CLAUDE.md, not
      frontmatter-wrapped `SKILL.md` files. OK to present as the rubric worked example (packaging one as a
      `SKILL.md` with a discriminating description is itself Demo 2's authoring exercise)? Rec: yes.
      *(demos_or_activities.md:31)*

## 🔵 Lab continuity

- [ ] **12. Grow the L20 skill.** Confirm the lab reuses each student's L20 skill as one node of the L21
      system (a handoff or a shared sub-skill) — "grow your one skill into a small system," not a fresh
      start. *(objectives.md:119; demos_or_activities.md:185)*
- [ ] **13. Capstone deliverable = a skill *system*.** Confirm the deliverable is a small real skill system
      (≥1 handoff and/or shared sub-skill) that students author, graph, and self-audit for the three
      anti-patterns — not another single skill (that's what makes L21 a *composition* capstone distinct
      from L20's *authoring* one). *(objectives.md:110)*

## ⚪ Overlap guardrails — confirm the boundary holds

- [ ] **14. L20 boundary (reinforce, don't re-teach).** L20 owns single-skill authoring +
      skill/tool/prompt taxonomy + description-as-trigger + JIT loading; L21 reuses these as callbacks and
      builds on them (classify archetypes + compose many). The "shared skill that's really a tool"
      anti-pattern is the one intentional re-invocation of L20's skill-vs-tool line.
      *(objectives.md:36, :121; demos_or_activities.md:187)*
- [ ] **15. L22 on-ramp (forward-point only).** L21 draws the skills↔agents analogy (handoff → subagent
      pipeline; shared sub-skill → shared worker; dependency graph → supervisor/worker graph) but never
      builds a multi-agent system, so L22 isn't pre-empted. When L22's roadmap is authored, it should reuse
      L21's composition vocabulary. *(objectives.md:23, :112, :122; demos_or_activities.md:188)*
