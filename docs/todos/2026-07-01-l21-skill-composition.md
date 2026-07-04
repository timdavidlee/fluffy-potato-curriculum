# 2026-07-01 — L23 (Skill patterns & composition) open items

Tracking list for the **L23 Skill patterns & composition** roadmap (stage-1 complete this session:
`objectives.md` + `demos_or_activities.md` under `docs/origin/lesson_roadmaps/L23/`). Each item notes
the doc + line it lives in and the in-doc recommendation. Resolve items here or migrate them into the
roadmap docs as decisions land. Line numbers drift as docs are edited — grep `NEED INPUT` in the two
L23 docs for the authoritative set.

> **Context:** L23 is the **composition capstone of the skills thread**, following [L22 Skills](../origin/lesson_roadmaps/L22/objectives.md).
> It is deliberately **not** framed as the end of the mini curriculum (see item 1). Runtime substrate
> was corrected this session from L22's hand-rolled loader to the **L04/L14 LangGraph agent + `list_skills`/`load_skill`
> LangChain tools** (item 2).

> **Headline:** none of these block taking L23 into stage 2 (`generate-materials-from-roadmap`). **Update
> 2026-07-04:** the confirm-the-default batch (**#5, #10–15**) was resolved and baked into the two L23
> roadmap docs as dated `DECIDED (2026-07-04)` markers, and **#9 (build real example skills + mock API) is
> now done** — the `example_skills/` pair is built, tested, and passing the gate. **All items are resolved
> or delegated** (only #8's cross-lesson spinoff remains, tracked in its own note). L23 is stage-2-ready.

---

## 🟡 Structural / cross-cutting — decide once

- [x] **1. End-of-mini-curriculum wrap-up doc — DECIDED (2026-07-01).** Two wrap-up docs live at the
      `lessons/` root, siblings of `SYLLABUS.md` / `tracks.toml`: **`MINI_WRAPUP.md`** (closes the mini
      cut) and **`FULL_WRAPUP.md`** (closes the full course). These — not any lesson roadmap — own the
      "end of course" framing. L23's docs now point at `MINI_WRAPUP.md` throughout. **Remaining actions:**
      (a) ~~author `MINI_WRAPUP.md` + `FULL_WRAPUP.md`~~ — **scaffolded** (heading-only skeletons at the
      `lessons/` root, 2026-07-01); still need content filled in once the tracks' lessons are generated
      (both carry `NEED INPUT` markers for granularity / add-back list / next-steps scope); (b) drop L22's
      stale "final lesson / capstone" self-framing when L22 is regenerated (L23 now follows it).
      *(resolved in objectives.md:5, :23, :96, :110, :123; demos_or_activities.md:7, :170)*
- [x] **2. Runtime substrate = LangGraph agent + `list_skills`/`load_skill` — DECIDED (2026-07-01).** The
      L04/L14 LangGraph agent (Sonnet 4.6) extended with two LangChain tools — `list_skills()` (discovery:
      all skills' `{name, description}`) and `load_skill(name)` (load: one skill's full body) — is the
      runtime, **not** L22's hand-rolled loader. L22 hand-rolls to demystify; L23 does it as real tools
      (same "hand-roll → real" spine as L11→Langfuse, L14→LangGraph). Makes dependency-graph edges concrete
      (edge = one skill's body calling `load_skill` on another). No new dep beyond LangGraph (in use since
      L04). *(resolved in objectives.md:19; demos_or_activities.md:32)*
- [x] **3. Teach the sharper cost model — DECIDED: yes, Option A (2026-07-01).** With `list_skills`,
      always-on cost is **two tool schemas** (not L22's "N descriptions"); the N descriptions become a
      per-`list_skills`-call cost, bodies load per-`load_skill` on the path taken. Taught explicitly as a
      *refinement of L22* (not a contradiction) — it's the payoff of the tool-based design from #2. Docs
      already frame it this way. *(resolved in objectives.md:65)*
- [x] **4. Anchor model — DECIDED: Sonnet 4.6 (2026-07-01).** Same baseline as L22 and the whole course
      (Haiku 4.5 remains the cheap-contrast model). Collision demo (Demo 5) is model-dependent — if it
      won't misfire on Sonnet, make descriptions collide harder or note a smaller model fails sooner
      (fallback already in the doc). *(objectives.md; demos_or_activities.md Demo 5 + pacing notes)*
- [x] **5. Lecture duration / split — DECIDED (2026-07-04).** Target **~90–120 min**, single session by
      default; **optional** split at the Demo 2/3 boundary into "archetypes & authoring" (Demos 1–2) and
      "composition, graph & anti-patterns" (Demos 3–5). As an "added by request" mini-cut lesson it need not
      carry retrospective weight (that's `MINI_WRAPUP.md`), so no padded ~2 hr session. *(resolved in
      objectives.md "Open authoring questions" duration + depth bullets; demos_or_activities.md pacing notes)*

## 🟢 Scope of what's taught — in-doc recommendation, safe to batch-accept

- [x] **6. Archetype labels — DECIDED (2026-07-01).** Three **core** archetypes taught + authored
      (script-centric / principle-centric / procedure-centric, matching the PRD). Added: (a) the
      **{instructions | scripts | resources} center-of-gravity** framing that explains *why* these are the
      shapes; (b) a fourth **reference/knowledge (resource-centric)** archetype as a taught **aside** — the
      cheap right tool for a handful of facts, with RAG (L21) as the escalation when knowledge outgrows
      in-context; (c) an **industry-term vocabulary mapping** (tool-wrapper / checklist / runbook / SOP /
      playbook-ambiguity, etc.) in the vocabulary section. *(objectives.md Objective 1 + vocabulary;
      demos_or_activities.md Demo 1)*
- [x] **7. Two composition patterns only — DECIDED (2026-07-01).** Teach *only* sequential handoff +
      shared lower-level skill (per PRD). **Conditional/dispatch is punted to L24** as supervisory
      orchestration (agent-level routing-to-one-of-N); L23 mentions it as a one-line forward-pointer only,
      not a taught pattern or demo. *(resolved in objectives.md Objective 3; demos_or_activities.md open
      questions)*
- [~] **8. Anti-pattern demo material — DELEGATED (2026-07-01).** L23's own anti-pattern demo (Demo 5:
      colliding-description pair run live + fake-shared-skill-that's-really-a-tool stub + a *drawn*
      over-chained 5-hop-vs-2-step pipeline) is **already specified** in the demos doc. The bigger effort —
      giving **every mini-cut lesson** a gotcha/anti-pattern demo, using L23 Demo 5 as the template — is
      spun out to its own cross-cutting tracker, to be handled in a **separate session**:
      **[2026-07-01-mini-cut-gotcha-antipattern-demos.md](2026-07-01-mini-cut-gotcha-antipattern-demos.md)**.
      *(demos_or_activities.md:38)*

## 🟠 Example material — repo gaps (impacts stage-2 build)

- [x] **9. Build real example skills — DONE (2026-07-04).** Built both archetype-gap examples as real,
      runnable, offline artifacts under `src/fluffy_potato_curriculum/lessons/L23/example_skills/`
      — **lesson-owned, deliberately kept out of the live `.claude/skills/` registry** (they're teaching
      material, not curriculum-authoring tools; the roadmap's earlier `.claude/skills/` wording was
      superseded by this location choice):
      - **script-centric** `get_order/` — a mock orders API (`get_order_api.py`) with a genuinely
        heterogeneous JSON contract (discriminated-union `payment`, per-item `options`, variable address
        list, optional `tracking`/`note`s) + a thin `SKILL.md` wrapper. The messy contract is the
        non-toy payoff: running the script beats re-deriving the shape each call.
      - **shared lower-level** `check_lesson_links/` — a mechanical `extract_links.py` helper + a
        `SKILL.md` that adds the *judgment* (broken ref vs. illustrative `L<NN>` forward-pointer vs.
        not-yet-generated sibling), so it's a shared skill and **not** the "shared skill that's really a
        tool" anti-pattern. Invoked by both operating skills (`A → C ← B`).
      Both have mirrored tests (`tests/lessons/L23/…`) and pass `ruff` + `pyright --strict` + `pytest`
      (26 tests). Bonus: `check_lesson_links`'s first live run found **three off-by-one broken links** in
      `objectives.md` (`../../../` → `../../../../` for `.claude/rules/` and `src/…SYLLABUS.md`), now fixed.
      *(resolved in demos_or_activities.md Demo 1 step 3, Demo 4 pre-flight, open questions; example_skills/README.md)*
- [x] **10. Lean on the repo's own `.claude/skills/` — DECIDED (2026-07-04): heavily.** Worked examples are
      the real skills: `author-lesson-roadmap` → `generate-materials-from-roadmap` (sequential handoff),
      `.claude/rules/*.md` (rubric archetype), `sync-lesson-numbering` (shared-node cousin). *(resolved in
      objectives.md "Open authoring questions"; demos_or_activities.md open questions)*
- [x] **11. `.claude/rules/*.md` as the "rubric" archetype example — DECIDED (2026-07-04): yes.** Present the
      on-disk, principle-centric rules files as "rubric-style guidance" even though they're referenced by
      CLAUDE.md rather than frontmatter-wrapped; packaging one as a `SKILL.md` with a discriminating
      description is itself Demo 2's authoring exercise. *(resolved in demos_or_activities.md Demo 1 pre-flight)*

## 🔵 Lab continuity

- [x] **12. Grow the L22 skill — DECIDED (2026-07-04): yes.** The lab reuses each student's L22 skill as one
      node of the L23 system (a handoff or a shared sub-skill) — "grow your one skill into a small system,"
      not a fresh start. *(resolved in objectives.md "Open authoring questions"; demos_or_activities.md open questions)*
- [x] **13. Capstone deliverable = a skill *system* — DECIDED (2026-07-04): yes.** The deliverable is a small
      real skill system (≥1 handoff and/or shared sub-skill) that students author, graph, and self-audit for
      the three anti-patterns — not another single skill (that's what makes L23 a *composition* capstone
      distinct from L22's *authoring* one). *(resolved in objectives.md "Bridge / capstone")*

## ⚪ Overlap guardrails — confirm the boundary holds

- [x] **14. L22 boundary (reinforce, don't re-teach) — DECIDED (2026-07-04): boundary holds.** L22 owns
      single-skill authoring + skill/tool/prompt taxonomy + description-as-trigger + JIT loading; L23 reuses
      these as callbacks and builds on them (classify archetypes + compose many). The "shared skill that's
      really a tool" anti-pattern is the one intentional re-invocation of L22's skill-vs-tool line. *(resolved
      in objectives.md prerequisites + "Open authoring questions"; demos_or_activities.md open questions)*
- [x] **15. L24 on-ramp (forward-point only) — DECIDED (2026-07-04): boundary holds.** L23 draws the
      skills↔agents analogy (handoff → subagent pipeline; shared sub-skill → shared worker; dependency graph
      → supervisor/worker graph) but never builds a multi-agent system, so L24 isn't pre-empted. When L24's
      roadmap is authored it must reuse L23's composition vocabulary. *(resolved in objectives.md "Where this
      lesson sits" + bridge + "Open authoring questions"; demos_or_activities.md open questions)*
