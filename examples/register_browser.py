"""Example: Register a browser for web push."""

from azure_notification_hub import NotificationHubsClient, create_browser_installation

client = NotificationHubsClient(
    connection_string="Endpoint=sb://...;SharedAccessKeyName=...;SharedAccessKey=...",
    hub_name="myhub",
)

installation = create_browser_installation(
    installation_id="my-unique-id",
    push_channel={
        "endpoint": "https://fcm.googleapis.com/fcm/send/...",
        "p256dh": "BNn...",
        "auth": "abc...",
    },
    tags=["user:123", "all", "web"],
    expiration_time="2026-12-31T23:59:59Z",
)

result = client.create_or_update_installation(installation)
print(f"Registered: {result}")
