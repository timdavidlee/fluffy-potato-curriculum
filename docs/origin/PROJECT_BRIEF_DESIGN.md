# End of Week Project Design Guidelines "How to write a starter brief"

An **end-of-week project** is a larger, integrative build where students
consolidate that week's lessons into an open-ended artifact they can demo and
reason about end-to-end. Projects turn isolated lab exercises into something a
student can show off.

A **project starter brief** in this context is a short prompt / scenario description
given to the students to inform them what they should build

## Purpose

Purpose is to practice using concepts and langgraph frameworks to deliver a small feature.

## Cadence and scope

- **Frequency:** Will be a single-day hackathon-type environment
- **Time-box:** Approximately 12-16 student hours per person will be available
- **Team size:** 2-3 students will work together to design their agent

## What every project must include

The minimum bar every project must meet:

- exercises at least one concept from that week's lessons
- at least a shallow agent implementation
- A runnable artifact (notebook or script) reproducible from a single
  command.
- A short README following the structure below.

## File layout

The evaluation rubric will live here:

- src/fluffy_potato_curriculum/projects/EVALUATION.md

Each project brief (or problem statement) should have the following:

- src/fluffy_potato_curriculum/projects/<brief>/
- src/fluffy_potato_curriculum/projects/<brief>/README.md
- src/fluffy_potato_curriculum/projects/<brief>/starter.py
- src/fluffy_potato_curriculum/projects/<brief>/any-data-set.csv
- src/fluffy_potato_curriculum/projects/<brief>/any-mock-up.html

## Project Starter Brief README structure

Each project ships with a README containing, in order:

1. **Problem statement** — What type of agent should be built by the students? Should be 1-2 sentences
2. **Background** - This is a longer section that elaborates on the pain point, explains the backdrop of why this feature is needed, and anything relevant to the specific industry or general expectations.
3. **Target users** - who will be interacting with this agent
4. **Implementation considerations / edge cases** - what else should the student keep in mind
   when designing their project
5. **Suggested API Contract** - what type of endpoints should be created?
6. **Evaluation** - Link to the shared rubric at `src/fluffy_potato_curriculum/projects/EVALUATION.md` (same across all projects).
7. **Stretch Goals** - similar to "extra credit" only if there's time, the student should be able to extend the project with additional features, or perhaps UI design
8. **Helpful links** - links to lessons in this repo or materials in the general internet

## Evaluation

This is a concise summary of the evaluation that should be formalized for student consumption in `src/fluffy_potato_curriculum/projects/EVALUATION.md` and is listed for reference

- 1st, instructor review against a rubric — list rubric criteria
    - quality of python code
    - product considerations + evaluation
    - presentation

- 2nd, with a peer review favorite vote

## Showcase format

Will be a live demo with slides, approximately 7 minutes long
- students will present the problem
- students will demonstrate the feature
- students will then explain how they made it + lessons learned

## Required Deliverable

- 1st, student's slides
- 2nd, an offline test of the service FastAPI endpoint, script, or Jupyter notebook
- 3rd, a minor "reflections" writeup by the team about what they learned and where they will take the project next

## Project briefs / idea bank

A bank of suggested project themes, mapped to which lessons they exercise.
Students may pick from the bank or propose their own subject to instructor
approval.

Names + one line description (maintained by claude) will be saved in `src/fluffy_potato_curriculum/projects/README.md` and then will have a corresponding folder with a longer description + instructions.


## Project Brief Checklist

Before a project brief is ready to hand to students:

- [ ] Problem statement is concrete and time-boxed.
- [ ] Reproduction commands are tested on a fresh environment.
- [ ] Brief includes a link to `src/fluffy_potato_curriculum/projects/EVALUATION.md`.
- [ ] At least one stretch goal is offered.
- [ ] Helpful links section is populated with relevant lessons and external resources.
