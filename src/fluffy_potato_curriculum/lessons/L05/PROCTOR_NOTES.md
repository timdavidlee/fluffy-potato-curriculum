# L05 Proctor Notes

Covers the L05 lab: **L0504** (routing + user-input branching + optional eval). Runs **fully
offline** — a deterministic `StubChat` stands in for `ChatAnthropic`, so no API key is needed and
every run is reproducible. The focus is **graph wiring** (conditional edges, deciders), not model
output. The lecture demo ([L0503](L0503_lecture.ipynb)) uses the real `ChatAnthropic` client; the
lab deliberately doesn't, so the wiring is the only variable.

> Keep repeating the lesson's spine: **a conditional edge is not the model deciding.** Every branch
> in this lab is decided by *code the student wrote* reading *state*, never by the model deciding
> to call a tool. That's L14.

---

## L0504_lab problem 1 — Routing state + classify node

COMMON GOTCHAS:
- `RouteState` needs **both** `category` (set by the model) and `user_choice` (set by the user in
  problem 5). Students often add only one; the lab reuses one state type for both deciders.
- The classifier must keep **only** a known label. If the stub/model returns extra words, the
  `next((c for c in (...) if c in label), "general")` guard defaults to `general`. Skipping the
  guard means an unknown label reaches the conditional edge and **raises at routing time**.

UNBLOCKERS: Remind them the stub keys on **ticket content** words (charge/refund/twice → billing;
error/500/crash → technical; else general). It deliberately ignores the instruction's listed
category words.

TIME: 6–10 min. STRETCH: ask why `classify` is on the *cheap* model — it only needs a one-word label.

## L0504_lab problem 2 — The branch nodes

COMMON GOTCHAS:
- Three near-identical functions invite copy-paste bugs (e.g. the `technical` node returning
  `"steps": ["billing"]`). Then problem 4's path prints the wrong branch name — a good catch.
- Same `.content` / partial-update reminders as L04's L0404 problem 2.

UNBLOCKERS: A factory (`make_branch`) is fine if they prefer it (the demo uses one) — but three
explicit functions are clearer and equally correct.

TIME: 6–8 min. STRETCH: give one branch its own distinct prompt and confirm the trace still shows one
branch span.

## L0504_lab problem 3 — The conditional edge

COMMON GOTCHAS:
- The biggest conceptual miss: thinking `route` "asks the model." It does **not** — it returns
  `state["category"]`, a label already in state. Say it out loud with them.
- `add_conditional_edges("classify", route, {...})` — the **mapping** keys must match what `route`
  returns and the values must be real node names. A mismatch (`{"bill": "billing"}` while `route`
  returns `"billing"`) raises at runtime.
- Forgetting to wire each branch to `END`.

UNBLOCKERS: Have them print `draw_mermaid()` — the dashed conditional edges from `classify` should fan
to all three branches, all converging on `END`.

TIME: 8–12 min. STRETCH: what happens if `route` returns a key not in the mapping? (It raises — a
nudge toward validating model output, an L02/L12 theme.)

## L0504_lab problem 4 — Run and prove determinism

COMMON GOTCHAS:
- Same `steps: []` seeding gotcha as L04's L0404 problem 4.
- Expecting the *reply text* to prove determinism — it's the **path** (`out["steps"]`) that's the
  invariant. The two-invocation equality check is the proof.

UNBLOCKERS: If two runs differ, a node is mutating shared module state — check the nodes return fresh
dicts and don't append to a global list.

TIME: 4–6 min. STRETCH: ask how they'd *measure* path stability over many tickets — leads into
problem 6.

## L0504_lab problem 5 — Same graph, user-input branch

COMMON GOTCHAS:
- Confusing this with "the agent asks the user." Re-draw it: `user_choice` is **already in the
  initial state** before the run; nothing is asked mid-run. The asking-mid-run (`interrupt`) version
  is **L17**.
- `route_by_user` must read `state["user_choice"]`, **not** call any model. Some students reflexively
  add a model call — that defeats the whole point (no model in the routing decision).
- The `intake` node is a plain pass-through returning `{"steps": ["intake"]}` — it exists only to
  give the conditional edge a source node.

UNBLOCKERS: The tell-tale check: feed a **technical** ticket with `user_choice="billing"` → the path
must be `['intake', 'billing']`. If it routes to `technical`, they wired the edge to the classifier
or read the wrong field.

TIME: 8–12 min. STRETCH: combine — route on the user's choice, then read state inside the branch — to
feel "user owns the edge, model works inside the node."

## L0504_lab problem 6 (optional) — Evaluate the classifier

COMMON GOTCHAS:
- Calling `classify` with a bare string instead of a state dict — it takes `{"ticket": ..., "steps":
  []}` and returns a dict; the label is `["category"]`.
- Being surprised the pass rate isn't 4/4. **That's the lesson.** The last case ("crashing … want a
  refund") mentions a refund (billing) *and* a crash (technical); the classifier checks billing
  keywords first, so it labels it `billing` while the eval expects `technical`. Don't let them "fix"
  the data to force 4/4 — the eval is doing its job by surfacing a real ambiguity.

UNBLOCKERS: This is the L12 discipline inlined ("when you build something, you evaluate it"). One line:
a deterministic workflow is the *easiest* thing to evaluate — same input → same path. This same eval
set rides forward onto the L14 agent.

TIME: 5–8 min. STRETCH: add two more cases; or change the classifier to check technical keywords
first and watch which cases flip — eval as a feedback loop.

## L0504_lab problem 7 — Workflow vs. agent (written)

EXPECTED ANSWER: Add a **conditional edge that loops back to the model** (a back-edge / cycle) so the
**model** decides whether to keep going (call a tool) or stop. That single back-edge converts the
acyclic workflow into a cyclic, model-driven **agent** — and hands control of the path from the
developer to the model. (It's the L10 loop, now as a graph edge; built for real in L14.) This is the
exact question [L0505_lecture.md](L0505_lecture.md) answers in full.

COMMON GOTCHAS: Answers that say "use a bigger model" or "add more nodes" miss it — the change is
*structural* (a cycle) and *about control* (the model decides), not about capability or size.

TIME: 3–5 min.
