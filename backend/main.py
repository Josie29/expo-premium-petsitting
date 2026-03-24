import os
import textwrap

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

from backend.emailer import send_email

load_dotenv()

app = FastAPI()


def _cors_origins():
    """Return allowed CORS origins for the API from ``FRONTEND_ORIGIN``.

    Parses a comma-separated list when ``FRONTEND_ORIGIN`` is set; otherwise
    allows all origins so local setups work without extra configuration.

    Returns:
        list[str]: Either ``["*"]`` when the env var is empty, or a list of
            trimmed origin strings (empty segments are dropped).

    """
    raw = os.getenv("FRONTEND_ORIGIN", "").strip()
    if not raw:
        return ["*"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_methods=["POST"],
    allow_headers=["*"],
)


class ContactRequest(BaseModel):
    """Validated payload for POST ``/contact`` (public fields plus optional honeypot)."""

    name: str = Field(..., min_length=1, max_length=80)
    email: EmailStr
    details: str = Field(..., min_length=1, max_length=2000)
    company: str | None = Field(default=None, max_length=120)


@app.get("/health")
def health():
    """Liveness probe for deploys and monitors.

    Returns:
        dict[str, str]: ``{"status": "ok"}`` when the process is up.

    """
    return {"status": "ok"}


@app.post("/contact")
def contact(request: ContactRequest):
    """Accept a contact form submission and email it via configured SMTP.

    Rejects honeypot submissions where ``company`` is non-empty. On success,
    sends a plain-text message to ``SMTP_TO`` with ``Reply-To`` set to the
    submitter's email.

    Args:
        request: Validated name, email, details, and optional bot field.

    Returns:
        dict[str, str]: ``{"status": "ok"}`` after the message is queued for send.

    Raises:
        HTTPException: 400 if the honeypot ``company`` field is set (likely bot).
        HTTPException: 500 if SMTP send fails after configuration appeared valid.

    """
    if request.company:
        raise HTTPException(status_code=400, detail="Invalid submission.")

    subject_prefix = os.getenv("EMAIL_SUBJECT_PREFIX", "New contact request")
    subject = f"{subject_prefix}: {request.name}"

    body = textwrap.dedent(
        f"""\
        New contact request

        Name: {request.name}
        Email: {request.email}

        Details:
        {request.details}
        """
    )

    try:
        send_email(subject=subject, body=body, reply_to=request.email)
    except Exception as exc:  # pragma: no cover - keeps response consistent
        raise HTTPException(status_code=500, detail="Unable to send message.") from exc

    return {"status": "ok"}
