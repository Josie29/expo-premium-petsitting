from fastapi.testclient import TestClient

import backend.emailer as emailer
from backend.main import app


def test_contact_success_sends_email(monkeypatch):
    sent = {}

    def fake_send_email(subject, body, reply_to=None):
        sent["subject"] = subject
        sent["body"] = body
        sent["reply_to"] = reply_to

    monkeypatch.setattr(emailer, "send_email", fake_send_email)

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


def test_contact_rejects_honeypot(monkeypatch):
    monkeypatch.setattr(emailer, "send_email", lambda *args, **kwargs: None)
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
