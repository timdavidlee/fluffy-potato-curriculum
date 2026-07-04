# K04 — Walkthrough: Python you'll read (types & pydantic)

> Sibling doc: [objectives.md](objectives.md) (what this unit aims for), parent design
> [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md).
>
> **Audience for this file:** the **student**, working alone. Unlike an `L<NN>` demos file (a
> teacher script), this is your own runbook — you read each step, do the small thing it asks,
> and check your understanding against what's written. Nobody is driving but you.

## How to read this file

Every step is a small block shaped like the rest of the prework:

- **Do** — the one action. Often that's *read this snippet and predict*, sometimes it's *run this
  `uv run python -c "..."`*. K04 is reading-heavy on purpose (see
  [objectives.md § Format note](objectives.md)).
- **You should see / say** — what a correct reading or a correct run looks like.
- **Why it matters** — the one-sentence payoff. From L01 on, every file is typed; this is the
  reading skill that makes them legible.
- **If it breaks** — the likely stumble and the fix.

Work top to bottom. Steps build: the type-hint reading in Part 2 is what makes the pydantic model
in Part 4 readable. Everything runs against **this repo's** `.venv` — make sure `uv run python
-c "print('ok')"` prints `ok` before you start (that's your K01 check).

Concept callouts look like this:

> **Concept — the signature is the contract.** In a pyright-strict repo, the `def` line alone
> tells you the inputs and the output. You can trust it without running the code.

---

## Part 1 — Fast refresher: functions, types, imports

This part is a **warm-up**. If it's all obvious, skim it and jump to Part 2 — the self-check at
the end is what decides whether you were right to skim.

### Step 1.1 — Read a function signature

**Do.** Read this and say, out loud or on paper: what goes *in*, what comes *out*?

```python
def greet(name: str) -> str:
    return f"Hello, {name}"
```

**You should say.** "Takes one thing, `name`, expected to be a string; hands back a string."

**Why it matters.** Every function in this repo is written exactly like this — a typed input
list and a typed output. Reading the first line is reading the whole contract.

**If it breaks.** If `-> str` is unfamiliar, read it as an arrow: *"... gives back a `str`."*
That arrow shows up on every function; get comfortable with it here.

### Step 1.2 — Name the everyday types

**Do.** Match each value to its type: `"hi"`, `42`, `3.14`, `True`, `[1, 2, 3]`,
`{"a": 1}`, `None`.

**You should say.** `str`, `int`, `float`, `bool`, `list`, `dict`, `None` (the special
"nothing" value). These seven are ~all you'll meet as *runtime* values.

**Why it matters.** Type hints (Part 2) are built out of exactly these names plus a couple of
combining symbols. Know the atoms first.

### Step 1.3 — Read an import line (and connect it to the repo)

**Do.** Read this line from the repo and say where `get_settings` *comes from*:

```python
from fluffy_potato_curriculum.common.config import get_settings
```

**You should say.** "Reach into this repo's `src/fluffy_potato_curriculum/common/config.py` and
pull out the `get_settings` function." The dotted path *is* the folder path under `src/`.

> **Concept — imports are just paths.** `from a.b.c import thing` walks folders `a/ → b/ → c.py`
> and grabs `thing`. This is the `src/` layout from K01 showing up in code.

**Why it matters.** You'll see dozens of these `from fluffy_potato_curriculum...import` lines.
They're not magic — they're a map to a file you can open.

**If it breaks.** Actually open `src/fluffy_potato_curriculum/common/config.py` and find
`def get_settings`. Seeing the import resolve to a real file once makes the rest obvious.

---

## Part 2 — Reading type hints (the core of K04)

This is the part that matters. Goal: look at any annotation in the repo and say what it promises,
left to right, without hesitation.

### Step 2.1 — Plain annotations and the return arrow

**Do.** Read each; say the type:

```python
count: int
label: str
def save(data: str) -> None: ...
def load() -> str: ...
```

**You should say.** `count` is an int; `label` is a string; `save` takes a string and **returns
nothing useful** (`-> None` — you call it for its *effect*); `load` takes nothing and hands back
a string.

> **Concept — `-> None` means "no useful return."** The function does something (writes a file,
> prints, mutates) and hands you back nothing to use. Very common. Don't read it as "broken."

**Why it matters.** `-> None` trips people up more than any other hint. Nail it now.

### Step 2.2 — Containers spelled out: `list[int]`, `dict[str, Any]`

**Do.** Read these two:

```python
scores: list[int]
payload: dict[str, Any]
```

**You should say.** `scores` is a **list of ints**; `payload` is a **dict with string keys and
values of any type** — a loosely-typed bag.

> **Concept — `dict[str, Any]` is a bag; look for the docstring example.** When the type alone
> won't tell you the shape, this repo's convention (see
> [.claude/rules/python-style.md](../../../../.claude/rules/python-style.md)) is a concrete
> foo-bar example in the function's docstring, e.g. `[{"type": "click", "x": 10}]`. When you
> hit a `dict[str, Any]`, go read the docstring for the shape.

**Why it matters.** Agent code passes around `list[dict[str, Any]]` message lists constantly.
Reading "list of string-keyed bags" fluently is half of reading L10+.

### Step 2.3 — The most common hint: `X | None`

**Do.** Read these three, paying attention to the `= None`:

```python
nickname: str | None = None
retries: int | None
def find(key: str) -> str | None: ...
```

**You should say.** `nickname` is "a string **or** nothing, absent by default"; `retries` is "an
int or nothing"; `find` takes a string and returns "a string **or** `None`" (so the caller must
handle the "not found" case).

> **Concept — `X | None` means optional; `= None` means "absent by default."** This is *the*
> most common shape in the codebase. `config.py` alone has five of them.

**Why it matters.** Half the fields and half the return types you'll read are `X | None`. If you
read it as "optional, might be missing," you'll never be surprised by a `None`.

**If it breaks.** If the `|` looks strange: it reads as "or." `str | None` = "str or None." This
repo *only* uses this modern spelling — you will never see `Optional[str]` here, so don't go
learn that older form.

### Step 2.4 — Read four real signatures from `config.py`

**Do.** Open [`src/fluffy_potato_curriculum/common/config.py`](../../../../src/fluffy_potato_curriculum/common/config.py)
and read these four *real* signatures. Say what each takes and returns:

```python
def get_settings() -> Settings: ...
def langfuse_configured() -> bool: ...
def require_anthropic_key() -> str: ...
def require_openai_key() -> str: ...
```

**You should say.** `get_settings` takes nothing, returns a `Settings` object; `langfuse_configured`
takes nothing, returns a `bool` (True/False); the two `require_*` functions take nothing and
return a `str` (the key) — and, reading the bodies, *raise* if the key is missing.

**Why it matters.** This is a real file you already met in K02. You're now reading production
repo code, not toy snippets. That's the whole skill.

---

## Part 3 — What a type hint is *for* (and isn't)

### Step 3.1 — Types are a promise checked *before* the code runs

**Do.** Read this and predict: does Python *crash* at runtime when you pass a string?

```python
def double(n: int) -> int:
    return n * 2

double("oops")   # what happens?
```

**You should say.** Python does **not** crash — `"oops" * 2` is `"oopsoops"`, a perfectly legal
string. The *type checker* (pyright) would flag `double("oops")` as an error **before** you run,
but Python itself doesn't enforce the hint at runtime.

> **Concept — types are checked before run, not during.** pyright reads your code and complains
> about mismatches; the running program doesn't. Hints are a *contract for the reader and the
> checker*, not a runtime guardrail. (For real validation-at-runtime, that's pydantic — Part 4.)

**Why it matters.** This kills the "but it ran fine, so the types must be right?" confusion. Ran
fine ≠ type-correct.

### Step 3.2 — Watch it run (optional, 10 seconds)

**Do.** Run this to *see* the string case not crash:

```sh
uv run python -c "def double(n: int) -> int: return n * 2
print(double('oops'))"
```

**You should see.** `oopsoops` printed — no error. Runtime ignored the `int` hint.

**Why it matters.** Seeing it once beats being told. The hint was advisory at runtime.

> **Concept — the repo is pyright-strict, so every public `def` is fully annotated.** That's a
> *guarantee for you as a reader*: an untyped function fails the build, so the signature you're
> reading is always complete. The contract is always there to read. (See
> [.claude/rules/python-style.md](../../../../.claude/rules/python-style.md).)

---

## Part 4 — What a pydantic model is

A pydantic model is a **typed, validated data container** — a named bag of typed fields that
**checks its data the moment you build it**. This repo prefers models over passing bare `dict`s
around (see [python-style.md § Functions vs. classes](../../../../.claude/rules/python-style.md)).

### Step 4.1 — Read the real `Settings` model

**Do.** Open [`common/config.py`](../../../../src/fluffy_potato_curriculum/common/config.py) and
read the `Settings` class fields:

```python
class Settings(BaseSettings):
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_host: str | None = None
```

**You should say.** "A named container with five fields; each is a `str | None` defaulting to
`None` — so each is **optional**, absent by default." Apply your Step 2.3 reading directly.

> **Concept — `BaseSettings` loads fields from the environment / `.env`.** This is the K02 config
> seam. *This class* is the object your `ANTHROPIC_API_KEY` loads into: env var → validated field.

**Why it matters.** You met this file in K02 as "where keys live." Now you can read it as *code*:
it's a pydantic model, and its fields are `X | None` optionals.

### Step 4.2 — A model validates on construction

**Do.** Read this tiny model and predict: which of the two constructions is fine, and which
raises?

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    quantity: int

Item(name="widget", quantity=5)          # (a)
Item(name="widget", quantity="not a number")  # (b)
```

**You should say.** (a) is fine. (b) **raises a `ValidationError`** — pydantic tries to coerce
`"not a number"` into an `int`, can't, and rejects it, naming the field `quantity`.

> **Concept — a pydantic model validates when constructed.** Bad data doesn't slip through to be
> discovered later; the model refuses to build. That refusal is the feature — it's *why* the repo
> passes models instead of `dict`s.

### Step 4.3 — Watch the ValidationError (run this)

**Do.** Run it and read the error:

```sh
uv run python -c "
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    quantity: int

Item(name='widget', quantity='not a number')
"
```

**You should see.** A `pydantic_core.ValidationError` (traceback) whose body names the offending
field and reason — roughly:

```
1 validation error for Item
quantity
  Input should be a valid integer, unable to parse string as an integer ...
```

**Why it matters.** This *is* the "If it breaks" you'll meet in the lessons when a model rejects
your data. Now you recognize it on sight: it tells you the field and the problem.

**If it breaks.** If you get `ModuleNotFoundError: pydantic`, you're not in the repo `.venv` —
re-run with `uv run` from the repo root (K01). pydantic is already a dependency; you don't
install anything.

> **Concept — `str | None = None` vs. `quantity: int`.** A field with a default is optional; a
> field without one (`name`, `quantity`) is **required** — leave it out and you get the same
> `ValidationError`. Reading defaults tells you what's required.

---

## Part 5 — The three places you'll meet pydantic models

You don't need to build these — just recognize each when a lesson shows it.

**Do.** Read the three roles below and note which one you've already seen.

1. **Config — `BaseSettings`.** The `Settings` model in `config.py` (Step 4.1). Fields load from
   the environment / `.env`. **You've already met this** (K02).
2. **Structured output.** A `BaseModel` the code hands the LLM as the *shape it must fill in*,
   then parses the model's reply back into. You'll meet this in the prompting/output lessons
   (L02) and again as tool schemas (L07). *`<need input: point at the real structured-output
   model here once L02 materials generate it; today only config.py exists as a concrete
   example.>`*
3. **Tool schemas.** A model describing a tool's arguments so the LLM can call the tool with the
   right fields — the agent lessons (L11+). *`<need input: point at the real tool-args model once
   L07/L11 materials exist.>`*

> **Concept — same object, three jobs.** Config, output shape, tool args — all the *same* idea:
> a typed bag that validates itself. Learn to read one and you can read all three.

**Why it matters.** When a lesson drops a `class Foo(BaseModel):` on you, you won't ask "what is
this?" — you'll read its fields and move on.

---

## Pass checkpoint — self-check

Self-graded. Answer from **reading**, then check against the key below. You pass when 1 and 2 are
correct from the code alone, and you *predicted* 3 correctly **before** running it.

**Q1 — Read four signatures.** In plain English, what does each take and return?

```python
def get_settings() -> Settings: ...
def require_anthropic_key() -> str: ...
def langfuse_configured() -> bool: ...
def run(messages: list[dict[str, Any]]) -> str | None: ...
```

**Q2 — Read a model field.** In `config.py`, for `anthropic_api_key: str | None = None`: what
type is it, is it required, and what's the default?

**Q3 — Predict a validation error.** Before running Step 4.3's snippet, what happens when
`Item(quantity=...)` gets `"not a number"` for an `int` field?

<details>
<summary><b>Answer key</b> (don't peek until you've answered)</summary>

- **Q1.** `get_settings` — takes nothing, returns a `Settings` object. `require_anthropic_key` —
  takes nothing, returns a `str` (the key), and raises if it's missing. `langfuse_configured` —
  takes nothing, returns a `bool`. `run` — takes `messages`, a **list of string-keyed dicts**,
  and returns **either a `str` or `None`** (so the caller must handle the `None`). Getting
  `-> None` (there is none here — don't invent one), `-> bool`, and `str | None` right is the bar.
- **Q2.** Type `str` (or absent); **not required** — it's `str | None` with a default; defaults to
  `None`. So the object always builds even with no key set (that's why `config.py` has the
  `require_*` helpers — they turn "absent" into a clear error at the point of use).
- **Q3.** It raises a `ValidationError` naming the `quantity` field — pydantic can't parse
  `"not a number"` as an int, so it refuses to construct the model.

</details>

If any answer surprised you, re-read the Part it came from (Q1 → Part 2; Q2 → Part 4.1; Q3 →
Part 4.2/4.3) before moving on. Confident interpretation is the bar — not memorized rules.

---

## Bridge to K05

You can now read a typed signature as a contract and a pydantic model as a self-validating bag.
**K05 (async concepts)** adds exactly two new things to that same reading:

- one keyword — **`async`** in front of `def`,
- one operator — **`await`** in front of a call,

plus the reason agents want them: concurrent tool calls, parallel eval cases, and non-blocking
traces/streaming. That "**why async for agents**" explainer is K05's to give (see
[the prework todo](../../../todos/2026-07-03-2211-k-prework-track.md)) — K04 just hands you the
reading skill it builds on. Go straight to K05.

## Open authoring questions

- `<need input: should Part 3.2 and Part 4.3 run as `uv run python -c` snippets, or as cells in a
  K04 notebook (since K03 just taught the notebook workflow)? Both work; a notebook keeps the
  "restart-and-run-all" muscle warm, a -c one-liner is lower-friction. Stance: offer the -c form
  inline and note the cell equivalent.>`
- `<need input: do we want a machine-checkable pass signal for the self-check (e.g. a cell that
  asserts the student's typed answers), or is honor-system self-grading acceptable for a
  reading-heavy unit? K06 has a hard "docker compose ps healthy" gate; K04's is softer.>`
- `<need input: the structured-output and tool-schema example reads in Part 5 forward-reference
  L02/L07/L11 files that don't exist yet. Confirm K04 ships leaning on config.py as the sole
  concrete model with the other two described, or hold stage-2 generation until one real
  structured-output model lands.>`
- **RESOLVED:** modern hint syntax only (`X | None`, `list[int]`) — no `Optional`/`typing.List`,
  matching the repo's enforced style.
- **RESOLVED:** pydantic depth is capped at "read fields + watch one `ValidationError`" — no
  validators, config, or model design (that's taught in the lessons, in context).
