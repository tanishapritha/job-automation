from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    experience_years = Column(Float)
    current_role = Column(String)
    skills = Column(JSON)  # List of strings
    target_role = Column(String)
    location = Column(String)
    remote_preference = Column(String)
    email_tone = Column(String, default="Professional")
    created_at = Column(DateTime, default=datetime.utcnow)

    sent_mails = relationship("SentMail", back_populates="user")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String)
    description = Column(Text)
    apply_url = Column(String)
    source = Column(String)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    sent_mails = relationship("SentMail", back_populates="job")

class SentMail(Base):
    __tablename__ = "sent_mails"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    subject = Column(String)
    body = Column(Text)
    sent_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String) # e.g., "Sent", "Failed"

    user = relationship("User", back_populates="sent_mails")
    job = relationship("Job", back_populates="sent_mails")
