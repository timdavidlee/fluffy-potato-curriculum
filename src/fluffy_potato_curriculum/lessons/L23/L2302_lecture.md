# Skill archetypes and how to author each one

```yaml
title: "Skill archetypes and how to author each one"
keywords: skill archetype, center of gravity, instructions scripts resources, script-centric, API integration recipe, principle-centric, review rubric, procedure-centric, operating-model runbook, reference knowledge skill, RAG, SKILL.md authoring, discriminating description, wrong container
estimated duration: 30
```

> **Lesson:** L23 — Skill patterns & composition. Written reference lecture, paired with its lab
> ([L2303_lab_empty.ipynb](L2303_lab_empty.ipynb)). Read [L2301_intro.md](L2301_intro.md) first.
> This lecture lands **Objective 1** (classify by archetype) and **Objective 2** (author each
> archetype). Composition — wiring these into a system — is the next two notebooks
> ([L2304](L2304_lecture.ipynb), [L2305](L2305_lecture.ipynb)).
> **Anchor model: Claude Sonnet 4.6.**

<a id="top"></a>

## 1. "Skill" is not one shape

### 1.1 Recap: what a skill is (from L22)

- A **skill** is a markdown instruction file — a `name`, a `description` of *when it applies*, a
  body of instructions, and optionally bundled scripts — that the agent loads **just in time**.
- L22's one-line taxonomy still holds: **a tool is *called*, a skill is *read*, the system prompt
  is *always seen*.**
- L22 authored *one* skill and treated "skill" as a single thing. That's the gap this lecture
  closes: skills come in a few recurring **shapes**, and the shape changes how you write them.

### 1.2 The organizing idea: center of gravity

- Every skill bundles some mix of three things: **instructions**, **scripts**, and **resources**
  (facts/data). The **archetype** is just *which one is the center of gravity.*
- Instructions split further by whether they read as **ordered steps** (do this, then this) or
  **judgment criteria** (hold the work against these standards).
- diagram: a triangle with corners labeled `instructions`, `scripts`, `resources`; the
  `instructions` corner splits into two sub-labels `ordered steps` and `judgment criteria`; each
  corner/branch is annotated with the archetype that sits there (script-centric, procedure-centric,
  principle-centric, and the resource-centric aside)

### 1.3 Why classify first

- The archetype **tells you where the real content belongs** — and therefore how to author the
  skill well.
- Mis-classifying produces a bad skill: prose-describing a deterministic step instead of scripting
  it; writing a linear procedure where a rule list belongs; standing up retrieval for six facts.
- text: this is the *authoring* payoff of L23's first objective — you classify not to file
  paperwork, but because the label picks your pen.

[↑ Back to top](#top)

## 2. The three core archetypes

### 2.1 Script-centric — the API/integration recipe

- **Center of gravity: a bundled script.** The markdown is a thin wrapper; the real work runs.
- The body says *when* to run it, the *exact* invocation, and how to read its output — nothing more.
- Good when the operation is **deterministic and better executed than reasoned through**.
- text: real example in this repo — [`example_skills/get_order/SKILL.md`](example_skills/get_order/SKILL.md),
  a wrapper over a mock orders API (`get_order_api.py`) whose JSON is deliberately messy.
- diagram: a thin markdown box labeled "when + how to call" pointing at a fat box labeled
  "`get_order_api.py` (the real work)"; a speech bubble notes "run it, don't re-derive the contract"

### 2.2 Principle-centric — the review / rubric

- **Center of gravity: a rule list.** A set of principles or a checklist the agent applies as
  **judgment** — no single deterministic answer, no script that could replace it.
- Written as *criteria to hold work against*, not a linear procedure.
- Good when the value is **consistent application of taste or standards**.
- text: real examples in this repo — [`.claude/rules/python-style.md`](../../../../.claude/rules/python-style.md)
  and [`.claude/rules/pytest.md`](../../../../.claude/rules/pytest.md), or a `/code-review`-style
  "check the diff against these principles" skill.

### 2.3 Procedure-centric — the operating-model runbook

- **Center of gravity: an ordered procedure.** The skill drives a multi-step task end to end —
  numbered steps, decision points, a clear done-condition.
- Written **for an agent to follow**, with deterministic sub-steps delegated to scripts.
- Good when the value is **doing the steps in the right order every time**.
- text: real example in this repo — [`author-lesson-roadmap`](../../../../.claude/skills/author-lesson-roadmap/SKILL.md)
  (read these docs in order → draft → cross-check → report). The skill that helped build this lesson.

### 2.4 Side by side — the discriminator

- table: three columns (script-centric, principle-centric, procedure-centric) × rows for
  "center of gravity", "body reads like", "good when", "repo example"

| | script-centric | principle-centric | procedure-centric |
| --- | --- | --- | --- |
| center of gravity | a bundled script | a rule list | an ordered procedure |
| body reads like | "run this, read that" | "hold the work to these" | "step 1 … step N, done when …" |
| good when | the op is deterministic | consistency of taste matters | order-every-time matters |
| repo example | `example_skills/get_order` | `.claude/rules/*.md` | `author-lesson-roadmap` |

[↑ Back to top](#top)

## 3. The honorable-mention fourth shape

### 3.1 Reference / knowledge (resource-centric)

- **Center of gravity: the resource.** The body is **facts to read** — a small glossary, a schema,
  a handful of brand or product facts — not steps, criteria, or a script.
- It's the **cheap right answer when there are only a handful of terms** to know: the facts just
  sit in context when the skill loads.
- text: taught as an *aside*, not one of the three you'll author today — but a real, common shape.

### 3.2 When it outgrows a skill: RAG

- Once the knowledge outgrows what fits comfortably in context, a reference *skill* is the wrong
  tool — that's **retrieval-augmented generation (RAG)**'s job (**full-course L21**, not part of
  the mini cut).
- text: rule of thumb — a dozen definitions → a resource-centric skill; a document corpus → RAG.

[↑ Back to top](#top)

## 4. The archetype dictates the authoring

### 4.1 Same format, different body shape

- Every archetype uses the **same `SKILL.md` format** from L22 (frontmatter `name` + `description`,
  then a markdown body). What changes is the **shape of the body**.
- text: script-centric → minimal prose, a clear "when to run it", the exact invocation, how to read
  output; the deterministic logic lives in the **script**, not the markdown.
- text: rubric → an explicit, scannable list of rules with just enough example to apply each;
  written as **judgment criteria**, not a linear procedure.
- text: runbook → numbered, imperative, self-contained steps with explicit decision points and a
  clear done-condition; deterministic sub-steps delegated to scripts.

### 4.2 The description is still the trigger — now across a set

- Every archetype still needs a **discriminating description** (L22's load-bearing craft point) —
  the sentence the model matches on to decide *whether to read the skill at all*.
- L23 adds a constraint: descriptions must stay **mutually distinct across the whole set** of
  skills, or the model can't reliably pick — the setup for the **description-collision** anti-pattern
  in [L2305](L2305_lecture.ipynb).

### 4.3 The wrong-shape mistake (preview of the anti-patterns)

- Writing the wrong body shape is the archetype-level version of L22's "wrong container" mistake.
- diagram: two side-by-side "bad" panels — (left) a runbook that *prose-describes* a deterministic
  step in three verbose paragraphs instead of calling a script; (right) a rubric flattened into a
  rigid numbered procedure that loses its "apply judgment" character
- text: the cure is always the same — name the archetype, then let the body follow it.

[↑ Back to top](#top)

## 5. Vocabulary you'll meet elsewhere

### 5.1 The same shapes under other names

- table: our label → industry terms you'll see in the wild

| our label | also called |
| --- | --- |
| script-centric (API/integration recipe) | tool wrapper, executable skill, action / plugin |
| principle-centric (review/rubric) | checklist, style guide, guidelines, policy, *evaluative* playbook |
| procedure-centric (operating-model runbook) | runbook, SOP, recipe, *procedural* playbook |
| reference/knowledge (resource-centric) | cheat-sheet, knowledge pack, reference doc |

- text: caution — **"playbook"** gets used for *both* the rubric and the runbook shapes; our labels
  disambiguate it.

### 5.2 Archetypes are a spotting heuristic, not rigid boxes

- Real skills borrow across archetypes: a runbook that *calls* a script for one step; a review skill
  that *ends* by running a formatter; a runbook that opens with a short reference glossary.
- text: classify the **primary** shape so the authoring choices follow — then borrow as needed.
- text: next up — the lab ([L2303](L2303_lab_empty.ipynb)) has you classify real skills and author
  one; then we wire skills together into a system.

[↑ Back to top](#top)
