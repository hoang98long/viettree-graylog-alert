from datetime import datetime
from pydantic import BaseModel

class EventResponse(BaseModel):
    event_id: str; timestamp: datetime; source_ip: str; event_type: str; message: str; severity: str; telegram_sent: bool; telegram_error: str | None; raw_data: str
    model_config = {"from_attributes": True}
