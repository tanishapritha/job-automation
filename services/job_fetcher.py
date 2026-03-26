import os
import httpx
from typing import List
from schemas import JobBase
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY")

async def fetch_jobs(query: str, location: str, results: int = 10) -> List[JobBase]:
    """
    Fetch jobs from Adzuna API with a fallback to Remotive API.
    """
    country = "gb" # Default to UK or extract from location if possible
    # Attempt Adzuna
    if ADZUNA_APP_ID and ADZUNA_API_KEY:
        try:
            url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
            params = {
                "app_id": ADZUNA_APP_ID,
                "app_key": ADZUNA_API_KEY,
                "what": query,
                "where": location,
                "results_per_page": results,
                "content-type": "application/json"
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    jobs = []
                    for item in data.get("results", []):
                        jobs.append(JobBase(
                            title=item.get("title", ""),
                            company=item.get("company", {}).get("display_name", ""),
                            location=item.get("location", {}).get("display_name", ""),
                            description=item.get("description", ""),
                            apply_url=item.get("redirect_url", ""),
                            source="Adzuna"
                        ))
                    return jobs
        except Exception as e:
            print(f"Adzuna Fetch Error: {e}")

    # Fallback to Remotive
    try:
        url = "https://remotive.com/api/remote-jobs"
        params = {"search": query, "limit": results}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                jobs = []
                for item in data.get("jobs", []):
                    jobs.append(JobBase(
                        title=item.get("title", ""),
                        company=item.get("company_name", ""),
                        location="Remote",
                        description=item.get("description", ""),
                        apply_url=item.get("url", ""),
                        source="Remotive"
                    ))
                return jobs
    except Exception as e:
        print(f"Remotive Fetch Error: {e}")

    return []
