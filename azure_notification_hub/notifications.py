"""
Azure Notification Hubs — Platform notification factories.

Ported from @azure/notification-hubs JS SDK:
- notification.js → factory functions (create*Notification)
- notificationBodyBuilder.js → body builders (create*Body)

Supported platforms:
    - Apple (APNs) — create_apple_notification / create_apple_body
    - FCM Legacy (GCM) — create_fcm_legacy_notification / create_fcm_legacy_body
    - FCM V1 — create_fcm_v1_notification / create_fcm_v1_body
    - Windows (WNS) — create_windows_toast/tile/badge/raw_notification
    - ADM (Amazon) — create_adm_notification / create_adm_body
    - Baidu — create_baidu_notification / create_baidu_body
    - Browser (Web Push) — create_browser_notification
    - Template (cross-platform) — create_template_notification
    - Xiaomi — create_xiaomi_notification
"""

import json
from typing import Any

# ─── Constants ───────────────────────────────────────────────────

JSON_CONTENT_TYPE = "application/json;charset=utf-8"
XML_CONTENT_TYPE = "application/xml"
STREAM_CONTENT_TYPE = "application/octet-stream"

# WNS types
WNS_TOAST = "wns/toast"
WNS_TILE = "wns/tile"
WNS_BADGE = "wns/badge"
WNS_RAW = "wns/raw"


# ─── Apple (APNs) ────────────────────────────────────────────────


def create_apple_notification(
    body: dict | str,
    headers: dict[str, str] | None = None,
) -> dict:
    """Create an Apple Push Notification (APNs).

    Args:
        body: Apple native message (dict or JSON string).
              Structure: {"aps": {"alert": {...}, "badge": 1, "sound": "default"}}
        headers: Optional APNs headers:
            - apns-push-type: alert | background | voip | ...
            - apns-priority: "5" | "10"
            - apns-topic: bundle ID
            - apns-collapse-id: collapse identifier
            - apns-expiration: unix timestamp string

    Returns:
        Notification dict ready for send_notification().

    Example:
        >>> body = create_apple_body(alert="Hello", badge=1, sound="default")
        >>> notification = create_apple_notification(body=body)
    """
    return _build_notification("apple", body, headers)


def create_apple_body(
    alert: str | dict | None = None,
    badge: int | None = None,
    sound: str | dict | None = "default",
    category: str | None = None,
    thread_id: str | None = None,
    content_available: int | None = None,
    mutable_content: int | None = None,
    interruption_level: str | None = None,
    relevance_score: float | None = None,
    custom: dict | None = None,
) -> str:
    """Build an Apple APNs native message body.

    Args:
        alert: Alert text (str) or full alert dict.
        badge: Badge count.
        sound: Sound name or dict for critical sounds.
        category: Notification category.
        thread_id: Thread ID for grouping.
        content_available: Set to 1 for silent/background notifications.
        mutable_content: Set to 1 to allow Notification Service Extension.
        interruption_level: passive | active | time-sensitive | critical.
        relevance_score: 0.0–1.0 for notification ordering.
        custom: Additional top-level keys.

    Returns:
        JSON string ready for create_apple_notification().

    Example:
        >>> body = create_apple_body(alert="New message!", badge=3, sound="ping.aiff")
    """
    aps: dict[str, Any] = {}
    if alert is not None:
        aps["alert"] = alert
    if badge is not None:
        aps["badge"] = badge
    if sound is not None:
        aps["sound"] = sound
    if category is not None:
        aps["category"] = category
    if thread_id is not None:
        aps["thread-id"] = thread_id
    if content_available is not None:
        aps["content-available"] = content_available
    if mutable_content is not None:
        aps["mutable-content"] = mutable_content
    if interruption_level is not None:
        aps["interruption-level"] = interruption_level
    if relevance_score is not None:
        aps["relevance-score"] = relevance_score

    message: dict[str, Any] = {"aps": aps}
    if custom:
        message.update(custom)
    return json.dumps(message)


# ─── FCM Legacy (GCM) ───────────────────────────────────────────


def create_fcm_legacy_notification(
    body: dict | str,
    headers: dict[str, str] | None = None,
) -> dict:
    """Create an FCM Legacy (GCM) notification.

    Args:
        body: FCM Legacy native message (dict or JSON string).
        headers: Optional headers.

    Returns:
        Notification dict ready for send_notification().

    Example:
        >>> body = create_fcm_legacy_body(data={"key": "value"}, notification={"title": "Hi"})
        >>> notification = create_fcm_legacy_notification(body=body)
    """
    return _build_notification("gcm", body, headers)


create_gcm_notification = create_fcm_legacy_notification


def create_fcm_legacy_body(
    to: str | None = None,
    registration_ids: list[str] | None = None,
    condition: str | None = None,
    collapse_key: str | None = None,
    priority: str = "high",
    time_to_live: int | None = None,
    restricted_package_name: str | None = None,
    dry_run: bool = False,
    data: dict | None = None,
    notification: dict | None = None,
) -> str:
    """Build an FCM Legacy native message body.

    Args:
        to: Single device token or topic (/topics/xxx).
        registration_ids: List of device tokens (multicast).
        condition: Topic condition (e.g. "'TopicA' in topics && 'TopicB' in topics").
        collapse_key: Collapse key for replacing pending messages.
        priority: "normal" or "high".
        time_to_live: TTL in seconds (max 2419200 = 28 days).
        restricted_package_name: Android package name.
        dry_run: If True, test without actually sending.
        data: Custom data payload (all keys/values must be strings).
        notification: Predefined notification fields (title, body, icon, etc.).

    Returns:
        JSON string ready for create_fcm_legacy_notification().
    """
    message: dict[str, Any] = {"priority": priority, "dry_run": dry_run}
    if to:
        message["to"] = to
    if registration_ids:
        message["registration_ids"] = registration_ids
    if condition:
        message["condition"] = condition
    if collapse_key:
        message["collapse_key"] = collapse_key
    if time_to_live is not None:
        message["time_to_live"] = time_to_live
    if restricted_package_name:
        message["restricted_package_name"] = restricted_package_name
    if data:
        message["data"] = data
    if notification:
        message["notification"] = notification
    return json.dumps(message)


# ─── FCM V1 ──────────────────────────────────────────────────────


def create_fcm_v1_notification(
    body: dict | str,
    headers: dict[str, str] | None = None,
) -> dict:
    """Create an FCM V1 notification.

    Args:
        body: FCM V1 native message (dict or JSON string).
        headers: Optional headers.

    Returns:
        Notification dict ready for send_notification().

    Example:
        >>> body = create_fcm_v1_body(notification={"title": "Hi", "body": "Hello"})
        >>> notification = create_fcm_v1_notification(body=body)
    """
    return _build_notification("fcmv1", body, headers)


def create_fcm_v1_body(
    notification: dict | None = None,
    data: dict | None = None,
    android: dict | None = None,
    webpush: dict | None = None,
    apns: dict | None = None,
    fcm_options: dict | None = None,
    token: str | None = None,
    topic: str | None = None,
    condition: str | None = None,
) -> str:
    """Build an FCM V1 native message body.

    Args:
        notification: Predefined notification fields.
        data: Custom data payload (string key/values).
        android: Android-specific options.
        webpush: Web Push-specific options.
        apns: Apple-specific options (for iOS via FCM).
        fcm_options: FCM options (analytics_label).
        token: Target device token.
        topic: Target topic name.
        condition: Target topic condition.

    Returns:
        JSON string ready for create_fcm_v1_notification().
    """
    message: dict[str, Any] = {}
    if notification:
        message["notification"] = notification
    if data:
        message["data"] = data
    if android:
        message["android"] = android
    if webpush:
        message["webpush"] = webpush
    if apns:
        message["apns"] = apns
    if fcm_options:
        message["fcm_options"] = fcm_options
    if token:
        message["token"] = token
    if topic:
        message["topic"] = topic
    if condition:
        message["condition"] = condition
    return json.dumps(message)


# ─── Windows (WNS) ───────────────────────────────────────────────


def create_windows_notification(
    body: str,
    wns_type: str = WNS_TOAST,
    headers: dict[str, str] | None = None,
) -> dict:
    """Create a Windows Notification (WNS).

    Args:
        body: XML or raw body content.
        wns_type: One of wns/toast, wns/tile, wns/badge, wns/raw.
        headers: Optional headers (X-WNS-* headers).

    Returns:
        Notification dict ready for send_notification().

    Raises:
        ValueError: If wns_type is invalid.

    Example:
        >>> notification = create_windows_notification('<toast>...</toast>', wns_type="wns/toast")
    """
    factories = {
        WNS_TOAST: create_windows_toast_notification,
        WNS_TILE: create_windows_tile_notification,
        WNS_BADGE: create_windows_badge_notification,
        WNS_RAW: create_windows_raw_notification,
    }
    factory = factories.get(wns_type)
    if not factory:
        raise ValueError(f"Invalid WNS type: {wns_type}. Use: {', '.join(factories)}")
    return factory(body, headers)


def create_windows_toast_notification(
    body: str,
    headers: dict[str, str] | None = None,
) -> dict:
    """Create a Windows Toast notification.

    Args:
        body: Toast XML body.
        headers: Optional WNS headers.

    Returns:
        Notification dict.
    """
    return _build_windows(WNS_TOAST, XML_CONTENT_TYPE, body, headers)


def create_windows_tile_notification(
    body: str,
    headers: dict[str, str] | None = None,
) -> dict:
    """Create a Windows Tile notification.

    Args:
        body: Tile XML body.
        headers: Optional WNS headers.

    Returns:
        Notification dict.
    """
    return _build_windows(WNS_TILE, XML_CONTENT_TYPE, body, headers)


def create_windows_badge_notification(
    body: str,
    headers: dict[str, str] | None = None,
) -> dict:
    """Create a Windows Badge notification.

    Args:
        body: Badge XML body.
        headers: Optional WNS headers.

    Returns:
        Notification dict.
    """
    return _build_windows(WNS_BADGE, XML_CONTENT_TYPE, body, headers)


def create_windows_raw_notification(
    body: str,
    headers: dict[str, str] | None = None,
) -> dict:
    """Create a Windows Raw notification.

    Args:
        body: Raw content string.
        headers: Optional WNS headers.

    Returns:
        Notification dict.
    """
    return _build_windows(WNS_RAW, STREAM_CONTENT_TYPE, body, headers)


def create_windows_toast_body(
    text: str,
    launch: str | None = None,
    duration: str | None = None,
    scenario: str | None = None,
) -> str:
    """Build a Windows Toast XML body.

    Args:
        text: Toast text content.
        launch: Deep link / launch arguments.
        duration: "short" | "long".
        scenario: "default" | "alarm" | "incomingCall" | "reminder".

    Returns:
        XML string.

    Example:
        >>> xml = create_windows_toast_body("Hello!", launch="/page")
    """
    attrs = ""
    if launch:
        attrs += f' launch="{launch}"'
    if duration:
        attrs += f' duration="{duration}"'
    if scenario:
        attrs += f' scenario="{scenario}"'
    return (
        f"<toast{attrs}>"
        f"<visual><binding template='ToastText01'>"
        f"<text id='1'>{text}</text>"
        f"</binding></visual>"
        f"</toast>"
    )


def _build_windows(
    wns_type: str,
    content_type: str,
    body: str,
    headers: dict[str, str] | None,
) -> dict:
    """Build a Windows notification with WNS headers."""
    h = dict(headers) if headers else {}
    h.setdefault("X-WNS-Type", wns_type)
    return {
        "platform": "windows",
        "contentType": content_type,
        "body": body,
        "headers": h,
    }


# ─── Windows Phone (MPNS) ────────────────────────────────────────

# MPNS (Microsoft Push Notification Service) is deprecated but still
# supported by Azure Notification Hubs for legacy devices.


def create_windowsphone_notification(
    body: str,
    headers: dict[str, str] | None = None,
) -> dict:
    """Create a Windows Phone notification (MPNS).

    NOTE: MPNS is deprecated. Use this only for legacy Windows Phone 8.x devices.

    Args:
        body: XML body (toast, tile, or raw).
        headers: Optional MPNS headers:
            - X-WindowsPhone-Target: toast | tile | raw
            - X-NotificationClass: 1 (tile) | 2 (toast) | 3 (raw)

    Returns:
        Notification dict ready for send_notification().

    Example:
        >>> notification = create_windowsphone_notification(
        ...     body="<wp:Toast><wp:Text1>Hello</wp:Text1></wp:Toast>",
        ...     headers={"X-WindowsPhone-Target": "toast", "X-NotificationClass": "2"}
        ... )
    """
    result: dict[str, Any] = {
        "platform": "windowsphone",
        "contentType": XML_CONTENT_TYPE,
        "body": body,
        "headers": headers or {},
    }
    return result


def create_windowsphone_toast_body(
    text1: str, text2: str | None = None, param: str | None = None
) -> str:
    """Build a Windows Phone Toast XML body.

    Args:
        text1: Primary text.
        text2: Secondary text.
        param: Navigation parameter.

    Returns:
        XML string.
    """
    xml = f"<wp:Toast><wp:Text1>{text1}</wp:Text1>"
    if text2:
        xml += f"<wp:Text2>{text2}</wp:Text2>"
    if param:
        xml += f"<wp:Param>{param}</wp:Param>"
    xml += "</wp:Toast>"
    return xml


# ─── ADM (Amazon Device Messaging) ──────────────────────────────


def create_adm_notification(
    body: dict | str,
    headers: dict[str, str] | None = None,
) -> dict:
    """Create an ADM (Amazon) notification.

    Args:
        body: ADM native message (dict or JSON string).
        headers: Optional headers.

    Returns:
        Notification dict ready for send_notification().

    Example:
        >>> body = create_adm_body(data={"key": "value"}, consolidation_key="my-key")
        >>> notification = create_adm_notification(body=body)
    """
    return _build_notification("adm", body, headers)


def create_adm_body(
    data: dict | None = None,
    notification: dict | None = None,
    consolidation_key: str | None = None,
    expires_after: int | None = None,
    priority: str = "normal",
) -> str:
    """Build an ADM native message body.

    Args:
        data: Custom data payload.
        notification: Predefined notification fields.
        consolidation_key: Collapse key (max 1 per device).
        expires_after: TTL in seconds (max 604800 = 7 days).
        priority: "normal" or "high".

    Returns:
        JSON string ready for create_adm_notification().
    """
    message: dict[str, Any] = {"priority": priority}
    if data:
        message["data"] = data
    if notification:
        message["notification"] = notification
    if consolidation_key:
        message["consolidationKey"] = consolidation_key
    if expires_after is not None:
        message["expiresAfter"] = expires_after
    return json.dumps(message)


# ─── Baidu ───────────────────────────────────────────────────────


def create_baidu_notification(
    body: dict | str,
    headers: dict[str, str] | None = None,
) -> dict:
    """Create a Baidu Push notification.

    Args:
        body: Baidu native message (dict or JSON string).
        headers: Optional headers.

    Returns:
        Notification dict ready for send_notification().

    Example:
        >>> body = create_baidu_body(title="Hello", description="World")
        >>> notification = create_baidu_notification(body=body)
    """
    return _build_notification("baidu", body, headers)


def create_baidu_body(
    title: str | None = None,
    description: str | None = None,
    notification_builder_id: int = 0,
    notification_basic_style: int = 0,
    open_type: int = 1,
    url: str | None = None,
    custom_content: dict | None = None,
) -> str:
    """Build a Baidu native message body.

    Args:
        title: Notification title.
        description: Notification description/body.
        notification_builder_id: Custom notification builder ID.
        notification_basic_style: Basic style flags (bitmask).
        open_type: 1=open app, 2=open URL, 3=open intent.
        url: URL to open (if open_type=2).
        custom_content: Custom key-value data.

    Returns:
        JSON string ready for create_baidu_notification().
    """
    message: dict[str, Any] = {
        "notification_builder_id": notification_builder_id,
        "notification_basic_style": notification_basic_style,
        "open_type": open_type,
    }
    if title:
        message["title"] = title
    if description:
        message["description"] = description
    if url:
        message["url"] = url
    if custom_content:
        message["custom_content"] = custom_content
    return json.dumps(message)


# ─── Browser (Web Push) ──────────────────────────────────────────


def create_browser_notification(
    body: dict | str,
    headers: dict[str, str] | None = None,
) -> dict:
    """Create a Browser Web Push notification.

    Args:
        body: Browser push payload (dict or JSON string).
              Typically: {"title": "...", "body": "...", "icon": "...", "url": "..."}
        headers: Optional headers.

    Returns:
        Notification dict ready for send_notification().

    Example:
        >>> notification = create_browser_notification({"title": "Hello", "body": "World"})
    """
    return _build_notification("browser", body, headers)


# ─── Template ────────────────────────────────────────────────────


def create_template_notification(
    body: dict | str,
    headers: dict[str, str] | None = None,
) -> dict:
    """Create a Template notification (cross-platform).

    Template registrations define platform-specific templates.
    The body contains data to fill template variables.

    Args:
        body: Key-value data matching template placeholders (dict or JSON string).
              Example: {"message": "Hello", "badge": 1, "sound": "default"}
        headers: Optional headers.

    Returns:
        Notification dict ready for send_notification().

    Example:
        >>> notification = create_template_notification({"message": "Hello!", "badge": 1})
    """
    return _build_notification("template", body, headers)


# ─── Xiaomi ──────────────────────────────────────────────────────


def create_xiaomi_notification(
    body: dict | str,
    headers: dict[str, str] | None = None,
) -> dict:
    """Create a Xiaomi Push notification.

    Args:
        body: Xiaomi native message (dict or JSON string).
        headers: Optional headers.

    Returns:
        Notification dict ready for send_notification().

    Example:
        >>> notification = create_xiaomi_notification({"title": "Hello", "body": "World"})
    """
    return _build_notification("xiaomi", body, headers)


# ─── Internal Helpers ────────────────────────────────────────────


def _build_notification(
    platform: str,
    body: dict | str,
    headers: dict[str, str] | None,
) -> dict:
    """Build a notification dict for the given platform."""
    payload = _ensure_string(body)
    result: dict[str, Any] = {
        "platform": platform,
        "contentType": JSON_CONTENT_TYPE,
        "body": payload,
    }
    if headers:
        result["headers"] = headers
    return result


def _ensure_string(body: dict | str) -> str:
    """Convert dict to JSON string, pass through if already string."""
    if isinstance(body, str):
        return body
    return json.dumps(body)
