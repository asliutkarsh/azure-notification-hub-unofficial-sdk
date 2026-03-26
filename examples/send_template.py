"""Example: Send a Template notification (cross-platform)."""

from azure_notification_hub import NotificationHubsClient, create_template_notification

client = NotificationHubsClient(
    connection_string="Endpoint=sb://...;SharedAccessKeyName=...;SharedAccessKey=...",
    hub_name="myhub",
)

# Template registrations define platform-specific templates.
# This sends data to fill those template variables.
notification = create_template_notification(
    body={
        "message": "Hello from Python!",
        "badge": 1,
        "sound": "default",
        "title": "Test",
    }
)

result = client.send_notification(notification, tag_expression="user:123")
print(f"Sent: {result}")
