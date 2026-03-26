"""Tests for azure_notification_hub.auth module."""

import pytest

from azure_notification_hub.auth import (
    create_sas_token,
    parse_connection_string,
    sign_string,
)


def test_sign_string():
    sig = sign_string("mykey", "mysign")
    assert isinstance(sig, str)
    assert len(sig) > 0
    # Same input = same output
    assert sign_string("mykey", "mysign") == sig


def test_sign_string_different_inputs():
    sig1 = sign_string("key1", "sign1")
    sig2 = sign_string("key2", "sign2")
    assert sig1 != sig2


def test_create_sas_token():
    token = create_sas_token("my-policy", "my-key", "https://ns.servicebus.windows.net/")
    assert token.startswith("SharedAccessSignature sr=")
    assert "&sig=" in token
    assert "&se=" in token
    assert "&skn=my-policy" in token


def test_create_sas_token_with_expiry():
    token = create_sas_token(
        "my-policy", "my-key", "https://ns.servicebus.windows.net/", expiry=1000000
    )
    assert "se=1000000" in token


def test_parse_connection_string():
    cs = "Endpoint=sb://ns.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=abc123="
    parsed = parse_connection_string(cs)
    assert parsed["endpoint"] == "sb://ns.servicebus.windows.net/"
    assert parsed["shared_access_key_name"] == "RootManageSharedAccessKey"
    assert parsed["shared_access_key"] == "abc123="
    assert parsed["entity_path"] is None


def test_parse_connection_string_with_entity_path():
    cs = "Endpoint=sb://ns.servicebus.windows.net/;SharedAccessKeyName=Policy;SharedAccessKey=key=;EntityPath=hub1"
    parsed = parse_connection_string(cs)
    assert parsed["entity_path"] == "hub1"


def test_parse_connection_string_missing_endpoint():
    with pytest.raises(ValueError, match="missing 'Endpoint'"):
        parse_connection_string("SharedAccessKeyName=Policy;SharedAccessKey=key=")


def test_parse_connection_string_missing_key_name():
    with pytest.raises(ValueError, match="SharedAccessKeyName"):
        parse_connection_string("Endpoint=sb://ns.servicebus.windows.net/;SharedAccessKey=key=")


def test_parse_connection_string_missing_key():
    with pytest.raises(ValueError, match="SharedAccessKey"):
        parse_connection_string(
            "Endpoint=sb://ns.servicebus.windows.net/;SharedAccessKeyName=Policy"
        )
