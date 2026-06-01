## Summary

<!-- What does this PR change and why? One or two sentences. -->

## Type of change

<!-- Mirrors the Conventional Commit types enforced by commitizen. Check all that apply. -->

- [ ] `feat` — new lesson/project content or runtime feature
- [ ] `fix` — bug fix
- [ ] `docs` — docs, roadmaps, or briefs only
- [ ] `refactor` — code change that neither fixes a bug nor adds a feature
- [ ] `test` — adding or fixing tests
- [ ] `chore` / `build` / `ci` — tooling, deps, or config

## Details

<!-- Anything a reviewer needs: design choices, trade-offs, follow-ups, screenshots. -->

## Checklist

- [ ] Commits follow [Conventional Commits](https://www.conventionalcommits.org/) (`uv run cz commit` or `uv run cz check`)
- [ ] `uv run ruff format` — formatted
- [ ] `uv run ruff check` — lint clean
- [ ] `uv run pyright` — type clean (strict)
- [ ] `uv run pytest` — tests pass
- [ ] New runtime deps added via `uv add` (lockfile in sync)
- [ ] Tests mirror the `src/` path one-to-one
