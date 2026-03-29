"""
job_scraper.py — Unified multi-platform job scraper
Scrapes LinkedIn, Indeed, and Naukri concurrently using JobSpy.
Every result carries a `platform` field so the caller always knows the source.
"""

import asyncio
import logging
from datetime import datetime, UTC
from typing import Literal, Optional, Any
from jobspy import scrape_jobs

logger = logging.getLogger(__name__)

# ── Supported platforms ─────────────────────────────────────────────────────
Platform = Literal["linkedin", "indeed", "naukri"]
ALL_PLATFORMS: list[Platform] = ["linkedin", "indeed", "naukri"]

# ── Filter maps ─────────────────────────────────────────────────────────────
JOB_TYPE_MAP = {
    "full_time":  "fulltime",
    "part_time":  "parttime",
    "contract":   "contract",
    "internship": "internship",
    "temporary":  "temporary",
}

# Seniority keyword hints for post-filtering
SENIORITY_HINTS = {
    "internship": ["intern", "internship", "trainee", "apprentice"],
    "entry":      ["junior", "jr", "entry", "graduate", "fresher", "associate"],
    "mid":        ["mid", "intermediate", "associate", "ii"],
    "senior":     ["senior", "sr", "lead", "principal", "staff", "iii"],
    "director":   ["director", "head of", "vp", "vice president"],
    "executive":  ["cto", "ceo", "cpo", "chief", "c-suite"],
}

# ── Platform-specific field extractors ─────────────────────────────────────
def _extract_naukri_extras(row) -> dict:
    """Naukri-specific fields."""
    def safe(k, d=""):
        v = row.get(k, d)
        return d if (v is None or (isinstance(v, float) and str(v) == "nan")) else v

    return {
        "skills":              safe("skills"),
        "experience_range":    safe("experience_range"), 
        "company_rating":      safe("company_rating"),
        "company_reviews":     safe("company_reviews_count"),
        "vacancy_count":       safe("vacancy_count"),
        "work_from_home_type": safe("work_from_home_type"),
    }

def _extract_indeed_extras(row) -> dict:
    """Indeed-specific fields."""
    def safe(k, d=""):
        v = row.get(k, d)
        return d if (v is None or (isinstance(v, float) and str(v) == "nan")) else v

    return {
        "company_industry":  safe("company_industry"),
        "company_revenue":   safe("company_revenue_label"),
        "company_employees": safe("company_employees_label"),
        "company_logo":      safe("company_logo"),
    }

def _normalise_row(row, platform: Platform) -> dict:
    """
    Convert a JobSpy pandas Series row into a clean flat dict.
    """
    def safe(k, d=""):
        v = row.get(k, d)
        return d if (v is None or (isinstance(v, float) and str(v) == "nan")) else v

    salary_str = ""
    lo, hi     = safe("min_amount"), safe("max_amount")
    cur        = safe("currency", "INR" if platform == "naukri" else "USD")
    interval   = safe("interval", "yearly")
    if lo and hi:
        salary_str = f"{cur} {int(lo):,}–{int(hi):,} / {interval}"
    elif lo:
        salary_str = f"{cur} {int(lo):,}+ / {interval}"

    platform_data: dict = {}
    if platform == "naukri":
        platform_data = _extract_naukri_extras(row)
    elif platform == "indeed":
        platform_data = _extract_indeed_extras(row)
    elif platform == "linkedin":
        platform_data = {
            "job_level": safe("job_level"),
        }

    return {
        "platform":      platform,
        "title":         safe("title"),
        "company":       safe("company"),
        "location":      safe("location"),
        "description":   safe("description"),
        "apply_url":     safe("job_url"),
        "job_type":      safe("job_type"),
        "salary":        salary_str,
        "is_remote":     bool(safe("is_remote", False)),
        "date_posted":   str(safe("date_posted", "")),
        "company_url":   safe("company_url"),
        "emails":        safe("emails", []),
        "fetched_at":    datetime.now(UTC).isoformat(),
        "platform_data": platform_data,
    }

async def search_platforms(
    keywords: str,
    platforms: list[Platform]    = ALL_PLATFORMS,
    location: str                = "",
    experience_level: str        = "",
    job_type: str                = "",
    remote_preference: str       = "",
    hours_old: int               = 168,
    results_per_platform: int    = 10,
    country_indeed: str          = "India",
    fetch_full_description: bool = True,
    salary_min: Optional[int]    = None,
) -> list[dict]:
    """
    Scrapes requested platforms concurrently using JobSpy.
    """
    jobspy_job_type = JOB_TYPE_MAP.get(job_type, None)
    is_remote       = True if remote_preference == "remote" else None

    logger.info("Scraping %s | keywords='%s' location='%s'", platforms, keywords, location)

    loop = asyncio.get_event_loop()
    df = await loop.run_in_executor(
        None,
        lambda: scrape_jobs(
            site_name                  = platforms,
            search_term                = keywords,
            location                   = location,
            results_wanted             = results_per_platform,
            hours_old                  = hours_old,
            job_type                   = jobspy_job_type,
            is_remote                  = is_remote,
            country_indeed             = country_indeed,
            linkedin_fetch_description = fetch_full_description,
            description_format         = "markdown",
            min_amount                 = salary_min,
            verbose                    = 0,
        )
    )

    if df is None or df.empty:
        return []

    # ── Post-filter: experience level ────────────────────────────────────────
    if experience_level and experience_level in SENIORITY_HINTS:
        hints = SENIORITY_HINTS[experience_level]
        mask  = df["title"].str.lower().str.contains("|".join(hints), na=False)
        if "experience_range" in df.columns:
            mask = mask | df["experience_range"].str.lower().str.contains("|".join(hints), na=False)
        filtered = df[mask]
        df = filtered if not filtered.empty else df

    # ── Normalise ────────────────────────────────────────────────────────────
    jobs: list[dict] = []
    for _, row in df.iterrows():
        platform_name: Platform = str(row.get("site", "unknown")).lower()
        jobs.append(_normalise_row(row, platform_name))

    jobs.sort(key=lambda j: (j["date_posted"] or ""), reverse=True)
    return jobs

async def search_all_platforms(
    keywords: str,
    location: str          = "",
    experience_level: str  = "mid",
    job_type: str          = "full_time",
    remote_preference: str = "hybrid",
    hours_old: int         = 168,
    results_per_platform: int = 10,
    country_indeed: str    = "India",
    salary_min: Optional[int] = None,
) -> list[dict]:
    return await search_platforms(
        keywords              = keywords,
        platforms             = ALL_PLATFORMS,
        location              = location,
        experience_level      = experience_level,
        job_type              = job_type,
        remote_preference     = remote_preference,
        hours_old             = hours_old,
        results_per_platform  = results_per_platform,
        country_indeed        = country_indeed,
        salary_min            = salary_min,
    )
