from fastapi import APIRouter, Depends, status
import logging

logger = logging.getLogger(__name__)
from sqlalchemy.orm import Session

from app.api.dependencies import request_id_dependency, db_session_dependency
from app.schemas.deals import CreateDealRequest, DealSummary
from app.services import deals_service

router = APIRouter()


@router.post("/deals", status_code=status.HTTP_201_CREATED)
def create_deal(
    body: CreateDealRequest,
    db: Session = Depends(db_session_dependency),
    request_id: str = Depends(request_id_dependency),
):
    try:
        deal = deals_service.create_deal(
            db,
            title=body.title,
            description=body.description,
            image_url=body.image_url,
            price_cents=body.price_cents,
            min_qty_to_close=body.min_qty_to_close,
            end_at=body.end_at,
        )
    except Exception as exc:  # pylint: disable=broad-exception-caught
        # log the full stack so we know exactly what went wrong in production
        logger.exception("failed to create deal: %s", exc)
        # re-raise so FastAPI can turn it into a 500 response as usual
        raise
    payload = DealSummary.from_orm(deal)
    return {"data": payload, "request_id": request_id}
