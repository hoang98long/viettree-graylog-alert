import asyncio
import pytest
from app.core.config import Settings
from app.services.telegram import TelegramService


def test_telegram_rejects_when_not_configured():
    service = TelegramService(Settings(telegram_enabled=False))
    with pytest.raises(RuntimeError, match="not configured"):
        asyncio.run(service.send_alert(text="test"))
