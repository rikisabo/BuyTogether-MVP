from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import request_id_dependency, db_session_dependency
from app.services import deals_service
from app.schemas.deals import CloseJobResponse

router = APIRouter()


@router.post("/close-deals")
def close_deals(
    db: Session = Depends(db_session_dependency),
    request_id: str = Depends(request_id_dependency),
):
    result = deals_service.close_deals_job(db)
    payload = CloseJobResponse(**result)
    return {"data": payload, "request_id": request_id}


@router.post("/send-confirmation-reminders")
def send_confirmation_reminders(
    db: Session = Depends(db_session_dependency),
    request_id: str = Depends(request_id_dependency),
):
    from app.services.confirmation_service import send_reminders

    result = send_reminders(db)
    return {"data": result, "request_id": request_id}
