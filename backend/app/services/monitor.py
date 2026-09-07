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
        self.last_message_at: datetime | None = None
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
            logger.info("Graylog connected; fetched %s messages", len(messages))
            for message in messages:
                await self._process(message)
            self.last_poll = now
        except Exception as exc:
            self.graylog_status = "disconnected"
            logger.warning("Graylog polling failed: %s", exc)

    async def _process(self, item: dict) -> None:
        result = self.detector.detect(item.get("message", ""))
        if not result.detected:
            return
        fingerprint = self.fingerprint_for(item)
        timestamp = self._parse_timestamp(item.get("timestamp"))
        with SessionLocal() as db:
            if db.scalar(select(SecurityEvent).where(SecurityEvent.fingerprint == fingerprint)):
                return
            fields = item.get("fields", item.get("raw", {}))
            source = str(item.get("source", ""))
            device_ip = self._field(fields, "device_ip", "source_ip", "_source_ip")
            event = SecurityEvent(
                event_id=item.get("id") or fingerprint,
                graylog_message_id=item.get("id") or None,
                fingerprint=fingerprint,
                timestamp=timestamp,
                source_ip=device_ip or source,
                source=source,
                device_name=self._field(fields, "device_name", "host", "hostname") or source,
                device_ip=device_ip,
                device_type=self._field(fields, "device_type", "_device_type") or "firewall",
                event_type=result.event_type,
                message=item.get("message", ""),
                severity=result.severity,
                detection_reason=result.reason,
                matched_pattern=result.matched_pattern,
                raw_data=json.dumps(item.get("raw", {}), default=str),
            )
            db.add(event); db.commit(); db.refresh(event)
            self.last_message_at = timestamp
            if self.telegram.configured:
                try:
                    await self.telegram.send_alert(event=event)
                    event.telegram_sent = True
                    event.telegram_sent_at = datetime.now(timezone.utc)
                    logger.info("Telegram alert sent for event %s", event.event_id)
                except Exception as exc:
                    event.telegram_error = str(exc)
                    logger.warning("Telegram alert failed: %s", exc)
                db.commit()
            logger.warning("Configuration change detected and saved: %s", event.event_id)

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

    @staticmethod
    def _field(fields: dict, *names: str) -> str | None:
        for name in names:
            value = fields.get(name)
            if value not in (None, ""):
                return str(value)
        return None

    async def test_graylog(self) -> None:
        try:
            await self.graylog.test_connection()
            self.graylog_status = "connected"
        except Exception:
            self.graylog_status = "disconnected"
            raise

    def status(self) -> dict:
        with SessionLocal() as db:
            today = datetime.now(timezone.utc).date()
            today_count = db.scalar(select(func.count()).select_from(SecurityEvent).where(SecurityEvent.timestamp >= datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc))) or 0
            total_count = db.scalar(select(func.count()).select_from(SecurityEvent)) or 0
        return {"status": "healthy", "graylog": self.graylog_status, "graylog_connected": self.graylog_status == "connected", "telegram": "enabled" if self.telegram.configured else "disabled", "telegram_enabled": self.telegram.configured, "polling": "running" if self.running else "stopped", "firewall_label": self.settings.firewall_label, "graylog_url": self.settings.graylog_url, "poll_interval": self.settings.poll_interval_seconds, "last_poll": self.last_poll.isoformat() if self.last_poll else None, "last_poll_at": self.last_poll.isoformat() if self.last_poll else None, "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None, "events_today": today_count, "events_count": total_count}
