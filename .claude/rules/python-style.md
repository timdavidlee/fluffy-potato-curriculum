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

## Functions vs. classes

- **Prefer plain functions.** A function with a few typed parameters is the default unit of
  code here — reach for it before a class. Free functions are easier to read, test, and teach.
- **When the parameter list grows unwieldy** (rough rule of thumb: more than ~4–5 positional
  args, or you find yourself threading the same bundle of values through several functions),
  stop passing loose arguments and pick one of:
  - a **class** when there's genuine mutable state or behavior to manage across calls
    (e.g. a client that holds a connection, a stateful builder), or
  - a **Pydantic model** when you just need to pass a structured bundle of data around —
    a typed, validated container is clearer than a long signature or a bare `dict`.
- Don't introduce a class purely to group functions that share no state — that's a module's
  job. Use a class when state or lifecycle justifies it, not as a namespace.
- **Everything stays fully type-annotated** regardless of which shape you choose (see the
  Typing section): function params and returns, class attributes, and Pydantic fields.

## Docstrings

- **Private/helper functions can keep docstrings minimal** — a one-line summary is fine, or
  none at all when the name and signature already say everything.
- **When a function has a complex or loosely-typed shape, show a concrete example.** If a
  param or return is a generic container whose structure isn't obvious from the type alone —
  `dict[str, Any]`, `list[dict[str, Any]]`, nested/heterogeneous structures — include a small
  foo-bar example of the actual shape in the docstring:

  ```python
  def parse_events(raw: list[dict[str, Any]]) -> dict[str, Any]:
      """Group raw events by type.

      Example input:
          [{"type": "click", "x": 10}, {"type": "key", "code": "Esc"}]
      Example output:
          {"click": [{"x": 10}], "key": [{"code": "Esc"}]}
      """
  ```

  The example matters more than prose here — a reader should see the shape at a glance instead
  of reverse-engineering it from `dict[str, Any]`.
- This pairs with the typing rules: prefer a Pydantic model or `TypedDict` when the shape is
  fixed and worth naming. The example-in-docstring guidance is for the genuinely dynamic cases
  where a precise type isn't practical.

## Code reuse & structure

- **Check for existing functionality before writing new code.** Before adding a helper,
  parser, client wrapper, etc., search the repo (`rg`/grep, or scan the relevant package)
  for something that already does it. Reuse or extend the existing thing rather than
  introducing a parallel implementation.
- **Shared functionality lives in a `common` package.** When logic is used by more than one
  lesson/project/module — or you can see it about to be — move it to
  `src/fluffy_potato_curriculum/common/` and import it from there, rather than copy-pasting
  or leaving it buried in one lesson. Keep lesson-specific code in the lesson; promote to
  `common/` only once it's genuinely shared.
- **Be minimal and precise.** Add the smallest change that solves the problem. Don't
  speculatively generalize, add unused parameters/branches, or build abstractions for a
  second caller that doesn't exist yet. New code should read like the code already around it.

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
