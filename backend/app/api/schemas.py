from datetime import datetime
from pydantic import BaseModel, ConfigDict


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    event_id: str
    graylog_message_id: str | None
    timestamp: datetime
    received_at: datetime
    source: str
    source_ip: str
    device_name: str | None
    device_ip: str | None
    device_type: str | None
    event_type: str
    severity: str
    message: str
    detection_reason: str | None
    matched_pattern: str | None
    telegram_sent: bool
    telegram_sent_at: datetime | None
    telegram_error: str | None
    raw_data: str


class EventsPage(BaseModel):
    items: list[EventResponse]
    total: int
