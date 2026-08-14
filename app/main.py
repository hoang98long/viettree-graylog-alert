import asyncio, logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.routes import router
from app.core.config import get_settings
from app.database.database import init_db
from app.services.monitor import MonitorService

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
settings = get_settings(); templates = Jinja2Templates(directory="app/templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(); app.state.monitor = MonitorService(settings)
    task = asyncio.create_task(app.state.monitor.run())
    yield
    task.cancel()
    try: await task
    except asyncio.CancelledError: pass

app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "index.html", {"app_name": settings.app_name})
