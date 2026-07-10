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

- This repo calls the Anthropic/OpenAI SDKs. **The default suite never hits a live API** —
  mock the client or stub responses. `uv run pytest` must be deterministic and offline.
- Put shared fakes (e.g. a canned LLM response) in a fixture, not inline per test.
- **Live-API tests are the one sanctioned exception, and they are opt-in.** Mark any test
  that makes a real model call `@pytest.mark.integration` (registered in `pyproject.toml`).
  The default `addopts` carries `-m "not integration"`, so those tests are *deselected* from
  `uv run pytest` and never run in the offline gate; run them deliberately with
  `uv run pytest -m integration`. Guard each one with a `skipif` on the missing key (e.g.
  `get_settings().anthropic_api_key is None`) so an opt-in run without credentials skips
  cleanly instead of erroring. Reserve this for behavior only a live model can exercise —
  seam and defensive-parse paths (which inject replies a real model won't produce) still
  belong in the offline `FakeModel` set. Live assertions are inherently non-deterministic:
  pin the robust property (an over-cap expense is *not approved*), not a brittle exact label.

## Before committing

Full gate (from CLAUDE.md):
`uv run ruff format && uv run ruff check && uv run pyright && uv run pytest`.
