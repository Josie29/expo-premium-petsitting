"""API tests for ``backend.main`` (health, contact flow, CORS helper).

High-level coverage:
- ``GET /health`` — liveness response.
- ``POST /contact`` — happy path with mocked SMTP helper; honeypot rejection;
  request validation (422); server error when sending fails (500).
- ``_cors_origins`` — wildcard default and comma-separated origin parsing.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import _cors_origins, app


def test_health_returns_ok():
    """GET /health returns a simple ok payload for probes."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_contact_success_sends_email(monkeypatch):
    """Valid POST /contact invokes send_email with subject, body, and reply-to."""
    sent = {}

    def fake_send_email(subject, body, reply_to=None):
        sent["subject"] = subject
        sent["body"] = body
        sent["reply_to"] = reply_to

    # Patch where `send_email` is used (main's bound import), not the emailer module.
    monkeypatch.setattr("backend.main.send_email", fake_send_email)

    client = TestClient(app)
    response = client.post(
        "/contact",
        json={"name": "Maya", "email": "maya@example.com", "details": "Need care next week."},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "Maya" in sent["body"]
    assert "Need care next week." in sent["body"]
    assert sent["reply_to"] == "maya@example.com"
    assert "Maya" in sent["subject"]


def test_contact_rejects_honeypot(monkeypatch):
    """POST /contact returns 400 when the hidden company field is filled (bot check)."""
    monkeypatch.setattr("backend.main.send_email", lambda *args, **kwargs: None)
    client = TestClient(app)

    response = client.post(
        "/contact",
        json={
            "name": "Bot",
            "email": "bot@example.com",
            "details": "Spam",
            "company": "Sneaky Field",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid submission."


def test_contact_returns_500_when_send_fails(monkeypatch):
    """POST /contact maps SMTP/helper failures to a generic 500 response."""

    def boom(*args, **kwargs):
        raise RuntimeError("SMTP down")

    monkeypatch.setattr("backend.main.send_email", boom)
    client = TestClient(app)

    response = client.post(
        "/contact",
        json={"name": "A", "email": "a@example.com", "details": "Hi"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Unable to send message."


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({"name": "", "email": "a@b.co", "details": "x"}, id="empty_name"),
        pytest.param({"name": "A", "email": "not-an-email", "details": "x"}, id="bad_email"),
        pytest.param({"name": "A", "email": "a@b.co", "details": ""}, id="empty_details"),
    ],
)
def test_contact_validation_errors_return_422(monkeypatch, payload):
    """Invalid name, email, or details yields 422 from Pydantic/FastAPI."""
    monkeypatch.setattr("backend.main.send_email", lambda *args, **kwargs: None)
    client = TestClient(app)
    response = client.post("/contact", json=payload)
    assert response.status_code == 422


def test_contact_rejects_name_over_max_length(monkeypatch):
    """Name longer than 80 characters is rejected with 422."""
    monkeypatch.setattr("backend.main.send_email", lambda *args, **kwargs: None)
    client = TestClient(app)
    response = client.post(
        "/contact",
        json={
            "name": "x" * 81,
            "email": "a@example.com",
            "details": "ok",
        },
    )
    assert response.status_code == 422


def test_contact_rejects_details_over_max_length(monkeypatch):
    """Details longer than 2000 characters is rejected with 422."""
    monkeypatch.setattr("backend.main.send_email", lambda *args, **kwargs: None)
    client = TestClient(app)
    response = client.post(
        "/contact",
        json={
            "name": "A",
            "email": "a@example.com",
            "details": "x" * 2001,
        },
    )
    assert response.status_code == 422


def test_contact_rejects_company_over_max_length(monkeypatch):
    """Honeypot company field still validated; oversized value yields 422."""
    monkeypatch.setattr("backend.main.send_email", lambda *args, **kwargs: None)
    client = TestClient(app)
    response = client.post(
        "/contact",
        json={
            "name": "A",
            "email": "a@example.com",
            "details": "ok",
            "company": "x" * 121,
        },
    )
    assert response.status_code == 422


def test_cors_origins_default_wildcard(monkeypatch):
    """When FRONTEND_ORIGIN is unset or empty, allow all origins."""
    monkeypatch.delenv("FRONTEND_ORIGIN", raising=False)
    assert _cors_origins() == ["*"]
    monkeypatch.setenv("FRONTEND_ORIGIN", "   ")
    assert _cors_origins() == ["*"]


def test_cors_origins_splits_comma_separated_list(monkeypatch):
    """Comma-separated FRONTEND_ORIGIN values are trimmed and split."""
    monkeypatch.setenv("FRONTEND_ORIGIN", " https://a.com , https://b.com ")
    assert _cors_origins() == ["https://a.com", "https://b.com"]
