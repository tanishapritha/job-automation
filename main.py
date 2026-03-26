"""
Job Search & Mail Automation API
─────────────────────────────────
FastAPI application entry-point.
Mounts routers, creates DB tables, and starts the APScheduler.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import Base, engine
from routers import jobs, mail
from scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle hook."""
    # Create all tables on startup
    Base.metadata.create_all(bind=engine)
    # Start the background scheduler
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()


app = FastAPI(
    title="Job Search & Mail Automation API",
    description=(
        "Automated job search via Adzuna, AI-powered cover-letter "
        "generation with Groq LLM, and Gmail delivery — all on autopilot."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# ── Mount routers ────────────────────────────────────────────────────────────
app.include_router(jobs.router)
app.include_router(mail.router)


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "Job Automation API is running 🚀"}
