import asyncio, logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import get_settings
from app.database.database import init_db
from app.services.monitor import MonitorService

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(); app.state.monitor = MonitorService(settings)
    task = asyncio.create_task(app.state.monitor.run())
    yield
    task.cancel()
    try: await task
    except asyncio.CancelledError: pass

app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)
