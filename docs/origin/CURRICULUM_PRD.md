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
| L09 | Choosing model power for the task                     | describe the trade-off axes between model classes (capability, latency, cost, context length); match a task or agent step to an appropriate model class; design a mixed-model agent (small model for routing/classification, capable model for reasoning); estimate cost and latency budgets for a multi-step agent |
| L10 | Shallow agents in LangGraph                           | model an agent as a graph; build a single-loop LangGraph agent; reason about graph state                  |
| L11 | LangGraph design patterns                             | name common patterns (ReAct, plan-and-execute, supervisor, hierarchical, state-machine routing) and their distinguishing features; match a use case to an appropriate pattern; describe trade-offs (latency, control, complexity) |
| L12 | Human-in-the-loop and approval gates                  | identify steps that warrant human approval (irreversible side effects, high-stakes decisions, low-confidence tool calls); implement an interrupt/resume pattern in LangGraph; design an approval UX (what to surface, what to ask, safe default); reason about the cost of blocking the agent on a human (latency, throughput, attention) |
| L13 | Deep agents vs. shallow agents                        | contrast a deep agent's loop with a shallow agent's; identify what a deep agent adds (planning, persistent memory, todo/file state, reflection); decide when a deep agent is justified vs. overkill |
| L14 | Static system prompt vs. context management           | diagnose when an agent needs active context management (window overflow, instruction loss, cost spiral); apply at least three techniques (summarization/compaction, retrieval, just-in-time loading, scratchpad files, sliding windows); compare static vs. managed approaches on cost, latency, and recall |
| L15 | Memory and retrieval (RAG, embeddings, vector stores) | explain embeddings and vector similarity intuitively; build a minimal RAG pipeline (chunk, embed, store, retrieve, augment); contrast in-context memory (message history, scratchpad) with external memory (vector store, database); decide when retrieval is needed vs. fitting content directly in the context window |
| L16 | Skills: just-in-time capabilities for agents          | describe what a skill is and how it differs from a tool or prompt; author a markdown skill with instructions and supporting scripts; reason about just-in-time loading vs. always-on context; decide when a capability belongs as a skill vs. a tool vs. system-prompt content |
| L17 | Multi-agent / subagent architecture (stretch)         | design a supervisor + workers pattern; explain when subagents help vs. hurt                               |
| L18 | Evaluation                                            | build a minimal eval set for an agent's task; identify regressions across runs; design eval cases that target known failure modes; reason about eval cost (sample size, model calls, human review) |

## Open questions

Anything not yet decided that downstream lesson/lab authoring will need an
answer to before it can proceed.

- <need input: open question 1, or remove this section if none>
