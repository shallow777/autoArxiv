from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage


def send_digest_email(subject: str, html_body: str) -> bool:
    host = os.getenv("SMTP_HOST", "").strip()
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME", "").strip()
    password = os.getenv("SMTP_PASSWORD", "").strip()
    mail_from = os.getenv("SMTP_FROM", username).strip()
    mail_to = os.getenv("EMAIL_TO", "").strip()
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    if not all([host, username, password, mail_from, mail_to]):
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = mail_from
    message["To"] = mail_to
    message.set_content("This email contains an HTML digest. Please view it in an HTML-capable mail client.")
    message.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(host, port, timeout=30) as smtp:
        if use_tls:
            smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(message)
    return True
