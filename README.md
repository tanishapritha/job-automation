# Job Search & Mail Automation API

Automated job search, AI-powered cover-letter generation, and Gmail delivery — all on autopilot.

## Stack

- **FastAPI** — async REST API
- **SQLite** — lightweight local database (Postgres-ready for prod)
- **Adzuna API** — job search aggregator
- **Groq LLM** — AI email generation (Llama 3 8B)
- **Gmail SMTP** — email delivery
- **APScheduler** — daily automation pipeline

## Quick Start

```bash
# 1. Clone
git clone https://github.com/tanishapritha/job-automation.git
cd job-automation

# 2. Create virtual env & install deps
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Fill in your API keys in .env

# 4. Run
uvicorn main:app --reload
```

API docs available at **http://localhost:8000/docs**

---

> Full documentation (endpoints, automation details, deploy guide) will be added in Phase 3.
