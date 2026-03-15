from __future__ import annotations
from datetime import datetime, timezone, timedelta
import secrets
from typing import Dict, Any

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from .email_service import email_service
from app.models.participant import Participant
from app.models.deal import Deal

from app.settings import settings


def _generate_token() -> str:
    # url-safe token
    return secrets.token_urlsafe(32)


def send_confirmation_email(part: Participant, deal: Deal) -> None:
    # build link using FRONTEND_URL
    from app.settings import settings
    frontend = settings.FRONTEND_URL
    token = part.confirmation_token
    if not token:
        return
    link = f"{frontend}/confirm/{token}"
    subject = f"אישור השתתפות ב-{deal.title}"
    body = (
        f"שלום {part.name},\n\n"
        "תודה שהצטרפת להצעה שלנו. כדי להשלים את ההצטרפות, אנא לחץ על הקישור למטה:\n"
        f"{link}\n\n"
        "במידה ולא תאשר, תצטרך להצטרף מחדש.\n\n"
        "בברכה, צוות קנייה קבוצתית"
    )
    html = f"""
    <html lang=\"he\">\n
    <body style=\"font-family: Arial, sans-serif; direction: rtl; text-align: right;\">\n      <table width=\"100%\" style=\"max-width: 600px; margin: auto; border: 1px solid #e5e7eb; border-radius:8px; background:#ffffff;\">\n        <tr>\n          <td style=\"padding:20px;\">\n            <h2 style=\"color:#1d4ed8;\">אישור השתתפות ב-{deal.title}</h2>\n            <p>שלום {part.name},</p>\n            <p>כדי לאשר את ההשתתפות שלך במבצע, יש ללחוץ על הכפתור הבא:</p>\n            <p style=\"text-align:center; margin:20px 0;\">\n              <a href=\"{link}\" style=\"background:#1d4ed8; color:#ffffff; padding:12px 22px; border-radius:6px; text-decoration:none; font-weight:700;\">אשר את ההשתתפות שלי</a>\n            </p>\n            <p style=\"color:#4b5563;\">אם הכפתור לא עובד, העתק ושמור את הקישור הבא בדפדפן:</p>\n            <p style=\"color:#6b7280; word-wrap:break-word;\">{link}</p>\n            <p style=\"color:#4b5563; margin-top:24px;\">בברכה,<br />צוות קנייה קבוצתית</p>\n          </td>\n        </tr>\n      </table>\n    </body>\n    </html>
    """
    email_service.send_email(part.email, subject, body, html=html)


def join_participant(db: Session, deal: Deal, part: Participant) -> None:
    # generate token if none
    if not part.confirmation_token:
        part.confirmation_token = _generate_token()
    part.last_email_sent_at = datetime.now(timezone.utc)
    part.reminder_count = 0
    db.add(part)
    db.commit()
    # send initial email
    send_confirmation_email(part, deal)


def confirm(db: Session, token: str) -> Participant | None:
    stmt = select(Participant).where(Participant.confirmation_token == token)
    part = db.execute(stmt).scalar_one_or_none()
    if not part:
        return None
    part.is_confirmed = True
    part.confirmed_at = datetime.now(timezone.utc)
    # clear token so link cannot be reused
    part.confirmation_token = None
    db.commit()
    return part


def send_reminders(db: Session) -> Dict[str, Any]:
    # scan active deals and unconfirmed participants
    now = datetime.now(timezone.utc)
    sent = 0
    stmt = (
        select(Participant, Deal)
        .join(Deal, Participant.deal_id == Deal.id)
        .where(
            Deal.status == "ACTIVE",
            Participant.is_confirmed == False,
        )
    )
    for part, deal in db.execute(stmt).all():
        # determine if we need to send based on deal end
        remaining = deal.end_at - now
        # if first reminder: send when <=2 days remaining
        # second reminder: when <=1 day remaining
        should_send = False
        if part.reminder_count == 0 and remaining <= timedelta(days=2):
            should_send = True
        elif part.reminder_count == 1 and remaining <= timedelta(days=1):
            should_send = True
        if should_send:
            send_confirmation_email(part, deal)
            part.reminder_count += 1
            part.last_email_sent_at = now
            db.add(part)
            sent += 1
    if sent > 0:
        db.commit()
    return {"sent": sent}
