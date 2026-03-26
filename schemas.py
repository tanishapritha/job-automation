from pydantic import BaseModel, HttpUrl, EmailStr
from typing import List, Optional
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
class JobBase(BaseModel):
    title: str
    company: str
    location: str
    description: str
    apply_url: str
    source: str

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
    location: str
    results: int = 10
