import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import Base, engine
from routers import jobs, mail
from scheduler import start_scheduler, stop_scheduler

# Create tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start Scheduler
    start_scheduler()
    yield
    # Shutdown: Stop Scheduler
    stop_scheduler()

app = FastAPI(title="Job Automation API", lifespan=lifespan)

# ── CORS Middleware (Must be FIRST) ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include Routers ────────────────────────────────────────────────────────
app.include_router(jobs.user_router)
app.include_router(jobs.router)
app.include_router(mail.router)

# ── Mount static files ──────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "Job Automation API is running 🚀"}
