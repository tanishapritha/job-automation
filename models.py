from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    experience_years = Column(Float)
    current_role = Column(String)
    skills = Column(JSON)
    target_role = Column(String)
    location = Column(String)
    remote_preference = Column(String)
    email_tone = Column(String, default="Professional")
    created_at = Column(DateTime, default=datetime.now(UTC))

    sent_mails = relationship("SentMail", back_populates="user")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String)
    description = Column(Text)
    apply_url = Column(String, unique=True) # Unique to prevent duplicates
    source = Column(String) # "linkedin", "indeed", etc
    
    # Enrichment fields
    salary = Column(String, nullable=True)
    is_remote = Column(Boolean, default=False)
    date_posted = Column(String, nullable=True)
    company_url = Column(String, nullable=True)
    platform_data = Column(JSON, nullable=True) # Catch-all for extra platform info
    
    fetched_at = Column(DateTime, default=datetime.now(UTC))
    sent_mails = relationship("SentMail", back_populates="job")

class SentMail(Base):
    __tablename__ = "sent_mails"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    subject = Column(String)
    body = Column(Text)
    sent_at = Column(DateTime, default=datetime.now(UTC))
    status = Column(String)

    user = relationship("User", back_populates="sent_mails")
    job = relationship("Job", back_populates="sent_mails")
