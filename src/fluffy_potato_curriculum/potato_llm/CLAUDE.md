# potato_llm/

The provider-agnostic seam for talking to an LLM, hand-rolled as the **L01–L02 teaching
artifact**. Everything in those first two lessons that "calls a model" goes through this
interface, so swapping Anthropic for OpenAI is a one-line change at the edge of a program
instead of a rewrite of the middle.

Nothing here is an official SDK type — the "Potato" prefix is a reminder that we hand-rolled it
for teaching. In production you'd reach for a framework like LangChain or a gateway like
OpenRouter; we build the seam once, by hand, so students see exactly what those do *before*
adopting one. **From L03 onward the course does exactly that:** it switches to LangChain's
`ChatAnthropic` (an `init_chat_model("anthropic:claude-sonnet-4-6")` handle) as the real
provider-agnostic client, and that is the through-line for the rest of the curriculum —
tool calling, the agent loop, tracing, and evals all drive a LangChain chat model (see
[../common/CLAUDE.md](../common/CLAUDE.md) and `common/agent_loop.py`). So this module is the
*motivation* for the framework, not a parallel client that grows alongside it.

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
- Content is plain text on purpose. This seam stays a **plain-text completions** client for
  L01–L02; tool calls, the model→tool→model loop, and tracing are **not** bolted onto it later —
  they are taught on LangChain's `ChatAnthropic` from L03 on (see `common/agent_loop.py` and
  `common/fake_model.py`).

See the root [CLAUDE.md](../../../CLAUDE.md) for the toolchain and the full pre-commit gate.
