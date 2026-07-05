# Connecting to an existing MCP server (wire-shape walkthrough)

```yaml
title: "Connecting to an existing MCP server (wire-shape walkthrough)"
keywords: mcp, client, connect, discovery, list_tools, call_tool, stdio, transport, handshake, tool spec, not-runnable, wire shape
estimated duration: 20
```

> **Lesson:** L09. **Roadmap:** Demo 2 in the [demos_or_activities.md](../../../../docs/origin/lesson_roadmaps/L09/demos_or_activities.md).
> A slide outline (teacher-presented) covering **connecting a client to an already-published MCP
> server** and reading the discovery handshake.
>
> **⚠️ NOT RUNNABLE in this environment.** The Python `mcp` package is **not installed** in the course
> env, so the code blocks below are shown for their **wire shape**, not for execution. Read them to see
> *what crosses the boundary*; do not try to run them here. (If your own environment has `mcp`
> installed — `uv add mcp` — the snippets are written to run; that's outside the pinned course env.)
> The fully-offline version of this idea is the [L0903 demo](L0903_lecture.ipynb) and the
> [L0904 lab](L0904_lab_empty.ipynb), which work with the same tool *spec* without a live connection.

## section 1. The one config change

### slide 1.1 Adding a server is config, not code

- Recall the [L0902 lecture](L0902_lecture.md) section 1 pain: each inline client needed tool-specific
  *integration code*. With MCP, adding a server is a **config entry**, not an integration.
- diagram: contrast — left, three boxes of per-client integration code (the inline world); right, a
  single small config block naming the server (the MCP world).
- The whole point of slide 1.1: the cost of "add this tool to my agent" drops from *write an
  integration* to *name a server*.

### slide 1.2 A stdio server config (shown, not run)

- For a local **stdio** server, the client config names the command that launches the server as a child
  process. This is the lowest-friction transport for local development.
- text: a representative config — the exact key names vary by client; the *shape* is what matters.

```python
# NOT-RUNNABLE here (no `mcp` package). Shown for wire shape only.
# A client config entry describing how to launch a local stdio MCP server.
server_config = {
    "command": "uv",
    "args": ["run", "python", "-m", "my_org.book_meeting_server"],
    "transport": "stdio",
}
```

- Note what is *absent*: any tool-specific code. The config says *how to start the server*, never *what
  tools it has* — the client learns the tools at connect time (section 2). Compare to an HTTP/SSE
  server, where the config would carry a URL instead of a launch command.

[↑ Back to top](#connecting-to-an-existing-mcp-server-wire-shape-walkthrough)

## section 2. The discovery handshake

### slide 2.1 Connect, then ask "what do you expose?"

- The client connects over the transport and issues a **list-tools** request. The server replies with
  its published tool specs. This is the step inline tools don't have — the client *discovers* the tool
  list instead of shipping with it.
- text: the connect-and-discover shape (pseudocode against a typical MCP client API).

```python
# NOT-RUNNABLE here (no `mcp` package). Shown for wire shape only.
async with connect_stdio(server_config) as session:
    await session.initialize()           # protocol handshake (version negotiation)
    listed = await session.list_tools()  # discovery: "what tools do you expose?"
    for tool in listed.tools:
        print(tool.name, "->", tool.description)
        print("  schema:", tool.inputSchema)
```

- The `tool.name`, `tool.description`, `tool.inputSchema` you get back are **exactly the L08 design
  surface**, serialized — the same fields the [L0903 demo](L0903_lecture.ipynb) translates offline.

### slide 2.2 What the discovery response looks like on the wire

- table: the shape of one tool entry in the discovery response — this is what every connecting model
  sees registered into its system prompt.

| Field | Example value | Comes from |
| --- | --- | --- |
| `name` | `"book_meeting"` | the L08 tool name |
| `description` | `"Book a meeting on the user's calendar. Use when the user asks to schedule…"` | the L08 description, written for the model |
| `inputSchema` | `{"type": "object", "properties": {…}, "required": ["attendee", "start"]}` | the L08 parameter schema (JSON Schema) |

- The teacher-narration point: the client now "knows about tools it did not ship with." Ownership of the
  tool list has moved to the **server author** (reinforce [L0902 lecture](L0902_lecture.md) slide 2.3).

[↑ Back to top](#connecting-to-an-existing-mcp-server-wire-shape-walkthrough)

## section 3. Calling a discovered tool end-to-end

### slide 3.1 The round-trip, with the MCP hop made explicit

- Once the specs are registered, the model emits an `AIMessage` with a tool call exactly as in
  [L07](../L07/objectives.md). The client routes it over the transport; the server runs the tool and
  returns a structured result; the client feeds it back as a `ToolMessage`.
- diagram: `model (AIMessage.tool_calls)` → `client routes over transport` → `server runs book_meeting`
  → `client wraps as ToolMessage` → `model (final answer)`. Steps 2–4 are the MCP hop; the model never
  sees them.
- text: the call shape (pseudocode).

```python
# NOT-RUNNABLE here (no `mcp` package). Shown for wire shape only.
# The client, having seen the model emit a tool call for "book_meeting" (AIMessage.tool_calls),
# forwards the call to the server and gets a structured result back.
result = await session.call_tool(
    name="book_meeting",
    arguments={"attendee": "priya@example.com", "start": "2026-06-16T14:00", "duration_minutes": 90},
)
print(result.content)  # the server's structured tool result, fed back to the model as a ToolMessage
```

### slide 3.2 The model can't tell it's MCP

- From the model's seat, this is the **same** `AIMessage.tool_calls` / `ToolMessage` exchange as
  [L07](../L07/objectives.md). MCP is invisible to it — it lives entirely in the client's routing and
  the operator's config.
- That invisibility is the proof of the abstraction: the model designed-for in L08 and the loop coming
  in [L10](../L10/objectives.md) both work *unchanged* whether the tool is inline or MCP-served.

[↑ Back to top](#connecting-to-an-existing-mcp-server-wire-shape-walkthrough)

## section 4. Failure modes on the wire

### slide 4.1 Stop the server, watch the boundary fail

- The teacher-demo move: stop the server process mid-conversation and re-issue the prompt. The client
  surfaces a **transport error** to the model — a failure mode an inline tool *cannot* have.
- table: the boundary-specific failures (mirrors [L0902 lecture](L0902_lecture.md) slide 3.4) and how
  the model reacts.

| Failure | What the client surfaces | Model reaction (L08 error classes) |
| --- | --- | --- |
| server not running | connection refused / no handshake | reports failure; can't recover without the operator |
| transport disconnect | mid-call error | **recoverable** — may retry; often resolves on restart |
| version mismatch | handshake rejected | **unrecoverable** — fix config, not retryable |
| missing server-side credential | the *tool result* is an auth error | **unrecoverable** for the model; operator must supply the key |

- Tie to [L08](../L08/objectives.md): the model treats a well-shaped error as new context exactly as
  before. The new thing is *where* the error can originate — now on either side of the wire.

### slide 4.2 Recovery is an operator action

- Restart the server, re-run the prompt — recovery. The lesson: cross-process tools add an
  **operational** dimension inline tools don't have. Someone has to keep the server alive.
- This operational tax is one row in the [L0902 lecture](L0902_lecture.md) section 5 cost ledger, made
  concrete: "a transport to keep healthy" is not abstract once you've watched a stopped server break a
  conversation.

[↑ Back to top](#connecting-to-an-existing-mcp-server-wire-shape-walkthrough)

## section 5. What carries forward

### slide 5.1 You read a discovery response; you traced a cross-process call

- After this walkthrough you can read a server's published tool list and predict what the model will
  see, and you can trace an `AIMessage.tool_calls` → transport → server → `ToolMessage` round-trip and
  name where it can fail.
- Next: [L0906](L0906_lecture.ipynb) shows the *other* side of the wire — **building** the server whose
  tools you just discovered (also shown, not run here). The offline [L0904 lab](L0904_lab_empty.ipynb)
  has you validate and translate the spec these handshakes exchange.

[↑ Back to top](#connecting-to-an-existing-mcp-server-wire-shape-walkthrough)
