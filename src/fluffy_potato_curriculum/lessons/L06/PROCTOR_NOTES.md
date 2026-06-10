# L06 Proctor Notes

Notes for whoever runs the L06 labs. One section per problem, keyed by lab id and problem number.
Times are rough and assume a semi-technical student with basic Python who completed L01–L05.

> **Environment note (read first):** the Python **`mcp` package is not installed** in the course env.
> Both L06 labs (**L0604** validate/translate a tool spec, **L0607** the MCP-vs-inline decision) are
> therefore **fully offline / pure standard library** (`json`, `dataclasses`) — **no API key, no `mcp`
> package, no network.** They run here deterministically. The lab teaches the conceptual core of MCP —
> *a well-designed tool serialized to a portable spec, and the decision to package it that way* —
> without a live server.
>
> Two L06 lecture artifacts **show code that needs `mcp`** and are deliberately **not runnable** in
> this env: the connect walkthrough ([L0605_lecture.md](L0605_lecture.md), a slide outline) and the
> build-a-server walkthrough ([L0606_lecture.ipynb](L0606_lecture.ipynb), shown but not executed). Do
> **not** ask students to run those — they read them for the wire shape and the server skeleton. The
> runnable offline counterpart is the [L0603 demo](L0603_lecture.ipynb).
>
> **The single most repeated correction this lesson:** *MCP changes packaging and transport, not tool
> design.* Every L05 principle (name, description, schema, error shape) is unchanged. If a student
> thinks MCP makes design easier or harder, redirect to the [L0602 lecture](L0602_lecture.md) slide 1.5.
>
> The labs map to the L06 subgoals: **L0604** → describe the spec / connect-discover mechanics by
> translating and validating a tool spec; **L0607** → decide when MCP is worth the overhead.

## L0604_lab problem 1 — Translate inline -> MCP tool spec

- **Common gotchas:** rewriting or "improving" the schema contents instead of carrying them over
  unchanged (the whole point is that they *don't* change); using snake_case `inputschema` or leaving it
  as `input_schema` (MCP specs use camelCase `inputSchema`); dropping `name` or `description`.
- **Unblockers:** "Return `{'name': ..., 'description': ..., 'inputSchema': inline['input_schema']}`.
  The only change is the key name on the schema — copy everything else verbatim."
- **Time:** ~6 min.
- **Key point:** the translation is a key rename. That it's *this trivial* is the lesson — the design
  surface is identical across packagings.

## L0604_lab problem 2 — Prove the design surface survives

- **Common gotchas:** comparing `json.dumps` strings (key order can differ) instead of the dict objects;
  asserting against the wrong key on one side.
- **Unblockers:** "Three asserts: `mcp_spec['inputSchema'] == BOOK_MEETING_INLINE['input_schema']`, and
  the same for `name` and `description`. Dict `==` is fine — no need to stringify."
- **Time:** ~4 min.
- **Key point:** this is the [lecture](L0602_lecture.md) slide 2.2 claim, checked mechanically rather
  than asserted in prose.

## L0604_lab problem 3 — Round-trip back to inline

- **Common gotchas:** not reversing the rename (returning `inputSchema` again); reordering keys and then
  expecting `==` to fail (dict equality ignores order, so this still passes — reassure the student).
- **Unblockers:** "Mirror Problem 1: `input_schema` <- `spec['inputSchema']`. `mcp_spec_to_inline(mcp_spec)`
  must equal the original `BOOK_MEETING_INLINE`."
- **Time:** ~4 min.
- **Key point:** lossless *both* directions is *why* the tool is portable — a client can consume a
  discovered spec or publish an inline one with no information loss.

## L0604_lab problem 4 — Validate a discovered spec

- **Common gotchas:** using truthiness on a missing key and hitting `KeyError` (use `.get(...)`);
  checking only the name and forgetting the `inputSchema['type'] == 'object'` rule; returning a bare
  `False` instead of an informative `REJECTED: ...` string (the whole L05 lesson is that errors should
  *say why*).
- **Unblockers:** "Three guards in order: empty `name` -> reject; empty `description` -> reject;
  `inputSchema` not a dict or its `type` != `'object'` -> reject; else `'OK'`. Use `spec.get('name')`
  so a missing key doesn't crash." Expected: good=OK, the other three each REJECTED with a reason.
- **Time:** ~8 min.
- **Key point:** a client discovers specs it did *not* write (ownership moved to the server author), so
  validating the structure before trusting it is the cross-process analogue of L04's
  "the application validates."

## L0604_lab problem 5 — Why is the description load-bearing? (written)

- **Common gotchas:** "it documents the tool for developers" — backwards; the description is for the
  *model's* selection step, and for an MCP server it is published to *every* connecting client.
- **Unblockers:** expected: the published `description` is read by **every connecting model on every
  conversation** — it becomes runtime system prompt for every agent that uses the server, owned by the
  server author (lecture slide 2.3). An inline description is read by one agent's model; an MCP one is
  read by all of them. Tie to L05's *more tools ≠ more capable agent* — a flabby server description
  taxes every client.
- **Time:** ~4 min.

## L0607_lab problem 1 — The cost/benefit ledger (written)

- **Common gotchas:** listing benefits as costs or vice versa; conflating "extra process" and
  "transport" into one item (they're distinct operational costs).
- **Unblockers:** expected costs (any reasonable subset of the five): extra process to run; a transport
  to keep healthy; a versioning surface (server vs client); a wider debugging surface (failure on
  either side); a deployment story. Benefits (the four): portability (one server, many clients);
  separation of concerns (tool author ≠ agent author); discoverability (clients introspect); a security
  boundary (own credentials/permissions). See [lecture](L0602_lecture.md) slide 5.2.
- **Time:** ~5 min.
- **Key point:** the asymmetry — costs are immediate and roughly fixed; benefits compound with the
  number of consumers. That asymmetry *is* the decision rule for the next problems.

## L0607_lab problem 2 — Encode the decision

- **Common gotchas:** wrong rule order (checking the consumer count before isolation, so a one-consumer
  secrets tool wrongly returns inline); using `<` instead of `<=` for the single-consumer guard;
  forgetting that a tight loop can still have multiple consumers (the loop rule must come *after* the
  consumer-count rule and only fire for >1 consumer).
- **Unblockers:** "Four guards in order: `needs_isolation` -> MCP; `consumers <= 1` -> inline;
  `tight_loop` -> inline; else MCP." Walk them through *why* isolation is first (it's a benefit only the
  cross-process split can buy, regardless of consumer count).
- **Time:** ~8 min.
- **Key point:** the decision keys on the **number of consumers** more than anything else, with
  isolation and latency as overrides. This is the [lecture](L0602_lecture.md) section 5 logic in code.

## L0607_lab problem 3 — Build the decision table

- **Common gotchas:** an f-string formatting slip with the boolean columns (cast to `str` before
  width-aligning); re-deriving the verdict by hand instead of calling `recommend(s)`.
- **Unblockers:** "Loop the scenarios; print `recommend(s)` alongside the fields. Don't hand-judge —
  call your function." Expected verdicts down the table: inline, MCP, inline, MCP.
- **Time:** ~5 min.

## L0607_lab problem 4 — The gradient: a tool gains a consumer (written)

- **Common gotchas:** treating the original `inline` verdict as permanent; not connecting the flip to
  the consumer-count rule from Problem 2.
- **Unblockers:** expected: with a second consumer, `consumers` goes 1 -> 2, so the single-consumer
  guard no longer fires and (absent a tight loop) `recommend` flips to **MCP**. It's a *gradient*
  because the right answer moves with the situation — many tools start inline and graduate to MCP when
  reuse appears (lecture slide 5.4). The decision is revisited, not locked.
- **Time:** ~4 min.

## L0607_lab problem 5 — Push back on premature MCP (written)

- **Common gotchas:** agreeing with the teammate because MCP "sounds professional" — exactly the trap
  the lecture warns against.
- **Unblockers:** expected one-liner: **complexity that buys nothing is just complexity; inline is the
  right default until a second consumer appears.** Exposing every tool over MCP pays the full cost
  ledger for tools that have no portability benefit to earn it back (lecture slide 5.4).
- **Time:** ~3 min.
- **Stretch (for fast finishers):** add a `consumers=2, tight_loop=True, needs_isolation=True` scenario
  and have them predict the verdict *before* running it (isolation wins -> MCP), reinforcing the
  rule-ordering point.
