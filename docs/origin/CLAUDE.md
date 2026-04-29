# This folder will contain all the original Prompts used to build the curriculum


Everything in this directory should be treated as markdowns used for other ai-agents to read and gain guidance on how to create the curriculum.

- markdowns include enough detail so that an ai-agent could start re-generating the curriculum with minimal questions from the human user

## Doesn't belong here

- Any code

## Whats at the folder base

```
CLAUDE.md # (this file)
CURRICULUM_PRD.md # the primary design file
LAB_DESIGN.md # general guidelines for designing labs

```

## UNITS 

Should be monotomically increasing, and earlier number means the lesson chronologically should be taught before larger numbers

```
(repo) ./docs/origin/lessons/L01  # taught first
...
(repo) ./docs/origin/lessons/L10 # taught later
```

Units should have at minimum have 2- 3 markdown files as the following:

```
# a summary of learning goals objectives, and main points
(repo) .docs/origin/lessons/L01/objectives.md

# any type of teacher lead demonstration of the topic (no student participation)
(repo) .docs/origin/lessons/L01/demos_or_activities.md

# optional - any outside links or videos related to the topic
(repo) .docs/origin/lessons/L01/external_or_additional_resources.md 
```
