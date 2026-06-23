"""The hand-rolled model -> tool -> model loop, instrumented to emit a trace.

This is the canonical reference copy of the loop students built inline in L07.
L07's loop *printed* one line per iteration — a "minimum-viable trace" that
vanished when the run ended. L08 keeps the **control flow identical** and adds
*observation*: a ``TraceEvent`` emitted at each boundary (before/after the model
call, around each tool dispatch, and a framing span for the whole run), collected
into ``RunResult.trace``.

The headline rule: **instrumentation is a wrapper, not a rewrite.** Tracing only
*observes* the loop; it never changes how the loop decides things. If adding a
trace ever changed the run's behavior, observation has leaked into control flow.

``run()`` works with any object exposing a ``create(...)`` method that returns a
response with ``content`` blocks — both ``anthropic.Anthropic().messages`` and the
offline :class:`~fluffy_potato_curriculum.common.fake_model.FakeModel` qualify.
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol

from .tracing import SpanUsage, TraceEvent

DEFAULT_MODEL = "claude-sonnet-4-6"
"""The course anchor model (Sonnet 4.6), so a trace of this loop matches the
behavior students saw in L07."""


class SupportsCreate(Protocol):
    """Anything with a ``create(...)`` returning a message-like object.

    The real ``anthropic.Anthropic().messages`` and the teaching ``FakeModel``
    both satisfy this — that interchangeability is what lets the same loop run
    live or offline.
    """

    def create(self, **kwargs: Any) -> Any: ...


class ToolCall(Protocol):
    """The shape of one ``tool_use`` block the loop reads (SDK block or fake).

    Declared with read-only properties so both a mutable SDK block and a frozen
    teaching block satisfy it — the loop only ever *reads* these.
    """

    @property
    def id(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def input(self) -> dict[str, Any]: ...


def _empty_trace() -> list[TraceEvent]:
    return []


@dataclass
class RunResult:
    """What the loop returns: the answer, how many model calls it took, why it
    stopped, and — new in L08 — the full ``trace`` the summary was derived from.

    You should be able to point at where each summary field came from in the
    trace: ``final_text`` is the last ``llm`` span's text, ``iterations`` is the
    count of ``llm`` spans, ``termination`` is on the ``chain`` span's outputs.
    """

    final_text: str
    iterations: int
    termination: str  # "natural" | "max_steps"
    trace: list[TraceEvent] = field(default_factory=_empty_trace)


def dispatch(tools: Mapping[str, Callable[..., str]], call: ToolCall) -> dict[str, Any]:
    """Run one requested tool and return a ``tool_result`` block.

    On success: a ``tool_result`` carrying the tool's output. On ANY exception
    (unknown tool name, or the tool raised): a ``tool_result`` with
    ``is_error=True`` and a SHORT message (``repr(exc)``) — never a traceback.
    The loop keeps going; the model decides what to do next.

    Example output (failure)::

        {"type": "tool_result", "tool_use_id": "c1",
         "content": "KeyError(\\"no population on file for 'Atlantis'\\")",
         "is_error": True}
    """
    fn = tools.get(call.name)
    if fn is None:
        return {
            "type": "tool_result",
            "tool_use_id": call.id,
            "content": f"no such tool {call.name!r}",
            "is_error": True,
        }
    try:
        output = fn(**call.input)
        return {"type": "tool_result", "tool_use_id": call.id, "content": output}
    except Exception as exc:
        # The loop turns ANY tool failure into a message, not a crash.
        # repr(exc) is a class name + one line, e.g. KeyError('no population...').
        # Short, descriptive, cheap -- never dump a traceback at the model.
        return {
            "type": "tool_result",
            "tool_use_id": call.id,
            "content": repr(exc),
            "is_error": True,
        }


def _new_id() -> str:
    return uuid.uuid4().hex


def _extract_usage(response: Any) -> SpanUsage | None:
    """Pull token counts off a response, if it reports any."""
    usage = getattr(response, "usage", None)
    if usage is None:
        return None
    return SpanUsage(input_tokens=usage.input_tokens, output_tokens=usage.output_tokens)


def run(
    model: SupportsCreate,
    tools: Mapping[str, Callable[..., str]],
    user_msg: str,
    max_steps: int = 8,
    *,
    tool_schemas: list[dict[str, Any]] | None = None,
    model_name: str = DEFAULT_MODEL,
) -> RunResult:
    """Run a model -> tool -> model loop until the model stops asking for tools.

    Each iteration: call the model; if it emitted ``tool_use`` blocks, run EVERY
    one, package ALL their ``tool_result``s into a single user-role message, and
    loop; if it emitted only text, return it (natural termination). The
    ``max_steps`` cap forces a halt even if the model still wants tools.

    Returns a :class:`RunResult` whose ``trace`` is the ordered list of spans
    emitted at the loop's boundaries (one ``chain`` span for the run, one ``llm``
    span per model call, one ``tool`` span per dispatch), all sharing a
    ``trace_id``.
    """
    trace_id = _new_id()
    events: list[TraceEvent] = []
    schemas: list[Any] = tool_schemas if tool_schemas is not None else list(tools)
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_msg}]

    final_text = ""
    termination = "max_steps"
    iterations = max_steps
    chain_start = time.time()

    for step in range(1, max_steps + 1):
        # --- the model call: one `llm` span ---
        llm_start = time.time()
        response = model.create(model=model_name, max_tokens=512, tools=schemas, messages=messages)
        llm_end = time.time()
        blocks: list[Any] = list(response.content)
        tool_uses = [block for block in blocks if block.type == "tool_use"]
        events.append(
            TraceEvent(
                run_id=_new_id(),
                trace_id=trace_id,
                run_type="llm",
                name="model.create",
                inputs={"messages": len(messages)},
                outputs={"tool_calls": [call.name for call in tool_uses]},
                usage=_extract_usage(response),
                start_time=llm_start,
                end_time=llm_end,
            )
        )

        # No tool_use block -> the model thinks it's done. NATURAL termination.
        if not tool_uses:
            final_text = "".join(block.text for block in blocks if block.type == "text")
            termination = "natural"
            iterations = step
            break

        # Record the assistant turn, then answer EVERY tool_use with a matching
        # tool_result in ONE user-role message before the next call.
        messages.append({"role": "assistant", "content": blocks})
        results: list[dict[str, Any]] = []
        for call in tool_uses:
            # --- the tool dispatch: one `tool` span ---
            tool_start = time.time()
            result = dispatch(tools, call)
            tool_end = time.time()
            is_error = bool(result.get("is_error"))
            events.append(
                TraceEvent(
                    run_id=_new_id(),
                    trace_id=trace_id,
                    run_type="tool",
                    name=call.name,
                    inputs=dict(call.input),
                    outputs={"content": result["content"]},
                    error=result["content"] if is_error else None,
                    start_time=tool_start,
                    end_time=tool_end,
                )
            )
            results.append(result)
        messages.append({"role": "user", "content": results})

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
