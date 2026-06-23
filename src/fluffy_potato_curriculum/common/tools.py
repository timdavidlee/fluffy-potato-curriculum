"""The shared tools the hand-rolled agent loop dispatches.

This is the canonical reference copy of the tools students first built inline in
L07. L08 (and L09, and the later LangGraph lessons) import them from here instead
of re-deriving them, so every lesson traces and evaluates the *same* agent.

The tools stay deliberately tiny and deterministic — the lessons are about the
loop, the trace, and the eval set, not about tool design (that was L05). Each
tool returns a ``str`` and signals failure in one of two ways, which is exactly
what gives L08's "locate a failure" objective its raw material:

- a tool that **raises** (``calculator`` on junk input, ``lookup`` on a missing
  city, ``flaky_fetch`` on a crashing URL) — the loop converts the exception
  into a ``tool_result`` with ``is_error: true`` (see ``agent_loop.dispatch``);
- a tool that **returns an error as data** (``flaky_fetch`` on an error URL) —
  the L05 "errors are values" pattern; the call succeeds, the *content* is bad.
"""

from __future__ import annotations

from typing import Any

# --- calculator -------------------------------------------------------------

_ALLOWED_EXPR_CHARS = set("0123456789+-*/(). ")


def calculator(expression: str) -> str:
    """Evaluate a simple arithmetic expression, or raise ``ValueError`` on junk.

    The whitelist blocks names, attributes, and calls, so the ``eval`` below can
    only ever see arithmetic — a non-arithmetic expression raises before it runs.
    """
    if not expression or set(expression) - _ALLOWED_EXPR_CHARS:
        raise ValueError(f"refusing to evaluate non-arithmetic expression: {expression!r}")
    # eval is safe here ONLY because the whitelist above blocks names/attributes/calls.
    return str(eval(expression))


# --- lookup -----------------------------------------------------------------

POPULATIONS: dict[str, str] = {
    "tokyo": "37000000",
    "lagos": "15000000",
    "paris": "11000000",
}
"""A tiny in-memory table. Keyed by lowercase city name; a couple of cities are
deliberately absent so "city not found" is reachable (a clean tool-error)."""


def lookup(city: str) -> str:
    """Return a city's population from the tiny table, or raise ``KeyError``."""
    key = city.strip().lower()
    if key not in POPULATIONS:
        raise KeyError(f"no population on file for {city!r}")
    return POPULATIONS[key]


# --- flaky_fetch ------------------------------------------------------------

_FETCH_OK_BODY = "the answer is 42"


def flaky_fetch(url: str) -> str:
    """Fetch a URL from a tiny fake network whose behavior is keyed by the URL.

    Keying the behavior on the URL makes each failure *reproducible* — the demos
    and labs can provoke any signature on demand, with no real network and no
    randomness:

    - ``"https://ok"``      -> returns a usable value (success).
    - ``"https://error"``   -> returns a structured **error as data** (the call
      succeeds; the content says it failed — the L05 pattern).
    - ``"https://crash"``   -> **raises** ``RuntimeError`` (an uncaught exception
      the loop must convert into a ``tool_result``).
    - ``"https://garbage"`` -> returns **malformed** output (succeeds, but the
      content is unusable).

    Any other URL raises ``ValueError`` (an unknown endpoint).
    """
    match url:
        case "https://ok":
            return _FETCH_OK_BODY
        case "https://error":
            return '{"error": "503 service unavailable"}'
        case "https://crash":
            raise RuntimeError("connection reset by peer")
        case "https://garbage":
            return "\x00\x07 <not-json> ��"
        case _:
            raise ValueError(f"unknown url: {url!r}")


# --- the dispatch table + JSON-Schema definitions ---------------------------

TOOLS: dict[str, Any] = {
    "calculator": calculator,
    "lookup": lookup,
    "flaky_fetch": flaky_fetch,
}
"""Tool NAME -> the Python function that runs it. The loop never hard-codes a
tool name; it looks each requested name up here."""


TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "calculator",
        "description": "Evaluate a basic arithmetic expression and return the exact result.",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string", "description": "e.g. '17*23'."}},
            "required": ["expression"],
        },
    },
    {
        "name": "lookup",
        "description": "Look up a city's population from a small internal table.",
        "input_schema": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "a city name, e.g. 'Tokyo'."}},
            "required": ["city"],
        },
    },
    {
        "name": "flaky_fetch",
        "description": "Fetch the contents of a URL. May fail in several ways.",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string", "description": "an https URL to fetch."}},
            "required": ["url"],
        },
    },
]
"""JSON-Schema tool definitions a real model requires. The offline ``FakeModel``
ignores them; the live Anthropic client needs them."""
