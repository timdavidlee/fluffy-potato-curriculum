# L09: Teacher-led demos — MCP: packaging tools as a portable contract

> Sibling docs: [objectives.md](objectives.md) (what the lesson aims for), parent design [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md).
>
> **Audience for this file:** the teacher running L09. Every demo below is *teacher-driven, no student participation*. Student-driven exercises live in the L09 labs (separate file).

## How to read this file

Each demo is a self-contained block with:

- **Goal** — the single insight the demo should land. Tied to a learning objective from [objectives.md](objectives.md).
- **Pre-flight** — what the teacher needs loaded before class.
- **Live script** — the order of operations during the demo. Treat it as a checklist, not a teleprompter.
- **What to highlight** — the moment(s) where the teacher should slow down and call out the takeaway out loud.
- **If the demo misbehaves** — graceful fallback for when the model surprises you (because it will).

The demos are ordered to match the four learning objectives from [objectives.md](objectives.md). Demo 4 (trade-offs) is comparative and depends on Demos 2 and 3 having happened, so run the sequence in order on the first delivery of the lesson.

## Pre-flight (once, at the top of the lesson)

The teacher should have, before the first demo starts:

- A working REPL or notebook with the project's Claude SDK setup (per the project's `uv` env), the same trace-printing wrapper used in [L08's demos](../L08/demos_or_activities.md), and an additional MCP-aware client component. <!-- *NEED INPUT*: which MCP client anchors the demos and labs — the project's existing Python SDK with a small custom MCP-client wrapper, Claude Desktop, claude.ai's MCP support, or a published Python MCP-client library? Affects what "connect to an existing server" looks like in code. Mirrors the same open question in [objectives.md](objectives.md). -->
- A pre-installed and verified **existing MCP server** for Demo 2. <!-- *NEED INPUT*: which existing MCP server should the "connect to an existing server" subgoal target? Best guess: a small, well-known server with a tool or two the student can hit deterministically (a filesystem server, a fetch server, or a calculator-style toy server). The chosen server propagates into Demos 2 and 4. Mirrors the same open question in [objectives.md](objectives.md). -->
- A pre-built **minimal MCP server in Python** for Demo 3, exposing exactly one tool — reusing one of the well-designed tools from [L08's demos](../L08/demos_or_activities.md) (e.g. the tight-schema `book_meeting` from L08 Demo 3, or the `lookup_user_by_email` from L08 Demo 4) so students see the L08 design lessons port over unchanged. <!-- *NEED INPUT*: which Python library should the "build your own server" subgoal use? The official Python MCP SDK is the obvious answer; pin the exact package name and version once decided so labs can use `uv add`. Mirrors the same open question in [objectives.md](objectives.md). -->
- A second MCP client pre-configured and ready, *pointing at the same server from Demo 3*. The second client can be a different process running the project SDK, or the official MCP inspector, or Claude Desktop — whatever produces a visible "second consumer" for Demo 4. The point is to demonstrate portability live, not just describe it.
- A side-by-side display: the active MCP server's published tool list (rendered the way the discovery handshake would render it) on one panel, the model's tool-use request on another, the server-side log of the call on a third. Without this layout, the demos read as "stuff happened in another window" — the contrast across boundaries is the whole lesson.

> Why two clients pre-staged: the headline value of MCP is "one server, many clients." A demo that uses one client is just a wire-format demo. A demo that uses two clients against the same server is a *portability* demo — and that's what justifies the protocol.

<!-- *NEED INPUT*: which model class anchors the demos — likely the same as L08's choice; pin once both are settled. Mirrors the same open question in [objectives.md](objectives.md). -->

## Demo 1 — The pain MCP solves (Objective 1)

**Goal:** show the duplication that MCP eliminates. Land the framing from [objectives.md](objectives.md): *tools designed for one client require N integrations to be reused across N clients.*

**Pre-flight:**

- A small inline tool — reuse the `current_time(tz)` tool from [L08 Demo 1](../L08/demos_or_activities.md) — wired three different ways:
  - **Way A:** registered with the project's Claude Python SDK as an inline tool (the L08 way).
  - **Way B:** registered with a different mock client (a hand-written second SDK wrapper, or a deliberately different framework). The point is for the registration code to *look different* from Way A — different function signature, different schema syntax, different error contract.
  - **Way C:** a hypothetical third client described on a slide (e.g. "an IDE plugin," "Claude Desktop," "a coworker's agent"). The teacher narrates that this would require *yet another* integration.

  The three Ways do not need to be production code — they need to be visibly different so the duplication is unmistakable.

- A slide showing the same `current_time` tool spec from L08 (name, description, schema, return shape) at the top, with arrows pointing to three boxes labeled Way A, Way B, Way C — each box showing a *different* registration shape for the same underlying tool.

**Live script:**

1. Show the Way A registration code on screen. Run a model call that triggers the tool. Observe the call.
2. Show the Way B registration code side-by-side with Way A. Read aloud what's the same (the tool's purpose, name, description, schema) and what's different (the boilerplate around it). Run the same model call against Way B's client. Observe the call — same result, different glue code.
3. Pull up the slide for Way C and narrate: "Now imagine doing this every time a new client wants this tool." Quickly count: 3 clients × N tools = 3N integrations.
4. Pull up a slide showing the MCP shape: one server (the tool), N clients (each speaking the protocol). Same tool, registered once, consumed everywhere.

**What to highlight:**

- The duplication is *integration boilerplate*, not tool logic. The L08 tool design (name, description, schema, errors) is the same in every Way — only the wrapping changes. MCP makes the wrapping standard.
- The three things MCP standardizes from [objectives.md](objectives.md) — discovery, invocation, packaging. Name them as you transition from the duplication slide to the MCP shape slide.
- What MCP does *not* change: the L08 design pressures. This is critical. Repeat it explicitly so students don't think MCP makes design easier.
- MCP is a protocol, not a framework, not Anthropic-specific. The boxes in the "MCP shape" slide should make this visible — the clients can be from different vendors, different languages.

**If the demo misbehaves:**

- This demo is mostly narration over slides plus two live runs of the same tool against different clients. The risk is low. If a live run fails, fall back to the slide narrative — the duplication point lands without needing the live runs. Just don't skip showing both Way A and Way B side by side; the visual contrast is the demo.

## Demo 2 — Connecting to an existing MCP server (Objective 2)

**Goal:** show the discovery handshake and the cross-process round-trip end-to-end against a server the student did *not* write. Land the framing from [objectives.md](objectives.md): *discovery is the new capability — the client asks the server what it exposes.*

**Pre-flight:**

- The chosen existing MCP server installed and verified working with the chosen client. Run a smoke test the day of the lesson — server processes can rot, transports can break.
- A short, visible piece of client configuration that registers the server (e.g. a `mcp_servers.toml` snippet, a `claude_desktop_config.json` snippet, or a Python `MCPClient(...)` constructor call). Pre-load it; this is *not* the moment to live-edit JSON.
- A test prompt that the chosen server's tools can actually answer. <!-- *NEED INPUT*: confirm the prompt and the server pairing once the existing server is pinned. Example: if the server is a filesystem MCP, prompt with *"List the markdown files under docs/origin/."* If it is a fetch server, prompt with *"Fetch the title of example.com."* -->

**Live script:**

1. Show the client configuration on screen and read it aloud. Note: this is the only client-side change needed to add the server. Compare mentally to Demo 1's per-client integration burden — Way A and Way B both required tool-specific code; this is a config entry.
2. Start the client. Inspect the discovered tool list — the client's introspection output, or the project's wrapper that prints the discovered tools after handshake. Show that the client now knows about tools it didn't ship with.
3. Run the test prompt. Observe the trace: model emits a tool-use request → client routes the request to the MCP server over the chosen transport → server runs the tool → result returns through the client → model continues. Highlight each phase as it scrolls past.
4. Stop the MCP server process mid-conversation. Re-run the prompt. Observe the failure mode: the client surfaces a transport error to the model. Discuss what the model does next (usually reports the failure, sometimes retries — exactly the recoverable-error behavior from [L08](../L08/objectives.md), but at the transport layer this time).
5. Restart the server. Re-run. Recovery.

**What to highlight:**

- The *discovery* step is the new piece. Inline tools are known to the agent at code-write time; MCP tools are known at connect time. This shifts ownership of the tool list to the server author.
- The cross-process boundary's failure modes from [objectives.md](objectives.md) — server not running, transport disconnect, version mismatch, missing credentials. Demo 2 deliberately triggers the first to make it visible.
- The model doesn't care that the tool is over MCP. From the model's perspective, it received a tool-use result (or an error) just like in [L07](../L07/objectives.md). MCP is invisible to the model — it shows up only in the *client's* implementation and the *operator's* config.

**If the demo misbehaves:**

- If the existing server fails its smoke test on the day, fall back to a *local* mock MCP server pre-built by the teacher that exposes one trivial tool (a static "ping" returning "pong"). The point is the handshake and round-trip, not the specific server's output. Have the mock ready in reserve.
- If the deliberate "stop the server" step takes too long to recover, narrate the failure and skip the restart — Demo 4 will revisit failure modes in the trade-off discussion.

## Demo 3 — Building your own MCP server (Objective 3)

**Goal:** show that a tool the student has already seen designed (in L08) can be repackaged as an MCP server with no design changes — and watch a client discover and call it. Land the framing from [objectives.md](objectives.md): *the L08 design lessons carry over wholesale.*

**Pre-flight:**

- A pre-built minimal MCP server in Python (≤100 lines, ideally less) that exposes one of the L08 well-designed tools — recommended: the tight-schema `book_meeting` tool with informative validation errors from [L08 Demo 3](../L08/demos_or_activities.md), since its design surface (typed parameters, per-field constraints, structured errors) showcases what carries across the boundary.
- The L08 inline version of the same tool open in a side-by-side editor pane. Annotate (in the slide deck or on screen) the parts that are *identical* across the two: the name, the description, the parameter list with descriptions, the constraint set, the error shape. Annotate the parts that are *different*: the registration boilerplate (a function decorator vs. a server-startup call), the transport (in-process call vs. stdio), the entry point (none vs. a `__main__` block).
- The same client from Demo 2 reconfigured to also point at this new local server (so both the existing server *and* the new server are available — but only the new one is exercised in this demo).
- The same test prompt from [L08 Demo 3](../L08/demos_or_activities.md): *"Book a 90-minute design review with Priya next Tuesday afternoon."*

**Live script:**

1. Show the L08 inline tool and the new MCP server side by side. Walk through the diff: highlighted lines for what's identical (design surface), highlighted lines for what's different (packaging). The visual should make the "design unchanged, packaging changed" point obvious.
2. Start the new MCP server process. Show the server-side log — `Tool 'book_meeting' registered. Listening on stdio.` (or equivalent for the chosen transport).
3. From the client, trigger the discovery handshake against the new server. Show the discovered tool spec — name, description, schema. It should be visibly the same spec the L08 demo registered inline.
4. Run the prompt. Observe the same recovery behavior students saw in [L08 Demo 3](../L08/demos_or_activities.md): the model submits a partial call, gets back a structured validation error naming the missing email field, and on the next turn either asks the user or tries again with a synthesized address.
5. Force a deliberate Python exception inside the tool implementation (e.g. by passing a duration of `999999`). Show that — if the server is well-built — the exception is caught and returned as a structured tool result, not a transport-level crash. If it crashes the server instead, treat that as the teaching moment: this is exactly the cross-process error-shaping discipline from [objectives.md](objectives.md).

**What to highlight:**

- Same tool, same model, same prompt, same recovery behavior — even though the tool now lives in a separate process and reaches the model through MCP. The L08 design discipline is doing the work; MCP is just moving the bytes.
- The server author owns the published tool list. Anything in the description is what every connecting model will see in its system prompt at the start of every conversation. (Back-reference [L08](../L08/objectives.md): *"more tools ≠ more capable agent"* — this applies to MCP server authors too. Don't dump 20 tools into one server.)
- The `__main__` block / startup is small — an MCP server is not a microservice unless you make it one. The whole thing is a script with a wire protocol. Don't let students inflate the implementation in their heads.

**If the demo misbehaves:**

- If the server fails to start (port conflict, transport setup error), fall back to the inline L08 version of the same tool to confirm the model behavior is what students remember from L08, then narrate what the MCP version *would* show. The design-portability point still lands.
- If the validation-error path in step 4 doesn't trigger (model happens to fill in the email correctly), use the duration-out-of-range path or rerun with a vaguer prompt. The point is the structured error round-trip, not the specific field.

## Demo 4 — When to MCP, when to stay inline (Objective 4)

**Goal:** show the trade-off live by exercising the same tool both ways and then connecting a *second* client to the MCP version. Land the framing from [objectives.md](objectives.md): *MCP is most valuable when there is a second consumer.*

**Pre-flight:**

- The L08 inline version and the Demo 3 MCP version of the same `book_meeting` tool, both functional, both wired to the same primary client.
- A *second* MCP client (the one staged in pre-flight) pointing at the same Demo 3 MCP server.
- The trace wrapper extended to also print wall-clock time per call, so the inline-vs-MCP latency difference is numerically visible.
- A whiteboard or slide listing the costs and benefits from [objectives.md](objectives.md) subgoal 4 (costs: extra process, transport, versioning, debugging, deployment; benefits: portability, separation of concerns, discoverability, security boundary). The teacher will tick items off as they appear in the demo.

**Live script:**

1. Run the L08 prompt against the *inline* version. Note wall-clock latency. Mark the costs at "zero" — no extra process, no transport.
2. Run the same prompt against the *MCP* version through the primary client. Note wall-clock latency. The MCP path is typically slightly slower (transport overhead, especially over stdio cold-start). Tick the cost columns: extra process (yes), transport (yes), debugging surface (yes — failure can now happen on either side).
3. Now bring up the *second* client. Without writing any tool code, point the second client at the same MCP server. Run a prompt from the second client that triggers the same tool. Observe: it just works.
4. Tick the benefit columns: portability (yes — the second client added the tool with config alone, not code), separation of concerns (yes — the tool author and the second client author could be different people), discoverability (yes — second client introspected the server's tool list).
5. Walk through the three example scenarios from [objectives.md](objectives.md):
   - **One-off in a single script.** Inline wins. The cost columns are non-zero, the benefit columns are zero (no second consumer).
   - **Multi-client tool (today's demo!).** MCP wins. Costs are paid, benefits are realized.
   - **Latency-sensitive tight-loop tool.** Show the per-call latency from steps 1–2 and discuss: if a tool is called 50 times per turn, the overhead compounds. Inline often wins here on overhead, but MCP may still win on packaging if the latency budget allows.

**What to highlight:**

- The *gradient* point from [objectives.md](objectives.md): many tools start inline and graduate to MCP when a second consumer appears. The decision is not permanent, and the right answer depends on the *number of consumers* more than any other factor.
- Costs are real and immediate. Benefits compound with the number of consumers. The break-even point is somewhere between one and many — for a one-off, it's "many"; for a tool that *will* be reused, it's "now."
- A common student temptation is to reach for MCP early because it sounds more "professional." Push back: complexity that buys nothing is just complexity. Inline is the right default until reuse appears.

**If the demo misbehaves:**

- If the second client fails to connect (config drift, transport mismatch), narrate what *would* happen and use the slide of the cost/benefit matrix to make the point. The portability claim does not require a flawless live demo to be persuasive; the architecture of "one server, two clients" is convincing on its own.
- If the latency comparison in step 2 doesn't show a meaningful gap (well-warmed stdio, fast machine), don't fake one — say so explicitly and note that the latency cost can be small in practice but compounds at scale.

## Optional bridge demo — toward L10 (hand-rolled agent loop)

If time allows, run one final demo that previews [L10](../L10/objectives.md) (when its roadmap exists): take the existing model→tool→model round-trip from this lesson and gesture at the *loop* version — the same wiring, but with the model continuing to call tools across multiple turns until it decides to stop. Show that whether the tool is inline (L08) or MCP-served (L09) is irrelevant to the loop's structure; both plug in identically. Don't teach the loop here — that's L10. Just show the indifference.

<!-- *NEED INPUT*: include this bridge demo, or save it as the opener for L10? -->

## Pacing notes for the teacher

- **Per-demo time:** Demo 1 is ~10 minutes (mostly narration + two short runs). Demos 2 and 3 are ~15 minutes each (live wiring, multiple steps, cross-process moving parts). Demo 4 is ~15 minutes (comparative — needs setup time but is mostly observational). Total fits a 60–80 minute block, plus the optional bridge. <!-- *NEED INPUT*: confirm against the lesson-time budget once duration is pinned in [objectives.md](objectives.md)'s open questions. -->
- **Variance budget:** the cross-process boundary adds new failure modes. Budget for one server restart per demo. If a transport flakes, narrate the recovery — students will see this same flake when they do the lab, so seeing the teacher recover gracefully is itself instructive.
- **The audience watches, doesn't participate.** Resist the temptation to ask "what should this MCP server expose?" — that is a lab pattern, not a demo pattern. Hands-on practice is for the L09 labs.
- **Keep the same tool across Demos 3 and 4.** Reusing the L08 `book_meeting` tool across demos lets students focus on the *packaging* changing, not the tool. Don't introduce a new tool for variety.
- **Smoke-test all servers the day of the lesson.** MCP servers are processes, processes rot, and a failed connection mid-demo eats time the lesson does not have.

## Open authoring questions

- <!-- *NEED INPUT*: which MCP client anchors the demos and labs — the project's existing Python SDK with a small custom MCP-client wrapper, Claude Desktop, claude.ai's MCP support, or a published Python MCP-client library? Affects what "connect to an existing server" looks like in code. Mirrors the same open question in [objectives.md](objectives.md). -->
- <!-- *NEED INPUT*: which existing MCP server should the "connect to an existing server" subgoal target? Best guess: a small, well-known server with a tool or two the student can hit deterministically (a filesystem server, a fetch server, or a calculator-style toy server). The chosen server propagates into Demos 2 and 4. Mirrors the same open question in [objectives.md](objectives.md). -->
- <!-- *NEED INPUT*: which Python library should the "build your own server" subgoal use? The official Python MCP SDK is the obvious answer; pin the exact package name and version once decided so labs can use `uv add`. Mirrors the same open question in [objectives.md](objectives.md). -->
- <!-- *NEED INPUT*: should L09 cover MCP **resources** and **prompts** (the other two primitives in the protocol) or scope strictly to **tools**? The PRD subgoals only mention tools, so the safest default is "tools only, with resources and prompts as a one-paragraph mention and a forward link." Mirrors the same open question in [objectives.md](objectives.md). -->
- <!-- *NEED INPUT*: should L09 introduce authentication / credentials / secrets handling for MCP servers, or defer to a later lesson? Best guess: defer the deep dive but mention it as a real concern in Demo 4's trade-off discussion — security is one of the genuine reasons the cross-process boundary is valuable. Mirrors the same open question in [objectives.md](objectives.md). -->
- <!-- *NEED INPUT*: which model class anchors the L09 demos — likely the same as L08's choice, but pin once both are settled. Mirrors the same open question in [objectives.md](objectives.md). -->
- <!-- *NEED INPUT*: do the L09 demo tools share an implementation with the L09 lab tools, or are lab tools designed from scratch by students? Recommend reusing Demo 3's `book_meeting` MCP server as the lab starting point, since the L08 version is already familiar. -->
- <!-- *NEED INPUT*: a pointer/link to where the demo MCP server code lives (a `demos/` subdir? an `mcp_servers/` subdir?) — not yet decided in non-draft docs. -->
