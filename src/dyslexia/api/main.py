"""FastAPI entrypoint. Models load once at startup; DB tables are created if missing."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import read_aloud, simplify, session, coach, health, dashboard, handwriting, auth as auth_router
from .db import init_db
from ..common.logging_utils import get_logger

log = get_logger(__name__)
STATE: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    from ..services.stt_service import STTService
    from ..services.tts_service import TTSService
    from ..services.ocr_service import OCRService

    log.info("initializing database...")
    init_db()

    log.info("loading models...")
    STATE["stt"] = STTService()
    STATE["tts"] = TTSService()
    STATE["ocr"] = OCRService()
    yield
    STATE.clear()


app = FastAPI(title="WordWing - AI Reading Assistant",
              version="0.2.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

for r in (health.router, auth_router.router, read_aloud.router,
        simplify.router, session.router, coach.router, dashboard.router, handwriting.router):
    app.include_router(r)