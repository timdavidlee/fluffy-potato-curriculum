# L23 example skills

Teaching material for **L23 — Skill patterns & composition**. These two skills
fill the two archetype gaps that the repo's real [`.claude/skills/`](../../../../../.claude/skills)
didn't already have an example of, so that every archetype and both composition
shapes have a real, on-disk instance the lesson can read, run, and graph.

They live **here, under the lesson**, not in the repo's live `.claude/skills/`
registry — they are teaching examples, not part of the curriculum-authoring
toolchain, and shouldn't be auto-loaded into real Claude Code sessions. L23's
runtime (the L04/L11 LangGraph agent with `list_skills` / `load_skill`) points at
*this* directory alongside the real skills it reads.

## What's here

| Directory | Archetype / role | Where the real work lives |
| --- | --- | --- |
| [`get_order/`](get_order/SKILL.md) | **Script-centric** (API/integration recipe) | `get_order_api.py` — a mock, offline orders API with a deliberately messy JSON contract |
| [`check_lesson_links/`](check_lesson_links/SKILL.md) | **Shared lower-level skill** (fan-in) | `extract_links.py` — mechanical link extraction; the `SKILL.md` adds the judgment |

## How they map to the demos

- **Demo 1 (archetypes):** `get_order/SKILL.md` is the clean **script-centric**
  example — a thin wrapper over a script. It contrasts with the real
  `author-lesson-roadmap` (runbook / procedure-centric) and the `.claude/rules/*.md`
  files (rubric / principle-centric).
- **Demo 4 (shared skill + graph):** `check_lesson_links` is the shared node `C`
  that both operating skills — `author-lesson-roadmap` and
  `generate-materials-from-roadmap` — fan into (`A → C ← B`).

## Why the contracts are deliberately messy

The script-centric archetype only earns its keep when the underlying operation is
genuinely awkward to reason through. So the mock order payload is nested and
heterogeneous on purpose: a **discriminated-union `payment`** (its fields depend
on `method`), per-item `options` maps with different keys, a variable-length
address list, optional `tracking`, and optional per-event `note`s. Wrapping that
in a script the agent *runs* clearly beats making the model re-derive the shape on
every call — which is the point Demo 1 lands.

## Running them

```sh
# script-centric: fetch one order's messy JSON contract
uv run python -m fluffy_potato_curriculum.lessons.L23.example_skills.get_order.get_order_api ORD-1001

# shared skill's mechanical helper: extract + resolve one doc's links
uv run python -c "from pathlib import Path; from fluffy_potato_curriculum.lessons.L23.example_skills.check_lesson_links.extract_links import extract_links; doc=Path('docs/origin/lesson_roadmaps/L23/objectives.md'); [print(link.kind, link.resolves, link.target) for link in extract_links(doc.read_text(), doc.parent)]"
```

Both are offline and deterministic — nothing here touches a network or an LLM.
