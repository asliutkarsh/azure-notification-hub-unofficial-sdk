"""
Azure Notification Hubs authentication — SAS token generation and connection string parsing.

Ported from @azure/notification-hubs JS SDK:
- sasTokenCredential.js → create_sas_token()
- connectionStringUtils.js → parse_connection_string()
- hmacSha256.js → sign_string()
"""

import base64
import hashlib
import hmac
import time
from urllib.parse import quote


def sign_string(key: str, to_sign: str) -> str:
    """HMAC-SHA256 sign, base64 encode, URL encode.

    Ported from the JS SDK's hmacSha256.js.

    Args:
        key: Shared access key.
        to_sign: String to sign.

    Returns:
        URL-encoded base64 HMAC-SHA256 signature.
    """
    sig = hmac.new(
        key.encode("utf-8"),
        to_sign.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    encoded = base64.b64encode(sig).decode("utf-8")
    return quote(encoded, safe="")


def create_sas_token(
    shared_access_key_name: str,
    shared_access_key: str,
    audience: str,
    expiry: int | None = None,
) -> str:
    """Create a SAS token for Azure Notification Hubs.

    Generates a token in the format:
        SharedAccessSignature sr=<resource>&sig=<signature>&se=<expiry>&skn=<keyname>

    Ported from the JS SDK's SasTokenCredential.getToken().

    Args:
        shared_access_key_name: The shared access key name (e.g. "DefaultFullSharedAccessSignature").
        shared_access_key: The shared access key value.
        audience: The resource URI (endpoint).
        expiry: Unix timestamp for token expiry. Defaults to now + 1 hour.

    Returns:
        SAS token string ready for the Authorization header.

    Example:
        >>> token = create_sas_token("DefaultFullSharedAccessSignature", "abc123...", "https://myns.servicebus.windows.net/")
    """
    if expiry is None:
        expiry = int(time.time()) + 3600  # 1 hour

    audience = quote(audience.lower(), safe="")
    key_name = quote(shared_access_key_name, safe="")

    string_to_sign = f"{audience}\n{expiry}"
    sig = sign_string(shared_access_key, string_to_sign)

    return f"SharedAccessSignature sr={audience}&sig={sig}&se={expiry}&skn={key_name}"


def parse_connection_string(connection_string: str) -> dict:
    """Parse an Azure Service Bus / Notification Hub connection string.

    Connection string format:
        Endpoint=sb://...;SharedAccessKeyName=...;SharedAccessKey=...[;EntityPath=...]

    Ported from the JS SDK's parseNotificationHubsConnectionString().

    Args:
        connection_string: The connection string to parse.

    Returns:
        Dict with keys: endpoint, shared_access_key, shared_access_key_name, entity_path.

    Raises:
        ValueError: If the connection string is malformed.

    Example:
        >>> parsed = parse_connection_string("Endpoint=sb://ns.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=abc=")
        >>> parsed["endpoint"]
        'sb://ns.servicebus.windows.net/'
    """
    result = {}
    parts = connection_string.strip().split(";")

    for part in parts:
        part = part.strip()
        if not part:
            continue
        eq_idx = part.index("=")
        key = part[:eq_idx].strip()
        value = part[eq_idx + 1 :].strip()
        result[key] = value

    if "Endpoint" not in result:
        raise ValueError("Connection string missing 'Endpoint'")

    if "SharedAccessKey" in result and "SharedAccessKeyName" not in result:
        raise ValueError("Connection string with SharedAccessKey needs SharedAccessKeyName")

    if "SharedAccessKeyName" in result and "SharedAccessKey" not in result:
        raise ValueError("Connection string with SharedAccessKeyName needs SharedAccessKey")

    return {
        "endpoint": result["Endpoint"],
        "shared_access_key": result.get("SharedAccessKey"),
        "shared_access_key_name": result.get("SharedAccessKeyName"),
        "entity_path": result.get("EntityPath"),
    }
