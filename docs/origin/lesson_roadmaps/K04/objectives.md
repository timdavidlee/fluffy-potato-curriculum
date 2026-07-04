# K04 — Python you'll read: types & pydantic

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (prework track `K<NN>`).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).
> Prework series overview: [docs/todos/2026-07-03-2211-k-prework-track.md](../../../todos/2026-07-03-2211-k-prework-track.md).

## Format note

K04 is a **self-paced prework unit**, not a proctor-led lesson — same shape as
[K01](../K01/objectives.md). A student works through it **alone** as a guided runbook:
concrete numbered steps, a short **concept callout** inline the moment a step motivates one,
and clear **verify / pass** checkpoints. The companion [demos_or_activities.md](demos_or_activities.md)
is the student's own walkthrough, not a teacher script.

**One thing is different about K04 specifically.** K01–K03 are *command*-oriented ("run this,
see this"). K04 is **reading**-oriented. The student's job here is to look at a snippet of
typed code and *say what it means with confidence* — because from L01 onward, every file they
open is fully typed and half of what they'll meet is pydantic models. So most steps are
**"read this snippet → what does it say? → check your understanding"**, with a few small
`uv run python -c "..."` snippets to *watch* a type checker complain or a pydantic model reject
bad data. The "Do → You should see → why it matters → If it breaks" spirit still holds; "Do" is
often "read and predict" rather than "type a command."

## Where this unit sits

K04 is the fourth prework unit. By now the student has a working environment (K01), keys wired
through the config seam (K02), and a Jupyter restart-and-run-all workflow (K03). What they do
**not** yet have is fluency reading the *style* of Python this repo is written in.

This repo is **pyright-strict** (see [.claude/rules/python-style.md](../../../../.claude/rules/python-style.md)):
every public function is fully annotated, and structured data travels in **pydantic models**
rather than bare `dict`s. A semi-technical student who "knows basic Python" can still stall on
`def run(messages: list[dict[str, Any]]) -> AIMessage | None:` — not because it's hard, but
because nobody ever showed them how to *read* it left to right. K04 removes that stall so the
lessons that follow read as engineering, not noise.

K04 is a **reading** unit by design. The repo *requires* students to eventually **write**
annotations too (pyright strict fails an untyped `def`), and K04 says so plainly — but the
assessable skill here is **interpreting** typed and pydantic code confidently. Designing your
own models is out of scope; that's what the lessons teach in context.

## Prerequisites

Before starting K04 the student should have completed:

- **K01 — Environment & tooling.** `uv run python ...` works; the `.venv` is active.
- **K02 — Keys & the config seam.** They've seen [`common/config.py`](../../../../src/fluffy_potato_curriculum/common/config.py)
  already — K04 reuses it as its worked pydantic example, so the file is familiar.
- **K03 — Jupyter workflow.** Not strictly required to read code, but the snippets can be run in
  a notebook cell just as well as via `uv run python -c`.

And, from the course's stated baseline ([CURRICULUM_PRD.md § Prerequisites](../../CURRICULUM_PRD.md)):

- **Basic Python** — variables, `def` functions, `import`, calling a library method, and
  reading a `list` / `dict` literal. K04 does a *fast* refresher on these, not a from-zero
  teach. A student who has never written a `def` should do an intro-Python resource first
  (`<need input: do we link a specific external "Python in 90 minutes" resource for students
  who fail the K04 refresher self-check, or is that out of scope for prework?>`).

## Learning objectives

By the end of K04, a student should be able to:

1. **Refresh the three basics the lessons lean on: functions, types, imports.** Concretely:
   - Read a `def name(param): ...` signature and say what goes in and what comes out.
   - Name Python's everyday runtime types (`str`, `int`, `float`, `bool`, `list`, `dict`,
     `None`) and recognize them in a value.
   - Read an `import` line — both `import x` and `from package.module import thing` — and know
     that `from fluffy_potato_curriculum.common.config import get_settings` means "reach into
     *this repo's* `common/config.py` and pull out `get_settings`." This connects the `src/`
     layout from K01 to the import lines they'll see everywhere.
   - This objective is a **fast on-ramp**, not the point of the unit. A student comfortable here
     should move quickly; the self-check gates it.

2. **Read a type hint and say what it promises — left to right.** *(The core objective.)*
   Concretely, interpret each of these confidently:
   - `x: int` / `name: str` — a plain annotation: "this value is expected to be an `int`."
   - `-> None` — "this function returns nothing useful; you call it for its effect." Contrast
     with `-> str` ("hands back a string").
   - `list[int]` / `dict[str, Any]` — a **container spelled out**: a list *of ints*; a dict with
     *string keys and any values*. Read `dict[str, Any]` as "a bag of string-keyed data whose
     value shapes vary" — and know that when the repo uses it, the docstring usually shows a
     concrete example of the shape (per [python-style.md](../../../../.claude/rules/python-style.md)).
   - `X | None` — "an `X`, **or** nothing." Read `str | None = None` as "optionally a string,
     defaulting to absent." This is the single most common hint in the repo (`config.py` alone
     has five of them) so it gets its own beat.
   - A full signature end-to-end, e.g. `def get_settings() -> Settings:` and
     `def require_anthropic_key() -> str:` from the real `config.py`.
   - **These are modern-syntax hints on purpose.** The student will *only* ever see `X | None`,
     `list[int]`, built-in generics — never `Optional[X]` or `typing.List` — because the repo's
     style forbids the old spelling. K04 teaches the spelling they'll actually meet.

3. **Explain what a type hint is *for* — and what it is *not*.** Concretely:
   - A hint is a **promise checked before the code runs** (by pyright, in strict mode), not a
     runtime guardrail. Passing a `str` where an `int` is annotated is a *type error the checker
     flags*, not a crash — Python itself won't stop you at runtime.
   - Because the repo is **pyright-strict**, an unannotated public `def` is a *build failure*, so
     every function the student reads *will* be fully annotated. That's a promise they can rely
     on when reading: the signature is the contract.
   - The student watches this once, live: a two-line `uv run python -c` snippet that pyright
     would reject (see demo 3), so "type error" stops being abstract.

4. **Say what a pydantic model is: a typed, validated data container.** Concretely:
   - Read a `class Foo(BaseModel):` (or `BaseSettings`) block as "a named bag of fields, each
     with a type, that **validates its data when constructed**." It is the repo's answer to
     "don't pass a bare `dict` around" (per [python-style.md § Functions vs. classes](../../../../.claude/rules/python-style.md)).
   - Read the fields of the **real** `Settings` model in
     [`common/config.py`](../../../../src/fluffy_potato_curriculum/common/config.py):
     `anthropic_api_key: str | None = None` etc. — apply objective 2's `X | None` reading to a
     live model, and connect it back to K02 ("*this* is the object your keys load into").
   - Predict what **validation failure** looks like: construct a model with the wrong-typed field
     and watch pydantic raise a `ValidationError` that names the field and the problem. This is
     the "If it breaks" the student will actually hit when a model rejects their data.

5. **Recognize the three places pydantic models show up across the course** — so a model is
   never a surprise later. Concretely, name and *read* one example of each:
   - **Config** — `BaseSettings` (the `Settings` model in `config.py`): fields loaded from the
     environment / `.env`. Already met in K02.
   - **Structured output** — a `BaseModel` the code hands the LLM as the *shape* it must fill in,
     then parses the response back into (the L02 structured-output arc, and tool schemas in L07).
   - **Tool schemas** — a model that describes a tool's arguments so the model can call it (the
     agent lessons). `<need input: name one concrete tool-args model / structured-output model
     from the repo to point at as the canonical read once L07/L11 materials exist — today only
     config.py's Settings exists as a real, generatable example, so K04 leans on it and forward-
     references the other two.>`
   - K04 only teaches **reading** these — "here's what one looks like, here's how to interpret its
     fields." *Designing* a model for a task is taught in the lessons, in context.

## Concepts to highlight inline

Short callouts to drop next to the step that motivates them (the K-series inline style):

- **"The signature is the contract."** In a strict-typed repo, you can trust the annotations —
  reading the `def` line tells you the inputs and output without running anything.
- **"`X | None` means optional."** The most common shape in the codebase; read the `= None`
  default as "absent by default."
- **"`dict[str, Any]` is a loosely-typed bag — look for the docstring example."** When the type
  alone doesn't tell you the shape, the repo convention is a concrete foo-bar example in the
  docstring. Train the student to go look for it.
- **"Types are checked *before* run, not *during*."** pyright is a linter for types; Python
  won't enforce them at runtime. This prevents the classic "but it ran fine?" confusion.
- **"A pydantic model validates on construction."** The moment you build one with bad data, it
  raises — that's the feature, not a bug. It's *why* the repo prefers models over `dict`s.
- **"You'll mostly read models, occasionally write them."** Set the expectation: K04 makes you
  fluent at reading; the lessons ask you to write a few.

## Verify / pass checkpoint

K04 passes when the student can do a short **self-check** — no proctor, self-graded against an
answer key in [demos_or_activities.md](demos_or_activities.md):

1. **Read four signatures.** Given (from the real repo) `def get_settings() -> Settings:`,
   `def require_anthropic_key() -> str:`, `def langfuse_configured() -> bool:`, and a
   constructed `def run(messages: list[dict[str, Any]]) -> str | None:`, the student writes, in
   plain English, what each takes and returns. They must get **`-> None` / `-> bool` / `str |
   None`** right — those are the ones people fumble.
2. **Read the `Settings` model.** Open `config.py`, point at
   `anthropic_api_key: str | None = None`, and answer: what type is this field, is it required,
   and what does it default to? (Answer: `str` or absent; optional; defaults to `None`.)
3. **Predict a validation error.** Before running it, the student predicts what happens when a
   pydantic model with an `int` field is handed the string `"not a number"` — then runs the
   provided `uv run python -c` snippet and confirms a `ValidationError` naming the field.

Passing = 1 and 2 correct from reading alone, and a correct *prediction* on 3 before running it.
The bar is **confident interpretation**, not recall of syntax rules.

`<need input: is the K04 self-check purely honor-system self-graded, or do we want a tiny
auto-checkable script (e.g. a notebook cell that asserts the student's typed answers) the way
K01/K06 might have a machine-checkable pass signal? The reading-heavy nature makes this softer
than K06's "docker compose ps all-healthy".>`

## Bridge to K05

K05 (**async concepts**) is where the reading skill from K04 pays its first dividend. The student
will meet a *new* pair of annotations K04 deliberately left out:

- **`async def` and `await`** — K04 taught "read the `def` line as a contract"; K05 adds the
  `async` keyword and the `-> Awaitable[...]` / coroutine return shape to that reading.
- **`asyncio.gather(...)`** returning a `list[...]` of results — a `list[T]` read (objective 2)
  applied to concurrent calls.

K04 should end by **naming this forward pointer explicitly**: "you can now read a typed
signature; K05 adds one keyword — `async` — and one operator — `await` — to that same reading,
and explains *why* agents want them (concurrent tool calls, parallel eval cases, non-blocking
traces)." That "why async for agents" explainer is **owned by K05** (see
[the prework todo](../../../todos/2026-07-03-2211-k-prework-track.md)); K04 only hands off the
reading skill, it does not pre-teach async.

## Open authoring questions

- `<need input: does the mini track require K04, or is reading-typed-code assumed for mini
  students? The prework todo leaves mini's K-subset open — K04/K05 gate the agent arc, which the
  mini also reaches, so it likely stays required.>`
- `<need input: how deep does the pydantic beat go? Stance taken: read fields + watch one
  ValidationError, and explicitly NOT validators, config, computed fields, or model design.
  Confirm we don't want even a one-line mention of field constraints (e.g. that models can
  enforce ranges), since students will see them in structured-output lessons.>`
- `<need input: the "structured output" and "tool schema" example reads in objective 5 can only
  point at real, generated repo files once L02/L07/L11 materials exist. Until then K04 uses
  config.py's Settings as the sole concrete model and forward-references the other two by
  description. Confirm that forward-reference is acceptable, or hold K04's stage-2 generation
  until at least one structured-output model lands in the repo.>`
- **RESOLVED:** K04 is reading-first, not writing-first — the repo *requires* writing
  annotations, and K04 says so, but the assessed skill is interpretation. (Per the prework todo's
  framing.)
- **RESOLVED:** K04 teaches only modern hint syntax (`X | None`, `list[int]`, built-in generics)
  — never `Optional`/`typing.List` — matching the repo's enforced style so students learn the
  spelling they'll actually meet.
