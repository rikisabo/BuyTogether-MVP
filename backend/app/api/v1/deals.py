from typing import Optional

from fastapi import APIRouter, Depends, Query, Path, status, BackgroundTasks
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.dependencies import request_id_dependency, db_session_dependency
from app.schemas.deals import (
    DealSummary,
    JoinDealRequest,
    ParticipantInfo,
    JoinResponse,
    DealsPage,
)
from app.services import deals_service
from app.services.email_service import email_service
from app.services.confirmation_service import send_confirmation_email
from app.settings import settings
from sqlalchemy import select, func
from app.models.participant import Participant

router = APIRouter()


@router.get("/deals")
def list_deals(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(db_session_dependency),
    request_id: str = Depends(request_id_dependency),
):
    deals, total = deals_service.list_deals(db, status, page, page_size)
    payload = {
        "items": [DealSummary.from_orm(d) for d in deals],
        "page": page,
        "page_size": page_size,
        "total": total,
    }
    return {"data": payload, "request_id": request_id}


@router.get("/deals/{deal_id}")
def get_deal(
    deal_id: UUID = Path(...),
    db: Session = Depends(db_session_dependency),
    request_id: str = Depends(request_id_dependency),
):
    deal = deals_service.get_deal(db, deal_id)
    # count participants separately
    count = db.execute(
        select(func.count()).select_from(Participant).where(Participant.deal_id == deal_id)
    ).scalar_one()
    unconf = db.execute(
        select(func.count()).select_from(Participant).where(
            Participant.deal_id == deal_id,
            Participant.is_confirmed == False,
        )
    ).scalar_one()
    payload = DealSummary.from_orm(deal)
    payload.participants_count = count  # field added to schema
    payload.unconfirmed_count = unconf
    return {"data": payload, "request_id": request_id}


@router.post("/deals/{deal_id}/join", status_code=status.HTTP_200_OK)
def join_deal_endpoint(
    body: JoinDealRequest,
    background_tasks: BackgroundTasks,
    deal_id: UUID = Path(...),
    db: Session = Depends(db_session_dependency),
    request_id: str = Depends(request_id_dependency),
):
    deal_obj, part_obj = deals_service.join_deal(
        db,
        deal_id,
        body.name,
        body.email,
        body.qty,
        body.city,
        body.street,
        body.house_number,
        body.apartment,
        body.phone,
        body.notes,
    )

    # schedule email notifications after commit
    background_tasks.add_task(send_confirmation_email, part_obj, deal_obj)
    admin_subject = f"New participant for deal {deal_obj.title}"
    admin_body = (
        f"Participant {part_obj.name} ({part_obj.email}) joined with qty {part_obj.qty}.\n"
        f"City: {part_obj.city}, Street: {part_obj.street}, House: {part_obj.house_number}."
    )
    background_tasks.add_task(
        email_service.send_email,
        settings.EMAIL_FROM,
        admin_subject,
        admin_body,
    )

    payload = JoinResponse(
        deal=DealSummary.from_orm(deal_obj),
        participant=ParticipantInfo.from_orm(part_obj),
    )
    return {"data": payload, "request_id": request_id}


@router.post("/confirm/{token}")
def confirm_participation(
    token: str = Path(...),
    db: Session = Depends(db_session_dependency),
    request_id: str = Depends(request_id_dependency),
):
    from app.services.confirmation_service import confirm

    part = confirm(db, token)
    if not part:
        return {"data": {"success": False}, "request_id": request_id}
    return {"data": {"success": True}, "request_id": request_id}
