<!-- SCAFFOLD — headings only. Fill in stage-2 (or by hand) once the mini-track lessons are generated.
     This doc closes the MINI cut; it owns the "end of the mini course" framing (no lesson roadmap does).
     Full-course closer is the sibling FULL_WRAPUP.md. Track membership: tracks.toml / SYLLABUS.md. -->

# Mini course — wrap-up

> The closing recap for the **mini cut** (11 lessons). Read after the final mini lesson (L21).
> Track definition: [SYLLABUS.md](SYLLABUS.md) · [tracks.toml](tracks.toml). Rationale: [CURRICULUM_PRD.md](../../../docs/origin/CURRICULUM_PRD.md) ("Condensed Mini Lesson Plan").

## 1. What this course was

*One paragraph: the mini cut's promise — go from LLM token basics to a working, traced, evaluated shallow LangGraph agent, then compose capabilities into a skill system. Name the five anchor objectives + the two by-request skills lessons.*

## 2. What you built (the arc)

*The through-line as a sequence, in mini teaching order: L01 → L02 → L04 → L05 → L07 → L08 → L09 → L11 → L12 → L20 → L21. One line per lesson — what it added to the stack. End on the mental picture: tokens → prompts → tools → hand-rolled loop → tracing → eval → workflows → shallow agent → skills → skill systems.*

<!-- *NEED INPUT*: per-lesson recap granularity — one line each (11 bullets), or grouped into ~4 phases (foundations / tools / agent+observability / skills)? Recommendation: grouped phases with the lesson numbers in each, so the arc reads as a story, not a table. -->

## 3. Key takeaways

*The handful of ideas that outlast the syntax — the things a student should still believe in a year. Candidates: "a tool is called, a skill is read, the system prompt is always seen"; "trace before you guess"; "eval or it's vibes"; "you wire a workflow, the model drives an agent"; "just-in-time beats always-on"; "composition earns its keep only when the system beats the monolith."*

## 4. The mental model

*The single diagram/framing to carry forward: where a capability can live (system prompt vs. tool vs. skill vs. — full course — MCP/subagent), and the model→tool→model loop with tracing + eval wrapped around it.*

## 5. What you can now do

*Map to the observable course objectives (design a tool; decide tool-vs-model; build a shallow LangGraph agent; trace it; evaluate it; author and compose skills). Phrase each as "you can now …".*

## 6. Where to go from here — what the full course adds

*The mini cut deliberately dropped lessons. List them in the PRD's "first to add back" order, one line each on what they'd add, linking to the full syllabus.* See [FULL_WRAPUP.md](FULL_WRAPUP.md) for the complete arc.

<!-- *NEED INPUT*: pull the add-back list + order straight from CURRICULUM_PRD.md's "Cut, in rough order of first to add back" (L19+L18 RAG, L10 model power, L03 CoT, L15 HITL, L06 MCP, L13 patterns, L14 middleware, L16 deep/shallow, L17 context mgmt, L22 multi-agent, L23 eval revisited). Keep it a pointer to the PRD rather than duplicating the rationale, so it can't drift. -->

## 7. Further resources

*Links carried from lessons' `external_or_additional_resources.md`, plus the frameworks/tools used (LangGraph, Langfuse, the Anthropic API/skills format). Keep short and curated.*

## 8. Glossary quick-reference

*Optional: a compact recall list of the load-bearing terms (token/context window, tool schema, agent loop, span/trace, eval case/scorer, workflow vs. agent, skill/JIT/progressive disclosure, archetype, dependency graph). Point back to the lesson that defined each.*
