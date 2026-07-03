"""Typed configuration for the curriculum, loaded from the environment.

Why this exists: the LLM clients need API keys, and we want *one* validated place
that reads them — with a clear, actionable error when a key is missing — instead of
scattering `os.environ[...]` lookups across notebooks and lessons.

`pydantic-settings` reads each field from the process environment (case-insensitive,
so `anthropic_api_key` is filled from `ANTHROPIC_API_KEY`) and, as a convenience for
local work, from a `.env` file at the repo root. Never commit a real `.env` — it
holds secrets. Copy `.env.example` to `.env` and fill in your own keys.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Anchor the `.env` lookup to the repo root, not the current working directory.
# Notebooks run with the kernel's cwd set to the notebook's own directory
# (e.g. lessons/L01/), so a bare relative ".env" would never resolve the
# repo-root file. config.py lives at <root>/src/fluffy_potato_curriculum/common/,
# so the root is four parents up.
_REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Process-wide configuration, read once from the environment / `.env`.

    Keys are optional at load time so the object always builds; the `require_*`
    helpers below turn a missing key into a clear error at the point of use.
    """

    model_config = SettingsConfigDict(
        env_file=_REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    anthropic_api_key: str | None = None
    openai_api_key: str | None = None

    # Self-hosted Langfuse tracing (introduced in L11, reused by the LangGraph
    # lessons L14+). All optional: when unset, tracing is simply skipped and the
    # code runs unchanged — see `langfuse_configured()` and the L11 notebooks.
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_host: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Return the cached, process-wide settings (read once from env / `.env`)."""
    return Settings()


def langfuse_configured() -> bool:
    """Return True only when all three Langfuse settings are present.

    Tracing is an opt-in extra: notebooks call this to decide whether to attach a
    Langfuse callback. With any of the three values missing it returns False and
    the workflow runs without tracing — the run is identical, only the spans are
    absent — so a keyless restart-and-run-all still passes.
    """
    settings = get_settings()
    return bool(
        settings.langfuse_public_key and settings.langfuse_secret_key and settings.langfuse_host
    )


def require_anthropic_key() -> str:
    """Return the Anthropic API key, or raise a clear error if it isn't set."""
    key = get_settings().anthropic_api_key
    if not key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Add it to your environment or to a `.env` "
            "file at the repo root (see `.env.example`) before making live LLM calls."
        )
    return key


def require_openai_key() -> str:
    """Return the OpenAI API key, or raise a clear error if it isn't set."""
    key = get_settings().openai_api_key
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add it to your environment or to a `.env` "
            "file at the repo root (see `.env.example`) before making live LLM calls."
        )
    return key
