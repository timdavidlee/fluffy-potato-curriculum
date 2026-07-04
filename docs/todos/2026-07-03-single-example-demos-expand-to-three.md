# 2026-07-03 — Expand single-example demos/labs to ≥3 examples for variety

**Goal:** sweep every notebook demo and lab under
`src/fluffy_potato_curriculum/lessons/L<NN>/` for cells that illustrate a concept with a
**single example** (one prompt, one input string, one document, one tool call) and expand them to
**at least 3 varied examples** the student actually executes. One example reads as a special case;
three shows the shape holds across inputs and surfaces the interesting variation (edge cases,
failure modes, differing outputs).

## Why

- A lone example is easy to overfit to — students copy it without seeing the concept generalize.
- Variety exposes the *why*: where a tokenizer splits differently, where structured-output parsing
  gets brittle, where a prompt tactic helps vs. doesn't.
- Cheap, high-leverage pedagogical polish that doesn't change lesson scope.

## Approach

- Go lesson-by-lesson (`L01` → …). For each `*_lecture.ipynb`, `*_lab_empty.ipynb`,
  `*_lab_solutions.ipynb`, scan for demo cells that run exactly one input through the concept.
- Expand to 3+ inputs — ideally a small list iterated over, or a `parametrize`-style table — so the
  contrast is visible in one glance. Pick inputs that *differ meaningfully* (short/long, easy/edge,
  success/failure), not three near-duplicates.
- Keep the notebook-length cap in mind (`.claude/rules/notebooks.md`, ~25 cells): expand *within* a
  cell (loop over a list) rather than adding many new cells. Split only if a notebook is already at
  the cap.
- Respect the live-call rules: if examples hit a live model, keep calls small/few (low
  `max_tokens`), and don't commit live output. For `_empty` labs, clear outputs after.
- Per touched notebook: restart-and-run-all clean, then run the gate
  (`uv run ruff format && uv run ruff check && uv run pyright && uv run pytest`).

## Scope / triage

- **In scope:** demo cells and lab exercises where a single example stands in for a general
  concept.
- **Skip:** cells where one example is genuinely the point (a single end-to-end walkthrough, a
  narrative "here's the one canonical call"), setup cells, and anything already showing variety.
- Built lessons to sweep first (mini + full); unbuilt mini lessons (L03, L05, L23) get this baked
  in at generation time instead — note in their roadmaps.

## Open question

- `<need input: is this a standalone pass, or fold it into the LangChain notebook-regeneration`
  `already pending in 2026-07-03-langchain-notebook-migration.md?>` — many of those notebooks are
  getting rewritten anyway; cheapest to apply the 3-example rule as they're regenerated rather than
  touching them twice.
