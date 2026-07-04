# Syllabus — mini vs full tracks

Which lessons belong to the **mini** course vs the **full** course. The lesson
directories in this folder stay flat (`L01/` … `L25/`); track membership is
data, defined in [tracks.toml](tracks.toml) — a lesson belongs to a track by
membership there, not by where it lives on disk.

- **Prework (`K01`–`K06`)** — required, gated setup completed **before `L01`** by
  every student, on **both** tracks. Not part of the mini/full lesson count — it's a
  prerequisite, not a subset. These are **self-paced, step-by-step setup guides** (not
  proctor-led lecture+lab): environment/tooling, keys & the config seam, the Jupyter
  workflow, reading typed/pydantic/async code, and a **mandatory** multi-container Docker
  stack. The gate to start `L01` is K06's "does the stack come up?" check. See the design
  todo [`docs/todos/2026-07-03-2211-k-prework-track.md`](../../../docs/todos/2026-07-03-2211-k-prework-track.md).
- **Full** — the master 25-lesson plan.
- **Mini** — the condensed ~32 hr cut (14 lessons): the five-objective core
  (tool design, when-to-use-a-tool, shallow LangGraph agent, eval, tracing)
  plus the early graph ramp (L03–L05, foundational for everything after),
  chain-of-thought prompting (L06), and Skills (L22) and skill patterns &
  composition (L23) by explicit request. Every mini lesson is also a full lesson.

See [docs/origin/CURRICULUM_PRD.md](../../../docs/origin/CURRICULUM_PRD.md) for
the full rationale (master table + "Condensed Mini Lesson Plan"). Keep that PRD
and `tracks.toml` in sync when lessons change.

## Prework — required before `L01` (both tracks)

Gated setup, completed before the course proper. Every student does all six regardless
of track (`mini`/`full`).

| #   | Prework unit                              | Gate |
| --- | ----------------------------------------- | ---- |
| K01 | Environment & tooling                     | soft |
| K02 | Keys & the config seam                    | **hard** (keys wired through the config seam) |
| K03 | Jupyter workflow                          | soft |
| K04 | Python you'll read: types & pydantic      | understanding gate for the agent arc |
| K05 | Async concepts                            | understanding gate for the agent arc |
| K06 | Docker & the multi-container stack        | **hard** (`docker compose ps` all-healthy + a smoke call through the config seam) |

Prework order: K01 → K02 → K03 → K04 → K05 → K06.

## Course lessons

| #   | Lesson title                                                  | Mini | Full |
| --- | ------------------------------------------------------------- | :--: | :--: |
| L01 | LLM and token basics                                          |  ✅  |  ✅  |
| L02 | Prompting fundamentals                                        |  ✅  |  ✅  |
| L03 | Single-node operations                                        |  ✅  |  ✅  |
| L04 | Directed graphs: sequential chaining                          |  ✅  |  ✅  |
| L05 | Conditional graphs: routing & branching                       |  ✅  |  ✅  |
| L06 | Teaching an LLM to think via prompting                        |  ✅  |  ✅  |
| L07 | Tool calling: how it works                                    |  ✅  |  ✅  |
| L08 | Designing good tools                                          |  ✅  |  ✅  |
| L09 | MCP: packaging tools as a portable contract                   |      |  ✅  |
| L10 | Cyclic graphs: the ReAct agent loop                           |  ✅  |  ✅  |
| L11 | Shallow agents in LangGraph                                   |  ✅  |  ✅  |
| L12 | What an agent generates: state, logs, traces & extracts       |  ✅  |  ✅  |
| L13 | Evaluation: first pass                                        |  ✅  |  ✅  |
| L14 | Choosing model power for the task                             |      |  ✅  |
| L15 | LangGraph design patterns                                     |      |  ✅  |
| L16 | Agent middleware and conditional tools                        |      |  ✅  |
| L17 | Human-in-the-loop and approval gates                          |      |  ✅  |
| L18 | Deep agents vs. shallow agents                                |      |  ✅  |
| L19 | Static system prompt vs. context management                   |      |  ✅  |
| L20 | Embeddings and vector similarity                              |      |  ✅  |
| L21 | RAG pipeline                                                  |      |  ✅  |
| L22 | Skills: just-in-time capabilities for agents                  |  ✅  |  ✅  |
| L23 | Skill patterns & composition                                  |  ✅  |  ✅  |
| L24 | Multi-agent / subagent architecture (stretch)                 |      |  ✅  |
| L25 | Evaluation revisited                                          |      |  ✅  |

Mini teaching order: L01 → L02 → L03 → L04 → L05 → L06 → L07 → L08 → L10 → L11 → L12 → L13 → L22 → L23.

## Course wrap-ups

Each track closes with a wrap-up doc (what was covered · takeaways · where to go next) — these,
not any lesson, own the "end of the course" framing:

- [MINI_WRAPUP.md](MINI_WRAPUP.md) — closes the mini cut (read after L23).
- [FULL_WRAPUP.md](FULL_WRAPUP.md) — closes the full course (read after L25).
