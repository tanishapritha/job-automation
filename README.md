# Job Automation & Strategic Outreach Engine

A high-performance pipeline for automated job hunting across **LinkedIn, Indeed, and Naukri**, featuring AI-powered outreach via **Llama-3 (Groq)** and real-time dashboard visualization.

---

## Quick Start

### 1. Setup Environment
```bash
# Clone the repository
git clone https://github.com/tanishapritha/job-automation.git
cd job-automation

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Secrets
Create a `.env` file in the root directory (based on `.env.example`):
- `GROQ_API_KEY`: Get your key from [console.groq.com](https://console.groq.com/)
- `GMAIL_USER`: Your Gmail email address.
- `GMAIL_APP_PASSWORD`: Generate this in your [Google App Passwords](https://myaccount.google.com/apppasswords) settings.

---

## How to Run & Test

The engine is split into two parts: the **Core API** and the **Strategy Labs**.

### 🛠 Part 1: The Core API (FastAPI)
This must be running **first** for all other features to work.
```bash
.\venv\Scripts\python -m uvicorn main:app --reload
```
- **Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Live Dashboard**: [http://localhost:8000/static/index.html](http://localhost:8000/static/index.html) (Classic Minimalist UI)

---

### Part 2: Testing the Search Engine
Use the **Job Strategy Lab** to verify the scrapers (LinkedIn, Indeed, Naukri).
```bash
# In a NEW terminal window (keep uvicorn running)
.\venv\Scripts\activate
streamlit run job_lab.py
```
- **How to Test**: Enter your keywords (e.g., `FastAPI; Python`) and hit "Launch Hunt". You will see a live table of unique openings and raw JSON metadata.

---

### Part 3: Testing AI Mail Generation
Use the **Mail Strategy Lab** to refine the AI's outreach tone.
```bash
# In a NEW terminal window (keep uvicorn running)
.\venv\Scripts\activate
streamlit run mail_lab.py
```
- **How to Test**: Change your name, skills, and the job description in the sidebar. Hit "Generate Strategy Preview" to see exactly how Llama-3 drafts the cover letter.

---

## Automations
- **Daily Scan**: The engine triggers a multi-platform scan at **08:00 AM** every morning.
- **Smart Filtering**: The `scheduler.py` automatically ignores any job you've already applied to in the past.
- **Deduplication**: Identical job posts found on multiple boards (LinkedIn and Indeed) are automatically merged into a single unique record.
