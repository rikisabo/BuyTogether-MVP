from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


class DealSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: Optional[str]
    image_url: Optional[str]
    status: str
    price_cents: int
    min_qty_to_close: int
    current_qty: int
    end_at: datetime
    # number of unique participants who have joined the deal
    participants_count: int = 0
    unconfirmed_count: int = 0


class ParticipantInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: EmailStr
    qty: int
    city: Optional[str]
    street: Optional[str]
    house_number: Optional[str]
    apartment: Optional[str]
    phone: Optional[str]
    notes: Optional[str]
    is_confirmed: bool
    confirmed_at: Optional[datetime]
    reminder_count: int
    last_email_sent_at: Optional[datetime]
    state: str
    tracking_id: Optional[UUID]


class CreateDealRequest(BaseModel):
    title: str
    description: str
    image_url: Optional[str] = None
    price_cents: int = Field(..., gt=0)
    min_qty_to_close: int = Field(..., gt=0)
    end_at: datetime

    @field_validator("end_at")
    @classmethod
    def end_at_must_be_future(cls, v: datetime) -> datetime:
        # אם הגיע naive datetime – נניח UTC
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)

        if v <= datetime.now(timezone.utc):
            raise ValueError("end_at must be in the future")
        return v


class JoinDealRequest(BaseModel):
    name: str
    email: EmailStr
    qty: int = Field(..., ge=1, le=100)
    city: str
    street: str
    house_number: str
    apartment: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None


class DealsPage(BaseModel):
    items: List[DealSummary]
    page: int
    page_size: int
    total: int


class JoinResponse(BaseModel):
    deal: DealSummary
    participant: ParticipantInfo


class CloseJobResponse(BaseModel):
    closed_count: int
    failed_count: int