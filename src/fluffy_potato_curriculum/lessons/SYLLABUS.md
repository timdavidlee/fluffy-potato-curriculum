# Syllabus — mini vs full tracks

Which lessons belong to the **mini** course vs the **full** course. The lesson
directories in this folder stay flat (`L01/` … `L23/`); track membership is
data, defined in [tracks.toml](tracks.toml) — a lesson belongs to a track by
membership there, not by where it lives on disk.

- **Full** — the master 23-lesson plan.
- **Mini** — the condensed ~26 hr cut (11 lessons): the five-objective core
  (tool design, when-to-use-a-tool, shallow LangGraph agent, eval, tracing)
  plus Skills (L20) and skill patterns & composition (L21) by explicit request.
  Every mini lesson is also a full lesson.

See [docs/origin/CURRICULUM_PRD.md](../../../docs/origin/CURRICULUM_PRD.md) for
the full rationale (master table + "Condensed Mini Lesson Plan"). Keep that PRD
and `tracks.toml` in sync when lessons change.

| #   | Lesson title                                                  | Mini | Full |
| --- | ------------------------------------------------------------- | :--: | :--: |
| L01 | LLM and token basics                                          |  ✅  |  ✅  |
| L02 | Prompting fundamentals                                        |  ✅  |  ✅  |
| L03 | Teaching an LLM to think via prompting                        |      |  ✅  |
| L04 | Tool calling: how it works                                    |  ✅  |  ✅  |
| L05 | Designing good tools                                          |  ✅  |  ✅  |
| L06 | MCP: packaging tools as a portable contract                   |      |  ✅  |
| L07 | Hand-rolled agent loop                                        |  ✅  |  ✅  |
| L08 | Tracing: reading what your agent did                          |  ✅  |  ✅  |
| L09 | Evaluation: first pass                                        |  ✅  |  ✅  |
| L10 | Choosing model power for the task                             |      |  ✅  |
| L11 | Explicit graphs & workflows in LangGraph (deterministic DAGs) |  ✅  |  ✅  |
| L12 | Shallow agents in LangGraph                                   |  ✅  |  ✅  |
| L13 | LangGraph design patterns                                     |      |  ✅  |
| L14 | Agent middleware and conditional tools                        |      |  ✅  |
| L15 | Human-in-the-loop and approval gates                          |      |  ✅  |
| L16 | Deep agents vs. shallow agents                                |      |  ✅  |
| L17 | Static system prompt vs. context management                   |      |  ✅  |
| L18 | Embeddings and vector similarity                              |      |  ✅  |
| L19 | RAG pipeline                                                  |      |  ✅  |
| L20 | Skills: just-in-time capabilities for agents                  |  ✅  |  ✅  |
| L21 | Skill patterns & composition                                  |  ✅  |  ✅  |
| L22 | Multi-agent / subagent architecture (stretch)                 |      |  ✅  |
| L23 | Evaluation revisited                                          |      |  ✅  |

Mini teaching order: L01 → L02 → L04 → L05 → L07 → L08 → L09 → L11 → L12 → L20 → L21.
