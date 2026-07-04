# L13 lecture: Carry the eval set forward

```yaml
title: "L13 lecture: Carry the eval set forward"
keywords: evaluation, practice, ratchet, carry forward, langgraph, L04, L11, llm-as-judge, langfuse dataset, experiment, run comparison
estimated duration: 8
```

> **Lesson:** L13 — Evaluation: first pass. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L13/objectives.md) (objective 5) · [demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L13/demos_or_activities.md) (bridge demo).
> **Comes after:** `L1306_lecture` (you put a cost on an eval run, walked the scorer spectrum, and turned on a managed judge). This short closer makes the *practice* concrete: the dataset you built is the thing you carry forward.

## section 1. The rule, stated once

### slide 1.1 The discipline this lesson establishes

- text: the PRD singles L13 out as a *practice to carry forward*. Say the rule out loud and keep it:
- text: **when you build or change an agent, you add or run an eval set.** Not "when you have time" — every time.
- text: the cases you wrote this lesson live as the **`l13-agent-evals` Langfuse dataset**. The vocabulary behind them — `EvalCase`, the `Scorer` protocol — sits in `fluffy_potato_curriculum.common.evals`, with `upload_dataset` to push the set and `emit_score` to record verdicts. It's promoted to `common/` for exactly one reason: so the *next* agent runs the **same dataset** instead of reinventing it.
- diagram: a ratchet wheel labeled "l13-agent-evals dataset" with a pawl labeled "regression check (run comparison)" — turns forward (new passing cases) but cannot slip back (a regression is caught before shipping).

### slide 1.2 Why a ratchet, not a one-time test

- text: a unit test pins a deterministic output once. An eval set is a *ratchet*: once a case passes, any later change that breaks it is a regression you catch **before** shipping — re-run the dataset as an experiment and Langfuse's run comparison flags the pass→fail.
- text: the cost of *not* having it is asymmetric: writing the case is minutes; rediscovering the bug in production is hours plus the damage it did in between.

[↑ Back to top](#l13-lecture-carry-the-eval-set-forward)

## section 2. The very next lessons

### slide 2.1 L04 (workflows) — the cheapest place to start the habit

- text: in the mini cut the next taught lesson is **[L04 (Explicit graphs & workflows / DAGs)](../../../../docs/origin/lesson_roadmaps/L04/objectives.md)**. A deterministic workflow is *trivially* evaluable — fixed path, known outputs — so it's the gentlest possible place to attach an eval set (a handful of cases, uploaded as a dataset) and feel the habit with almost no friction.

### slide 2.2 L11 (shallow agents) — the ratchet's headline demonstration

- text: in **L11** you rebuild the agent with LangGraph's prebuilt `create_agent` (a shallow-agent one-liner). The handoff is the *practice*, not a file: run the **same `l13-agent-evals` dataset** as a **Langfuse experiment** against the new implementation.
- text: *same dataset, different implementation — did anything regress?* Two dataset runs — L13's reference L10 graph (`agent_graph`) and L11's `create_agent` agent — line up in Langfuse's **run-comparison view**, the cleanest possible demonstration of the ratchet. (L11 itself comes *before* L13 and checks its L10-equivalence by eye; the repeatable experiment is what you add here and carry forward — L11's own lab doesn't run it.)
- diagram: two boxes — "L13 reference graph (`agent_graph`)" and "L11 `create_agent` agent" — both run as experiments over the *same* `l13-agent-evals` dataset, producing two dataset runs compared side by side in Langfuse.

[↑ Back to top](#l13-lecture-carry-the-eval-set-forward)

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

### slide 3.2 The tooling forward pointer

- text: L13 already lives on the self-hosted **Langfuse** you met in L12: you uploaded the `l13-agent-evals` **dataset**, launched **experiments** (Sonnet vs Haiku), read the **run comparison**, and turned on a **managed LLM-as-judge**. The `evaluate()` / `compare()` in `common/evals.py` are the readable *concept sketch* underneath — not the runner.
- text: the payoff of building the vocabulary by hand first is the same as L12's: the dataset items, scores, and experiments you clicked through *are* the exact `EvalCase` / `EvalResult` / run structure you already wrote.
- text: a later at-scale eval lesson doesn't introduce the platform — it deepens what you run on it: multi-step graphs, retrieval quality, judges done properly, and multi-agent systems.
- text: closing line: *"you built the vocabulary by hand, ran it on the real platform, and every agent you build from here comes with a dataset you can re-run."*

[↑ Back to top](#l13-lecture-carry-the-eval-set-forward)
