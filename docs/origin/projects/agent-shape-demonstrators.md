# Agent-shape demonstrators — problem + dataset ideas

> **Purpose:** a brainstorm bank of *problem + dataset* pairs, grouped by the three
> orchestration shapes the course teaches, for authoring lesson demos/labs and end-of-week
> project briefs. This is **design source** (an idea menu), not a committed brief — promote a
> pick into `src/fluffy_potato_curriculum/projects/<brief>/` following
> [PROJECT_BRIEF_DESIGN.md](../PROJECT_BRIEF_DESIGN.md) when it graduates.
>
> **Audience:** whoever is authoring a demo, lab, or project and needs a task that *cleanly*
> exercises one graph shape. Each idea states **why the shape fits** (the pedagogical "tell")
> so the wrong shape isn't reached for.

## The three shapes and where they live

| Shape | Owning lesson(s) | Who decides the path | The one-line tell |
| --- | --- | --- | --- |
| **Linear node-DAG** | [L04](../lesson_roadmaps/L04/objectives.md) — sequential chaining | Developer wires a **fixed** forward path | The task is a *known, unbranching* sequence: step N's output feeds step N+1, every run takes the same route |
| **Conditional DAG** | [L05](../lesson_roadmaps/L05/objectives.md) — routing & branching | Developer wires branches; a **routing function** reads state | The set of paths is *known ahead of time*, but *which* one runs depends on a classification / lookup / user choice |
| **Free-form shallow agent** | [L10](../lesson_roadmaps/L10/objectives.md) loop + [L11](../lesson_roadmaps/L11/objectives.md) `create_agent` | The **model** decides which tool, in what order, and when to stop | The steps *can't be known in advance* — the query is open-ended and needs the cyclic loop |

**Domains already spent by the demos — pick something else for a project.** L04/L05 both run the
**support-ticket** domain (parse → draft → policy-check; then classify → billing/technical/general
→ converge). L10/L11 run **`calculator` + `lookup` + `flaky_fetch`** on an arithmetic-puzzle task.
The ideas below deliberately use *contrasting* domains so a project isn't a re-skin of a demo. (A
single-domain "triptych" reuse is noted at the end for teams who'd rather go deep on one dataset.)

**Dataset ground rules (all ideas honor these).** Datasets must be **small, offline, and
reproducible** — a CSV/JSONL/markdown fixture that ships in the brief folder, so a run costs cents
and passes restart-and-run-all without a network fetch (see the notebook + config-seam rules). Live
model calls still go through the config seam; the *data* the agent reads is canned. Where an idea
points at a public dataset, the intent is "take a ~20–50 row slice and commit it," never "fetch at
runtime."

---

## 1. Linear node-DAG demonstrators (L04)

**What makes a good one:** a task that genuinely decomposes into a *fixed chain* of focused steps —
extract → transform → generate → check — where splitting one mega-prompt into small typed nodes buys
reliability, per-node testing, and per-node model mixing (Haiku for the light extract/format nodes,
Sonnet for the heavy generate node). **Anti-pattern to avoid:** a task with a real fork in it — if
"it depends" enters the description, it's an L05 router, not a chain.

### 1a. Meeting transcript → action-item recap email  ⭐ recommended
- **Problem:** turn a raw meeting transcript into a structured recap email with owners and due dates.
- **Node chain:** `clean/segment` → `extract decisions + action items` (structured) → `assign owner + due date` → `draft recap email` (Sonnet) → `tone/format check` against a house-style snippet.
- **Dataset:** ~10–15 synthetic transcripts (generate once, commit as `.txt`/`.jsonl`); pair each with a 4–5 line style policy for the check node. No PII, fully offline.
- **Why linear:** every meeting goes through the *same* five steps in the same order — there is no branch. It's the cleanest "why decompose vs. one giant prompt" story: each node is independently checkable, and the `extract` step is a natural Haiku-vs-Sonnet contrast.

### 1b. Product-review digest card
- **Problem:** condense a batch of product reviews into a single at-a-glance summary card (per-aspect sentiment + a one-line verdict).
- **Node chain:** `parse review` → `extract aspects` (battery, screen, price…) → `score sentiment per aspect` → `compose summary card` → `format/length check`.
- **Dataset:** a ~30-row reviews CSV — either a committed slice of a public review corpus (Amazon/Yelp-style) or fully synthetic. Easiest dataset to source of the four.
- **Why linear:** fixed pipeline, and the aspect-extract → sentiment split shows why two small prompts beat one ("extract *then* judge" is more reliable than "extract-and-judge at once").

### 1c. Recipe scaler → grouped shopping list
- **Problem:** take a recipe and a target serving count, produce a shopping list grouped by store aisle.
- **Node chain:** `parse recipe` → `normalize units` → `scale to N servings` → `group ingredients by aisle` → `render list`.
- **Dataset:** ~12 recipes as markdown/JSON fixtures.
- **Why linear:** the most *deterministic-feeling* chain here — great for making "control flow as data" concrete because a reader can predict the whole path. Light on model judgment (good for a lab where the graph mechanics, not prompt quality, are the point).

### 1d. Research abstract → plain-language explainer
- **Problem:** rewrite a dense paper abstract as an ELI15 explainer without losing the core claim.
- **Node chain:** `parse abstract` → `extract claims + method` → `de-jargon` → `draft plain-language summary` (Sonnet) → `readability check`.
- **Dataset:** ~20 committed abstracts (arXiv/PubMed slice — abstracts are short and redistributable-friendly; confirm licensing on the exact source before committing).
- **Why linear:** fixed sequence, and the `readability check` terminal node is a natural home for L04's optional "evaluate the workflow" beat.

<!-- *NEED INPUT*: which one to promote to a full brief. Recommendation: 1a (meeting recap) as the flagship linear brief (universally relatable, obviously a chain), with 1b (product reviews) as the low-friction lab example since its dataset is trivial to source. -->

---

## 2. Conditional DAG demonstrators (L05)

**What makes a good one:** a task where inputs fan out into a *small, known set* of branches that do
**genuinely different work**, and where a **fallback/ambiguous case is load-bearing** (L05's central
craft lesson — "a router that only knows how to succeed isn't done"). **Anti-pattern to avoid:**
branches that all do the same thing with a different noun — that's a linear chain with a variable,
not a router.

### 2a. Content-moderation router  ⭐ recommended
- **Problem:** route a user post to `allow` / `needs-review` / `block` and produce the branch-appropriate artifact.
- **Branch shape:** `classify (+ reason)` → **allow** (pass through, log) · **needs-review** (draft a reviewer summary) · **block** (generate a policy citation). Converge to a decision record.
- **Dataset:** ~25 synthetic posts (clean, borderline, clearly-violating) + a short (5–8 rule) policy doc. Include ≥2 deliberately ambiguous posts.
- **Why conditional:** the three branches do *visibly different* work, and **`needs-review` is a real fallback** — the ambiguous post that the classifier hedges on lands there instead of erroring. That maps one-to-one onto L05's fallback-branch teaching moment.

### 2b. Homework answer-type grader
- **Problem:** grade a student answer, routing by *question type* because each type is graded differently.
- **Branch shape:** `classify question type` → **multiple-choice** (exact match) · **short-answer** (key-fact rubric) · **essay** (rubric + Sonnet judgment) · **code** (spec check). Converge to a score + feedback.
- **Dataset:** ~20 question+answer fixtures spanning the four types.
- **Why conditional:** the strongest "branches genuinely differ" example in the set — an MCQ grader and an essay grader share *nothing* but the graph shape. Good for driving home "same shape, different work per branch."

### 2c. Personal-finance transaction router
- **Problem:** process a bank transaction down one of `auto-categorize` / `needs-enrichment` / `flag-anomaly`.
- **Branch shape:** `classify` → **auto-categorize** (cheap label) · **needs-enrichment** (look up merchant, draft a note) · **flag-anomaly** (generate an alert). Converge to an enriched record.
- **Dataset:** a ~40-row synthetic transactions CSV with a few planted anomalies (duplicate charge, out-of-pattern amount).
- **Why conditional:** clean three-way fan-out with an obvious cost story (most rows take the cheap auto-categorize branch; only the odd one out pays for the expensive branch) — reinforces per-node model mixing from L04 on a fresh domain.

### 2d. Multilingual FAQ concierge
- **Problem:** answer a support FAQ, routing on *both* detected language and intent.
- **Branch shape:** `detect language + intent` → intent-specific answer branch, rendered in the detected language; unknown intent → **fallback** "escalate to human" branch.
- **Dataset:** ~20 FAQ pairs across 2–3 languages + a handful of out-of-scope questions to exercise the fallback.
- **Why conditional:** shows routing on a *composite* key (language × intent) without a model driving the loop, and the out-of-scope questions make the fallback branch matter. Slightly more advanced (two routing dimensions) — good as a stretch.

<!-- *NEED INPUT*: which one to promote. Recommendation: 2a (moderation) as the flagship — its fallback/ambiguous story lines up exactly with L05's Demo 2, so a project reinforces the lecture. 2b (answer-type grader) is the best pick if the goal is to hammer "branches do genuinely different work." -->

---

## 3. Free-form shallow-agent demonstrators (L10 / L11)

**What makes a good one:** an *open-ended* task over a **toolset**, where the model must choose which
tools to call, in what order, how many times, and when to stop — and where a fixed chain or router
*couldn't* pre-wire the answer because it depends on intermediate results. The "dataset" here is
**canned tool-backed data + a bank of tasks/questions**. **Anti-pattern to avoid:** a task with one
obvious tool-call sequence — if you can draw the DAG ahead of time, it's an L04/L05 workflow, and
reaching for an agent just adds cost and unpredictability (the exact failure mode L04/L05 warn about).

### 3a. Multi-hop research agent over an offline knowledge base  ⭐ recommended
- **Problem:** answer multi-hop questions ("what year was the director of *<film>* born?") that require chaining several lookups.
- **Toolset:** `search(query) -> titles`, `get_article(title) -> text`, `get_section(title, section) -> text`.
- **Dataset:** a committed JSON snapshot of ~30–50 interlinked mini-articles (people, films, places) with deliberate cross-references, so 2–3 hops are *required* and reproducible offline.
- **Why an agent:** the number and order of lookups depend on what each search returns — you cannot pre-wire it. This is the canonical "the loop earns its keep" task, and multi-hop makes the back-edge visibly fire more than once.

### 3b. Data-analyst agent over a small SQL store  ⭐ recommended
- **Problem:** answer open-ended questions about a dataset ("which product had the biggest month-over-month growth?").
- **Toolset:** `list_tables()`, `describe_table(name)`, `run_sql(query)`, `calculator(expr)`.
- **Dataset:** a small SQLite / DuckDB file (or CSVs loaded into DuckDB) — synthetic store sales, or a committed slice of a classic sample DB (Chinook/Northwind). ~4 tables, a few hundred rows.
- **Why an agent:** different questions need different queries in different orders (inspect schema → draft SQL → maybe recompute → summarize); the model genuinely drives control. Also the most "real job" flavored of the set. (This is the concrete DuckDB tool the PRD's "common toolbelt" TODO earmarks for L08 — a project is a natural place to cash it in.)

### 3c. Returns & refund support agent  (ties the whole arc together)
- **Problem:** decide whether a customer can return an order and for how much, then draft the reply.
- **Toolset:** `lookup_order(id)`, `check_return_window(order)`, `calc_refund(order, reason)`, `search_policy(query)`.
- **Dataset:** an orders CSV (~30 rows) + a short returns-policy doc.
- **Why an agent:** eligibility depends on facts the model discovers mid-run (order date, item condition, policy edge cases), so tool order varies per case. **Pedagogical bonus:** it's the *same support domain* L04/L05 wired as a workflow — running it as a model-driven agent makes the "workflow vs. agent" contrast concrete on one dataset (see triptych note below).

### 3d. Personal-expense assistant
- **Problem:** answer budget questions ("am I over on dining this month, and by how much?").
- **Toolset:** `search_transactions(filter)`, `sum_by_category(cat, period)`, `get_budget(cat)`, `calculator(expr)`.
- **Dataset:** a transactions CSV + a budget JSON (reuse/extend 2c's transactions fixture).
- **Why an agent:** the question dictates which tools and how many arithmetic steps; the `calculator` forces a real second hop after the data lookup. A gentler agent task than 3a/3b — good for a first agent lab.

<!-- *NEED INPUT*: which one(s) to promote. Recommendation: 3a (multi-hop research) and 3b (SQL analyst) are the two strongest "you cannot pre-wire this" demonstrators — pick one as the flagship agent brief. 3c is the pick if you want the L04→L05→L10 arc to land on a single shared domain. -->

---

## Cross-cutting notes for whoever authors from this

- **Reuse one dataset across all three shapes (the "triptych").** The **e-commerce/support** domain
  can carry a linear brief (draft-a-reply pipeline), a conditional brief (triage router), *and* an
  agent brief (3c returns agent) on one committed orders+policy fixture. That lets a project or a
  lesson thread show, on identical data, "developer wires the flow → developer wires the branches →
  model drives the flow" — the exact arc L04 Demo 4 and L05 Demo 4 set up. Trade-off: less domain
  variety; upside: the shape contrast is unmistakable.
- **Per-node model mixing** (Haiku light / Sonnet heavy) is a free win for every linear and
  conditional idea — the classify/extract/format nodes are Haiku, the generate/judge nodes are
  Sonnet. Call it out in the brief; it's L04/L05's per-node binding objective on real data.
- **Every idea should carry a tiny eval set** — the L13 "evaluate everything you build" habit. The
  linear and conditional ideas are trivially evaluable (same input → same path); the agent ideas
  eval on final-answer correctness plus tool-call trace shape.
- **Difficulty ladder for a first agent lab:** 3d (expenses) < 3c (returns) < 3b (SQL) ≈ 3a
  (multi-hop). Start gentle if it's students' first `create_agent` run.

<!-- *NEED INPUT*: should any of these graduate into `src/fluffy_potato_curriculum/projects/` now, or stay an idea menu until a project week needs one? Default: keep as a menu; promote on demand per PROJECT_BRIEF_DESIGN.md. -->
