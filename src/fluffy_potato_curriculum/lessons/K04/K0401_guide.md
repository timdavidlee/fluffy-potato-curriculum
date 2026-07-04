# K04 — Python you'll read: types & pydantic

This is a self-paced prework unit. You work through it **alone** as a runbook — read each
step, do the small thing it asks, and check your understanding against what's written.

Unlike K01–K03, K04 is **reading**-oriented. From L01 onward every file you open is fully
typed, and half of what you'll meet is pydantic models. Your job here is to look at a snippet
of typed code and *say what it means with confidence*. Most steps are **"read this snippet →
what does it say? → check,"** with a few small `uv run python -c` snippets to *watch* a
pydantic model reject bad data.

## How to read this file

Each step has:

- **Do** — the one action. Usually *read this snippet and predict*; sometimes *run this
  `uv run python -c "..."`*.
- **You should say / see** — what a correct reading or run looks like.
- **Why it matters** — the one-sentence payoff.

Work top to bottom; steps build. Everything runs against **this repo's** `.venv` — make sure
`uv run python -c "print('ok')"` prints `ok` before you start (that's your K01 check).

> **Concept — the signature is the contract.** In a pyright-strict repo, the `def` line alone
> tells you the inputs and the output. You can trust it without running the code.

---

## 1. Fast refresher: functions, types, imports

A **warm-up**. If it's all obvious, skim it — the self-check at the end decides whether you
were right to skim.

### 1.1 Read a function signature

**Do.** Read this and say: what goes *in*, what comes *out*?

```python
def greet(name: str) -> str:
    return f"Hello, {name}"
```

**You should say.** "Takes one thing, `name`, a string; hands back a string." That arrow
`->` reads as *"gives back a…"* and shows up on every function in this repo.

### 1.2 Name the everyday types

**Do.** Match each value to its type: `"hi"`, `42`, `3.14`, `True`, `[1, 2, 3]`, `{"a": 1}`,
`None`.

**You should say.** `str`, `int`, `float`, `bool`, `list`, `dict`, `None` (the special
"nothing" value). These seven are ~all you'll meet as *runtime* values, and type hints are
built out of exactly these names plus a couple of combining symbols.

### 1.3 Read an import line

**Do.** Read this line from the repo and say where `get_settings` *comes from*:

```python
from fluffy_potato_curriculum.common.config import get_settings
```

**You should say.** "Reach into this repo's `src/fluffy_potato_curriculum/common/config.py`
and pull out `get_settings`." The dotted path *is* the folder path under `src/`.

> **Concept — imports are just paths.** `from a.b.c import thing` walks folders
> `a/ → b/ → c.py` and grabs `thing`. This is the `src/` layout from K01 showing up in code.

**If it breaks.** Open `src/fluffy_potato_curriculum/common/config.py` and find
`def get_settings`. Seeing one import resolve to a real file makes the rest obvious.

---

## 2. Reading type hints (the core of K04)

Goal: look at any annotation in the repo and say what it promises, left to right, without
hesitation.

### 2.1 Plain annotations and the return arrow

**Do.** Read each; say the type:

```python
count: int
label: str
def save(data: str) -> None: ...
def load() -> str: ...
```

**You should say.** `count` is an int; `label` a string; `save` takes a string and **returns
nothing useful** (`-> None` — you call it for its *effect*); `load` takes nothing and hands
back a string.

> **Concept — `-> None` means "no useful return."** The function does something (writes a
> file, prints, mutates) and hands you back nothing to use. Common — don't read it as "broken."

### 2.2 Containers spelled out: `list[int]`, `dict[str, Any]`

**Do.** Read these two:

```python
scores: list[int]
payload: dict[str, Any]
```

**You should say.** `scores` is a **list of ints**; `payload` is a **dict with string keys and
values of any type** — a loosely-typed bag.

> **Concept — `dict[str, Any]` is a bag; look for the docstring example.** When the type alone
> won't tell you the shape, this repo's convention is a concrete foo-bar example in the
> function's docstring, e.g. `[{"type": "click", "x": 10}]`. When you hit a `dict[str, Any]`,
> go read the docstring for the shape.

**Why it matters.** Agent code passes around `list[dict[str, Any]]` message lists constantly.
Reading "list of string-keyed bags" fluently is half of reading L10+.

### 2.3 The most common hint: `X | None`

**Do.** Read these three, paying attention to the `= None`:

```python
nickname: str | None = None
retries: int | None
def find(key: str) -> str | None: ...
```

**You should say.** `nickname` is "a string **or** nothing, absent by default"; `retries` is
"an int or nothing"; `find` returns "a string **or** `None`" (so the caller must handle the
"not found" case).

> **Concept — `X | None` means optional; `= None` means "absent by default."** This is *the*
> most common shape in the codebase — `config.py` alone has five of them.

**If it breaks.** The `|` reads as "or": `str | None` = "str or None." This repo *only* uses
this modern spelling — you will never see `Optional[str]` here, so don't go learn that older
form.

### 2.4 Read four real signatures from `config.py`

**Do.** Open `src/fluffy_potato_curriculum/common/config.py` and read these four *real*
signatures. Say what each takes and returns:

```python
def get_settings() -> Settings: ...
def langfuse_configured() -> bool: ...
def require_anthropic_key() -> str: ...
def require_openai_key() -> str: ...
```

**You should say.** `get_settings` takes nothing, returns a `Settings` object;
`langfuse_configured` returns a `bool`; the two `require_*` functions return a `str` (the key)
— and, reading the bodies, *raise* if the key is missing.

**Why it matters.** This is a real file you already met in K02. You're now reading production
repo code, not toy snippets. That's the whole skill.

---

## 3. What a type hint is *for* (and isn't)

**Do.** Read this and predict: does Python *crash* at runtime when you pass a string?

```python
def double(n: int) -> int:
    return n * 2

double("oops")   # what happens?
```

**You should say.** Python does **not** crash — `"oops" * 2` is `"oopsoops"`, a legal string.
The *type checker* (pyright) would flag `double("oops")` as an error **before** you run, but
Python itself doesn't enforce the hint at runtime.

> **Concept — types are checked before run, not during.** pyright reads your code and complains
> about mismatches; the running program doesn't. Hints are a *contract for the reader and the
> checker*, not a runtime guardrail. (For real validation-at-runtime, that's pydantic — next.)

This kills the "but it ran fine, so the types must be right?" confusion. Ran fine ≠
type-correct.

> **Concept — the repo is pyright-strict, so every public `def` is fully annotated.** An
> untyped function fails the build, so the signature you're reading is always complete — the
> contract is always there to read.

---

## 4. What a pydantic model is

A pydantic model is a **typed, validated data container** — a named bag of typed fields that
**checks its data the moment you build it**. This repo prefers models over passing bare
`dict`s around.

### 4.1 Read the real `Settings` model

**Do.** In `common/config.py`, read the `Settings` class fields:

```python
class Settings(BaseSettings):
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_host: str | None = None
```

**You should say.** "A named container with five fields; each is a `str | None` defaulting to
`None` — so each is **optional**, absent by default." Apply your 2.3 reading directly.

> **Concept — `BaseSettings` loads fields from the environment / `.env`.** This is the K02
> config seam. *This class* is the object your `ANTHROPIC_API_KEY` loads into: env var →
> validated field.

### 4.2 A model validates on construction

**Do.** Read this tiny model and predict: which construction is fine, and which raises?

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    quantity: int

Item(name="widget", quantity=5)                # (a)
Item(name="widget", quantity="not a number")   # (b)
```

**You should say.** (a) is fine. (b) **raises a `ValidationError`** — pydantic can't coerce
`"not a number"` into an `int`, so it rejects it, naming the field `quantity`.

> **Concept — a pydantic model validates when constructed.** Bad data doesn't slip through to
> be discovered later; the model refuses to build. That refusal is the feature — it's *why* the
> repo passes models instead of `dict`s.

> **Concept — required vs. optional.** A field with a default (`str | None = None`) is
> optional; a field without one (`name`, `quantity`) is **required** — leave it out and you get
> the same `ValidationError`. Reading defaults tells you what's required.

### 4.3 Watch the ValidationError (run this)

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

**You should see.** A `ValidationError` traceback whose body names the offending field and
reason — roughly:

```
1 validation error for Item
quantity
  Input should be a valid integer, unable to parse string as an integer ...
```

**Why it matters.** This *is* the "If it breaks" you'll meet in the lessons when a model
rejects your data. Now you recognize it on sight: it tells you the field and the problem.

**If it breaks.** `ModuleNotFoundError: pydantic` means you're not in the repo `.venv` —
re-run with `uv run` from the repo root (K01). pydantic is already a dependency; you install
nothing.

---

## 5. The three places you'll meet pydantic models

You don't need to build these — just recognize each when a lesson shows it.

1. **Config — `BaseSettings`.** The `Settings` model in `config.py` (§4.1). Fields load from
   the environment / `.env`. **You've already met this** (K02).
2. **Structured output.** A `BaseModel` the code hands the LLM as the *shape it must fill in*,
   then parses the reply back into. You'll meet this in the prompting/output lessons (L02) and
   again as tool schemas (L07).
3. **Tool schemas.** A model describing a tool's arguments so the LLM can call the tool with
   the right fields — the agent lessons (L11+).

> **Concept — same object, three jobs.** Config, output shape, tool args — all the *same* idea:
> a typed bag that validates itself. Learn to read one and you can read all three.

Today `config.py`'s `Settings` is your one concrete model; the other two are described here so
you recognize them the moment a lesson drops a `class Foo(BaseModel):` on you.

---

## Pass checkpoint — self-check

Self-graded. Answer from **reading**, then check against the key. You pass when 1 and 2 are
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

**Q3 — Predict a validation error.** Before running §4.3's snippet, what happens when
`Item(quantity=...)` gets `"not a number"` for an `int` field?

<details>
<summary><b>Answer key</b> (don't peek until you've answered)</summary>

- **Q1.** `get_settings` — takes nothing, returns a `Settings` object. `require_anthropic_key`
  — takes nothing, returns a `str` (the key), and raises if it's missing.
  `langfuse_configured` — takes nothing, returns a `bool`. `run` — takes `messages`, a **list
  of string-keyed dicts**, and returns **either a `str` or `None`** (so the caller must handle
  the `None`). Getting `-> bool` and `str | None` right is the bar.
- **Q2.** Type `str` or absent; **not required** — it's `str | None` with a default; defaults
  to `None`. So the object always builds even with no key set (that's why `config.py` has the
  `require_*` helpers — they turn "absent" into a clear error at the point of use).
- **Q3.** It raises a `ValidationError` naming the `quantity` field — pydantic can't parse
  `"not a number"` as an int, so it refuses to construct the model.

</details>

If any answer surprised you, re-read the section it came from (Q1 → §2; Q2 → §4.1; Q3 →
§4.2/4.3) before moving on. Confident interpretation is the bar — not memorized rules.

---

## Bridge to K05

You can now read a typed signature as a contract and a pydantic model as a self-validating
bag. **K05 (async concepts)** adds exactly two new things to that same reading:

- one keyword — **`async`** in front of `def`,
- one operator — **`await`** in front of a call,

plus the reason agents want them: concurrent tool calls, parallel eval cases, and non-blocking
traces/streaming. That "why async for agents" explainer is K05's to give — K04 just hands you
the reading skill it builds on. Go straight to K05.
