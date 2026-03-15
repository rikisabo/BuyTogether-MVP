import os
import smtplib
from email.message import EmailMessage
from typing import Optional


class EmailService:
    def __init__(self):
        # configuration via environment variables
        from app.settings import settings
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT or 587
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASS
        self.from_addr = settings.EMAIL_FROM
        # if host is missing, we'll disable sending and just log

    def send_email(self, to: str, subject: str, body: str, html: Optional[str] = None) -> None:
        if not self.host:
            # fallback: just print
            print(f"[email] to={to} subject={subject}\n{body}\n{html or ''}")
            return
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.from_addr
        msg['To'] = to
        msg.set_content(body)
        if html:
            msg.add_alternative(html, subtype='html')

        try:
            with smtplib.SMTP(self.host, self.port) as smtp:
                smtp.starttls()
                if self.user and self.password:
                    smtp.login(self.user, self.password)
                smtp.send_message(msg)
        except Exception as exc:
            # avoid failing API when email service is temporarily unavailable
            print(f"[email] failed to send to {to}: {exc}")


email_service = EmailService()
