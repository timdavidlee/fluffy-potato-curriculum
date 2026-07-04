# K06: Docker & the multi-container stack

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (Prework track row K06).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).
> Sibling doc: [demos_or_activities.md](demos_or_activities.md) — the self-paced walkthrough.
> Related infra doc: [docs/classroom-llm-management.md](../../../classroom-llm-management.md).

## Format note

Self-paced student walkthrough, not lecture+lab — same shape as K01 (see
[K01/objectives.md](../K01/objectives.md) for the full format rationale).

## Where this unit sits

K06 is the **last prework unit and the final gate before `L01`**. The course's local
infrastructure is genuinely **multi-service** — a tracing stack, a database, and the agent app —
so every student needs real, minimum Docker Compose literacy: **bring the stack up, keep it up,
read it when it breaks.** Not image authoring; not Dockerfile design. Just operating a stack
someone else defined.

**Docker is mandatory for every student**, not an opt-in fallback. Everyone installs Docker
Desktop here and brings the Compose stack up as part of setup, so later lessons can assume a local
database + agent service exist. This is a **hard environment gate**: K06's "does the stack come
up?" check is the go/no-go for starting `L01`.

The single outcome: **the student installs Docker, runs `docker compose up -d`, confirms every
service is healthy with `docker compose ps`, reads a service's logs when something is wrong, and
knows the one destructive command (`down -v`) to never run by reflex.**

## Prerequisites

- K01–K05 complete: working env, keys wired through the config seam (K02 — the stack's services
  read config the same way), and the async/types mental models.
- Hardware able to run Docker Desktop. The **lean default** (Postgres + Adminer) is light — a
  spare GB of RAM is plenty. The optional local-Langfuse overlay is heavier (Langfuse pulls in
  ClickHouse + more), so budget a few GB if you run it.

## What the stack contains (grounds every objective)

Taught against the repo's real [`compose.yaml`](../../../../compose.yaml) (authored in the same
effort). **Decided (K-prework open question #2): the default stack is LEAN, with a documented
overlay for local Langfuse.** So K06 brings up exactly two services by default:

- **`db`** — a local **PostgreSQL** (`postgres:16-alpine`): the "data plane" datastore where later
  lessons (L12+) persist an agent's *extracts / new records* — **not** trace spans. Has a named
  volume (`pgdata`) so its data survives restarts, and a healthcheck `docker compose ps` reads.
- **`adminer`** — a small web UI (`adminer:5`) for browsing that database. It's in the lean
  default mainly so the stack is genuinely **multi-service**: adminer reaches `db` **by service
  name** over the shared network, which is the networking concept K06 exists to teach.

Two things are deliberately **not** in the lean default, and students learn *why*:

- **Tracing (Langfuse) is out of the default.** A student points tracing at the **shared
  instructor Langfuse** instance (zero local weight — the recommended path), or brings up a
  **local Langfuse** with the documented **overlay** (see the walkthrough's "Appendix: self-host
  Langfuse locally"). Langfuse's own stack (web + worker + postgres + clickhouse + redis + minio)
  is heavy; keeping it optional is the whole point of "lean." Infra background:
  [classroom-llm-management.md](../../../classroom-llm-management.md).
- **The agent service is forward-looking.** There is **no agent app in the repo yet** — so the
  lean stack doesn't fabricate one. When the course grows an agent service, it attaches to *this*
  same compose network and reaches the DB at `db:5432`. K06 teaches the operating skills on `db` +
  `adminer`; the agent container slots in later without changing any of those skills.

## Learning objectives

By the end of K06, a student should be able to:

1. **Install Docker Desktop and confirm the engine is running.** Concretely: install Docker
   Desktop, start it, and run `docker version` / `docker compose version` successfully. The
   concept: **the Docker *engine* (the daemon) must be running** for any `docker` command to work
   — "is Docker Desktop actually open?" is the first troubleshooting question, always.

2. **Explain the three core objects: image vs. container vs. volume.** Concretely, at a
   semi-technical altitude:
   - an **image** is a read-only template (a packaged filesystem + config);
   - a **container** is a running instance of an image (start/stop/throw away freely);
   - a **volume** is persistent storage that **outlives** containers — this is where the
     databases' data lives so it survives a restart.

3. **Read a `compose.yaml` well enough to operate it.** Concretely: recognize that a
   `compose.yaml` defines several **services** (containers) that share one network and address
   each other **by service name**; that **ports** map container→host (`host:container`); that
   **env vars** pass through (the same `.env` from K02); and that **named volumes** hold the
   persistent DB/ClickHouse data. They read the file to operate it — they do not write it.

4. **Bring the stack up, inspect it, and take it down.** Concretely, the core operating loop:
   - `docker compose up -d` — start all services in the background;
   - `docker compose ps` — list services and their **health**;
   - `docker compose logs -f <service>` — follow one service's logs;
   - `docker compose down` — stop and remove the containers (**volumes survive**).

5. **Recognize and avoid the destructive command.** Concretely: `docker compose down -v` also
   **deletes the named volumes** — i.e. wipes your Langfuse/DB data. State it out loud as the
   footgun: `down` is safe and routine; **`down -v` is data loss** and should never be a reflex.

6. **Do basic troubleshooting from logs and state.** Concretely, handle the four most common
   failures without help:
   - Docker Desktop not running → start it;
   - **port already in use** → another process holds the host port; stop it or remap;
   - a container **stuck restarting** → read its logs (`logs -f <service>`) for the real error;
   - **startup ordering** → Langfuse waits on Postgres + ClickHouse (`depends_on` / healthchecks);
     a first-boot "not ready yet" often resolves once dependencies pass their healthcheck;
   - the DB won't come up / disk pressure → volume or disk-space reset (carefully — see objective
     5 before reaching for `-v`).

7. **Pass the go/no-go gate for `L01`.** Concretely: `docker compose ps` shows **all services
   healthy** AND a **smoke call through the config seam** succeeds (the K02 smoke call, now with
   the stack up). This is the concrete signal that the student is ready to begin the course.

## Concepts to highlight inline (the callouts)

- **The engine must be running.** Every `docker` failure starts with "is Docker Desktop open?"
- **Services address each other by name.** Inside the compose network, the agent reaches the DB at
  `postgres:5432` (service name), not `localhost`.
- **Volumes are the data; containers are disposable.** Restarting/removing containers is safe;
  removing *volumes* is not.
- **`down` vs `down -v`.** The single most important distinction in the unit. One is routine; one
  is data loss.
- **Logs first.** A container that won't stay up is telling you why in its logs — read them before
  changing anything.
- **The stack reads the same `.env`.** Config continuity from K02: no new secret-management model,
  just more services reading the same seam.

## Verify / pass checkpoint (the L01 gate)

K06 — and the entire prework track — is "done" when:

```sh
docker compose up -d
docker compose ps          # every service: healthy / running
# then, with the stack up, the K02 smoke call through the config seam succeeds
```

All services healthy **and** a passing smoke call = **cleared to start `L01`.** If a service is
unhealthy, objective 6's troubleshooting (logs, ports, dependency ordering) is the recovery path.

## Bridge to L01 (end of prework)

K06 closes the prework track. A student who reaches the green `docker compose ps` + smoke call has:
a pinned env (K01), wired keys (K02), the Jupyter workflow (K03), the ability to read
typed/pydantic (K04) and async (K05) code, and a running local stack (K06). They start `L01` from
the same baseline as the whole cohort — which is the entire reason the prework track exists.

## Resolved decisions

- **Langfuse hosting — RESOLVED:** lean default (no Langfuse in `compose.yaml`) + a documented
  local-Langfuse overlay; recommended path is the shared instructor instance. See "What the stack
  contains."
- **Concrete stack — RESOLVED:** two real services in `compose.yaml` — `db` (`postgres:16-alpine`,
  port 5432, named volume `pgdata`, `pg_isready` healthcheck) and `adminer` (`adminer:5`, port
  8080). No custom Dockerfile — both are prebuilt images, so a first `docker compose up -d` needs
  no build step.

## Open authoring questions

- `<need input: the "agent service" is forward-looking — no agent app exists in the repo yet, so
  the lean stack ships db + adminer only. Confirm this is acceptable for K06, i.e. the gate is
  "db/adminer healthy + config-seam smoke call" and the real agent container lands with a later
  lesson. If an agent service must exist NOW, we need to decide what it runs (there is no agent app
  to containerize today).>`
- `<need input: should the K06 gate additionally prove DB reachability (e.g. a tiny write/read
  against the db service), or is "services healthy + config-seam smoke call" sufficient? A DB
  round-trip needs a Postgres client dependency the repo doesn't have yet (would go through
  `uv add`).>`
