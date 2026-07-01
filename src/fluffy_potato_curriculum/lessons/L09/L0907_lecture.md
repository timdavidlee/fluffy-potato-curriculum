# L09 lecture: Carry the eval set forward

```yaml
title: "L09 lecture: Carry the eval set forward"
keywords: evaluation, practice, ratchet, carry forward, langgraph, L11, L12, L23, llm-as-judge, langfuse datasets
estimated duration: 8
```

> **Lesson:** L09 — Evaluation: first pass. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L09/objectives.md) (objective 5) · [demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L09/demos_or_activities.md) (bridge demo).
> **Comes after:** `L0906_lecture` (you put a cost on an eval run and walked the scorer spectrum). This short closer makes the *practice* concrete: the harness you built is the thing you carry forward.

## section 1. The rule, stated once

### slide 1.1 The discipline this lesson establishes

- text: the PRD singles L09 out as a *practice to carry forward*. Say the rule out loud and keep it:
- text: **when you build or change an agent, you add or run an eval set.** Not "when you have time" — every time.
- text: the harness you built lives in `fluffy_potato_curriculum.common.evals` (`EvalCase`, the `Scorer` protocol, `evaluate(...)`). It's promoted to `common/` for exactly one reason: so the *next* agent imports it instead of reinventing it.
- diagram: a ratchet wheel labeled "eval set" with a pawl labeled "regression check" — turns forward (new passing cases) but cannot slip back (a regression is caught before shipping).

### slide 1.2 Why a ratchet, not a one-time test

- text: a unit test pins a deterministic output once. An eval set is a *ratchet*: once a case passes, any later change that breaks it is a regression you catch **before** shipping — not one you rediscover in a trace weeks later.
- text: the cost of *not* having it is asymmetric: writing the case is minutes; rediscovering the bug in production is hours plus the damage it did in between.

[↑ Back to top](#l09-lecture-carry-the-eval-set-forward)

## section 2. The very next lessons

### slide 2.1 L11 (workflows) — the cheapest place to start the habit

- text: in the mini cut the next taught lesson is **[L11 (Explicit graphs & workflows / DAGs)](../../../../docs/origin/lesson_roadmaps/L11/objectives.md)**. A deterministic workflow is *trivially* evaluable — fixed path, known outputs — so it's the gentlest possible place to attach an eval set and feel the habit with almost no friction.

### slide 2.2 L12 (shallow agents) — the ratchet's headline demonstration

- text: in **L12** you rebuild the agent as a LangGraph graph. The handoff is the *practice*, not a file: bring the **same `EvalCase`s** you wrote today and run them against the new implementation.
- text: *same cases, different implementation — did anything regress?* That is the cleanest possible demonstration of the ratchet, and it's already wired: L12's lab imports `common/evals.py`.
- diagram: two boxes — "L09 hand-rolled loop" and "L12 LangGraph agent" — both feeding the *same* `evaluate(...)` runner, which emits one pass-rate table per implementation, side by side.

[↑ Back to top](#l09-lecture-carry-the-eval-set-forward)

## section 3. Where this scales (and where it stops)

### slide 3.1 L09 is a first pass, on purpose

- text: a tiny readable harness over the hand-rolled loop is *enough* to establish the habit. Naming the boundary keeps the lesson honest and the scope small.
- table: what L09 deliberately leaves to L23.

| L09 (first pass) | L23 (evaluation revisited) |
| --- | --- |
| one hand-rolled loop | multi-step LangGraph graphs: per-node vs. end-to-end metrics |
| outcome + trajectory checks | retrieval quality for RAG (precision@k / recall@k) |
| one illustrative LLM-judge | LLM-as-judge done properly — what it can and can't reliably score |
| a single agent | multi-agent systems (subagent quality vs. orchestration quality) |
| a handful of cases, K=3–5 | scaling eval cost (sampling strategies, CI gating) |

### slide 3.2 The tooling forward pointer

- text: the same self-hosted **Langfuse** you met in L08 has a *datasets / experiments* feature that stores eval runs and scores — the platform version of the `evaluate()` you hand-built. L09 name-drops it; L23 uses it.
- text: the payoff of building the harness by hand first is the same as L08's: when you open the platform, the dataset items, scores, and experiments are the exact `EvalCase` / `EvalResult` / run structure you already wrote.
- text: closing line: *"you built the minimal version by hand, so the real eval platform is just your harness, hosted — and every agent you build from here comes with an eval set."*

[↑ Back to top](#l09-lecture-carry-the-eval-set-forward)
