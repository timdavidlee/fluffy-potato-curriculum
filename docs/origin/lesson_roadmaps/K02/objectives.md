# K02: Keys & the config seam

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (Prework track row K02).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).
> Sibling doc: [demos_or_activities.md](demos_or_activities.md) — the self-paced walkthrough.

## Format note

Self-paced student walkthrough, not lecture+lab — same shape as K01 (see
[K01/objectives.md](../K01/objectives.md) for the full format rationale). The paired
[demos_or_activities.md](demos_or_activities.md) is the runbook the student executes.

## Where this unit sits

K02 comes right after K01: the environment runs, but it has **no credentials**, so any code that
calls a live model fails. K02 wires the keys — the safe way — and sets the hygiene rules for the
**real, paid** API calls this course makes. It is a **hard environment gate** (alongside K06):
without keys through the config seam, most of `L01` onward can't run.

The single outcome: **the student has a working `.env` with their Anthropic key, reaches it only
through `common/config.py` (never scattered `os.environ`), and understands that calls cost real
money — so they keep them small and never commit keys or live output.**

## Prerequisites

- K01 complete: a working `uv` env, `uv run` understood, a green `uv run pytest`.
- An **Anthropic API key** the student can obtain (the course anchor provider, Claude Sonnet
  4.6). `<need input: are keys issued to students centrally (instructor-provisioned, spend-capped)
  or does each student create their own Anthropic account? Determines the K02 opening step and who
  owns the spend cap.>`

## Learning objectives

By the end of K02, a student should be able to:

1. **Create a `.env` from the template and fill in their key.** Concretely: `cp .env.example .env`,
   paste their `ANTHROPIC_API_KEY=…`, and confirm `.env` is **gitignored** (`git status` does not
   list it). The concept: **secrets live in `.env`, which never enters git** — the template
   (`.env.example`, committed, keyless) documents *which* variables exist; the real values live
   only in the untracked `.env`.

2. **Explain the config seam and reach a key through it — never `os.environ`.** Concretely:
   describe that `fluffy_potato_curriculum.common.config` is a **single, typed doorway** to all
   configuration — a `pydantic-settings` `Settings(BaseSettings)` that reads environment variables
   and the repo-root `.env`, exposing `get_settings()`, `require_anthropic_key()`,
   `require_openai_key()`, and `langfuse_configured()`. State the rule: **all code reads config
   through this seam, not via ad-hoc `os.environ["…"]` lookups scattered around.** Recognize *why*:
   one validated place to load/name/require config means a missing key fails **early with a clear
   message** (`require_anthropic_key()` raises a readable error) instead of a cryptic `KeyError`
   deep in a call.

3. **State the live-call hygiene rules and why they exist.** Concretely: articulate that this
   course makes **real, paid** model calls (the live demo is often the point), so the student must:
   - **keep calls small and few** — low `max_tokens`, a handful of calls — so a session costs
     cents, not dollars;
   - **never commit keys** (they're in gitignored `.env`) **or live output** (clear notebook
     outputs that hit the API before committing — nondeterministic and sometimes not free to
     re-expose);
   - go through the **`potato_llm` seam**, not a raw SDK, so a canned/offline client can be
     swapped in where a live call isn't the teaching point.

4. **Smoke-test the wiring.** Concretely: run a tiny check that proves the key is reachable
   through the seam (and, optionally, one minimal live call) — K02's pass signal (below).

## Concepts to highlight inline (the callouts)

- **`.env` vs `.env.example`.** Template is committed and keyless; the real file is untracked.
  Copy one to the other; never rename or commit the real one.
- **The config seam is the single doorway.** `common/config.py` is *the* place config is read and
  validated. Reaching around it with `os.environ` is the anti-pattern the course actively avoids.
- **Fail fast, fail readable.** `require_anthropic_key()` turns "missing key" into a clear
  sentence at the top of a run, not a stack trace 20 frames deep.
- **Real money.** Unlike a sandbox, these calls are billed. Small + few is a habit, not a
  nicety — it's the L01 cost lesson felt one unit early.
- **Never commit live output.** Notebook cells that hit the API get their output cleared before
  commit (this pairs with K03's restart-and-run-all discipline).

## Verify / pass checkpoint

K02 is "done" when the key is reachable through the seam:

```sh
uv run python -c "from fluffy_potato_curriculum.common.config import require_anthropic_key; require_anthropic_key(); print('key wired ✓')"
```

prints the success line (it raises a clear error if the key is missing/misplaced). An optional
second check makes **one minimal live call** through the `potato_llm` seam (low `max_tokens`) to
prove end-to-end reachability — this is the same smoke call K06's final go/no-go reuses.

## Bridge to K03

With keys wired, the student can make live calls — but the course's main surface for *running*
code interactively is **Jupyter**. K03 (Jupyter workflow) picks up here: `uv run jupyter lab`, the
restart-and-run-all discipline, and top-level `await` in cells — plus the "clear live output
before committing" rule K02 just introduced, now made concrete in a notebook.

## Open authoring questions

- `<need input: central instructor-issued keys (spend-capped) vs. student-created accounts — see
  Prerequisites. Also: is a shared Langfuse key set here too, or deferred to K06 where the stack
  comes up?>`
