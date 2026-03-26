import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, engine

client = TestClient(app)

def test_health_check():
    """Verify API is alive."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_user_and_search():
    """E2E flow: Create user -> Search Jobs."""
    user_payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "experience_years": 3,
        "current_role": "Data Scientist",
        "skills": ["Python", "SQL"],
        "target_role": "Senior dev",
        "location": "London",
        "remote_preference": "Remote",
        "email_tone": "Professional"
    }
    
    # 1. Create User
    response = client.post("/users/", json=user_payload)
    assert response.status_code == 200
    user_id = response.json()["id"]

    # 2. Search Jobs (mocking the fetcher internally for test stability)
    with patch("routers.jobs.fetch_jobs", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = [
            # Using same fields as JobBase schema
            {
                "title": "Python Dev",
                "company": "Big Tech",
                "location": "London",
                "description": "Write code",
                "apply_url": "http://apply.me",
                "source": "Mock"
            }
        ]
        
        search_payload = {"query": "Python", "location": "London"}
        response = client.post("/jobs/search", json=search_payload)
        assert response.status_code == 200
        assert len(response.json()) > 0
