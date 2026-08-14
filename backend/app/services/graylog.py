from datetime import datetime, timezone
from typing import Any
import httpx
from app.core.config import Settings


class GraylogClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._mock_sent = False

    async def search(self, start: datetime, end: datetime) -> list[dict[str, Any]]:
        if self.settings.mock_graylog:
            return self._mock_messages()
        url = f"{self.settings.graylog_url.rstrip('/')}{self.settings.graylog_search_endpoint}"
        auth = (self.settings.graylog_username, self.settings.graylog_password) if self.settings.graylog_username else None
        params = {"query": self.settings.graylog_search_query, "range": max(1, int((end - start).total_seconds()) + 2), "limit": 150, "sort": "timestamp:asc"}
        async with httpx.AsyncClient(verify=self.settings.graylog_verify_ssl, timeout=10.0, auth=auth) as client:
            response = await client.get(url, params=params, headers={"Accept": "application/json"})
            response.raise_for_status()
            return self._normalize(response.json())

    def _normalize(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        items = payload.get("messages", payload.get("events", []))
        normalized = []
        for item in items:
            raw = item.get("message", item)
            source = str(raw.get("source", raw.get("source_ip", "")))
            normalized.append({"id": str(raw.get("gl2_message_id", raw.get("id", ""))), "timestamp": raw.get("timestamp", datetime.now(timezone.utc).isoformat()), "source": source, "message": str(raw.get("message", raw.get("full_message", ""))), "level": str(raw.get("level", "")), "facility": str(raw.get("facility", "")), "raw": raw})
        return normalized

    def _mock_messages(self) -> list[dict[str, Any]]:
        if self._mock_sent:
            return []
        self._mock_sent = True
        now = datetime.now(timezone.utc).isoformat()
        message = "User admin executed the configuration command: access-list OUTSIDE extended permit tcp any any eq 443"
        return [{"id": "mock-config-change-001", "timestamp": now, "source": self.settings.asa_ip, "message": message, "level": "warning", "facility": "local4", "raw": {"mock": True, "source": self.settings.asa_ip, "message": message}}]
