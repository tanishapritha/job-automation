import pytest
from unittest.mock import MagicMock, patch
from services.mail_service import send_email

def test_send_email_success():
    """Test that send_email calls SMTP server correctly."""
    # Mock credentials so it doesn't fail the "if not GMAIL_USER" check
    with patch("services.mail_service.GMAIL_USER", "test@gmail.com"), \
         patch("services.mail_service.GMAIL_APP_PASSWORD", "secret"), \
         patch("smtplib.SMTP") as mock_smtp_class:
        mock_server = mock_smtp_class.return_value
        
        success = send_email("test@example.com", "Subject", "Body")
        
        assert success is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
