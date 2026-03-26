"""Example: Send an FCM V1 notification (Android)."""

from azure_notification_hub import (
    NotificationHubsClient,
    create_fcm_v1_body,
    create_fcm_v1_notification,
)

client = NotificationHubsClient(
    connection_string="Endpoint=sb://...;SharedAccessKeyName=...;SharedAccessKey=...",
    hub_name="myhub",
)

body = create_fcm_v1_body(
    notification={"title": "Hello", "body": "This is a test"},
    data={"orderId": "12345", "type": "order_update"},
    android={
        "priority": "high",
        "notification": {"channel_id": "orders", "sound": "default"},
    },
)

notification = create_fcm_v1_notification(body=body)
result = client.send_notification(notification, tag_expression="user:123")
print(f"Sent: {result}")
