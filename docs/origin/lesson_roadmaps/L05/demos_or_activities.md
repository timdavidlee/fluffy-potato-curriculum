# L05: Teacher-led demos — Conditional graphs (routing & branching)

> Sibling docs: [objectives.md](objectives.md) (what the lesson aims for), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md).
>
> **Audience for this file:** the teacher running L05. Every demo below is *teacher-driven, no student participation*. Student-driven exercises live in the L05 labs (separate file, stage 2).
>
> **Anchor model: Claude Sonnet 4.6** for the specialized branch nodes, **Claude Haiku 4.5** for the entry classifier/router node — the same per-node mixing mechanism L04 already demonstrated; this file reuses it rather than re-explaining it. **Client: native LangChain `ChatAnthropic`**, same as L04 — the "frameworks bring their own client" departure was already made and called out there; no need to re-make the point here beyond a one-line recall.

## How to read this file

Each demo is a self-contained block with:

- **Goal** — the single insight the demo should land. Tied to a learning objective from [objectives.md](objectives.md).
- **Pre-flight** — what the teacher needs loaded before class.
- **Live script** — the order of operations during the demo. Treat it as a checklist, not a teleprompter.
- **What to highlight** — the moment(s) where the teacher should slow down and say the takeaway out loud.
- **If the demo misbehaves** — graceful fallback for when the model surprises you (it will).

The demos are ordered to match L05's four learning objectives. Demo 1 introduces the **conditional edge** itself, tracing one value from a node's write to a branch decision (objective 1). Demo 2 builds the full **router/switch** — classifier entry node fanning out to specialized branches, including the ambiguous/fallback case (objective 2). Demo 3 swaps the router's decider to **direct user input** and puts the two deciders side by side (objective 3). Demo 4 is the **closing argument** of the workflow-vs-agent arc, naming precisely what L11 will change (objective 4). An optional demo carries L04's eval-the-workflow habit onto the router. **They build on each other** — Demos 2–4 reuse Demo 1's graph skeleton and the same running-example domain, never a fresh one. Run them in order on first delivery.

> **This lesson expands, not repeats, three demos already sketched in [L04's demos file](../L04/demos_or_activities.md).** L04's Demo 2 (routing + mixed models), Demo 3 (user-input branching), and Demo 4 (workflow-vs-agent line) covered this ground at the depth a shared lesson could afford. L05 owns this material outright now — each demo below goes deeper (the fallback-branch case, the side-by-side decider comparison, the precise L11 delta) than L04's versions had room for. **L05's Demo 0 (sequential chaining) does not exist** — that content stays in L04; this file opens directly on the conditional edge and assumes students walk in already able to build a fixed-edge `StateGraph`.

> **The spine of L05: one new primitive, pressure-tested from every angle.** Everything except the conditional edge is L04, reused without re-teaching. Keep saying "the routing function decides — and the routing function is *your* code, reading state *you* control." The lesson's payoff is Demo 4: naming exactly what L11 changes, so nothing about the agent lesson comes as a surprise.

## Pre-flight (once, at the top of the lesson)

The teacher should have, before the first demo starts:

- **LangGraph + the native LangChain Claude client ready**, exactly as in L04: `from langgraph.graph import StateGraph, END` and `from langchain_anthropic import ChatAnthropic`. No re-introduction needed — one line of recall ("same client as last lesson") is enough.
- **Two model clients constructed and named:** `haiku = ChatAnthropic(model="claude-haiku-4-5-...")` for the classifier/router entry node, `sonnet = ChatAnthropic(model="claude-sonnet-4-6-...")` for the specialized branch nodes. <!-- *NEED INPUT*: confirm exact model id strings for the Haiku 4.5 and Sonnet 4.6 snapshots used by ChatAnthropic, read from common/config.py rather than hard-coded in cells — same open item as L04's demos file; resolve once, reuse in both. -->
- **A completed L04-style sequential graph on hand, uninstantiated** (not rebuilt live) — just enough to point at and say "this is where we left off: fixed edges only." Used for a 30-second recall at the top of Demo 1, not a rebuild.
- <!-- *NEED INPUT*: running-example domain — this file assumes continuation of L04's support-ticket domain (billing / technical / general categories, a short policy snippet), matching the recommendation flagged in objectives.md. If a different domain is chosen in stage 2, every demo below needs its sample inputs swapped, but the demo *structure* (classify → branch → converge; then swap decider; then close the arc) does not change. -->
- **A small support-ticket dataset**, reused/extended from L04's fixture: at minimum one clearly-billing, one clearly-technical, one clearly-general, and **one deliberately ambiguous** ticket that a Haiku classifier is likely to mis-label or split a coin flip on — the ambiguous one is load-bearing for Demo 2's fallback-branch teaching moment, don't skip it. <!-- *NEED INPUT*: confirm the exact sample tickets (recommend reusing L04's fixture and adding one more ambiguous ticket if L04's set doesn't already stress the classifier hard enough). Stage 2 ships these as a shared fixture between L04 and L05. -->
- **A `user_choice` version of the same tickets** — the same requests, but expressed as a structured menu selection a user would pick (e.g. a dropdown value `"billing" | "technical" | "general"`) rather than free text a model must classify. Used in Demo 3. <!-- *NEED INPUT*: confirm the exact user_choice shape (a plain string enum is the simplest; confirm no richer structure is wanted for the demo). -->
- **Run-inspection via `graph.stream(stream_mode="updates")`, not Langfuse.** L05, like L04, is before L12 (tracing) — don't depend on the shared Langfuse instance. **Decided:** use the same `.stream(..., stream_mode="updates")` call students have used since L03 — it yields one chunk per node that fires, so "which branch ran" is visible directly (only the chosen branch's node appears in the stream) without a dashboard. This keeps a single run-inspection tool threaded across L03 → L04 → L05 → L10.
- **A graph-diagram renderer ready**, same as L04 (`compiled_graph.get_graph().draw_mermaid_png()` or Mermaid text) — reused for Demo 1 and Demo 3's side-by-side, not re-explained.
- **Completed graph definitions in a sibling file** to paste if live-coding falls behind — the router graph (Demo 2) and the user-input-branching variant (Demo 3).
- **`common/evals.py` importable** for the optional eval-the-router beat.

> Why continuing the support-ticket domain (pending confirmation above): L05 is about the conditional edge, not about learning a new domain from scratch — reusing L04's tickets means the *only* new thing on screen is the branch, exactly matching the lesson's narrow scope. If stage 2 picks a different domain, keep this same "everything held constant except the branch" design principle when re-picking sample data.

## Demo 1 — The conditional edge: from state write to branch decision (Objective 1)

**Goal:** introduce the **conditional edge** as the one new primitive this lesson adds, and trace a single value all the way from *a node writing it* to *a routing function reading it* to *the branch that executes*. Land the vocabulary: routing function, decider, `add_conditional_edges`.

**Pre-flight:**

- The completed L04 sequential graph on screen (not live-built) — point at it, don't rebuild it.
- One support ticket chosen to run through, plus its expected category.

**Live script:**

1. **30-second recall, not a rebuild:** put L04's fixed-edge graph diagram up. "Every edge here is `add_edge` — always A to B, no matter what state says. That's the whole graph vocabulary from last lesson except one thing."
2. State the new primitive on the board: a **conditional edge** is a transition chosen at *runtime* by a **routing function** — a plain Python function that reads **state** and returns the name of the next node. Write the skeleton on the board: `def route(state) -> str: ...` then `add_conditional_edges("classify", route, {"billing": "billing_node", ...})`.
3. Live-code a minimal two-node graph: a `classify` node that calls **Haiku** and writes a `category` field into state, and a routing function that reads `state["category"]` and returns it directly (mapping label to node name one-to-one). Wire it with a single conditional edge out of `classify`.
4. `compile()`, then `invoke()` on the chosen ticket. Use the pre-flight run-inspection fallback to show, explicitly, which branch executed.
5. **Trace the value by hand on the board**, slowly: the model produced a label → the `classify` node wrote it into `state["category"]` → the routing function *read* `state["category"]` → `add_conditional_edges`'s mapping turned that string into a node name → LangGraph executed that node. Five arrows, five hops — walk every one.

**What to highlight:**

- **The routing function is plain Python, not a model call.** It's an `if`/dict-lookup over state — the "decision" already happened when the `classify` node wrote its label; the routing function only *reads*.
- **"Runtime-chosen" is not "unpredictable."** Say it early, it recurs all lesson: a conditional edge is still a deterministic function of state. Same state in, same branch out.
- **Name the L05-vs-L11 line for the first time here, briefly** (Demo 4 owns the full version): "the routing function reads state *I* control. Ten lessons from now, a routing function will read whether the *model* asked for a tool. Different question, same LangGraph mechanism — we'll come back to this."

**If the demo misbehaves:**

- If live-coding the conditional edge falls behind, paste the completed two-node graph and walk the five-hop trace on the board anyway — the trace, not the typing, is the point of this demo.
- If Haiku's label doesn't match any key in the routing map, let it happen and note it out loud: "see that? An unmapped label is exactly the gap Demo 2 spends its whole time on." Don't fix it live — it's a preview, not a bug to squash.

## Demo 2 — Router/switch: classify, branch, converge — and the fallback case (Objective 2)

**Goal:** build the full **router/switch** pattern — an entry classifier fanning out to specialized branches that converge — and use it to (a) reinforce **per-node model mixing** as a *known* mechanism from L04, and (b) make the **ambiguous-classification / fallback-branch** case a deliberate, worked example rather than an embarrassment to route around.

**Pre-flight:**

- Demo 1's two-node skeleton, extended with three specialized branch nodes.
- The billing / technical / general branches sketched on the board, each with its own focused prompt, converging to a single `END`.
- The ambiguous ticket queued and ready to run *after* the clean cases.

**Live script:**

1. Extend Demo 1's graph: add three specialized branch nodes (`billing`, `technical`, `general`), each a **Sonnet** call with its own prompt, all wired to converge at `END`.
2. Recall, in one line, the per-node model-mixing mechanism from L04: "classify only needs a label — cheap model. The branches need judgment — capable model. Same mechanism as the sequential chain, just a different graph shape." Do not re-derive *why* this works; that was L04's job.
3. Run the three clean tickets (billing / technical / general) one at a time. Use the run-inspection fallback each time to confirm the branch matches the category, and re-run **one** ticket a second time to reinforce determinism from Demo 1: same input, same branch, every time.
4. **Now run the ambiguous ticket.** Let Haiku produce whatever label it produces — possibly a wrong one, possibly a label that isn't exactly `"billing"` / `"technical"` / `"general"` (e.g. it hedges, or returns something slightly off-format). Do not pre-fix the prompt to avoid this.
5. Show what happens without a fallback branch wired: either the routing function raises, or (if only the three keys are mapped) the graph errors on an unmapped label. Name it: "a router that only knows how to succeed isn't done."
6. Add a **fallback/default branch** — a `general` (or dedicated `needs_review`) node the routing function returns for any unmapped label — and re-run the ambiguous ticket. Show it now completes, landing somewhere defined.

**What to highlight:**

- **The router pattern:** one entry classifier, N specialized branches, one convergence point. This shape recurs constantly — name it so students recognize it in the wild.
- **Determinism, reinforced a second time (first in Demo 1):** the same ticket takes the same path on every run. This is *why* a router is trivially testable — the optional eval demo below cashes this in directly.
- **The fallback branch is not optional-nice-to-have, it's part of "the router is done."** A routing function needs defined behavior for every label it might see, not just the labels you expected. This is the single most important craft lesson in this demo — slow down here.
- **Per-node model mixing is exactly L04's mechanism, applied to a new shape.** Don't re-teach *why* mixing works (cost/latency/quality trade, L01-adjacent); just point at the two different models on the two kinds of nodes and move on. The *decision framework* for when to mix is L14's job — say that explicitly and keep going, don't improvise a mini-lecture on it.

**If the demo misbehaves:**

- If Haiku actually classifies the "ambiguous" ticket cleanly (models are good at this), that's fine — pick a harder ambiguous example live, or manually construct a state dict with an out-of-vocabulary `category` value and invoke the graph directly with it (skipping the classify node) to force the fallback path deliberately. The teaching point (a router needs a defined fallback) doesn't require the *model* to be the one that produces the bad label.
- If the trace/run-inspection doesn't clearly show which node ran, fall back to printing `state` before and after `invoke()` and diffing by eye — the mechanism matters more than the tooling polish.

## Demo 3 — Same shape, different decider: user-input branching (Objective 3)

**Goal:** take the router's exact shape from Demo 2 and swap the decider from a model classifier to **direct user input**, then put the two deciders head to head. Land the sharpest possible contrast with an agent: **a conditional edge can route on a value with no model anywhere near the decision.**

**Pre-flight:**

- Demo 2's completed router graph.
- The `user_choice` version of the sample tickets from pre-flight (a structured selection, not free text).

**Live script:**

1. Show the swap explicitly: remove the `classify` node, and instead have `user_choice` arrive as a field already present in the **initial state** passed to `invoke()` — e.g. `graph.invoke({"ticket": ..., "user_choice": "billing"})`. The routing function changes from reading `state["category"]` (a model's label) to reading `state["user_choice"]` (a value nobody computed — it was just handed in).
2. Run it with a few different `user_choice` values and confirm the deterministic branch each time, using the same run-inspection fallback as before.
3. **Put the two graphs side by side on screen** — Demo 2's classifier-routed graph and this user-input-routed graph. Same node shapes, same conditional-edge mechanism, same convergence at `END`. The only difference: *where the value in state came from.* Say it as a single sentence and repeat it: "same graph shape, different decider."
4. Land the sharpest framing of the lesson: in the user-input version, **no model is involved in the routing decision at all** — not even to produce a label. The user picked; the developer wired the options; the routing function just read a field. This is as far from "the model is deciding" as a conditional edge can get.
5. Build the **combined** shape in a few lines: route on `user_choice` first (developer-owned edge), and *inside* the chosen branch node, still make a model call (e.g. the `billing` branch still calls Sonnet to draft a reply). Say the rule this demonstrates out loud: **the user (or developer logic) owns the edge; the model can still do real work inside a node.** This is the shape most real conditional workflows actually take.

**What to highlight:**

- **"Same shape, different decider" is the single most reusable sentence in this lesson.** A router's *shape* — entry point, conditional edge, branches, convergence — doesn't care whether the decider is derived data, a model label, or a human choice. Only the source of the value changes.
- **User-input branching is the cleanest anchor against "the model is choosing."** Whenever a student later conflates a conditional edge with model agency, come back to this demo: here, unambiguously, there is no model in the loop at all.
- **Forward pointer, one line, don't teach it:** "this `user_choice` arrived before the graph ever started running. A graph that *pauses mid-run* to ask the user and *resumes* on the answer needs LangGraph's `interrupt` and a checkpointer — that's L17's territory, much later. Today, the input is just... already there."

**If the demo misbehaves:**

- If students conflate "the user picked a branch" with "the agent asked the user a question," re-draw the side-by-side: in this demo the value is sitting in the initial state dict *before* `invoke()` is ever called — nothing is asked *during* the run. The asking-mid-run version doesn't exist yet in anything students have seen.
- If time is short, cut the combined shape (step 5) to a single slide rather than live code — the side-by-side comparison (steps 3–4) is the load-bearing part of this demo.

## Demo 4 — Closing the arc: what L05 is, and precisely what L11 changes (Objective 4)

**Goal:** deliver the **closing argument** of the workflow-vs-agent arc that opened at L04: name, with precision, the *one* thing that changes between a L05 conditional edge and an L11 (agent) conditional edge. Do **not** build the agent or a cycle here — this demo is diagram and discussion, naming the delta so precisely that L11 contains no surprises.

**Pre-flight:**

- Demo 2's or Demo 3's compiled router diagram, rendered and on screen.
- A **sketch** (not a live build, not runnable code) of the L11 shallow-agent shape: an `agent` node, a `tools` node, and a conditional edge out of `agent` that either loops back to `tools` or exits to `END`.

**Live script:**

1. Put a L05 router diagram up. Trace a path with your finger: entry → conditional edge → one branch → `END`. Every arrow still moves forward. Name it: **still a DAG, still acyclic, still a workflow** — no matter how many branches it has.
2. Ask the routing-function question out loud for the L05 graph: "what does this routing function look at?" Answer together: **state the developer put there** — a computed value, a model's classification label, or direct user input. Never "did the model decide to call a tool."
3. Now put the L11 sketch up next to it. Same shape of question, same LangGraph mechanism (`add_conditional_edges`, a routing function) — but ask it again for this graph: "what does *this* routing function look at?" Answer: **whether the model's last `AIMessage` has `tool_calls`.** The value being read didn't come from a developer-written node — it came from the model's own output, un-mediated by a developer-authored label.
4. Point at the one structural difference beyond the decider: the L11 sketch has an edge **from `tools` back to `agent`** — a cycle. Name it precisely: "every graph you built today was acyclic. The agent has exactly one back-edge. That back-edge, plus a model-authored decision instead of a developer-authored one, is the entire distance between what you built this lesson and an agent."
5. Before leaving the sketch, broaden it: the agent's tool loop is **not the only reason a graph ever loops back**. Sketch (don't build) two **developer-owned** back-edges next to it: a **retry / self-correction loop** (`generate → validate`, where `validate` routes back to `generate` until a pass flag is set or an attempt counter in state runs out) and an **evaluator–optimizer loop** (`draft → critique`, routing back to redraft until the critique's score clears a bar). Ask the room the decider question for each: *who decides whether to go around again?* A developer-authored check — a flag, a counter, a score bar. **Still workflows, loops and all.** Only the third loop — where the routing function reads the model's own decision to call a tool — is the agent. This sharpens L04's first-cut line "a workflow never loops back" into the honest version: *a workflow can loop back, but **you** wrote its exit condition.*
6. Say the full closing line, slowly, as the lesson's last main point: *"L04 gave you a graph with no branches. L05 gave you a graph with branches you own. In a few lessons, L11 gives you a graph with a branch the **model** owns, wired into a loop. Same primitives the entire way — `StateGraph`, nodes, edges, conditional edges, state, reducers. The only thing that ever changes is who decides."*
7. Reason briefly about **when developer-controlled branching (today) is the right tool** versus when it isn't: a router is right whenever the set of possible paths is known ahead of time and choosing among them is a classification, lookup, or user choice. Name the common failure mode: reaching for an agent to do what a router would do at a fraction of the cost and unpredictability — this is the same failure mode named in L04's Demo 4, reinforced here on the routing case specifically.

**What to highlight:**

- **The delta is precise, not vague.** Resist "agents are just fancier routing" — that's true mechanically and misleading pedagogically. The precise version: *same API, different source of authority over the value being read, plus a back-edge.* Say the precise version.
- **A back-edge alone isn't an agent.** The loop taxonomy (step 5) exists to keep "cycle" from becoming the students' definition of agent — retry and evaluator–optimizer loops are cyclic *workflows* because the exit condition is developer-authored. Keep every loop on the same axis the lesson has drilled all day: who decides.
- **This demo is mostly diagram + discussion — resist the urge to build anything.** Building the cycle is L11's entire lesson; if this demo starts writing agent code, it has overstepped into L11's territory and stolen its payoff.
- **The arc has a start (L04) and this is its middle-to-end, not its final word** — L11 is still where the agent actually gets built. This demo's job is to make sure that when it does, nothing about it is a new mental model, only a change of decider plus one new edge.

**If the demo misbehaves:**

- This demo is low-risk (no live code to break). If a student pushes back with "but the classifier in Demo 2 already feels like the model deciding," reach back to Demo 2 and Demo 3's framing together: the model produced a *label*; a *user* produced a *value with no model at all*; in both cases a developer-written routing function did the actual choosing. Only in the L11 sketch does the *model's own tool-call decision* get read directly by the routing function, with no developer-authored label in between.

## Common pitfalls coda — naming L05's three gotchas

**Shape note:** a short **"common pitfalls" coda**, not a new live demo — L05 already *touches* each of these across Demos 1, 2, and 4. Its job is to **name** them as portable gotchas, restate the cure in a line, and pin each back to where the room saw it. Budget ~5 minutes as a recap slide. Follows the [L23 Demo 5](../L23/demos_or_activities.md#demo-5--the-three-composition-anti-patterns-objective-5) anti-pattern-beat template (name it → show it break → state the cure → tie to the payoff), like the [L01](../L01/demos_or_activities.md#common-pitfalls-coda--naming-l01s-four-gotchas) and [L04](../L04/demos_or_activities.md#common-pitfalls-coda--naming-l04s-two-gotchas) codas. Two of these three — the workflow-vs-agent and brittle-branch gotchas — are the ones the [L04/L05 split](objectives.md) moved *out* of L04's coda and into L05, which now owns the routing material; L05 adds the third (the decider slip) on top.

**Goal:** turn the workflow-vs-agent close (Demo 4) and the router/fallback beat (Demo 2) into three named routing gotchas a student can catch when they wire their own conditional edge.

**Pre-flight:**

- Nothing new to load. One recap slide; the Demo 2 router diagram and the Demo 4 L11 back-edge sketch still on screen to point back at.

**Live script (recap — point back, don't re-run):**

1. **Workflow where an agent is needed — or the reverse.** ❌ Reaching for an agent when the task has a known shape (more cost, less predictability, harder to debug), or forcing a rigid routed DAG when the steps genuinely can't be known in advance. Point back at Demo 4 ("what L11 changes"). **Cure:** default to the simplest shape that fits — a router is right whenever the set of possible paths is known ahead of time and picking among them is a classification, lookup, or user choice; a back-edge (agency) is a deliberate choice, not a nicety.
2. **Brittle branch conditions.** ❌ A routing function that assumes the classifier returns one of the expected labels and `KeyError`s (or silently mis-routes) when the model returns something off-menu. Point back at Demo 2's ambiguous ticket. **Cure:** validate the label is in the allowed set (L02's [enum-as-contract](../L02/objectives.md)) and always wire a default / `END` branch — a router that only knows how to succeed isn't done.
3. **Letting the model own the branch by accident.** ❌ Wiring the routing function to route on a *raw model output* — the model's free-form reply used as the destination — instead of on a small **validated label** your plain-Python code branches on. That quietly hands the *model* the choice of path: the L05→L11 line crossed without deciding to. Point back at Demo 1's five-hop trace (the routing function *reads* state **you** control) and Demo 4's precise L05-vs-L11 delta. **Cure:** the classifier writes a constrained label (again L02's enum-as-contract); the developer's routing function reads *that* and owns the branch. If you actually want the model to choose the path, build an agent ([L11](../L11/objectives.md)) on purpose — don't back into one.

**What to highlight:**

- **#1 and #3 are the workflow-vs-agent line at two altitudes**, and keeping that line sharp is L05's whole spine (Demo 4): #1 is choosing the wrong *shape* on purpose (an agent where a router would do); #3 is the *mechanism* slipping — the model taking the wheel by accident because the routing function read the model's raw output instead of a label you validated. #2 is the different axis: routing *robustness*, not who decides.
- **#3 points straight forward to [L11](../L11/objectives.md)** (where reading the model's own decision is the whole point, on purpose) and **#2's cure leans back on [L02](../L02/objectives.md)** (the structured-output-by-instruction discipline). Name the links, **don't re-teach them here.**

**If a student pushes back:**

- "The Demo 2 classifier is a model — isn't that the model deciding (gotcha #3)?" No — the model produced a *label*; the developer's plain-Python routing function read that label and picked the edge (Demo 1's trace). #3 only bites when you skip the validated-label step and let the model's raw output *be* the branch. The model doing work inside a node is fine; the model owning the edge is the line.

## Optional demo — evaluate the router (carry L04's eval habit forward)

If time allows, close by reinforcing the same habit L04's optional demo introduced, now applied to routing instead of chaining. A router is, if anything, an *easier* eval target than a linear chain — every case is "given this input, was the branch correct?"

1. Recall L04's optional eval-the-workflow beat in one line — don't re-teach `common/evals.py`'s mechanics, just recall that it exists and was used once already.
2. Import the harness from `common/evals.py` and write ~4–5 `EvalCase`s over the Demo 2 router: an input ticket in, the expected `category` (and by extension, the expected branch) out. Include the ambiguous ticket as one case, with the **fallback branch** as its expected outcome — this doubles as a regression check that the fallback wiring from Demo 2 actually works.
3. Run `evaluate(...)` and read the pass rate. Land the point: a router's determinism (Demos 1–2) is *why* this eval is cheap and meaningful — same input always takes the same path, so "did it take the right path" is a clean, binary, automatable question.

<!-- *NEED INPUT*: include this eval-the-router beat in the lecture, or hold it for the L05 lab? Same open question as L04's demos file raised for its own optional eval beat — resolve both together if possible, since a consistent answer (both in-lecture, or both lab-only) will read better across the two lessons than a split decision. -->

## Pacing notes for the teacher

- **Per-demo time:** Demo 1 is short (10–15 minutes — it's one new idea, traced once). Demo 2 is the long one (18–22 minutes including the router build, the clean runs, and the fallback-branch worked example — don't rush the ambiguous-ticket beat, it's the demo's whole point). Demo 3 is 12–15 (the decider swap, the side-by-side, the combined shape). Demo 4 is 10–15 (diagram + discussion, no build, but don't rush the closing line — let it land). Optional eval beat is 5–8. Total ~55–75 minutes plus discussion — fits the ~60–75 minute single lecture proposed in [objectives.md](objectives.md)'s open questions. If it runs long, the natural split point is after Demo 2: "the conditional edge + router" then "user-input decider + workflow-vs-agent close."
- **Live-coding budget:** only Demo 1's minimal two-node graph and Demo 2's branch-node additions need live-coding. Demo 3 is a small, mostly-edit change to Demo 2's graph. Demo 4 is diagram + talk, no code. Do **not** re-derive `StateGraph`'s basic builder API — that was L04's job; if a student has forgotten it, point back to L04 rather than re-teaching it here.
- **The ambiguous ticket is not optional.** Every other demo file in this course has a "keep the misbehavior, don't paper over it" note; here it's promoted to a required beat, because the fallback-branch lesson doesn't land without a genuine (or deliberately constructed) unmapped-label case.
- **The audience watches, doesn't participate.** Hands-on router-building, the decider comparison exercise, and constructing a fallback branch from scratch are L05 lab material (stage 2), not this file's job.

## Open authoring questions

Most of L05's big decisions are already pinned in [objectives.md](objectives.md) (developer-owned deciders only; native `ChatAnthropic`, reused not re-explained; Haiku-classifier/Sonnet-branch mixing as mechanism only, decision framework deferred to L14; user-input branching in the initial-state form only, `interrupt`/checkpointer deferred to L17; the precise L05-vs-L11 delta). The remaining open items are stage-2 mechanics, several shared with L04's still-open items:

- <!-- *NEED INPUT*: exact model id strings for the Haiku 4.5 and Sonnet 4.6 snapshots, read from common/config.py rather than hard-coded in cells — same open item as L04's demos file; resolve once for both lessons. -->
- <!-- *NEED INPUT*: running-example domain — this file assumes continuation of L04's support-ticket domain; confirm in stage 2 or pick a distinct domain (see objectives.md for the same flagged choice). -->
- <!-- *NEED INPUT*: the exact sample tickets, in particular the deliberately ambiguous one that stresses the classifier for Demo 2's fallback-branch beat — recommend reusing L04's fixture plus one additional hard case. -->
- <!-- *NEED INPUT*: the exact user_choice shape for Demo 3 (a plain string enum is the simplest option; confirm no richer structure is wanted). -->
- **Resolved:** run-inspection across every demo in this file is `graph.stream(stream_mode="updates")` node-update events — the L03 → L10 through-line — not print statements or a Mermaid highlight.
- <!-- *NEED INPUT*: are the demos run in a projected Jupyter notebook, a slide-embedded REPL, or a demo-runner script? Mirrors the same open question in L04's, L10's, and L13's demos files. -->
- <!-- *NEED INPUT*: include the optional eval-the-router beat in the lecture or hold it for the lab? Same open question as L04's demos file raised for its own optional eval beat — consider resolving both together for consistency. -->
