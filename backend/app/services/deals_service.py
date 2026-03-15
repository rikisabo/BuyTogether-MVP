from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict
from uuid import UUID, uuid4

from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session

from app.models.deal import Deal
from app.models.participant import Participant
from app.core.errors import ApiError
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT


# public helpers ------------------------------------------------

def list_deals(db: Session, status: Optional[str], page: int, page_size: int):
    stmt = select(Deal)
    if status:
        stmt = stmt.where(Deal.status == status)
    stmt = stmt.order_by(Deal.created_at.desc())
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    deals = db.execute(stmt).scalars().all()
    return deals, total


def get_deal(db: Session, deal_id: UUID) -> Deal:
    deal = db.execute(select(Deal).where(Deal.id == deal_id)).scalar_one_or_none()
    if not deal:
        raise ApiError(
            code="DEAL_NOT_FOUND",
            message="Deal not found",
            status_code=HTTP_404_NOT_FOUND,
        )
    return deal


# admin ---------------------------------------------------------

def create_deal(
    db: Session,
    *,
    title: str,
    description: str,
    image_url: Optional[str],
    price_cents: int,
    min_qty_to_close: int,
    end_at: datetime,
) -> Deal:
    deal = Deal(
        title=title,
        description=description,
        image_url=image_url,
        price_cents=price_cents,
        min_qty_to_close=min_qty_to_close,
        end_at=end_at,
        status="ACTIVE",
        current_qty=0,
    )
    db.add(deal)
    db.commit()
    db.refresh(deal)
    return deal


# business logic ------------------------------------------------

def join_deal(
    db: Session,
    deal_id: UUID,
    name: str,
    email: str,
    qty: int,
    city: str,
    street: str,
    house_number: str,
    apartment: str | None,
    phone: str | None,
    notes: str | None,
) -> Tuple[Deal, Participant]:
    if qty < 1 or qty > 100:
        raise ApiError(
            code="VALIDATION_ERROR",
            message="qty must be between 1 and 100",
            status_code=HTTP_409_CONFLICT,
        )

    with db.begin():
        deal = db.execute(
            select(Deal).where(Deal.id == deal_id).with_for_update()
        ).scalar_one_or_none()
        if not deal:
            raise ApiError(
                code="DEAL_NOT_FOUND",
                message="Deal not found",
                status_code=HTTP_404_NOT_FOUND,
            )
        if deal.status != "ACTIVE":
            raise ApiError(
                code="DEAL_NOT_ACTIVE",
                message="Deal is not active",
                status_code=HTTP_409_CONFLICT,
            )

        part = db.execute(
            select(Participant)
            .where(
                Participant.deal_id == deal_id,
                Participant.email == email,
            )
            .with_for_update()
        ).scalar_one_or_none()

        if part:
            delta = qty - part.qty
            part.qty = qty
            part.name = name
            part.city = city
            part.street = street
            part.house_number = house_number
            part.apartment = apartment
            part.phone = phone
            part.notes = notes
            deal.current_qty += delta
        else:
            part = Participant(
                deal_id=deal_id,
                name=name,
                email=email,
                qty=qty,
                city=city,
                street=street,
                house_number=house_number,
                apartment=apartment,
                phone=phone,
                notes=notes,
                state="JOINED",
            )
            db.add(part)
            deal.current_qty += qty

        # ensure participant has a confirmation token and resets reminder metadata
        if not part.confirmation_token:
            part.confirmation_token = str(uuid4())
        part.last_email_sent_at = datetime.now(timezone.utc)
        part.reminder_count = 0

        db.flush()
        db.refresh(deal)
        db.refresh(part)
        return deal, part


def close_deals_job(db: Session) -> Dict[str, int]:
    now = datetime.now(timezone.utc)
    closed = 0
    failed = 0
    with db.begin():
        eligible = db.execute(
            select(Deal)
            .where(
                Deal.status == "ACTIVE",
                or_(
                    Deal.end_at <= now,
                    Deal.current_qty >= Deal.min_qty_to_close,
                ),
            )
        ).scalars().all()

        for d in eligible:
            locked = db.execute(
                select(Deal).where(Deal.id == d.id).with_for_update()
            ).scalar_one()

            if locked.current_qty >= locked.min_qty_to_close:
                locked.status = "CLOSED"
                closed += 1
                parts = db.execute(
                    select(Participant)
                    .where(
                        Participant.deal_id == locked.id,
                        Participant.state == "JOINED",
                    )
                ).scalars().all()
                for p in parts:
                    if p.tracking_id is None:
                        p.tracking_id = str(uuid4())
                    p.state = "INVITED_TO_PAY"
            else:
                locked.status = "FAILED"
                failed += 1

    return {"closed_count": closed, "failed_count": failed}
