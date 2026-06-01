# Python style

Conventions for all Python in this repo. These reflect the enforced config in
[pyproject.toml](../../pyproject.toml) — when in doubt, run the tools rather than guess.

## Baseline

- **Target:** Python 3.13. Use modern syntax freely (`X | None`, `match`, `list[int]`,
  built-in generics — never `typing.List`/`Optional`).
- **Formatter is authoritative.** Run `uv run ruff format`; never hand-format. Double quotes,
  space indent, 100-col line length (the formatter wraps; `E501` is intentionally ignored).
- **Lint clean.** `uv run ruff check` must pass. Active rule sets: `E/W` (pycodestyle),
  `F` (pyflakes), `I` (isort — let ruff sort imports), `B` (bugbear), `UP` (pyupgrade),
  `SIM` (simplify), `RUF`. Prefer `--fix` for mechanical issues; fix real warnings by hand.

## Typing (pyright strict)

- `uv run pyright` runs in **strict** mode. Every public `def` must be fully annotated —
  params and return. An untyped `def` fails the build.
- Annotate return types explicitly, including `-> None`.
- No implicit `Any`. If a third-party value is untyped, narrow or cast it deliberately;
  don't let `Any` propagate.
- Avoid `# type: ignore` — prefer fixing the type. If unavoidable, scope it to the specific
  rule (`# pyright: ignore[reportX]`) and add a one-line why.

## Layout & imports

- `src/` layout only. Import via the package path
  (`from fluffy_potato_curriculum.lessons.L03 import ...`); never import from a top-level dir.
- Lesson code lives under `src/fluffy_potato_curriculum/lessons/L<NN>/` (zero-padded).
- Keep imports at module top, sorted by ruff's isort. No conditional/lazy imports unless
  there's a real reason (heavy optional dep, circular-import break) — note it in a comment.

## Curriculum-specific

- This is teaching code: clarity beats cleverness. Prefer explicit, readable steps over
  dense one-liners, even when a comprehension would be shorter.
- Comment the *why*, not the *what*. Assume a semi-technical Python learner reads this.
- New runtime deps go through `uv add` (dev deps `uv add --dev`) so `uv.lock` stays in sync —
  never hand-edit `pyproject.toml`.
