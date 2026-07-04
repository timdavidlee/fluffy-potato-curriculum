# TODO — repair broken in-page TOC / back-to-top anchors (curriculum-wide)

**Status: DONE** (2026-07-03). All 19 anchors across 11 files regenerated from their
current heading slugs; a durable guard now enforces this — `tests/lessons/test_toc_anchors.py`
walks every `lessons/**/*.{md,ipynb}` and asserts each same-doc `#anchor` resolves to a
heading (faithful GitHub slugger, so double-hyphen `—`/` -- ` targets are not false positives).
The repro in this note collapsed space runs and over-reported (262 hits); the guard mirrors
GitHub's non-collapsing rule instead.

Discovered 2026-07-04 while verifying the L11 reorder (PRs #44 / #47 / #49). The reorder
fixed only the anchors it broke or touched (`L1206`, `L1307`, `L2206` — landed in #49);
this note tracks the **pre-existing, unrelated** breakage across other lessons.

## The problem

Notebook TOC links and `[↑ Back to top]` links are **hand-authored** `](#slug)` targets.
When a heading is later reworded (or its punctuation changes), the anchor is not updated,
so the link points at a slug that no longer exists. GitHub builds heading slugs by
lowercasing, stripping punctuation, and turning runs of spaces into hyphens — so a `:`,
`+`, `(...)`, or an em/en-dash (`—`, `--`) in a heading is easy to get wrong by hand.

Confirmed real (not slug-tool false positives), e.g.:
- `L10/L1004`: heading "Problem 5 — **Multiple tool calls in one reply**" but anchor
  `#6-problem-5--**two-tool-calls-in-one-response**-written` (heading was reworded).
- `L05/L0503`: heading gained a "(a forward-pointing taste…)" parenthetical the anchor omits.
- `L02/L0210`: heading `-- Classification: prompt + validator` → the `:`/`+`/` -- ` produce a
  different slug than the hand-written anchor.

## Snapshot (main @ `1cbe917`, 2026-07-04) — 11 files, ~19 anchors

This drifts as lessons change; **regenerate the list** with the repro below rather than
trusting this snapshot.

- `L01/L0106_lecture.ipynb` — `#4-what-this-is-and-is-not`
- `L02/L0210_lab_empty.ipynb` + `_solutions.ipynb` — 5 problem anchors each
- `L04/L0403_lecture.ipynb` — `#6-read-the-trace`
- `L05/L0503_lecture.ipynb` — `#5-read-the-trace----a-model-per-node`
- `L08/L0806_lab_solutions.ipynb` — `#3-problem-2--tighten-the-parameter-schema`
- `L09/L0906_lecture.ipynb` — `#1-the-pure-python-core-this-part-is-just-l05`
- `L10/L1004_lab_empty.ipynb` + `_solutions.ipynb` — `#6-problem-5--two-tool-calls-…`
- `L13/L1303_lab_empty.ipynb` + `_solutions.ipynb` — `#4-problem-3--a-regression-case-from-an-l08-failure`

## Repro / regenerate the list

```python
# uv run python - <<'PY'
import json, re, glob, os
def slug(t):
    s = t.strip().lower(); s = re.sub(r'[^\w\s-]', '', s); s = re.sub(r'[ \t]+', ' ', s)
    return s.replace(' ', '-')
def text_of(p):
    if p.endswith('.md'): return open(p).read()
    nb = json.load(open(p))
    return "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "markdown")
for p in glob.glob("src/fluffy_potato_curriculum/lessons/**/*", recursive=True):
    if not p.endswith((".md", ".ipynb")): continue
    t = text_of(p)
    heads = {slug(m.group(1)) for m in re.finditer(r'(?m)^#{1,6}\s+(.*)$', t)}
    broken = [a for a in re.findall(r'\]\(#([^)]+)\)', t) if a != "top" and a not in heads]
    if broken: print(p, sorted(set(broken)))
PY
```

## Fix approach (own pass; independent of the L11 reorder)

- [x] Regenerate every `](#…)` in-page anchor from its actual heading slug (mechanical:
      map each TOC/back-to-top link to the current heading's GitHub slug). Watch the
      GitHub slug rules for `—`/`--`, `:`, `+`, `()`.
- [x] Re-run the check until it prints nothing (used a *faithful* slugger, not the buggy
      space-collapsing repro below).
- [x] Added the durable **guard**: `tests/lessons/test_toc_anchors.py` (one parametrized
      case per doc; strips fenced code; applies GitHub's `-1`/`-2` dedup).
- [x] `_empty`/`_solutions` pairs kept in sync (both fixed — L02/L0210, L10/L1004, L13/L1303).

Not blocking anything; low-risk, edits are navigation-only (no code/behavior change).
