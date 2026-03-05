from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

import httpx
import pytest
from alembic import command
from alembic.config import Config
from httpx import AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = "postgresql://buytogether:password@localhost:5433/buytogether_test"

# Make sure the app/migrations use the test DB, not the default one
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from app.main import create_app  # noqa: E402

engine = create_engine(TEST_DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def _reset_public_schema() -> None:
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))
        conn.execute(text("CREATE SCHEMA public;"))


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    backend_dir = Path(__file__).resolve().parents[1]
    alembic_ini = backend_dir / "alembic.ini"
    migrations_dir = backend_dir / "migrations"

    _reset_public_schema()

    alembic_cfg = Config(str(alembic_ini))
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    alembic_cfg.set_main_option("script_location", str(migrations_dir))
    command.upgrade(alembic_cfg, "head")

    yield


@pytest.fixture(scope="function", autouse=True)
def clean_tables():
    with engine.begin() as conn:
        result = conn.execute(
            text(
                """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename NOT LIKE 'pg_%'
                  AND tablename NOT LIKE 'sql_%'
                  AND tablename <> 'alembic_version'
                """
            )
        )
        tables = [row[0] for row in result.fetchall()]
        if tables:
            conn.execute(
                text(f"TRUNCATE TABLE {', '.join(tables)} RESTART IDENTITY CASCADE")
            )


@pytest.fixture
def db_session() -> Generator:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
async def async_client(db_session) -> AsyncClient:
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL

    app = create_app()

    from app.db import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def seed_deal(db_session):
    from datetime import datetime, timezone, timedelta
    from app.models.deal import Deal

    deal = Deal(
        title="Test Deal",
        description="A test deal",
        price_cents=1000,
        min_qty_to_close=10,
        current_qty=0,
        end_at=datetime.now(timezone.utc) + timedelta(days=1),
        status="ACTIVE",
    )
    db_session.add(deal)
    db_session.commit()
    db_session.refresh(deal)
    return deal