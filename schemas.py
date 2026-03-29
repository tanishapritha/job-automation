from pydantic import BaseModel, HttpUrl, EmailStr, Field
from typing import List, Optional, Any
from datetime import datetime

# --- User ---
class UserBase(BaseModel):
    name: str
    email: EmailStr
    experience_years: float
    current_role: str
    skills: List[str]
    target_role: str
    location: str
    remote_preference: str
    email_tone: str = "Professional"

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# --- Job ---
class PlatformData(BaseModel):
    job_level:           Optional[str] = None
    skills:              Optional[Any] = None
    experience_range:    Optional[str] = None
    company_rating:      Optional[Any] = None
    company_reviews:     Optional[Any] = None
    vacancy_count:       Optional[Any] = None
    work_from_home_type: Optional[str] = None
    company_industry:    Optional[str] = None
    company_revenue:     Optional[str] = None
    company_employees:   Optional[str] = None
    company_logo:        Optional[str] = None

class JobBase(BaseModel):
    title: str = "Untitled"
    company: str = "Unknown"
    location: str = "Remote"
    description: Optional[str] = ""
    apply_url: str
    source: str = "Scraper"
    platform:      Optional[str] = None
    salary:        Optional[str] = None
    is_remote:     Optional[bool] = False
    date_posted:   Optional[str] = None
    company_url:   Optional[str] = None
    platform_data: Optional[PlatformData] = None

class JobResponse(JobBase):
    id: int
    fetched_at: datetime
    class Config:
        from_attributes = True

# --- Mail ---
class MailGenerateRequest(BaseModel):
    user_id: int
    job_id: int

class MailSendRequest(BaseModel):
    user_id: int
    job_id: int
    subject: str
    body: str

class MailHistoryResponse(BaseModel):
    id: int
    user_id: int
    job_id: int
    subject: str
    body: str
    sent_at: datetime
    status: str
    class Config:
        from_attributes = True

# --- Search ---
class JobSearchRequest(BaseModel):
    query: str
    location: str = ""
    results: int = 10
    experience_level: str = "mid"
    job_type: str = "full_time"
    remote_preference: str = "hybrid"
    hours_old: int = 168
    country_indeed: str = "India"
    salary_min: Optional[int] = None
