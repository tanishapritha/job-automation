import pytest
from unittest.mock import MagicMock, patch
from services.llm_service import generate_email
from models import User, Job

def test_generate_email_success():
    """Test that generate_email calls Groq and returns a string."""
    mock_user = MagicMock(spec=User)
    mock_user.name = "John Doe"
    mock_user.skills = ["Python"]
    mock_user.current_role = "Dev"
    mock_user.experience_years = 5
    mock_user.email_tone = "Professional"

    mock_job = MagicMock(spec=Job)
    mock_job.title = "Backend dev"
    mock_job.company = "Tech Inc"
    mock_job.description = "We need Python"

    with patch("services.llm_service.Groq") as mock_groq_class:
        mock_client = mock_groq_class.return_value
        mock_client.chat.completions.create.return_value.choices[0].message.content = "Sample Email Body"
        
        email = generate_email(mock_user, mock_job)
        
        assert email == "Sample Email Body"
        mock_client.chat.completions.create.assert_called_once()
