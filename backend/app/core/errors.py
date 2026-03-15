from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY


class ApiError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = HTTP_409_CONFLICT,
        details: dict | None = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


def api_error_handler(request: Request, exc: ApiError):
    request_id = getattr(request.state, "request_id", None)
    content = {
        "data": None,
        "request_id": request_id,
        "error": {"code": exc.code, "message": exc.message},
    }
    if exc.details is not None:
        content["error"]["details"] = exc.details
    return JSONResponse(status_code=exc.status_code, content=content)


def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", None)
    # exc.errors() can include non-serializable objects in the ``ctx``
    # (e.g. a ValueError instance when a custom validator raises one).  FastAPI
    # will attempt to JSON-encode the whole list and fail, which turns a simple
    # 422 into a 500.  Strip out the context before returning.
    errors = exc.errors()
    for err in errors:
        if "ctx" in err:
            # drop any values that can't be serialized; a string version is
            # sufficient for consumers.
            cleaned_ctx: dict = {}
            for k, v in err.get("ctx", {}).items():
                try:
                    # jsonable_encoder from fastapi could be used, but a simple
                    # str() fallback is enough here.
                    import json
                    json.dumps(v)
                    cleaned_ctx[k] = v
                except Exception:
                    cleaned_ctx[k] = str(v)
            err["ctx"] = cleaned_ctx
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "data": None,
            "request_id": request_id,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation error",
                "details": errors,
            },
        },
    )
