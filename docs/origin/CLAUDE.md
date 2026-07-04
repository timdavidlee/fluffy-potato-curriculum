# This folder will contain all the original Prompts used to build the curriculum


Everything in this directory should be treated as markdowns used for other ai-agents to read and gain guidance on how to create the curriculum.

- markdowns include enough detail so that an ai-agent could start re-generating the curriculum with minimal questions from the human user

## Doesn't belong here

- Any code

## Whats at the folder base

```
CLAUDE.md # (this file)
CURRICULUM_PRD.md # the primary design file
LECTURES.md # general guidelines for designing lectures
LAB_DESIGN.md # general guidelines for designing labs
PROJECT_BRIEF_DESIGN.md # how to write an end-of-week project brief
```

## LESSON ROADMAPS 

**lesson road map**: are essentially highly condensed summaries of what will be taught. A second process will use this content to generate the LESSON and LABS.

1. Should be monotomically increasing, and earlier number means the lesson chronologically should be taught before larger numbers

```
(repo) ./docs/origin/lesson_roadmaps/L01  # taught first
...
(repo) ./docs/origin/lesson_roadmaps/L10 # taught later
```

**Prework `K<NN>` series (a parallel track before `L01`).** Alongside the `L<NN>`
lessons there is a **prework** track prefixed **`K`** — required, gated setup students
complete *before* the course proper (environment, keys/config, Jupyter, reading
typed/pydantic/async code, and a mandatory Docker stack). It follows the exact same
roadmap → materials conventions as `L<NN>`; the only differences are the prefix and where
it sorts — and how the material *reads*:

- **Format: self-paced step-by-step setup guides, not lecture+lab.** K units are guided
  runbooks a student works through **alone**, following concrete numbered steps with
  **concepts highlighted inline** as each step motivates one (short callouts), plus clear
  verify/pass checkpoints (e.g. K06's `docker compose ps` all-healthy go/no-go). This is a
  deliberate contrast to the `L<NN>` proctor-led `LECTURES.md` + `LAB_DESIGN.md` shape — the
  prework is procedural onboarding done unattended, so it optimizes for "do this → here's
  what just happened / why it matters," not a taught lecture.
- `K` sorts **before** `L` alphabetically, so `K01…K06` precede `L01` with **zero
  renumbering** of the `L<NN>` plan. The same "monotonically increasing, earlier taught
  first" rule holds *within* the `K` series.
- Roadmaps live at `./docs/origin/lesson_roadmaps/K<NN>/`, materials at
  `./src/fluffy_potato_curriculum/lessons/K<NN>/` — same two folders, same file layout as
  an `L<NN>` lesson.
- Track membership and rationale are owned by `tracks.toml` / `SYLLABUS.md` (a `[prework]`
  section) and the design todo `docs/todos/2026-07-03-2211-k-prework-track.md`.

2. Will match to a student facing lesson folder for example

```
(repo) ./src/fluffy_potato_curriculum/lessons/L01  # taught first
...
(repo) ./src/fluffy_potato_curriculum/lessons/L10 # taught later
```

The student facing directories will have **LESSONS** and **LABS**


3. **road map directory** folders should have at minimum have 2- 3 markdown files as the following:

```
# a summary of learning goals objectives, and main points
(repo) .docs/origin/lesson_roadmaps/L01/objectives.md

# any type of teacher lead demonstration of the topic (no student participation)
(repo) .docs/origin/lesson_roadmaps/L01/demos_or_activities.md

# optional - any outside links or videos related to the topic
(repo) .docs/origin/lesson_roadmaps/L01/external_or_additional_resources.md 
```
