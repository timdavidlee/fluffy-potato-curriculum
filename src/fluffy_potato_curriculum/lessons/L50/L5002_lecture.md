# L50 capstone: assembling the mini-project

```yaml
title: "L50 capstone: assembling the mini-project"
keywords: capstone, vertical slice, assembly, reuse, tool design, shallow agent, trace, eval case, regression, receipt reconciliation, hand-off
estimated duration: 15
```

> **Lesson:** L50 — Agent mini-project (mini-track capstone). This deck is the **framing** you read right before the build: what a capstone is, why it's all assembly, and the shape of the slice you're about to build together. The build itself is the guided notebook [L5003_lecture](L5003_lecture.ipynb).
> **Colour key (as in every deck):** **cyan** = the point being made; **coral** = a failure or a cost. Nothing new is taught here — every idea is one you already own.

## section 1. What a capstone actually is

### slide 1.1 A vertical slice, not a product

- text: a capstone is a **vertical slice** — one narrow path that goes *all the way through* the stack, from a fuzzy goal to an evaluated agent.
- text: it is the opposite of a wide feature that touches many things but only reaches halfway. Thin and complete beats wide and half-wired.
- diagram: two builds side by side. Left, **cyan**, a single narrow column labeled "goal → tool → agent → trace → eval" reaching all the way to the bottom (a complete slice). Right, `--ink-faint`, a wide row of five feature boxes that stops halfway down with a **coral** dashed line "never traced, never evaluated". The cyan slice is the point; the wide-but-shallow build is the failure. **This thin-column-vs-wide-row contrast is the deck's opening motif.**

### slide 1.2 Scope creep is *this* lesson's failure mode

- text: the capstone skill isn't building something big — it's **finishing a thin slice, then stopping.**
- text: naming the non-goals out loud *is* the skill. A mini-project is defined as much by what it refuses to do as by what it does.
- diagram: a horizontal **cyan** "done" line with four checked boxes on it — "one task · one new tool · one trace · one eval case". Below it, a `--ink-faint` bin labeled "non-goals → v2 / your own project" holding **coral** cards ("multi-receipt batches", "live bank API", "planning / memory / subagents") pulled *off* the done-line. The restraint is cyan; the parked scope is coral, deliberately set aside.

[↑ Back to top](#l50-capstone-assembling-the-mini-project)

## section 2. Nothing new — it's assembly

### slide 2.1 The five-objective arc, one motion

- text: you built each of these one at a time, on a task the course handed you. Today you drive the whole chain yourself, in order, on a task that's *yours*.
- diagram: a left-to-right **flow** of five **cyan** pills — "scope" → "tool" → "agent" → "trace" → "eval" — each pill tagged underneath with the lesson that owns it (`L08` · `L07/L08` · `L10/L11` · `L12` · `L13`). One continuous arrow runs through all five: the point is the *connection*, not any single pill. No coral — nothing here fails; it connects.

### slide 2.2 Reuse over re-derive

- text: the loop, the tracing, the eval types all already live in the shared `common/` layer. You **import** them — you don't rebuild them.
- text: the *only* genuinely new code in the whole lesson is one small tool. If you're re-implementing an agent loop or a trace emitter, stop and import it.
- diagram: a **block/contrast** picture. Four `--ink-faint` blocks stamped "imported from common/" — `agent_graph.run` · `tracing` · `evals` · `calculator` — flow into a build box. Beside them, a single **cyan** block "find_matching_record — the only new code" flows into the same box, standing out as the one fresh piece. The contrast (dim imports vs one bright new tool) is the whole slide.

[↑ Back to top](#l50-capstone-assembling-the-mini-project)

## section 3. The slice we'll build: receipt reconciliation

### slide 3.1 One expense, three receipt shapes

- text: a receipt arrives in a different shape from every source. Normalizing across those shapes is the real work — and exactly what a model shouldn't do by eyeball.
- table: the same three fields, wearing a different name (or no name) per source.

| Source | vendor field | amount field | shape |
| --- | --- | --- | --- |
| Cafe POS | `merchant` | `total` | JSON object |
| Rideshare | `company` | `amount_charged` | JSON, renamed |
| Hotel folio | first text line | "Amount due:" line | raw text |

### slide 3.2 The one tool, and a real two-tool decision

- text: `find_matching_record` normalizes any format to `(vendor, amount)` and looks it up — a **warranted** tool, because reliable cross-format matching is not eyeball work.
- text: pairing it with the reused `calculator` (total the line items, check the variance) gives the agent a genuine tool-selection decision — which is what makes its trace worth reading.
- diagram: a **flow** — a stack of three differently-shaped receipt chips (cafe/rideshare/folio) funnel into one **cyan** box "find_matching_record: normalize → match", out to a matched ledger record. A second **cyan** box "calculator: sum line items → variance" branches off the same receipt. Both tools cyan (both are the point); the varied inputs `--ink-faint`. This normalize-and-match picture is the section-3 motif.

[↑ Back to top](#l50-capstone-assembling-the-mini-project)

## section 4. Find your *own* failure

### slide 4.1 The malformed receipt

- text: feed it a receipt where OCR gave up — no readable vendor, an unparseable amount. A good agent returns "no confident match" and **stops**; a naive first cut keeps retrying the matcher on the same bad input.
- text: this failure isn't planted by the course. It's on your task, in your trace — and you locate it by *reading the trace*, not by guessing.
- diagram: a trace **waterfall** — a `chain` frame, then the *same* `find_matching_record` span repeating three times (each **coral**, each returning "match: null"), the run ending on a **coral** "max_steps" cap instead of a clean stop. The repetition is the runaway signature; coral is earned here because this is the actual failure. **This waterfall is re-drawn in 4.2.**

### slide 4.2 A failure becomes a kept case

- text: the L13 loop, on your own agent — **trace a failure → write a case that catches it → keep it forever.**
- text: a good scorer *fails when the bug is present and passes when it's fixed*. Read the trajectory: no repeated identical call, and a clean `natural` stop.
- diagram: 4.1's runaway waterfall (**coral**) on the left with one **cyan** scorer box reading its trajectory; an arrow to a small two-row result — "buggy → False" (coral) above "fixed → True" (**cyan**). The scorer is the cyan point; the buggy run stays coral. Second beat of the waterfall motif, now with a verdict attached.

[↑ Back to top](#l50-capstone-assembling-the-mini-project)

## section 5. Done means traced *and* evaluated

### slide 5.1 "It ran once" is not done

- text: one green run of a non-deterministic agent proves little. The habit the whole mini course built — trace before you guess, eval or it's vibes — is what makes a slice *finished*.
- text: the one line to carry out: **the slice is done when it's traced and has one case that would catch its regression.**
- diagram: two agent cards. Left, `--ink-faint` "ran once — no trace, no eval", struck through with a **coral** "vibes" stamp. Right, **cyan** "traced + one kept eval case", badged "finished slice". The contrast is the slide; cyan is the bar you're aiming for.

[↑ Back to top](#l50-capstone-assembling-the-mini-project)

## section 6. This primes your own project

### slide 6.1 A walkthrough now, your build next

- text: today everyone builds the *same* agent, guided. The independent build is the end-of-week project — the same motion, wider and yours.
- text: the seam between them is the **first thing you'd add next** — a second tool (reimbursement detection), a harder receipt format, a tighter scorer.
- diagram: two lanes reconverging on "the shape of an agent". Top lane, solid **cyan**, "L50 walkthrough — everyone builds the same, guided". Bottom lane, **dashed** `--ink-faint`, "end-of-week project — yours, wider", with a small cyan "first thing you'd add" chip bridging the two. Dashed means *next*, not failed — explicitly no coral. The bookend of the deck: the slice you just built is the template for the one you'll build alone.

[↑ Back to top](#l50-capstone-assembling-the-mini-project)
