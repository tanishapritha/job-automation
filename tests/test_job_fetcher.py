import pytest
from unittest.mock import AsyncMock, patch
from services.job_fetcher import fetch_jobs

@pytest.mark.asyncio
async def test_fetch_jobs_fallback():
    """Test that if Adzuna fails, it falls back to Remotive."""
    with patch("httpx.AsyncClient.get") as mock_get:
        # First call (Adzuna) returns 500
        # Second call (Remotive) returns 200 with one job
        mock_get.side_effect = [
            AsyncMock(status_code=500),
            AsyncMock(status_code=200, json=lambda: {
                "jobs": [{
                    "title": "Software Engineer",
                    "company_name": "Remotive Tech",
                    "url": "https://remotive.com/1",
                    "description": "Short desc"
                }]
            })
        ]

        jobs = await fetch_jobs("python", "remote")
        
        assert len(jobs) == 1
        assert jobs[0].title == "Software Engineer"
        assert jobs[0].source == "Remotive"
