"""
azure_notification_hub — Unofficial Python SDK for Azure Notification Hubs.

This package provides a Python client for the Azure Notification Hubs REST API,
mirroring the official @azure/notification-hubs Node.js SDK.

Quick start:

    from azure_notification_hub import NotificationHubsClient

    client = NotificationHubsClient(
        connection_string="Endpoint=sb://...",
        hub_name="my-hub"
    )

    # Send a web push
    from azure_notification_hub import create_browser_notification
    notification = create_browser_notification(body='{"title":"Hello","body":"World"}')
    client.send_notification(notification, tag_expression="user:123")

Supported platforms:
    - Apple (APNs)
    - FCM Legacy (GCM)
    - FCM V1
    - Windows (WNS — toast, tile, badge, raw)
    - ADM (Amazon)
    - Baidu
    - Browser (Web Push)
    - Template (cross-platform)
    - Xiaomi
"""

from azure_notification_hub.auth import (
    create_sas_token,
    parse_connection_string,
)
from azure_notification_hub.client import (
    AzureNHError,
    NotificationHubsClient,
    SubscriptionGoneError,
    create_browser_installation,
)
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
    create_windowsphone_notification,
    create_windowsphone_toast_body,
    create_xiaomi_notification,
)

__version__ = "0.1.0"

__all__ = [
    # Client
    "NotificationHubsClient",
    "AzureNHError",
    "SubscriptionGoneError",
    # Auth
    "create_sas_token",
    "parse_connection_string",
    # Installation
    "create_browser_installation",
    # Notification factories
    "create_apple_notification",
    "create_apple_body",
    "create_fcm_legacy_notification",
    "create_fcm_legacy_body",
    "create_fcm_v1_notification",
    "create_fcm_v1_body",
    "create_windows_notification",
    "create_windows_toast_notification",
    "create_windows_toast_body",
    "create_windows_tile_notification",
    "create_windows_badge_notification",
    "create_windows_raw_notification",
    "create_windowsphone_notification",
    "create_windowsphone_toast_body",
    "create_adm_notification",
    "create_adm_body",
    "create_baidu_notification",
    "create_baidu_body",
    "create_browser_notification",
    "create_template_notification",
    "create_xiaomi_notification",
]
