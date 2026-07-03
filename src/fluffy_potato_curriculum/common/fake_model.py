"""A scripted, offline stand-in for a LangChain chat model.

The agent loop drives a chat model the LangChain way: ``model.bind_tools(...)``
then ``.invoke(messages)`` -> an :class:`~langchain_core.messages.AIMessage`
whose ``.tool_calls`` list says which tools (if any) the model wants run. The real
``ChatAnthropic`` (or any ``bind_tools``-capable model) provides that; ``FakeModel``
provides a *deterministic* version so the reading demos and labs run with **no API
key and no network**, and produce the exact same trace every time.

This matters pedagogically: the L11 reading skills are clearest on a fixed, known
trace. A scripted model gives that — its moves are decided in advance, so a
"runaway", a "wrong-arguments" run, or a clean run is reproducible on demand. The
real model only appears in the live instrument/export demos, where *producing* a
fresh trace is the point.

``FakeModel`` mimics only the slice of the chat-model interface the loop touches:
``.bind_tools(tools)`` (which it ignores, returning itself) and ``.invoke(messages)``
(which returns the next scripted ``AIMessage``). Build the script with
:func:`text_reply` and :func:`tool_reply` / :func:`tool_call`.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.messages.tool import ToolCall


def tool_call(call_id: str, name: str, args: dict[str, Any]) -> ToolCall:
    """Build one scripted tool call (``call_id`` becomes the LangChain tool_call id).

    Example::

        tool_call("c1", "calculator", {"expression": "17*23"})
    """
    return ToolCall(id=call_id, name=name, args=args, type="tool_call")


def _usage(input_tokens: int, output_tokens: int) -> dict[str, int]:
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
    }


def text_reply(text: str, *, input_tokens: int = 100, output_tokens: int = 20) -> AIMessage:
    """A scripted final answer: an ``AIMessage`` with text and no tool calls.

    A reply with no ``tool_calls`` is how the loop recognizes the model is done
    (natural termination)."""
    return AIMessage(content=text, usage_metadata=_usage(input_tokens, output_tokens))


def tool_reply(*calls: ToolCall, input_tokens: int = 100, output_tokens: int = 20) -> AIMessage:
    """A scripted tool-requesting turn: an ``AIMessage`` carrying ``tool_calls``.

    Example::

        tool_reply(tool_call("c1", "calculator", {"expression": "17*23"}))
    """
    return AIMessage(
        content="",
        tool_calls=list(calls),
        usage_metadata=_usage(input_tokens, output_tokens),
    )


@dataclass
class FakeModel:
    """A chat model whose replies are scripted in advance.

    ``bind_tools`` ignores its argument and returns ``self`` (the script already
    decides what the model "asks for"). ``invoke`` ignores the messages and returns
    the next scripted ``AIMessage``; when the script runs out it **repeats the last
    line** — which is how a runaway loop (the ``max_steps`` case) is simulated: keep
    asking for the same tool forever.

    Example::

        model = FakeModel([
            tool_reply(tool_call("c1", "calculator", {"expression": "17*23"})),
            text_reply("17 * 23 is 391."),
        ])
    """

    scripted: list[AIMessage]
    calls: int = field(default=0)

    def bind_tools(self, tools: Sequence[Any]) -> FakeModel:
        """Match the chat-model interface; the script, not the tools, drives replies."""
        return self

    def invoke(self, messages: Sequence[BaseMessage]) -> AIMessage:
        index = min(self.calls, len(self.scripted) - 1)
        self.calls += 1
        return self.scripted[index]
