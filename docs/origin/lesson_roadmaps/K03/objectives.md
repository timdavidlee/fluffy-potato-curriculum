# K03: Jupyter workflow

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (Prework track row K03).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).
> Sibling doc: [demos_or_activities.md](demos_or_activities.md) — the self-paced walkthrough a
> student actually runs.

## Format note

Self-paced student walkthrough, not lecture+lab — same shape as K01 (see
[K01/objectives.md](../K01/objectives.md) for the full format rationale). The paired
[demos_or_activities.md](demos_or_activities.md) is the runbook the student executes: every step
is "Do → You should see → why it matters → If it breaks," and the walkthrough **is** the
hands-on work — there is no separate lab.

## Where this unit sits

K03 comes after K02: the environment runs (K01) and the keys are wired (K02), so the student can
now make live calls — but almost every one of those calls happens **inside a Jupyter notebook**,
which is the course's main interactive surface from `L01` onward. K03 gets the student launching
the notebook server against the pinned kernel and, more importantly, teaches the **one discipline
that keeps notebooks from lying to you: restart-and-run-all.**

The single outcome: **the student can launch `uv run jupyter lab`, open a lesson notebook, and run
it cleanly top-to-bottom on a fresh kernel — and understands why a notebook that only runs
out-of-order is broken, why the first cell holds all imports, and that they must clear live output
before committing.** This is not a Python-teaching unit (that's K04) and not an async unit (that's
K05); K03 is purely *how you drive the notebook tool correctly*.

## Prerequisites

- K01 complete: a working `uv` env, `uv run` understood, a green `uv run pytest`.
- K02 complete: an `ANTHROPIC_API_KEY` in a gitignored `.env`, reachable through the config seam.
  (K03's checkpoint opens an existing lesson notebook; if that notebook makes a live call, the key
  from K02 is what lets restart-and-run-all finish without erroring.)

No Jupyter experience is assumed — the notebook server itself is launched for the first time here.

## Learning objectives

By the end of K03, a student should be able to:

1. **Launch the notebook server against the pinned kernel with `uv run jupyter lab`.** Concretely:
   run `uv run jupyter lab` from the repo root, watch it open a browser tab, and understand that
   the `uv run` prefix (K01, Step 4) is what guarantees the notebook's kernel is the project's
   pinned `.venv` — so `import fluffy_potato_curriculum...` works inside a cell for the same reason
   `uv run pytest` works at the shell. The concept: **a notebook is just another way to run code
   in the pinned env; the kernel is the `.venv`.**

2. **Explain what a kernel is and what "restart" does to it.** Concretely: describe — at a
   semi-technical altitude — that the **kernel** is the long-lived Python process behind the
   notebook that remembers every variable, import, and function you've defined this session, in
   the order you *ran* the cells (not the order they appear on screen). "Restart the kernel" throws
   that memory away and starts a blank process. This is the mental model the next objective rests
   on.

3. **Internalize the restart-and-run-all discipline and why it is the headline rule.** Concretely:
   state that a correct notebook must **run cleanly top-to-bottom on a fresh kernel** — so the
   student's habit is Kernel → **Restart Kernel and Run All Cells** as the real test of whether a
   notebook works, not "the cells are all green right now." Recognize the failure it catches:
   **out-of-order execution state is the #1 source of notebook confusion** — a cell that only works
   because of a variable defined in a cell *below* it, or in a cell you since deleted, will look
   fine in your live session and then fail for the next person (or for you tomorrow). The concept
   to carry into every later lesson: **if it doesn't survive restart-and-run-all, it's broken —
   green output in a stale session proves nothing.**

4. **Read execution counts as a correctness signal.** Concretely: point at the `[1]`, `[2]`, `[3]`
   numbers to the left of each code cell and explain that after a clean run they should read
   **1, 2, 3, … in top-to-bottom order**; scrambled counts (`[7]`, `[3]`, `[12]`) are the visible
   fingerprint of an out-of-order session that hasn't been restart-run-all'd. A committed notebook
   should show the clean sequence.

5. **State the "first code cell is the setup cell" rule.** Concretely: articulate that **all
   imports and data loading go in the first code cell**, runnable without edits — not scattered
   through the notebook — so that a fresh-kernel run has everything it needs up front and no later
   cell secretly depends on an import three cells down. Recognize this as the structural half of
   the restart-and-run-all discipline: linear execution is only possible if setup comes first.

6. **Recognize top-level `await` in a cell (pointer only, no async yet).** Concretely: know that
   Jupyter lets you write `await some_coro()` **directly in a cell** — no `asyncio.run(...)`
   wrapper — because the notebook runs inside an event loop already. The student does **not** learn
   what `async`/`await` *mean* here; they only need to recognize the syntax so it isn't startling
   when a lesson notebook uses it. Explicit forward-pointer: **"you'll learn what this actually does
   in K05 (async concepts)."**

7. **Clear live output before committing a student notebook.** Concretely: state that notebook
   cells which hit the live API must have their **output cleared before committing** (it's
   nondeterministic and can re-expose paid responses), and know the repo's mechanism — the
   `_empty` student copies get cleared with the pinned `nbconvert` command, while `_solutions` and
   lecture notebooks may keep reference outputs. This makes concrete the "never commit live output"
   rule K02 introduced.

## Concepts to highlight inline (the callouts)

These are the "why it matters" boxes the walkthrough drops next to the relevant step:

- **The kernel is the `.venv`.** `uv run jupyter lab` starts a notebook whose kernel is the pinned
  project environment — that's why imports of course code just work, and it's the same `uv run`
  discipline from K01, not a new one.
- **Restart-and-run-all is the source of truth.** A notebook is only "working" if it runs clean
  top-to-bottom on a fresh kernel. Green cells in a live session prove nothing — they can depend
  on hidden, out-of-order state. This is the load-bearing concept of the whole unit.
- **Out-of-order state is the #1 notebook trap.** A cell can pass because of a variable from a cell
  below it (or a since-deleted cell). It works for you, breaks for everyone else. Restart-run-all
  is how you catch it before you commit.
- **Execution counts should read 1, 2, 3…** The little `[n]` numbers are a free correctness check:
  clean ascending = linear run; scrambled = you haven't restarted.
- **Setup cell first.** All imports and data loading live in the first code cell. Nothing later may
  depend on state defined below it.
- **Top-level `await` is fine — and you'll learn why in K05.** You can `await` directly in a cell;
  for now just recognize it, don't worry about what it means.
- **Clear live output before you commit.** Cells that hit the API get their output cleared (paid,
  nondeterministic). This is K02's "never commit live output" rule, now concrete — done with the
  repo's `nbconvert` command for `_empty` student notebooks.

## Verify / pass checkpoint

K03 is "done" when the student can prove the discipline, not just describe it:

1. `uv run jupyter lab` launches and opens the browser tab.
2. The student opens an **existing lesson notebook** (e.g.
   `src/fluffy_potato_curriculum/lessons/L03/L0302_lecture.ipynb`) and runs
   **Kernel → Restart Kernel and Run All Cells**.
3. It **completes top-to-bottom with no errors**, and the execution counts read `1, 2, 3, …`.

A clean restart-and-run-all on a real lesson notebook is the pass signal: it proves the server
launched against the pinned kernel, the environment and key (K01/K02) are reachable from inside a
cell, and the student has performed the one discipline every later unit assumes. If it errors,
the walkthrough's troubleshooting (is this the pinned kernel? did an earlier cell fail? is the key
from K02 set?) is the recovery path.

`<need input: pick the single canonical checkpoint notebook to name in the walkthrough. It must be
one that runs clean top-to-bottom by K03 (i.e. its lesson materials are already generated and, if
it makes live calls, the K02 key covers them). L0302_lecture.ipynb is the current placeholder —
confirm it exists and passes restart-run-all, or swap in a known-good early notebook.>`

## Bridge to K04

K03 gets the student *driving* notebooks correctly, but the code they'll read inside those
notebooks uses the repo's house style — strict type hints and pydantic models — which a
semi-technical student may not read fluently yet. **K04 (Python you'll read: types & pydantic)**
picks up there: how to read `X | None`, `list[int]`, `-> None`, and what a pydantic model
(`BaseSettings`, structured output, tool schemas) is — so the lesson notebooks stop looking
foreign.

## Open authoring questions

- `<need input: name the exact, known-good checkpoint notebook (see Verify checkpoint above). Must
  survive restart-and-run-all at the point K03 runs — some lesson notebooks make live calls and
  need the K02 key; a keyless/offline notebook would be a safer checkpoint if one exists.>`
- `<need input: is there a browser-less fallback for the launch step (e.g. a student on a remote/
  headless box)? `uv run jupyter lab` assumes it can open a browser tab; if headless students exist,
  the walkthrough needs the "copy the localhost URL / token" variant.>`
- `<need input: exact JupyterLab menu label for restart-run-all across the pinned version — confirm
  it reads "Restart Kernel and Run All Cells" in jupyterlab>=4.5, so the walkthrough's click-path
  matches what the student sees.>`
