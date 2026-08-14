from fastapi import APIRouter, HTTPException, Query, Request
from sqlalchemy import select
from app.api.schemas import EventResponse
from app.database.database import SessionLocal
from app.database.models import SecurityEvent

router = APIRouter(prefix="/api")

@router.get("/health")
def health(): return {"status": "ok"}

@router.get("/status")
def status(request: Request): return request.app.state.monitor.status()

@router.get("/events", response_model=list[EventResponse])
def events(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    with SessionLocal() as db: return list(db.scalars(select(SecurityEvent).order_by(SecurityEvent.timestamp.desc()).offset(offset).limit(limit)))

@router.get("/events/{event_id}", response_model=EventResponse)
def event_detail(event_id: str):
    with SessionLocal() as db:
        event = db.scalar(select(SecurityEvent).where(SecurityEvent.event_id == event_id))
        if not event: raise HTTPException(404, "Event not found")
        return event

@router.post("/test/telegram")
async def test_telegram(request: Request):
    try:
        await request.app.state.monitor.telegram.send_alert(text="Test alert from ASA Config Monitor")
        return {"status": "sent"}
    except Exception as exc:
        raise HTTPException(503, str(exc))
