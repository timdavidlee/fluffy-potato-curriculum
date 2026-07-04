# K01: Environment & tooling

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (Prework track row K01).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).
> Sibling doc: [demos_or_activities.md](demos_or_activities.md) — the self-paced walkthrough a
> student actually runs.

## Format note — this is prework, not a lesson

K units are **self-paced, step-by-step setup guides**, not proctor-led lecture+lab. A student
works through K01 **alone, at a keyboard**, following concrete numbered steps and hitting a
verify checkpoint at the end. This `objectives.md` says *what K01 must land and why*; the
paired [demos_or_activities.md](demos_or_activities.md) is the ordered walkthrough itself
("do this → here's what just happened → why it matters"). There is no separate lab — the
walkthrough **is** the hands-on work.

## Where this unit sits

K01 is the **first thing a student does** in the whole course — before `L01`, before any other
`K` unit. Everything downstream assumes a working local checkout with the project's pinned
environment. If K01 doesn't land, every later unit fails in a way that looks like a lesson bug
but is really a setup bug — which is exactly the mid-lesson debugging the prework track exists to
prevent.

The single outcome: **the student can run project code through `uv` against the pinned `.venv`,
and understands the three moving parts they'll touch every day — the repo (`src/` layout), the
environment (`uv` + `.venv`), and the run command (`uv run`).** K01 is deliberately narrow: keys
(K02), Jupyter (K03), and Docker (K06) each get their own unit. K01 only gets the student to a
green `uv run` and a passing test suite.

## Prerequisites

This is the entry point. A student needs only:

- A computer they can install software on (macOS, Linux, or WSL2 on Windows).
- A terminal they can type into, and the willingness to paste commands.
- Git installed, or the ability to install it (the walkthrough links the installer).

No Python, `uv`, or project familiarity is assumed. **`uv` itself is installed in this unit** —
it is the one prerequisite the walkthrough sets up rather than assuming.

## Learning objectives

By the end of K01, a student should be able to:

1. **Clone the repository and land in the right directory.** Concretely: install `uv`
   (the single toolchain entry point), `git clone` the repo, `cd` into it, and recognize the
   top-level markers that say "I'm in the right place" (`pyproject.toml`, `uv.lock`, `src/`,
   `.python-version`).

2. **Explain what a virtual environment (venv) is, and why the project has its own.** Concretely:
   describe — at a semi-technical altitude, no prior venv experience assumed — that a **virtual
   environment is a self-contained, per-project Python** (its own interpreter + its own installed
   packages) living in the project's `.venv/` folder, kept **separate** from the system Python
   and from every other project. State *why* it exists: without it, two projects that need
   different versions of the same package collide, and installing packages globally slowly
   corrupts your system Python. With a venv, this project's dependencies are quarantined in
   `.venv/` and can't break anything outside it. Recognize the two ways code "gets into" the
   venv: the course's default **`uv run <cmd>`** (uses `.venv` automatically, objective 4) and
   the traditional manual **`source .venv/bin/activate`** (shown once so the concept isn't
   mysterious, but not the course default).

3. **Explain what `uv sync` does and run it.** Concretely: run `uv sync` and describe, in their
   own words, that it (a) reads the **pinned** `pyproject.toml` + `uv.lock`, (b) provisions the
   correct Python version from `.python-version` (3.13), and (c) materializes the isolated
   **`.venv/`** (the virtual environment from objective 2) with the exact locked dependency
   versions. The takeaway concept: **the lockfile is the source of truth — everyone in the cohort
   gets byte-for-byte the same environment**, which is why "works on my machine" stops being a
   class-wide problem.

4. **Run project code with `uv run` and explain why, not `python`.** Concretely: run something
   through `uv run` (e.g. `uv run python -c "..."`, `uv run pytest`) and explain that `uv run`
   guarantees the command executes **inside the pinned `.venv`** without the student having to
   manually "activate" anything. The concept to internalize: **`uv run <cmd>` is the default verb
   for this course** — every command in every later unit is prefixed with it for exactly this
   reason. Recognize the failure mode of a bare `python foo.py` (wrong interpreter, missing deps,
   `ModuleNotFoundError`).

5. **Read the `src/` layout well enough to navigate.** Concretely: locate
   `src/fluffy_potato_curriculum/` and name the top-level subsystems they'll meet
   (`lessons/`, `common/`, `potato_llm/`, `local_ui/`), and state the one rule that matters for a
   student: **imports use the package path** (`from fluffy_potato_curriculum.lessons... import`),
   never a bare top-level directory. They don't need to understand *why* src-layout exists — only
   to not fight it when an import looks "too long."

6. **Confirm the environment is real by running the test suite.** Concretely: run `uv run pytest`
   and see it collect and pass. This is K01's own pass signal (below) — a green suite proves the
   env, the interpreter, and the imports all line up.

7. **(Optional) Enable the commit-message git hook.** Concretely: run
   `git config core.hooksPath .githooks` once, and understand it's an opt-in convenience (a
   `prepare-commit-msg` helper), safe to skip. Flagged optional so a student who just wants to
   *run* code isn't blocked on git-hook setup.

## Concepts to highlight inline (the callouts)

These are the "why it matters" boxes the walkthrough drops next to the relevant step. Each is one
idea, surfaced at the moment the student's hands are on it:

- **What a virtual environment is.** A per-project, self-contained Python (its own interpreter +
  packages) in `.venv/`, isolated from the system Python and from other projects — so
  dependencies can't collide or corrupt anything outside the project. This is the concept a
  semi-technical student is most likely to be missing; land it explicitly, don't assume it.
- **Pinned environment / lockfile.** `uv.lock` + `.python-version` mean that venv is
  *reproducible*, not *approximate* — every student's `.venv/` is byte-for-byte the same. This is
  the difference between a curriculum and a pile of scripts.
- **`uv run` is the verb.** Every later command is `uv run …`. Introduce it once, here, so it's
  invisible infrastructure by `L01`.
- **`.venv` is disposable.** It's derived from the lockfile — if it ever gets weird, delete it
  and `uv sync` again. Nothing important lives in `.venv/` that isn't reconstructable.
- **`src/` layout.** Code lives under `src/fluffy_potato_curriculum/`; you import it by its
  package path. Long import lines are correct, not a smell.
- **Don't hand-edit `pyproject.toml`.** New deps go through `uv add` so the lockfile stays in
  sync — a rule the student won't need yet but should have *seen* once.

## Verify / pass checkpoint

K01 is "done" when, from a fresh clone:

```sh
uv sync            # provisions .venv from the lockfile, exits 0
uv run pytest      # collects and passes
```

both succeed. A student who reaches a green `pytest` has a working, pinned environment and is
cleared to proceed to K02. If either command fails, the walkthrough's troubleshooting section
(is `uv` on `PATH`? right directory? stale `.venv`?) is the recovery path — this is *the* unit
where a student is most likely to get stuck on machine-specific setup, so the troubleshooting
must be generous.

## Bridge to K02

K01 ends with runnable project code but **no API keys** — so any code that calls a live model
would fail. That's the exact hook into **K02 (Keys & the config seam)**: the environment is real,
now we give it credentials, wired through `common/config.py` (never scattered `os.environ`), and
learn the live-call hygiene the course's real, paid API calls demand.

## Open authoring questions

- `<need input: does the course hand students a pre-clone (e.g. a GitHub Classroom fork / a
  Codespace) or is a raw `git clone` of the public repo the assumed entry? Changes whether K01
  opens with an auth/access step or goes straight to `uv sync`.>`
- `<need input: Windows support stance — is WSL2 the supported path (recommended), or must the
  walkthrough carry native-Windows PowerShell variants for every command? Affects how many
  command variants each step needs.>`
