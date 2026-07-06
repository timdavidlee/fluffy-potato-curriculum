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

## MCP servers

Claude Code can connect to [MCP](https://modelcontextprotocol.io) servers for extra tools
(e.g. design/asset tools, ticket trackers). Add one with:

```sh
claude mcp add <name> -s <scope> -- <command> [args...]
```

- `-s local` (default) — only you, only in this project.
- `-s user` — only you, across every project on this machine. Use this for personal tools
  that aren't specific to this repo (e.g. Canva).
- `-s project` — written to a checked-in `.mcp.json`, shared with anyone who clones the repo.
  Only use this for servers the whole team needs for curriculum work.

List configured servers with `claude mcp list`; remove one with `claude mcp remove <name>`.

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

The lesson arc (`L01`–`L25`):

1. LLM and token basics
2. Prompting fundamentals
3. Single-node operations
4. Directed graphs: sequential chaining
5. Conditional graphs: routing & branching
6. Teaching an LLM to think via prompting
7. Tool calling: how it works
8. Designing good tools
9. MCP: packaging tools as a portable contract
10. Cyclic graphs: the ReAct agent loop
11. Shallow agents in LangGraph
12. What an agent generates: state, logs, traces & extracts
13. Evaluation: first pass
14. Choosing model power for the task
15. LangGraph design patterns
16. Agent middleware and conditional tools
17. Human-in-the-loop and approval gates
18. Deep agents vs. shallow agents
19. Static system prompt vs. context management
20. Embeddings and vector similarity
21. RAG pipeline
22. Skills: just-in-time capabilities for agents
23. Skill patterns & composition
24. Multi-agent / subagent architecture (stretch)
25. Evaluation revisited

The mini track is a 14-lesson subset closing with `L50` (agent mini-project walkthrough) — see
the [Syllabus](src/fluffy_potato_curriculum/lessons/SYLLABUS.md).
