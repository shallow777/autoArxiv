from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

from .models import Paper


def send_digest_email(subject: str, html_body: str, papers: list[Paper]) -> bool:
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
    message.set_content("这是一封包含 HTML 摘要的邮件，请使用支持 HTML 的客户端查看。")

    message.add_alternative(html_body, subtype="html")
    html_part = message.get_payload()[-1]
    for paper in papers:
        if paper.figure_bytes and paper.figure_subtype and paper.figure_content_id:
            html_part.add_related(
                paper.figure_bytes,
                maintype="image",
                subtype=paper.figure_subtype,
                cid=f"<{paper.figure_content_id}>",
                filename=f"{paper.arxiv_id}-figure.{paper.figure_subtype}",
            )

    with smtplib.SMTP(host, port, timeout=30) as smtp:
        if use_tls:
            smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(message)
    return True
