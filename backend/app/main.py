from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .settings import settings
from .utils.logging import setup_logging, RequestIDMiddleware
from .api.routers import health, root
from .db import engine
import logging
from sqlalchemy import text


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="buyToghether API")

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # request id middleware
    app.add_middleware(RequestIDMiddleware)

    # include routers under /api/v1
    app.include_router(root.router, prefix="/api/v1")
    app.include_router(health.router, prefix="/api/v1")

    # exception handlers
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", None)
        logging.getLogger("uvicorn.error").exception("Unhandled exception")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "request_id": request_id},
        )

    @app.on_event("startup")
    def on_startup():
        # test DB connectivity
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logging.getLogger("uvicorn.info").info("Database connectivity OK")
        except Exception:
            logging.getLogger("uvicorn.error").exception("Database connectivity FAILED")

    return app


app = create_app()
