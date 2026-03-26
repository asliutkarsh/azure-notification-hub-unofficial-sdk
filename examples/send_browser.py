"""Example: Send a web push notification."""

from azure_notification_hub import NotificationHubsClient, create_browser_notification

client = NotificationHubsClient(
    connection_string="Endpoint=sb://...;SharedAccessKeyName=...;SharedAccessKey=...",
    hub_name="myhub",
)

notification = create_browser_notification(
    body={"title": "Hello!", "body": "World", "url": "/dashboard"}
)

result = client.send_notification(notification, tag_expression="user:123")
print(f"Sent: trackingId={result.get('trackingId')}, success={result.get('successCount')}")
