"""Tests for the configuration seam in `common.config`."""

from __future__ import annotations

import pytest

from fluffy_potato_curriculum.common.config import (
    Settings,
    require_anthropic_key,
    require_openai_key,
)


def test_settings_reads_key_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-123")
    assert Settings().anthropic_api_key == "sk-test-123"


def test_require_anthropic_key_returns_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "fluffy_potato_curriculum.common.config.get_settings",
        lambda: Settings(anthropic_api_key="sk-test-123"),
    )
    assert require_anthropic_key() == "sk-test-123"


def test_require_anthropic_key_raises_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(
        "fluffy_potato_curriculum.common.config.get_settings",
        lambda: Settings(anthropic_api_key=None),
    )
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY is not set"):
        require_anthropic_key()


def test_require_openai_key_raises_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(
        "fluffy_potato_curriculum.common.config.get_settings",
        lambda: Settings(openai_api_key=None),
    )
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY is not set"):
        require_openai_key()
