# K06 — Docker & the multi-container stack

```yaml
title: K06 — Docker & the multi-container stack
keywords: docker, docker desktop, docker compose, containers, multi-container stack, healthcheck, compose up, compose down, go/no-go gate, Langfuse, prework
estimated duration: 35
```

This is the **last prework unit** — the finish line (Step 6) is the go/no-go gate for starting `L01`.

## How to read this file

Work top to bottom; budget ~30–40 minutes (the first `up` downloads several container images, which
is slow once and fast forever after). You are **operating** a stack the repo already defines in
`compose.yaml` — you won't write any Docker yourself. All commands run from the repo root.

> **The one command never to run casually:** `docker compose down -v`. The `-v` deletes your data
> volumes — your database contents (and trace history, if you run the Langfuse overlay). Step 5
> covers this; until then, use `docker compose down` (no `-v`).

## Step 1 — Install Docker Desktop and confirm the engine is running

**Do:** install Docker Desktop (macOS/Windows) or Docker Engine (Linux) from docker.com, **launch
it**, wait for its status to say "running," then:

```sh
docker version
docker compose version
```

**You should see:** version info for both — importantly a **Server** section in `docker version`
(that's the engine/daemon).

**What just happened / why it matters:** a `docker` command is just a client; it needs the
**engine (daemon)** running to do anything. If the engine is down you'll get "Cannot connect to the
Docker daemon." So the first question whenever Docker misbehaves is always: **is Docker Desktop
actually open and running?**

**If it breaks:** no **Server** section, or "cannot connect to the daemon" → Docker Desktop isn't
running. Open it, wait for the whale/status indicator to go green, retry.

## Step 2 — Read the stack you're about to run

**Do:** look at the compose file at the repo root (read it, don't edit it):

```sh
cat compose.yaml
```

**You should see:** a `services:` block with **two** services — **`db`** (a `postgres:16-alpine`
database, port `5432`) and **`adminer`** (a web DB browser, port `8080`) — plus a `volumes:` block
declaring the named volume `pgdata`. The file is heavily commented; read the comments, they explain
each concept in place.

**What just happened / why it matters:** a `compose.yaml` describes a **multi-service** app. Three
things to notice as you read it:

- each entry under `services:` is one **container**; they share a private network and reach each
  other **by service name** — notice `adminer` is told its DB host is `db` (the service name), not
  `localhost`. Inside the network, `db` resolves to the postgres container;
- `ports: "HOST:CONTAINER"` maps a container port onto your machine — `5432:5432` puts Postgres on
  your `localhost:5432`, `8080:8080` puts Adminer's UI on `localhost:8080`;
- `volumes:` are **named, persistent storage** — `pgdata` is where the database keeps its data so it
  **survives** stopping and restarting the containers. Restarting containers is safe; the volume is
  where the important state lives.

The `db` service also reads the **same `.env` from K02** (`POSTGRES_*`, with dev defaults) — no new
secrets model, just another service reading the one config seam.

> **Where's Langfuse (tracing)?** Not in the lean default, on purpose — it's heavy. You'll either
> point tracing at the shared instructor Langfuse instance, or bring up a local one with the
> optional overlay in the **Appendix** at the bottom of this file. K06 teaches the operating skills
> on `db` + `adminer`; those skills are identical whatever else you add later.

## Step 3 — Bring the stack up

**Do:**

```sh
docker compose up -d
```

**You should see:** Docker pull each image (slow the first time), then create and start every
service. `-d` ("detached") returns your prompt while they run in the background.

**What just happened / why it matters:** one command started the whole multi-container app. The
first run downloads images and can take several minutes — that's normal and one-time. Subsequent
`up`s are quick.

**If it breaks:** **"port is already allocated"** → some other program on your machine is using a
port the stack wants. The lean stack claims **`5432`** (Postgres) and **`8080`** (Adminer) on your
host — a pre-existing local Postgres on 5432 is the usual culprit. Stop that program, or ask the
proctor which port to free.

## Step 4 — Inspect: is everything healthy?

**Do:**

```sh
docker compose ps
```

**You should see:** both services listed — **`db`** reporting **healthy** (its `pg_isready`
healthcheck passes within a few seconds) and **`adminer`** running (it waited for `db` to be
healthy before starting).

**What just happened / why it matters:** `ps` is your dashboard — it shows what's up and each
service's **health**. If a service isn't healthy yet, give it a moment (see Step 5's ordering
note); if it's *stuck*, read its logs:

```sh
docker compose logs -f db          # follow one service's logs; Ctrl-C to stop following
```

**Logs are the first thing to read** when a container won't stay up — the real error is almost
always in there.

**Prove it's real:** open **http://localhost:8080** in a browser — that's the Adminer UI, served by
the `adminer` container through the `8080:8080` port map. Log in with system *PostgreSQL*, server
`db`, and the `POSTGRES_*` credentials (defaults `potato` / `potato` / `fluffy_potato`). You just
watched one container (adminer) talk to another (`db`) **by service name** — the whole point of a
multi-service stack.

## Step 5 — Know how to stop it (and the footgun)

**Do (routine, safe):**

```sh
docker compose down
```

**You should see:** the containers stop and get removed. Your **data volume `pgdata` remains** — run
`docker compose up -d` again and your database contents are still there.

**What just happened / why it matters — the most important distinction in this unit:**

- **`docker compose down`** — stops and removes containers. **Data survives** (it's in the
  volumes). Safe and routine; run it whenever you want to shut the stack down.
- **`docker compose down -v`** — *also deletes the named volumes.* That **wipes `pgdata` — your
  database contents** (and, if you run the Langfuse overlay, your trace history). There is almost
  never a reason to run this in the course; treat it as a data-loss command, not a "clean restart"
  reflex.

> Rule of thumb: reach for `down`. If you think you need `-v`, stop and ask first — you're about to
> delete data.

**If a container was stuck (troubleshooting recap):** the common causes, in order —
1. **Docker Desktop not running** (Step 1);
2. **port already in use** (Step 3);
3. **stuck restarting** → `docker compose logs -f db` (or `adminer`) and read the error;
4. **startup ordering** → `adminer` waits on `db`'s healthcheck (`depends_on: condition:
   service_healthy`); a first-boot "adminer isn't up yet" often just means `db` is still becoming
   healthy — wait a moment, re-check `ps`. (The Langfuse overlay has deeper ordering: its web
   service waits on Postgres + ClickHouse.)
5. **disk space / corrupt volume** → last resort, and the only time `-v` is on the table — do it
   deliberately, knowing it deletes data.

## Step 6 — The go/no-go gate for L01

**Do:** with the stack up (`docker compose up -d`), confirm both halves of the gate:

```sh
docker compose ps        # (a) every service healthy
```

then re-run the **K02 smoke call through the config seam** (now with the stack running):

```sh
uv run python -c "from fluffy_potato_curriculum.common.config import require_anthropic_key; require_anthropic_key(); print('key wired ✓')"
```

**You should see:** both services healthy **and** the smoke call succeed. The gate proves your
infra is up and your key reaches the config seam; a deeper DB round-trip is left to the lessons
that actually persist data.

**What just happened / why it matters:** **this is the finish line of the entire prework track.**
All services healthy + a passing smoke call means your local infrastructure is real and reachable,
and you start `L01` from the same baseline as everyone else in the cohort.

## Done — prework complete

You can now bring the course's local stack up, inspect it, read it when it breaks, and take it down
without destroying your data. Combined with K01–K05 (pinned env, wired keys, Jupyter, and the
ability to read typed/pydantic/async code), you are **cleared to begin `L01`.** There is no K07 —
this is the end of prework. Start `L01` from a green `docker compose ps` and a passing smoke call.

## Appendix: self-host Langfuse locally (optional overlay)

**You do not need this for the L01 gate.** The recommended tracing path is to point at the **shared
instructor Langfuse** instance (you get a URL + project keys, set in `.env` through the K02 config
seam — no extra containers). This appendix is only for a **solo / self-paced** learner who wants
Langfuse running entirely on their own machine.

Langfuse's self-host stack is **heavy** and **fast-moving** — its own `docker compose` bundles the
Langfuse web + worker, a Postgres, ClickHouse, Redis, and MinIO (S3). Rather than fork (and let
drift) that file into this repo, use Langfuse's **official** self-host Compose as the source of
truth:

**Do (optional):**

1. Follow the official Langfuse self-hosting guide (search "Langfuse self-host docker compose") and
   bring up its stack per their instructions:
   ```sh
   # in a separate directory, per the official guide:
   git clone https://github.com/langfuse/langfuse
   cd langfuse
   docker compose up -d          # Langfuse's OWN compose — separate from this repo's lean stack
   ```
2. Open the Langfuse UI (default `http://localhost:3000`), create a project, and copy its public +
   secret keys and host URL.
3. Put them in **this repo's** `.env` (read by `common/config.py`; `langfuse_configured()` flips to
   true):
   ```sh
   # .env
   LANGFUSE_PUBLIC_KEY=pk-lf-...
   LANGFUSE_SECRET_KEY=sk-lf-...
   LANGFUSE_HOST=http://localhost:3000
   ```

**Why this is an overlay, not the default:** it's several extra containers and a few GB — most
students should use the shared instance. The `db` + `adminer` skills you learned above transfer
directly: it's the same `up -d` / `ps` / `logs -f` / `down` (never `-v`) loop, just more services.
