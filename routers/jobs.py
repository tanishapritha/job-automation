from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, Job
from schemas import UserCreate, UserResponse, JobSearchRequest, JobResponse
from services.job_fetcher import fetch_jobs

# --- User Routes ---
user_router = APIRouter(prefix="/users", tags=["Users"])

@user_router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@user_router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --- Job Routes ---
router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/search", response_model=List[JobResponse])
async def search_jobs_endpoint(request: JobSearchRequest, db: Session = Depends(get_db)):
    """
    Search for jobs across Adzuna/Remotive and save them to the DB.
    """
    fetched_jobs = await fetch_jobs(request.query, request.location, request.results)
    db_jobs = []
    for job_data in fetched_jobs:
        # Avoid duplicate jobs by exact title+company check (simple deduplication for now)
        existing = db.query(Job).filter(
            Job.title == job_data.title, 
            Job.company == job_data.company
        ).first()
        if not existing:
            db_job = Job(**job_data.model_dump())
            db.add(db_job)
            db_jobs.append(db_job)
        else:
            db_jobs.append(existing)
    
    db.commit()
    for j in db_jobs:
        db.refresh(j)
    return db_jobs

@router.get("/saved/{user_id}", response_model=List[JobResponse])
def list_saved_jobs(user_id: int, db: Session = Depends(get_db)):
    """
    List jobs. For simplicity, this returns all jobs in the system, 
    but in a real app, it might be filtered by user interests.
    """
    return db.query(Job).all()
