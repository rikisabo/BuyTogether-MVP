from typing import Generator

from fastapi import Request, Depends
from sqlalchemy.orm import Session
from uuid import uuid4

from app.db import get_db


def request_id_dependency(request: Request) -> str:
    return getattr(request.state, "request_id", str(uuid4()))


def db_session_dependency() -> Generator[Session, None, None]:
    yield from get_db()
