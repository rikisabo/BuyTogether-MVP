from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health(request: Request):
    request_id = getattr(request.state, "request_id", None)
    return {"status": "ok", "request_id": request_id}
