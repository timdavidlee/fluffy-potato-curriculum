# Curriculum PRD

The primary design document for this curriculum. AI agents generating lessons
or labs should read this first to understand the course's intent, then drill
into the per-lesson `objectives.md` files under `./lessons/L<NN>/`.

## Course summary

The goal of this course is to teach the fundamentals of AI agents, starting with LLM token basics, all the way to subagent architecture so that students can experience the full lifecycle of agent and tool design.

## Target audience

The target audience will be semi-techical students that have basic python familiarity.

## Lecture Materials

The expectation is that students will not verbally be able to absorb all the taught
content, so the written lecture materials should be very thorough in explaining concepts
or back-referencing earlier materials with links and similar wording. When in doubt, include more detail, more clarifications, and more examples.

(Vocabulary: a **lesson** is the high-level unit — one `L<NN>/` directory and one row in the lesson plan below. A **lecture** is one taught artifact within a lesson; a lesson can have multiple lectures.)

## Prerequisites

Students should be familiar with basic programming of classes, functions, types, and APIs in python

## Course objectives

The capabilities a student will have built by the end of the course. Each
should be observable (something the student can *do*, not just *know about*)
and should map to one or more lessons below.

- design a tool for an agent
- understand when a tool is needed vs. relying on core model
- design own "shallow agent" in langgraph
- stretch: a multi-agent design in langgraph
- understand the basics of agent evaluation and tracing


## Lesson plan

Lessons are taught in numeric order (`L01` first). Each row links to that
lesson's `objectives.md` once it exists.

| #   | Lesson title                                          | Subgoals                                                                                                  |
| --- | ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| L01 | LLM and token basics                                  | tokenize a string; reason about context windows; explain temperature and sampling; estimate cost          |
| L02 | Prompting fundamentals                                | use system/user/assistant roles; request structured output; use few-shot examples deliberately            |
| L03 | Teaching an LLM to think via prompting                | write a chain-of-thought prompt; use a scratchpad / `<thinking>` block; apply self-critique; recognize when explicit reasoning helps vs. hurts |
| L04 | Tool calling: how it works                            | wire a single tool to a model call; trace one tool-call round-trip; describe the tool-call protocol       |
| L05 | Designing good tools                                  | decide when a tool is needed vs. model-alone; name and schema-design a tool; handle tool errors           |
| L06 | MCP: packaging tools as a portable contract           | describe the problem MCP solves (portable tool contract across clients); connect to an existing MCP server from a client; expose a simple tool as an MCP server; decide when MCP is worth the overhead vs. an inline tool |
| L07 | Hand-rolled agent loop                                | build a model→tool→model loop in plain Python; reason about termination; handle tool failures             |
| L08 | Tracing: reading what your agent did                  | read a trace of an agent run (model calls, tool calls, intermediate state); locate where a failure occurred from the trace alone; instrument a hand-rolled agent loop to emit useful traces; compare two traces of the same task to spot what changed |
| L09 | Evaluation: first pass                                | build a minimal eval set for a tool-calling / hand-rolled-loop agent; design eval cases that target failure modes already seen in traces from L08; compare two runs of the same task to flag regressions; reason about eval cost (sample size, model calls, human review); establish the practice that every later lesson will carry forward |
| L10 | Choosing model power for the task                     | describe the trade-off axes between model classes (capability, latency, cost, context length); match a task or agent step to an appropriate model class; design a mixed-model agent (small model for routing/classification, capable model for reasoning); estimate cost and latency budgets for a multi-step agent |
| L11 | Explicit graphs & workflows in LangGraph (deterministic DAGs) | model a multi-step task as a directed acyclic graph of explicit nodes (each node free to bind a different model — cheap for routing, capable for reasoning); wire fixed edges and shared state; build a deterministic prompt-chaining / routing workflow where the developer controls the path — branching on a model classification *or on direct user input* — with no model-driven looping; contrast a workflow (you wire the flow) with an agent (the model drives the flow) |
| L12 | Shallow agents in LangGraph                           | model an agent as a graph; build a single-loop LangGraph agent; reason about graph state                  |
| L13 | LangGraph design patterns                             | name common patterns (ReAct, plan-and-execute, supervisor, hierarchical, state-machine routing) and their distinguishing features; match a use case to an appropriate pattern; describe trade-offs (latency, control, complexity) |
| L14 | Agent middleware and conditional tools                | explain agent middleware as hooks around the agent loop (before/after model, request/response modification) that change behavior without rewriting the graph; apply a middleware to inspect, log, or guard a step; implement conditional (dynamic) tool exposure — gate which tools the model sees based on state, role, or prior steps; reason about when middleware is the right seam vs. editing graph nodes directly <!-- *NEED INPUT*: placed after L13 patterns so students see ReAct/supervisor first; move to immediately after L12 if you'd rather teach middleware before patterns --> |
| L15 | Human-in-the-loop and approval gates                  | identify steps that warrant human approval (irreversible side effects, high-stakes decisions, low-confidence tool calls); implement an interrupt/resume pattern in LangGraph; design an approval UX (what to surface, what to ask, safe default); reason about the cost of blocking the agent on a human (latency, throughput, attention) |
| L16 | Deep agents vs. shallow agents                        | contrast a deep agent's loop with a shallow agent's; identify what a deep agent adds (planning, persistent memory, todo/file state, reflection); decide when a deep agent is justified vs. overkill |
| L17 | Static system prompt vs. context management           | diagnose when an agent needs active context management (window overflow, instruction loss, cost spiral); apply at least three techniques (summarization/compaction, retrieval, just-in-time loading, scratchpad files, sliding windows); compare static vs. managed approaches on cost, latency, and recall |
| L18 | Embeddings and vector similarity                      | explain embeddings as a vector representation of text; compute and reason about cosine similarity / nearest-neighbor lookup; intuit *why* semantically related text scores closer; run a similarity-only lab without a vector DB |
| L19 | RAG pipeline                                          | build a minimal RAG pipeline (chunk, embed, store, retrieve, augment) on top of L18's similarity primitives; introduce a vector store as the operational layer; contrast in-context memory (message history, scratchpad) with external memory (vector store, database); decide when retrieval is needed vs. fitting content directly in the context window |
| L20 | Skills: just-in-time capabilities for agents          | describe what a skill is and how it differs from a tool or prompt; author a markdown skill with instructions and supporting scripts; reason about just-in-time loading vs. always-on context; decide when a capability belongs as a skill vs. a tool vs. system-prompt content |
| L21 | Multi-agent / subagent architecture (stretch)         | design a supervisor + workers pattern; explain when subagents help vs. hurt                               |
| L22 | Evaluation revisited                                  | extend the L09 eval discipline to complex systems: evaluate a multi-step LangGraph agent (per-node vs. end-to-end metrics); evaluate retrieval quality for RAG (precision@k / recall@k); reason about LLM-as-judge — what it can and can't reliably score; evaluate a multi-agent system (subagent quality vs. orchestration quality); scale eval cost (sampling strategies, CI gating) |

## Condensed Mini Lesson Plan

The above table is a master list, this should always be a reduced version of the above
table.

If the course had to be compressed to ~20 hours, this is the cut. It is
anchored on the five course objectives (tool design, when-to-use-a-tool,
shallow LangGraph agent, eval, tracing) and drops everything that doesn't
directly serve them. The multi-agent stretch is the first thing out.

**Kept (10 lessons, ~24 hrs at the full-course per-lesson rate):**

Skills (L20) is included by explicit request on top of the five-objective core — it is the one
kept lesson not anchored to a course objective; it pushes the cut slightly past the ~20 hr floor.

| #   | Lesson title                       | Why it stays                                                                 |
| --- | ---------------------------------- | ---------------------------------------------------------------------------- |
| L01 | LLM and token basics               | Non-negotiable foundation — every later lesson assumes it                    |
| L02 | Prompting fundamentals             | Non-negotiable foundation; CoT (L03) folds in here                           |
| L04 | Tool calling: how it works         | Covers the *tool design* objective — mechanics half                          |
| L05 | Designing good tools               | Covers the *when a tool is needed vs. model alone* objective                 |
| L07 | Hand-rolled agent loop             | The spine — exposes mechanics before LangGraph hides them                    |
| L08 | Tracing                            | Covers the *tracing* objective; sets up L09                                  |
| L09 | Evaluation: first pass             | Covers the *evaluation* objective; pairs with tracing                        |
| L11 | Explicit graphs & workflows (DAGs) | Workflows-before-agents: deterministic graph before the model-driven loop   |
| L12 | Shallow agents in LangGraph        | Covers the *design a shallow agent in LangGraph* objective                   |
| L20 | Skills: just-in-time capabilities  | Added by request; depends on tools + prompting, which the mini course keeps  |

**Cut, in rough order of "first to add back if the budget grows":**

1. **L19 RAG pipeline** (+ L18 embeddings as its prerequisite) — most-asked-for practical capability; pulls in two lessons but is the highest-impact restoration
2. **L10 Choosing model power** — short, broadly useful, low cost to slot in
3. **L03 Teaching an LLM to think via prompting** — folds into L02 in the mini cut; restores cleanly if you have an extra ~2 hrs
4. **L15 Human-in-the-loop and approval gates** — production-relevant; not foundational for first exposure
5. **L06 MCP** — topical but advanced; defer until students have built and felt the pain MCP solves
6. **L13 LangGraph design patterns** — a survey lesson, not a skill lesson
7. **L14 Agent middleware and conditional tools** — advanced agent-control mechanism; defer until students have a working shallow agent and know the patterns
8. **L16 Deep vs. shallow** — framing only; collapses into L17 cleanly
9. **L17 Context management** — secondary in a short course; the mini course doesn't build long enough sessions to feel the problem
10. **L21 Multi-agent (stretch)** — already stretch in the full course
11. **L22 Evaluation revisited** — depends on multi-step / RAG / multi-agent systems the mini course doesn't build



## Open questions

Anything not yet decided that downstream lesson/lab authoring will need an
answer to before it can proceed.

- <!-- *NEED INPUT*: open question 1, or remove this section if none -->
