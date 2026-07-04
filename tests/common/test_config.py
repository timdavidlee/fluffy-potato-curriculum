"""Tests for the configuration seam in `common.config`."""

from __future__ import annotations

import pytest

from fluffy_potato_curriculum.common.config import (
    Settings,
    require_anthropic_key,
    require_langfuse,
    require_openai_key,
)

_ALL_LANGFUSE = {
    "langfuse_host": "https://langfuse.example",
    "langfuse_public_key": "pk-test",
    "langfuse_secret_key": "sk-test",
}


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


def test_require_langfuse_returns_triple(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "fluffy_potato_curriculum.common.config.get_settings",
        lambda: Settings(**_ALL_LANGFUSE),
    )
    assert require_langfuse() == ("https://langfuse.example", "pk-test", "sk-test")


@pytest.mark.parametrize(
    ("missing_field", "missing_env"),
    [
        ("langfuse_host", "LANGFUSE_HOST"),
        ("langfuse_public_key", "LANGFUSE_PUBLIC_KEY"),
        ("langfuse_secret_key", "LANGFUSE_SECRET_KEY"),
    ],
)
def test_require_langfuse_raises_when_any_missing(
    monkeypatch: pytest.MonkeyPatch, missing_field: str, missing_env: str
) -> None:
    values = {**_ALL_LANGFUSE, missing_field: None}
    monkeypatch.setattr(
        "fluffy_potato_curriculum.common.config.get_settings",
        lambda: Settings(**values),
    )
    with pytest.raises(RuntimeError, match=missing_env):
        require_langfuse()
