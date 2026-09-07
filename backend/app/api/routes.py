from fastapi import APIRouter, HTTPException, Query, Request
from sqlalchemy import func, select
from app.api.schemas import EventResponse, EventsPage
from app.database.database import SessionLocal
from app.database.models import SecurityEvent

router = APIRouter(prefix="/api")

@router.get("/health")
def health(): return {"status": "ok"}

@router.get("/status")
def status(request: Request): return request.app.state.monitor.status()

@router.get("/events", response_model=EventsPage)
def events(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    with SessionLocal() as db:
        total = db.scalar(select(func.count()).select_from(SecurityEvent)) or 0
        items = list(db.scalars(select(SecurityEvent).order_by(SecurityEvent.timestamp.desc()).offset(offset).limit(limit)))
        return {"items": items, "total": total}

@router.get("/events/{event_id}", response_model=EventResponse)
def event_detail(event_id: str):
    with SessionLocal() as db:
        event = db.scalar(select(SecurityEvent).where(SecurityEvent.event_id == event_id))
        if not event: raise HTTPException(404, "Event not found")
        return event

@router.post("/test/telegram")
async def test_telegram(request: Request):
    try:
        await request.app.state.monitor.telegram.send_alert(text="Test alert from Firewall Config Monitor")
        return {"status": "sent"}
    except Exception as exc:
        raise HTTPException(503, str(exc))

@router.post("/test/graylog")
async def test_graylog(request: Request):
    try:
        await request.app.state.monitor.test_graylog()
        return {"status": "connected"}
    except Exception as exc:
        raise HTTPException(503, "Unable to connect to Graylog") from exc
