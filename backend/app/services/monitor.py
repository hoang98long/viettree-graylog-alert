import asyncio, hashlib, json, logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import func, select
from app.core.config import Settings
from app.database.database import SessionLocal
from app.database.models import SecurityEvent
from app.services.detector import ConfigChangeDetector
from app.services.graylog import GraylogClient
from app.services.telegram import TelegramService

logger = logging.getLogger(__name__)


class MonitorService:
    def __init__(self, settings: Settings):
        self.settings, self.graylog = settings, GraylogClient(settings)
        self.detector, self.telegram = ConfigChangeDetector(), TelegramService(settings)
        self.last_poll: datetime | None = None
        self.graylog_status = "unknown"
        self.running = False

    async def run(self) -> None:
        self.running = True
        try:
            while True:
                await self.poll_once()
                await asyncio.sleep(self.settings.poll_interval_seconds)
        except asyncio.CancelledError:
            logger.info("Graylog polling stopped")
            raise
        finally:
            self.running = False

    async def poll_once(self) -> None:
        now = datetime.now(timezone.utc)
        start = (self.last_poll - timedelta(seconds=self.settings.poll_overlap_seconds)) if self.last_poll else now - timedelta(seconds=self.settings.initial_lookback_seconds)
        try:
            messages = await self.graylog.search(start, now)
            self.graylog_status = "connected"
            logger.info("Retrieved %s Graylog messages", len(messages))
            for message in messages:
                await self._process(message)
            self.last_poll = now
        except Exception as exc:
            self.graylog_status = "disconnected"
            logger.warning("Graylog polling failed: %s", exc)

    async def _process(self, item: dict) -> None:
        if item.get("source") != self.settings.asa_ip:
            return
        result = self.detector.detect(item.get("message", ""))
        if not result.detected:
            return
        fingerprint = self.fingerprint_for(item)
        timestamp = self._parse_timestamp(item.get("timestamp"))
        with SessionLocal() as db:
            if db.scalar(select(SecurityEvent).where(SecurityEvent.fingerprint == fingerprint)):
                return
            event = SecurityEvent(event_id=item.get("id") or fingerprint, fingerprint=fingerprint, timestamp=timestamp, source_ip=item["source"], event_type=result.event_type, message=item.get("message", ""), severity=result.severity, raw_data=json.dumps(item.get("raw", {}), default=str))
            db.add(event); db.commit(); db.refresh(event)
            if self.telegram.configured:
                try:
                    await self.telegram.send_alert(event=event)
                    event.telegram_sent = True
                except Exception as exc:
                    event.telegram_error = str(exc)
                    logger.warning("Telegram alert failed: %s", exc)
                db.commit()
            logger.warning("Configuration change detected: %s", event.event_id)

    @staticmethod
    def fingerprint_for(item: dict) -> str:
        """Stable fallback identity when Graylog did not supply a message id."""
        material = f"{item.get('timestamp','')}|{item.get('source','')}|{item.get('message','')}"
        return hashlib.sha256((item.get("id") or material).encode()).hexdigest()

    @staticmethod
    def _parse_timestamp(value: str | None) -> datetime:
        if not value: return datetime.now(timezone.utc)
        try: return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError: return datetime.now(timezone.utc)

    def status(self) -> dict:
        with SessionLocal() as db:
            today = datetime.now(timezone.utc).date()
            count = db.scalar(select(func.count()).select_from(SecurityEvent).where(SecurityEvent.timestamp >= datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc))) or 0
        return {"graylog": self.graylog_status, "telegram": "configured" if self.telegram.configured else "not configured", "asa_ip": self.settings.asa_ip, "graylog_url": self.settings.graylog_url, "poll_interval": self.settings.poll_interval_seconds, "last_poll": self.last_poll.isoformat() if self.last_poll else None, "events_today": count}
