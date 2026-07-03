# fluffy-potato-curriculum

Python curriculum repository: code + materials. Claude Code is the primary driver for changes here.

## Rules

Detailed, enforced conventions live in [.claude/rules/](.claude/rules/). Read the relevant
file before writing code:

- [python-style.md](.claude/rules/python-style.md) — formatting, lint rule sets, pyright-strict typing, src layout.
- [pytest.md](.claude/rules/pytest.md) — test layout, strict markers, fixtures, LLM/network mocking.
- [notebooks.md](.claude/rules/notebooks.md) — keep notebooks short, reproducible (restart-run-all), gated live calls, output hygiene.

## Toolchain

- **Package/env manager:** [uv](https://github.com/astral-sh/uv) (managed lockfile in `uv.lock`).
- **Linter/formatter:** [ruff](https://docs.astral.sh/ruff/) (config in `pyproject.toml`).
- **Type checker:** [pyright](https://microsoft.github.io/pyright/) in `strict` mode.
- **Tests:** [pytest](https://docs.pytest.org/).
- **Commits:** [commitizen](https://commitizen-tools.github.io/commitizen/) — Conventional Commits + version bumps (config in `pyproject.toml`).
- **Python:** 3.13 (pinned in `.python-version`).

## Layout

```
src/fluffy_potato_curriculum/common      # shared runtime layer imported across lessons
src/fluffy_potato_curriculum/potato_llm   # provider-agnostic LLM client seam
src/fluffy_potato_curriculum/lessons      # generated teaching materials, one L<NN>/ per lesson
src/fluffy_potato_curriculum/projects     # end-of-week project briefs + starter code
src/fluffy_potato_curriculum/local_ui     # local read-only FastAPI viewer for lesson materials
tests/                                    # pytest tests (mirrors src/ one-to-one)
```

Each subsystem has a local map — read it before working in that tree:

- [common/CLAUDE.md](src/fluffy_potato_curriculum/common/CLAUDE.md) — the config seam, agent loop, tracing, and eval harness shared across the agent-arc lessons.
- [potato_llm/CLAUDE.md](src/fluffy_potato_curriculum/potato_llm/CLAUDE.md) — the hand-rolled `PotatoLLMClient` interface and its Anthropic/OpenAI implementations.
- [lessons/CLAUDE.md](src/fluffy_potato_curriculum/lessons/CLAUDE.md) — how `L<NN>/` materials are laid out and generated from roadmaps.
- [projects/CLAUDE.md](src/fluffy_potato_curriculum/projects/CLAUDE.md) — end-of-week brief structure and the Claude-maintained idea bank.
- [local_ui/CLAUDE.md](src/fluffy_potato_curriculum/local_ui/CLAUDE.md) — a local, read-only FastAPI server for browsing/reviewing lesson materials in a browser.
- [docs/origin/CLAUDE.md](docs/origin/CLAUDE.md) — the curriculum design docs and lesson roadmaps that drive generation.

Curriculum modules go under `src/fluffy_potato_curriculum/lessons/L<NN>/` where `<NN>` is the
zero-padded lesson number (e.g. `L01`, `L10`). Companion materials (notebooks, datasets, slides)
live in that lesson's directory alongside the lesson code.

End of the week - Project briefs, any starter code or dataset retrieval or transformations
will be in the `projects/` directory

## Common commands

Run everything through `uv` so the pinned `.venv` is used:

| Task | Command |
| --- | --- |
| Install / sync deps | `uv sync` |
| Add a runtime dep | `uv add <pkg>` |
| Add a dev-only dep | `uv add --dev <pkg>` |
| Run a script | `uv run python path/to/script.py` |
| Format | `uv run ruff format` |
| Lint | `uv run ruff check` |
| Lint with autofix | `uv run ruff check --fix` |
| Typecheck | `uv run pyright` |
| Tests | `uv run pytest` |
| Guided commit | `uv run cz commit` |
| Check commit message | `uv run cz check --rev HEAD` |
| Bump version + changelog | `uv run cz bump` |

Before committing, the bar is: `uv run ruff format && uv run ruff check && uv run pyright && uv run pytest`.

## Conventions

- Type-annotate public functions; pyright runs in `strict` so untyped `def` will fail.
- Prefer the `src/` layout — never import from a top-level package directory.
- Keep test files mirroring the module path: `src/fluffy_potato_curriculum/foo/bar.py` → `tests/foo/test_bar.py`.
- New runtime dependencies must go through `uv add` (not hand-edited into `pyproject.toml`) so the lockfile stays in sync.

## Git hooks

A `prepare-commit-msg` hook in [.githooks/](./.githooks/) drafts a commit message via the `claude` CLI when you run `git commit` without `-m`. It silently no-ops when:

- a message source is already set (`-m`, `-F`, merge, squash, amend),
- nothing is staged, or
- the `claude` binary isn't on `$PATH`.

Hooks live under version control but git only honors them after you point `core.hooksPath` at the directory. Run this once per clone:

```sh
git config core.hooksPath .githooks
```

To bypass the hook for a single commit, just pass `-m`: `git commit -m "your message"`.
