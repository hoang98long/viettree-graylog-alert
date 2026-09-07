import asyncio
from datetime import datetime, timezone
import httpx
from app.core.config import Settings
from app.database.models import SecurityEvent


class TelegramService:
    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def configured(self) -> bool:
        return bool(self.settings.telegram_enabled and self.settings.telegram_bot_token and self.settings.telegram_chat_id)

    async def send_alert(self, event: SecurityEvent | None = None, text: str | None = None) -> None:
        if not self.configured:
            raise RuntimeError("Telegram is not configured")
        content = text or (f"🚨 FIREWALL CONFIGURATION CHANGE\n\nDevice:\n{event.device_name or event.device_ip or 'Unknown'}\n\nSource:\n{event.source}\n\nEvent:\n{event.event_type}\n\nSeverity:\n{event.severity}\n\nTime:\n{event.timestamp}\n\nMessage:\n{event.message}\n\nReason:\n{event.detection_reason or 'Configuration pattern matched'}\n\nEvent ID:\n{event.event_id}")
        url = f"https://api.telegram.org/bot{self.settings.telegram_bot_token}/sendMessage"
        last_error: Exception | None = None
        async with httpx.AsyncClient(timeout=10.0) as client:
            for attempt in range(3):
                try:
                    response = await client.post(url, json={"chat_id": self.settings.telegram_chat_id, "text": content})
                    response.raise_for_status()
                    return
                except httpx.HTTPError as exc:
                    last_error = exc
                    if attempt < 2:
                        await asyncio.sleep(attempt + 1)
        raise RuntimeError(f"Telegram request failed after retries: {last_error}")
