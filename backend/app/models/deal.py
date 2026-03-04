"""Deal model for group-buying functionality."""
from datetime import datetime
from enum import Enum
import uuid

from sqlalchemy import String, Text, Integer, DateTime, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from ..db import Base


class DealStatus(str, Enum):
    """Status enum for deals."""
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    FAILED = "FAILED"


class Deal(Base):
    """Deal model representing a group-buying deal."""

    __tablename__ = "deals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    min_qty_to_close: Mapped[int] = mapped_column(Integer, nullable=False)
    current_qty: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    end_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[DealStatus] = mapped_column(
        SQLEnum(DealStatus), nullable=False, default=DealStatus.ACTIVE
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_deals_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<Deal(id={self.id}, title={self.title}, status={self.status})>"
