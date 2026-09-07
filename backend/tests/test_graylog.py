from datetime import datetime, timezone
from app.core.config import Settings
from app.services.graylog import GraylogClient


def test_normalize_graylog_message_uses_source_and_preserves_raw():
    client = GraylogClient(Settings())
    result = client._normalize({"messages": [{"message": {"gl2_message_id": "abc", "timestamp": "2026-08-31T10:00:00Z", "source": "TEST-FIREWALL", "message": "configuration change: created firewall rule"}}]})
    assert result[0]["id"] == "abc"
    assert result[0]["source"] == "TEST-FIREWALL"
    assert result[0]["raw"]["message"].startswith("configuration change")


def test_mock_graylog_emits_one_message():
    client = GraylogClient(Settings(mock_graylog=True))
    assert len(client._mock_messages()) == 1
    assert client._mock_messages() == []
