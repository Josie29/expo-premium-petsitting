"""Unit tests for ``backend.emailer`` (env parsing and SMTP send path).

High-level coverage:
- ``_env_bool`` — common truthy/falsey string conventions.
- ``send_email`` — missing config raises ``RuntimeError``; successful send uses
  TLS, optional login, and ``Reply-To``; TLS and login can be disabled via env.
"""

from unittest.mock import MagicMock, patch

import pytest

from backend.emailer import _env_bool, send_email


def _smtp_instance_mock():
    """Build a mock SMTP instance usable as a context manager.

    ``smtplib.SMTP`` is used as ``with SMTP(...) as server``, so the mock's
    ``__enter__`` must return the same object that receives ``starttls`` / ``send_message``.

    Returns:
        MagicMock: Configured instance with ``__enter__`` / ``__exit__`` set.

    """
    mock_server = MagicMock()
    mock_server.__enter__.return_value = mock_server
    mock_server.__exit__.return_value = None
    return mock_server


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("true", True),
        ("TRUE", True),
        ("1", True),
        ("yes", True),
        ("on", True),
        ("false", False),
        ("0", False),
        ("no", False),
        ("", False),
    ],
)
def test_env_bool_parses_strings(monkeypatch, raw, expected):
    """Environment strings map to booleans with sensible defaults."""
    monkeypatch.setenv("EPOCH_TEST_FLAG", raw)
    assert _env_bool("EPOCH_TEST_FLAG", default="false") is expected


def test_env_bool_uses_default_when_unset(monkeypatch):
    """When the variable is missing, the default string is interpreted as bool."""
    monkeypatch.delenv("EPOCH_TEST_MISSING", raising=False)
    assert _env_bool("EPOCH_TEST_MISSING", default="true") is True
    assert _env_bool("EPOCH_TEST_MISSING", default="false") is False


def test_send_email_raises_when_smtp_not_configured(monkeypatch):
    """RuntimeError when host, from, or to is empty."""
    monkeypatch.setenv("SMTP_HOST", "")
    monkeypatch.setenv("SMTP_FROM", "f@example.com")
    monkeypatch.setenv("SMTP_TO", "t@example.com")
    with pytest.raises(RuntimeError, match="Missing SMTP configuration"):
        send_email("s", "b")

    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_FROM", "")
    with pytest.raises(RuntimeError, match="Missing SMTP configuration"):
        send_email("s", "b")

    monkeypatch.setenv("SMTP_FROM", "f@example.com")
    monkeypatch.setenv("SMTP_TO", "")
    with pytest.raises(RuntimeError, match="Missing SMTP configuration"):
        send_email("s", "b")


def test_send_email_full_flow_with_tls_and_auth(monkeypatch):
    """SMTP connect, STARTTLS, login, and send_message run when configured."""
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_FROM", "from@example.com")
    monkeypatch.setenv("SMTP_TO", "to@example.com")
    monkeypatch.setenv("SMTP_USERNAME", "user")
    monkeypatch.setenv("SMTP_PASSWORD", "secret")
    monkeypatch.setenv("SMTP_USE_TLS", "true")

    mock_server = _smtp_instance_mock()
    with patch("backend.emailer.smtplib.SMTP", return_value=mock_server) as mock_smtp:
        send_email("Subject line", "Body text", reply_to="reply@example.com")

    mock_smtp.assert_called_once_with("smtp.example.com", 587, timeout=10)
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("user", "secret")
    mock_server.send_message.assert_called_once()
    msg = mock_server.send_message.call_args[0][0]
    assert msg["Subject"] == "Subject line"
    assert msg["Reply-To"] == "reply@example.com"


def test_send_email_skips_login_without_credentials(monkeypatch):
    """No login when username or password is blank."""
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_FROM", "from@example.com")
    monkeypatch.setenv("SMTP_TO", "to@example.com")
    monkeypatch.setenv("SMTP_USERNAME", "")
    monkeypatch.setenv("SMTP_PASSWORD", "")

    mock_server = _smtp_instance_mock()
    with patch("backend.emailer.smtplib.SMTP", return_value=mock_server):
        send_email("S", "B")

    mock_server.login.assert_not_called()
    mock_server.send_message.assert_called_once()


def test_send_email_skips_tls_when_disabled(monkeypatch):
    """STARTTLS is not called when SMTP_USE_TLS is false."""
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_FROM", "from@example.com")
    monkeypatch.setenv("SMTP_TO", "to@example.com")
    monkeypatch.setenv("SMTP_USE_TLS", "false")

    mock_server = _smtp_instance_mock()
    with patch("backend.emailer.smtplib.SMTP", return_value=mock_server):
        send_email("S", "B")

    mock_server.starttls.assert_not_called()
