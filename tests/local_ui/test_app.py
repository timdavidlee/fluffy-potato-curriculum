"""API endpoint behavior via FastAPI's TestClient (offline, no network)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from fluffy_potato_curriculum.local_ui.app import create_app
from tests.local_ui._api import get_json, get_status


@pytest.fixture
def client(lessons_dir: Path) -> TestClient:
    return TestClient(create_app(lessons_dir))


def test_tracks_endpoint_lists_names(client: TestClient) -> None:
    names = [t["name"] for t in get_json(client, "/api/tracks")]
    assert names == ["full", "mini"]


def test_lessons_endpoint_lists_lessons(client: TestClient) -> None:
    ids = [lesson["lesson_id"] for lesson in get_json(client, "/api/lessons")]
    assert ids == ["L01", "L02"]


def test_lesson_detail_includes_items(client: TestClient) -> None:
    detail = get_json(client, "/api/lessons/L01")
    assert detail["items"][0]["item_id"] == "L0101_intro"


def test_unknown_lesson_returns_404(client: TestClient) -> None:
    assert get_status(client, "/api/lessons/L99") == 404


def test_item_endpoint_returns_rendered_html(client: TestClient) -> None:
    body = get_json(client, "/api/lessons/L01/items/L0101_intro")
    assert "<h1" in body["html"]


def test_unknown_item_returns_404(client: TestClient) -> None:
    assert get_status(client, "/api/lessons/L01/items/nope") == 404


def test_index_page_served(client: TestClient) -> None:
    assert get_status(client, "/") == 200
