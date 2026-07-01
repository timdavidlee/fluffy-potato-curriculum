---
description: Review CLAUDE.md / README.md against the current repo and update them (and add nested CLAUDE.md files where they'd help navigation)
model: opus
---

Audit this repo's guidance docs against reality and bring them up to date. The goal: a
teammate (or Claude Code) reading `CLAUDE.md` / `README.md` should find nothing stale, no
broken pointers, and no missing map for a part of the tree that has grown enough to need one.

If `$ARGUMENTS` is provided, scope the audit to that path or topic (e.g. a single lesson dir,
`README.md` only, "just check the toolchain commands"). Otherwise audit the whole repo.

## 1. Gather ground truth first

Do not trust the docs — check them against the repo as it is *now*.

- Find every guidance doc: the root `CLAUDE.md`, `README.md`, and all nested `CLAUDE.md`
  files (`find . -name CLAUDE.md -not -path './.git/*'`; today there are also ones under
  `docs/origin/`, `src/fluffy_potato_curriculum/lessons/`, and `.../projects/`).
- Read the enforced conventions under [.claude/rules/](../rules/) — `python-style.md`,
  `pytest.md`, `notebooks.md` — these are the source of truth the docs summarize.
- Establish the real layout: top-level packages under `src/fluffy_potato_curriculum/`
  (`common/`, `lessons/`, `potato_llm/`, `projects/`), the set of `lessons/L<NN>/` dirs,
  and the test tree under `tests/`.
- Confirm the toolchain claims by inspection, not memory: read `pyproject.toml`
  (deps, ruff/pyright/pytest/commitizen config, scripts), `.python-version`, `uv.lock`
  presence, and `.githooks/`. Use `git log --oneline -20` to see what changed recently.

## 2. Check each doc for staleness

For every guidance doc, verify and flag:

- **Broken or moved pointers.** Every file/dir path, relative link, and `L<NN>` reference
  must resolve. Renamed or deleted lessons/modules are the most common rot here.
- **Layout drift.** The described directory structure matches the actual tree (new
  top-level packages like `common/` or `potato_llm/` documented; removed ones gone).
- **Command / toolchain drift.** Commands, tool versions, Python version, lint rule sets,
  and config claims match `pyproject.toml` / `.python-version` / the rules files.
- **Convention drift / new caveats.** Coding conventions and caveats still hold; anything a
  new pattern in the code now requires that the docs don't mention (e.g. the `config` seam,
  the `potato_llm` client, live-demo gating) gets captured.
- **Contradictions.** A nested `CLAUDE.md` must not contradict the root one or the rules
  files; the root should point down to the nested maps rather than duplicate them.

## 3. Consider adding nested CLAUDE.md files

Nested `CLAUDE.md` files are how Claude Code navigates without loading the whole tree. Propose
a new one for any directory that (a) is a distinct enough subsystem that its own conventions or
entry points aren't obvious from the root doc, and (b) has grown enough to warrant a local map
(e.g. a `common/` package, a `potato_llm/` client, a lessons subtree). Keep each one short:
what lives here, how it's meant to be used, local gotchas, and a pointer back up. Don't add one
to a thin or self-explanatory directory — a CLAUDE.md that just restates the filenames is noise.

## 4. Apply and report

- Make the edits directly. Keep the existing voice and formatting; prefer minimal, precise
  changes over rewrites. Follow the repo's own doc conventions.
- Do **not** touch files marked as drafts (see the draft-marker convention for
  `docs/origin/`) or invent conventions the code doesn't actually follow.
- When you finish, give a short summary: what was stale (with `file:line`), what you changed,
  and any new `CLAUDE.md` files you added and why. If something looks stale but you're not
  sure of the intended direction, list it as a question rather than guessing.
