"""Example: Send an Apple Push Notification (APNs)."""

from azure_notification_hub import (
    NotificationHubsClient,
    create_apple_body,
    create_apple_notification,
)

client = NotificationHubsClient(
    connection_string="Endpoint=sb://...;SharedAccessKeyName=...;SharedAccessKey=...",
    hub_name="myhub",
)

body = create_apple_body(
    alert={"title": "New Message", "body": "You have a new message"},
    badge=3,
    sound="ping.aiff",
    category="MESSAGE",
    thread_id="chat-123",
    interruption_level="active",
)

notification = create_apple_notification(
    body=body,
    headers={"apns-topic": "com.example.app"},
)

result = client.send_notification(notification, tag_expression="user:123")
print(f"Sent: {result}")
