# L07: Tool calling: how it works

> Parent design doc: [CURRICULUM_PRD.md](../../CURRICULUM_PRD.md) (lesson-plan row L07).
> Folder conventions: [docs/origin/CLAUDE.md](../../CLAUDE.md).

## Where this lesson sits

L01–L06 covered everything you can do with a model that is purely *text-in, text-out*: tokenization and cost (L01), prompting roles and structured output (L02), and eliciting better reasoning by changing the *content* of prompts (L06). L07 is the first lesson where the model is given the ability to *act* — to request that the application run an external function and feed the result back. This is the bedrock of every agent in the rest of the course.

The framing carried over from L06 — *reasoning is just more tokens, and a structured-output contract like `<thinking>` is a contract about shape, not capability* — applies directly here. A tool call is also "just more tokens" the model emits in a structured shape that the surrounding application interprets. The model is not running anything; the application is.

L07 deliberately sticks to *one* tool and *one* round-trip. Schema-design judgment, when-to-use-a-tool decisions, and tool-error handling are all L08's territory.

## Prerequisites

Students arriving at L07 should already be able to:

- Send a multi-turn chat completion with system/user/assistant roles (L02).
- Request structured output (e.g. JSON) from a model and parse it (L02).
- Estimate the token cost of a prompt and reason about context-window pressure (L01) — important here because tool definitions and tool results both consume context.
- Recognize that prompt-shape contracts (like `<thinking>` tags from L06) are interpreted by the *surrounding code*, not enforced by the model.

If a student is shaky on any of these, redirect to the corresponding L01–L06 lab before continuing.

## Vocabulary the lesson introduces

These terms recur across L08 and the later tool/agent lessons, so the lesson must land them clearly:

- **Tool** — a callable in the application (typically a Python function) that the model can request via the tool-call protocol.
- **Tool definition / schema** — a structured description (name, natural-language description, per-argument JSON-Schema input shape) the model is handed alongside the prompt. It tells the model what tools exist and how to invoke them. Under LangChain you don't hand-write this: `bind_tools([fn])` *infers* it from a typed Python function — the name from `fn`, the description from its docstring, the argument schema from its type hints (`Annotated[...]` per-arg descriptions, `Literal` enums). You can inspect the inferred dict with `convert_to_openai_tool(fn)`.
- **Tool call** — an entry in a model reply's `AIMessage.tool_calls` list saying "I want to call tool X with arguments Y." Each entry is a dict `{"name", "args", "id"}`. Not an execution; a request.
- **Tool result** — a dedicated `ToolMessage(content=..., tool_call_id=...)` — its own message role, distinct from human and assistant — that carries the output of running the requested tool and names the call id it answers. Closes the loop.
- **Round-trip** — one full `model → tool-call → application runs tool → tool-result → model` exchange. L07 deals only with single round-trips; multi-step loops arrive in L10.

> **Resolved:** the course standardizes on LangChain's `ChatAnthropic` (an `init_chat_model("anthropic:claude-sonnet-4-6")` handle). Tool calls surface as `AIMessage.tool_calls`; results go back as `ToolMessage`; tool definitions are inferred from typed Python functions via `bind_tools` (no hand-written JSON schema).

## Learning objectives

By the end of L07, a student should be able to:

1. **Wire a single tool to a model call.** Concretely:
   - Write a plain, typed Python function that performs some side-effect-free work (e.g. compute, look up a value in a small dict, call a deterministic stub).
   - Let that function *be* the tool definition: `bind_tools([fn])` infers the name, description, and per-argument JSON schema from the function's name, docstring, and type hints (`Annotated[...]` per-arg descriptions, `Literal` enums) — no hand-written JSON.
   - Invoke the tool-bound model (`model.bind_tools([fn]).invoke(messages)`) with a user prompt that should plausibly trigger the tool.
   - When the reply's `AIMessage.tool_calls` carries a request, dispatch on the tool name, validate the arguments, call the underlying function, and capture the result.
   - Send the result back as a `ToolMessage(content=..., tool_call_id=...)` in the next turn, and receive the model's final answer.

2. **Trace one tool-call round-trip.** Concretely:
   - Read a model reply and identify whether its `AIMessage` carries text in `.content`, structured requests in `.tool_calls`, or both.
   - For a tool call, read off the tool name, the arguments (`args`, a parsed dict, not a string blob), and the unique `id` that ties request to result.
   - Read the application's follow-up `ToolMessage` and identify: which call id (`tool_call_id`) it answers, what content it carries, whether it represents success or failure (`status="error"`).
   - Lay out the message-by-message shape of a successful round-trip on paper or in a notebook: `HumanMessage → AIMessage(tool_calls) → ToolMessage → AIMessage(final)`. Recognize that this is a four-message sequence in the conversation history, even though the user only "asked once."
   - Distinguish three observable outcomes from the model: it called the tool, it answered without calling the tool, or it called the tool with malformed/hallucinated arguments. Be able to look at a transcript and say which happened.

3. **Describe the tool-call protocol.** Concretely:
   - Explain in one or two sentences that *tool calling is a protocol the model has been trained to participate in*, not a runtime capability of the model. The model emits structured tokens; the application interprets them. The model does not "execute" anything.
   - Name the three actors in a single round-trip — model, application, tool — and which one performs each step (decide to call → emit tool-call block → validate arguments → run the function → format the result → continue the conversation).
   - Explain why tool definitions are passed on *every* request (the model is stateless across calls; the schema is part of the prompt) and what that implies for token cost (foreshadow L14 on model & provider choice and L19 on context management — every tool definition is paid for, every request).
   - Recognize that the *decision to call a tool* is a reasoning step, and that L06's CoT/scratchpad/when-not-to-reason guidance applies inside that decision (reinforce, do not re-teach).

## Main points the lecture should land

- **A tool call is just more structured tokens.** The model is not running code, opening a network connection, or reaching into your filesystem. It is generating a token sequence that — by training — has the shape of a tool call, which LangChain surfaces as an entry in the reply's `AIMessage.tool_calls`. Your application is the one that reads those tokens, decides what to do with them, runs the actual function, and feeds the result back. This framing is the single most important thing the lesson must land, because it determines how students debug, secure, and scale every agent that comes later.

- **The schema is a contract about shape, not a guarantee about behavior.** Mirroring L06's framing of `<thinking>` tags: a tool definition tells the model "tools of this shape exist." It does not force the model to call one, does not validate the arguments at generation time, and does not stop the model from inventing a tool name that doesn't exist. The application validates; the model proposes.

- **The round-trip is conversational.** A single tool-using exchange is *at minimum* four messages in the history: the user's `HumanMessage`, the assistant's `AIMessage` carrying the tool call, the application's `ToolMessage` carrying the result, and the assistant's final `AIMessage`. Students must build the intuition that *every* tool call grows the message history — not as a side effect, but as the protocol itself.

- **The model is stateless across calls.** Every request must include the full tool definition list and the full conversation history (or a compaction of it — but that is L19's territory). Students often assume "I told the model about the tool last turn, so it remembers." It does not. The schema is in the prompt every time.

- **Tools cost tokens, twice over.** The tool *definition* is in every prompt; the tool *result* is in the message history forever after. A 500-token tool definition added to a 10-turn conversation costs roughly 5,000 input tokens before any tool is even called. This is why L14 (models & providers) and L19 (context management) come back to tool-cost reasoning.

- **The model can hallucinate tool calls.** Wrong tool name, wrong argument types, made-up tools, missing required args, extra unspecified args. The application is responsible for catching these. Showing one hallucination in the lecture is more educational than ten clean runs — the same way L06 used a tag-violation moment to teach that scratchpad contracts are best-effort.

- **The decision to call a tool is itself a reasoning step.** Reinforce, don't re-teach: everything from L06 — CoT, scratchpad, recognizing when explicit reasoning helps vs. hurts — applies inside the tool-call decision. A model that is asked to "use the calculator if you need to" is making a reasoning judgment about whether the calculator is needed. <!-- *NEED INPUT*: overlap with L06 on reasoning-as-tokens framing — reinforce vs. re-teach? Lean reinforce, but confirm the linkage in the lecture rather than re-teaching CoT. -->

## Common student confusions to watch for

- *"The model runs the tool."* It does not. The application runs the tool. The model only emits a request shaped like a tool call. Land this every time it comes up — it shapes how students think about security, debugging, and what the model "can and cannot do" for the rest of the course.
- *"If I define a tool, the model will use it."* Not necessarily. Tool selection is a sampling decision, conditioned on the prompt, the conversation, and the tool description. A vague description of a tool is a tool the model will skip. (This is the bridge to L08's schema-design lesson.)
- *"Tool calls are deterministic."* They are not. Same prompt, same schema, the model may call or skip the tool, and may pass slightly different arguments across runs.
- *"Tool results are part of the assistant message."* They are not. The application hands the result back as a dedicated `ToolMessage` — its own message role (a third role beyond human and assistant), not a user-role message. LangChain formats that `ToolMessage` for the model. The history carries three message types — `HumanMessage`, `AIMessage`, and `ToolMessage` — and the `ToolMessage` is the *application* speaking, not the human.
- *"More tools = better agent."* More tools means more schema text in every prompt, more chances to mis-pick, and more edge cases to validate. Foreshadow L08 ("Designing good tools") and L24 (multi-agent / subagent), where the answer to "too many tools" is sometimes "split the agent."
- *"I can force the model to always call this tool."* `bind_tools(..., tool_choice=...)` controls (auto / any / none / specific) bias the decision, but even forced choice does not guarantee well-formed arguments — only that *some* tool call will be attempted. <!-- *NEED INPUT*: include `tool_choice` mechanics here, or defer to L08? Currently leaning *brief mention here, deeper in L08.* -->

## Bridge to L08

L08 ("Designing good tools") takes the mechanics from L07 and asks the design questions: *should* this be a tool, what should we name it, what should the schema look like, how should it report failures? L07's job is to make the protocol mechanically obvious. L08's job is to make students opinionated about it. The two lessons must agree on vocabulary — `tool`, `tool definition`, `tool call`, `tool result`, `round-trip` — so an L08 student doesn't have to relearn terms.

A useful mental handoff for the lecturer: by the end of L07, a student can build a tool-using exchange that *works*. By the end of L08, they can argue about whether the tool should exist at all and whether the schema is good.

## Open authoring questions

- > **Resolved:** the course standardizes on LangChain's `ChatAnthropic` (an `init_chat_model("anthropic:claude-sonnet-4-6")` handle). Tool calls surface as `AIMessage.tool_calls`; results go back as `ToolMessage`; tool definitions are inferred from typed Python functions via `bind_tools` (no hand-written JSON schema). This vocabulary is reused everywhere — L08 and the later tool/agent lessons build on it.
- <!-- *NEED INPUT*: estimated lecture duration — best guess 60–90 minutes as one lecture, or split into two (protocol + vocabulary, then first wired round-trip)? -->
- <!-- *NEED INPUT*: which model class anchors the labs (mirrors the same open question raised in L06's roadmap). Smaller models behave differently around tool selection — a Haiku-class model may skip a vague tool, a Sonnet-class model may call it anyway. The lab examples should be tuned to whichever model is canonical. -->
- <!-- *NEED INPUT*: include `tool_choice` / forced-tool-call mechanics in L07, or defer to L08 alongside the broader design conversation? Mirrored in the "common confusions" section. -->
- <!-- *NEED INPUT*: should the L07 lab tool be a pure-Python function (calculator, deterministic lookup) or a real external service (weather API, time-of-day)? Real services teach failure modes earlier but introduce flakiness; pure functions keep the focus on the protocol. -->
- <!-- *NEED INPUT*: are Anthropic's built-in / first-party tools (web search, code execution, computer use) in scope here, or is L07 strictly user-defined-tool only? Recommend: user-defined-tool only in L07; built-ins introduced as an aside in L08 or L09 (MCP) where the "where does the tool live?" question is already on the table. -->
- <!-- *NEED INPUT*: any specific L01–L06 labs that must be completed before L07 is taught, beyond the prerequisite skills above? -->
