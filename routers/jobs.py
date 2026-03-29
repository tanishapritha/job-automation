from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from database import get_db
from models import User, Job
from schemas import UserCreate, UserResponse, JobSearchRequest, JobResponse
from services.job_scraper import search_all_platforms

logger = logging.getLogger(__name__)

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
    Search for jobs across LinkedIn, Indeed, and Naukri. 
    Defensive mapping to prevent 500 crashes.
    """
    try:
        fetched_jobs_dicts = await search_all_platforms(
            keywords              = request.query,
            location              = request.location,
            results_per_platform  = request.results,
            experience_level      = request.experience_level,
            job_type              = request.job_type,
            remote_preference     = request.remote_preference,
            hours_old             = request.hours_old,
            country_indeed        = request.country_indeed,
            salary_min            = request.salary_min
        )
    except Exception as e:
        logger.error(f"Scraper Level Failure: {e}")
        raise HTTPException(status_code=503, detail="Search engine currently unavailable")
    
    db_jobs = []
    seen_urls_this_batch = set()
    
    for job_dict in fetched_jobs_dicts:
        url = job_dict.get("apply_url")
        if not url or url in seen_urls_this_batch:
            continue
        seen_urls_this_batch.add(url)

        # Skip if already in DB
        existing = db.query(Job).filter(Job.apply_url == url).first()
        if not existing:
            try:
                db_job = Job(
                    title         = job_dict.get("title", "Untitled"),
                    company       = job_dict.get("company", "Unknown"),
                    location      = job_dict.get("location", "Remote"),
                    description   = job_dict.get("description", ""),
                    apply_url     = url,
                    source        = job_dict.get("platform", "Unknown"),
                    salary        = job_dict.get("salary"),
                    is_remote     = job_dict.get("is_remote", False),
                    date_posted   = job_dict.get("date_posted"),
                    company_url   = job_dict.get("company_url"),
                    platform_data = job_dict.get("platform_data")
                )
                db.add(db_job)
                db.commit() # Individual commit for robustness in demo
                db.refresh(db_job)
                db_jobs.append(db_job)
            except Exception as e:
                db.rollback()
                logger.warning(f"Skipping malformed job: {e}")
                continue
        else:
            db_jobs.append(existing)
            
    return db_jobs

@router.get("/saved", response_model=List[JobResponse])
def list_saved_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()
