# Carry the eval set forward

```yaml
title: "Carry the eval set forward"
keywords: evaluation, practice, ratchet, carry forward, langgraph, L03, L11, LLM-as-judge, Langfuse dataset, experiment, run comparison
estimated duration: 8
```

> **Lesson:** L13 — Evaluation: first pass. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L13/objectives.md) (objective 5) · [demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L13/demos_or_activities.md) (bridge demo).
> **Comes after:** `L1306_lecture` (you put a cost on an eval run, walked the scorer spectrum, and turned on a managed judge). This short closer makes the *practice* concrete: the dataset you built is the thing you carry forward.

## section 1. The rule, stated once

### slide 1.1 The discipline this lesson establishes

- text: the PRD singles L13 out as a *practice to carry forward*. Say the rule out loud and keep it:
- text: **when you build or change an agent, you add or run an eval set.** Not "when you have time" — every time.
- text: the cases you wrote this lesson live as the **`l13-agent-evals` Langfuse dataset**. The vocabulary behind them — `EvalCase`, the `Scorer` protocol — sits in `fluffy_potato_curriculum.common.evals`, with `upload_dataset` to push the set and `emit_score` to record verdicts. It's promoted to `common/` for exactly one reason: so the *next* agent runs the **same dataset** instead of reinventing it.
- diagram: a ratchet wheel labeled "l13-agent-evals dataset" with a pawl labeled "regression check (run comparison)". Colour intent: the wheel, its forward-turn arrow ("new passing cases"), and the pawl are all **cyan** — the practice is this lesson's own contribution; the only **coral** element is the attempted slip-back arrow, drawn caught dead against the pawl ("a regression is caught before shipping"). This ratchet is the closer's motif — it turns again at 1.2 and shows up broken (pawl missing) on anti-pattern #5 in 4.1.

### slide 1.2 Why a ratchet, not a one-time test

- text: a unit test pins a deterministic output once. An eval set is a *ratchet*: once a case passes, any later change that breaks it is a regression you catch **before** shipping — re-run the dataset as an experiment and Langfuse's run comparison flags the pass→fail.
- text: the cost of *not* having it is asymmetric: writing the case is minutes; rediscovering the bug in production is hours plus the damage it did in between.
- diagram: two-up contrast, and the ratchet motif's second beat. Left panel in **ink-faint**: a unit test as a single static checkmark that pinned one deterministic output once — timeline flat after it. Right panel: the 1.1 ratchet turning forward across "change 1 → change 2 → change 3", with a **coral** pass→fail arrow trying to slip back and the **cyan** pawl catching it before a "ship" chip. Below, the asymmetry as two bars (cost claims get a chart, not prose): a short **cyan** bar "write the case: minutes" vs a tall **coral** bar "rediscover in production: hours + damage".

[↑ Back to top](#carry-the-eval-set-forward)

## section 2. The very next lessons

### slide 2.1 L03 (workflows) — the cheapest place to start the habit

- text: in the mini cut the next taught lesson is **[L03 (Explicit graphs & workflows / DAGs)](../../../../docs/origin/lesson_roadmaps/L03/objectives.md)**. A deterministic workflow is *trivially* evaluable — fixed path, known outputs — so it's the gentlest possible place to attach an eval set (a handful of cases, uploaded as a dataset) and feel the habit with almost no friction.
- diagram: bridge — re-draw the L03 acyclic chain exactly as L03's own deck renders it (three **cyan** nodes joined by straight **cyan** edges, no back-edge: "developer owns the path"), with a **cyan** dataset chip ("a handful of cases, `upload_dataset`") feeding the entry node and a column of **cyan** checkmark chips off the END node ("fixed path, known outputs"). No coral anywhere — the point is zero friction; one **dashed ink-faint** annotation ties it back: "same dataset mechanics as this lesson".

### slide 2.2 L11 (shallow agents) — the ratchet's headline demonstration

- text: in **L11** you rebuild the agent with LangGraph's prebuilt `create_agent` (a shallow-agent one-liner). The handoff is the *practice*, not a file: run the **same `l13-agent-evals` dataset** as a **Langfuse experiment** against the new implementation.
- text: *same dataset, different implementation — did anything regress?* Two dataset runs — L13's reference L10 graph (`agent_graph`) and L11's `create_agent` agent — line up in Langfuse's **run-comparison view**, the cleanest possible demonstration of the ratchet. (L11 itself comes *before* L13 and checks its L10-equivalence by eye; the repeatable experiment is what you add here and carry forward — L11's own lab doesn't run it.)
- diagram: the ratchet's headline picture, built from the course's own motifs: left, the L10 two-node cycle with its **cyan** back-edge, labeled "L13 reference graph (`agent_graph`)"; right, the same small cycle inside L11's **cyan** `create_agent(...)` bracket box. Both feed arrows down into one shared **cyan** `l13-agent-evals` dataset chip — the *fixed* thing — which fans out to two dataset-run columns side by side in Langfuse's run-comparison grid. Grid cells cyan / ink-faint, with exactly one **coral** pass→fail cell flagged ("did anything regress?" — this is what the pawl catching looks like in the UI).

[↑ Back to top](#carry-the-eval-set-forward)

## section 3. Where this scales (and where it stops)

### slide 3.1 L13 is a first pass, on purpose

- text: a small readable vocabulary plus one shared dataset on Langfuse is *enough* to establish the habit. Naming the boundary keeps the lesson honest and the scope small.
- table: what L13 deliberately leaves to a later, at-scale evaluation lesson.

| L13 (first pass) | later: evaluation at scale |
| --- | --- |
| one shallow ReAct graph | multi-step LangGraph graphs: per-node vs. end-to-end metrics |
| outcome + trajectory checks | retrieval quality for RAG (precision@k / recall@k) |
| one illustrative LLM-judge | LLM-as-judge done properly — what it can and can't reliably score |
| a single agent | multi-agent systems (subagent quality vs. orchestration quality) |
| a handful of cases, K=3–5 | scaling eval cost (sampling strategies, CI gating) |

- diagram: scope fence (the table stays): one solid **cyan** box "L13 — first pass" holding four chips (one shallow ReAct graph · outcome + trajectory checks · one illustrative judge · a handful of cases, K=3–5), ringed by **dashed ink-faint** ghost chips for everything the table defers (per-node metrics · RAG retrieval quality · judge rigor · multi-agent · CI gating), the ring labeled "→ at-scale eval lesson". Dashed = deferred, not failure — no coral anywhere.

### slide 3.2 The tooling forward pointer

- text: L13 already lives on the self-hosted **Langfuse** you met in L12: you uploaded the `l13-agent-evals` **dataset**, launched **experiments** (Sonnet vs Haiku), read the **run comparison**, and turned on a **managed LLM-as-judge**. The `aevaluate()` / `compare()` in `common/evals.py` are the readable *concept sketch* underneath — not the runner.
- text: the payoff of building the vocabulary by hand first is the same as L12's: the dataset items, scores, and experiments you clicked through *are* the exact `EvalCase` / `EvalResult` / run structure you already wrote.
- diagram: two-layer stack with tie-lines (the L12 hand-rolled→platform payoff picture, re-drawn for evals): bottom layer **dashed ink-faint** — `common/evals.py` (`EvalCase` · `Scorer` · `aevaluate()` / `compare()`), labeled "readable concept sketch, not the runner"; top layer **cyan** — the self-hosted Langfuse (dataset · experiments · run comparison · managed judge). **Cyan** tie-lines pair each hand-rolled name with the platform object it *is*: `EvalCase` ↔ dataset item, `EvalResult` ↔ score, a run ↔ an experiment. Explicitly no coral — nothing on this slide fails.
- text: a later at-scale eval lesson doesn't introduce the platform — it deepens what you run on it: multi-step graphs, retrieval quality, judges done properly, and multi-agent systems.
- text: closing line: *"you built the vocabulary by hand, ran it on the real platform, and every agent you build from here comes with a dataset you can re-run."*

[↑ Back to top](#carry-the-eval-set-forward)

## section 4. Five eval anti-patterns, named

### slide 4.1 The five — and the brittle scorer that cuts across them

- text: the demos showed each of these break; let's name them now as portable anti-patterns you can
  catch when you write your *own* eval set. Two families run underneath: **#1 and #4 are the same discipline
  — eval design starts in the trace** (L12's side); **#2, #3, and #5 are the "don't trust one number"
  family** — one run, one judge, one terminal table are each a single point you shouldn't build on.
- table: the five anti-patterns, the one-line cure, and where you saw it.

| Anti-pattern | Cure | Where you saw it |
| --- | --- | --- |
| **Happy-path-only eval set** — cases you imagined passing, none drawn from real failures | trace a failure → add a case that fails-when-broken and passes-when-fixed → keep it forever | [`L1302`](L1302_lecture.ipynb) — cases come from observed traces, not imagination |
| **Sample too small** — one green run treated as proof on a non-deterministic agent | a pass *rate* over K samples, not a single verdict | [`L1304`](L1304_lecture.ipynb) — "one run can be luck" |
| **Over-trusting the LLM-as-judge** — a judge's verdict taken as ground truth | place it on the cost/judgment spectrum (assertion → fuzzy → judge → human), cross-check it, never treat it as an oracle | [`L1306`](L1306_lecture.ipynb) — the scorer spectrum |
| **Not targeting failure modes seen in traces** — scoring generic quality instead of the specific bugs **L12** surfaced | one regression case per observed trace failure (runaway, wrong-args, premature termination) | [`L1302`](L1302_lecture.ipynb) — the trace is the source of truth |
| **Regressions that slip through** — no durable before/after comparison, so a fix that breaks something else goes unnoticed | keep every experiment run (the Langfuse ratchet); compare today vs. last week, not vs. memory | [`L1304`](L1304_lecture.ipynb) — run comparison + slide 1.2 above |

- text: and one cross-cutting fault that sits *inside* the scorers — the **over-tight (brittle)
  check**: an exact-string match red-flagging a correct-but-reworded answer. It trains you to ignore
  reds, which is worse than no check. **Cure:** use the *loosest check that still catches the bug*
  (the `L1302` brittleness beat and the `L1303` "loosen a brittle check" lab). A single green on an
  imagined happy-path case is anti-patterns #1, #2, and #5 at once.
- diagram: the five anti-patterns as **coral** chips grouped under two family brackets — "#1 + #4: eval design starts in the trace (L12's side)" and "#2 + #3 + #5: don't trust one number" — each chip carrying a small **cyan** cure tag (the table's cure column, one phrase each). Chip #5 gets a tiny pawl-less ratchet glyph — the 1.1 motif, broken. Beneath, the cross-cutting brittle-check fault as its own strip: a **coral** exact-string gate red-flagging a correct-but-reworded answer, with the **cyan** cure beside it ("loosest check that still catches the bug"). The table stays.

[↑ Back to top](#carry-the-eval-set-forward)
