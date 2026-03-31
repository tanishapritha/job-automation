# Job Search & Mail Automation API

Automated job search via Adzuna, AI-powered cover-letter generation with Groq LLM (Llama 3), and Gmail delivery — all on autopilot.

## Features

- **Daily Automation**: Runs a pipeline at 08:00 AM every day.
- **AI-Powered**: Generates personalized emails based on your unique skills and the job description.
- **Smart Filtering**: Remembers which jobs you've applied to and never sends duplicates.
- **Reliable Sourcing**: Pulls from Adzuna with a fallback to Remotive.

---

## Setup Instructions

### 1. Clone & Install
```bash
git clone https://github.com/tanishapritha/job-automation.git
cd job-automation
python -m venv venv
# Windows: venv\Scripts\activate | Unix: source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment
Create a `.env` file (see `.env.example`):
- **Adzuna**: [Get credentials here](https://developer.adzuna.com/)
- **Groq**: [Get API key here](https://console.groq.com/)
- **Gmail**: Generate an [App Password](https://myaccount.google.com/apppasswords)

### 3. Run Locally
```bash
uvicorn main.py:app --reload
```
Visit **http://localhost:8000/docs** for interactive documentation.

---

## API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/users/` | Create your user profile |
| `POST` | `/jobs/search` | Search and save jobs |
| `POST` | `/mail/generate` | Generate AI email draft |
| `POST` | `/mail/send` | Send email & log to history |
| `GET` | `/mail/history/{id}` | View application history |

---

## How the Automation Works

The `APScheduler` runs `daily_pipeline()` every morning:
1.  **Fetch**: Queries jobs for every user based on their `target_role`.
2.  **Filter**: Deduplicates against the `sent_mails` table (3 job limit/day).
3.  **Generate**: Uses Groq LLM to write a cover letter tailored to the user's `skills`.
4.  **Send**: Delivers the email via Gmail SMTP.

---

## Free Tier Limits (Approx.)

| Service | Limit |
| :--- | :--- |
| **Adzuna** | 1,000 requests/day |
| **Groq (Llama 3)** | 14,400 tokens/min |
| **Gmail** | 500 emails/day |
| **Render** | Free instance (sleeps after 15m inactivity) |

---

## Deployment

This repo is **Render-ready**.
1. Connect your GitHub to Render.com.
2. It will auto-detect `render.yaml`.
3. Fill in the environment variables in the Render Dashboard.
