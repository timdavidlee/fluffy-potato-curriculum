# Pytest

How tests are written and run in this repo. Config lives in
[pyproject.toml](../../pyproject.toml) under `[tool.pytest.ini_options]`.

## Running

- Always via uv: `uv run pytest`. Tests are collected from `tests/` only (`testpaths`).
- `addopts = "-ra --strict-markers --strict-config"` is active:
  - `--strict-markers` — every `@pytest.mark.<x>` must be registered in `pyproject.toml`
    first, or collection errors. Don't invent ad-hoc markers.
  - `--strict-config` — unknown config keys fail fast.
  - `-ra` — a short summary of non-passing tests prints after each run.

## Layout

- The `tests/` tree **mirrors the `src/` tree one-to-one**. Every module gets a sibling test
  file at the same relative path:
  `src/fluffy_potato_curriculum/lessons/L03/foo.py` → `tests/lessons/L03/test_foo.py`.
  Mirror the directory structure exactly — don't flatten or regroup tests.
- Files are `test_*.py`, functions are `test_*`, classes (rare) are `Test*`.
- Each test dir needs an `__init__.py` (matches the existing `tests/` package layout).

## Writing tests

- **Prefer a single assert per test.** Each test pins one behavior with one assertion; if you
  reach for a second `assert`, that's usually a second test (or a parametrize case). A few
  tightly-related asserts on one logical outcome are fine — many asserts checking different
  behaviors is not.
- **Use pytest-native structures, not `unittest`.** Plain `assert` (pytest rewrites it for rich
  diffs), `pytest.raises`, `pytest.fixture`, `tmp_path`, `monkeypatch`, `capsys`. Never
  `unittest.TestCase`, `self.assertEqual`, `setUp`/`tearDown`, or `@mock.patch` decorators —
  use the `monkeypatch` fixture instead.
- **Prefer `@pytest.mark.parametrize` for repetition.** Any time tests differ only in
  inputs/expected values, collapse them into one parametrized test rather than copy-pasting —
  it keeps the single-assert shape and makes the case table obvious. (Remember `--strict-markers`:
  `parametrize` is built in and fine; custom markers must be registered first.)
- Prefer **fixtures** over setup/teardown; keep them in a local `conftest.py` when shared
  across a directory.
- **Annotate test functions** too — `def test_x() -> None:`. pyright strict covers `tests/`,
  so untyped test defs fail the typecheck even though ruff's `B`/`SIM` are relaxed there.
- One behavior per test; name it for the behavior (`test_rejects_empty_prompt`), not the
  function under test.
- Use `tmp_path`/`monkeypatch` for filesystem and env isolation — never touch real files,
  cwd, or global state.

## LLM / network boundaries

- This repo calls the Anthropic/OpenAI SDKs. **Never hit a live API in a test** — mock the
  client or stub responses. Tests must be deterministic and offline.
- Put shared fakes (e.g. a canned LLM response) in a fixture, not inline per test.

## Before committing

Full gate (from CLAUDE.md):
`uv run ruff format && uv run ruff check && uv run pyright && uv run pytest`.
