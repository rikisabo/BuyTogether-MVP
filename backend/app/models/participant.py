"""Participant model for group-buying deals."""
from datetime import datetime
from enum import Enum
import uuid

from sqlalchemy import String, Integer, DateTime, Enum as SQLEnum, Index, ForeignKey, UniqueConstraint
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from ..db import Base


class ParticipantState(str, Enum):
    """State enum for participants in a deal."""
    JOINED = "JOINED"
    INVITED_TO_PAY = "INVITED_TO_PAY"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class Participant(Base):
    """Participant model for group-buying deals."""

    __tablename__ = "participants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    # new address/contact columns
    city: Mapped[str] = mapped_column(String(255), nullable=True)
    street: Mapped[str] = mapped_column(String(255), nullable=True)
    house_number: Mapped[str] = mapped_column(String(50), nullable=True)
    apartment: Mapped[str | None] = mapped_column(String(50), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    tracking_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # confirmation tracking
    is_confirmed: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, default=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    confirmation_token: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    last_email_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reminder_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    state: Mapped[ParticipantState] = mapped_column(
        SQLEnum(ParticipantState), nullable=False, default=ParticipantState.JOINED
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
        UniqueConstraint("deal_id", "email", name="uq_participants_deal_email"),
        Index("ix_participants_deal_id", "deal_id"),
        Index("ix_participants_email", "email"),
    )

    def __repr__(self) -> str:
        return f"<Participant(id={self.id}, deal_id={self.deal_id}, email={self.email}, state={self.state})>"
