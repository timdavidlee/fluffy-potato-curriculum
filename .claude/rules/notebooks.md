# Jupyter notebooks

Conventions for authoring `.ipynb` files in this repo — teacher lecture notebooks and
`_empty`/`_solutions` lab notebooks under `src/fluffy_potato_curriculum/lessons/L<NN>/`.

This file covers *how a notebook is built and styled*. File naming, the lecture/lab item
layout, and required metadata are owned by the lesson-authoring docs in `docs/origin/`; don't
duplicate them here.

## Keep notebooks short

This is the headline rule. A notebook is a teaching unit, not a scratchpad — long notebooks
lose students and rot fast.

- **One concept (or one tight cluster) per notebook.** If you're introducing a second,
  separable idea, that's a second lecture/lab item with its own `<NN>` index — not more cells
  bolted onto this one.
- **Soft cap: ~25 cells, or whatever fits one focused ~15-minute segment** — whichever comes
  first. When you bump against it, split rather than scroll. A lesson is meant to be a
  *sequence* of short notebooks, not one long one.
- Prefer extracting reused logic into the lesson's Python modules / `common/` and importing it,
  over growing the notebook — *except* where the authoring docs call for a self-contained
  teaching notebook, in which case keep the inline code minimal.

## Structure & navigation

Notebooks scroll, so students need a map and a way back. Every notebook follows the same
navigational skeleton.

- **Numbered headings.** Section headings carry a hierarchical number that tracks nesting:
  top-level sections are `1`, `2`, `3`; subsections `1.1`, `1.2`; sub-subsections `1.1.1`.
  Don't nest deeper than three levels (`1.1.1`) — if you need a fourth, the notebook is doing
  too much and should split (see *Keep notebooks short*). Number in the markdown heading text
  itself, e.g. `## 2. Character-based tokenizers` → `### 2.1 Encoding to IDs`.
- **Table of contents.** The opening markdown cell (after the title/metadata) is a TOC: a
  bulleted, indented list of the numbered sections, each a Markdown link to that section's
  heading anchor. Keep it in sync when you add or renumber sections.
- **"Jump to top" anchors.** Put a `<a id="top"></a>` anchor at the top of the notebook (in the
  title cell), and at the end of each top-level section add a small `[↑ Back to top](#top)`
  link so students can return to the TOC without scrolling. Add these at every relevant section
  boundary, not on every cell.
- Anchor links use GitHub-style slugs of the heading text (e.g. `## 2. Tokenizers` →
  `#2-tokenizers`); verify they resolve when the notebook renders.

## Reproducibility

- **Restart-and-run-all must pass on a fresh kernel, top to bottom, with no errors** (with any
  required API keys present — see *Live network / LLM calls*). This is non-negotiable — a
  notebook that only runs out of order is broken.
- **Author for linear execution.** No cell may depend on state from a cell below it or from a
  since-deleted cell. Execution counts in a committed notebook should read as a clean
  top-to-bottom run (`1, 2, 3, …`), not a scrambled session.
- **First code cell is the setup cell:** all imports and data loading, runnable without edits.
  Don't scatter imports through the notebook.

## Dependencies & environment

- Run notebooks with `uv run jupyter lab` so the pinned `.venv` kernel is used.
- **Every third-party import must come from a dep added via `uv add`** (dev deps via
  `uv add --dev`) so `pyproject.toml` / `uv.lock` stay in sync. **Never** use inline
  `%pip install` / `!pip install` cells.

## Live network / LLM calls

This is a course about calling real models, so notebooks **may** make real API calls — the live
demo is often the point. But a normal run has to stay safe, cheap, and reproducible:

- **Live calls require an API key; read it through the config seam, never hard-code it.** Keys
  load via `fluffy_potato_curriculum.common.config` (a `pydantic-settings` layer over the
  environment and a repo-root `.env`) — don't scatter ad-hoc `os.environ` lookups. A notebook
  whose teaching point genuinely needs a live model **may assume the key is set** and raise a
  clear error when it isn't (the `require_*_key` helpers do this); a keyless restart-and-run-all
  is no longer required for those notebooks. Where the concept *doesn't* need a live model,
  still prefer a canned/offline client (next bullet) so the run stays cheap and deterministic.
- **Go through the `potato_llm` seam, not a raw SDK**, so a fake/canned client can be dropped in.
  Where the *concept* doesn't actually need a live model (a deterministic illustration, a CI run),
  prefer a canned client or recorded response — the same mocking stance as tests
  (see [pytest.md](pytest.md)).
- **Keep live calls small and few** (low `max_tokens`, a handful of calls) so a class run costs
  cents, not dollars.
- **Don't commit live response output.** Clear the output of any cell that hit the API before
  committing; committed outputs should be deterministic (offline or canned) and small.

## Code quality inside cells

The [python-style.md](python-style.md) rules still apply to notebook code:

- `uv run ruff format` and `uv run ruff check` cover `.ipynb` under `src/` — keep cells lint-
  and format-clean.
- Type-annotate functions defined in cells (params + return). pyright doesn't type-check
  notebooks, so this is on you — but teaching code should model the project's strict-typed style.
- Markdown cells are concise: they frame the next demo, they don't replace it. Comment the
  *why*; prefer explicit, readable steps over dense one-liners (this is teaching code).

## Outputs & committing

- **Clear cell outputs before committing `_empty` student notebooks** and any non-reference
  notebook — students run the cells themselves, and stale outputs confuse. `_empty` notebooks
  are often derived from a `_solutions` copy and carry its outputs, so this is an active
  cleanup step, not a no-op. `_solutions` and teacher lecture notebooks **may** retain outputs
  as a reference rendering.
- **Clear outputs with `nbconvert`** (already a dev dep) targeted at the student copies — never
  a blanket strip, which would wipe the `_solutions`/lecture reference outputs you want to keep:

  ```sh
  uv run jupyter nbconvert --clear-output --inplace src/fluffy_potato_curriculum/lessons/**/*_lab_empty.ipynb
  ```
- **Never commit large or binary output blobs** (base64 images, multi-MB tables, animation
  frames). Keep demonstration plots small; if an output is heavy, clear it.
- Never leave secrets, API keys, or absolute local paths in cells or outputs.
- Edit notebooks through Jupyter or the `NotebookEdit` tool — don't hand-edit the raw `.ipynb`
  JSON.

## Before committing

Notebooks under `src/` are part of the same gate (from CLAUDE.md):
`uv run ruff format && uv run ruff check && uv run pyright && uv run pytest`. On top of that,
for each notebook you touched: restart-and-run-all to confirm it runs clean (with any required
API keys present for notebooks that make live calls), then clear the outputs of any `_empty`
student copy (see *Outputs & committing* above) before committing.
