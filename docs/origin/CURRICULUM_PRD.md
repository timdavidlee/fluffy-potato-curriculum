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

**Ordering note — orchestration before tools.** After prompting fundamentals (L02),
the course teaches the graph/orchestration model early as a three-lesson ramp —
**L03 single-node → L04 sequential graphs → L05 conditional graphs** — using plain
LLM calls only (no tools yet). Only then does it return to **L06 chain-of-thought**
and **L07 tool calling**. The through-line: *you wire the graph (L03–L05); the model
drives the loop (from L10, the agent loop)* — deterministic developer-controlled
branching is taught first, model-driven control comes later. Two consequences worth
tracking: (a) the L03–L05 graph block currently carries the LangGraph framing inherited
from the former workflows lesson, so LangGraph now appears *before* the hand-rolled loop
(L10) — if you'd rather preserve "mechanics before the framework," teach L03–L05
hand-rolled in plain Python and reserve the LangGraph name for L14; (b) the
workflow-vs-agent contrast opens at L04 and closes at L14 (shallow agents), ~10 lessons
apart. `<need input: keep L03–L05 in LangGraph, or teach them hand-rolled and introduce
LangGraph at L14?>`

| #   | Lesson title                                          | Subgoals                                                                                                  |
| --- | ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| L01 | LLM and token basics                                  | tokenize a string; reason about context windows; explain temperature and sampling; estimate cost          |
| L02 | Prompting fundamentals                                | use system/user/assistant roles; request structured output; use few-shot examples deliberately            |
| L03 | Single-node operations                                | wrap a single LLM call as a reusable node with explicit typed input/output state; treat a node as a pure function over shared state (state in → state out); run and inspect one node in isolation; understand *why* an explicit step is the unit you orchestrate <!-- new lesson — needs a roadmap authored under lesson_roadmaps/L03/ --> |
| L04 | Directed graphs: sequential chaining                  | model a multi-step task as a directed acyclic graph of explicit nodes; wire fixed edges and shared state; build a deterministic prompt-chaining workflow where the developer controls the path (no model-driven looping); contrast a workflow (you wire the flow) with an agent (the model drives the flow, introduced at L14) <!-- seeded from the former L11 workflows lesson (deterministic-DAG half) --> |
| L05 | Conditional graphs: routing & branching               | add conditional edges that branch on a model classification *or on direct user input*; build a router/switch with fixed, developer-controlled branches; reason about deterministic branching now vs. model-driven control later (the agent loop, L10/L14) <!-- new lesson — split out from the former L11 workflows lesson (routing half); needs a roadmap authored under lesson_roadmaps/L05/ --> |
| L06 | Teaching an LLM to think via prompting                | write a chain-of-thought prompt; use a scratchpad / `<thinking>` block; apply self-critique; recognize when explicit reasoning helps vs. hurts |
| L07 | Tool calling: how it works                            | wire a single tool to a model call; trace one tool-call round-trip; describe the tool-call protocol       |
| L08 | Designing good tools                                  | decide when a tool is needed vs. model-alone; name and schema-design a tool; handle tool errors           |
| L09 | MCP: packaging tools as a portable contract           | describe the problem MCP solves (portable tool contract across clients); connect to an existing MCP server from a client; expose a simple tool as an MCP server; decide when MCP is worth the overhead vs. an inline tool |
| L10 | Hand-rolled agent loop                                | build a model→tool→model loop in plain Python; reason about termination; handle tool failures             |
| L11 | Tracing: reading what your agent did                  | read a trace of an agent run (model calls, tool calls, intermediate state); locate where a failure occurred from the trace alone; instrument a hand-rolled agent loop to emit useful traces; compare two traces of the same task to spot what changed |
| L12 | Evaluation: first pass                                | build a minimal eval set for a tool-calling / hand-rolled-loop agent; design eval cases that target failure modes already seen in traces from L11; compare two runs of the same task to flag regressions; reason about eval cost (sample size, model calls, human review); establish the practice that every later lesson will carry forward |
| L13 | Choosing model power for the task                     | describe the trade-off axes between model classes (capability, latency, cost, context length); match a task or agent step to an appropriate model class; design a mixed-model agent (small model for routing/classification, capable model for reasoning) — including binding different models to different nodes of the graphs from L03–L05; estimate cost and latency budgets for a multi-step agent |
| L14 | Shallow agents in LangGraph                           | model an agent as a graph; build a single-loop LangGraph agent; reason about graph state                  |
| L15 | LangGraph design patterns                             | name common patterns (ReAct, plan-and-execute, supervisor, hierarchical, state-machine routing) and their distinguishing features; match a use case to an appropriate pattern; describe trade-offs (latency, control, complexity) |
| L16 | Agent middleware and conditional tools                | explain agent middleware as hooks around the agent loop (before/after model, request/response modification) that change behavior without rewriting the graph; apply a middleware to inspect, log, or guard a step; implement conditional (dynamic) tool exposure — gate which tools the model sees based on state, role, or prior steps; reason about when middleware is the right seam vs. editing graph nodes directly <!-- *NEED INPUT*: placed after L15 patterns so students see ReAct/supervisor first; move to immediately after L14 if you'd rather teach middleware before patterns --> |
| L17 | Human-in-the-loop and approval gates                  | identify steps that warrant human approval (irreversible side effects, high-stakes decisions, low-confidence tool calls); implement an interrupt/resume pattern in LangGraph; design an approval UX (what to surface, what to ask, safe default); reason about the cost of blocking the agent on a human (latency, throughput, attention) |
| L18 | Deep agents vs. shallow agents                        | contrast a deep agent's loop with a shallow agent's; identify what a deep agent adds (planning, persistent memory, todo/file state, reflection); decide when a deep agent is justified vs. overkill |
| L19 | Static system prompt vs. context management           | diagnose when an agent needs active context management (window overflow, instruction loss, cost spiral); apply at least three techniques (summarization/compaction, retrieval, just-in-time loading, scratchpad files, sliding windows); compare static vs. managed approaches on cost, latency, and recall |
| L20 | Embeddings and vector similarity                      | explain embeddings as a vector representation of text; compute and reason about cosine similarity / nearest-neighbor lookup; intuit *why* semantically related text scores closer; run a similarity-only lab without a vector DB |
| L21 | RAG pipeline                                          | build a minimal RAG pipeline (chunk, embed, store, retrieve, augment) on top of L20's similarity primitives; introduce a vector store as the operational layer; contrast in-context memory (message history, scratchpad) with external memory (vector store, database); decide when retrieval is needed vs. fitting content directly in the context window |
| L22 | Skills: just-in-time capabilities for agents          | describe what a skill is and how it differs from a tool or prompt; author a markdown skill with instructions and supporting scripts; reason about just-in-time loading vs. always-on context; decide when a capability belongs as a skill vs. a tool vs. system-prompt content |
| L23 | Skill patterns & composition                          | classify a skill by archetype (API/integration recipe with a bundled script, review/rubric of rules or principles, operating-model runbook); author each archetype in the `SKILL.md` format; compose skills — sequential handoff and a shared lower-level skill invoked by multiple operating skills; reason about the skill dependency graph and just-in-time loading across it; recognize composition anti-patterns (over-chaining, a shared "skill" that's really a tool, description collisions) |
| L24 | Multi-agent / subagent architecture (stretch)         | design a supervisor + workers pattern; explain when subagents help vs. hurt                               |
| L25 | Evaluation revisited                                  | extend the L12 eval discipline to complex systems: evaluate a multi-step LangGraph agent (per-node vs. end-to-end metrics); evaluate retrieval quality for RAG (precision@k / recall@k); reason about LLM-as-judge — what it can and can't reliably score; evaluate a multi-agent system (subagent quality vs. orchestration quality); scale eval cost (sampling strategies, CI gating) |

## Condensed Mini Lesson Plan

The above table is a master list, this should always be a reduced version of the above
table.

If the course had to be compressed to ~20 hours, this is the cut. It is
anchored on the five course objectives (tool design, when-to-use-a-tool,
shallow LangGraph agent, eval, tracing) and drops everything that doesn't
directly serve them. The multi-agent stretch is the first thing out.

**Kept (13 lessons, ~30 hrs at the full-course per-lesson rate):**

Skills (L22) and skill patterns & composition (L23) are included by explicit request on top of the
five-objective core — the two kept lessons not anchored to a course objective; they push the cut
past the ~20 hr floor. Together they make "compose skills into a system" the mini-cut capstone.
The early graph ramp (L03 single-node → L04 sequential → L05 conditional) is kept whole: it now
precedes tools and the agent loop, so every later mini lesson builds on the node/graph model and
none of the three can be dropped without breaking what follows — this is why the mini grew from 11
to 13 lessons.

| #   | Lesson title                            | Why it stays                                                                 |
| --- | --------------------------------------- | ---------------------------------------------------------------------------- |
| L01 | LLM and token basics                    | Non-negotiable foundation — every later lesson assumes it                    |
| L02 | Prompting fundamentals                  | Non-negotiable foundation; CoT (L06) folds in here                           |
| L03 | Single-node operations                  | The orchestration unit — a node is one LLM call you wire; every graph builds on it |
| L04 | Directed graphs: sequential chaining    | Deterministic prompt-chaining before the model-driven loop                   |
| L05 | Conditional graphs: routing & branching | Developer-controlled branching before the agent drives control               |
| L07 | Tool calling: how it works              | Covers the *tool design* objective — mechanics half                          |
| L08 | Designing good tools                    | Covers the *when a tool is needed vs. model alone* objective                 |
| L10 | Hand-rolled agent loop                  | The spine — exposes mechanics before LangGraph hides them                    |
| L11 | Tracing                                 | Covers the *tracing* objective; sets up L12                                  |
| L12 | Evaluation: first pass                  | Covers the *evaluation* objective; pairs with tracing                        |
| L14 | Shallow agents in LangGraph             | Covers the *design a shallow agent in LangGraph* objective                   |
| L22 | Skills: just-in-time capabilities       | Added by request; depends on tools + prompting, which the mini course keeps  |
| L23 | Skill patterns & composition            | Added by request; the composition capstone — compose skills into a system    |

**Cross-cutting thread — assistant message channels (narration / thinking / answer).**
The three kinds of assistant output must stay covered in the mini even though L06
(their natural home) is cut. Assign homes explicitly:

- **Answer** messages — already owned by **L02** (parsing the structured
  `<answer>{…}</answer>` block; the structured-output subgoal). No gap.
- **Narration** messages — the agent's interim assistant text between tool calls.
  Already present in **L10** (called out as "interim narration") and made readable
  in **L11** (narrate the run from the trace). Keep; consider naming it explicitly
  as a channel rather than an aside.
- **Thinking** messages — **GAP in the mini.** The `<thinking>` channel is owned by
  **L06, which the mini cuts**, and L02/L07 both currently *defer* it to L06
  ("that's L06, don't re-teach"). With no L06, the mini needs a home for the minimal
  thinking-block treatment. **Fix:** promote L02's existing optional `<thinking>`
  preview demo into a small taught beat in the mini (L02 already teaches the
  structured-`<answer>` half, so the thinking half is a natural sibling), reinforced
  at L07 where "deciding to call a tool is a reasoning step." Resolve the latent
  inconsistency: the mini plan says "CoT folds into L02," but L02's roadmap says it
  does *not* teach the thinking half — in the mini cut, it must.

**Cut, in rough order of "first to add back if the budget grows":**

1. **L21 RAG pipeline** (+ L20 embeddings as its prerequisite) — most-asked-for practical capability; pulls in two lessons but is the highest-impact restoration
2. **L13 Choosing model power** — short, broadly useful, low cost to slot in
3. **L06 Teaching an LLM to think via prompting** — folds into L02 in the mini cut; restores cleanly if you have an extra ~2 hrs
4. **L17 Human-in-the-loop and approval gates** — production-relevant; not foundational for first exposure
5. **L09 MCP** — topical but advanced; defer until students have built and felt the pain MCP solves
6. **L15 LangGraph design patterns** — a survey lesson, not a skill lesson
7. **L16 Agent middleware and conditional tools** — advanced agent-control mechanism; defer until students have a working shallow agent and know the patterns
8. **L18 Deep vs. shallow** — framing only; collapses into L19 cleanly
9. **L19 Context management** — secondary in a short course; the mini course doesn't build long enough sessions to feel the problem
10. **L24 Multi-agent (stretch)** — already stretch in the full course
11. **L25 Evaluation revisited** — depends on multi-step / RAG / multi-agent systems the mini course doesn't build



## Future topics / TODO

Topics we want the curriculum to cover but haven't yet slotted into a lesson.
Each is a note to design a lesson (or extend an existing one) later — not a
committed lesson yet. When one graduates, add a row to the lesson plan above
(or the mini cut) and give it an `L<NN>/` roadmap.

- **Agent memory store — remembering across turns *and* across sessions.** How
  an agent persists and recalls information beyond a single run: user
  preferences, facts learned earlier, prior-session context. This is distinct
  from context management (below): context management is about *what fits in the
  window right now*; memory is about *what survives after the window is gone*.
  Cover the split between short-term / working memory (the message list students
  own from L02) and long-term memory (an external store the agent reads/writes).
  **Survey the popular technologies** and where each fits — e.g. LangGraph
  persistence (checkpointers for thread state + the `Store`/`BaseStore` API for
  cross-thread memory), dedicated memory layers (mem0, Letta/MemGPT, Zep), and
  vector-store-backed memory. Relationship to what exists: L21 (RAG) already
  contrasts in-context vs. external memory and gives the retrieval primitive a
  memory store is built on; this topic is the *cross-session, preference/fact
  memory* framing L21 doesn't own. Decide whether it becomes its own lesson or a
  section extending L19.

- **"Batteries-included" agent tooling + base-agent vs. deep-agent comparison.**
  The common built-in toolbelt production agents ship with, and a head-to-head
  of the two archetypes. Two distinct pieces, two homes:
  - **Agent *scaffolding* tools — planning / TODO lists, file management,
    reflection.** These are what a *deep* agent adds on top of a shallow one, so
    this belongs in **L18 (Deep agents vs. shallow agents)** as its concrete
    implementation. L18 already scopes it ("planning, persistent memory,
    todo/file state, reflection"); the TODO is to make the vehicle concrete —
    contrast **LangChain's base agent** (`create_agent` / prebuilt ReAct, the
    *shallow* agent students build in L14) against **LangGraph's `deepagents`**,
    whose batteries are exactly a planning tool (`write_todos`), a virtual
    filesystem (`ls`/`read_file`/`write_file`/`edit_file`), and sub-agents.
    Land *when* the deep scaffolding earns its complexity vs. when a shallow
    agent is enough.
  - **Concrete popular *domain* tools — e.g. DuckDB (SQL/data), web search,
    file I/O.** These are tools you *give* an agent, independent of shallow-vs-
    deep, so they belong in **L08 (Designing good tools)** as real-world tool
    examples / a short "common toolbelt" survey — keep them out of L18 so its
    contrast stays about *architecture*, not which tools are bolted on.
  - Verify the current `deepagents` / `create_agent` API surface when building
    this — both are fast-moving; the names above are from general knowledge, not
    checked against a pinned version.

- **Context management strategies.** A deeper, technology-oriented treatment of
  keeping a long-running agent's context lean. L19 (Static system prompt vs.
  context management) already scopes the *concepts* — window overflow,
  instruction loss, cost spiral, and the technique list (summarization/
  compaction, retrieval, just-in-time loading, scratchpad/file offload, sliding
  windows). The TODO here is to make sure that lesson (currently full-course
  only, no roadmap yet) actually gets built and to broaden it toward the
  concrete strategies and tooling students will meet: automatic compaction /
  summarization, sliding-window and truncation policies, prompt caching as a
  cost lever, and framework support (e.g. LangGraph/LangChain trimming and
  summarization helpers). Many lessons already forward-point to L19 for this
  (L01, L02, L07, L22, L23) — those pointers are dangling until L19 exists.

## Open questions

Anything not yet decided that downstream lesson/lab authoring will need an
answer to before it can proceed.

- <!-- *NEED INPUT*: open question 1, or remove this section if none -->
