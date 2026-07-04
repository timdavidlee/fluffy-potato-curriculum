# K03 — Jupyter workflow

## How to read this file

Work top to bottom; budget ~15–20 minutes. The finish line is a clean **Restart Kernel and Run
All Cells** on a real notebook (Step 3). **Reminder:** every command is `uv run …` (K01, Step 4)
— including the one that launches Jupyter.

> **The one habit this unit installs:** a notebook is only "working" if it runs cleanly
> top-to-bottom on a *fresh* kernel. Cells that are all green right now prove nothing — they can
> secretly depend on state you can't see. You'll do the fresh-kernel run yourself in Step 3, and
> it becomes your reflex for every lesson after this.

## Step 1 — Launch JupyterLab against the pinned kernel

**Do:** from the repo root, start the notebook server:

```sh
uv run jupyter lab
```

**You should see:** some startup logs in the terminal, then a browser tab open automatically to
JupyterLab (a file browser on the left showing the repo). If a browser doesn't open, the terminal
prints a `http://localhost:8888/lab?token=…` URL — copy it into your browser.

**What just happened / why it matters:** the `uv run` prefix is doing the same job it did in K01 —
it launches Jupyter **inside the pinned `.venv`**, so the notebook's **kernel** (the Python process
that will actually run your cells) is the project environment. That's why, inside a cell,
`import fluffy_potato_curriculum...` and your K02 key both just work: it's the exact same
environment `uv run pytest` uses, not your system Python.

**If it breaks:** "command not found: jupyter" → you dropped the `uv run` prefix (or `uv sync`
from K01 didn't finish — re-run it). "Address already in use" → a Jupyter server is already
running; use the tab that's already open, or stop the old one with Ctrl-C in its terminal.

> **Leave this terminal running.** The server lives in it. When you're done for the day, come back
> and press **Ctrl-C** to stop it. Opening a *second* terminal for other `uv run` commands is fine.

## Step 2 — Open the practice notebook

**Do:** in the JupyterLab file browser on the left, navigate to this unit's practice notebook and
double-click it to open:

```
src/fluffy_potato_curriculum/lessons/K03/K0302_demo.ipynb
```

**You should see:** the notebook open in the main pane — a stack of **cells**, some Markdown (prose
headings) and some code. To the left of each code cell is an execution counter that reads `[ ]`
when the cell hasn't run yet this session.

**What just happened / why it matters:** a notebook interleaves prose and runnable code cells.
Crucially, the kernel runs cells **in the order you execute them, not the order they appear on the
page** — it remembers every variable and import from every cell you've run this session. That
memory is powerful and also the source of the trap you're about to learn to avoid.

## Step 3 — Restart Kernel and Run All Cells (this is the pass checkpoint)

**Do:** with `K0302_demo.ipynb` open, choose **Kernel → Restart Kernel and Run All Cells…** from
the top menu, and confirm the prompt.

**You should see:** the kernel resets to a blank state, then every cell runs from the top down.
When it finishes, the execution counters on the left read **`[1]`, `[2]`, `[3]`, …** in order,
top to bottom, and **no cell shows an error traceback.**

**What just happened / why it matters — the load-bearing concept of this unit:**

"Restart Kernel" threw away everything the kernel remembered and started a blank Python process.
"Run All Cells" then ran the notebook from a clean slate, top to bottom — exactly the way the next
person (or you, tomorrow) will experience it. **This is the real test of whether a notebook
works.** A notebook whose cells are all green in a live session can still be broken, because a cell
might only work thanks to a variable defined in a cell *below* it, or in a cell you already
deleted. That hidden, out-of-order state is the **#1 source of notebook confusion in this course**
— and restart-and-run-all is how you catch it before it bites.

Two things to read off the result:

- **The execution counts should be `1, 2, 3, …` in order.** That ascending sequence is the visible
  proof of a clean linear run. If you ever see scrambled counts like `[7]`, `[3]`, `[12]`, that's
  the fingerprint of an out-of-order session — restart-and-run-all to fix it.
- **The first code cell did all the setup.** Notice that imports and any data loading live in the
  **first code cell**, so the fresh kernel has everything it needs before any later cell runs. That
  ordering is *why* a top-to-bottom run can succeed at all — it's the structural half of this
  discipline. When you write your own notebooks in the lessons, put all imports in that first cell,
  never scattered further down.

**This is K03's pass checkpoint:** a clean restart-and-run-all on a real notebook, with ascending
execution counts and no errors. If you got here, you can drive notebooks the way the course
expects.

**If it breaks:** read the *first* error, not the last. `ModuleNotFoundError` or a config/key error
→ the kernel isn't the pinned env or your K02 key isn't set (relaunch with `uv run jupyter lab`;
re-check `.env` from K02). A `NameError` on a variable that "should" exist → that's exactly the
out-of-order trap this step exists to expose: some cell depends on state that a clean run doesn't
have. If it's *your* notebook, move the missing definition earlier; for a course notebook, report
it — a lesson notebook that fails restart-run-all is a bug.

## Step 4 — Notice top-level `await` (you'll learn it in K05)

**Do:** as you scroll lesson notebooks, you'll come across a cell that runs something like:

```python
result = await some_async_call(...)   # no asyncio.run(...) wrapper
```

**You should see:** it runs like any other cell — no error, no special ceremony.

**What just happened / why it matters:** Jupyter lets you write `await` **directly at the top level
of a cell**, without wrapping it in `asyncio.run(...)`, because the notebook is already running
inside an event loop. **You do not need to understand what `async`/`await` mean yet** — just
recognize the syntax so it isn't startling when a lesson uses it. **K05 (async concepts)** is where
you'll actually learn what this does and why the agent course leans on it.

## Step 5 — Clear live output before you commit

**Do (only when you're about to commit a notebook you changed):** clear the outputs of the
**student `_empty`** copies with the repo's pinned tool:

```sh
uv run jupyter nbconvert --clear-output --inplace src/fluffy_potato_curriculum/lessons/**/*_lab_empty.ipynb
```

**You should see:** the command rewrite those notebooks in place with their cell outputs stripped.

**What just happened / why it matters:** this makes K02's "never commit live output" rule concrete.
Notebook cells that hit the live API produce output that is **paid and nondeterministic**, so it
must not be committed — a fresh clone should start clean and re-run it. The course splits notebooks
by name for exactly this:

- **`_empty`** — the student copy you fill in. **Always cleared before commit** (the command above).
- **`_solutions`** and **lecture** notebooks — reference copies that *may* keep their outputs as a
  rendered example. That's why the command targets only `*_lab_empty.ipynb` — a blanket strip would
  wipe the reference outputs you want to keep.

**If it breaks:** nothing to break here — but note the glob (`**`) needs a shell that expands it
(zsh does by default; in bash you may need `shopt -s globstar`). If it matches nothing, you're
either not at the repo root or there are no `_empty` notebooks to clear yet.

## Done — and the hook into K04

You can now launch JupyterLab on the pinned kernel, run a notebook the way the course expects
(restart-and-run-all, setup cell first, clean ascending execution counts), recognize top-level
`await`, and clear live output before committing. What you *can't* do fluently yet is **read** the
code inside those cells — the repo is strict-typed and pydantic-heavy. **K04 (Python you'll read:
types & pydantic)** picks up there, so the lesson notebooks stop looking foreign.
