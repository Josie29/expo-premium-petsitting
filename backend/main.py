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
    name: str = Field(..., min_length=1, max_length=80)
    email: EmailStr
    details: str = Field(..., min_length=1, max_length=2000)
    company: str | None = Field(default=None, max_length=120)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/contact")
def contact(request: ContactRequest):
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
