import os
import httpx
from typing import List, Optional
from schemas import JobBase
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY")

async def fetch_jobs(
    query: str, 
    location: str, 
    results: int = 10,
    category: Optional[str] = None,
    salary_min: Optional[int] = None,
    max_days_old: Optional[int] = 3,
    remote_only: bool = False,
    full_time: Optional[bool] = None
) -> List[JobBase]:
    """
    Enhanced job fetcher with advanced Adzuna parameters and freshness control.
    """
    country = "gb" # Default to UK for best Adzuna results
    
    # 🔗 Streamline Logic: Broaden search while injecting intent
    search_query = query
    if remote_only:
        search_query += " remote"

    # Attempt Adzuna
    if ADZUNA_APP_ID and ADZUNA_API_KEY:
        try:
            url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
            params = {
                "app_id": ADZUNA_APP_ID,
                "app_key": ADZUNA_API_KEY,
                "what": search_query,
                "where": location,
                "results_per_page": results,
                "content-type": "application/json"
            }
            
            # --- Advanced Filters ---
            if category: params["category"] = category
            if salary_min: params["salary_min"] = salary_min
            if max_days_old: params["max_days_old"] = max_days_old
            if full_time is not None: params["full_time"] = "1" if full_time else "0"

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

    # Fallback to Remotive (Automatically focuses on Remote/Tech)
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
