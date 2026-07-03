<!-- SCAFFOLD — headings only. Fill in stage-2 (or by hand) once the full-course lessons are generated.
     This doc closes the FULL course; it owns the "end of the course" framing (no lesson roadmap does).
     Mini-cut closer is the sibling MINI_WRAPUP.md. Track membership: tracks.toml / SYLLABUS.md. -->

# Full course — wrap-up

> The closing recap for the **full course** (23 lessons). Read after the final lesson (L25).
> Track definition: [SYLLABUS.md](SYLLABUS.md) · [tracks.toml](tracks.toml). Rationale: [CURRICULUM_PRD.md](../../../docs/origin/CURRICULUM_PRD.md).

## 1. What this course was

*One paragraph: the full arc's promise — the complete agent lifecycle, from LLM token basics through tool/agent design, observability and eval, LangGraph workflows and agents, the advanced agent-control lessons (patterns, middleware, HITL, deep agents, context management), retrieval/RAG, skills and composition, and finally multi-agent architecture with eval revisited.*

## 2. What you built (the arc)

*The through-line across all 23 lessons, in teaching order. Group into phases so it reads as a story rather than a list. Suggested phases: Foundations (L01–L06) · Tools & MCP (L07–L09) · The agent spine + observability (L10–L12) · Model choice & LangGraph (L13–L14) · Agent-control patterns (L15–L19) · Retrieval (L20–L21) · Skills & composition (L22–L23) · Multi-agent & eval-at-scale (L24–L25).*

<!-- *NEED INPUT*: confirm the phase groupings above (they're a proposal, not from the PRD). Recommendation: keep ~8 phases so each is a coherent chunk; put the lesson numbers in each phase heading. -->

## 3. Key takeaways

*The ideas that outlast the syntax — the durable mental models from across the whole course. Superset of MINI_WRAPUP.md §3, plus the advanced-arc lessons: retrieval vs. in-context memory, when a deep agent is justified, context management as a discipline, LLM-as-judge's limits, and multi-agent trade-offs (subagents help vs. hurt).*

## 4. The mental model

*The unifying framing: where a capability can live (system prompt / tool / MCP / skill / subagent), the model→tool→model loop, and the observability+eval discipline wrapped around every layer. One diagram that scales from a single tool call to a multi-agent system.*

## 5. What you can now do

*Map to the course objectives (design a tool; decide tool-vs-model; build a shallow LangGraph agent; the multi-agent stretch; agent evaluation and tracing) plus the capabilities the full arc adds beyond the five (RAG, context management, HITL, skills & composition). Phrase each as "you can now …".*

## 6. Where to go from here

*Beyond-the-course directions: production concerns (cost/latency at scale, guardrails, deployment), deeper multi-agent orchestration, evaluation in CI, and the frameworks/ecosystem to explore next. This is the full course's outer edge — point outward, not back.*

<!-- *NEED INPUT*: decide the "next steps beyond the course" scope — keep it to a short curated list (production readiness, advanced eval, multi-agent depth, ecosystem) vs. a longer reading path. Recommendation: short + curated; this is a capstone send-off, not a syllabus. -->

## 7. Further resources

*Links carried from lessons' `external_or_additional_resources.md`, plus the frameworks/tools used across the course (LangGraph, Langfuse, vector stores, the Anthropic API/skills format). Curated, not exhaustive.*

## 8. Glossary quick-reference

*Optional: a compact recall list of the load-bearing terms across all 23 lessons, each pointing back to the lesson that defined it. Superset of MINI_WRAPUP.md §8 with the advanced-arc terms (embedding/cosine similarity, RAG chunk/retrieve/augment, middleware, interrupt/resume, deep vs. shallow agent, supervisor/worker, precision@k / recall@k).*
