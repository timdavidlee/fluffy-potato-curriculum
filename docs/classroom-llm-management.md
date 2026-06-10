# Classroom LLM management

> **Status:** decision notes, not yet implemented. Captures options for letting a cohort of
> students share one LLM budget with per-student usage tracking and spend caps.
> **Scope:** operational/infrastructure only — this is *not* curriculum content and does **not**
> live under [`docs/origin/`](origin/) (that tree is curriculum-generation prompts).

## The problem

A cohort of students each makes real Anthropic API calls during the labs (the course is
live-by-default — notebooks make real calls through the
[`common/config.py`](../src/fluffy_potato_curriculum/common/config.py) seam). For a class we want:

- **One shared budget** the instructor funds, not N individual billing accounts.
- **Per-student usage visibility** — who spent what.
- **Per-student spend caps** — a runaway loop (cf. L07's `max_steps`) shouldn't drain the pool.
- **No change to what students import** — the lesson code keeps using `PotatoLLMClient`.

## The key distinction

Two concerns get bundled together and should stay separate:

1. **The student-facing client** — what lesson code imports. *Already decided:* the course uses the
   hand-rolled `PotatoLLMClient` (a Protocol over Anthropic/OpenAI clients under
   [`src/fluffy_potato_curriculum/potato_llm/`](../src/fluffy_potato_curriculum/potato_llm/)),
   deliberately **not** LangChain or OpenRouter. Don't reopen this for a billing concern.
2. **The operational billing/tracking layer** — how a cohort shares one budget. This can sit
   *behind* the config seam as an env/`base_url`/key change, touching **zero** lesson code.

Keeping them separate is the whole game: pick a tracking mechanism that plugs in as configuration,
so the curriculum's provider story is untouched.

## Options considered

### 1. Anthropic-native Workspaces + Admin API — *recommended for "shared Anthropic"*

The Anthropic Console supports **Workspaces**: create separate API keys with per-key spend limits,
and pull per-key cost/usage from the Admin API (or the Console usage/cost dashboard).

- ✅ First-party; **no third party in the request path**; no surcharge.
- ✅ Stays on the native Anthropic Messages API, so it doesn't disturb the L04+ "we call Claude's
  native API" framing.
- ✅ Plugs into the config seam as a per-student key (and optionally an org/workspace).
- ⚠️ Per-student keys are an admin task (provision/rotate per cohort).
- ⚠️ Spend caps are workspace/key-level controls, not a hard real-time per-request budget gate.

This is the most direct answer to *"track calls against a shared Anthropic API."*

### 2. Self-hosted proxy (e.g. LiteLLM) — *recommended if you need hard budgets*

Run a proxy that holds the single real Anthropic key, mints per-student **virtual keys** with
budgets, and logs spend per key.

- ✅ Hard per-key budget enforcement; per-student logging.
- ✅ Stays Anthropic-format, so the native-SDK teaching is undisturbed.
- ✅ Plugs into the config seam as a `base_url` + per-student virtual key.
- ⚠️ You run and maintain the infra (a service + its datastore).

### 3. OpenRouter — *works, but not the best fit here*

OpenRouter is an OpenAI-format gateway across many providers, with per-key usage tracking.

- ✅ **Sub-keys with credit caps** drawing from one funded account; per-key usage in the dashboard /
  activity API → genuine per-student tracking.
- ✅ **BYOK ("bring your own key")** mode: attach your own Anthropic key and have OpenRouter route
  through it while recording usage — the literal *"track calls against a shared Anthropic API."*
- ⚠️ **OpenAI-format gateway.** It binds to the project's `openai_client.py` (base-url swap), **not**
  the Anthropic-SDK `anthropic_client.py` — which quietly undercuts the L04+ native-Messages-API
  framing.
- ⚠️ **BYOK surcharge.** OpenRouter takes a percentage fee on BYOK requests. <!-- *NEED INPUT*: verify current OpenRouter BYOK surcharge % before relying on it; figure changes over time. -->
- ⚠️ Reintroduces the OpenRouter dependency the course already chose to avoid for the provider
  abstraction (see [memory: provider abstraction decision]). Acceptable as *infra* behind the seam,
  but easy to let leak into the taught client — which is what to avoid.

## How any option plugs into the existing seam

[`common/config.py`](../src/fluffy_potato_curriculum/common/config.py) (pydantic-settings over env +
repo-root `.env`) already centralizes the key/endpoint. Each option becomes a configuration change
behind `PotatoLLMClient`:

| Option | What changes in config | Which `potato_llm` client |
| --- | --- | --- |
| Anthropic Workspaces | per-student Anthropic key (+ optional workspace) | `anthropic_client.py` (native) |
| LiteLLM proxy | `base_url` → proxy, per-student virtual key | `anthropic_client.py` (Anthropic-format) |
| OpenRouter | `base_url` → OpenRouter, per-student sub-key | `openai_client.py` (OpenAI-format) |

Students keep importing the same client; the cohort plumbing is entirely operational.

## Recommendation

For *"let a class share one Anthropic budget with per-student visibility and caps"*:

1. **Anthropic Workspaces** if you want zero infra and native API fidelity.
2. **LiteLLM proxy** if you need hard, enforced per-student budgets.
3. **OpenRouter** only if you separately want its multi-provider routing — and even then, keep it as
   an operational layer behind the seam, never as the taught client.

## Open questions

- <!-- *NEED INPUT*: cohort size and per-student budget target — drives whether soft (Workspaces) or hard (proxy) caps are needed. -->
- <!-- *NEED INPUT*: who administers key provisioning/rotation per cohort, and is a manual Console workflow acceptable or is automation (Admin API) wanted? -->
- <!-- *NEED INPUT*: does any lesson actually need OpenAI-format/multi-provider routing, or is the course Anthropic-only in practice? If Anthropic-only, OpenRouter's main advantage doesn't apply. -->
- <!-- *NEED INPUT*: verify current OpenRouter BYOK surcharge % and Anthropic per-key spend-limit controls before committing to a number in planning. -->

## Related

- Provider abstraction decision (hand-rolled `PotatoLLMClient`, not LangChain/OpenRouter).
- Live-demos + config seam (`common/config.py`) — the integration point for all options above.
- L11 roadmap open question on reconciling LangGraph's own client with the `potato_llm` seam —
  a related "framework brings its own client" tension, tracked in
  [`docs/origin/lesson_roadmaps/L11/objectives.md`](origin/lesson_roadmaps/L11/objectives.md).
