# MCP: same tool, new packaging

```yaml
title: "MCP: same tool, new packaging"
keywords: mcp, model context protocol, portable tool contract, tool spec, discovery, transport, stdio, client, server, inline tool, packaging
estimated duration: 10
```

> **Lesson:** L09 — MCP: packaging tools as a portable contract.
> **Roadmap:** see this lesson's [objectives.md](../../../../docs/origin/lesson_roadmaps/L09/objectives.md).
> This is a short framing piece. Read it before the written reference lecture
> ([L0602_lecture.md](L0602_lecture.md)), the offline spec-translation demo
> ([L0603_lecture.ipynb](L0603_lecture.ipynb)), the connect-to-a-server slide outline
> ([L0605_lecture.md](L0605_lecture.md)), and the build-a-server walkthrough
> ([L0606_lecture.ipynb](L0606_lecture.ipynb)).
> **Anchor model throughout: Claude Sonnet 4.6** (same anchor as [L07](../L07/L0401_intro.md) / [L08](../L08/L0501_intro.md)).

## Where this lesson sits

[L07](../L07/objectives.md) taught the **mechanics** of a tool call — the `tool_use` / `tool_result`
round-trip, who runs what, and why the application validates. [L08](../L08/objectives.md) taught the
**design** of a good tool — naming, descriptions written for the model's eyes, tight schemas,
informative errors, named side effects. In both lessons the tool was a Python function living inside
**one process**: your code registered it, your code ran it when the model asked.

L09 changes exactly **one thing**: the *packaging*. The tool's implementation is still a Python
function with the same name, description, schema, and error shape. But now it sits behind a standard
wire protocol — the **Model Context Protocol (MCP)** — so the *same* tool can be discovered and called
by *any* MCP-compatible client without rewiring. A custom Python agent, an IDE plugin, and Claude
Desktop can all talk to one MCP server.

This is the first lesson where you cross a process boundary on purpose. That move is a feature (the
tool can crash, upgrade, or run with different permissions independently of the agent) and a tax (an
extra process to run, a transport to keep healthy, failures that can now happen on either side).

## The one idea, said five ways

If you remember nothing else from L09, remember this: **MCP changes where the tool lives and how it is
reached — not how it should be designed.** Said five ways, because students keep expecting MCP to do
more (or less) than it does:

1. MCP is a **protocol, not a framework**. It specifies how a client and server *talk* about tools.
   It does not prescribe an SDK, a language, or a hosting model. Any process that speaks the protocol
   on a supported transport is a valid MCP server.
2. **The L08 design lessons carry over wholesale.** A bad name, weak description, or loose schema is
   just as bad over MCP as inline. MCP makes a *well-designed* tool portable; it does not rescue a
   badly designed one.
3. **Discovery is the new capability.** With an inline tool, the agent author knows what tools exist
   at code-write time. With MCP, the client *asks* the server at connect time: "what tools do you
   expose?" The server's published tool list becomes an external API the server author owns.
4. **The model can't tell the difference.** From the model's seat, an MCP tool call is the same
   `tool_use` / `tool_result` round-trip as [L07](../L07/objectives.md). MCP is invisible to the
   model — it shows up only in the *client's* implementation and the *operator's* config.
5. **MCP earns its overhead when a second consumer appears.** One agent, one tool, one place — inline
   wins. The moment a different agent, team, or app wants the same tool, MCP's portability starts
   paying for its tax.

## Vocabulary this lesson lands

These terms recur whenever tools are packaged for reuse:

- **MCP (Model Context Protocol)** — an open protocol for a *client* and a *server* to talk about
  tools (and, beyond this lesson's scope, resources and prompts).
- **MCP server** — a process that *exposes* one or more tools over the protocol. Can be a 50-line
  Python script, not necessarily a microservice.
- **MCP client** — the agent or app that *connects* to a server, discovers its tools, and routes the
  model's tool calls to it.
- **Tool spec** — the on-the-wire description of a tool a server publishes: `name`, `description`,
  `inputSchema`. This is the [L08](../L08/objectives.md) design surface, serialized.
- **Discovery** — the handshake where a client asks a server for its tool list at connect time.
- **Transport** — *how* the bytes move between client and server. **stdio** (server is a child
  process the client launches and pipes to) and **HTTP/SSE** (server is a separate networked process)
  are the two you'll meet.

## A note on the code you'll see (read this carefully)

The official Python **`mcp` package is not installed in this course environment**, and we do not add
it. That has a deliberate consequence for how L09 is built:

- The **offline** material — the spec-translation demo ([L0903](L0603_lecture.ipynb)) and all three
  labs ([L0904](L0604_lab_empty.ipynb), [L0907](L0607_lab_empty.ipynb), and the validator lab) — uses
  **only the Python standard library** (`json`, `dataclasses`). It runs here, deterministically, with
  no API key and no `mcp` package. These labs work directly with the *tool spec* — the JSON shape that
  crosses the wire — which is the part of MCP you most need to understand.
- The material that genuinely needs a live MCP connection — **connecting to an existing server**
  ([L0905](L0605_lecture.md), a slide outline) and **building your own server**
  ([L0906](L0606_lecture.ipynb), a code walkthrough) — shows the real code but is **marked
  NOT-RUNNABLE without the `mcp` package**. You read it to see the wire shape and the server skeleton;
  you do not execute it in this environment. (If your local environment installs `mcp`, the code is
  written to run — but that is outside the course's pinned env.)

This split is intentional. The conceptual core of MCP — *a well-designed tool, serialized to a
portable spec, discovered and called across a process boundary* — is fully teachable offline. The live
connection is a demonstration of a thing you already understand on paper.

The one sentence to leave L09 with:

> *MCP takes a tool you already know how to design and serializes it to a portable spec, so any client
> that speaks the protocol can discover and call it — the design is unchanged; only the packaging and
> the boundary are new.*

Next: the written reference lecture in [L0602_lecture.md](L0602_lecture.md), then the offline
spec-translation demo ([L0903](L0603_lecture.ipynb)) and the connect/build walkthroughs
([L0905](L0605_lecture.md) / [L0906](L0606_lecture.ipynb)).
