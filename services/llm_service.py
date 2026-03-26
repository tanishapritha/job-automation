import os
from groq import Groq
from models import User, Job
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama3-8b-8192"

def generate_email(user: User, job: Job) -> str:
    """
    Generate a tailored job application email using Groq LLM.
    """
    if not GROQ_API_KEY:
        return "GROQ_API_KEY not configured. Cannot generate email."

    client = Groq(api_key=GROQ_API_KEY)
    
    prompt = f"""
    You are an expert career coach helping {user.name} apply for a job.
    Write a concise, high-impact application email for the following job:
    
    JOB TITLE: {job.title}
    COMPANY: {job.company}
    DESCRIPTION: {job.description[:400]}
    
    APPLICANT PROFILE:
    NAME: {user.name}
    CURRENT ROLE: {user.current_role}
    EXPERIENCE: {user.experience_years} years
    SKILLS: {", ".join(user.skills)}
    TONE: {user.email_tone}
    
    INSTRUCTIONS:
    - Focus on how {user.name}'s skills match the job requirements.
    - Keep it under 200 words.
    - Return ONLY the email body.
    - Do NOT include a subject line.
    - Do NOT include markdown formatting or conversational filler like "Here is your email".
    - Address the hiring manager or recruiter.
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=GROQ_MODEL,
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM Generation Error: {e}")
        return f"Error generating email: {str(e)}"
