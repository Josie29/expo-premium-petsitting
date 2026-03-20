import os
import smtplib
from email.message import EmailMessage


def _env_bool(name, default="true"):
    value = os.getenv(name, default).strip().lower()
    return value in {"1", "true", "yes", "on"}


def send_email(subject, body, reply_to=None):
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_use_tls = _env_bool("SMTP_USE_TLS", "true")
    smtp_from = os.getenv("SMTP_FROM", "")
    smtp_to = os.getenv("SMTP_TO", "")

    if not smtp_host or not smtp_from or not smtp_to:
        raise RuntimeError("Missing SMTP configuration.")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = smtp_from
    message["To"] = smtp_to
    if reply_to:
        message["Reply-To"] = reply_to
    message.set_content(body)

    with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
        if smtp_use_tls:
            server.starttls()
        if smtp_username and smtp_password:
            server.login(smtp_username, smtp_password)
        server.send_message(message)
