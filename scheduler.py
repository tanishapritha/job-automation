import asyncio
from datetime import datetime, UTC, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User, Job, SentMail
from services.job_scraper import search_all_platforms
from services.llm_service import generate_email
from services.mail_service import send_email

# Simple in-memory cache to avoid redundant platform scrapes
# Cache key: (keywords, location) -> (timestamp, List[dict])
_job_cache = {}
CACHE_EXPIRATION = timedelta(hours=2)

scheduler = AsyncIOScheduler()

async def get_jobs_cached(query: str, location: str, remote: str):
    """
    Returns jobs using the multi-platform engine, with a 2-hour cache.
    """
    key = (query, location, remote)
    now = datetime.now(UTC)
    
    if key in _job_cache:
        timestamp, cached_results = _job_cache[key]
        if now - timestamp < CACHE_EXPIRATION:
            return cached_results
            
    # Fresh scrape across LinkedIn, Indeed, Naukri
    jobs = await search_all_platforms(
        keywords          = query,
        location          = location,
        remote_preference = remote,
        results_per_platform = 10,
        hours_old         = 48 # Keep it fresh for daily run
    )
    _job_cache[key] = (now, jobs)
    return jobs

async def daily_pipeline():
    """
    Automated daily pipeline using the new JobSpy engine.
    """
    print(f"[{datetime.now()}] Starting JobSpy automation pipeline...")
    db: Session = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            print(f"Processing candidate: {user.email}")
            
            # 1. Multi-platform Scrape
            jobs_data = await get_jobs_cached(user.target_role, user.location, user.remote_preference)
            
            # 2. Sent Job History Check
            sent_job_ids = [row[0] for row in db.query(SentMail.job_id).filter(SentMail.user_id == user.id).all()]
            
            unseen_jobs = []
            for jdict in jobs_data:
                # Deduplicate by URL
                db_job = db.query(Job).filter(Job.apply_url == jdict["apply_url"]).first()
                if not db_job:
                    db_job = Job(
                        title         = jdict["title"],
                        company       = jdict["company"],
                        location      = jdict["location"],
                        description   = jdict["description"],
                        apply_url     = jdict["apply_url"],
                        source        = jdict["platform"],
                        salary        = jdict["salary"],
                        is_remote     = jdict["is_remote"],
                        date_posted   = jdict["date_posted"],
                        company_url   = jdict["company_url"],
                        platform_data = jdict["platform_data"]
                    )
                    db.add(db_job)
                    db.commit()
                    db.refresh(db_job)

                if db_job.id not in sent_job_ids:
                    unseen_jobs.append(db_job)
                
                if len(unseen_jobs) >= 3: # Limit to top 3 per day
                    break
            
            # 3. Personalized AI Outreach
            for job in unseen_jobs:
                print(f"Drafting with Llama 3 for {job.company}...")
                email_body = generate_email(user, job)
                subject = f"Application for {job.title} at {job.company}"
                
                success = send_email(user.email, subject, email_body)
                
                # 4. Persistence
                sent_mail = SentMail(
                    user_id=user.id,
                    job_id=job.id,
                    subject=subject,
                    body=email_body,
                    status="Sent" if success else "Failed"
                )
                db.add(sent_mail)
                db.commit()
                print(f"Email Signal: {sent_mail.status} for {job.platform.upper()} position.")

    except Exception as e:
        print(f"Pipeline Failure: {e}")
    finally:
        db.close()
    print(f"[{datetime.now()}] JobSpy Pipeline Complete.")

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            daily_pipeline, 
            CronTrigger(hour=8, minute=0),
            id="jobspy_daily_hunt",
            replace_existing=True
        )
        scheduler.start()
        print("Chronos Engine: Daily multi-platform hunt set for 08:00.")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("Chronos Engine: Shutdown Sequence Complete.")
