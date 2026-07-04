"""The hand-rolled model -> tool -> model loop, instrumented to emit a trace.

This is the canonical reference copy of the loop students built inline in L10.
L10's loop *printed* one line per iteration — a "minimum-viable trace" that
vanished when the run ended. L12 keeps the **control flow identical** and adds
*observation*: a ``TraceEvent`` emitted at each boundary (before/after the model
call, around each tool dispatch, and a framing span for the whole run), collected
into ``RunResult.trace``.

The headline rule: **instrumentation is a wrapper, not a rewrite.** Tracing only
*observes* the loop; it never changes how the loop decides things. If adding a
trace ever changed the run's behavior, observation has leaked into control flow.

The loop drives a **LangChain chat model** the standard way — ``model.bind_tools(...)``
then ``.invoke(messages)`` -> an ``AIMessage`` whose ``.tool_calls`` say which tools
to run. Any ``bind_tools``-capable model (``ChatAnthropic``, ``ChatOpenAI``, an
``init_chat_model(...)`` handle, or the offline
:class:`~fluffy_potato_curriculum.common.fake_model.FakeModel`) satisfies it — that
interchangeability is what makes the loop provider-agnostic and lets it run live or
offline unchanged.
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol, cast

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.messages.tool import ToolCall

from .tracing import SpanUsage, TraceEvent

DEFAULT_MODEL = "anthropic:claude-sonnet-4-6"
"""The course anchor as an ``init_chat_model`` identifier (provider:model). Swap
the provider prefix (e.g. ``"openai:gpt-..."``) and the same loop runs unchanged —
that is the point of driving the model through LangChain."""


class _BoundModel(Protocol):
    """A tool-bound chat model: ``.invoke(messages)`` -> a message.

    The message parameter is positional-only so both a real LangChain runnable
    (whose first arg is ``input``) and the teaching ``FakeModel`` (``messages``)
    satisfy it structurally regardless of the name they give it.
    """

    def invoke(self, messages: list[BaseMessage], /) -> BaseMessage: ...


class ChatModel(Protocol):
    """Anything with ``.bind_tools(...)`` returning an invokable model.

    A real LangChain chat model and the teaching ``FakeModel`` both satisfy this —
    that interchangeability is what lets the same loop run live or offline.
    """

    def bind_tools(self, tools: Sequence[Any], /) -> _BoundModel: ...


def _empty_trace() -> list[TraceEvent]:
    return []


@dataclass
class RunResult:
    """What the loop returns: the answer, how many model calls it took, why it
    stopped, and — new in L12 — the full ``trace`` the summary was derived from.

    You should be able to point at where each summary field came from in the
    trace: ``final_text`` is the last ``llm`` span's text, ``iterations`` is the
    count of ``llm`` spans, ``termination`` is on the ``chain`` span's outputs.
    """

    final_text: str
    iterations: int
    termination: str  # "natural" | "max_steps"
    trace: list[TraceEvent] = field(default_factory=_empty_trace)


def dispatch(tools: Mapping[str, Callable[..., str]], call: ToolCall) -> ToolMessage:
    """Run one requested tool and return a ``ToolMessage`` carrying the result.

    On success: a ``ToolMessage`` (``status="success"``) with the tool's output. On
    ANY failure (unknown tool name, or the tool raised): a ``ToolMessage`` with
    ``status="error"`` and a SHORT message (``repr(exc)``) — never a traceback. The
    ``tool_call_id`` matches the call so the model can pair result to request. The
    loop keeps going; the model decides what to do next.

    Example output (failure)::

        ToolMessage(content="KeyError(\\"no population on file for 'Atlantis'\\")",
                    tool_call_id="c1", status="error")
    """
    fn = tools.get(call["name"])
    if fn is None:
        return ToolMessage(
            content=f"no such tool {call['name']!r}",
            tool_call_id=call["id"] or "",
            status="error",
        )
    try:
        output = fn(**call["args"])
        return ToolMessage(content=output, tool_call_id=call["id"] or "", status="success")
    except Exception as exc:
        # The loop turns ANY tool failure into a message, not a crash.
        # repr(exc) is a class name + one line, e.g. KeyError('no population...').
        # Short, descriptive, cheap -- never dump a traceback at the model.
        return ToolMessage(content=repr(exc), tool_call_id=call["id"] or "", status="error")


def _new_id() -> str:
    return uuid.uuid4().hex


def extract_usage(message: AIMessage) -> SpanUsage | None:
    """Pull token counts off a reply, if it reports any.

    Shared with the graph producer (:mod:`.agent_graph`) so an ``llm`` span carries
    the same token accounting whether a loop or a graph produced it."""
    usage = message.usage_metadata
    if usage is None:
        return None
    return SpanUsage(input_tokens=usage["input_tokens"], output_tokens=usage["output_tokens"])


def text_of(message: AIMessage) -> str:
    """The plain-text answer of a reply, whether ``content`` is a string or blocks.

    Shared with the graph producer (:mod:`.agent_graph`)."""
    if isinstance(message.content, str):
        return message.content
    parts: list[str] = []
    for block in message.content:
        if isinstance(block, str):
            parts.append(block)
        elif block.get("type") == "text":  # a content block dict, e.g. {"type": "text", ...}
            parts.append(str(block.get("text", "")))
    return "".join(parts)


def run(
    model: ChatModel,
    tools: Mapping[str, Callable[..., str]],
    user_msg: str,
    max_steps: int = 8,
) -> RunResult:
    """Run a model -> tool -> model loop until the model stops asking for tools.

    Each iteration: invoke the tool-bound model; if the reply carried ``tool_calls``,
    run EVERY one, append a ``ToolMessage`` per call, and loop; if it carried only
    text, return it (natural termination). The ``max_steps`` cap forces a halt even
    if the model still wants tools.

    Returns a :class:`RunResult` whose ``trace`` is the ordered list of spans
    emitted at the loop's boundaries (one ``chain`` span for the run, one ``llm``
    span per model call, one ``tool`` span per dispatch), all sharing a
    ``trace_id``.
    """
    trace_id = _new_id()
    events: list[TraceEvent] = []
    bound = model.bind_tools(list(tools.values()))
    messages: list[BaseMessage] = [HumanMessage(content=user_msg)]

    final_text = ""
    termination = "max_steps"
    iterations = max_steps
    chain_start = time.time()

    for step in range(1, max_steps + 1):
        # --- the model call: one `llm` span ---
        llm_start = time.time()
        reply = cast(AIMessage, bound.invoke(messages))
        llm_end = time.time()
        events.append(
            TraceEvent(
                run_id=_new_id(),
                trace_id=trace_id,
                run_type="llm",
                name="model.invoke",
                inputs={"messages": len(messages)},
                outputs={"tool_calls": [call["name"] for call in reply.tool_calls]},
                usage=extract_usage(reply),
                start_time=llm_start,
                end_time=llm_end,
            )
        )

        # No tool calls -> the model thinks it's done. NATURAL termination.
        if not reply.tool_calls:
            final_text = text_of(reply)
            termination = "natural"
            iterations = step
            break

        # Record the assistant turn, then answer EVERY tool call with a matching
        # ToolMessage before the next model invocation.
        messages.append(reply)
        for call in reply.tool_calls:
            # --- the tool dispatch: one `tool` span ---
            tool_start = time.time()
            result = dispatch(tools, call)
            tool_end = time.time()
            is_error = result.status == "error"
            events.append(
                TraceEvent(
                    run_id=_new_id(),
                    trace_id=trace_id,
                    run_type="tool",
                    name=call["name"],
                    inputs=dict(call["args"]),
                    outputs={"content": result.content},
                    error=cast(str, result.content) if is_error else None,
                    start_time=tool_start,
                    end_time=tool_end,
                )
            )
            messages.append(result)

    # The framing `chain` span goes first so a reader sees the run summary up top.
    events.insert(
        0,
        TraceEvent(
            run_id=trace_id,
            trace_id=trace_id,
            run_type="chain",
            name="agent_loop.run",
            inputs={"user_msg": user_msg},
            outputs={"termination": termination, "iterations": iterations},
            start_time=chain_start,
            end_time=time.time(),
        ),
    )
    return RunResult(
        final_text=final_text,
        iterations=iterations,
        termination=termination,
        trace=events,
    )
