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
