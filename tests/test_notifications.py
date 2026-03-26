"""Tests for azure_notification_hub.notifications module."""

import json
import pytest

from azure_notification_hub.notifications import (
    create_adm_body,
    create_adm_notification,
    create_apple_body,
    create_apple_notification,
    create_baidu_body,
    create_baidu_notification,
    create_browser_notification,
    create_fcm_legacy_body,
    create_fcm_legacy_notification,
    create_fcm_v1_body,
    create_fcm_v1_notification,
    create_template_notification,
    create_windows_badge_notification,
    create_windows_notification,
    create_windows_raw_notification,
    create_windows_tile_notification,
    create_windows_toast_body,
    create_windows_toast_notification,
    create_xiaomi_notification,
)


# ─── Apple ───────────────────────────────────────────────────────


def test_create_apple_notification():
    n = create_apple_notification(body='{"aps":{"alert":"hi"}}')
    assert n["platform"] == "apple"
    assert n["contentType"] == "application/json;charset=utf-8"
    assert n["body"] == '{"aps":{"alert":"hi"}}'


def test_create_apple_notification_with_headers():
    n = create_apple_notification(body="{}", headers={"apns-topic": "com.example"})
    assert n["headers"]["apns-topic"] == "com.example"


def test_create_apple_body():
    body = create_apple_body(alert="Hello", badge=1, sound="default")
    data = json.loads(body)
    assert data["aps"]["alert"] == "Hello"
    assert data["aps"]["badge"] == 1
    assert data["aps"]["sound"] == "default"


def test_create_apple_body_with_custom():
    body = create_apple_body(alert="Hi", custom={"orderId": "123"})
    data = json.loads(body)
    assert data["orderId"] == "123"


def test_create_apple_body_dict_alert():
    body = create_apple_body(alert={"title": "T", "body": "B"})
    data = json.loads(body)
    assert data["aps"]["alert"]["title"] == "T"


# ─── FCM Legacy ──────────────────────────────────────────────────


def test_create_fcm_legacy_notification():
    n = create_fcm_legacy_notification(body='{"to":"token"}')
    assert n["platform"] == "gcm"


def test_create_gcm_notification_alias():
    from azure_notification_hub.notifications import create_gcm_notification

    n = create_gcm_notification(body="{}")
    assert n["platform"] == "gcm"


def test_create_fcm_legacy_body():
    body = create_fcm_legacy_body(to="/topics/news", data={"key": "val"})
    data = json.loads(body)
    assert data["to"] == "/topics/news"
    assert data["data"] == {"key": "val"}
    assert data["priority"] == "high"


def test_create_fcm_legacy_body_with_ttl():
    body = create_fcm_legacy_body(to="token", time_to_live=3600)
    data = json.loads(body)
    assert data["time_to_live"] == 3600


# ─── FCM V1 ──────────────────────────────────────────────────────


def test_create_fcm_v1_notification():
    n = create_fcm_v1_notification(body='{"token":"t"}')
    assert n["platform"] == "fcmv1"


def test_create_fcm_v1_body():
    body = create_fcm_v1_body(
        notification={"title": "Hi", "body": "World"},
        data={"key": "val"},
        android={"priority": "high"},
    )
    data = json.loads(body)
    assert data["notification"]["title"] == "Hi"
    assert data["data"] == {"key": "val"}
    assert data["android"]["priority"] == "high"


# ─── Windows ─────────────────────────────────────────────────────


def test_create_windows_toast_notification():
    n = create_windows_toast_notification(body="<toast>hi</toast>")
    assert n["platform"] == "windows"
    assert n["contentType"] == "application/xml"
    assert n["headers"]["X-WNS-Type"] == "wns/toast"


def test_create_windows_tile_notification():
    n = create_windows_tile_notification(body="<tile>hi</tile>")
    assert n["headers"]["X-WNS-Type"] == "wns/tile"


def test_create_windows_badge_notification():
    n = create_windows_badge_notification(body="<badge value='1'/>")
    assert n["headers"]["X-WNS-Type"] == "wns/badge"


def test_create_windows_raw_notification():
    n = create_windows_raw_notification(body="raw data")
    assert n["headers"]["X-WNS-Type"] == "wns/raw"
    assert n["contentType"] == "application/octet-stream"


def test_create_windows_notification_toast():
    n = create_windows_notification(body="<toast/>", wns_type="wns/toast")
    assert n["headers"]["X-WNS-Type"] == "wns/toast"


def test_create_windows_notification_invalid():
    with pytest.raises(ValueError, match="Invalid WNS type"):
        create_windows_notification(body="x", wns_type="wns/invalid")


def test_create_windows_toast_body():
    xml = create_windows_toast_body(text="Hello!", launch="/page")
    assert "Hello!" in xml
    assert 'launch="/page"' in xml


def test_create_windows_toast_body_duration():
    xml = create_windows_toast_body(text="Hi", duration="long")
    assert 'duration="long"' in xml


# ─── ADM ─────────────────────────────────────────────────────────


def test_create_adm_notification():
    n = create_adm_notification(body='{"data":{"k":"v"}}')
    assert n["platform"] == "adm"


def test_create_adm_body():
    body = create_adm_body(data={"key": "val"}, consolidation_key="ck")
    data = json.loads(body)
    assert data["data"] == {"key": "val"}
    assert data["consolidationKey"] == "ck"


# ─── Baidu ───────────────────────────────────────────────────────


def test_create_baidu_notification():
    n = create_baidu_notification(body='{"title":"hi"}')
    assert n["platform"] == "baidu"


def test_create_baidu_body():
    body = create_baidu_body(
        title="Hello", description="World", open_type=2, url="https://example.com"
    )
    data = json.loads(body)
    assert data["title"] == "Hello"
    assert data["open_type"] == 2
    assert data["url"] == "https://example.com"


# ─── Browser ─────────────────────────────────────────────────────


def test_create_browser_notification_dict():
    n = create_browser_notification(body={"title": "Hi", "body": "World"})
    assert n["platform"] == "browser"
    data = json.loads(n["body"])
    assert data["title"] == "Hi"


def test_create_browser_notification_string():
    n = create_browser_notification(body='{"title":"Hi"}')
    assert n["body"] == '{"title":"Hi"}'


# ─── Template ────────────────────────────────────────────────────


def test_create_template_notification():
    n = create_template_notification(body={"message": "Hello", "badge": 1})
    assert n["platform"] == "template"


# ─── Xiaomi ──────────────────────────────────────────────────────


def test_create_xiaomi_notification():
    n = create_xiaomi_notification(body={"title": "Hi"})
    assert n["platform"] == "xiaomi"


# ─── Windows Phone ───────────────────────────────────────────────


def test_create_windowsphone_notification():
    from azure_notification_hub import create_windowsphone_notification

    n = create_windowsphone_notification(
        body="<wp:Toast><wp:Text1>Hi</wp:Text1></wp:Toast>",
        headers={"X-WindowsPhone-Target": "toast", "X-NotificationClass": "2"},
    )
    assert n["platform"] == "windowsphone"
    assert n["headers"]["X-WindowsPhone-Target"] == "toast"


def test_create_windowsphone_toast_body():
    from azure_notification_hub import create_windowsphone_toast_body

    xml = create_windowsphone_toast_body("Hello", "World", "/page")
    assert "<wp:Text1>Hello</wp:Text1>" in xml
    assert "<wp:Text2>World</wp:Text2>" in xml
    assert "<wp:Param>/page</wp:Param>" in xml


# ─── Common ──────────────────────────────────────────────────────


def test_dict_auto_serialized():
    n = create_browser_notification(body={"title": "Test"})
    assert isinstance(n["body"], str)
    assert json.loads(n["body"])["title"] == "Test"


def test_string_passthrough():
    n = create_browser_notification(body='{"already":"json"}')
    assert n["body"] == '{"already":"json"}'
