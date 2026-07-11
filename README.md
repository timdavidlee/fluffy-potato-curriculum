# fluffy-potato-curriculum

Python curriculum: code + materials for an agents-focused course. Driven via Claude Code.

## Quick start

```sh
uv sync                                # install deps into the pinned .venv
cp .env.example .env                   # then fill in your API keys (live LLM calls)
uv run pytest                          # run the test suite
git config core.hooksPath .githooks    # one-time, enables the commit-message hook
```

## Local lesson viewer

A read-only FastAPI viewer for browsing the generated lesson materials in a browser:

```sh
uv run python -m fluffy_potato_curriculum.local_ui   # serves http://127.0.0.1:8000/
```

`HOST` / `PORT` env vars override the bind address. See
[local_ui/CLAUDE.md](src/fluffy_potato_curriculum/local_ui/CLAUDE.md) for details.

## Documentation

- [Curriculum PRD](docs/origin/CURRICULUM_PRD.md) — the primary design doc: course intent,
  objectives, and the full lesson plan.
- [CLAUDE.md](./CLAUDE.md) — toolchain, repo layout, common commands, and conventions.
- [.claude/rules/](.claude/rules/) — enforced style rules:
  [python-style](.claude/rules/python-style.md),
  [pytest](.claude/rules/pytest.md),
  [notebooks](.claude/rules/notebooks.md).
- [Syllabus](src/fluffy_potato_curriculum/lessons/SYLLABUS.md) — mini vs full track membership
  (defined in [tracks.toml](src/fluffy_potato_curriculum/lessons/tracks.toml)).
- [docs/](docs/CLAUDE.md) — design source (`origin/`), tracking notes (`todos/`), and handoffs.

Each subsystem under `src/fluffy_potato_curriculum/` has a local `CLAUDE.md` map — see the
Layout section of [CLAUDE.md](./CLAUDE.md) for the full list.

### Topics

Required prework (`K01`–`K06`, before `L01`): environment & tooling · keys & the config seam ·
Jupyter workflow · types & pydantic · async concepts · Docker & the multi-container stack.

The lesson arc (`L01`–`L25`; `L04` is a reserved gap — the former "Directed graphs: sequential
chaining" was merged into `L03` on 2026-07-09, and downstream lessons were not renumbered):

- `L01` — LLM and token basics
- `L02` — Prompting fundamentals
- `L03` — Directed graphs: from one node to a sequential chain
- `L05` — Conditional graphs: routing & branching
- `L06` — Teaching an LLM to think via prompting
- `L07` — Tool calling: how it works
- `L08` — Designing good tools
- `L09` — MCP: packaging tools as a portable contract
- `L10` — Cyclic graphs: the ReAct agent loop
- `L11` — Shallow agents in LangGraph
- `L12` — What an agent generates: state, logs, traces & extracts
- `L13` — Evaluation: first pass
- `L14` — Choosing model power for the task
- `L15` — LangGraph design patterns
- `L16` — Agent middleware and conditional tools
- `L17` — Human-in-the-loop and approval gates
- `L18` — Deep agents vs. shallow agents
- `L19` — Static system prompt vs. context management
- `L20` — Embeddings and vector similarity
- `L21` — RAG pipeline
- `L22` — Skills: just-in-time capabilities for agents
- `L23` — Skill patterns & composition
- `L24` — Multi-agent / subagent architecture (stretch)
- `L25` — Evaluation revisited

The mini track is a 13-lesson subset closing with `L50` (mini-project walkthrough) — see
the [Syllabus](src/fluffy_potato_curriculum/lessons/SYLLABUS.md).
