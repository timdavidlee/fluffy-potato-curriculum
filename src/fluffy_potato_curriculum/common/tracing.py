"""Structured tracing for a hand-rolled agent loop (the L11 teaching artifact).

A **trace** is the durable, structured record of what an agent run did: every
model call, tool call, and the loop step itself, captured as an ordered list of
typed **spans** so you can read the run *after the fact* instead of re-running a
non-deterministic agent to guess what happened.

The `TraceEvent` model is a deliberately *approximate* match to the OpenTelemetry
span model that Langfuse ingests — close enough that a student who opens Langfuse
(or any OTel-based tracer) finds the same structure, and close enough that
exporting over OTLP is a natural step. It is intentionally not an exact SDK
schema. The vocabulary lines up with the tools students meet later:

- OpenTelemetry calls one entry a **span**; Langfuse calls it an **observation**
  (an ``llm`` span renders as a *GENERATION*, a ``tool``/``chain`` span as a
  *SPAN*); LangSmith calls it a **run**. We say **span** in prose.

This module is imported by L11 (which instruments the loop), and reused by L12
(evaluation reads ``RunResult.trace``) and the later LangGraph lessons.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

RunType = Literal["llm", "tool", "chain"]
"""The categorical kind of a span.

Maps to Langfuse observation types (``llm`` -> GENERATION, ``tool``/``chain`` ->
SPAN) and to OpenTelemetry span kinds. ``chain`` is the loop/run framing span;
``llm`` is one model call; ``tool`` is one tool dispatch.
"""


class SpanUsage(BaseModel):
    """Token accounting attached to an ``llm`` span.

    Langfuse renders these as token usage and cost on a GENERATION. Tool and
    chain spans carry no usage (``None``).
    """

    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class TraceEvent(BaseModel):
    """One span: a single model call, a single tool call, or the loop step.

    The field set is deliberately small and defensible — each field answers a
    question you actually ask of a run:

    - ``run_type`` / ``name`` — *what kind of step was this, and which one?*
    - ``inputs`` — *what did the model choose?* (the arguments are where the
      truth is — read them first)
    - ``outputs`` / ``error`` — *what came back, and did it fail?*
    - ``usage`` — *why did it cost that much?* (``llm`` spans only)
    - ``start_time`` / ``end_time`` — *why was it slow?*

    Deliberately *left out*: full prompt bodies, raw tracebacks, every
    intermediate variable. A trace bloated with everything is as unreadable as
    no trace — minimalism is a design choice, not an omission.

    Example (one ``tool`` span, as a dict)::

        {
            "run_id": "…", "trace_id": "…", "run_type": "tool",
            "name": "calculator", "inputs": {"expression": "17*23"},
            "outputs": {"content": "391"}, "error": None,
        }
    """

    run_id: str
    """This span's own id."""
    trace_id: str
    """Shared by every span of one run — the field that makes a run separable
    from another when traces are stored together, and the key a trace diff
    (L11 objective 4) and the Langfuse view group on."""
    parent_run_id: str | None = None
    """Nesting parent, when spans nest. Mostly flat for a shallow loop."""
    run_type: RunType
    name: str
    """e.g. ``"model.create"``, ``"calculator"``, ``"agent_loop.run"``."""
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    """Set on a failed span; ``None`` on success."""
    start_time: float | None = None
    """Unix seconds when the span started (``time.time()``)."""
    end_time: float | None = None
    usage: SpanUsage | None = None

    @property
    def duration_s(self) -> float | None:
        """Wall-clock seconds for this span, or ``None`` if times are missing."""
        if self.start_time is None or self.end_time is None:
            return None
        return self.end_time - self.start_time

    def one_line(self) -> str:
        """A compact, human-readable rendering for narrating a trace in class.

        Example: ``llm    model.create        -> tool_calls=['calculator']``.
        """
        head = f"{self.run_type:5} {self.name:20}"
        if self.run_type == "tool":
            tail = f"{self.inputs} -> {self.outputs.get('content')!r}"
            if self.error is not None:
                tail += "  [is_error]"
            return f"{head} {tail}"
        if self.run_type == "llm":
            calls = self.outputs.get("tool_calls")
            toks = f" tokens={self.usage.total_tokens}" if self.usage is not None else ""
            return f"{head} -> tool_calls={calls}{toks}"
        return f"{head} {self.outputs}"


def to_jsonl(events: Iterable[TraceEvent]) -> str:
    """Serialize spans to JSON-lines (one span per line) — the on-disk form."""
    return "\n".join(event.model_dump_json() for event in events)


def from_jsonl(text: str) -> list[TraceEvent]:
    """Parse a JSON-lines trace back into spans. Blank lines are ignored."""
    return [TraceEvent.model_validate_json(line) for line in text.splitlines() if line.strip()]


def write_jsonl(events: Iterable[TraceEvent], path: Path) -> None:
    """Write spans to ``path`` as JSON-lines."""
    path.write_text(to_jsonl(events), encoding="utf-8")


def read_jsonl(path: Path) -> list[TraceEvent]:
    """Read a JSON-lines trace file back into spans."""
    return from_jsonl(path.read_text(encoding="utf-8"))
