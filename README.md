# azure-notification-hub-unofficial

[![PyPI version](https://img.shields.io/pypi/v/azure-notification-hub-unofficial)](https://pypi.org/project/azure-notification-hub-unofficial/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Unofficial Python SDK for **Azure Notification Hubs** — a port of the official [@azure/notification-hubs](https://www.npmjs.com/package/@azure/notification-hubs) Node.js SDK.

Sends push notifications to **Apple (APNs)**, **Firebase (FCM/GCM)**, **Windows (WNS)**, **Amazon (ADM)**, **Baidu**, **Browser (Web Push)**, **Xiaomi**, and **Template** registrations.

## Why This Exists

Azure provides **two official packages** for Notification Hubs in Python:

| Package | Purpose | Can send notifications? |
|---|---|---|
| [`azure-mgmt-notificationhubs`](https://pypi.org/project/azure-mgmt-notificationhubs/) | **Management** — create/delete hubs, namespaces, policies | ❌ No |
| [`azure-notificationhubs`](https://www.npmjs.com/package/@azure/notification-hubs) (Node.js) | **Operations** — send notifications, manage registrations | ✅ Yes, but Node.js only |

There is **no official Python SDK** for sending notifications. Microsoft's own [documentation](https://learn.microsoft.com/en-us/azure/notification-hubs/notification-hubs-python-push-notification-rest-wrapper) recommends using raw REST API calls or a community wrapper.

This package fills that gap — it's a **1:1 port** of the Node.js SDK's REST API client, built on `httpx`.

## Install

```bash
pip install azure-notification-hub-unofficial
```

## Quick Start

```python
from azure_notification_hub import (
    NotificationHubsClient,
    create_browser_notification,
    create_browser_installation,
)

# 1. Create client
client = NotificationHubsClient(
    connection_string="Endpoint=sb://...;SharedAccessKeyName=...;SharedAccessKey=...;EntityPath=myhub",
    hub_name="myhub",
)

# 2. Register a device (installation)
installation = create_browser_installation(
    installation_id="unique-id-123",
    push_channel={
        "endpoint": "https://fcm.googleapis.com/fcm/send/...",
        "p256dh": "BNn...",
        "auth": "abc..."
    },
    tags=["user:123", "all", "web"],
)
client.create_or_update_installation(installation)

# 3. Send a notification
notification = create_browser_notification(
    body={"title": "Hello!", "body": "This is a test."}
)
result = client.send_notification(notification, tag_expression="user:123")
print(result)  # {'trackingId': '...', 'successCount': 1, ...}
```

## Supported Platforms

| Platform | Factory | Body Builder |
|---|---|---|
| **Apple (APNs)** | `create_apple_notification()` | `create_apple_body()` |
| **FCM Legacy (GCM)** | `create_fcm_legacy_notification()` | `create_fcm_legacy_body()` |
| **FCM V1** | `create_fcm_v1_notification()` | `create_fcm_v1_body()` |
| **Windows (WNS)** | `create_windows_toast_notification()` | `create_windows_toast_body()` |
| **Windows Tile** | `create_windows_tile_notification()` | — |
| **Windows Badge** | `create_windows_badge_notification()` | — |
| **Windows Raw** | `create_windows_raw_notification()` | — |
| **ADM (Amazon)** | `create_adm_notification()` | `create_adm_body()` |
| **Baidu** | `create_baidu_notification()` | `create_baidu_body()` |
| **Browser (Web Push)** | `create_browser_notification()` | — |
| **Template** | `create_template_notification()` | — |
| **Xiaomi** | `create_xiaomi_notification()` | — |

## Examples

### Apple (APNs)

```python
from azure_notification_hub import create_apple_notification, create_apple_body

body = create_apple_body(
    alert="New message!",
    badge=3,
    sound="ping.aiff",
    category="MESSAGE",
    interruption_level="active",
)
notification = create_apple_notification(
    body=body,
    headers={"apns-topic": "com.example.app"},
)
client.send_notification(notification, tag_expression="user:123")
```

### FCM V1 (Android / cross-platform)

```python
from azure_notification_hub import create_fcm_v1_notification, create_fcm_v1_body

body = create_fcm_v1_body(
    notification={"title": "Hello", "body": "World"},
    data={"key1": "value1", "key2": "value2"},
    android={"priority": "high"},
)
notification = create_fcm_v1_notification(body=body)
client.send_notification(notification, tag_expression="user:123")
```

### Windows Toast

```python
from azure_notification_hub import create_windows_toast_notification, create_windows_toast_body

body = create_windows_toast_body(text="Hello!", launch="/page", duration="long")
notification = create_windows_toast_notification(body=body)
client.send_notification(notification, tag_expression="user:123")
```

### Template (cross-platform)

```python
from azure_notification_hub import create_template_notification

# Template registrations define platform-specific templates.
# This sends data to fill those templates.
notification = create_template_notification(body={
    "message": "Hello!",
    "badge": 1,
    "sound": "default",
})
client.send_notification(notification, tag_expression="user:123")
```

### Tag-based Targeting

```python
# Send to a specific user
client.send_notification(notification, tag_expression="user:123")

# Send to a user AND platform
client.send_notification(notification, tag_expression="user:123 AND web")

# Broadcast to all
client.send_broadcast_notification(notification)
```

### TTL and Urgency

```python
client.send_notification(
    notification,
    tag_expression="user:123",
    ttl=60,          # expires after 60 seconds
    urgency="high",  # high | normal | low
)
```

### Scheduled (Standard SKU)

```python
from datetime import datetime, timedelta, timezone

scheduled_time = datetime.now(timezone.utc) + timedelta(minutes=5)
client.schedule_notification(scheduled_time, notification, tag_expression="user:123")
```

### Registrations (debug)

```python
# List all registrations
regs = client.list_registrations()
for reg in regs:
    print(reg["Tags"], reg["RegistrationId"])

# Get a specific registration
reg = client.get_registration("registration-id-here")
```

### Analytics

```python
# Get delivery outcome
outcome = client.get_notification_outcome_details("tracking-id-here")

# Get feedback container URL
url = client.get_feedback_container_url()
```

## Authentication

The SDK uses **SAS token authentication** — the same as the Node.js SDK.

```python
from azure_notification_hub import create_sas_token

token = create_sas_token(
    shared_access_key_name="DefaultFullSharedAccessSignature",
    shared_access_key="your-key-here",
    audience="https://myns.servicebus.windows.net/",
)
# Returns: "SharedAccessSignature sr=...&sig=...&se=...&skn=..."
```

## Connection String Format

```
Endpoint=sb://<namespace>.servicebus.windows.net/;SharedAccessKeyName=<policy>;SharedAccessKey=<key>[;EntityPath=<hub-name>]
```

Get this from: **Azure Portal → Notification Hub → Access Policies → DefaultFullSharedAccessSignature**.

## Error Handling

```python
from azure_notification_hub import AzureNHError, SubscriptionGoneError

try:
    client.send_notification(notification, tag_expression="user:123")
except SubscriptionGoneError:
    # 410 — subscription expired, delete the installation
    client.delete_installation(installation_id)
except AzureNHError as e:
    print(f"Error {e.status_code}: {e.body}")
```

## Architecture

```
your-code
  ↓
NotificationHubsClient (this SDK)
  ↓
Azure Notification Hubs REST API (2020-06)
  ↓
Platform Push Services (FCM, APNs, WNS, ADM, Baidu)
  ↓
Device / Browser
```

## Why Unofficial?

**Azure does not provide an official Python SDK for sending notifications.**

| Official Package | What It Does |
|---|---|
| `azure-mgmt-notificationhubs` | **Resource management** — create/delete Notification Hub namespaces and hubs. Uses Azure Resource Manager API. |
| `@azure/notification-hubs` (Node.js) | **Send notifications** — full operations SDK. But Node.js only. |

For Python, Microsoft's [official documentation](https://learn.microsoft.com/en-us/azure/notification-hubs/notification-hubs-python-push-notification-rest-wrapper) recommends building your own REST client or using a community wrapper.

This SDK is that community wrapper — a **complete port** of the Node.js SDK covering:
- All 9 notification platforms
- Installation management
- Tag-based targeting
- Scheduled sends (Standard SKU)
- TTL / Urgency
- Registration management
- Analytics / feedback

This SDK is a **1:1 port** of the Node.js SDK with full platform support.

## Comparison with Node.js SDK

| Feature | Node.js (`@azure/notification-hubs`) | This SDK |
|---|---|---|
| Installations | ✅ | ✅ |
| All platforms | ✅ | ✅ |
| Tag expressions | ✅ | ✅ |
| Scheduled sends | ✅ | ✅ |
| TTL / Urgency | ✅ | ✅ |
| Registrations | ✅ | ✅ |
| Analytics | ✅ | ✅ |
| Async | ✅ (Promises) | Sync (httpx.Client) |

## License

MIT
