<!--
  PR template for AI-assisted changes.
  Fill the "Required" section fully. The rest are prompts — delete what
  doesn't apply, but prefer over-explaining the *why*: this text is the
  primary context a future human or agent will have when revisiting this PR.
-->

## Summary

<!-- One or two sentences: what this PR does and why it exists. -->

## Motivation / Context

<!-- The problem being solved. Link the issue/ticket. What was the state
     before, and why is that a problem worth changing? -->

Closes #
Context:

## AI generation details (Required)

- **Tool / model:** <!-- e.g. Claude Code (Opus 4.8), Cursor, Copilot, hand-written -->
- **AI vs. human split:** <!-- e.g. "~80% AI-generated, auth logic hand-written" -->
- **Prompting approach:** <!-- Brief: what were you asking it to do? Was it working
  from full repo context, a spec, or partial context? -->
- **Human review level:** <!-- Pick honestly — reviewers calibrate off this -->
  - [ ] Read every line and understand it
  - [ ] Read the important paths; skimmed boilerplate
  - [ ] Ran it / tests pass, but did not read line-by-line
  - [ ] Prototype — not yet carefully reviewed

## Flags for reviewers

<!-- Where should a reviewer look hardest? Call out anything AI is prone to
     getting subtly wrong. -->

- **New dependencies added:** <!-- list them, or "none" — verify these exist & are maintained -->
- **New/changed external API or library usage:** <!-- verify signatures aren't hallucinated -->
- **Areas of low confidence:** <!-- edge cases, concurrency, error handling, etc. -->

## What changed

<!-- Bulleted, human-readable. Group by concern, not by file. -->

-

## Decisions & tradeoffs

<!-- The part that saves the next person hours. -->

- **Approach chosen:**
- **Alternatives considered / rejected (and why):**
- **Anything the AI got wrong initially that shaped the final design:**
- **Assumptions made:** <!-- things that are true today but could change -->

## Testing & verification

- **How this was verified:** <!-- tests added, manual steps, screenshots, etc. -->
- **What is NOT covered:**
- [ ] Automated tests added/updated
- [ ] Manually verified
- [ ] Covered by existing tests

## Risk & blast radius

- **What breaks if this is wrong:** <!-- user-facing? data? internal only? -->
- **Rollback plan:** <!-- revert-safe? migration involved? -->
- **Reviewer effort suggested:** <!-- e.g. "quick" / "careful" / "needs domain expert" -->

## Known limitations / follow-ups

<!-- Explicitly list what was deliberately left out and why. Prevents future
     readers from assuming an omission was an oversight. -->

-

## For future readers

<!-- Optional but valuable. One short paragraph in plain language: if someone
     (or an agent) lands here in 6 months debugging related code, what's the
     one thing they need to know that isn't obvious from the diff? -->
