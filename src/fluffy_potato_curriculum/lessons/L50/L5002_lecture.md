# L50: the receipt-reconciliation problem

```yaml
title: "L50: the receipt-reconciliation problem"
keywords: receipt reconciliation, cross-format normalization, tool-vs-model, warranted tool, three-tool decision, expense policy, graceful failure, no confident match, runaway loop, regression case, scorer, vertical slice
estimated duration: 15
```

> **Lesson:** L50 — Agent mini-project (mini-track capstone). This deck sets up the **problem you're about to build against**: what reconciliation is, why it's genuinely hard, and how to *reason* about the tool, the failure, and what "done" means — so the guided build [L5003_lecture](L5003_lecture.ipynb) is you executing a plan you already understand, not following steps blind.
> **Colour key (as in every deck):** **cyan** = the point being made; **coral** = a failure or a cost. Nothing here is a new *concept* — it's a new *problem* to point your existing skills at.

## section 1. The problem: does this receipt match the ledger?

### slide 1.1 Reconciliation, stated plainly

- text: you have **one receipt** and a small **ledger** of expense records the company already booked. The question the agent answers: *which ledger record is this receipt, and do the amounts agree?* — and, when nothing lines up, say so instead of guessing.
- text: that's the whole task. It sounds like a lookup, and the *matching* part is — the hard part is that the receipt almost never arrives in the ledger's shape.
- diagram: a **flow** — one **cyan** receipt chip on the left, an arrow into a box "match → same record? amounts agree?", out to one of two ends: a **cyan** "matched, reconciled" record and a **coral** "no confident match". Both ends are legitimate outcomes; the coral one is a *correct* answer, not a failure. The two-outcome shape is the section-1 motif.

### slide 1.2 Why it's hard: one expense, three receipt shapes

- text: the same three facts — **who**, **how much**, **what shape** — wear a different name (or no name) in every source. A human reads across them by eyeball; that's exactly the reading you don't want a *model* doing by eyeball on money.
- text: normalizing those varied shapes into one comparable `(vendor, amount)` is the real work of the task. Hold onto that — it's what decides where the tool goes in section 2.
- table: the same three fields, disguised per source.

| Source | vendor lives in | amount lives in | shape |
| --- | --- | --- | --- |
| Cafe POS | `merchant` | `total` | JSON object |
| Rideshare | `company` | `amount_charged` | JSON, renamed fields |
| Hotel folio | first text line | the "Amount due:" line | raw text, no fields |

[↑ Back to top](#l50-the-receipt-reconciliation-problem)

## section 2. How to think about the tools

### slide 2.1 Where does the tool go? Apply the L08 test

- text: ask the L08 question out loud — *could the model do this reliably in its head?* For "normalize a hotel folio's raw text and match it to a ledger row," the honest answer is **no**: it's fiddly, deterministic, and a wrong guess is a wrong reimbursement. That "no" is what **warrants** the tool.
- text: so the split is deliberate: the **tool** does the brittle normalize-and-match; the **model** does the judgement around it — deciding *when* to match, *when* to total, and *when* to declare no match. Draw that line yourself before you write a line of code.
- diagram: a **contrast** picture. On the model's side, a **cyan** brain labeled "decides: match? total? give up?" — judgement. On the tool's side, a **cyan** gear labeled "normalize any shape → `(vendor, amount)` → look up" — mechanism. A `--ink-faint` dashed seam between them labeled "the L08 line, drawn on *this* task". The point is the line, not either box alone.

### slide 2.2 More tools make it a real decision

- text: give the agent three tools — `find_matching_record`, the reused **`calculator`** (total the line items, check the variance), and a pre-built **`check_expense_policy`** (is the amount under its category cap?). Now it must **choose** which to reach for, and when.
- text: that choice is the point. A one-tool agent has no decision to observe; a multi-tool agent leaves a **trajectory** — and a trajectory is the only thing worth tracing and, later, worth evaluating.
- text: `find_matching_record` is the only tool you *write*; `calculator` and `check_expense_policy` are provided/reused. The authoring budget stays at one — the agent's toolset does not.
- diagram: a **flow** — a receipt funnels into a junction ("agent picks") that branches to three **cyan** boxes: "`find_matching_record`: normalize → match", "`calculator`: sum line items → variance", and "`check_expense_policy`: amount → within cap?". Arrows from all three converge on "reconciled?". All tools cyan (all legitimate); the branch the agent takes is the emphasis — it's exactly what the trace records.

[↑ Back to top](#l50-the-receipt-reconciliation-problem)

## section 3. How to think about failure

### slide 3.1 The receipt you can't place

- text: now feed it the hard case: a receipt where OCR gave up — no readable vendor, an unparseable amount. Reason about what *good* looks like **before** you run it: a good agent returns **"no confident match" and stops.** Refusing to match is the right answer here.
- text: the **coral** version is the naive first cut — it re-calls the matcher on the same unreadable input, again and again, and runs to the step cap. Same bad input, same null result, burning tokens. That's the failure this task hands you for free — no course-planted bug.
- diagram: a trace **waterfall** — a `chain` frame, then the *same* `find_matching_record` span repeating three times (each **coral**, each returning "match: null"), the run ending on a **coral** "max_steps" cap instead of a clean stop. The repeated identical span is the runaway *signature* you learn to spot; coral is earned because this is the real failure. **This waterfall reappears in 3.2.**

### slide 3.2 What a failure has to become: a kept case

- text: finding the failure isn't the finish line — **catching it forever** is. Turn the trace into one `EvalCase` plus a `Scorer`, and reason about what that scorer must do: **fail when the bug is present, pass once it's fixed.** A scorer that passes on the broken run catches nothing.
- text: read the *trajectory*, not just the answer — "no repeated identical matcher call" and "terminated `natural`, not `max_steps`". That's the L13 loop pointed at your own agent: **trace a failure → write a case that catches it → keep it.**
- diagram: 3.1's runaway waterfall (**coral**) on the left, one **cyan** scorer box reading its trajectory, an arrow to a two-row verdict — "buggy run → False" (**coral**) above "fixed run → True" (**cyan**). The scorer is the cyan point; the buggy run stays coral. Second beat of the waterfall motif, now with a verdict attached.

[↑ Back to top](#l50-the-receipt-reconciliation-problem)

## section 4. How to know you're done

### slide 4.1 "It ran once" is not done

- text: the agent is non-deterministic — one green run proves almost nothing. So the bar for *this* build isn't "it produced an answer." Reason about doneness the way the whole mini course taught you: **trace before you guess, eval or it's vibes.**
- text: the one sentence to carry into the build: **the slice is done when it's traced *and* has one case that would catch its regression.** That's the target you're aiming the next 70 minutes at.
- diagram: two agent cards. Left, `--ink-faint` "ran once — no trace, no eval", struck through with a **coral** "vibes" stamp. Right, **cyan** "traced + one kept eval case", badged "done". The contrast is the slide; cyan is the bar.

[↑ Back to top](#l50-the-receipt-reconciliation-problem)

## section 5. You already own every piece

### slide 5.1 One new tool; the rest is assembly

- text: none of this is new machinery. The loop, the tracing, the eval types all live in `common/` — you **import** them. The *only* genuinely new code is one small tool, `find_matching_record`. If you catch yourself re-implementing an agent loop or a trace emitter, stop and import it.
- text: so the skill on display today isn't building something big — it's pointing skills you already have at a problem you now understand, building the **thinnest slice that goes all the way through**, and then *stopping*. The "first thing you'd add next" (a harder format, a tighter scorer, reimbursement detection) is the seam into your own [end-of-week project](../../../../docs/origin/PROJECT_BRIEF_DESIGN.md).
- diagram: a **block/contrast** picture. Four `--ink-faint` blocks stamped "imported from `common/`" — `create_agent` · `tracing` · `evals` · `calculator` — flow into a build box. Beside them a single **cyan** block "`find_matching_record` — the only new code" flows into the same box, the one bright piece among the dim ones. The contrast *is* the slide: dim imports, one fresh tool.

[↑ Back to top](#l50-the-receipt-reconciliation-problem)
