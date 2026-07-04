"""Trace the **L10 ReAct graph** — the same trace contract, a different producer.

L10 no longer teaches a hand-rolled ``while`` loop; it teaches a cyclic
``StateGraph`` — an ``agent`` node, a ``route`` conditional edge, a prebuilt
``ToolNode``, and the ``tools -> agent`` back-edge that makes it a cycle. This
module is the canonical reference copy of *that* graph (the role
:mod:`~fluffy_potato_curriculum.common.agent_loop` and
:mod:`~fluffy_potato_curriculum.common.tools` play for the plain loop) **plus** a
producer that runs the compiled graph and returns the very same
:class:`~fluffy_potato_curriculum.common.agent_loop.RunResult` L12 reads and L13
scores.

The headline: **keep the trace *schema*, swap the *producer*.** ``agent_loop.run``
emits a span at each boundary of a by-hand loop; this module reads the *same*
ordered ``list[TraceEvent]`` off ``graph.stream(stream_mode="updates")`` instead —
the exact stream students already watched in L03/L10, now captured. Each
``{node: update}`` chunk becomes a span:

- one ``chain`` span framing the whole run;
- one ``llm`` span per ``agent``-node visit (its ``AIMessage`` reply);
- one ``tool`` span per ``ToolNode`` dispatch (one per ``ToolMessage``).

Because it returns the identical ``RunResult`` shape, :mod:`.evals`,
``tool_trajectory``, and every L13 scorer keep working against a graph run with no
changes — the trace is the stable seam, the graph is now what fills it.
"""

# pyright: reportUnknownMemberType=false
# LangGraph's StateGraph *builder* methods (`add_node`, `compile`, `stream`) are
# pervasively partially-typed upstream (their own signatures leak `Unknown`), which
# trips pyright-strict's reportUnknownMemberType at every call site. This module is the
# canonical wrapper around that builder, so we relax *only* that one rule *only* here —
# every other strict guarantee (including on our own values) stays in force.

from __future__ import annotations

import time
import uuid
from collections.abc import Callable, Mapping
from typing import Annotated, Any, TypedDict, cast

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.messages.tool import ToolCall
from langchain_core.runnables import RunnableLambda
from langgraph.errors import GraphRecursionError
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

# Reuse the plain loop's return type and its message-reading helpers so a graph run
# is indistinguishable from a loop run downstream: evals.py does
# `from .agent_loop import RunResult`, so returning the SAME class is what keeps
# every L13 scorer (which types `run: RunResult`) accepting a graph-produced run.
from .agent_loop import ChatModel, RunResult, extract_usage, text_of
from .tools import TOOLS
from .tracing import TraceEvent


class AgentState(TypedDict):
    """The agent's state: one growing message list.

    The ``add_messages`` reducer **appends** each node's messages to the running
    conversation (in the L04 DAGs a returned key *overwrote* it) — that append is
    why the history grows turn by turn, and it is the invariant every node upholds.
    """

    messages: Annotated[list[BaseMessage], add_messages]


def build_agent(
    model: ChatModel,
    tools: Mapping[str, Callable[..., str]] = TOOLS,
    *,
    handle_tool_errors: bool = True,
) -> CompiledStateGraph[AgentState, Any, Any, Any]:
    """Wire and compile the L10 ReAct graph: agent node + ToolNode + route + back-edge.

    ``model`` is any ``bind_tools``-capable chat model (the offline
    :class:`~fluffy_potato_curriculum.common.fake_model.FakeModel`, ``ChatAnthropic``,
    …). ``tools`` is the shared name -> function table; its *values* are handed to
    both ``model.bind_tools(...)`` and the ``ToolNode``. ``handle_tool_errors`` is
    passed straight through to ``ToolNode`` so a raised tool exception comes back as
    a ``ToolMessage(status="error")`` the back-edge hands to the model, rather than
    crashing the run (L10, rule 3).
    """
    tool_list = list(tools.values())
    bound = model.bind_tools(tool_list)

    def agent_node(state: AgentState) -> dict[str, list[BaseMessage]]:
        """Call the tool-bound model on the conversation; return its one reply to append."""
        reply = bound.invoke(state["messages"])
        return {"messages": [reply]}

    async def aagent_node(state: AgentState) -> dict[str, list[BaseMessage]]:
        """The awaitable twin of ``agent_node``: ``await bound.ainvoke(...)``.

        Giving the node both a sync and an async body (below, via ``RunnableLambda``)
        is what lets the *same* compiled graph be driven by ``graph.stream`` (which
        calls the node's sync ``invoke``) or ``graph.astream`` (which awaits its
        ``ainvoke``) — so one ``build_agent`` backs both :func:`trace_graph` and
        :func:`atrace_graph`.
        """
        reply = await bound.ainvoke(state["messages"])
        return {"messages": [reply]}

    def route(state: AgentState) -> str:
        """Conditional edge: got tool calls? -> the tools node; else -> END (natural stop)."""
        last = state["messages"][-1]
        if isinstance(last, AIMessage) and last.tool_calls:
            return "tools"
        return END

    builder = StateGraph(AgentState)
    # A dual-mode node: `agent_node` serves sync `.stream`, `aagent_node` serves
    # async `.astream`. The prebuilt `ToolNode` is already dual-mode (it runs sync
    # tools in a thread under `.astream`), so the whole graph runs either way.
    builder.add_node("agent", RunnableLambda(agent_node, afunc=aagent_node))
    builder.add_node("tools", ToolNode(tool_list, handle_tool_errors=handle_tool_errors))
    builder.set_entry_point("agent")
    # The conditional exit (route) and the plain back-edge -- the only two edges.
    builder.add_conditional_edges("agent", route, {"tools": "tools", END: END})
    builder.add_edge("tools", "agent")  # the back-edge -- this is what makes it a cycle
    return builder.compile()


def _new_id() -> str:
    return uuid.uuid4().hex


def _recursion_limit(max_steps: int) -> int:
    """Translate ``max_steps`` (model calls) into a graph ``recursion_limit`` (node visits).

    The loop counted ``max_steps`` *model* calls; the graph counts *super-steps*
    (node visits), and one full model->tool round is two — the ``agent`` node then
    the ``tools`` node. So ``2 * max_steps`` node visits lets the graph make exactly
    ``max_steps`` ``agent`` visits *and* dispatch each one's tools (matching the
    loop, which dispatches the final step's tools before its cap trips) before the
    next ``agent`` visit would exceed the cap and raise ``GraphRecursionError``. That
    makes the graph's cap fire at the same model-call count the loop's ``max_steps``
    did — so ``termination == "max_steps"`` means the same thing across both.
    """
    return 2 * max_steps


def _llm_span(reply: AIMessage, trace_id: str, start: float, end: float) -> TraceEvent:
    """One ``llm`` span for an ``agent``-node visit — the node's model reply."""
    return TraceEvent(
        run_id=_new_id(),
        trace_id=trace_id,
        run_type="llm",
        name="agent",  # the graph node; in the trace, node = span
        inputs={},
        outputs={"tool_calls": [call["name"] for call in reply.tool_calls]},
        usage=extract_usage(reply),
        start_time=start,
        end_time=end,
    )


def _tool_span(
    result: ToolMessage,
    call: ToolCall | None,
    trace_id: str,
    start: float,
    end: float,
) -> TraceEvent:
    """One ``tool`` span for a ``ToolNode`` dispatch.

    ``result`` is the ``ToolMessage`` the ToolNode produced; ``call`` is the
    matching ``ToolCall`` recovered from the preceding ``agent`` reply (by
    ``tool_call_id``), which is where the tool *arguments* live — a ``ToolMessage``
    carries only the result, not the args the model chose.
    """
    is_error = result.status == "error"
    name = call["name"] if call is not None else (result.name or "tool")
    args = dict(call["args"]) if call is not None else {}
    content = result.content if isinstance(result.content, str) else str(result.content)
    return TraceEvent(
        run_id=_new_id(),
        trace_id=trace_id,
        run_type="tool",
        name=name,
        inputs=args,
        outputs={"content": content},
        error=content if is_error else None,
        start_time=start,
        end_time=end,
    )


def trace_graph(
    graph: CompiledStateGraph[AgentState, Any, Any, Any],
    user_msg: str,
    *,
    max_steps: int = 8,
) -> RunResult:
    """Run a compiled L10 graph and capture its run as a :class:`RunResult`.

    Streams the graph with ``stream_mode="updates"`` and turns each ``{node:
    update}`` chunk into a span: an ``agent`` chunk -> one ``llm`` span, a ``tools``
    chunk -> one ``tool`` span per ``ToolMessage`` in it. Termination mirrors the
    loop's vocabulary: a clean stream end (``route`` returned ``END``) is
    ``"natural"``; hitting the ``recursion_limit`` raises ``GraphRecursionError``,
    which we catch and report as ``"max_steps"`` — the same cause, in the same word,
    as the plain loop's cap.

    ``max_steps`` is the number of model calls to allow before the cap fires (see
    :func:`_recursion_limit`).
    """
    trace_id = _new_id()
    events: list[TraceEvent] = []
    # id -> the ToolCall that requested it, so a tool span can recover the args the
    # model chose (a ToolMessage carries only the result). Refreshed each agent turn.
    pending: dict[str, ToolCall] = {}

    final_text = ""
    iterations = 0
    termination = "natural"

    wall_start = time.time()
    last_t = wall_start
    stream = graph.stream(
        {"messages": [HumanMessage(content=user_msg)]},
        {"recursion_limit": _recursion_limit(max_steps)},
        stream_mode="updates",
    )
    try:
        for raw_chunk in stream:
            chunk = cast(dict[str, dict[str, Any]], raw_chunk)
            now = time.time()
            for node_name, update in chunk.items():
                messages = cast(list[BaseMessage], update.get("messages", []))
                if node_name == "agent":
                    reply = cast(AIMessage, messages[-1])
                    iterations += 1
                    pending = {call["id"] or "": call for call in reply.tool_calls}
                    events.append(_llm_span(reply, trace_id, last_t, now))
                    # A reply with no tool calls is the model stopping -> route -> END.
                    if not reply.tool_calls:
                        final_text = text_of(reply)
                elif node_name == "tools":
                    for message in messages:
                        tool_message = cast(ToolMessage, message)
                        call = pending.get(tool_message.tool_call_id)
                        events.append(_tool_span(tool_message, call, trace_id, last_t, now))
            last_t = now
    except GraphRecursionError:
        # The cap caught a runaway, not the model -- same meaning as the loop's max_steps.
        termination = "max_steps"

    # The framing `chain` span goes first so a reader sees the run summary up top.
    events.insert(
        0,
        TraceEvent(
            run_id=trace_id,
            trace_id=trace_id,
            run_type="chain",
            name="agent_graph.run",
            inputs={"user_msg": user_msg},
            outputs={"termination": termination, "iterations": iterations},
            start_time=wall_start,
            end_time=time.time(),
        ),
    )
    return RunResult(
        final_text=final_text,
        iterations=iterations,
        termination=termination,
        trace=events,
    )


async def atrace_graph(
    graph: CompiledStateGraph[AgentState, Any, Any, Any],
    user_msg: str,
    *,
    max_steps: int = 8,
) -> RunResult:
    """The ``await``-able twin of :func:`trace_graph` — same spans, streamed with
    ``graph.astream``.

    Line-for-line :func:`trace_graph` with the one change that makes it async:
    ``async for chunk in graph.astream(...)`` instead of ``for chunk in
    graph.stream(...)``. ``astream`` awaits the ``agent`` node's ``ainvoke`` (the
    run's only real I/O), so a caller can overlap several graph runs with
    ``asyncio.gather``; each ``{node: update}`` chunk maps to the identical span,
    so the returned :class:`RunResult` is indistinguishable from the sync path's.
    """
    trace_id = _new_id()
    events: list[TraceEvent] = []
    pending: dict[str, ToolCall] = {}

    final_text = ""
    iterations = 0
    termination = "natural"

    wall_start = time.time()
    last_t = wall_start
    stream = graph.astream(
        {"messages": [HumanMessage(content=user_msg)]},
        {"recursion_limit": _recursion_limit(max_steps)},
        stream_mode="updates",
    )
    try:
        async for raw_chunk in stream:
            chunk = cast(dict[str, dict[str, Any]], raw_chunk)
            now = time.time()
            for node_name, update in chunk.items():
                messages = cast(list[BaseMessage], update.get("messages", []))
                if node_name == "agent":
                    reply = cast(AIMessage, messages[-1])
                    iterations += 1
                    pending = {call["id"] or "": call for call in reply.tool_calls}
                    events.append(_llm_span(reply, trace_id, last_t, now))
                    if not reply.tool_calls:
                        final_text = text_of(reply)
                elif node_name == "tools":
                    for message in messages:
                        tool_message = cast(ToolMessage, message)
                        call = pending.get(tool_message.tool_call_id)
                        events.append(_tool_span(tool_message, call, trace_id, last_t, now))
            last_t = now
    except GraphRecursionError:
        termination = "max_steps"

    events.insert(
        0,
        TraceEvent(
            run_id=trace_id,
            trace_id=trace_id,
            run_type="chain",
            name="agent_graph.run",
            inputs={"user_msg": user_msg},
            outputs={"termination": termination, "iterations": iterations},
            start_time=wall_start,
            end_time=time.time(),
        ),
    )
    return RunResult(
        final_text=final_text,
        iterations=iterations,
        termination=termination,
        trace=events,
    )


def run(
    model: ChatModel,
    tools: Mapping[str, Callable[..., str]],
    user_msg: str,
    max_steps: int = 8,
) -> RunResult:
    """Build the L10 graph for ``model``/``tools`` and trace one run of it.

    A drop-in for :func:`agent_loop.run` — same ``(model, tools, user_msg,
    max_steps)`` signature and same :class:`RunResult` return — so a lesson can swap
    which *producer* backs a run by changing only the import, while every scorer and
    trace reader downstream stays put.
    """
    graph = build_agent(model, tools)
    return trace_graph(graph, user_msg, max_steps=max_steps)


async def arun(
    model: ChatModel,
    tools: Mapping[str, Callable[..., str]],
    user_msg: str,
    max_steps: int = 8,
) -> RunResult:
    """The ``await``-able twin of :func:`run`: build the L10 graph and
    :func:`atrace_graph` one run of it — a drop-in for :func:`agent_loop.arun`."""
    graph = build_agent(model, tools)
    return await atrace_graph(graph, user_msg, max_steps=max_steps)
