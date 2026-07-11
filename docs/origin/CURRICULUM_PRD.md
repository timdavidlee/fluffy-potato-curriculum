# Curriculum PRD

The primary design document for this curriculum. AI agents generating lessons
or labs should read this first to understand the course's intent, then drill
into the per-lesson `objectives.md` files under `./lessons/L<NN>/`.

> **Keep in sync:** the repo [`README.md`](../../README.md) surfaces the lesson plan below
> (topics list) and links here. When you add, remove, retitle, or reorder a lesson, update the
> README's Documentation → Topics list too — alongside `tracks.toml` / `SYLLABUS.md`.

## Course summary

The goal of this course is to teach the fundamentals of AI agents, starting with LLM token basics, all the way to subagent architecture so that students can experience the full lifecycle of agent and tool design.

## Target audience

The target audience will be semi-techical students that have basic python familiarity.

### Voice & point of view

All student-facing materials (lectures, labs, prework guides) are written **to the student**, in
the second person ("you"). The student is the reader — not a proctor, not the author. Two rules
follow:

- **Address the learner, not the presenter.** Write what the *student* should understand or do, and
  keep presenter/author meta-instructions out of the material — no "Teach X so you can debug it,"
  "name them now," "Defend the choice against…," or "(do not teach here)." State the point; don't
  narrate the act of teaching it.
- **Match the register to the material type.** The point of view is always the student; the
  *register* differs by artifact:

| Material | Register | Reads like |
| --- | --- | --- |
| **Lecture** (`_lecture.md` / `.ipynb`) | **Coach** — warm, mentor tone, medium length | someone guiding you through the idea ("here's the one line to hold onto…"), not reciting at you |
| **Lab** (`_lab_*.ipynb`) | **Punchy** — terse, energetic, high-signal | short, direct task prompts with momentum ("Now break it on purpose.") |
| **Prework guide** (`K<NN><II>_guide.md`) | **Runbook** — procedural, "do this → here's why" | numbered steps a student follows alone, with concept callouts inline |

Register controls *how the material reads*, not *how much it teaches*. A lecture stays thorough
(see **Lecture Materials** below) while sounding like a coach; a lab stays complete while sounding
punchy. Depth is set by the content; register is set by the tone.

- **Keep table-related text as concise as possible — in both lectures and labs.** The `table:`
  lead-in description *and* the cells themselves should be short noun phrases or fragments, not full
  sentences. A table is a scannable reference, so trim it hard: if a cell wants a full sentence, the
  point usually belongs in the surrounding prose, not the table.

Per-format specifics and before/after exemplars belong in [LECTURES.md](LECTURES.md) (Coach) and
[LAB_DESIGN.md](LAB_DESIGN.md) (Punchy); this section is the course-wide rule they inherit.

## Lecture Materials

The expectation is that students will not verbally be able to absorb all the taught
content, so the written lecture materials should be very thorough in explaining concepts
or back-referencing earlier materials with links and similar wording. When in doubt, include more detail, more clarifications, and more examples.

(Vocabulary: a **lesson** is the high-level unit — one `L<NN>/` directory and one row in the lesson plan below. A **lecture** is one taught artifact within a lesson; a lesson can have multiple lectures.)

## Prerequisites

Students should be familiar with basic programming of classes, functions, types, and APIs in python

## Course objectives

Two lenses on the course. The **student takeaways** are the handful of things every
student walks away able to do — the spine the mini track and the L50 capstone hang on.
The **core themes** are the content domains the course moves through to get there; each
theme is touched by several lessons, and a lesson can serve more than one.

### Student takeaways

Each is observable (something the student can *do*). The first four map to lessons below; the fifth is the end-of-week hackathon project (the L50 capstone is its worked-example on-ramp).

1. **Design a tool for an agent** — name it, schema its inputs/outputs, and handle its errors *(L07–L08)*
2. **Build a directed LLM-powered pipeline** — a developer-wired workflow of typed nodes with fixed and conditional edges, where you control the path *(L03, L05)*
3. **Build a customized free-form agent that drives its own tools** — the model-driven ReAct loop, wired by hand then recognized inside `create_agent` *(L10–L11)*
4. **Understand how agents are measured and what they produce** — read the state, logs, traces, and extracts a run emits, and evaluate its quality *(L12–L13)*
5. **Ship a hackathon project** — build an end-to-end application combining an agent, a UI, and a provided database, in a single-day team hackathon *(the end-of-week project; the L50 capstone is its worked-example on-ramp)*

### Core themes

The content domains the course moves through on the way to those takeaways.

- **LLM foundations** — tokens, context windows, cost, and sampling; prompting with roles, structured output, and few-shot *(L01–L02)*
- **Orchestration** — directed and conditional graphs, the cyclic agent loop, shallow agents, design patterns, human-in-the-loop gates, and multi-agent systems *(L03, L05, L10, L11, L15, L17, L24)*
- **Tool ecosystem** — the tool-call protocol, designing good tools, and packaging them behind MCP *(L07–L09)*
- **Agent instruction & guidance** — directing an agent through complex work via the prompt (chain-of-thought, self-critique), skills (packaged roadmaps and runbooks), and injected hints (middleware, conditional tools) *(L06, L16, L22–L23)*
- **Agents and outside systems** — deep-agent memory and files, context management, embeddings, and RAG *(L18–L21)*
- **Budgets, performance & resources** — cost and latency budgets, choosing models and providers, and measuring quality through tracing and evaluation *(L01, L12–L14, L25)*


## Prework track (`K<NN>`) — required before `L01`

Before the course proper, every student completes a **gated prework track** prefixed
**`K`** (sorts ahead of `L`, so no `L<NN>` renumbering). It front-loads the environment
and mental-model setup the lessons assume so the whole cohort starts `L01` from one
baseline instead of debugging setup mid-lesson. Unlike the lessons, K units are
**self-paced, step-by-step setup guides** (concepts highlighted inline as you work), not
proctor-led lecture+lab. Prework gates **both** the mini and full tracks — it is a
prerequisite, not a subset. Roadmaps live under `./lesson_roadmaps/K<NN>/`; design and
rationale in [`docs/todos/2026-07-03-2211-k-prework-track.md`](../todos/2026-07-03-2211-k-prework-track.md).

| #   | Prework unit                         | Covers                                                                                          |
| --- | ------------------------------------ | ----------------------------------------------------------------------------------------------- |
| K01 | Environment & tooling                | git clone, `uv sync` / `uv run`, venv & the pinned `.venv`, the `src/` layout, optional `core.hooksPath` |
| K02 | Keys & the config seam               | `.env.example` → `.env`, `common/config.py` (`require_*_key()`, never scattered `os.environ`), live-call hygiene (real paid calls: keep small/cheap; never commit keys or live output) |
| K03 | Jupyter workflow                     | `uv run jupyter lab`, the **restart-and-run-all** mental model, top-level `await` in cells       |
| K04 | Python you'll read: types & pydantic | fast refresher (types, functions, imports), **reading type hints** (`X \| None` / `list[int]` / `-> None`, pyright-strict), and **what a pydantic model is** (`BaseSettings`, structured output, tool schemas) |
| K05 | Async concepts                       | `async`/`await`, the event loop, `asyncio.gather` for concurrency, top-level `await`; owns the canonical **"why async for agents"** explainer the course cross-references (see [`docs/todos/2026-07-03-2152-prefer-async-methods.md`](../todos/2026-07-03-2152-prefer-async-methods.md)) |
| K06 | Docker & the multi-container stack   | **mandatory for everyone** — image/container/volume, `compose.yaml` services + named volumes, `docker compose up -d / ps / logs -f / down` (and the `down -v` footgun), basic troubleshooting; stands up Langfuse + Postgres + ClickHouse plus the DB/agent services |

**Gate to start `L01`:** K06's "does the stack come up?" check — `docker compose ps` all
healthy + a smoke call through the config seam — is the go/no-go, alongside the K02 keys gate.

## Lesson plan

Lessons are taught in numeric order (`L01` first). Each row links to that
lesson's `objectives.md` once it exists.

**Ordering note — orchestration before tools.** After prompting fundamentals (L02),
the course teaches the graph/orchestration model early as a two-lesson ramp —
**L03 (single node → sequential chain) → L05 conditional graphs** — using plain
LLM calls only (no tools yet). Only then does it return to **L06 chain-of-thought**
and **L07 tool calling**. The through-line: *you wire the graph (L03, L05); the model
drives the loop (from L10, the agent loop)* — deterministic developer-controlled
branching is taught first, model-driven control comes later. Two consequences worth
tracking: (a) the graph model is **continuous from L03 onward** — L03 and L05 build
forward graphs in LangGraph (`StateGraph`, nodes, edges, conditional edges), and L10
reuses those exact primitives to build the **ReAct agent as a *cyclic* graph**, adding
the one thing the earlier graphs lacked: a **back-edge** from the tool node to the agent
node. So "mechanics before the framework" is satisfied *within* the graph model — L10
wires the agent node-by-node by hand, and L11 immediately reveals the prebuilt `create_agent`
as "that same graph, packaged"; (b) the workflow-vs-agent contrast opens at L03
(forward, developer-driven) and closes at L10–L11 (the loop, model-driven), with L10 as the
hinge where the graph first gains a cycle.

> **Merge note (2026-07-09).** The former **L03 "Single-node operations"** and **L04
> "Directed graphs: sequential chaining"** are now a **single lesson at L03** —
> *"Directed graphs: from one node to a sequential chain."* Single-node-in-isolation was
> too thin to stand alone (its payoff only arrives when a second node is wired), so the
> node is now built and *immediately* chained in one lesson. The **`L04` slot is a reserved
> gap** — the downstream lessons were **not** renumbered (consistent with the existing gaps
> at L14+ and L50). Read "L03" wherever older notes say "the sequential-chaining lesson (L04)."

| #   | Lesson title                                          | Subgoals                                                                                                  |
| --- | ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| L01 | LLM and token basics                                  | tokenize a string; reason about context windows; explain temperature and sampling; estimate cost <!-- also carries a mechanistic model-scale beat (a local GPT-2 124M→355M→774M ladder sharpening the next-token distribution) — taught as a foreshadow of L14 (choosing models & providers), not a separately assessed subgoal --> |
| L02 | Prompting fundamentals                                | use system/user/assistant roles; request structured output; use few-shot examples deliberately; recognize and prompt for the common single-step task shapes (extraction, classification, ranking, constrained generation, summarization) |
| L03 | Directed graphs: from one node to a sequential chain  | wrap a single LLM call as a reusable, typed node — a pure function over shared state (state in → state out); run and inspect one node in isolation; then wire several such nodes into a directed acyclic graph with fixed edges and shared state; build a deterministic prompt-chaining workflow where the developer controls the path (no model-driven looping); contrast a workflow (you wire the flow) with an agent (the model drives the flow, introduced at L11) <!-- merged 2026-07-09 from the former L03 (single-node) + L04 (sequential chaining); roadmap at lesson_roadmaps/L03/ --> |
| ~~L04~~ | *reserved gap — merged into L03*                  | The former "Directed graphs: sequential chaining" was merged into L03 on 2026-07-09; the slot is intentionally left empty rather than renumbering L05+ (matches the L14+/L50 gaps). |
| L05 | Conditional graphs: routing & branching               | add conditional edges that branch on a model classification *or on direct user input*; build a router/switch with fixed, developer-controlled branches; reason about deterministic branching now vs. model-driven control later (the agent loop, L10/L11) <!-- new lesson — split out from the former L11 workflows lesson (routing half); needs a roadmap authored under lesson_roadmaps/L05/ --> |
| L06 | Teaching an LLM to think via prompting                | write a chain-of-thought prompt; use a scratchpad / `<thinking>` block; apply self-critique; recognize when explicit reasoning helps vs. hurts |
| L07 | Tool calling: how it works                            | wire a single tool to a model call; trace one tool-call round-trip; describe the tool-call protocol       |
| L08 | Designing good tools                                  | decide when a tool is needed vs. model-alone; name and schema-design a tool; handle tool errors           |
| L09 | MCP: packaging tools as a portable contract           | describe the problem MCP solves (portable tool contract across clients); connect to an existing MCP server from a client; expose a simple tool as an MCP server; decide when MCP is worth the overhead vs. an inline tool |
| L10 | Cyclic graphs: the ReAct agent loop                   | build a ReAct agent as a cyclic `StateGraph` (agent node → conditional back-edge → prebuilt `ToolNode`), reusing the L03/L05 graph primitives plus the new back-edge; reason about termination (`recursion_limit`, natural `END`); handle tool failures (`ToolNode(handle_tool_errors=True)`) |
| L11 | Shallow agents in LangGraph                           | build a shallow agent with LangChain's `create_agent` — the one-line equivalent of the L10 agent graph; run it on the L10 tasks and confirm behavioral equivalence; recognize what `create_agent` wraps (the same agent-node/tool-node/back-edge graph students built by hand) without re-wiring it, deferring the deeper `StateGraph` internals to L15 |
| L12 | What an agent generates: state, logs, traces & extracts | inventory what an agent run produces and split it across two planes — *observability* (state, logs, traces: what the agent did, for you to debug/eval) vs *data* (extracts / new records: what the agent made, persisted to a DB or S3); read a trace of an agent run (model calls, tool calls, intermediate state); locate where a failure occurred from the trace alone; instrument an agent to emit useful traces; compare two traces of the same task to spot what changed; keep hard data out of the trace and the trace out of the datastore |
| L13 | Evaluation: first pass                                | build a minimal eval set for a tool-calling agent and run it as a Langfuse **dataset + experiment** (on the same self-hosted Langfuse used for tracing in L12); design eval cases that target failure modes already seen in traces from L12; compare two experiments of the same task in Langfuse to flag regressions; reason about eval cost (sample size, model calls) and the scorer cost/judgment spectrum, ending on Langfuse's **managed LLM-as-judge**; establish the practice that every later lesson will carry forward |
| L14 | Choosing models & providers for the task              | survey the major model providers and where each is differentially strong (vision/OCR, long-context, reasoning/planning, cheap high-throughput execution); match a task or agent step to an appropriate provider *and* power tier — not just a size class within one provider; design a mixed-model, mixed-provider agent (e.g. a vision model for OCR, a strong reasoner for planning, a small fast model for routing/execution), binding different models to different nodes of the graphs from L03/L05; weigh capability against latency, cost, and context length; estimate cost and latency budgets for a multi-step, multi-model agent |
| L15 | LangGraph design patterns                             | name common patterns (ReAct, plan-and-execute, supervisor, hierarchical, state-machine routing) and their distinguishing features; match a use case to an appropriate pattern; describe trade-offs (latency, control, complexity) |
| L16 | Agent middleware and conditional tools                | explain agent middleware as hooks around the agent loop (before/after model, request/response modification) that change behavior without rewriting the graph; apply a middleware to inspect, log, or guard a step; implement conditional (dynamic) tool exposure — gate which tools the model sees based on state, role, or prior steps; reason about when middleware is the right seam vs. editing graph nodes directly <!-- *NEED INPUT*: placed after L15 patterns so students see ReAct/supervisor first; move to immediately after L11 (shallow agents) if you'd rather teach middleware before patterns --> |
| L17 | Human-in-the-loop and approval gates                  | identify steps that warrant human approval (irreversible side effects, high-stakes decisions, low-confidence tool calls); implement an interrupt/resume pattern in LangGraph; design an approval UX (what to surface, what to ask, safe default); reason about the cost of blocking the agent on a human (latency, throughput, attention) |
| L18 | Deep agents vs. shallow agents                        | contrast a deep agent's loop with a shallow agent's; identify what a deep agent adds (planning, persistent memory, todo/file state, reflection); decide when a deep agent is justified vs. overkill |
| L19 | Static system prompt vs. context management           | diagnose when an agent needs active context management (window overflow, instruction loss, cost spiral); apply at least three techniques (summarization/compaction, retrieval, just-in-time loading, scratchpad files, sliding windows); compare static vs. managed approaches on cost, latency, and recall |
| L20 | Embeddings and vector similarity                      | explain embeddings as a vector representation of text; compute and reason about cosine similarity / nearest-neighbor lookup; intuit *why* semantically related text scores closer; run a similarity-only lab without a vector DB |
| L21 | RAG pipeline                                          | build a minimal RAG pipeline (chunk, embed, store, retrieve, augment) on top of L20's similarity primitives; introduce a vector store as the operational layer; contrast in-context memory (message history, scratchpad) with external memory (vector store, database); decide when retrieval is needed vs. fitting content directly in the context window |
| L22 | Skills: just-in-time capabilities for agents          | describe what a skill is and how it differs from a tool or prompt; author a markdown skill with instructions and supporting scripts; reason about just-in-time loading vs. always-on context; decide when a capability belongs as a skill vs. a tool vs. system-prompt content |
| L23 | Skill patterns & composition                          | classify a skill by archetype (API/integration recipe with a bundled script, review/rubric of rules or principles, operating-model runbook); author each archetype in the `SKILL.md` format; compose skills — sequential handoff and a shared lower-level skill invoked by multiple operating skills; reason about the skill dependency graph and just-in-time loading across it; recognize composition anti-patterns (over-chaining, a shared "skill" that's really a tool, description collisions) |
| L24 | Multi-agent / subagent architecture (stretch)         | design a supervisor + workers pattern; explain when subagents help vs. hurt                               |
| L25 | Evaluation revisited                                  | extend the L13 eval discipline — on the same self-hosted Langfuse — to complex systems: evaluate a multi-step LangGraph agent (per-node vs. end-to-end metrics); evaluate retrieval quality for RAG (precision@k / recall@k); reason about LLM-as-judge — what it can and can't reliably score; evaluate a multi-agent system (subagent quality vs. orchestration quality); scale eval cost (sampling strategies, CI gating) |

**Capstone — L50, tying it all together: mini project (mini track only, for now).** After the
lesson arc there is a single **project-walkthrough capstone**: a proctor-led, end-to-end build
of a small ("mini") tool-calling agent that consolidates the mini cut's core build skills at once —
design a tool, wire the agent loop, trace it, and eval it. It is deliberately numbered **L50**,
not L26, so the capstone sits at the very end with a **gap left open** (L26–L49) to slot future
lessons *before* it without renumbering — the same "park it out of the way" move the `K`-prefix
uses for prework. Its full row lives in the mini plan below.

Format note: like the `K` prework, L50 is **not** the standard proctor-led lecture+lab shape —
it is an end-to-end **walkthrough** of building one project. Its roadmap will live at
`./lesson_roadmaps/L50/` once authored (not yet written — planned only, like L14–L25).

<!-- *NEED INPUT*: L50 is currently registered as MINI-TRACK-ONLY per request, which breaks the
otherwise-invariant "every mini lesson is also a full lesson" (mini ⊆ full). Decide whether the
capstone should also join the `full` track (the natural home for a superset), or stay a
mini-exclusive capstone. If it joins `full`, add "L50" to `[full].order` in tracks.toml and a row
to the master table above. -->

## Condensed Mini Lesson Plan

The above table is a master list, this should always be a reduced version of the above
table.

If the course had to be compressed to ~20 hours, this is the cut. It is
anchored on the five student takeaways (tool design, directed pipeline,
free-form agent, tracing & eval, hackathon project) and drops everything that
doesn't directly serve them. The multi-agent stretch is the first thing out.

**Kept (13 lessons + the L50 project capstone, ~32 hrs at the full-course per-lesson rate):**

Skills (L22) and skill patterns & composition (L23) are included by explicit request on top of the
five-takeaway core — the two kept lessons not anchored to a takeaway; they push the cut
past the ~20 hr floor. They make "compose skills into a system" the mini cut's last *taught*
lesson; the mini course then **closes with the L50 mini-project walkthrough** — a hands-on,
end-to-end build that consolidates the mini cut's core build skills (see the master plan above for why it is
numbered L50 and its walkthrough format).
The early graph ramp (L03 *from one node to a sequential chain* → L05 conditional) is kept whole: it
now precedes tools and the agent loop, so every later mini lesson builds on the node/graph model and
neither lesson can be dropped without breaking what follows. (Before the 2026-07-09 merge this ramp
was three lessons — single-node, sequential, conditional; the first two are now one lesson at L03.)
Chain-of-thought prompting (L06)
is kept by explicit request: it gives the `<thinking>` channel a real home (see the assistant
message-channels thread below) and reinforces "deciding to call a tool is a reasoning step" right
before L07 — this is why the mini grew from 10 to 13 lessons.

| #   | Lesson title                            | Why it stays                                                                 |
| --- | --------------------------------------- | ---------------------------------------------------------------------------- |
| L01 | LLM and token basics                    | Non-negotiable foundation — every later lesson assumes it                    |
| L02 | Prompting fundamentals                  | Non-negotiable foundation                                                    |
| L03 | Directed graphs: from one node to a sequential chain | The orchestration unit — a node is one LLM call you wire — then wired into a deterministic prompt-chaining workflow; every graph builds on it |
| L05 | Conditional graphs: routing & branching | Developer-controlled branching before the agent drives control               |
| L06 | Teaching an LLM to think via prompting  | Kept by request; owns the `<thinking>` channel and frames tool-calling as reasoning before L07 |
| L07 | Tool calling: how it works              | Covers the *tool design* objective — mechanics half                          |
| L08 | Designing good tools                    | Covers the *when a tool is needed vs. model alone* objective                 |
| L10 | Cyclic graphs: the ReAct agent loop     | The spine — the agent as a graph with a back-edge; wire it by hand before L11's prebuilt hides it |
| L11 | Shallow agents in LangGraph             | Covers the *design a shallow agent in LangGraph* objective — LangChain's `create_agent`, the one-line form of the L10 agent graph |
| L12 | What an agent generates                 | Tracing at the center (sets up L13), framed by the artifact taxonomy: state · logs · traces (observability) vs extracts / new records → DB/S3 (data) |
| L13 | Evaluation: first pass                  | Covers the *evaluation* objective; pairs with tracing                        |
| L22 | Skills: just-in-time capabilities       | Added by request; depends on tools + prompting, which the mini course keeps  |
| L23 | Skill patterns & composition            | Added by request; the composition capstone — compose skills into a system    |
| L50 | Tying it all together: mini project     | Project capstone (mini track only, for now) — a proctor-led walkthrough building one small tool-calling agent end-to-end (tool → agent loop → trace → eval), consolidating the mini cut's core build skills; walkthrough format, not lecture+lab |

**Cross-cutting thread — assistant message channels (narration / thinking / answer).**
The three kinds of assistant output are all covered in the mini. Homes:

- **Answer** messages — owned by **L02** (parsing the structured
  `<answer>{…}</answer>` block; the structured-output subgoal). No gap.
- **Narration** messages — the agent's interim assistant text between tool calls.
  Already present in **L10** (called out as "interim narration") and made readable
  in **L12** (narrate the run from the trace). Keep; consider naming it explicitly
  as a channel rather than an aside.
- **Thinking** messages — owned by **L06**, which the mini now keeps: the
  `<thinking>` channel gets its full chain-of-thought treatment there, reinforced at
  L07 where "deciding to call a tool is a reasoning step." (L02 keeps its lighter
  `<thinking>` preview as a sibling to the structured-`<answer>` half, but no longer
  has to carry the channel alone.)

**Cut, in rough order of "first to add back if the budget grows":**

1. **L21 RAG pipeline** (+ L20 embeddings as its prerequisite) — most-asked-for practical capability; pulls in two lessons but is the highest-impact restoration
2. **L14 Choosing models & providers** — short, broadly useful; matches models/providers to capabilities
3. **L17 Human-in-the-loop and approval gates** — production-relevant; not foundational for first exposure
4. **L09 MCP** — topical but advanced; defer until students have built and felt the pain MCP solves
5. **L15 LangGraph design patterns** — a survey lesson, not a skill lesson
6. **L16 Agent middleware and conditional tools** — advanced agent-control mechanism; defer until students have a working shallow agent and know the patterns
7. **L18 Deep vs. shallow** — framing only; collapses into L19 cleanly
8. **L19 Context management** — secondary in a short course; the mini course doesn't build long enough sessions to feel the problem
9. **L24 Multi-agent (stretch)** — already stretch in the full course
10. **L25 Evaluation revisited** — depends on multi-step / RAG / multi-agent systems the mini course doesn't build



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
    *shallow* agent students build in L11) against **LangGraph's `deepagents`**,
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
