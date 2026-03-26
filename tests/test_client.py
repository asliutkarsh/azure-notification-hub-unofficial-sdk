"""Tests for azure_notification_hub.client module."""

import json

from azure_notification_hub.client import create_browser_installation


def test_create_browser_installation():
    inst = create_browser_installation(
        installation_id="id-123",
        push_channel={"endpoint": "https://example.com", "p256dh": "pk", "auth": "au"},
        tags=["user:123", "all"],
        expiration_time="2026-12-31T00:00:00Z",
    )
    assert inst["installationId"] == "id-123"
    assert inst["platform"] == "browser"
    assert inst["pushChannel"]["endpoint"] == "https://example.com"
    assert inst["tags"] == ["user:123", "all"]
    assert inst["expirationTime"] == "2026-12-31T00:00:00Z"


def test_create_browser_installation_minimal():
    inst = create_browser_installation(
        installation_id="id-1",
        push_channel={"endpoint": "e", "p256dh": "p", "auth": "a"},
    )
    assert inst["installationId"] == "id-1"
    assert "tags" not in inst
    assert "expirationTime" not in inst


def test_create_browser_installation_no_optional():
    inst = create_browser_installation(
        installation_id="id-2",
        push_channel={"endpoint": "e", "p256dh": "p", "auth": "a"},
    )
    assert "tags" not in inst
    assert "expirationTime" not in inst
