# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false
# ^ Starlette's TestClient is httpx-backed, and pyright resolves httpx's client
#   methods as partially-unknown in this environment. Isolate that here so the
#   test modules stay strict-clean: these helpers hand back concrete types
#   (``int`` / ``Any``) at the boundary.
"""Thin typed wrappers around the httpx-backed FastAPI ``TestClient``."""

from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient


def get_status(client: TestClient, url: str) -> int:
    """HTTP status code for a GET request."""
    return client.get(url).status_code


def get_json(client: TestClient, url: str) -> Any:
    """Parsed JSON body for a GET request (``Any`` — shape is asserted by callers)."""
    return client.get(url).json()


def get_text(client: TestClient, url: str) -> str:
    """Response body as text for a GET request."""
    return client.get(url).text


def get_header(client: TestClient, url: str, name: str) -> str:
    """A single response header value for a GET request."""
    return client.get(url).headers[name]
