# L06: MCP — packaging tools as a portable contract

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (lesson-plan row L06).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).

## Where this lesson sits

[L05](../L05/objectives.md) taught how to *design* a good tool: naming, descriptions written for the model's eyes, tight schemas, informative errors, named side effects. Everything in L05 was framed inside one Python process: the tool was a function the runtime called directly when the model requested it.

L06 changes the *packaging*. The tool's implementation might still be a Python function, but it now sits behind a standard wire protocol — the **Model Context Protocol (MCP)** — so that the same tool can be discovered and called by *any* MCP-compatible client without rewiring. Claude Desktop, claude.ai, an IDE plugin, and a custom Python agent can all talk to the same MCP server.

This is the first lesson where the student crosses a process boundary on purpose. The L05 design lessons survive the move unchanged — a poorly designed MCP tool is still a poorly designed tool — but new questions appear: how does the client discover what tools the server exposes, what does the transport cost, and when is the portability worth it?

L06 is the last lesson before L07 (hand-rolled agent loop), where the student builds the model→tool→model loop in plain Python. L07 will need a tool to call; the student should be able to choose between an inline tool (L05) and an MCP-served tool (L06) based on the trade-offs L06 establishes.

## Prerequisites

Students arriving at L06 should already be able to:

- Decide when a tool is needed vs. model-alone, and design a tool's name, description, and parameter schema for an LLM consumer (L05, objective 1 and 2).
- Write a tool description aimed at the model with enough detail that the model can pick it correctly without external context (L05, objective 2).
- Distinguish validation, recoverable, and unrecoverable errors and shape error responses informatively (L05, objective 3).
- Wire a single tool to a model call and trace one tool-call round-trip (L04, prerequisite from L05).
- Run a simple Python process from the command line and reason about stdio (basic Python literacy, per the CURRICULUM_PRD's "basic python familiarity" assumption).

If a student is shaky on the L05 design principles, redirect to the L05 lab before continuing. L06 builds on those principles rather than re-teaching them.

## Learning objectives

By the end of L06, a student should be able to:

1. **Describe the problem MCP solves.** Concretely:
   - Name the pain MCP addresses: tools designed for one client (a single Claude SDK app, a specific IDE plugin, a custom agent) require N separate integrations to be reused across N clients. Each client has its own way to register tools, its own credential handling, its own tool-call format.
   - Identify the three things MCP standardizes across clients: tool **discovery** (a client can ask "what tools do you expose?"), tool **invocation** (a client can call any tool with the same wire shape), and tool **packaging** (a tool author publishes one server; many clients consume it).
   - Recognize what MCP does *not* change: the design pressures from L05 are identical. A bad name, weak description, or loose schema is just as bad over MCP as inline.
   - Place MCP correctly in the stack: it sits *between* the client (the agent or app the user runs) and the tool implementation (a server process). It is not a model feature, not an SDK feature, not an Anthropic-specific feature — it's an open protocol.

2. **Connect to an existing MCP server from a client.** Concretely:
   - Configure an MCP-aware client (the project's chosen client — see open question below) to talk to an already-published MCP server. Recognize the two common transports a student will encounter: **stdio** (server is a child process the client launches and pipes to) and **HTTP/SSE** (server is a separate process the client connects to over the network).
   - Walk through the discovery handshake conceptually: the client connects, asks the server what tools and resources it exposes, and registers them as available to the model. Be able to read a server's published tool list and predict what the model will see.
   - Invoke at least one tool from the server through the client end-to-end and read the resulting trace: model emits a tool-use request, the client routes it to the MCP server, the server runs the tool, the result comes back through the client to the model.
   - Recognize the failure modes specific to the cross-process boundary: server not running, transport disconnect, version mismatch between client and server, credentials missing on the server side.

3. **Expose a simple tool as an MCP server.** Concretely:
   - Build a minimal MCP server in Python that exposes one tool with a well-designed name, description, schema, and error shape — applying every L05 design principle unchanged.
   - Choose a transport (stdio is the lowest-friction default for local development) and run the server so a local MCP client can discover and call the tool.
   - Verify the round-trip: connect the client, see the tool appear in the discovery response, call it through the model, observe the result.
   - Apply L05's error-shaping principles to the cross-process case: a Python exception in the server should not propagate as a transport-level error; it should be caught and returned as a structured tool result the model can interpret.

4. **Decide when MCP is worth the overhead vs. an inline tool.** Concretely:
   - Name the costs MCP adds: an extra process to run and manage, a transport to keep healthy, a versioning surface (server vs. client), a debugging step (failures can now happen on either side of the wire), and a deployment story (the server has to live somewhere).
   - Name the benefits MCP adds: portability (one server, many clients), separation of concerns (tool authors and agent authors can be different people or teams), discoverability (clients can introspect), and a security boundary (the tool process can run with different credentials and permissions than the client).
   - Apply the trade-off on at least three example scenarios:
     - A one-off tool used inside a single Python script — inline almost always wins.
     - A tool that should be available to multiple agents and to Claude Desktop — MCP wins.
     - A latency-sensitive tool called many times per turn (e.g. inside a tight inner loop) — inline often wins on overhead, MCP may still win on packaging if latency budget allows.
   - Recognize the *gradient*: many tools start inline and graduate to MCP once a second consumer appears. The decision is not permanent.

## Main points the lecture should land

- **MCP is a protocol, not a framework.** It specifies how a client and a server talk about tools, resources, and prompts. It does not prescribe an SDK, a language, or a hosting model. Any process that speaks the protocol on a supported transport is a valid MCP server. This matters because students should not conflate "MCP" with whatever specific Python library the lab happens to use.
- **The L05 design lessons carry over wholesale.** Every L05 principle — descriptions written for the model, tight schemas, informative errors, named side effects — applies one-to-one to MCP tools. MCP changes *where* the tool lives and *how* it is reached; it does not change *how it should be designed*. A common student mistake is to think MCP makes design easier or harder; it does neither.
- **Discovery is the new capability.** Inline tools are registered by the application code that owns them — the agent author knows what tools exist. With MCP, the client *asks* the server at connect time. This shifts the surface area: the server's published tool list (and the descriptions on each tool) is now an external API the server author owns. Treat it like one.
- **The cross-process boundary is a feature and a tax.** It is a feature because it gives you isolation — the tool process can crash without taking the agent down, can run with different permissions, can be replaced or upgraded independently. It is a tax because every call now crosses a boundary, errors can happen on either side, and you have one more thing to deploy. The decision in subgoal 4 is fundamentally about whether the feature is worth the tax for *this* tool.
- **MCP is most valuable when there is a second consumer.** A tool used by exactly one agent in exactly one place is poorly served by MCP — the protocol's value comes from reuse. The moment a second consumer appears (a different agent, a different team, an IDE plugin, Claude Desktop), the MCP version's portability starts paying for its overhead. Encourage students to think about *future* consumers when making the call, not just present ones — but not so far in the future that they pay the tax for hypothetical reuse that never arrives.
- **Discovery and selection are still the model's job.** MCP makes more tools *available*; it does not make the model better at picking the right one. A server that exposes 20 tools to every connecting client is a server that floods every client's system prompt with 20 tool descriptions, dilutes the model's attention, and increases the wrong-tool failure rate (back-reference [L05](../L05/objectives.md): *"more tools ≠ more capable agent."*). Server authors should curate their published tool surface as carefully as inline tool authors curate theirs.

## Common student confusions to watch for

- *"MCP is a Claude thing."* It is an open protocol. Many clients and many servers exist, written in many languages, used by many models. The lab uses Python and Claude because the rest of the course does, not because MCP is tied to either.
- *"MCP replaces tool design."* It does not — it is *purely* a packaging and transport layer. All of L05 still applies. Students who skip L05 and go straight to MCP build well-packaged tools the model can't use well.
- *"If MCP is portable, I should always use it."* Portability has a cost (the cross-process tax). For one-off tools the cost dominates. The trade-off in subgoal 4 is real.
- *"The transport choice is technical detail, not a design choice."* Transport affects deployment, latency, and failure modes. stdio is great for local development and bad for shared services; HTTP/SSE is the reverse. Choosing wrong is recoverable but annoying.
- *"An MCP server is a microservice."* It can be deployed like one, but it can also be a 50-line Python script launched as a child process. Don't let the protocol's shape inflate the implementation in students' minds — start small.
- *"The server's published tool descriptions are a static doc."* They are read by every connecting model on every conversation. They are part of the runtime system prompt of every agent that uses the server. Treat them with the care L05 prescribes for any tool description.

## Bridge to L07

L07 builds a hand-rolled agent loop — model→tool→model in plain Python. The loop needs *some* set of tools to call. Students arriving at L07 will be able to choose between an inline tool from L05 and an MCP-served tool from L06, and should be able to defend the choice using subgoal 4's trade-offs. L07 will use the simpler of the two (likely inline) for the core teaching, but the L07 lab can optionally swap in an MCP tool to show the loop is indifferent to where the tool lives — which is itself a validation of MCP's value proposition.

## Open authoring questions

- <need input: estimated lecture duration — best guess 75–90 minutes as one lecture covering all four subgoals plus a live "connect to an existing server" walkthrough. Or split into two: protocol + connecting (subgoals 1–2), then building + trade-offs (subgoals 3–4)?>
- <need input: which MCP client anchors the demos and labs — the project's existing Python SDK with a small custom MCP-client wrapper, Claude Desktop, claude.ai's MCP support, or a published Python MCP-client library? Affects what "connect to an existing server" looks like in code.>
- <need input: which existing MCP server should the "connect to an existing server" subgoal target? Best guess: a small, well-known server with a tool or two the student can hit deterministically (a filesystem server, a fetch server, or a calculator-style toy server). The chosen server propagates into demos and labs.>
- <need input: which Python library should the "build your own server" subgoal use? The official Python MCP SDK is the obvious answer; pin the exact package name and version once decided so labs can use `uv add`.>
- <need input: should L06 cover MCP **resources** and **prompts** (the other two primitives in the protocol) or scope strictly to **tools**? The PRD subgoals only mention tools, so the safest default is "tools only, with resources and prompts as a one-paragraph mention and a forward link."  >
- <need input: should L06 introduce authentication / credentials / secrets handling for MCP servers, or defer to a later lesson? Best guess: defer the deep dive but mention it as a real concern in the trade-off subgoal — security is one of the genuine reasons the cross-process boundary is valuable.>
- <need input: any specific L05 labs that must be completed before this lesson is taught, beyond the prerequisite skills above?>
- <need input: which model class anchors the L06 demos — likely the same as L05's choice, but pin once both are settled.>
