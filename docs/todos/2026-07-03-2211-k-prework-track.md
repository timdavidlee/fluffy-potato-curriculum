# 2026-07-03 — `K<NN>` prework track: preflight requirements before `L01`

**Goal:** add a **prework track** students complete *before* the course proper — environment
setup + the mental models the lessons assume. It's a new lesson series prefixed **`K`** (for
"prework"), which also sorts *before* `L` alphabetically, so `K01…` precedes `L01` with **zero
renumbering** of the existing `L01…L25` plan. The K units are **required and gated**: a student
completes K01–K06 before starting `L01`.

Split out of `2026-07-03-2152-prefer-async-methods.md` (which now owns only the async-first code
change); this file owns the prework track. The two meet at **K05**, which teaches async and owns
the canonical "why async for agents" explainer the async-first work cross-references.

## Why a prework track

The repo assumes a lot before L01 that a semi-technical student won't have: a working `uv`/venv
env, API keys wired through the config seam, comfort driving Jupyter, the ability to *read*
strict-typed/pydantic/async code, and — now — a running multi-container Docker stack. Bundling
these into gated `K` units means the whole cohort starts L01 from one baseline instead of
debugging setup mid-lesson. Short single-topic units (per `.claude/rules/notebooks.md`), not one
mega-lesson.

## Breakout (confirmed) — K01–K06

- **K01 — Environment & tooling** — git clone, `uv sync` / `uv run`, venv & the pinned `.venv`,
  the `src/` layout, optional `git config core.hooksPath .githooks`.
- **K02 — Keys & the config seam** — `.env.example` → `.env`, `common/config.py`
  (`require_anthropic_key()`, never scattered `os.environ`), and live-call hygiene: notebooks
  make *real paid* calls, so keep them small/cheap and never commit keys or live output (`.env`
  is gitignored). From `.claude/rules/notebooks.md`.
- **K03 — Jupyter workflow** — `uv run jupyter lab`, the **restart-and-run-all** mental model,
  top-level `await` in cells.
- **K04 — Python you'll read** — a fast refresher for the semi-technical audience (types,
  functions, imports), plus **reading type hints** (`X | None` / `list[int]` / `-> None`; the
  repo is pyright-strict) and **what a pydantic model is** (`BaseSettings`, structured output,
  tool schemas).
- **K05 — async concepts** — `async`/`await`, the event loop, `asyncio.gather` for concurrency,
  top-level `await` (ties back to K03). **K05 owns the canonical "why async for agents"
  explainer** (concurrent tool calls, parallel eval cases, non-blocking traces / streaming) that
  the rest of the course cross-references — see the async-first TODO
  (`2026-07-03-2152-prefer-async-methods.md`) and the `invoke`/`ainvoke` pointer it defines.
- **K06 — Docker & the multi-container stack** — mandatory for everyone (see below).

## K06 — Docker & the multi-container stack (mandatory)

The course's local infra is genuinely **multi-service**, so students need real-minimum Docker
Compose literacy — not image authoring, just *bring the stack up, keep it up, read it when it
breaks*. **Docker is mandatory for every student**, not an opt-in fallback: everyone installs
Docker Desktop in K06 and brings the Compose stack up as part of setup, so later lessons can
assume a local database + agent service exist. Grounded in what the repo already commits to:

- **Langfuse (tracing) stack** — self-hosting Langfuse is **Langfuse server + PostgreSQL +
  ClickHouse** via the official Docker Compose ([classroom-llm-management.md:123](../classroom-llm-management.md)).
  Even where a student points at the shared instructor Langfuse instead of self-hosting, Docker
  is still required for the database + agent services below — so it's a universal prereq.
- **Database service** — L12 draws a plane boundary where extracted business data lands in a
  **database / object store**, not in trace spans. A local Postgres (or similar) service is the
  natural vehicle for the lessons that persist agent output.
- **Agent service** — the agent app itself run as a container alongside the DB + tracing services.

**What K06 should actually teach (real minima):**

- **Core concepts, briefly:** image vs. container vs. volume; a `compose.yaml` defines several
  **services** (containers) sharing one network and addressing each other by service name; ports
  map container→host; env vars pass through (`.env` again); **named volumes** hold the persistent
  data (Postgres/ClickHouse) that must survive a restart.
- **Start / stop / inspect each service:** `docker compose up -d`, `docker compose ps`,
  `docker compose logs -f <service>`, `docker compose down` — and the loaded footgun
  `docker compose down -v` (wipes volumes = deletes your Langfuse/DB data), called out explicitly.
- **Basic troubleshooting:** "is Docker Desktop running?", port-already-in-use, a container stuck
  restarting → read its logs, `depends_on`/healthcheck ordering (Langfuse waits on Postgres +
  ClickHouse), and disk-space/volume-reset when the DB won't come up.

## Gating — required before `L01`

The K units are **required and gated** — complete K01–K06 before starting `L01`.

- **Hard environment gates:** Docker-mandatory (K06) and the keys/config setup (K02).
- **Understanding gates:** the async / type-hints / pydantic units (K04–K05) so the agent arc can
  assume the mental model.
- **Concrete pass signal:** a K06 "does the stack come up?" check — `docker compose ps` all
  healthy + a smoke call through the config seam — is the go/no-go before `L01`.

## What to build (dependencies)

1. **The Compose stack** — no `compose.yaml` exists in the repo yet. Stand up Langfuse + Postgres
   + ClickHouse, plus the agent/DB services. K06's walkthrough should drive *that* file, so author
   them together.
2. **The `K<NN>` roadmap + material dirs** — roadmaps at `docs/origin/lesson_roadmaps/K<NN>/`,
   materials at `src/fluffy_potato_curriculum/lessons/K<NN>/`, following the same two-stage
   authoring flow as the L lessons (roadmap → generate materials).
3. **Track wiring** — `tracks.toml` / `SYLLABUS.md` gain a prework section; extend
   `docs/origin/CLAUDE.md`'s "monotonically increasing `L<NN>`" convention to note `K<NN>` as a
   parallel prework series ordered before `L01`.

## Reconcile with existing design docs (Docker-mandatory changes the current stance)

The current sources treat local Docker as *optional* — `classroom-llm-management.md` calls local
Docker the "solo/self-paced fallback" and L12's roadmap makes a keyless/offline run pass on the
hand-rolled trace alone ("Langfuse is the payoff, not a hard dependency"). Making Docker a
universal, gated prereq supersedes that framing. When this lands, update:

- `docs/classroom-llm-management.md` — reframe local Docker from fallback to baseline.
- `docs/origin/lesson_roadmaps/L12/objectives.md` — the "graceful/no-Docker" beats.
- `docs/origin/CURRICULUM_PRD.md` — add the `K<NN>` prework track to the plan.

## Open questions

- `<need input: does the mini track require the full K01–K06, or a reduced prework set? Docker
  (K06) + keys (K02) are needed by any track that self-hosts or persists; K04/K05 gate the agent
  arc which the mini also reaches.>`
- `<need input: confirm the shared-instructor-Langfuse path still exists alongside mandatory
  Docker — i.e. K06 stands up the DB + agent services locally, but tracing may point at the
  shared instance rather than a local Langfuse. Affects how heavy the local Compose stack is.>`
