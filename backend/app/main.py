"""
PaperPilot AI — FastAPI application entrypoint.

Run locally with:
    uvicorn app.main:app --reload --port 8000
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.routes import (
    auth_routes, papers_routes, chat_routes, compare_routes,
    export_routes, dashboard_routes,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("paperpilot")

app = FastAPI(
    title="PaperPilot AI",
    description="AI-Powered Research Paper Summarizer and Academic Assistant — 100% local/open-source AI stack.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    logger.info("Initializing database...")
    init_db()
    logger.info("PaperPilot AI backend is ready.")


app.include_router(auth_routes.router)
app.include_router(papers_routes.router)
app.include_router(chat_routes.router)
app.include_router(compare_routes.router)
app.include_router(export_routes.router)
app.include_router(dashboard_routes.router)


@app.get("/api/health", tags=["health"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
