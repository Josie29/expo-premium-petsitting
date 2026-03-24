import os
import smtplib
from email.message import EmailMessage


def _env_bool(name, default="true"):
    """Interpret a string environment variable as a boolean.

    Args:
        name: Environment variable name.
        default: Value used when ``name`` is unset (default ``"true"``).

    Returns:
        bool: True when the value (case-insensitive) is one of ``1``, ``true``,
            ``yes``, or ``on``; otherwise False.

    """
    value = os.getenv(name, default).strip().lower()
    return value in {"1", "true", "yes", "on"}


def send_email(subject, body, reply_to=None):
    """Send a plain-text email through SMTP using environment configuration.

    Reads host, port, TLS, credentials, and from/to addresses from the process
    environment. Uses STARTTLS when ``SMTP_USE_TLS`` is truthy. Authenticates
    only when both username and password are non-empty. Failures opening the
    connection, negotiating TLS, authenticating, or sending are not caught and
    propagate from ``smtplib``.

    Args:
        subject: Email subject line.
        body: Plain-text body.
        reply_to: Optional address for the ``Reply-To`` header.

    Raises:
        RuntimeError: If ``SMTP_HOST``, ``SMTP_FROM``, or ``SMTP_TO`` is missing.

    """
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
