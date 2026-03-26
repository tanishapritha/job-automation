import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

def send_email(to: str, subject: str, body: str) -> bool:
    """
    Send an email via Gmail SMTP using STARTTLS.
    """
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("Gmail credentials not configured.")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = str(GMAIL_USER)
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(str(GMAIL_USER), str(GMAIL_APP_PASSWORD))
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False
