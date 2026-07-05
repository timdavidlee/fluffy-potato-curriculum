# MCP: the portable tool contract, the boundary, and when it pays

```yaml
title: "MCP: the portable tool contract, the boundary, and when it pays"
keywords: mcp, model context protocol, tool spec, discovery, invocation, packaging, transport, stdio, http sse, cross-process boundary, portability, inline tool, trade-off, server, client
estimated duration: 80
```

> **Lesson:** L09. **Roadmap:** [objectives.md](../../../../docs/origin/lesson_roadmaps/L09/objectives.md).
> This is the written reference lecture — thorough on purpose, so a student who missed the verbal
> delivery can rebuild the lesson from the page. The offline spec-translation demo is
> [L0903](L0903_lecture.ipynb); connecting to an existing server is the slide outline
> [L0905](L0905_lecture.md); building your own server is the code walkthrough
> [L0906](L0906_lecture.ipynb). Hands-on practice is in the L09 labs (L0904 / L0907, plus the validator
> lab). **Anchor model throughout: Claude Sonnet 4.6.**
>
> **Environment note:** the Python `mcp` package is **not installed** in this course env. Everything in
> this lecture that involves a *live* MCP connection is shown as code/wire-shape for reading, not for
> running here. The tool-spec mechanics (sections 1–3) are fully exercisable offline.

## section 1. The problem MCP solves

### slide 1.1 N clients, N integrations

- A tool you designed in [L08](../L08/objectives.md) — say `book_meeting` — is a Python function plus
  a tool definition. To make it usable, you *register* it with a client: the Anthropic SDK in
  [L07](../L07/objectives.md) wanted `tools=[{...}]`; a different framework wants a decorator; an IDE
  plugin wants its own config; Claude Desktop wants a JSON entry.
- Each client has its **own** way to register tools, its **own** credential handling, its **own**
  tool-call format. The *tool* is the same; the *glue* is different every time.
- The pain, stated precisely: **a tool designed for one client requires N separate integrations to be
  reused across N clients.** Three clients × five tools = fifteen integrations, all hand-maintained.
- diagram: one `book_meeting` tool box at the top with three arrows down to three differently-shaped
  "registration" boxes labeled "Anthropic SDK", "other framework", "IDE plugin" — same tool, three
  different wrappers.

### slide 1.2 The duplication is glue, not logic

- Look closely at those N integrations and the **tool logic is identical** in all of them: the same
  `book_meeting(attendee, start, duration_minutes)` function, the same name, the same description, the
  same schema, the same error shape. Only the *wrapping* — how the client wants to be told about the
  tool — changes.
- This is the key observation MCP is built on: if the wrapping is the only thing that varies, then
  **standardize the wrapping** and the duplication disappears.
- Back-reference [L08](../L08/objectives.md): the design surface (name / description / schema / error)
  is exactly the part that *should* stay constant. MCP freezes a standard envelope around it.

### slide 1.3 The three things MCP standardizes

- table: the three capabilities MCP makes uniform across every client.

| MCP standardizes | Meaning | Inline-tool equivalent (the thing it replaces) |
| --- | --- | --- |
| **Discovery** | a client can ask a server "what tools do you expose?" | the agent author hard-codes the tool list |
| **Invocation** | any tool is called with the *same* wire shape | each client has its own call format |
| **Packaging** | a tool author publishes *one* server; many clients consume it | each client re-integrates the tool itself |

- Say it as a chant: **discover, invoke, package.** Those are the three nouns MCP owns. Everything else
  about your tool — what it does, how it's named, what it returns — is unchanged.

### slide 1.4 Where MCP sits in the stack

- MCP sits **between** the client (the agent or app the user runs) and the tool implementation (a
  server process). It is *not* a model feature, *not* an SDK feature, *not* Anthropic-specific. It is
  an open protocol.
- diagram: a vertical stack — `model` at top, then `client (agent/app)`, then a labeled wire
  `← MCP →`, then `server (tool implementation)`. The model and the server never touch directly; the
  client brokers everything.
- Common confusion to retire now: *"MCP is a Claude thing."* It is an open protocol with many clients
  and many servers, written in many languages, used by many models. This course uses Python and Claude
  because the rest of the course does — not because MCP is tied to either.

### slide 1.5 What MCP does *not* change

- MCP changes the **packaging and the transport**. It does **not** change the [L08](../L08/objectives.md)
  design pressures. A bad name is still bad; a loose schema is still loose; a bare-stack-trace error is
  still useless — now over a wire instead of in-process.
- A common student mistake is to think MCP makes design *easier* or *harder*. It does **neither**. The
  design work from L08 is identical; MCP just decides where the bytes go afterward.
- This is the single most repeated point in the lesson. If a student leaves thinking "MCP replaces tool
  design," the lesson failed.

[↑ Back to top](#mcp-the-portable-tool-contract-the-boundary-and-when-it-pays)

## section 2. The tool spec: your L08 design, serialized

### slide 2.1 A tool spec is the L08 design surface on the wire

- When a client discovers a server, what it gets back per tool is a **tool spec**: a `name`, a
  `description`, and an `inputSchema` (JSON Schema). That is *literally* the [L08](../L08/objectives.md)
  design surface — name, description-for-the-model, parameter schema — serialized to JSON.
- table: the L08 design lever and where it lands in an MCP tool spec.

| L08 design lever | MCP tool spec field | Unchanged? |
| --- | --- | --- |
| Tool name (chosen for the model) | `name` | identical |
| Description written for the model's eyes | `description` | identical |
| Tight parameter schema (types, required, enums, per-field descriptions) | `inputSchema` (JSON Schema) | identical |
| Error shape (informative `{error, field, message}`) | returned in the tool *result*, your code shapes it | identical |

- The point this table makes visible: **there is nothing new to design.** If you did L08 well, the spec
  writes itself.

### slide 2.2 The inline definition and the MCP spec are near-identical

- The Anthropic inline tool definition from [L07](../L07/objectives.md) and an MCP tool spec are almost
  the same JSON. The only routine difference you'll see is the schema field name: Anthropic's inline
  format calls it `input_schema`; MCP's spec calls it `inputSchema`. The *contents* — the JSON Schema —
  are identical.
- diagram: two JSON blocks side by side for the same `book_meeting` tool — left labeled "L07 inline
  definition (`input_schema`)", right labeled "MCP tool spec (`inputSchema`)" — with every line
  identical except the one renamed key, which is highlighted.
- The offline demo [L0903](L0903_lecture.ipynb) does this translation in code, both directions, and
  asserts the JSON Schema survives the move byte-for-byte. The [L0904 lab](L0904_lab_empty.ipynb) has
  you validate and translate a spec yourself — pure Python, no `mcp` package, no model.

### slide 2.3 The published tool list is an external API

- With an inline tool, the agent author owns the tool list — it's in their code. With MCP, the
  **server author** owns it: the list every connecting client discovers is published *by the server*,
  at connect time, into every model's system prompt.
- So the server's tool descriptions are no longer "comments in my code." They are **runtime system
  prompt for every agent that connects.** Treat them with the [L08](../L08/objectives.md) care you'd
  give any tool description — because that's exactly what they are.
- Back-reference [L08](../L08/objectives.md): *"more tools ≠ more capable agent."* A server that
  exposes 20 tools to every client floods every client's prompt with 20 descriptions, dilutes the
  model's attention, and raises the wrong-tool failure rate. **Curate the published surface.**

[↑ Back to top](#mcp-the-portable-tool-contract-the-boundary-and-when-it-pays)

## section 3. Connecting to a server: discovery is the new step

### slide 3.1 Two transports you'll meet

- **Transport** is *how* the client and server move bytes. Two are common, and the choice is a **design
  decision**, not a throwaway detail — it affects deployment, latency, and failure modes.
- table: the two transports and where each fits.

| Transport | Shape | Good for | Bad for |
| --- | --- | --- | --- |
| **stdio** | server is a child process the client launches and pipes to over stdin/stdout | local development, single-user tools, lowest friction | shared services, remote access, many concurrent clients |
| **HTTP/SSE** | server is a separate (possibly remote) process the client connects to over the network | shared/remote services, multiple clients, independent deployment | a quick local script (more setup than it's worth) |

- Rule of thumb: **stdio for local development, HTTP/SSE for anything shared.** Choosing wrong is
  recoverable but annoying.

### slide 3.2 The discovery handshake

- Discovery is the genuinely new piece versus inline tools. The sequence at connect time:
  1. The client **connects** to the server over the chosen transport.
  2. The client **asks** "what tools (and resources, and prompts) do you expose?"
  3. The server **replies** with its published tool specs (`name`, `description`, `inputSchema` each).
  4. The client **registers** those specs as tools available to the model — they go into the system
     prompt just like an inline tool definition would.
- diagram: client → `list_tools` request → server; server → `[tool spec, tool spec, ...]` → client;
  client → "these are now available to the model".
- The shift in ownership is the lesson: inline tools are known to the agent at **code-write time**; MCP
  tools are known at **connect time**, and the *server* decides what's on the list.

### slide 3.3 The model can't tell it's MCP

- Once the specs are registered, the model emits an `AIMessage` with a tool call exactly as in
  [L07](../L07/objectives.md). The client notices the tool belongs to an MCP server and routes the call
  over the transport; the server runs the tool and returns a structured result; the client feeds that
  back to the model as a `ToolMessage`.
- table: the round-trip phases, now with the MCP hop made explicit.

| # | Who | What happens |
| --- | --- | --- |
| 1 | model | emits an `AIMessage` with a tool call (name + args + id) — same as L07 |
| 2 | **client** | recognizes the tool is MCP-served; sends the call over the transport |
| 3 | **server** | runs the tool function; returns a structured result |
| 4 | **client** | wraps the result as a `ToolMessage` (paired by `tool_call_id`) and continues the conversation |
| 5 | model | reads the `ToolMessage` and produces its final answer — same as L07 |

- The model's view is **identical to L07**. MCP is invisible to it — it lives entirely in steps 2–4,
  which are the *client's* job and the *operator's* config. The slide-outline lecture
  [L0905](L0905_lecture.md) walks the real connection code (shown, not run here).

### slide 3.4 New failure modes live on the wire

- The cross-process boundary adds failure modes inline tools simply can't have. Naming them now means
  you recognize them in a trace later.
- table: the boundary-specific failures and what they look like.

| Failure | Cause | What you see |
| --- | --- | --- |
| **Server not running** | you forgot to start it, or it crashed | connection refused / no handshake |
| **Transport disconnect** | pipe closed, network blip | mid-conversation error on the next call |
| **Version mismatch** | client and server speak different protocol versions | handshake rejected or degraded |
| **Missing credentials** | the *server* lacks a key the tool needs | the tool *result* is an auth error (not a transport error) |

- Tie back to [L08](../L08/objectives.md)'s error classes: a transport disconnect is a **recoverable**
  error (retry may work); a version mismatch is **unrecoverable** (fix config). The model treats a
  well-shaped error as new context exactly as before — the difference is the error can now originate on
  *either side of the wire*.

[↑ Back to top](#mcp-the-portable-tool-contract-the-boundary-and-when-it-pays)

## section 4. Building a server: the design is unchanged

### slide 4.1 A server is a small program, not a microservice

- A minimal MCP server is a script: define the tool function (your L08 design, unchanged), register it
  with a server object, pick a transport, and run. Tens of lines, not a deployment.
- Common confusion to retire: *"an MCP server is a microservice."* It *can* be deployed like one over
  HTTP/SSE, but it can equally be a 50-line Python script launched as a stdio child process. Don't let
  the protocol's shape inflate the implementation in your head — **start small.**
- The build walkthrough [L0906](L0906_lecture.ipynb) shows the full skeleton for `book_meeting`
  (reused from [L08](../L08/objectives.md)) — shown as code, **not run here** (no `mcp` package).

### slide 4.2 The diff: design identical, packaging changed

- Put the L08 inline `book_meeting` next to its MCP-server version and the diff is small and
  *all in the packaging*.
- table: what's identical vs. what's different across the two versions.

| Identical (the L08 design) | Different (the MCP packaging) |
| --- | --- |
| function name `book_meeting` | a server registration call / decorator instead of an inline `tools=[...]` entry |
| the description written for the model | a transport choice (in-process call → stdio) |
| the parameter schema (types, required, per-field descriptions) | an entry point (none → a `__main__` block that starts the server) |
| the error shape (`{error, field, message}`) | the result now crosses a process boundary as serialized JSON |

- The headline: **same tool, same model, same prompt, same recovery behavior** — even though the tool
  now lives in a separate process and reaches the model through MCP. The L08 design discipline does the
  work; MCP just moves the bytes.

### slide 4.3 Error-shaping must survive the boundary

- In-process, an uncaught exception is a stack trace your code can catch. **Across the boundary, an
  uncaught exception in the server can crash the server** — taking the tool offline mid-conversation,
  which is a transport-level failure, not a tool result the model can read.
- The discipline: **catch exceptions inside the tool and return them as a structured tool result**, the
  same [L08](../L08/objectives.md) `{error, field, message}` shape. The model gets actionable context;
  the server stays up.
- diagram: two paths from a `duration_minutes: 999999` call — top path: exception escapes → server
  crashes → client sees a transport error (bad); bottom path: server catches it → returns
  `{error: "validation", field: "duration_minutes", message: "must be 15–240"}` → model fixes its call
  (good).
- This is L08's error design, now load-bearing for *availability*, not just helpfulness.

### slide 4.4 You own the published surface

- Because the server author owns the published tool list (slide 2.3), building a server means **you**
  decide what every connecting model sees. Expose the one tool the server is *for*; resist the urge to
  bundle "just in case" tools.
- Back-reference [L08](../L08/objectives.md): a focused tool set is navigable; tool soup is not. A
  server is just a new place that same curation discipline applies.

[↑ Back to top](#mcp-the-portable-tool-contract-the-boundary-and-when-it-pays)

## section 5. When is MCP worth the overhead?

### slide 5.1 The cross-process boundary is a feature and a tax

- The boundary is a **feature**: isolation. The tool process can crash without taking the agent down,
  run with different permissions, and be replaced or upgraded independently.
- The boundary is a **tax**: every call crosses a wire, errors can happen on either side, and you have
  one more thing to deploy and keep healthy.
- Subgoal 4 is fundamentally one question: **is the feature worth the tax for *this* tool?**

### slide 5.2 The costs and benefits, named

- table: the ledger from [objectives.md](../../../../docs/origin/lesson_roadmaps/L09/objectives.md).

| Costs MCP adds | Benefits MCP adds |
| --- | --- |
| an extra process to run and manage | **portability** — one server, many clients |
| a transport to keep healthy | **separation of concerns** — tool authors ≠ agent authors |
| a versioning surface (server vs. client) | **discoverability** — clients introspect the tool list |
| a wider debugging surface (failure on either side) | a **security boundary** — the tool runs with its own credentials/permissions |
| a deployment story (the server has to live somewhere) | |

- The asymmetry to internalize: **costs are immediate and roughly fixed; benefits compound with the
  number of consumers.** That asymmetry *is* the decision rule.

### slide 5.3 Three scenarios, three answers

- table: apply the ledger to the three roadmap scenarios.

| Scenario | Verdict | Why |
| --- | --- | --- |
| A one-off tool used inside a single Python script | **inline wins** | costs are non-zero, benefits are zero — there's no second consumer |
| A tool that should serve multiple agents *and* Claude Desktop | **MCP wins** | costs are paid once, portability/discoverability benefits are realized N times |
| A latency-sensitive tool called many times per turn (tight inner loop) | **inline often wins** | per-call transport overhead compounds; MCP may still win *if* the latency budget allows and packaging matters |

- The middle row is the canonical MCP case. The outer rows are the cautionary ones: don't reach for MCP
  for a one-off (complexity that buys nothing), and weigh the overhead when latency is tight.

### slide 5.4 The decision is a gradient, not a gate

- Many tools **start inline and graduate to MCP** once a second consumer appears. The decision is *not
  permanent*, and it depends on the **number of consumers** more than any other factor.
- A common temptation is to reach for MCP early because it sounds more "professional." Push back:
  **inline is the right default until reuse appears.** Complexity that buys nothing is just complexity.
- Think about *near-future* consumers when you decide — but don't pay the tax now for hypothetical
  reuse that never arrives. The break-even is "one" for a tool you *know* will be reused and "many" for
  a one-off. The [L0907 lab](L0907_lab_empty.ipynb) has you encode this ledger as a small decision
  function and run it over example tools — pure Python, no `mcp` package.

### slide 5.5 A word on security and credentials

- One genuine reason the boundary is valuable: the server process can hold credentials the client never
  sees. The tool runs with *its own* permissions, so a compromised or buggy agent can't directly reach
  the tool's secrets.
- We **name** this as a real benefit but **defer** the deep dive (auth flows, secret storage) to later
  in the course. For L09, it's one item on the benefit side of the ledger, not a full topic.

[↑ Back to top](#mcp-the-portable-tool-contract-the-boundary-and-when-it-pays)

## section 6. Scope, confusions, and the bridge to L10

### slide 6.1 What L09 deliberately scopes out

- **Tools only.** MCP also standardizes *resources* and *prompts* (its two other primitives). L09
  scopes to **tools** because that's what the rest of the course needs; resources and prompts are a
  one-line mention and a forward pointer, not a topic here.
- **No deep auth.** Credentials are named as a benefit (slide 5.5), not taught as a mechanism.
- **No live connection in this environment.** The `mcp` package isn't installed in the course env, so
  the connect/build material is read as code and wire-shape, not executed here. The spec mechanics —
  the part you most need — are fully offline-exercisable.

### slide 6.2 The confusions, named

- table: the recurring L09 confusions and the one-line correction for each.

| Confusion | Correction |
| --- | --- |
| "MCP is a Claude thing." | It's an open protocol — many clients, many servers, many languages, many models. |
| "MCP replaces tool design." | It's purely packaging + transport. All of [L08](../L08/objectives.md) still applies. |
| "If MCP is portable, I should always use it." | Portability has a cost. For one-off tools the cost dominates — inline wins. |
| "Transport is a technical detail, not a design choice." | Transport drives deployment, latency, and failure modes. stdio ≠ HTTP/SSE in where they fit. |
| "An MCP server is a microservice." | It can be a 50-line script launched as a child process. Start small. |
| "The published tool descriptions are a static doc." | They're runtime system prompt for every connecting model. Curate them like any tool description. |

### slide 6.3 Bridge to L10

- [L10](../L10/objectives.md) builds a hand-rolled agent loop — model→tool→model in plain Python,
  across multiple turns until the model decides to stop. The loop needs *some* tools to call.
- The choice you can now defend: an **inline tool** ([L08](../L08/objectives.md)) or an **MCP-served
  tool** (L09), justified by section 5's trade-offs. L10 will likely use the simpler one (inline) for
  the core teaching — but the loop is *indifferent* to where the tool lives, and that indifference is
  itself a validation of MCP's value proposition.
- One sentence to L10: *you can now design a tool, package it for portability, and decide which packaging
  fits — next you'll put it in a loop and let the model call it until the task is done.*

[↑ Back to top](#mcp-the-portable-tool-contract-the-boundary-and-when-it-pays)
