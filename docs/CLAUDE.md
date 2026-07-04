# docs/

Prose that supports the curriculum: **design source, tracking notes, and work handoffs.**
Markdown only — no code lives here (code goes under `src/`). Each subfolder has a distinct job;
pick the right one so docs stay findable.

## Which folder for what

| Folder | What it holds | Reach for it when… |
| --- | --- | --- |
| [`origin/`](origin/CLAUDE.md) | The **design source of truth** — `CURRICULUM_PRD.md`, `LECTURES.md`, `LAB_DESIGN.md`, `PROJECT_BRIEF_DESIGN.md`, and `lesson_roadmaps/L<NN>/` (stage-1 roadmaps that stage-2 generates materials from). | You are **deciding what a lesson teaches** or changing course-wide conventions. This is authored *before* materials and drives generation. Has its own deeper map — read [origin/CLAUDE.md](origin/CLAUDE.md). |
| [`todos/`](todos/) | **Dated, point-in-time tracking notes** (`YYYY-MM-DD-HHMM-<slug>.md`) — short lists of open items for one effort. | You want to **capture open items / follow-ups** discovered during a work session. Cheap and disposable. |
| [`handoffs/`](handoffs/) | **Dated, self-contained resumable specs** (`YYYY-MM-DD-<slug>.md`) — enough context for a *different* session or engineer to pick up in-flight work cold. | You are **handing off multi-session work** and a reader needs the goal, what's done (with the landing PR), the exact patterns to apply, the remaining checklist, and how to verify. |
| *(root, loose `*.md`)* | **Standalone reference docs** that aren't design-source or tracking — e.g. `classroom-llm-management.md` (cohort infra/ops), `preview_2day_crash_course.md` (a draft alt-track sketch). | You have a **durable reference doc** that doesn't belong to a lesson and isn't a to-do. Keep these few; prefer a subfolder if one fits. |

## todos vs. handoffs (the easy confusion)

- **todo** = a *checklist for me/us right now*. Terse, may go stale, safe to delete. Dated notes are
  **historical snapshots** — don't rewrite an old dated todo as if it were current.
- **handoff** = a *spec for whoever picks this up next*. Self-contained and authoritative: states the
  decision, the done-vs-remaining split, before→after examples, and a verification checklist. When
  its work is fully done, add `**Status: DONE**` at the top or delete it.

A big effort often has **both**: a lightweight `todos/` note while it's active, and a `handoffs/`
doc once it needs to survive a context boundary.

## Conventions

- **Naming:** dated files use `YYYY-MM-DD-<kebab-slug>.md`. Because several `todos/` notes can be
  written in a single day, prefix them with a 24-hour time as well: `YYYY-MM-DD-HHMM-<kebab-slug>.md`
  (e.g. `2026-07-03-1430-langchain-notebook-migration.md`). Get the time from `date +%Y-%m-%d-%H%M`
  rather than guessing. `handoffs/` (rarely more than one a day) keep the date-only form.
- **Draft marker:** a doc whose first line is an HTML-comment draft marker
  (`<!-- llm-status: draft ... -->`, or a bold `> **Status: draft / WIP**`) is **not** a source of
  truth — don't pull conventions from it or treat its claims as current.
- **Cross-reference, don't duplicate:** link to `origin/` design docs and to the landing PR rather
  than restating them; a handoff points *at* the authoritative code/docs, it doesn't fork them.
- This is navigation/organization guidance. Enforced **code** conventions (style, tests, notebooks)
  live in [`.claude/rules/`](../.claude/rules/), not here.
