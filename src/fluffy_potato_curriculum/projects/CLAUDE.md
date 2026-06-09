# projects/

End-of-week, integrative project briefs and their starter code. Each `<brief>/` directory is a
single-day hackathon-style build where students consolidate a week's lessons into a runnable,
demoable agent.

## Where the source material lives

The conventions and design intent for everything in here come from
[docs/origin/PROJECT_BRIEF_DESIGN.md](../../../docs/origin/PROJECT_BRIEF_DESIGN.md) — the
source of truth for what a brief must contain, its README structure, scope/cadence, and the
showcase format. Read it before authoring or editing a brief; don't infer the shape from
existing folders alone. The week-to-lesson mapping that a project draws on lives in
`docs/origin/CURRICULUM_PRD.md`.

## Layout

```
projects/
  README.md            # idea bank — names + one-line descriptions, maintained by Claude
  EVALUATION.md        # shared rubric, linked from every brief
  <brief>/
    README.md          # the brief (structure defined in PROJECT_BRIEF_DESIGN.md)
    starter.py         # runnable starter code
    *.csv / *.html     # any dataset or mock-up the brief needs
```

## Conventions

- **Claude owns the idea bank.** `README.md` here is a Claude-maintained index of suggested
  project themes mapped to the lessons they exercise, each with a corresponding `<brief>/`
  folder. Default to maintaining it rather than asking.
- Each brief's `README.md` follows the 8-section structure in `PROJECT_BRIEF_DESIGN.md`
  (problem statement → background → target users → implementation considerations → suggested
  API contract → evaluation → stretch goals → helpful links) and links to the shared
  `EVALUATION.md`.
- Starter code follows the repo Python rules: [.claude/rules/python-style.md](../../../.claude/rules/python-style.md).
