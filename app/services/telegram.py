import httpx
from app.core.config import Settings
from app.database.models import SecurityEvent


class TelegramService:
    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def configured(self) -> bool:
        return bool(self.settings.enable_telegram and self.settings.telegram_bot_token and self.settings.telegram_chat_id)

    async def send_alert(self, event: SecurityEvent | None = None, text: str | None = None) -> None:
        if not self.configured:
            raise RuntimeError("Telegram is not configured")
        content = text or (f"🚨 ASA CONFIGURATION ALERT\n\nFirewall: {event.source_ip}\n\nTime: {event.timestamp}\n\nEvent: {event.event_type}\n\nSource: {event.source_ip}\n\nMessage:\n{event.message}\n\nGraylog Event: {event.event_id}\n\nStatus: Detected")
        url = f"https://api.telegram.org/bot{self.settings.telegram_bot_token}/sendMessage"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json={"chat_id": self.settings.telegram_chat_id, "text": content})
            response.raise_for_status()
