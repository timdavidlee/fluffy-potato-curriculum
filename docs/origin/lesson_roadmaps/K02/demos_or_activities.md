# K02: Self-paced walkthrough — Keys & the config seam

> Sibling docs: [objectives.md](objectives.md), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md).
>
> **Audience:** the *student*, alone at a keyboard. Every step is something you run yourself. Same
> "Do → You should see → why it matters → If it breaks" shape as [K01](../K01/demos_or_activities.md).

## How to read this file

Work top to bottom; budget ~15 minutes. The finish line is a smoke check that proves your key is
reachable through the project's config seam (Step 4). **Reminder:** every command is `uv run …`
(K01, Step 4).

> **Money warning up front:** the calls in this course are **real and billed to your key.** They
> are tiny by design (a few tokens), but treat your key like a credit-card number — never paste it
> into a chat, a commit, or a screenshot.

## Step 1 — Copy the template to `.env`

**Do:**

```sh
cp .env.example .env
```

**You should see:** a new `.env` file at the repo root. Look at the template it came from:

```sh
cat .env.example
```

It lists the variables the project reads (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`) with **no
values**.

**What just happened / why it matters:** there are two files on purpose:

- **`.env.example`** — committed to git, **keyless**. Its only job is to document *which*
  variables exist, so a new student knows what to fill in.
- **`.env`** — your real, private copy with actual secret values. It is **gitignored** and must
  never be committed.

## Step 2 — Confirm `.env` is gitignored (do this before adding your key)

**Do:**

```sh
git status
git check-ignore .env
```

**You should see:** `git status` does **not** list `.env` as a new file, and `git check-ignore
.env` prints `.env` (confirming it's ignored).

**What just happened / why it matters:** you verified the safety net *before* putting a secret in
the file. If `.env` ever *did* show up in `git status`, stop — do not commit — and check
`.gitignore`. A key committed to git history is compromised even after you delete it.

## Step 3 — Add your Anthropic key

**Do:** open `.env` in an editor and fill in your key (obtain it from the Anthropic console, or
use the instructor-issued key — see the open question in [objectives.md](objectives.md)):

```sh
# .env
ANTHROPIC_API_KEY=sk-ant-...your-real-key...
OPENAI_API_KEY=            # leave blank unless a lesson says otherwise
```

Save the file.

**What just happened / why it matters:** the key now lives **only** in your untracked `.env`. The
project reads it from there — you never hard-code a key into a notebook or a `.py` file, and you
never look it up with a scattered `os.environ["ANTHROPIC_API_KEY"]`. The next step shows the one
correct doorway.

## Step 4 — Reach the key through the config seam (pass checkpoint)

**Do:**

```sh
uv run python -c "from fluffy_potato_curriculum.common.config import require_anthropic_key; require_anthropic_key(); print('key wired ✓')"
```

**You should see:** `key wired ✓`.

**What just happened / why it matters — the load-bearing concept:** you reached your key through
`fluffy_potato_curriculum.common.config` — the project's **single, typed doorway** to all
configuration. Under the hood it's a `pydantic-settings` `Settings` object that automatically
reads your environment **and** your `.env`, so `anthropic_api_key` is filled from
`ANTHROPIC_API_KEY`. The rule for the whole course:

> **All config is read through `common/config.py` — `get_settings()`, `require_anthropic_key()`,
> `require_openai_key()` — never via ad-hoc `os.environ[...]` scattered around the codebase.**

Why one doorway? Because `require_anthropic_key()` **fails fast and readable**: if the key is
missing or in the wrong place, you get a clear sentence right away —

**If it breaks:** if you see `ANTHROPIC_API_KEY is not set…`, the seam is working correctly and
telling you the key isn't reaching it. Check: is the key actually in `.env` (not `.env.example`)?
Is `.env` at the **repo root**? Did you save the file? No quotes needed around the value.

## Step 5 — (Optional) one tiny live call

**Do:** if you want end-to-end proof, make the smallest possible real call through the
`potato_llm` seam (this is the same smoke call K06's final go/no-go uses):

```sh
uv run python -c "
from fluffy_potato_curriculum.potato_llm import ...   # <need input: exact client entry point + minimal async call snippet>
# keep it tiny: a few max_tokens, one call
"
```

**You should see:** a short model reply. **What just happened / why it matters:** you just spent a
fraction of a cent. That's the whole hygiene lesson made real: **keep calls small (low
`max_tokens`) and few**, go through the `potato_llm` seam (so a canned client can replace the live
one where a real call isn't the point), and **clear any live output before committing** a notebook.

## Done — and the hook into K03

Your key is wired and reachable the safe way. Next you'll run code **interactively** in Jupyter,
where these live calls usually happen. **K03 (Jupyter workflow)** covers `uv run jupyter lab`, the
restart-and-run-all habit, top-level `await` in cells — and puts the "clear live output before you
commit" rule into practice.
