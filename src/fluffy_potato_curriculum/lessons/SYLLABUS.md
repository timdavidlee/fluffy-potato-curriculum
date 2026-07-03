# Syllabus — mini vs full tracks

Which lessons belong to the **mini** course vs the **full** course. The lesson
directories in this folder stay flat (`L01/` … `L25/`); track membership is
data, defined in [tracks.toml](tracks.toml) — a lesson belongs to a track by
membership there, not by where it lives on disk.

- **Full** — the master 25-lesson plan.
- **Mini** — the condensed ~30 hr cut (13 lessons): the five-objective core
  (tool design, when-to-use-a-tool, shallow LangGraph agent, eval, tracing)
  plus the early graph ramp (L03–L05, foundational for everything after) and
  Skills (L22) and skill patterns & composition (L23) by explicit request.
  Every mini lesson is also a full lesson.

See [docs/origin/CURRICULUM_PRD.md](../../../docs/origin/CURRICULUM_PRD.md) for
the full rationale (master table + "Condensed Mini Lesson Plan"). Keep that PRD
and `tracks.toml` in sync when lessons change.

| #   | Lesson title                                                  | Mini | Full |
| --- | ------------------------------------------------------------- | :--: | :--: |
| L01 | LLM and token basics                                          |  ✅  |  ✅  |
| L02 | Prompting fundamentals                                        |  ✅  |  ✅  |
| L03 | Single-node operations                                        |  ✅  |  ✅  |
| L04 | Directed graphs: sequential chaining                          |  ✅  |  ✅  |
| L05 | Conditional graphs: routing & branching                       |  ✅  |  ✅  |
| L06 | Teaching an LLM to think via prompting                        |      |  ✅  |
| L07 | Tool calling: how it works                                    |  ✅  |  ✅  |
| L08 | Designing good tools                                          |  ✅  |  ✅  |
| L09 | MCP: packaging tools as a portable contract                   |      |  ✅  |
| L10 | Hand-rolled agent loop                                        |  ✅  |  ✅  |
| L11 | Tracing: reading what your agent did                          |  ✅  |  ✅  |
| L12 | Evaluation: first pass                                        |  ✅  |  ✅  |
| L13 | Choosing model power for the task                             |      |  ✅  |
| L14 | Shallow agents in LangGraph                                   |  ✅  |  ✅  |
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

Mini teaching order: L01 → L02 → L03 → L04 → L05 → L07 → L08 → L10 → L11 → L12 → L14 → L22 → L23.

## Course wrap-ups

Each track closes with a wrap-up doc (what was covered · takeaways · where to go next) — these,
not any lesson, own the "end of the course" framing:

- [MINI_WRAPUP.md](MINI_WRAPUP.md) — closes the mini cut (read after L23).
- [FULL_WRAPUP.md](FULL_WRAPUP.md) — closes the full course (read after L25).
