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

**Prefer inputs a student can eyeball.** Favor raw samples whose correct output a semi-technical
student can verify by *reading the source* — a log they can hand-trace, a receipt whose math must
reconcile — over inputs that need domain expertise to grade (e.g. "is this plain-language rewrite of
a paper *faithful*?"). Verifiable-by-eye data is what makes the L13 "evaluate everything you build"
habit honest at this level.

---

## 1. Linear node-DAG demonstrators (L04)

**What makes a good one:** a task that genuinely decomposes into a *fixed chain* of focused steps —
extract → transform → generate → check — where splitting one mega-prompt into small typed nodes buys
reliability, per-node testing, and per-node model mixing (Haiku for the light extract/format nodes,
Sonnet for the heavy generate node). **Anti-pattern to avoid:** a task with a real fork in it — if
"it depends" enters the description, it's an L05 router, not a chain.

### 1a. Multi-page website-log traffic report  ⭐ recommended
- **Problem:** turn a raw web-server access log into a plain-English traffic report — per-visitor page journeys, top pages, entry/exit points, error and bot-spike callouts.
- **Node chain:** `parse log lines` (→ structured hits) → `sessionize` (group hits into per-visitor page sequences by IP + time gap) → `aggregate metrics` (top pages, bounce rate, 4xx/5xx counts, traffic spikes) → `draft insights report` (Sonnet) → `format/completeness check` against a report template.
- **Dataset:** one committed ~300-line access log in nginx/Apache combined format — ~12 distinct visitors moving across a handful of pages, some 404s, and one obvious scraper/bot spike. Fully offline, human-readable.
- **Why linear:** every log flows through the *same* parse → sessionize → aggregate → report sequence, no branch. And it's the cleanest **verify-by-eye** story in this section — a student can read the raw log, hand-trace one visitor's path, and check the report against it. `parse`/`sessionize` are natural Python-or-Haiku nodes; the narrative report is the Sonnet node.

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

### 1d. Receipt/invoice → line items → totals reconciliation
- **Problem:** extract the line items from a messy receipt/invoice and reconcile them against the stated total, flagging any discrepancy.
- **Node chain:** `parse receipt text` → `extract line items` (qty · description · unit price · amount) → `compute subtotal + tax + total` (plain Python) → `reconcile vs. stated total` → `format flag report`.
- **Dataset:** ~20 committed plain-text receipts/invoices with varied layouts, a few carrying a planted arithmetic error or a dropped line. Fully offline and immediately legible.
- **Why linear:** fixed extract → compute → check sequence — and the reason it replaces the old research-abstract idea: **correctness is objectively checkable**. A student reads the receipt, confirms the extracted items, and the totals either reconcile or they don't. That deterministic ground truth makes it the best home in this section for L04's optional "evaluate the workflow" beat.

<!-- *NEED INPUT*: which one to promote to a full brief. Recommendation: 1a (website-log traffic report) as the flagship linear brief — relatable, obviously a fixed chain, and directly verifiable against the raw log — with 1b (product reviews) as the low-friction lab example since its dataset is trivial to source. 1d (receipt reconciliation) is the pick when you want an objectively-gradable output for the eval beat. -->

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
- **Policy the classifier reads (concrete):** ~6 rules — `P1` threats/harassment, `P2` hate speech, `P3` spam/scam links, `P4` self-harm signals (→ *always* `needs-review` + a resources note, never auto-`block`), `P5` adult content. A **low-confidence** classification on any post *also* routes to `needs-review` — the "reject option" that stops the model from guessing on borderline cases (a nice teaching nuance: the fallback fires on *uncertainty*, not just on a specific label).
- **Decision record (the converge output):** `{post_id, decision, matched_rules, reason, confidence, artifact}` — `artifact` is the reviewer summary (`needs-review`) or the policy citation (`block`), and empty for `allow`.
- **Worked examples:**

  | Post | Branch | Artifact |
  | --- | --- | --- |
  | "Check out my store 🔥 buy now bit.ly/x2z" | `block` (P3 spam) | citation of rule P3 |
  | "i'm so done, nothing matters anymore" | `needs-review` (P4, ambiguous) | reviewer summary + resources note |
  | "gg, great match yesterday" | `allow` | logged, no action |

- **Starter eval set (L13 carry-forward):** ~5 `EvalCase`s of *post → expected decision*, with the ambiguous self-harm post pinned to `needs-review` so the case doubles as a regression check that the fallback wiring holds. A router is trivially testable — same post, same branch — which is half the reason to prefer one.
- **Forward hook:** the `needs-review` branch is exactly where **L17** (human-in-the-loop) later splices an approval/interrupt node — name it as a forward pointer, don't build it here.

### 2b. Multi-genre document intake extractor (router → completeness gate)
- **Problem:** an inbound document/email arrives in one of several genres; extract the genre-appropriate schema, then decide whether the extract is clean enough to persist or needs a follow-up.
- **Branch shape (two conditional edges):** `classify genre` → **invoice** (extract vendor · invoice # · line items · total · due date) · **job application** (extract applicant · role · years experience · contact) · **return request** (extract order id · item · reason · purchase date) · **unknown** (fallback → human triage). Converge, then a `validate required fields` node feeds a **second** conditional edge: → **ready-to-insert** (emit the record) · **requires-more-info** (list the missing fields, draft the follow-up ask).
- **Dataset:** ~20–25 inbound emails/documents across 3–4 genres, deliberately mixed quality — some complete, some missing a required field per their genre, plus a couple of off-genre items for the `unknown` branch.
- **Why conditional:** two routing decisions in one graph. The **genre router** keeps the "**branches do genuinely different work**" virtue — each branch targets a *different schema*, so an invoice extractor and an application extractor share nothing but the graph shape. The **completeness gate** is a second conditional edge whose `requires-more-info` branch is the load-bearing fallback (L05's central craft lesson). It's verify-by-eye — a student reads the email and its genre and missing fields are obvious — and it sets up **L12**'s extract→datastore framing directly: `ready-to-insert` *is* "the extract is clean enough to become a record."

### 2c. Hotel booking-change router (classify → validate → action)
- **Problem:** a guest emails a single hotel to change an existing reservation; classify the intent, validate it against the hotel's availability and policies, then take the right action — or explain why it can't.
- **Branch shape:** `classify intent` → **move dates** (validate the new slot → **rebook** if open · **offer alternatives** if full) · **upgrade** (validate the room class → **apply upgrade + fare difference** if available · **waitlist/decline** if not) · **cancel** (validate against the cancellation policy → **cancel + refund** if within policy · **cancel with penalty / deny refund** if against it) · **unclear** (fallback → ask the guest to clarify). Converge to a decision record + guest reply.
- **Dataset:** one hotel's fixture — a small availability table (room types × dates), a short cancellation-policy snippet (e.g. free cancel ≥48h out; a non-refundable rate), and ~20 guest messages spanning every intent and *both* outcomes (dates that are open and full; cancellations inside and outside the window).
- **Why conditional:** a **router whose branches each hold their own validate-then-branch decision** — several conditional edges, all reading developer-owned state (the availability table, the policy). The distinctive twist over 2b: the gate here is a **business rule**, not data-completeness, and each failure yields a *different action* (offer alternatives · waitlist · charge a penalty), so the unhappy-path branches are genuinely different work — exactly L05's "a router must define behavior for the cases you'd rather not hit." Verify-by-eye: read the request, check the availability table or policy, and the expected action is unambiguous.

### 2d. Multilingual FAQ concierge
- **Problem:** answer a support FAQ, routing on *both* detected language and intent.
- **Branch shape:** `detect language + intent` → intent-specific answer branch, rendered in the detected language; unknown intent → **fallback** "escalate to human" branch.
- **Dataset:** ~20 FAQ pairs across 2–3 languages + a handful of out-of-scope questions to exercise the fallback.
- **Why conditional:** shows routing on a *composite* key (language × intent) without a model driving the loop, and the out-of-scope questions make the fallback branch matter. Slightly more advanced (two routing dimensions) — good as a stretch.
- **Intents & languages (concrete):** a handful of intents — `hours`, `shipping_status`, `returns`, `password_reset` — over 2–3 languages (EN/ES/FR). The knowledge base is a small table keyed by intent, each row carrying a localized answer per language: `{intent, answers: {en: "...", es: "...", fr: "..."}}`.
- **The design decision this teaches (the real depth):** the *naive* graph fans out on **both** dimensions — a node per (language × intent), i.e. N×M nodes that explode when you add either a language or an intent. The better graph **branches on intent only** (developer-wired) and treats the **detected language as a field the chosen branch reads** to pick the localized text. Show both; recommend the second. *"Branch on one dimension, parameterize the other"* is the transferable lesson — and it's why this earns the section's stretch slot rather than being a third plain router.
- **Worked examples:**

  | Question | (intent, lang) | Answer branch |
  | --- | --- | --- |
  | "¿Cuál es el estado de mi envío?" | (`shipping_status`, es) | shipping answer, rendered ES |
  | "How do I reset my password?" | (`password_reset`, en) | reset answer, rendered EN |
  | "Do you sponsor work visas?" | (`unknown`, en) | **fallback** → escalate to human |

- **Starter eval set:** ~5 `EvalCase`s of *question → expected (intent, language)*, including one out-of-scope question pinned to the fallback branch. There are two routing dimensions to assert, so it's a slightly richer eval than 2a/2c — good practice at asserting a *composite* decision, not a single label.

<!-- *NEED INPUT*: which one to promote. Recommendation: 2a (moderation) as the flagship — its fallback/ambiguous story lines up exactly with L05's Demo 2, so a project reinforces the lecture. 2b (multi-genre intake extractor) is the best pick if you want two conditional edges in one graph — a genre router feeding a completeness gate — and a natural bridge into L12's extract→datastore framing. -->

---

## 3. Free-form shallow-agent demonstrators (L10 / L11)

**What makes a good one:** an *open-ended* task over a **toolset**, where the model must choose which
tools to call, in what order, how many times, and when to stop — and where a fixed chain or router
*couldn't* pre-wire the answer because it depends on intermediate results. The "dataset" here is
**canned tool-backed data + a bank of tasks/questions**. **Anti-pattern to avoid:** a task with one
obvious tool-call sequence — if you can draw the DAG ahead of time, it's an L04/L05 workflow, and
reaching for an agent just adds cost and unpredictability (the exact failure mode L04/L05 warn about).

### 3a. Health-plan coverage research agent (overlapping plans)  ⭐ recommended
- **Problem:** answer "is _X_ covered?" (and "is _X_ or _Y_ covered?") for a member enrolled in several overlapping plans — a **general/medical** plan, a **vision** plan, and a **dental** plan — where the same procedure can live under different plans and be covered by one but excluded by another.
- **Toolset:** `list_plans()` (the member's enrolled plans + summaries), `search_coverage(query)` (→ matching clauses across *all* plans, each tagged with which plan + section), `get_section(plan, section)` (the full coverage / exclusion / limit / pre-auth text).
- **Dataset:** three short committed plan documents (medical / vision / dental), each with `covered services`, `exclusions`, `limits & frequency`, `pre-authorization`, and a `coordination of benefits` note. Engineer the overlaps deliberately: e.g. the **vision** plan excludes "medical eye conditions — see medical plan," the **medical** plan covers "oral surgery from trauma" while **dental** covers routine extractions, and several services carry a frequency limit or a "covered *only if* <condition>" clause. Add a bank of ~15–20 questions spanning single-service, "X or Y," and overlap-triggering cases. Offline and **verify-by-eye** — a student reads three short policies and can confirm both the answer and the hop chain.
- **Why an agent:** the plan a procedure belongs to **isn't known up front**, so the number and order of lookups depend on what each clause reveals — an exclusion in one plan *redirects* the search to another (the back-edge fires again), and "is X *or* Y covered?" spawns two sub-investigations that may overlap. The agent must also decide when it has read enough to answer **yes / no / depends-with-conditions** (surfacing the frequency limit or pre-auth requirement, not just a bare yes). You cannot pre-wire it — the canonical "the loop earns its keep" task, now on a domain where the overlaps are the *reason* it chains. (Still foreshadows RAG / multi-hop retrieval in L20–L21.)

### 3b. Transaction drill-down analyst agent  ⭐ recommended
- **Problem:** answer open-ended "why" questions about a transactions dataset ("why did spending spike in March?") by drilling down — aggregate, spot the outlier, segment it, and isolate the individual transactions behind it.
- **Toolset:** `list_tables()`, `describe_table(name)`, `run_sql(query)`, `calculator(expr)` — DuckDB over the transaction data.
- **Dataset:** a small committed transactions store (SQLite/DuckDB, or CSVs loaded into DuckDB) — a `transactions` fact table (date · amount · category · merchant · account) plus a couple of dimension tables, a few hundred rows, with a **planted anomaly** or two (a category that spikes one month, a duplicated merchant charge) so the drill-down has something to find. Offline; verify-by-eye against the rows.
- **Why an agent:** drill-down is **inherently sequential** — each query is chosen from the *previous* result: total by month → March is high → by category → dining is up → by merchant → one vendor → list those rows. You can't pre-write the sequence, because you don't know March (or dining, or that vendor) is the culprit until the prior aggregate returns. Same "chain of dependent steps" as 3a, but over **structured tables via SQL**, so it stresses a different skill: query generation + recovering from a bad query (error → fix), which lines up with L10's tool-failure beat. (This is the DuckDB tool the PRD's "common toolbelt" TODO earmarks for L08 — a project is a natural place to cash it in.)

### 3c. Returns & refund support agent  (ties the whole arc together)
- **Problem:** decide whether a customer can return an order and for how much, then draft the reply.
- **Toolset:** `lookup_order(id)`, `check_return_window(order)`, `calc_refund(order, reason)`, `search_policy(query)`.
- **Dataset:** an orders CSV (~30 rows) + a short returns-policy doc.
- **Why an agent:** eligibility depends on facts the model discovers mid-run (order date, item condition, policy edge cases), so tool order varies per case. **Pedagogical bonus:** it's the *same support domain* L04/L05 wired as a workflow — running it as a model-driven agent makes the "workflow vs. agent" contrast concrete on one dataset (see triptych note below).

### 3d. Personal flight-booking agent
- **Problem:** the user gives a destination and a *fuzzy* timeframe ("a long weekend in early March, from the Bay Area"); the agent explores options and returns a short list of booking possibilities with trade-offs (price, non-stop vs. multi-hop, total duration, departure time).
- **Toolset:** `resolve_airports(city)` (a city may map to several — SFO/OAK/SJC), `search_flights(origin, destination, date)` (→ candidate itineraries), `get_itinerary(flight_id)` (legs, layovers, duration), `calculator(expr)` (compare totals / connection times).
- **Dataset:** a committed flights fixture — a schedule table of routes × dates × flights (price, stop count, legs, times), plus an airports table (city → codes). Sized so multiple dates *and* multiple nearby airports exist, and so some non-stops are pricey enough that a connection is worth surfacing. Fully offline; verify-by-eye ("cheapest non-stop on the 12th is $X" is checkable in the fixture).
- **Why an agent:** the **fuzzy timeframe is what forces the loop** — the agent decides how many dates to probe, whether to try nearby airports, and whether to fall back to multi-hop when non-stops are unavailable or expensive, then decides when the shortlist is good enough to stop. The number and order of searches can't be pre-wired. **Honest caveat (and a good teaching beat):** if you *fix* the window to an explicit date list and a single airport pair and just "return the cheapest," this collapses into an L05 fan-out, not an agent — keep the timeframe genuinely open-ended so the model owns the search. It's also the best "watch the back-edge fire many times" demonstrator in the set, which pairs naturally with L10's `recursion_limit`/termination beat (cap the probing).

<!-- *NEED INPUT*: which one(s) to promote. Recommendation: 3a (health-plan coverage research) and 3b (transaction drill-down) are the two strongest "you cannot pre-wire this" demonstrators — pick one as the flagship agent brief. 3c is the pick if you want the L04→L05→L10 arc to land on a single shared domain. -->

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
- **Difficulty ladder for a first agent lab:** 3c (returns) < 3b (SQL) < 3d (booking) ≈ 3a
  (coverage research). Start gentle (3c, a bounded lookup→check→calc) if it's students' first
  `create_agent` run; 3d and 3a are the deepest because both drive *many* loop turns — save them
  for after the loop and `recursion_limit` are solid.

<!-- *NEED INPUT*: should any of these graduate into `src/fluffy_potato_curriculum/projects/` now, or stay an idea menu until a project week needs one? Default: keep as a menu; promote on demand per PROJECT_BRIEF_DESIGN.md. -->
