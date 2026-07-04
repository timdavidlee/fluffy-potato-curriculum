# K01 — Environment & tooling

This is the first thing you do in the course — before `L01`, before any other unit. By the end
you'll have a working local checkout with the project's pinned environment, and you'll be able to
run any project command through `uv`.

## How to read this guide

The unit is a single ordered sequence you work through **alone, at a keyboard**. There is no
separate lab — this walkthrough *is* the hands-on work. Each **Step** has:

- **Do** — the exact command(s) to run. Copy-paste is fine; that's the point.
- **You should see** — what a success looks like, so you know whether to continue.
- **What just happened / why it matters** — a short concept callout. Read it *after* the command
  works — the idea sticks better once you've seen it happen.
- **If it breaks** — the most common failure and its fix, inline.

Work top to bottom. Don't skip the callouts — they're the concepts `L01` onward assumes you've
absorbed. Budget ~20–30 minutes. The finish line is a green test suite (Step 6).

> One habit to adopt now: **every command in this course starts with `uv run`** (except the few
> setup commands in Steps 1–3). If a later unit ever says "run `pytest`," it means
> `uv run pytest`. Step 4 explains why.

## Step 0 — Prerequisites (one-time)

**Do:** confirm you have a terminal and `git`:

```sh
git --version
```

**You should see:** a version like `git version 2.4x`. If instead you get "command not found,"
install git first (macOS: `xcode-select --install`; Linux: your package manager; Windows: use
**WSL2** and follow the Linux path).

**Why it matters:** git is how you get the code and (optionally) contribute changes back. It's
the one tool we assume rather than install.

## Step 1 — Install `uv`

**Do:** install the toolchain that runs everything else:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then **open a new terminal** (so your `PATH` picks up `uv`) and confirm:

```sh
uv --version
```

**You should see:** a `uv` version string.

**What just happened / why it matters:** `uv` is this course's single entry point for Python,
virtual environments, dependencies, and running code. You install it **once**; from here on it
manages everything else — including the exact Python version — so you never install Python
by hand.

**If it breaks:** if `uv --version` says "command not found," your shell didn't pick up the new
`PATH`. Fully close and reopen the terminal, or run the `source` line the installer printed.

## Step 2 — Clone the repository and enter it

**Do:**

```sh
git clone https://github.com/timdavidlee/fluffy-potato-curriculum.git
cd fluffy-potato-curriculum
ls
```

**You should see:** top-level markers that tell you you're in the right place —
`pyproject.toml`, `uv.lock`, `.python-version`, a `src/` directory, and `README.md`.

**What just happened / why it matters:** those four files are the fingerprint of a
`uv`-managed, pinned project:

- `pyproject.toml` — declares the project and its dependencies.
- `uv.lock` — the **exact, resolved** versions of every dependency (direct and transitive).
- `.python-version` — pins the Python interpreter (3.13).
- `src/` — where all the course code lives (more in Step 5).

**If it breaks:** "permission denied" or an auth prompt usually means the clone URL needs
credentials — make sure you can reach the repo on GitHub with your account.

## Step 3 — Create the pinned environment with `uv sync`

**Do:**

```sh
uv sync
```

**You should see:** `uv` download/provision Python 3.13 if needed, resolve the locked
dependencies, and create a `.venv/` directory. It exits `0` (no error). Confirm the folder is
there:

```sh
ls .venv        # bin/ (Scripts/ on Windows), lib/, pyvenv.cfg — this is your virtual environment
```

**What just happened / why it matters — the load-bearing concept of this unit:**

First, *what is that `.venv/` folder?* It's a **virtual environment**: a **self-contained,
project-local Python** — its own copy of the interpreter and its own installed packages — that
lives inside this project and is **isolated** from your system Python and from every other
project on your machine. Why bother? Because without isolation, two projects that need different
versions of the same package fight each other, and `pip install`-ing things globally slowly
rots your system Python. With a venv, everything this project needs is quarantined in `.venv/`
and **cannot break anything outside it**.

Second, `uv sync` didn't just *create* that venv — it filled it from `uv.lock` +
`.python-version` with the **exact** locked versions. Every student in the cohort runs this same
command and gets a **byte-for-byte identical `.venv/`**. That's why "it works on my machine but
not yours" stops being a class-wide problem — the lockfile, not your machine, is the source of
truth.

> **You do not need to "activate" anything.** Traditionally you'd turn a venv on with
> `source .venv/bin/activate` (`.venv\Scripts\activate` on Windows) and off with `deactivate`.
> That still works and you'll see it in other tutorials — but this course uses **`uv run`
> instead** (next step), which enters the venv automatically for a single command. Mentioned only
> so the concept isn't a mystery; you can ignore `activate` for this course.

Two corollaries worth internalizing now:

- **`.venv/` is disposable.** It's *derived* from the lockfile. If it ever gets into a weird
  state, delete it and run `uv sync` again — nothing irreplaceable lives there.
- **You never hand-edit `pyproject.toml`.** When you eventually need a new package, you'll run
  `uv add <pkg>` so the lockfile stays in sync. (You don't need this yet — just know the rule
  exists.)

**If it breaks:** the usual causes are being in the wrong directory (no `pyproject.toml` here →
`cd` into the repo) or a flaky network during download (re-run `uv sync`).

## Step 4 — Run code with `uv run`

**Do:** run a throwaway command *through* `uv`:

```sh
uv run python -c "import sys; print(sys.version)"
```

**You should see:** Python **3.13.x** printed — the pinned interpreter, not whatever `python`
your system happens to have.

**What just happened / why it matters:** `uv run <command>` executes the command **inside the
pinned `.venv`** automatically — no manual "activate the virtualenv" step. This is why the whole
course prefixes commands with `uv run`:

- `uv run pytest` → the project's tests, in the right env.
- `uv run ruff check` → the linter the project pins.
- `uv run jupyter lab` → the notebook server (K03).

**The failure mode to recognize:** a bare `python foo.py` runs your *system* Python, which
doesn't have the project's dependencies — you'll get `ModuleNotFoundError`. When that happens,
99% of the time the fix is "you forgot `uv run`."

## Step 5 — Get oriented in the `src/` layout

**Do:** look at where the code lives:

```sh
ls src/fluffy_potato_curriculum
```

**You should see:** the subsystems you'll spend the course in — `lessons/` (the `L<NN>/` and
`K<NN>/` materials), `common/` (shared runtime), `potato_llm/` (the LLM client seam), and
`local_ui/` (a local viewer).

**What just happened / why it matters:** this project uses the **`src/` layout** — code lives
under `src/fluffy_potato_curriculum/` and you import it by its **package path**:

```python
from fluffy_potato_curriculum.lessons.L01 import ...
```

The one rule that affects you as a student: **import by the package path, never from a bare
top-level folder.** If an import line looks "too long," that's correct — it's the full path, and
it's what lets `uv run` find the code reliably.

## Step 6 — Prove it works: run the tests (pass checkpoint)

**Do:**

```sh
uv run pytest
```

**You should see:** pytest collect a suite of tests and report them passing (exit `0`).

**What just happened / why it matters:** a green suite is proof that three things line up at
once — the pinned interpreter, the locked dependencies, and the `src/` imports. **This is K01's
pass checkpoint.** If you got here, your environment is real and you're cleared for K02.

**If it breaks:** re-read the error's first line. `ModuleNotFoundError` → you dropped the
`uv run` prefix, or `uv sync` didn't finish (re-run it). "no tests ran / wrong directory" → make
sure you're at the repo root. A genuinely stale env → delete `.venv/` and `uv sync` again.

## Step 7 — (Optional) Enable the commit-message hook

**Do (only if you plan to commit):**

```sh
git config core.hooksPath .githooks
```

**What just happened / why it matters:** this points git at the repo's `.githooks/`, enabling a
`prepare-commit-msg` helper that drafts commit messages for you. It's a convenience, **entirely
optional**, and safe to skip if you just want to run and read code. Nothing later depends on it.

## Done — and the hook into K02

You now have a working, pinned environment and can run any project command with `uv run`. The
one thing you *can't* do yet is call a live model — there are no API keys wired up. That's
exactly what **K02 (Keys & the config seam)** sets up next: real credentials, loaded the safe
way through `common/config.py`, plus the hygiene rules for the real, paid API calls the course
makes.
