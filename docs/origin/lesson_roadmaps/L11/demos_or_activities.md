# L11: Teacher-led demos — Shallow agents in LangGraph

> Sibling docs: [objectives.md](objectives.md) (what the lesson aims for), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md).
>
> **Audience for this file:** the teacher running L11. Every demo below is *teacher-driven, no student participation*. Student-driven exercises live in the L11 labs (separate file, stage 2).
>
> **Anchor model: Claude Sonnet 4.6 — a *single* model throughout.** Unlike [L04](../L04/objectives.md) (which mixed Haiku/Sonnet per node to show the mechanism), L11 holds the model fixed so **`create_agent` is the only new thing on screen** versus the L10 hand-rolled loop. Model-power trade-offs are L14's job (full course; dropped in the mini cut). The agent uses the **native LangChain `ChatAnthropic`** client (continuing the framework-client departure begun in L04, *not* the `potato_llm` seam).

## How to read this file

Each demo is a self-contained block with:

- **Goal** — the single insight the demo should land. Tied to a learning objective from [objectives.md](objectives.md).
- **Pre-flight** — what the teacher needs loaded before class.
- **Live script** — the order of operations during the demo. Treat it as a checklist, not a teleprompter.
- **What to highlight** — the moment(s) where the teacher should slow down and say the takeaway out loud.
- **If the demo misbehaves** — graceful fallback for when the model surprises you (it will).

The demos match the three objectives from [objectives.md](objectives.md). Demo 1 *draws* the shallow agent as a lightweight graph and maps each piece to its L10 equivalent (objective 1). Demo 2 *builds* the agent in one line with `create_agent` and runs it to behavioral equivalence with L10 (objective 2). Demo 3 names `create_agent`'s config surface and the boundary where you'd drop to an explicit graph — the L15 door (objective 3). The optional demo points forward to L15. They build on each other — Demos 2–3 reuse the same `create_agent` agent and the shared `common/tools.py` tools. Run them in order on first delivery.

> **The spine of L11: it's the same loop, in one line.** L11 introduces no new *control flow* — model → tool → model until termination is exactly the L10 loop. What changes is that **`create_agent` writes the loop for you**. Open with L10's Demo 4 framing students already saw — *"every framework you'll see is a fancier version of the loop you wrote"* — and L04's framing — *"you built the acyclic workflow; here's the **back-edge** that makes it an agent."* Reinforce the primitives from L04; do **not** re-derive the hand-rolled loop from scratch (that's L10, assumed solid here), and do **not** hand-assemble a `StateGraph` (that's L15).

## Pre-flight (once, at the top of the lesson)

The teacher should have, before the first demo starts:

- **`create_agent` + the native LangChain Claude client ready** — `from langchain.agents import create_agent` and `from langchain_anthropic import ChatAnthropic`. `langgraph` (`>=1.2.4`) and `langchain-anthropic` (`>=1.4.4`) are already project dependencies (added via `uv add`); no install during class. The key loads through `common/config.py` as before — only the *client* is the framework's. <!-- *NEED INPUT*: confirm the exact Sonnet 4.6 model id string passed to ChatAnthropic, read from common/config.py rather than hard-coded in cells. Mirrors the same open item in L04's demos. -->
- **The shared tools imported, not rebuilt:** `from fluffy_potato_curriculum.common.tools import calculator, lookup, flaky_fetch`. Rebuilding the *same* agent students already know (L10) as a one-liner is the whole point — new tools would dilute it. (LangChain wraps plain Python tools, so the same `common/tools.py` functions bind straight into `create_agent`.)
- **The L10 hand-rolled loop visible in scrollback** (or its `common/agent_loop.py` reference copy) as the side-by-side the whole lesson maps against — `agent_loop.run(...)` → `RunResult(final_text, iterations, termination)`.
- **The two canonical L10 tasks ready:** the **chaining task** (*"the population of the city whose name is the answer to `17**2 - 1`"* → `calculator` then `lookup`, natural termination) and the **`flaky_fetch` failure task** (walk the four URL behaviors, exercise tool-failure handling).
- **A lightweight graph diagram of what `create_agent` wraps** — an `agent` node, a `tools` node, a back-edge, and a conditional exit — as a slide or whiteboard sketch. This is a *picture*, not a build; `compiled_agent.get_graph().draw_mermaid_png()` on the `create_agent` result can generate it if the render path works. <!-- *NEED INPUT*: confirm the diagram render path works in the demo environment; a hand-drawn slide / Mermaid-text / ASCII fallback is fine. Mirrors L04's demos. -->
- **A completed `create_agent` snippet in a sibling file** to paste if live-coding falls behind.

> Why rebuild a *known* agent: L11 is about seeing `create_agent` as **the L10 loop, packaged** — not new capabilities. Reusing L10's tools and tasks means the only new thing on screen is the one-liner — so when the rebuild issues the same tool sequence and terminates naturally, the framework reads as *conveniences over a familiar skeleton*, exactly the lesson's pedagogical bet.

## Demo 1 — From loop to graph: draw what `create_agent` wraps (Objective 1)

**Goal:** before any code, *draw* the shallow-agent graph and map every piece back to its L10 equivalent. Land the headline — **it's the same model→tool→model loop, and `create_agent` is the one call that gives it to you** — and recall L04's framing that the line between a workflow and an agent is a single **back-edge**. Be explicit that this diagram is a *mental model*; building it by hand is L15, not today.

**Pre-flight:**

- A whiteboard / slide with the L10 loop pseudocode on the left, empty graph space on the right.
- L04's acyclic workflow diagram available for the callback.

**Live script:**

1. Recall L04 in one line: *"you wired an **acyclic** workflow — the developer owned the path. An agent adds one thing: a **back-edge** that hands the path to the model."* Put L04's DAG up, then draw the cycle.
2. Draw the shallow-agent graph piece by piece, naming each and its L10 twin:
   - an **`agent`** (model-call) node — the L10 "call the model" step;
   - a **`tools`** node — the L10 "run every tool call, append a matching `ToolMessage`" step;
   - a fixed **edge** `tools → agent` — the L10 "loop back after running tools";
   - a **conditional exit** out of `agent` → `tools` (the model's `AIMessage` has `tool_calls`) or → finish (natural termination) — the L10 `if the AIMessage has tool_calls: … else: return` branch.
3. Trace a run on the diagram with your finger: agent → (tool_calls?) → tools → agent → (no tool_calls) → done. Point at the **back-edge** and say: *that cycle is the agent.*
4. Say the punchline: *"`create_agent` builds exactly this — you won't wire it by hand. Wiring it by hand is L15, for when this one shape isn't enough."*

**What to highlight:**

- **Same loop, new picture.** If a student can't map each graph piece back to an L10 line, slow down and do the mapping explicitly — that mapping *is* objective 1.
- **The conditional exit is the L10 branch.** "Are there `tool_calls`?" used to be an `if` in your Python; `create_agent` makes it a routing decision inside the agent. The decision is identical; only who writes it changed.
- **"Shallow" is a deliberate scope, defined now:** one model, one tool set, one decision point that either calls a tool or finishes. *Not* a deep agent (planning / memory / reflection — L18). Shallow ≠ lesser; most production agents are shallow.

**If the demo misbehaves:**

- Pure diagram + discussion, so little can flake. If students fixate on "where's the loop variable?", point at the `tools → agent` edge: the framework's run-driver *is* the `while`, supplied for you (Demo 2 makes that concrete).

## Demo 2 — Build the shallow agent in one line with `create_agent` (Objective 2)

**Goal:** build the shallow agent in a single `create_agent` call and run it to **behavioral equivalence** with the L10 loop — the same tool sequence and natural termination, with none of the loop written by hand. Land what the framework gives you **for free** that L10 made you write.

**Pre-flight:**

- An empty cell/file for the live build, Demo 1's diagram beside it.
- The shared tools (`calculator`, `lookup`, `flaky_fetch`) imported.
- Both canonical tasks ready to run.

**Live script:**

1. Build the model: `model = ChatAnthropic(model=<Sonnet 4.6 id from config>)`.
2. Build the agent in **one line**: `agent = create_agent(model, [calculator, lookup, flaky_fetch], system_prompt=…)`. Say out loud what you did *not* write: no `while` loop, no `if ai.tool_calls` branch, no message-list bookkeeping, no step counter.
3. **Run for equivalence.** Invoke the agent on the **chaining task** (`agent.invoke({"messages": [{"role": "user", "content": …}]})`) → watch it issue `calculator` then `lookup` and terminate naturally — the *same sequence* L10 produced. Then invoke on the **`flaky_fetch` failure task** → confirm tool-failure handling still works.
4. **Read the result.** Print the returned `messages` list — the same user / assistant-with-`tool_calls` / `ToolMessage` / assistant sequence L10 built by hand — and pull the final answer off the last message.
5. **Render what it wrapped.** `agent.get_graph().draw_mermaid_png()` (or the Mermaid text) and put it next to Demo 1's hand-drawn diagram — they match. The one-liner *is* the graph you drew.
6. **Name the freebies against their L10 twins:** the run-driver loop (L10's `while`), the tool-call routing (L10's `if ai.tool_calls`), the message-history append (L10's manual `messages.append`), a **recursion/step limit** (L10's `max_steps` cap — show where it lives), and tool execution (L10's dispatch-and-catch).

**What to highlight:**

- **The framework gives you the boring parts for free** — run-driver, routing, message bookkeeping, step cap, tool execution. That convenience *is* the value proposition; name each freebie against the L10 hand-rolled twin so the trade is concrete, not magic.
- **One line, same behavior.** The proof is the run: same tools, same order, same natural stop as L10 — from a single constructor call. That equivalence is the demo's whole point.
- **The step cap didn't go away.** A runaway agent still hits `create_agent`'s recursion limit — the framework's `max_steps`. Hitting it is still a signal worth investigating (the L10 lesson), not noise.

**If the demo misbehaves:**

- If the rebuild's tool sequence differs from L10's on the day, that's ordinary run-to-run variance — re-run. (L11 proves equivalence informally; the *repeatable* proof, an eval set, is L13's job, one lesson on.)
- If `create_agent`'s import or signature has drifted with the pinned versions, paste the completed snippet from the sibling file and read it line by line — the teaching point is the shape of the call, not typing it live.

## Demo 3 — The config surface, and where the one-liner ends (Objective 3)

**Goal:** make explicit what you *do* configure on a shallow `create_agent` agent, and name the boundary where you'd leave the one-liner for an explicit graph — the door into L15. Land that **`create_agent` is the right tool until the control flow stops being a single loop.**

**Pre-flight:**

- Demo 2's `create_agent` agent still in scope.
- Demo 1's diagram, to point at the pieces you'd take control of below the one-liner.

**Live script:**

1. Walk the **config surface** on the same agent: the **model**, the **tools list**, and the **system prompt** — the three knobs a shallow agent actually uses. Change the system prompt once and re-run to show it's the same agent with a different instruction.
2. State what you *didn't* touch and don't need to: the message-history state and the loop are managed for you — no reducer, no `while`, no state schema. Contrast with L10, where all of that was yours.
3. **Name the ceiling.** Ask: *"what would make you outgrow this one line?"* — a second model for one step, a branch that isn't just tool-or-finish, a custom node, state beyond the message list. That is precisely when you drop to an explicit `StateGraph` and wire nodes/edges/reducers yourself.
4. Point at the door and stop: *"building that graph by hand — and the named patterns on top of it (ReAct, plan-and-execute, supervisor) — is L15. Today you have the one-liner and a picture of what it wraps."*

**What to highlight:**

- **Configure model + tools + prompt; that's the shallow-agent surface.** Everything else `create_agent` handles. Resist the urge to crack it open — cracking it open is L15.
- **The one-liner has a ceiling, and knowing where it is *is* the skill.** Reaching for a hand-built graph on a single loop is over-engineering (the L10-objective-4 mistake); refusing to leave the one-liner when the flow branches is the opposite mistake. L11 teaches the shallow side of that line; L15 teaches the other.

**If the demo misbehaves:**

- Mostly discussion + one prompt swap, so little can flake. If the prompt swap doesn't visibly change behavior on the canonical task, use a prompt that changes the *format* of the final answer — the point is "same agent, new instruction," not a dramatic behavior shift.

## Common pitfalls coda — naming L11's three gotchas

**Shape note:** a short **"common pitfalls" coda**, not a new live demo — L11's three demos already *address* each of these. Its job is to **name** them as portable gotchas, restate the cure in a line, and pin each back to the demo that raised it. Budget ~5 minutes as a recap slide. Follows the [L23 Demo 5](../L23/demos_or_activities.md#demo-5--the-three-composition-anti-patterns-objective-5) template, like the [L01 coda](../L01/demos_or_activities.md#common-pitfalls-coda--naming-l01s-four-gotchas).

> **Scope note (2026-07-04 reorder):** the cross-cutting gotcha tracker was written when *this* topic was numbered "L14" and assumed a **hand-assembled `StateGraph`** lesson, so it listed reducer/typing **state-mismanagement** gotchas. Those now belong to **[L15](../L15/objectives.md)** (which owns the hand-built graph); the current `create_agent`-first L11 keeps only the shallow-agent gotchas below.

**Goal:** turn the "same loop, in one line" mental model into three named shallow-agent gotchas — the ways `create_agent` lulls you into forgetting the L10 machinery is still underneath.

**Pre-flight:**

- Nothing new to load. One recap slide; Demo 1's loop↔graph mapping and Demo 2's freebies list still on screen to point back at.

**Live script (recap — point back, don't re-run):**

1. **Assuming the one-liner can't run away (no termination).** ❌ Trusting a framework agent not to loop forever because "it's prebuilt." Point back at Demo 2: `create_agent` still carries a **step cap** (its recursion limit / `max_steps`) — the L10 termination problem didn't vanish, it moved behind the constructor. **Cure:** know where the cap lives and treat hitting it as a signal, exactly as in [L10](../L10/objectives.md).
2. **Treating `create_agent` as magic you can't debug.** ❌ Not being able to map the one-liner back to agent → tools → back-edge, so a bad run is unexplainable. Point back at Demo 1: every piece has an L10 twin. **Cure:** debug the shallow agent *as the L10 loop it is* — read the returned `messages`, find the turn that went wrong; the framework hid the wiring, not the behavior.
3. **Wrong altitude: one-liner vs. hand-built graph.** ❌ Hand-assembling a `StateGraph` when `create_agent` already fits (over-engineering — the L10 objective-4 mistake), *or* clinging to the one-liner after the flow outgrows a single tool-or-finish loop (under-engineering). Point back at Demo 3's ceiling discussion. **Cure:** stay on `create_agent` until the control flow stops being one loop (a second model per step, a non-tool branch, custom state) — then drop to an explicit graph. That door is [L15](../L15/objectives.md).

**What to highlight:**

- All three are the same trap: **the convenience hides the machinery, but the machinery is still there.** L11's bet is that, having built the L10 loop by hand, students read `create_agent` as "that, packaged" — these gotchas are what happens when they forget it.
- #3 *is* the shallow-agent skill: knowing where the one-liner's ceiling is. Neither reflex — always hand-build, or never leave the one-liner — is right.

**If a student pushes back:**

- "So when do I ever hand-build the graph?" When you outgrow the single loop — that's L15, and Demo 3 named the exact triggers (second model, non-tool branch, custom state). Not before.

## Optional demo — toward L15 patterns

If time allows, point forward without teaching it: the shallow agent `create_agent` gave you *is* a named pattern (**ReAct**) — reason, act, repeat. L15 drops below the one-liner to build that graph explicitly and surveys the others (plan-and-execute, supervisor, hierarchical, state-machine routing) and *when* to reach for each. Ask the open question L15 answers — *"what do you build when a single tool-calling loop isn't the right shape?"* — and stop there.

Don't teach any pattern here — L11 owns *`create_agent` and the shallow-agent mental model*; L15 owns the explicit graph and the named patterns. Just land that the mental model students now have is the thing L15 builds *on top of*.

<!-- *NEED INPUT*: include this forward pointer in the lecture, or save it as L15's opener? Recommendation: a 60-second close — it frames the shallow agent as "the ReAct pattern, prebuilt" and motivates L15. -->

## Pacing notes for the teacher

- **Per-demo time:** Demo 1 is 10–15 minutes (diagram + L10 mapping, no build). Demo 2 is the core, 20–30 minutes (the `create_agent` call + two equivalence runs + reading the messages + the freebies list). Demo 3 is 10–15 (config surface + the L15 boundary). Optional close is 5. Total ~45–65 minutes plus discussion — fits the **~60–90 minute** lecture pinned in [objectives.md](objectives.md). This is shorter than the old node-by-node lesson because the hand-assembled `StateGraph` build moved to L15.
- **Live-coding budget:** only Demo 2's `create_agent` call needs live typing, and it's a few lines. Demo 1 is a diagram; Demo 3 is a prompt swap plus discussion. Do **not** hand-assemble a `StateGraph` in any demo — that's L15.
- **Single model, on purpose:** L11 holds the model at Sonnet 4.6 so the only variable vs. L10 is who writes the loop. Resist mixing models here — that was L04's mechanism demo; the *which-model* decision is L14's.
- **Variance budget:** the agent loop is non-deterministic — budget a re-run wherever a specific tool sequence matters. L11 confirms equivalence by eyeball; the *repeatable* check (an eval set) is L13, which comes after.
- **The audience watches, doesn't participate.** Resist "what tools should we pass here?" as a group question — that's a lab pattern. Hands-on `create_agent` building is for the L11 labs.

## Open authoring questions

Most of L11's big decisions are pinned in [objectives.md](objectives.md) (`create_agent`-first with the hand-assembled `StateGraph` deferred to L15; native `ChatAnthropic` not the seam; single anchor model Sonnet 4.6 with model-power deferred to L14; `langgraph` + `langchain-anthropic` deps already added; reuse `common/tools.py` and the two canonical L10 tasks; no eval/Langfuse carry-over, since L12/L13 now follow; persistence/checkpointing out of scope as a forward pointer to L17/L18/L19; the intentional L04↔L11 primitives overlap). The remaining open items are stage-2 mechanics:

- <!-- *NEED INPUT*: the exact Sonnet 4.6 model id string passed to ChatAnthropic, read from common/config.py. Mirrors L04's demos. -->
- <!-- *NEED INPUT*: confirm the graph-diagram render path (draw_mermaid_png vs Mermaid text vs ASCII) works in the demo environment for a create_agent result. Mirrors L04's demos. -->
- <!-- *NEED INPUT*: are the demos run in a projected Jupyter notebook, a slide-embedded REPL, or a demo-runner script? Mirrors the same open question in L10's and L04's demos. -->
- <!-- *NEED INPUT*: include the optional L15 forward-pointer in the lecture or hold it for L15's opener? Recommendation: a 60-second close. -->
