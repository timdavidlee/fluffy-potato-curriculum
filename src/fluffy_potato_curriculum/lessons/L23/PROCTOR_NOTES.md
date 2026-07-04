# L23 proctor notes — Skill patterns & composition

Teaching notes for whoever runs L23. One section per lab problem is at the bottom; read the
overview first.

## Lesson at a glance

L23 is the **composition capstone of the skills thread** — it turns the single skill students built
in L22 into a *system* of skills. Anchor model: **Claude Sonnet 4.6**. Roadmap:
[objectives.md](../../../../docs/origin/lesson_roadmaps/L23/objectives.md),
[demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L23/demos_or_activities.md).

Items, in teaching order:

| Item | File | What it does | ~min |
| --- | --- | --- | --- |
| 01 | `L2301_intro.md` | Framing: one skill → a system of skills | 8 |
| 02 | `L2302_lecture.md` | Slide outline — the three archetypes + authoring each (Demos 1–2) | 30 |
| 03 | `L2303_lab_*` | Lab — classify archetypes and author one (Obj 1–2) | 30 |
| 04 | `L2304_lecture.ipynb` | Notebook — handoff, shared skill, dependency graph & JIT (Demos 3–4) | 40 |
| 05 | `L2305_lecture.ipynb` | Notebook — the three anti-patterns (Demo 5) | 20 |
| 06 | `L2306_lab_*` | Capstone lab — compose a system, graph it, self-audit (Obj 3–5) | 40 |

Optional split (per the roadmap): **Lecture A** = items 01–03 (archetypes & authoring), **Lecture
B** = items 04–06 (composition, the graph & anti-patterns). Total ~90–120 min.

## Runtime notes (read before class)

- **Notebooks run offline by default.** All L23 notebooks drive the course's scripted `FakeModel`
  (from `common.fake_model`), so a restart-and-run-all passes with **no API key and no network** —
  the demonstrated `list_skills`/`load_skill` paths are deterministic. This is the same offline
  stance as L11/L12. Set `ANTHROPIC_API_KEY` (via the repo `.env`) only if you want to run the
  **optional** `if LIVE:` cell on real Sonnet 4.6; without a key it prints a skip line and the
  notebook still completes.
- **The worked skills are real.** The lectures read and graph this repo's own skill system
  (`.claude/skills/author-lesson-roadmap` → `generate-materials-from-roadmap`, the `.claude/rules/*.md`
  rubric files) plus the two example skills built for this lesson in
  [`example_skills/`](example_skills/README.md) (`get_order` script-centric; `check_lesson_links`
  shared). Have `example_skills/README.md` open — it maps each example to its archetype/demo.
- **Selection is model-driven and non-deterministic on a live model.** The offline `FakeModel` path
  is fixed, but if you run the live path, budget a re-run — "which skill does the agent
  `load_skill`?" is exactly the point in the composition and collision demos.
- **The composition/anti-pattern reasoning is a `create_agent` freebie** — the loop is L11's; the
  new part is the two skill tools and how they compose. Don't re-teach the loop.

## L2303_lab problem 1 (classify by archetype)

COMMON GOTCHAS: students conflate "has a script step" with script-centric — remind them archetype
is about the *center of gravity* (the primary shape), not whether a script appears anywhere. The
runbook example may tempt a "script-centric" label because it mentions running something; steer to
"the value is doing the steps in order."
UNBLOCKERS: point back to L2302's side-by-side table (center of gravity / body reads like / good
when). Ask: "where does the *real work* live — a script, a rule list, or an ordered procedure?"
TIME: ~5 min. STRETCH: have them name a fourth blurb that would be reference/knowledge (resource-
centric) and why RAG (L21) is the escalation.

## L2303_lab problem 2 (spot the wrong shape — written)

COMMON GOTCHAS: some will "fix" the prose instead of naming the archetype error. The point is
diagnosis: it's a deterministic step prose-described where a *script* belongs.
UNBLOCKERS: ask "could a script do this exact step every time with no judgment?" If yes → it should
be script-centric, and the markdown should just say when/how to run it.
TIME: ~4 min. STRETCH: have them rewrite the offending sentence as a one-line "run X, read Y."

## L2303_lab problem 3 (author a script-centric body)

COMMON GOTCHAS: over-writing — students pack the deterministic logic into the markdown. The whole
point is the body is *thin*: when to run it, exact invocation, how to read output. The `assert`
checks for `get_order_api` and an `ORD-` id, so a body missing the invocation fails.
UNBLOCKERS: open `example_skills/get_order/SKILL.md` as the model to imitate.
TIME: ~7 min. STRETCH: add a "how to read the output" line that names the discriminated-union
`payment.method` gotcha from the real skill.

## L2303_lab problem 4 (a discriminating description)

COMMON GOTCHAS: descriptions that say what the skill *does* but not what it's *not* — so they still
collide with the sibling. The best descriptions imply the boundary ("… for X; not for Y").
UNBLOCKERS: show the colliding sibling side by side and ask "what input should go to the OTHER one?"
TIME: ~5 min. STRETCH: write a one-line test task that would previously have been ambiguous and now
routes cleanly.

## L2303_lab problem 5 (grow your L22 skill — open-ended)

COMMON GOTCHAS: students who don't have their L22 skill handy — let them use the solutions' worked
`refund-policy` example. The classification is the graded part; the tightened description is craft.
UNBLOCKERS: "which of the three shapes is your L22 skill? What would collide with it in a set?"
TIME: ~9 min. STRETCH: sketch a second skill that would *handoff* from or *share* with this one —
foreshadows L2306.

## L2306_lab problem 1 (a sequential handoff)

COMMON GOTCHAS: forgetting that the edge is literal — the upstream body must actually contain
`load_skill("<downstream>")`. If the FakeModel script and the bodies disagree, `loaded_skills` won't
show the expected path. Keep the scripted `tool_call` names matching real skill names.
UNBLOCKERS: point at L2304 §2; the provided FakeModel script mirrors it. Print `list_skills()` to
confirm the new skill registered.
TIME: ~8 min. STRETCH: add a third stage and observe the path grow by one load.

## L2306_lab problem 2 (a shared lower-level skill)

COMMON GOTCHAS: students make C a *handoff* target of only one skill (a pipeline) instead of a
*shared* dependency of two. The `assert` wants C reachable from two operating skills (fan-in).
UNBLOCKERS: L2304 §3 — "A → C ← B". Edit *both* operating bodies to `load_skill("C")`.
TIME: ~8 min. STRETCH: confirm C's body loads once *per use* on a path that hits it twice, not baked
in per caller.

## L2306_lab problem 3 (draw the dependency graph)

COMMON GOTCHAS: mixing up the pipeline (a chain A→B) with the shared node (fan-in). `dependency_edges`
returns `(from, to)` pairs — the fan-in node is the one that appears as a *target* from two sources.
UNBLOCKERS: print the edges and read them aloud; the shared node is the repeated right-hand side.
TIME: ~7 min. STRETCH: render a Mermaid diagram of their graph (copy the pattern from L2304 §4).

## L2306_lab problem 4 (JIT in numbers)

COMMON GOTCHAS: counting a shared body twice — it loads per *use* along a path, but for the
always-on/cost framing the interesting number is the *distinct* bodies on the path. Always-on is
just the two tool schemas regardless of registry size.
UNBLOCKERS: reuse the JIT block from L2304 §5 (`dict.fromkeys(path)` for unique bodies).
TIME: ~6 min. STRETCH: compare always-on cost of a 3-skill vs a 30-skill registry — it's the same
two schemas; that's the payoff over L22's always-on descriptions.

## L2306_lab problem 5 (self-audit + one fix)

COMMON GOTCHAS: students declare their system "clean" without checking each anti-pattern. Require a
sentence per pattern (over-chaining / shared-skill-that's-really-a-tool / description collisions).
The code fix must make the two descriptions *substantially* differ (the `assert` guards this).
UNBLOCKERS: L2305 is the reference; map each anti-pattern to its inverted good move.
TIME: ~11 min. STRETCH: if their system genuinely has none, have them *introduce* one deliberately
and show the symptom, then cure it.
