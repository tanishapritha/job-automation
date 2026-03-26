from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, Job, SentMail
from schemas import MailGenerateRequest, MailSendRequest, MailHistoryResponse
from services.llm_service import generate_email
from services.mail_service import send_email

router = APIRouter(prefix="/mail", tags=["Mail"])

@router.post("/generate")
def generate_mail_endpoint(request: MailGenerateRequest, db: Session = Depends(get_db)):
    """
    Generate an email body for a specific user and job.
    """
    user = db.query(User).filter(User.id == request.user_id).first()
    job = db.query(Job).filter(Job.id == request.job_id).first()
    if not user or not job:
        raise HTTPException(status_code=404, detail="User or Job not found")
    
    body = generate_email(user, job)
    return {"user_id": user.id, "job_id": job.id, "body": body}

@router.post("/send")
def send_mail_endpoint(request: MailSendRequest, db: Session = Depends(get_db)):
    """
    Send an email and log it to SentMail.
    """
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    success = send_email(user.email, request.subject, request.body)
    
    sent_mail = SentMail(
        user_id=request.user_id,
        job_id=request.job_id,
        subject=request.subject,
        body=request.body,
        status="Sent" if success else "Failed"
    )
    db.add(sent_mail)
    db.commit()
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send email")
    
    return {"status": "ok", "message": "Email sent successfully"}

@router.get("/history/{user_id}", response_model=List[MailHistoryResponse])
def mail_history(user_id: int, db: Session = Depends(get_db)):
    """
    List all sent mails for a user.
    """
    return db.query(SentMail).filter(SentMail.user_id == user_id).all()
