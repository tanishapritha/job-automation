import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User, Job, SentMail
from services.job_fetcher import fetch_jobs
from services.llm_service import generate_email
from services.mail_service import send_email

# Simple in-memory cache for jobs to avoid redundant API hits for same query/location
# Cache structure: {(query, location): (timestamp, List[JobBase])}
_job_cache = {}
CACHE_EXPIRATION = timedelta(hours=1)

scheduler = AsyncIOScheduler()

async def get_jobs_cached(query: str, location: str):
    """
    Returns jobs for a query/location, using an in-memory 1-hour cache.
    """
    key = (query, location)
    now = datetime.utcnow()
    
    if key in _job_cache:
        timestamp, cached_jobs = _job_cache[key]
        if now - timestamp < CACHE_EXPIRATION:
            return cached_jobs
            
    # Fetch fresh
    jobs = await fetch_jobs(query, location)
    _job_cache[key] = (now, jobs)
    return jobs

async def daily_pipeline():
    """
    The main automation pipeline:
    1. Iterates through all users.
    2. Fetches matching jobs.
    3. Filters out already sent jobs.
    4. Generates and sends emails for the top 3 matches.
    """
    print(f"[{datetime.now()}] Starting daily job search pipeline...")
    db: Session = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            print(f"Processing user: {user.email}")
            # 1. Fetch jobs
            jobs_data = await get_jobs_cached(user.target_role, user.location)
            
            # 2. Filter out jobs already in SentMail for this user
            sent_job_ids = db.query(SentMail.job_id).filter(SentMail.user_id == user.id).all()
            sent_job_ids = [sid[0] for sid in sent_job_ids]
            
            # We need to save fetched jobs to DB first to get IDs, if not already there
            unseen_jobs = []
            for job_data in jobs_data:
                # Find if job exists in DB
                db_job = db.query(Job).filter(
                    Job.title == job_data.title, 
                    Job.company == job_data.company
                ).first()
                
                if not db_job:
                    db_job = Job(**job_data.model_dump())
                    db.add(db_job)
                    db.commit()
                    db.refresh(db_job)
                
                if db_job.id not in sent_job_ids:
                    unseen_jobs.append(db_job)
                
                if len(unseen_jobs) >= 3:
                    break
            
            # 3. Process top 3 unseen jobs
            for job in unseen_jobs:
                print(f"Generating email for {user.name} -> {job.company}...")
                email_body = generate_email(user, job)
                subject = f"Application for {job.title} at {job.company}"
                
                success = send_email(user.email, subject, email_body)
                
                # 4. Log to SentMail
                sent_mail = SentMail(
                    user_id=user.id,
                    job_id=job.id,
                    subject=subject,
                    body=email_body,
                    status="Sent" if success else "Failed"
                )
                db.add(sent_mail)
                db.commit()
                print(f"Email {sent_mail.status} for job {job.id}")

    except Exception as e:
        print(f"Error in daily pipeline: {e}")
    finally:
        db.close()
    print(f"[{datetime.now()}] Pipeline finished.")

def start_scheduler():
    """Start the background scheduler (every day at 08:00)."""
    if not scheduler.running:
        # Schedule daily_pipeline to run at 08:00 AM local time
        scheduler.add_job(
            daily_pipeline, 
            CronTrigger(hour=8, minute=0),
            id="daily_job_hunt",
            replace_existing=True
        )
        scheduler.start()
        print("Scheduler started: Daily pipeline set for 08:00.")

def stop_scheduler():
    """Gracefully shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("Scheduler stopped.")
