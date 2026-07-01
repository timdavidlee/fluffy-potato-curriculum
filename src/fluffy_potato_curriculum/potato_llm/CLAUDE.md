# potato_llm/

The provider-agnostic seam for talking to an LLM. Everything in the curriculum that "calls a
model" goes through this interface, so swapping Anthropic for OpenAI is a one-line change at
the edge of a program instead of a rewrite of the middle.

Nothing here is an official SDK type — the "Potato" prefix is a reminder that we hand-rolled it
for teaching. In production you'd reach for LiteLLM or a gateway like OpenRouter; we build it
once so students see exactly what those do. (This is deliberately **not** LangChain/OpenRouter.)

## What lives here

- `base.py` — the interface: `PotatoLLMClient` (a `runtime_checkable` `Protocol`), the
  `Message`/`ChatResponse`/`Usage` dataclasses, and the `Role` literal. Start here.
- `anthropic_client.py` — implementation backed by the Anthropic SDK. Hides the wrinkle that
  Anthropic takes the system prompt as a **separate top-level param**, not a message-list turn.
- `openai_client.py` — the mirror image: OpenAI keeps the system prompt **inside** the message
  list and reports `prompt_tokens`/`completion_tokens`, normalized back to our shape.

## Conventions

- **Keep provider translation in pure, testable helpers** (`extract_system`,
  `to_openai_messages`, …) so the mapping logic is unit-tested without a network call or an API
  key — see [tests/potato_llm/](../../../tests/potato_llm/). Never hit a live API in a test.
- **Keys come from the config seam**, not raw `os.environ`: both clients call the
  `require_*_key` helpers in [../common/config.py](../common/CLAUDE.md).
- Each client carries a `DEFAULT_MODEL` (Anthropic → the course anchor `claude-sonnet-4-6`;
  OpenAI → `gpt-4o-mini`). Override per call site as models evolve.
- Content is plain text on purpose — images and tool calls are introduced in later lessons.

See the root [CLAUDE.md](../../../CLAUDE.md) for the toolchain and the full pre-commit gate.
