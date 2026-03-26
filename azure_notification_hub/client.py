"""
Azure Notification Hubs REST API client.

Python port of @azure/notification-hubs JS SDK (NotificationHubsClient).
Supports all operations: installations, notifications, registrations, scheduling, analytics.

Example:
    >>> from azure_notification_hub import NotificationHubsClient, create_browser_notification
    >>> client = NotificationHubsClient("Endpoint=sb://...", "my-hub")
    >>> notification = create_browser_notification({"title": "Hi", "body": "Hello"})
    >>> result = client.send_notification(notification, tag_expression="user:123")
"""

import json
import logging
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any

import httpx

from azure_notification_hub.auth import create_sas_token, parse_connection_string
from azure_notification_hub.notifications import JSON_CONTENT_TYPE

logger = logging.getLogger("azure_notification_hub")

API_VERSION = "2020-06"


# ─── Exceptions ──────────────────────────────────────────────────


class AzureNHError(Exception):
    """Base exception for Azure Notification Hubs errors."""

    def __init__(self, status_code: int, body: str):
        self.status_code = status_code
        self.body = body
        super().__init__(f"Azure NH error {status_code}: {body}")


class SubscriptionGoneError(AzureNHError):
    """Raised when a push subscription has expired (HTTP 410)."""

    def __init__(self, body: str):
        super().__init__(410, body)


# ─── Client ──────────────────────────────────────────────────────


class NotificationHubsClient:
    """Azure Notification Hubs REST API client.

    Mirrors the Node.js @azure/notification-hubs SDK's NotificationHubsClient.

    Args:
        connection_string: Access Policy connection string from Azure Portal.
        hub_name: The Notification Hub name.

    Example:
        >>> client = NotificationHubsClient(
        ...     connection_string="Endpoint=sb://ns.servicebus.windows.net/;SharedAccessKeyName=DefaultFullSharedAccessSignature;SharedAccessKey=abc=;EntityPath=myhub",
        ...     hub_name="myhub"
        ... )
    """

    def __init__(self, connection_string: str, hub_name: str):
        parsed = parse_connection_string(connection_string)
        self._hub_name = hub_name
        self._endpoint = parsed["endpoint"].replace("sb://", "https://")
        self._shared_access_key = parsed["shared_access_key"]
        self._shared_access_key_name = parsed["shared_access_key_name"]
        self._entity_path = parsed.get("entity_path")
        self._client = httpx.Client(timeout=30)

        logger.info(
            f"Initialized | endpoint={self._endpoint} "
            f"hub={hub_name} entity={self._entity_path} "
            f"key={self._shared_access_key_name}"
        )

    # ─── URL / Headers ───────────────────────────────────────────

    def _base_url(self) -> str:
        base = self._endpoint.rstrip("/")
        hub_path = self._entity_path or self._hub_name
        return f"{base}/{hub_path}"

    def _request_url(self, path: str = "", extra_params: dict | None = None) -> str:
        url = f"{self._base_url()}{path}?api-version={API_VERSION}"
        if extra_params:
            for k, v in extra_params.items():
                url += f"&{k}={v}"
        return url

    def _create_headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        token = create_sas_token(
            self._shared_access_key_name,
            self._shared_access_key,
            self._endpoint,
        )
        headers = {
            "Authorization": token,
            "x-ms-version": API_VERSION,
            "x-ms-azsdk-telemetry": "class=NotificationHubsClient;method=python",
        }
        if extra:
            headers.update(extra)
        return headers

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        logger.debug(f"Response {response.status_code} | {response.text[:500]}")

        if response.status_code == 410:
            raise SubscriptionGoneError(response.text)
        if response.status_code >= 400:
            raise AzureNHError(response.status_code, response.text)
        if response.status_code == 204 or not response.content:
            return {}

        content_type = response.headers.get("content-type", "")
        if "xml" in content_type:
            return {"_raw_xml": response.text}
        return response.json()

    # ─── Installations ───────────────────────────────────────────

    def create_or_update_installation(self, installation: dict) -> dict:
        """Create or overwrite an installation.

        Args:
            installation: Installation dict (use create_browser_installation() helper).

        Returns:
            Response dict from Azure.

        Example:
            >>> from azure_notification_hub import create_browser_installation
            >>> inst = create_browser_installation(
            ...     installation_id="my-id",
            ...     push_channel={"endpoint": "...", "p256dh": "...", "auth": "..."},
            ...     tags=["user:123"]
            ... )
            >>> client.create_or_update_installation(inst)
        """
        installation_id = installation["installationId"]
        url = self._request_url(f"/installations/{installation_id}")
        headers = self._create_headers()
        headers["Content-Type"] = "application/json"
        body = json.dumps(installation)

        logger.info(f"PUT /installations/{installation_id}")
        resp = self._client.put(url, content=body, headers=headers)
        return self._handle_response(resp)

    def delete_installation(self, installation_id: str) -> dict:
        """Delete an installation.

        Args:
            installation_id: The installation ID to delete.

        Returns:
            Response dict from Azure.
        """
        url = self._request_url(f"/installations/{installation_id}")
        headers = self._create_headers()
        logger.info(f"DELETE /installations/{installation_id}")
        resp = self._client.delete(url, headers=headers)
        return self._handle_response(resp)

    def get_installation(self, installation_id: str) -> dict:
        """Get an installation by ID.

        Args:
            installation_id: The installation ID.

        Returns:
            Installation dict.
        """
        url = self._request_url(f"/installations/{installation_id}")
        headers = self._create_headers()
        logger.info(f"GET /installations/{installation_id}")
        resp = self._client.get(url, headers=headers)
        return self._handle_response(resp)

    def update_installation(self, installation_id: str, patches: list[dict]) -> dict:
        """Update an installation using JSON Patch (RFC6902).

        Args:
            installation_id: The installation ID.
            patches: List of JSON Patch operations.

        Returns:
            Response dict from Azure.
        """
        url = self._request_url(f"/installations/{installation_id}")
        headers = self._create_headers()
        headers["Content-Type"] = "application/json"
        body = json.dumps(patches)

        logger.info(f"PATCH /installations/{installation_id}")
        resp = self._client.patch(url, content=body, headers=headers)
        return self._handle_response(resp)

    # ─── Notifications ───────────────────────────────────────────

    def send_notification(
        self,
        notification: dict,
        tag_expression: str | None = None,
        test_send: bool = False,
        ttl: int | None = None,
        urgency: str | None = None,
    ) -> dict:
        """Send a notification to devices matching a tag expression.

        Args:
            notification: Notification dict from a factory (e.g. create_browser_notification()).
            tag_expression: Tag expression to target devices (e.g. "user:123").
            test_send: If True, use Azure test send (no actual delivery).
            ttl: Time-to-live in seconds.
            urgency: "low" | "normal" | "high".

        Returns:
            Dict with trackingId, correlationId, successCount, etc.

        Example:
            >>> from azure_notification_hub import create_browser_notification
            >>> notification = create_browser_notification({"title": "Hello", "body": "World"})
            >>> result = client.send_notification(notification, tag_expression="user:123")
        """
        url = self._request_url("/messages")
        headers = self._create_headers()

        headers["ServiceBusNotification-Format"] = notification.get("platform", "browser")
        headers["Content-Type"] = notification.get("contentType", JSON_CONTENT_TYPE)

        for k, v in notification.get("headers", {}).items():
            headers[k] = v

        if tag_expression:
            headers["ServiceBusNotification-Tags"] = tag_expression
        if test_send:
            headers["ServiceBusNotification-TestSend"] = "true"
        if ttl is not None:
            headers["ServiceBusNotification-TimeToLive"] = str(ttl)
        if urgency:
            headers["ServiceBusNotification-Urgency"] = urgency

        body = notification.get("body", "")
        platform = notification.get("platform", "unknown")

        logger.info(
            f"POST /messages | platform={platform} tags={tag_expression} "
            f"ttl={ttl} urgency={urgency}"
        )

        resp = self._client.post(url, content=body, headers=headers)
        return self._handle_response(resp)

    def send_broadcast_notification(
        self,
        notification: dict,
        test_send: bool = False,
        ttl: int | None = None,
        urgency: str | None = None,
    ) -> dict:
        """Send a notification to all registered devices.

        Args:
            notification: Notification dict from a factory.
            test_send: If True, use Azure test send.
            ttl: Time-to-live in seconds.
            urgency: "low" | "normal" | "high".

        Returns:
            Dict with trackingId, correlationId, etc.
        """
        return self.send_notification(
            notification,
            tag_expression=None,
            test_send=test_send,
            ttl=ttl,
            urgency=urgency,
        )

    # ─── Scheduled Notifications (Standard SKU) ──────────────────

    def schedule_notification(
        self,
        scheduled_time: datetime,
        notification: dict,
        tag_expression: str | None = None,
    ) -> dict:
        """Schedule a notification for future delivery.

        NOTE: Requires Standard SKU or above.

        Args:
            scheduled_time: When to deliver the notification.
            notification: Notification dict from a factory.
            tag_expression: Tag expression to target devices.

        Returns:
            Dict with trackingId, etc.
        """
        url = self._request_url("/schedulednotifications")
        headers = self._create_headers()
        headers["ServiceBusNotification-Format"] = notification.get("platform", "browser")
        headers["Content-Type"] = notification.get("contentType", JSON_CONTENT_TYPE)
        headers["ServiceBusNotification-ScheduleTime"] = scheduled_time.isoformat()

        for k, v in notification.get("headers", {}).items():
            headers[k] = v

        if tag_expression:
            headers["ServiceBusNotification-Tags"] = tag_expression

        body = notification.get("body", "")

        logger.info(f"POST /schedulednotifications | at={scheduled_time} tags={tag_expression}")
        resp = self._client.post(url, content=body, headers=headers)
        return self._handle_response(resp)

    def schedule_broadcast_notification(
        self,
        scheduled_time: datetime,
        notification: dict,
    ) -> dict:
        """Schedule a broadcast notification for future delivery.

        Args:
            scheduled_time: When to deliver.
            notification: Notification dict from a factory.

        Returns:
            Dict with trackingId, etc.
        """
        return self.schedule_notification(scheduled_time, notification)

    def cancel_scheduled_notification(self, notification_id: str) -> dict:
        """Cancel a scheduled notification.

        Args:
            notification_id: The notification ID from the scheduled send.

        Returns:
            Response dict from Azure.
        """
        url = self._request_url(f"/schedulednotifications/{notification_id}")
        headers = self._create_headers()
        logger.info(f"DELETE /schedulednotifications/{notification_id}")
        resp = self._client.delete(url, headers=headers)
        return self._handle_response(resp)

    # ─── Analytics ───────────────────────────────────────────────

    def get_notification_outcome_details(self, notification_id: str) -> dict:
        """Get delivery outcome for a sent notification.

        Args:
            notification_id: The trackingId from a send operation.

        Returns:
            Outcome details dict.
        """
        url = self._request_url(f"/messages/{notification_id}")
        headers = self._create_headers()
        logger.info(f"GET /messages/{notification_id}")
        resp = self._client.get(url, headers=headers)
        return self._handle_response(resp)

    def get_feedback_container_url(self) -> str:
        """Get the PNS feedback container URL.

        Returns:
            Azure Storage container URL for feedback data.
        """
        url = self._request_url("/feedbackcontainer")
        headers = self._create_headers()
        logger.info("GET /feedbackcontainer")
        resp = self._client.get(url, headers=headers)
        data = self._handle_response(resp)
        return data.get("url", "")

    # ─── Registrations ───────────────────────────────────────────

    def list_registrations(self, top: int = 100) -> list[dict]:
        """List all registrations.

        Args:
            top: Max number of registrations to return.

        Returns:
            List of registration dicts.
        """
        url = self._request_url("/registrations", extra_params={"$top": top})
        headers = self._create_headers()
        logger.info("GET /registrations")
        resp = self._client.get(url, headers=headers)

        if resp.status_code >= 400:
            raise AzureNHError(resp.status_code, resp.text)

        return self._parse_atom_entries(resp.text)

    def get_registration(self, registration_id: str) -> dict:
        """Get a registration by ID.

        Args:
            registration_id: The registration ID.

        Returns:
            Registration dict.
        """
        url = self._request_url(f"/registrations/{registration_id}")
        headers = self._create_headers()
        logger.info(f"GET /registrations/{registration_id}")
        resp = self._client.get(url, headers=headers)

        if resp.status_code >= 400:
            raise AzureNHError(resp.status_code, resp.text)

        return self._parse_atom_entry(resp.text)

    def delete_registration(self, registration_id: str) -> dict:
        """Delete a registration by ID.

        Args:
            registration_id: The registration ID to delete.

        Returns:
            Response dict from Azure.
        """
        url = self._request_url(f"/registrations/{registration_id}")
        headers = self._create_headers()
        logger.info(f"DELETE /registrations/{registration_id}")
        resp = self._client.delete(url, headers=headers)
        return self._handle_response(resp)

    # ─── XML Parsing (Atom Feed) ─────────────────────────────────

    def _parse_atom_entries(self, xml_text: str) -> list[dict]:
        """Parse Atom feed XML into a list of dicts."""
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "m": "http://schemas.microsoft.com/ado/2007/08/dataservices/metadata",
            "d": "http://schemas.microsoft.com/ado/2007/08/dataservices",
        }
        root = ET.fromstring(xml_text)
        return [self._extract_entry(entry, ns) for entry in root.findall("atom:entry", ns)]

    def _parse_atom_entry(self, xml_text: str) -> dict:
        """Parse a single Atom entry."""
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "m": "http://schemas.microsoft.com/ado/2007/08/dataservices/metadata",
            "d": "http://schemas.microsoft.com/ado/2007/08/dataservices",
        }
        root = ET.fromstring(xml_text)
        return self._extract_entry(root, ns)

    def _extract_entry(self, entry, ns: dict) -> dict:
        """Extract fields from an Atom entry."""
        result = {}

        title_el = entry.find("atom:title", ns)
        if title_el is not None and title_el.text:
            result["title"] = title_el.text

        updated_el = entry.find("atom:updated", ns)
        if updated_el is not None and updated_el.text:
            result["updated"] = updated_el.text

        etag = entry.get("{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}etag")
        if etag:
            result["etag"] = etag

        content = entry.find("atom:content", ns)
        if content is not None:
            properties = content.find("m:properties", ns)
            if properties is not None:
                for prop in properties:
                    tag = prop.tag.split("}")[-1] if "}" in prop.tag else prop.tag
                    result[tag] = prop.text
            else:
                for child in content:
                    tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                    if tag.endswith("RegistrationDescription") or tag.endswith("Installation"):
                        for prop in child:
                            prop_tag = prop.tag.split("}")[-1] if "}" in prop.tag else prop.tag
                            value = prop.text
                            if prop_tag == "Tags" and value:
                                value = [t.strip() for t in value.split(",")]
                            result[prop_tag] = value
                    elif tag not in ("title", "content"):
                        result[tag] = child.text

        id_el = entry.find("atom:id", ns)
        if id_el is not None and id_el.text:
            result["id"] = id_el.text

        return result

    # ─── Lifecycle ───────────────────────────────────────────────

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __repr__(self):
        return f"<NotificationHubsClient hub={self._hub_name} endpoint={self._endpoint}>"


# ─── Installation Factory ────────────────────────────────────────


def create_browser_installation(
    installation_id: str,
    push_channel: dict,
    tags: list[str] | None = None,
    expiration_time: str | None = None,
) -> dict:
    """Create a browser push installation object.

    Args:
        installation_id: Unique ID for this installation (e.g. UUID).
        push_channel: Dict with endpoint, p256dh, auth from PushSubscription.
        tags: Tags for targeting (e.g. ["user:123", "all", "web"]).
        expiration_time: ISO 8601 expiration datetime.

    Returns:
        Installation dict ready for create_or_update_installation().

    Example:
        >>> inst = create_browser_installation(
        ...     installation_id="abc-123",
        ...     push_channel={
        ...         "endpoint": "https://fcm.googleapis.com/fcm/send/...",
        ...         "p256dh": "BKy...",
        ...         "auth": "abc..."
        ...     },
        ...     tags=["user:123", "all", "web"]
        ... )
    """
    installation: dict[str, Any] = {
        "installationId": installation_id,
        "platform": "browser",
        "pushChannel": push_channel,
    }
    if tags:
        installation["tags"] = tags
    if expiration_time:
        installation["expirationTime"] = expiration_time
    return installation
